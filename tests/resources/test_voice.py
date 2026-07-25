"""Voice resource — mirrors zend-node/test/resources/voice.test.ts."""

from __future__ import annotations

import json

import httpx

from zend.client.http_client import HttpClient
from zend.resources.voice import Voice


def _client(handler) -> HttpClient:
    return HttpClient(
        api_key="k",
        base_url="https://api.test",
        timeout=5.0,
        transport=httpx.MockTransport(handler),
    )


class TestVoice:
    def test_send_posts_voice_send_and_snake_cases_nested_fallback(self) -> None:
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return httpx.Response(
                200,
                json={
                    "batch_id": "b1",
                    "recipients": 1,
                    "message_ids": ["m1"],
                    "status": "queued",
                },
            )

        res = Voice(_client(handler)).send(
            recipients=["+233201234567"],
            text="hello",
            fallback={"sms": True, "sms_text": "hello", "sender_id": "Brand"},
        )

        assert res.data is not None
        assert res.data.batch_id == "b1"
        assert captured["body"] == {
            "recipients": ["+233201234567"],
            "text": "hello",
            "fallback": {"sms": True, "sms_text": "hello", "sender_id": "Brand"},
        }

    def test_upload_sends_multipart_to_voice_upload(self) -> None:
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["content_type"] = request.headers.get("content-type", "")
            return httpx.Response(200, json={"url": "https://cdn/x.mp3"})

        Voice(_client(handler)).upload(b"audio", "x.mp3")
        assert captured["url"] == "https://api.test/voice/upload"
        assert captured["content_type"].startswith("multipart/form-data")

    def test_get_returns_batch_and_recipients_with_normalized_ids(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "batch": {
                        "batch_id": "voice_1",
                        "status": "failed",
                        "counts": {
                            "total": 1,
                            "answered": 0,
                            "no_answer": 0,
                            "busy": 0,
                            "failed": 0,
                            "fallback_sent": 0,
                        },
                    },
                    "recipients": [
                        {
                            "_id": "r1",
                            "to": "233201234567",
                            "status": "failed",
                            "voice_refunded": False,
                            "fallback_sms_sent": False,
                        }
                    ],
                },
            )

        res = Voice(_client(handler)).get("voice_1")
        assert res.data is not None
        assert res.data.batch.batch_id == "voice_1"
        assert res.data.batch.counts is not None
        assert res.data.batch.counts.fallback_sent == 0
        assert res.data.recipients[0].id == "r1"
        assert res.data.recipients[0].fallback_sms_sent is False

    def test_list_returns_batches_plus_pagination(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "batches": [{"batch_id": "voice_1", "status": "failed"}],
                    "total": 6,
                    "page": 1,
                    "limit": 2,
                },
            )

        res = Voice(_client(handler)).list(limit=2)
        assert res.data is not None
        assert res.data.batches[0].batch_id == "voice_1"
        assert res.data.total == 6
        assert res.data.limit == 2
