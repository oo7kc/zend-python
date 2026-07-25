"""HttpClient tests — mirrors zend-node/test/client/http-client.test.ts."""

from __future__ import annotations

import json

import httpx

from zend import ApplicationError, TimeoutError
from zend.client.http_client import HttpClient


def _client(transport: httpx.MockTransport, **kwargs) -> HttpClient:
    return HttpClient(
        api_key="sent_live_x",
        base_url="https://api.test",
        timeout=5.0,
        transport=transport,
        **kwargs,
    )


class TestHttpClientRequest:
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
