"""Messages resource tests."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
from pydantic import ValidationError

from zend.client.http_client import HttpClient
from zend.resources.messages import Messages
from zend.resources.messages.types import SendMessageOptions


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

    def test_send_bulk_serializes_nested_items(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return httpx.Response(200, json={"total": 1, "queued": 1})

        res = Messages(_client(handler)).send_bulk(
            messages=[
                {
                    "to": "+233201234567",
                    "body": "Hi",
                    "template_params": {"firstName": "Ama"},
                }
            ],
            preferred_channels=["sms"],
        )

        assert res.error is None
        assert captured["body"] == {
            "messages": [
                {
                    "to": "+233201234567",
                    "body": "Hi",
                    "template_params": {"firstName": "Ama"},
                }
            ],
            "preferred_channels": ["sms"],
        }

    def test_unknown_keyword_is_rejected_instead_of_dropped(self) -> None:
        with pytest.raises(ValidationError, match="sender_idd"):
            Messages(_client(lambda request: httpx.Response(200))).send(
                to="+233201234567",
                body="Hi",
                sender_idd="Brand",  # type: ignore[call-overload]
            )

    def test_options_and_keyword_arguments_cannot_be_mixed(self) -> None:
        options = SendMessageOptions(to="+233201234567", body="original")

        with pytest.raises(TypeError, match="not both"):
            Messages(_client(lambda request: httpx.Response(200))).send(
                options,
                body="override",  # type: ignore[call-overload]
            )

    def test_get_percent_encodes_opaque_id(self) -> None:
        captured: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(str(request.url))
            return httpx.Response(200, json={"id": "m1", "status": "queued"})

        Messages(_client(handler)).get("abc?admin=true/child")

        assert captured[0] == ("https://api.test/messages/abc%3Fadmin%3Dtrue%2Fchild")

    def test_unknown_response_status_is_preserved(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"id": "m1", "status": "paused"})

        res = Messages(_client(handler)).get("m1")

        assert res.error is None
        assert res.data is not None
        assert res.data.status == "paused"

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
