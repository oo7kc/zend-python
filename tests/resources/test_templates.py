"""Templates resource tests."""

from __future__ import annotations

import httpx

from zend.client.http_client import HttpClient
from zend.resources.templates import Templates


def _client(handler) -> HttpClient:
    return HttpClient(
        api_key="k",
        base_url="https://api.test",
        timeout=5.0,
        transport=httpx.MockTransport(handler),
    )


class TestTemplates:
    def test_list_gets_templates_with_query(self) -> None:
        captured: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(str(request.url))
            return httpx.Response(
                200,
                json={
                    "templates": [
                        {
                            "id": "t1",
                            "name": "Welcome",
                            "category": "transactional",
                            "status": "active",
                            "is_whatsapp_approved": True,
                        }
                    ],
                    "total": 1,
                },
            )

        res = Templates(_client(handler)).list(category="transactional", limit=10)

        assert res.data is not None
        assert res.data.templates[0].id == "t1"
        assert res.data.templates[0].is_whatsapp_approved is True
        assert res.data.total == 1
        assert captured[0] == "https://api.test/templates?category=transactional&limit=10"

    def test_get_gets_templates_id(self) -> None:
        captured: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(str(request.url))
            return httpx.Response(
                200,
                json={
                    "id": "t1",
                    "name": "Welcome",
                    "category": "transactional",
                    "status": "active",
                },
            )

        Templates(_client(handler)).get("t1")
        assert captured[0] == "https://api.test/templates/t1"
