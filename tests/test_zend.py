"""Facade tests — mirrors zend-node/test/zend.test.ts."""

from __future__ import annotations

import pytest

from zend import AsyncZend, Zend
from zend.resources.emails import Emails


class TestZend:
    def test_throws_when_no_api_key_and_none_in_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ZEND_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key is required"):
            Zend()

    def test_reads_api_key_from_env_when_arg_omitted(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ZEND_API_KEY", "sent_live_env")
        zend = Zend()
        assert isinstance(zend.emails, Emails)
        zend.close()

    def test_exposes_all_four_resources(self) -> None:
        zend = Zend("sent_live_x")
        assert isinstance(zend.emails, Emails)
        assert zend.messages is not None
        assert zend.voice is not None
        assert zend.templates is not None
        zend.close()


class TestAsyncZend:
    """Python-only: Node has a single async facade; we keep parity coverage here."""

    @pytest.mark.asyncio
    async def test_async_send_with_respx(self) -> None:
        import httpx
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

    @pytest.mark.asyncio
    async def test_async_emails_list(self) -> None:
        import httpx
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
