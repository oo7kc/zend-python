"""Async resource parity tests."""

from __future__ import annotations

import io
import threading

import httpx
import pytest

from zend import AsyncZend


class EventLoopGuardedFile(io.BytesIO):
    """Fail if a file read happens on the thread running the async test."""

    def __init__(self, value: bytes, event_loop_thread: int) -> None:
        super().__init__(value)
        self.event_loop_thread = event_loop_thread
        self.read_threads: list[int] = []

    def read(self, size: int = -1) -> bytes:
        thread = threading.get_ident()
        self.read_threads.append(thread)
        assert thread != self.event_loop_thread
        return super().read(size)


@pytest.mark.asyncio
async def test_async_bulk_voice_upload_and_template_get() -> None:
    requests: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append((request.method, request.url.path))
        if request.url.path == "/messages/bulk":
            return httpx.Response(200, json={"total": 1, "queued": 1})
        if request.url.path == "/voice/send":
            return httpx.Response(
                200,
                json={
                    "batch_id": "b1",
                    "recipients": 1,
                    "message_ids": ["m1"],
                    "status": "queued",
                },
            )
        if request.url.path == "/voice/upload":
            return httpx.Response(200, json={"url": "https://cdn.test/audio.mp3"})
        if request.url.path == "/templates/welcome":
            return httpx.Response(
                200,
                json={
                    "id": "welcome",
                    "name": "Welcome",
                    "category": "transactional",
                    "status": "active",
                },
            )
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    async with AsyncZend(
        "k",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    ) as zend:
        audio = EventLoopGuardedFile(b"audio", threading.get_ident())
        bulk = await zend.messages.send_bulk(messages=[{"to": "+1", "body": "hello"}])
        voice = await zend.voice.send(recipients=["+1"], text="hello")
        upload = await zend.voice.upload(audio, "message.mp3")
        template = await zend.templates.get("welcome")

    assert bulk.error is None
    assert voice.error is None
    assert upload.unwrap().url == "https://cdn.test/audio.mp3"
    assert audio.read_threads
    assert template.unwrap().id == "welcome"
    assert requests == [
        ("POST", "/messages/bulk"),
        ("POST", "/voice/send"),
        ("POST", "/voice/upload"),
        ("GET", "/templates/welcome"),
    ]
