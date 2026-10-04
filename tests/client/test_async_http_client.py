"""AsyncHttpClient contract tests."""

from __future__ import annotations

import httpx
import pytest

from zend import APIError, ApplicationError, ZendTimeoutError
from zend.client.http_client import AsyncHttpClient


def _client(handler) -> AsyncHttpClient:
    return AsyncHttpClient(
        api_key="sent_live_x",
        base_url="https://api.test",
        timeout=5.0,
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.asyncio
async def test_async_redirect_is_an_api_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(307, json={"id": "m1", "status": "queued"})

    client = _client(handler)
    try:
        res = await client.request("GET", "/messages/m1", cast_to=dict)
    finally:
        await client.aclose()

    assert res.data is None
    assert isinstance(res.error, APIError)
    assert res.error.status_code == 307


@pytest.mark.asyncio
async def test_async_timeout_is_typed() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    client = _client(handler)
    try:
        res = await client.request("GET", "/messages")
    finally:
        await client.aclose()

    assert isinstance(res.error, ZendTimeoutError)


@pytest.mark.asyncio
async def test_async_transport_failure_is_application_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    client = _client(handler)
    try:
        res = await client.request("GET", "/messages")
    finally:
        await client.aclose()

    assert isinstance(res.error, ApplicationError)
