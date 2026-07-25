from __future__ import annotations

from typing import Any, BinaryIO

from zend.client.http_client import AsyncHttpClient, HttpClient
from zend.common.types import ListParams, ZendResponse
from zend.resources.voice.types import (
    SendVoiceOptions,
    VoiceBatchDetail,
    VoiceBatchList,
    VoiceSendResult,
    VoiceUpload,
)


class Voice:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def send(
        self, options: SendVoiceOptions | None = None, **kwargs: Any
    ) -> ZendResponse[VoiceSendResult]:
        body = SendVoiceOptions.model_validate(options or kwargs)
        return self._client.request(
            "POST",
            "/voice/send",
            json_body=body,
            cast_to=VoiceSendResult,
        )

    def get(self, batch_id: str) -> ZendResponse[VoiceBatchDetail]:
        return self._client.request("GET", f"/voice/{batch_id}", cast_to=VoiceBatchDetail)

    def list(
        self, params: ListParams | None = None, **kwargs: Any
    ) -> ZendResponse[VoiceBatchList]:
        query = ListParams.model_validate(params or kwargs) if (params or kwargs) else None
        return self._client.request(
            "GET",
            "/voice",
            query=query.to_query() if query else None,
            cast_to=VoiceBatchList,
        )

    def upload(self, file: bytes | BinaryIO, filename: str) -> ZendResponse[VoiceUpload]:
        return self._client.request(
            "POST",
            "/voice/upload",
            files={"file": (filename, file)},
            cast_to=VoiceUpload,
        )


class AsyncVoice:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def send(
        self, options: SendVoiceOptions | None = None, **kwargs: Any
    ) -> ZendResponse[VoiceSendResult]:
        body = SendVoiceOptions.model_validate(options or kwargs)
        return await self._client.request(
            "POST",
            "/voice/send",
            json_body=body,
            cast_to=VoiceSendResult,
        )

    async def get(self, batch_id: str) -> ZendResponse[VoiceBatchDetail]:
        return await self._client.request(
            "GET", f"/voice/{batch_id}", cast_to=VoiceBatchDetail
        )

    async def list(
        self, params: ListParams | None = None, **kwargs: Any
    ) -> ZendResponse[VoiceBatchList]:
        query = ListParams.model_validate(params or kwargs) if (params or kwargs) else None
        return await self._client.request(
            "GET",
            "/voice",
            query=query.to_query() if query else None,
            cast_to=VoiceBatchList,
        )

    async def upload(
        self, file: bytes | BinaryIO, filename: str
    ) -> ZendResponse[VoiceUpload]:
        return await self._client.request(
            "POST",
            "/voice/upload",
            files={"file": (filename, file)},
            cast_to=VoiceUpload,
        )
