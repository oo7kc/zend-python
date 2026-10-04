from __future__ import annotations

import asyncio
import io
from concurrent.futures import ThreadPoolExecutor
from typing import Any, BinaryIO, overload

from typing_extensions import Unpack

from zend.client.http_client import AsyncHttpClient, HttpClient
from zend.common.types import ListParams, ListParamsKwargs, ZendResponse
from zend.common.url import path_segment
from zend.common.validation import resolve_optional_options, resolve_options
from zend.resources.voice.types import (
    SendVoiceKwargs,
    SendVoiceOptions,
    VoiceBatchDetail,
    VoiceBatchList,
    VoiceSendResult,
    VoiceUpload,
)


def _read_binary_file(file: BinaryIO) -> bytes:
    """Read an upload from the beginning without blocking the async event loop."""
    try:
        file.seek(0)
    except (OSError, io.UnsupportedOperation):
        pass
    return file.read()


class Voice:
    _client: HttpClient

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @overload
    def send(self, options: SendVoiceOptions) -> ZendResponse[VoiceSendResult]: ...

    @overload
    def send(self, **kwargs: Unpack[SendVoiceKwargs]) -> ZendResponse[VoiceSendResult]: ...

    def send(
        self, options: SendVoiceOptions | None = None, **kwargs: Any
    ) -> ZendResponse[VoiceSendResult]:
        body = resolve_options(SendVoiceOptions, options, kwargs)
        return self._client.request(
            "POST",
            "/voice/send",
            json_body=body,
            cast_to=VoiceSendResult,
        )

    def get(self, batch_id: str) -> ZendResponse[VoiceBatchDetail]:
        return self._client.request(
            "GET", f"/voice/{path_segment(batch_id)}", cast_to=VoiceBatchDetail
        )

    @overload
    def list(self, params: ListParams) -> ZendResponse[VoiceBatchList]: ...

    @overload
    def list(self, **kwargs: Unpack[ListParamsKwargs]) -> ZendResponse[VoiceBatchList]: ...

    def list(self, params: ListParams | None = None, **kwargs: Any) -> ZendResponse[VoiceBatchList]:
        query = resolve_optional_options(ListParams, params, kwargs)
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
    _client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    @overload
    async def send(self, options: SendVoiceOptions) -> ZendResponse[VoiceSendResult]: ...

    @overload
    async def send(self, **kwargs: Unpack[SendVoiceKwargs]) -> ZendResponse[VoiceSendResult]: ...

    async def send(
        self, options: SendVoiceOptions | None = None, **kwargs: Any
    ) -> ZendResponse[VoiceSendResult]:
        body = resolve_options(SendVoiceOptions, options, kwargs)
        return await self._client.request(
            "POST",
            "/voice/send",
            json_body=body,
            cast_to=VoiceSendResult,
        )

    async def get(self, batch_id: str) -> ZendResponse[VoiceBatchDetail]:
        return await self._client.request(
            "GET", f"/voice/{path_segment(batch_id)}", cast_to=VoiceBatchDetail
        )

    @overload
    async def list(self, params: ListParams) -> ZendResponse[VoiceBatchList]: ...

    @overload
    async def list(self, **kwargs: Unpack[ListParamsKwargs]) -> ZendResponse[VoiceBatchList]: ...

    async def list(
        self, params: ListParams | None = None, **kwargs: Any
    ) -> ZendResponse[VoiceBatchList]:
        query = resolve_optional_options(ListParams, params, kwargs)
        return await self._client.request(
            "GET",
            "/voice",
            query=query.to_query() if query else None,
            cast_to=VoiceBatchList,
        )

    async def upload(self, file: bytes | BinaryIO, filename: str) -> ZendResponse[VoiceUpload]:
        if isinstance(file, bytes):
            upload = file
        else:
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor(max_workers=1, thread_name_prefix="zend-upload") as executor:
                upload = await loop.run_in_executor(executor, _read_binary_file, file)
        return await self._client.request(
            "POST",
            "/voice/upload",
            files={"file": (filename, upload)},
            cast_to=VoiceUpload,
        )
