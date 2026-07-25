from __future__ import annotations

import httpx
import pytest

from zend.client.http_client import HttpClient


@pytest.fixture
def make_client():
    """Build an HttpClient wired to a MockTransport (mirrors test helpers)."""

    def _make(handler, **kwargs) -> HttpClient:
        return HttpClient(
            api_key=kwargs.pop("api_key", "k"),
            base_url=kwargs.pop("base_url", "https://api.test"),
            timeout=kwargs.pop("timeout", 5.0),
            transport=httpx.MockTransport(handler),
            **kwargs,
        )

    return _make
