from __future__ import annotations

from typing import Any


class ZendError(Exception):
    """Base error for all Zend SDK failures.

    Returned (not raised) inside :class:`~zend.ZendResponse` for API and
    transport failures.
    """

    name: str
    status_code: int | None
    code: str | None

    def __init__(
        self,
        message: str,
        *,
        name: str | None = None,
        status_code: int | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.name = name or "ZendError"
        self.status_code = status_code
        self.code = code

    def __str__(self) -> str:
        return str(self.args[0]) if self.args else ""

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(message={self.args[0]!r}, name={self.name!r}, "
            f"status_code={self.status_code!r}, code={self.code!r})"
        )

    @classmethod
    def from_http(
        cls,
        status_code: int,
        json_body: Any | None,
        text: str,
        status_text: str = "",
    ) -> ZendError:
        """Build an error from an HTTP error response."""
        message: str
        error_name = "api_error"

        if isinstance(json_body, dict):
            raw_message = json_body.get("message")
            if isinstance(raw_message, list):
                message = ", ".join(str(m) for m in raw_message)
            elif raw_message:
                message = str(raw_message)
            elif json_body.get("error"):
                message = str(json_body["error"])
            else:
                message = text or status_text or "Request failed"
            if json_body.get("error"):
                error_name = str(json_body["error"])
        else:
            message = text or status_text or "Request failed"

        return cls._for_status(message, name=error_name, status_code=status_code)

    @classmethod
    def _for_status(cls, message: str, *, name: str, status_code: int) -> ZendError:
        if status_code == 400:
            return BadRequestError(message, name=name, status_code=status_code)
        if status_code == 401:
            return AuthenticationError(message, name=name, status_code=status_code)
        if status_code == 403:
            return PermissionDeniedError(message, name=name, status_code=status_code)
        if status_code == 404:
            return NotFoundError(message, name=name, status_code=status_code)
        if status_code == 429:
            return RateLimitError(message, name=name, status_code=status_code)
        if status_code >= 500:
            return ServerError(message, name=name, status_code=status_code)
        return APIError(message, name=name, status_code=status_code)


class APIError(ZendError):
    """HTTP-level API failure (4xx/5xx)."""

    def __init__(
        self,
        message: str,
        *,
        name: str | None = None,
        status_code: int | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(
            message, name=name or "api_error", status_code=status_code, code=code
        )


class BadRequestError(APIError):
    pass


class AuthenticationError(APIError):
    pass


class PermissionDeniedError(APIError):
    """403 Forbidden — named to avoid shadowing the builtin PermissionError."""

    pass


class NotFoundError(APIError):
    pass


class RateLimitError(APIError):
    pass


class ServerError(APIError):
    pass


class ZendTimeoutError(ZendError):
    """Request exceeded the configured timeout.

    Named ``ZendTimeoutError`` so it does not shadow the builtin ``TimeoutError``.
    """

    def __init__(
        self,
        message: str,
        *,
        name: str | None = None,
        status_code: int | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(
            message, name=name or "timeout", status_code=status_code, code=code
        )


class ApplicationError(ZendError):
    """Network or unexpected client-side failure."""

    def __init__(
        self,
        message: str,
        *,
        name: str | None = None,
        status_code: int | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(
            message,
            name=name or "application_error",
            status_code=status_code,
            code=code,
        )
