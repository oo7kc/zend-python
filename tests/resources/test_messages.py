"""Messages resource — mirrors zend-node/test/resources/messages.test.ts."""

from __future__ import annotations

import json
from typing import Any

import httpx

from zend.client.http_client import HttpClient
from zend.resources.messages import Messages


def _client(handler) -> HttpClient:
    return HttpClient(
        api_key="k",
        base_url="https://api.test",
        timeout=5.0,
        transport=httpx.MockTransport(handler),
    )


class TestMessages:
    def test_send_posts_messages_preserves_template_params_keys(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return httpx.Response(200, json={"id": "m1", "status": "pending"})

        res = Messages(_client(handler)).send(
            to="+233201234567",
            template_id="welcome",
            template_params={"firstName": "John"},
            preferred_channels=["whatsapp", "sms"],
            fallback_enabled=True,
        )

        assert res.data is not None
        assert res.data.id == "m1"
        assert res.data.status == "pending"
        assert captured["body"] == {
            "to": "+233201234567",
            "template_id": "welcome",
            "template_params": {"firstName": "John"},
            "preferred_channels": ["whatsapp", "sms"],
            "fallback_enabled": True,
        }

    def test_cancel_puts_cancel(self) -> None:
        captured: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append((request.method, str(request.url)))
            return httpx.Response(200, json={"id": "m1", "status": "cancelled"})

        Messages(_client(handler)).cancel("m1")
        assert captured[0] == ("PUT", "https://api.test/messages/m1/cancel")

    def test_get_returns_full_message_record_normalized(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "_id": "m1",
                    "status": "sent",
                    "channel_used": "sms",
                    "to": "+233201234567",
                    "body": "Hi",
                    "total_cost": 0.03,
                    "delivery_attempts": [
                        {
                            "channel": "sms",
                            "status": "sent",
                            "attempted_at": "2026-01-01T00:00:00Z",
                            "cost": 0.03,
                            "error_message": "",
                        }
                    ],
                    "created_at": "2026-01-01T00:00:00Z",
                    "sent_at": "2026-01-01T00:00:01Z",
                    "error_message": "",
                },
            )

        res = Messages(_client(handler)).get("m1")
        assert res.data is not None
        assert res.data.id == "m1"
        assert res.data.channel_used == "sms"
        assert res.data.total_cost == 0.03
        assert res.data.delivery_attempts is not None
        assert res.data.delivery_attempts[0].channel == "sms"

    def test_list_returns_messages_plus_pagination(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "messages": [{"_id": "m1", "status": "sent"}],
                    "total": 100,
                    "page": 1,
                    "pages": 50,
                },
            )

        res = Messages(_client(handler)).list(limit=2)
        assert res.data is not None
        assert res.data.messages[0].id == "m1"
        assert res.data.total == 100
        assert res.data.page == 1
        assert res.data.pages == 50

    def test_retry_puts_retry(self) -> None:
        captured: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append((request.method, str(request.url)))
            return httpx.Response(200, json={"id": "m1", "status": "queued"})

        Messages(_client(handler)).retry("m1")
        assert captured[0] == ("PUT", "https://api.test/messages/m1/retry")
