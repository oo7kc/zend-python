from __future__ import annotations

import json

import httpx
import pytest

from zend import ApplicationError, AsyncZend, TimeoutError, Zend
from zend._client import HttpClient
from zend._normalize import normalize_response
from zend.resources.emails import Emails


def _client(transport: httpx.MockTransport, **kwargs) -> HttpClient:
    return HttpClient(
        api_key="sent_live_x",
        base_url="https://api.test",
        timeout=5.0,
        transport=transport,
        **kwargs,
    )


class TestHttpClient:
    def test_sends_api_key_and_snake_case_body(self) -> None:
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["method"] = request.method
            captured["headers"] = dict(request.headers)
            captured["body"] = json.loads(request.content)
            return httpx.Response(200, json={"estimated_cost": 0.02, "id": "m1", "status": "queued"})

        client = _client(httpx.MockTransport(handler))
        res = client.request(
            "POST",
            "/messages",
            json_body={
                "preferred_channels": ["sms"],
                "template_params": {"firstName": "J"},
                "to": "+1",
            },
            pass_through=["template_params"],
            cast_to=dict,
        )

        assert res.error is None
        assert res.data == {"estimated_cost": 0.02, "id": "m1", "status": "queued"}
        assert captured["url"] == "https://api.test/messages"
        assert captured["method"] == "POST"
        assert captured["headers"]["x-api-key"] == "sent_live_x"
        assert captured["headers"]["user-agent"].startswith("usezend-python/")
        assert captured["body"] == {
            "preferred_channels": ["sms"],
            "template_params": {"firstName": "J"},
            "to": "+1",
        }

    def test_maps_4xx_to_zend_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                422,
                json={
                    "statusCode": 422,
                    "message": "Invalid recipient",
                    "error": "validation_error",
                },
            )

        res = _client(httpx.MockTransport(handler)).request("POST", "/messages", json_body={})
        assert res.data is None
        assert res.error is not None
        assert res.error.status_code == 422
        assert str(res.error) == "Invalid recipient"
        assert res.error.name == "validation_error"

    def test_application_error_on_transport_failure(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("boom")

        res = _client(httpx.MockTransport(handler)).request("GET", "/messages")
        assert res.data is None
        assert isinstance(res.error, ApplicationError)
        assert res.error.name == "application_error"
        assert "boom" in str(res.error)

    def test_builds_query_ignoring_undefined(self) -> None:
        captured: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(str(request.url))
            return httpx.Response(200, json={"messages": [], "total": 0})

        _client(httpx.MockTransport(handler)).request(
            "GET", "/messages", query={"limit": 10, "status": None}
        )
        assert captured[0] == "https://api.test/messages?limit=10"

    def test_non_json_error_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(502, text="<html>502 Bad Gateway</html>")

        res = _client(httpx.MockTransport(handler)).request("GET", "/messages")
        assert res.data is None
        assert res.error is not None
        assert res.error.status_code == 502
        assert res.error.name == "api_error"

    def test_timeout_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("timed out")

        res = _client(httpx.MockTransport(handler)).request("GET", "/messages")
        assert res.data is None
        assert isinstance(res.error, TimeoutError)
        assert res.error.name == "timeout"
        assert "5000ms" in str(res.error)

    def test_normalizes_mongo_document(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "_id": "e1",
                    "__v": 0,
                    "user_id": "u1",
                    "from": "a",
                    "to": "b",
                    "status": "pending",
                },
            )

        res = _client(httpx.MockTransport(handler)).request("POST", "/email/send", cast_to=dict)
        assert res.error is None
        assert res.data == {
            "id": "e1",
            "user_id": "u1",
            "from": "a",
            "to": "b",
            "status": "pending",
        }
        assert "_id" not in res.data  # type: ignore[operator]
        assert "__v" not in res.data  # type: ignore[operator]


class TestNormalize:
    def test_preserves_existing_id(self) -> None:
        assert normalize_response({"_id": "x", "id": "keep", "__v": 1}) == {"id": "keep"}


class TestZend:
    def test_requires_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ZEND_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key is required"):
            Zend()

    def test_reads_api_key_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ZEND_API_KEY", "sent_live_env")
        zend = Zend()
        assert isinstance(zend.emails, Emails)
        zend.close()

    def test_exposes_all_resources(self) -> None:
        zend = Zend("sent_live_x")
        assert zend.emails is not None
        assert zend.messages is not None
        assert zend.voice is not None
        assert zend.templates is not None
        zend.close()


