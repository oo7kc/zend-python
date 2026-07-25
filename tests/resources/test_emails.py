"""Emails resource — mirrors zend-node/test/resources/emails.test.ts."""

from __future__ import annotations

import base64
import json
from typing import Any

import httpx

from zend.client.http_client import HttpClient
from zend.resources.emails import Emails


def _client(handler) -> HttpClient:
    return HttpClient(
        api_key="k",
        base_url="https://api.test",
        timeout=5.0,
        transport=httpx.MockTransport(handler),
    )


class TestEmails:
    def test_send_posts_email_send_and_returns_data(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["method"] = request.method
            return httpx.Response(200, json={"id": "e1"})

        res = Emails(_client(handler)).send(
            **{"from": "a@x.com", "to": "b@y.com", "subject": "hi", "html": "<p>ok</p>"}
        )

        assert res.data is not None
        assert res.data.id == "e1"
        assert captured["url"] == "https://api.test/email/send"
        assert captured["method"] == "POST"

    def test_get_gets_email_messages_id(self) -> None:
        captured: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(str(request.url))
            return httpx.Response(200, json={"id": "e1"})

        Emails(_client(handler)).get("e1")
        assert captured[0] == "https://api.test/email/messages/e1"

    def test_send_converts_bytes_attachment_to_base64(self) -> None:
        captured: dict[str, Any] = {}
        pdf = b"%PDF-1.4"

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return httpx.Response(200, json={"id": "e2"})

        Emails(_client(handler)).send(
            **{
                "from": "a@x.com",
                "to": "b@y.com",
                "subject": "inv",
                "html": "<p>ok</p>",
                "attachments": [
                    {
                        "filename": "inv.pdf",
                        "content": pdf,
                        "content_type": "application/pdf",
                    }
                ],
            }
        )

        assert captured["body"]["attachments"] == [
            {
                "filename": "inv.pdf",
                "content": base64.b64encode(pdf).decode("ascii"),
                "content_type": "application/pdf",
            }
        ]

    def test_send_passes_base64_string_attachment_unchanged(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return httpx.Response(200, json={"id": "e3"})

        Emails(_client(handler)).send(
            **{
                "from": "a@x.com",
                "to": "b@y.com",
                "subject": "inv",
                "html": "<p>ok</p>",
                "attachments": [{"filename": "inv.pdf", "content": "JVBERi0xLjQ="}],
            }
        )

        assert captured["body"]["attachments"] == [
            {"filename": "inv.pdf", "content": "JVBERi0xLjQ="}
        ]

    def test_send_omits_attachments_key_when_none_given(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return httpx.Response(200, json={"id": "e4"})

        Emails(_client(handler)).send(
            **{"from": "a@x.com", "to": "b@y.com", "subject": "hi", "html": "<p>ok</p>"}
        )

        assert "attachments" not in captured["body"]
