from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

import httpx

from zend.client.http_client import AsyncHttpClient, HttpClient
from zend.common.constants import DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from zend.resources.emails import AsyncEmails, Emails
from zend.resources.messages import AsyncMessages, Messages
from zend.resources.templates import AsyncTemplates, Templates
from zend.resources.voice import AsyncVoice, Voice


def _resolve_api_key(api_key: str | None) -> str:
    key = api_key if api_key is not None else os.environ.get("ZEND_API_KEY")
    if not key:
        raise ValueError(
            "Zend: an API key is required. Pass it to `Zend(api_key)` or set the "
            + "ZEND_API_KEY environment variable."
        )
    return key


def _resolve_base_url(base_url: str | None) -> str:
    return base_url or os.environ.get("ZEND_BASE_URL") or DEFAULT_BASE_URL


class Zend:
    """Synchronous Zend API client (experimental development version)."""

    _client: HttpClient
    emails: Emails
    messages: Messages
    voice: Voice
    templates: Templates

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Mapping[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = HttpClient(
            api_key=_resolve_api_key(api_key),
            base_url=_resolve_base_url(base_url),
            timeout=timeout,
            headers=dict(headers) if headers else None,
            transport=transport,
        )
        self.emails = Emails(self._client)
        self.messages = Messages(self._client)
        self.voice = Voice(self._client)
        self.templates = Templates(self._client)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Zend:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncZend:
    """Asynchronous Zend API client (experimental development version)."""

    _client: AsyncHttpClient
    emails: AsyncEmails
    messages: AsyncMessages
    voice: AsyncVoice
    templates: AsyncTemplates

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Mapping[str, str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = AsyncHttpClient(
            api_key=_resolve_api_key(api_key),
            base_url=_resolve_base_url(base_url),
            timeout=timeout,
            headers=dict(headers) if headers else None,
            transport=transport,
        )
        self.emails = AsyncEmails(self._client)
        self.messages = AsyncMessages(self._client)
        self.voice = AsyncVoice(self._client)
        self.templates = AsyncTemplates(self._client)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncZend:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