class TestMessagesResource:
    def test_send(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["to"] == "+233201234567"
            assert body["preferred_channels"] == ["sms"]
            assert body["template_params"] == {"first_name": "John"}
            return httpx.Response(200, json={"id": "m1", "status": "queued", "estimated_cost": 0.01})

        zend = Zend("k", base_url="https://api.test", transport=httpx.MockTransport(handler))
        res = zend.messages.send(
            to="+233201234567",
            body="Hi",
            preferred_channels=["sms"],
            template_params={"first_name": "John"},
        )
        assert res.error is None
        assert res.data is not None
        assert res.data.id == "m1"
        assert res.data.status == "queued"
        assert res.data.estimated_cost == 0.01
        zend.close()

    def test_get_cancel_retry(self) -> None:
        paths: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            paths.append(f"{request.method} {request.url.path}")
            return httpx.Response(
                200,
                json={"id": "m1", "status": "cancelled" if "cancel" in request.url.path else "queued"},
            )

        zend = Zend("k", base_url="https://api.test", transport=httpx.MockTransport(handler))
        assert zend.messages.get("m1").data is not None
        assert zend.messages.cancel("m1").data is not None
        assert zend.messages.retry("m1").data is not None
        assert paths == [
            "GET /messages/m1",
            "PUT /messages/m1/cancel",
            "PUT /messages/m1/retry",
        ]
        zend.close()


class TestEmailsResource:
    def test_send_encodes_bytes_attachment(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["from"] == "a@b.com"
            assert body["attachments"][0]["content"] == "aGVsbG8="  # base64("hello")
            assert body["attachments"][0]["content_type"] == "text/plain"
            return httpx.Response(200, json={"id": "e1", "status": "queued"})

        zend = Zend("k", base_url="https://api.test", transport=httpx.MockTransport(handler))
        res = zend.emails.send(
            **{
                "from": "a@b.com",
                "to": "u@g.com",
                "subject": "Hi",
                "html": "<p>x</p>",
                "attachments": [
                    {"filename": "a.txt", "content": b"hello", "content_type": "text/plain"}
                ],
            }
        )
        assert res.error is None
        assert res.data is not None
        assert res.data.id == "e1"
        zend.close()


class TestVoiceAndTemplates:
    def test_voice_send_and_upload(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/voice/upload":
                assert request.headers["content-type"].startswith("multipart/form-data")
                return httpx.Response(200, json={"url": "https://cdn.example.com/a.mp3"})
            return httpx.Response(
                200,
                json={
                    "batch_id": "b1",
                    "recipients": 1,
                    "message_ids": ["m1"],
                    "status": "queued",
                },
            )

        zend = Zend("k", base_url="https://api.test", transport=httpx.MockTransport(handler))
        send = zend.voice.send(recipients=["+1"], text="Hi", voice="female")
        assert send.data is not None
        assert send.data.batch_id == "b1"
        up = zend.voice.upload(b"audio", "a.mp3")
        assert up.data is not None
        assert up.data.url.endswith("a.mp3")
        zend.close()

    def test_templates_list_and_get(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/templates":
                assert request.url.params["category"] == "transactional"
                return httpx.Response(
                    200,
                    json={
                        "templates": [
                            {
                                "id": "welcome",
                                "name": "Welcome",
                                "category": "transactional",
                                "status": "active",
                            }
                        ],
                        "total": 1,
                    },
                )
            return httpx.Response(
                200,
                json={
                    "id": "welcome",
                    "name": "Welcome",
                    "category": "transactional",
                    "status": "active",
                },
            )

        zend = Zend("k", base_url="https://api.test", transport=httpx.MockTransport(handler))
        listed = zend.templates.list(category="transactional", status="active", limit=20)
        assert listed.data is not None
        assert listed.data.total == 1
        got = zend.templates.get("welcome")
        assert got.data is not None
        assert got.data.name == "Welcome"
        zend.close()


@pytest.mark.asyncio
class TestAsyncZend:
    async def test_async_send_with_respx(self) -> None:
        import respx

        with respx.mock(base_url="https://api.test") as router:
            router.post("/messages").mock(
                return_value=httpx.Response(200, json={"id": "m1", "status": "queued"})
            )
            async with AsyncZend("k", base_url="https://api.test") as zend:
                res = await zend.messages.send(to="+1", body="Hi")
            assert res.error is None
            assert res.data is not None
            assert res.data.id == "m1"

    async def test_async_emails_list(self) -> None:
        import respx

        with respx.mock(base_url="https://api.test") as router:
            router.get("/email/messages").mock(
                return_value=httpx.Response(
                    200,
                    json=[{"id": "e1", "status": "delivered", "from": "a@b.com"}],
                )
            )
            async with AsyncZend("k", base_url="https://api.test") as zend:
                res = await zend.emails.list(limit=10)
            assert res.error is None
            assert res.data is not None
            assert res.data[0].id == "e1"
            assert res.data[0].from_ == "a@b.com"
