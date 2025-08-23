import os
import time
import asyncio
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pandas as pd

from synthefy.data_models import ForecastV2Request, ForecastV2Response

BASE_URL = "https://prod.synthefy.com"
ENDPOINT = "/api/v2/foundation_models/forecast/stream"


class SynthefyError(Exception):
    """Base error for all Synthefy client exceptions."""


class APITimeoutError(SynthefyError):
    """The request timed out before completing."""


class APIConnectionError(SynthefyError):
    """The request failed due to a connection issue."""


class APIStatusError(SynthefyError):
    """Raised when the API returns a non-2xx status code."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        request_id: Optional[str] = None,
        error_code: Optional[str] = None,
        response_body: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id
        self.error_code = error_code
        self.response_body = response_body


class BadRequestError(APIStatusError):
    pass


class AuthenticationError(APIStatusError):
    pass


class PermissionDeniedError(APIStatusError):
    pass


class NotFoundError(APIStatusError):
    pass


class RateLimitError(APIStatusError):
    pass


class InternalServerError(APIStatusError):
    pass


def _extract_error_details(response: httpx.Response) -> Tuple[str, Optional[str], Optional[str], Any]:
    """Attempt to extract a professional, user-friendly error message and metadata.

    Returns a tuple of (message, request_id, error_code, parsed_body)
    """
    request_id = response.headers.get("x-request-id") or response.headers.get("X-Request-Id")
    parsed: Any
    message: str = f"HTTP {response.status_code} Error"
    code: Optional[str] = None

    try:
        parsed = response.json()
        # Common error shapes: {"error": {"message": str, "type"/"code": str}}, {"message": str}
        if isinstance(parsed, dict):
            error_obj: Any = parsed.get("error")
            if isinstance(error_obj, dict):
                message = (
                    error_obj.get("message")
                    or error_obj.get("detail")
                    or error_obj.get("error")
                    or message
                )
                code = error_obj.get("code") or error_obj.get("type")
                request_id = request_id or error_obj.get("request_id")
            else:
                message = (
                    parsed.get("message")
                    or parsed.get("detail")
                    or parsed.get("error")
                    or message
                )
                code = parsed.get("code") or parsed.get("type")
                request_id = request_id or parsed.get("request_id")
        else:
            parsed = response.text
            if isinstance(parsed, str) and parsed.strip():
                message = parsed.strip()[:500]
    except Exception:
        parsed = response.text
        if isinstance(parsed, str) and parsed.strip():
            message = parsed.strip()[:500]

    return message, request_id, code, parsed


def _raise_for_status(response: httpx.Response) -> None:
    if 200 <= response.status_code < 300:
        return

    message, request_id, code, parsed = _extract_error_details(response)
    status = response.status_code

    if status == 400 or status == 422:
        raise BadRequestError(message, status_code=status, request_id=request_id, error_code=code, response_body=parsed)
    if status == 401:
        raise AuthenticationError(message, status_code=status, request_id=request_id, error_code=code, response_body=parsed)
    if status == 403:
        raise PermissionDeniedError(message, status_code=status, request_id=request_id, error_code=code, response_body=parsed)
    if status == 404:
        raise NotFoundError(message, status_code=status, request_id=request_id, error_code=code, response_body=parsed)
    if status == 429:
        raise RateLimitError(message, status_code=status, request_id=request_id, error_code=code, response_body=parsed)
    if 500 <= status <= 599:
        raise InternalServerError(message, status_code=status, request_id=request_id, error_code=code, response_body=parsed)

    raise APIStatusError(message, status_code=status, request_id=request_id, error_code=code, response_body=parsed)


class SynthefyAPIClient:
    def __init__(self, api_key: str | None = None, *, timeout: float = 300.0, max_retries: int = 2, base_url: str = BASE_URL, organization: Optional[str] = None, user_agent: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("SYNTHEFY_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key must be provided either as a parameter or through SYNTHEFY_API_KEY environment variable"
                )

        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url, timeout=self.timeout)
        self.organization = organization
        self.user_agent = user_agent or f"synthefy-python httpx/{httpx.__version__}"

    # Context manager support (sync) and utilities
    def __enter__(self) -> "SynthefyAPIClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass

    def _headers(self, *, idempotency_key: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "X-API-KEY": self.api_key,
            "User-Agent": self.user_agent,
        }
        if self.organization:
            headers["X-Organization"] = self.organization
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _should_retry(self, response: Optional[httpx.Response], exc: Optional[Exception]) -> bool:
        if exc is not None:
            # Connection errors/timeouts are retryable
            return True
        if response is None:
            return False
        if response.status_code in (408, 409, 425, 429) or 500 <= response.status_code <= 599:
            return True
        return False

    def _compute_backoff(self, attempt: int, response: Optional[httpx.Response]) -> float:
        if response is not None:
            retry_after = response.headers.get("retry-after") or response.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    return float(retry_after)
                except ValueError:
                    pass
        # Exponential backoff with jitter
        base = min(2 ** attempt, 30)
        return base * (0.5 + 0.5 * (os.urandom(1)[0] / 255))

    def _post_with_retries(self, endpoint: str, json: Dict[str, Any], *, headers: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> httpx.Response:
        last_exc: Optional[Exception] = None
        response: Optional[httpx.Response] = None
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            try:
                response = self.client.post(endpoint, json=json, headers=headers or self._headers(), timeout=timeout or self.timeout)
                if not self._should_retry(response, None):
                    _raise_for_status(response)
                    return response
            except httpx.TimeoutException as exc:
                last_exc = APITimeoutError(str(exc))
            except httpx.HTTPError as exc:
                last_exc = APIConnectionError(str(exc))

            # Decide to retry
            if attempt < attempts - 1 and self._should_retry(response, last_exc):
                delay = self._compute_backoff(attempt, response)
                time.sleep(delay)
                continue

            # No more retries
            if last_exc is not None:
                raise last_exc
            if response is not None:
                _raise_for_status(response)
                return response

        # Should not reach here
        raise APIConnectionError("Request failed after retries")


    def forecast(self, request: ForecastV2Request, *, timeout: Optional[float] = None, idempotency_key: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> ForecastV2Response:
        response = self._post_with_retries(
            ENDPOINT,
            json=request.model_dump(),
            headers=self._headers(idempotency_key=idempotency_key, extra_headers=extra_headers),
            timeout=timeout,
        )
        response_data = response.json()
        return ForecastV2Response(**response_data)

    def forecast_dfs(
        self,
        history_dfs: List[pd.DataFrame],
        target_dfs: List[pd.DataFrame],
        target_col: str,
        timestamp_col: str,
        metadata_cols: List[str],
        leak_cols: List[str],
        model: str,
    ) -> List[pd.DataFrame]:
        request = ForecastV2Request.from_dfs(
            history_dfs,
            target_dfs,
            target_col,
            timestamp_col,
            metadata_cols,
            leak_cols,
            model,
        )

        response = self.forecast(request)

        return response.to_dfs()




class SynthefyAsyncAPIClient:
    def __init__(self, api_key: str | None = None, *, timeout: float = 300.0, max_retries: int = 2, base_url: str = BASE_URL, organization: Optional[str] = None, user_agent: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("SYNTHEFY_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key must be provided either as a parameter or through SYNTHEFY_API_KEY environment variable"
                )

        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        self.organization = organization
        self.user_agent = user_agent or f"synthefy-python httpx/{httpx.__version__}"

    async def __aenter__(self) -> "SynthefyAsyncAPIClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        try:
            await self.client.aclose()
        except Exception:
            pass

    def _headers(self, *, idempotency_key: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "X-API-KEY": self.api_key,
            "User-Agent": self.user_agent,
        }
        if self.organization:
            headers["X-Organization"] = self.organization
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _should_retry(self, response: Optional[httpx.Response], exc: Optional[Exception]) -> bool:
        if exc is not None:
            return True
        if response is None:
            return False
        if response.status_code in (408, 409, 425, 429) or 500 <= response.status_code <= 599:
            return True
        return False

    def _compute_backoff(self, attempt: int, response: Optional[httpx.Response]) -> float:
        if response is not None:
            retry_after = response.headers.get("retry-after") or response.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    return float(retry_after)
                except ValueError:
                    pass
        base = min(2 ** attempt, 30)
        return base * (0.5 + 0.5 * (os.urandom(1)[0] / 255))

    async def _post_with_retries(self, endpoint: str, json: Dict[str, Any], *, headers: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> httpx.Response:
        last_exc: Optional[Exception] = None
        response: Optional[httpx.Response] = None
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            try:
                response = await self.client.post(endpoint, json=json, headers=headers or self._headers(), timeout=timeout or self.timeout)
                if not self._should_retry(response, None):
                    _raise_for_status(response)
                    return response
            except httpx.TimeoutException as exc:
                last_exc = APITimeoutError(str(exc))
            except httpx.HTTPError as exc:
                last_exc = APIConnectionError(str(exc))

            if attempt < attempts - 1 and self._should_retry(response, last_exc):
                delay = self._compute_backoff(attempt, response)
                await asyncio.sleep(delay)
                continue

            if last_exc is not None:
                raise last_exc
            if response is not None:
                _raise_for_status(response)
                return response

        raise APIConnectionError("Request failed after retries")

    async def forecast(self, request: ForecastV2Request, *, timeout: Optional[float] = None, idempotency_key: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> ForecastV2Response:
        response = await self._post_with_retries(
            ENDPOINT,
            json=request.model_dump(),
            headers=self._headers(idempotency_key=idempotency_key, extra_headers=extra_headers),
            timeout=timeout,
        )
        response_data = response.json()
        return ForecastV2Response(**response_data)

    async def forecast_dfs(
        self,
        history_dfs: List[pd.DataFrame],
        target_dfs: List[pd.DataFrame],
        target_col: str,
        timestamp_col: str,
        metadata_cols: List[str],
        leak_cols: List[str],
        model: str,
    ) -> List[pd.DataFrame]:
        request = ForecastV2Request.from_dfs(
            history_dfs,
            target_dfs,
            target_col,
            timestamp_col,
            metadata_cols,
            leak_cols,
            model,
        )
        response = await self.forecast(request)
        return response.to_dfs()


