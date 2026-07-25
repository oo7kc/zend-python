from __future__ import annotations

from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, TypeAdapter

from zend._errors import ApplicationError, TimeoutError, ZendError
from zend._normalize import normalize_response
from zend._response import ZendResponse
from zend._version import VERSION

T = TypeVar("T")


def _dump_body(body: Any, pass_through: list[str] | None = None) -> Any:
    """Serialize a request body to snake_case wire JSON.

    Pydantic models dump with aliases where set (e.g. ``from_`` → ``from``).
    Nested keys under ``pass_through`` fields are left untouched.
    """
    del pass_through  # nested keys already preserved by model_dump / raw dicts
    if isinstance(body, BaseModel):
        data = body.model_dump(by_alias=True, exclude_none=True)
    elif isinstance(body, dict):
        data = {k: v for k, v in body.items() if v is not None}
    else:
        return body

    if "from_" in data and "from" not in data:
        data["from"] = data.pop("from_")
    return data


def _parse_json(response: httpx.Response) -> Any:
    text = response.text
    if not text:
        return None
    try:
        return response.json()
    except ValueError:
        return None


def _cast(data: Any, cast_to: type[T] | TypeAdapter[T] | None) -> T:
    if cast_to is None:
        return data  # type: ignore[return-value]
    if isinstance(cast_to, TypeAdapter):
        return cast_to.validate_python(data)
    if isinstance(cast_to, type) and issubclass(cast_to, BaseModel):
        return cast_to.model_validate(data)  # type: ignore[return-value]
    # list[...] / other generics via TypeAdapter
    return TypeAdapter(cast_to).validate_python(data)


class HttpClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float,
        headers: dict[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._timeout = timeout
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json",
                "User-Agent": f"usezend-python/{VERSION}",
                **(headers or {}),
            },
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        json_body: Any = None,
        pass_through: list[str] | None = None,
        files: Any = None,
        cast_to: type[T] | TypeAdapter[T] | None = None,
    ) -> ZendResponse[T]:
        params = None
        if query:
            params = {k: v for k, v in query.items() if v is not None}

        kwargs: dict[str, Any] = {"method": method, "url": path, "params": params}
        if files is not None:
            kwargs["files"] = files
        elif json_body is not None:
            kwargs["json"] = _dump_body(json_body, pass_through)

        try:
            response = self._client.request(**kwargs)
        except httpx.TimeoutException:
            return ZendResponse(
                data=None,
                error=TimeoutError(f"Request timed out after {int(self._timeout * 1000)}ms"),
            )
        except httpx.HTTPError as exc:
            return ZendResponse(data=None, error=ApplicationError(str(exc)))

        return self._handle_response(response, cast_to)

    def _handle_response(
        self,
        response: httpx.Response,
        cast_to: type[T] | TypeAdapter[T] | None,
    ) -> ZendResponse[T]:
        json_body = _parse_json(response)

        if response.is_error:
            return ZendResponse(
                data=None,
                error=ZendError.from_http(
                    response.status_code,
                    json_body,
                    response.text,
                    response.reason_phrase,
                ),
            )

        normalized = normalize_response(json_body)
        try:
            data = _cast(normalized, cast_to)
        except Exception as exc:  # noqa: BLE001 — surface as application_error
            return ZendResponse(data=None, error=ApplicationError(str(exc)))
        return ZendResponse(data=data, error=None)


class AsyncHttpClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float,
        headers: dict[str, str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json",
                "User-Agent": f"usezend-python/{VERSION}",
                **(headers or {}),
            },
            transport=transport,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        json_body: Any = None,
        pass_through: list[str] | None = None,
        files: Any = None,
        cast_to: type[T] | TypeAdapter[T] | None = None,
    ) -> ZendResponse[T]:
        params = None
        if query:
            params = {k: v for k, v in query.items() if v is not None}

        kwargs: dict[str, Any] = {"method": method, "url": path, "params": params}
        if files is not None:
            kwargs["files"] = files
        elif json_body is not None:
            kwargs["json"] = _dump_body(json_body, pass_through)

        try:
            response = await self._client.request(**kwargs)
        except httpx.TimeoutException:
            return ZendResponse(
                data=None,
                error=TimeoutError(f"Request timed out after {int(self._timeout * 1000)}ms"),
            )
        except httpx.HTTPError as exc:
            return ZendResponse(data=None, error=ApplicationError(str(exc)))

        return self._handle_response(response, cast_to)

    def _handle_response(
        self,
        response: httpx.Response,
        cast_to: type[T] | TypeAdapter[T] | None,
    ) -> ZendResponse[T]:
        json_body = _parse_json(response)

        if response.is_error:
            return ZendResponse(
                data=None,
                error=ZendError.from_http(
                    response.status_code,
                    json_body,
                    response.text,
                    response.reason_phrase,
                ),
            )

        normalized = normalize_response(json_body)
        try:
            data = _cast(normalized, cast_to)
        except Exception as exc:  # noqa: BLE001
            return ZendResponse(data=None, error=ApplicationError(str(exc)))
        return ZendResponse(data=data, error=None)
