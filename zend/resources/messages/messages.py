from __future__ import annotations

from typing import Any, overload

from typing_extensions import Unpack

from zend.client.http_client import AsyncHttpClient, HttpClient
from zend.common.types import ListParams, ListParamsKwargs, ZendResponse
from zend.common.url import path_segment
from zend.common.validation import resolve_optional_options, resolve_options
from zend.resources.messages.types import (
    BulkMessageKwargs,
    BulkMessageOptions,
    BulkMessageResult,
    Message,
    MessageList,
    SendMessageKwargs,
    SendMessageOptions,
    SendMessageResult,
)


class Messages:
    _client: HttpClient

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @overload
    def send(self, options: SendMessageOptions) -> ZendResponse[SendMessageResult]: ...

    @overload
    def send(self, **kwargs: Unpack[SendMessageKwargs]) -> ZendResponse[SendMessageResult]: ...

    def send(
        self, options: SendMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[SendMessageResult]:
        body = resolve_options(SendMessageOptions, options, kwargs)
        return self._client.request(
            "POST",
            "/messages",
            json_body=body,
            cast_to=SendMessageResult,
        )

    @overload
    def send_bulk(self, options: BulkMessageOptions) -> ZendResponse[BulkMessageResult]: ...

    @overload
    def send_bulk(self, **kwargs: Unpack[BulkMessageKwargs]) -> ZendResponse[BulkMessageResult]: ...

    def send_bulk(
        self, options: BulkMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[BulkMessageResult]:
        body = resolve_options(BulkMessageOptions, options, kwargs)
        return self._client.request(
            "POST",
            "/messages/bulk",
            json_body=body,
            cast_to=BulkMessageResult,
        )

    def get(self, id: str) -> ZendResponse[Message]:
        return self._client.request("GET", f"/messages/{path_segment(id)}", cast_to=Message)

    @overload
    def list(self, params: ListParams) -> ZendResponse[MessageList]: ...

    @overload
    def list(self, **kwargs: Unpack[ListParamsKwargs]) -> ZendResponse[MessageList]: ...

    def list(self, params: ListParams | None = None, **kwargs: Any) -> ZendResponse[MessageList]:
        query = resolve_optional_options(ListParams, params, kwargs)
        return self._client.request(
            "GET",
            "/messages",
            query=query.to_query() if query else None,
            cast_to=MessageList,
        )

    def cancel(self, id: str) -> ZendResponse[Message]:
        return self._client.request("PUT", f"/messages/{path_segment(id)}/cancel", cast_to=Message)

    def retry(self, id: str) -> ZendResponse[Message]:
        return self._client.request("PUT", f"/messages/{path_segment(id)}/retry", cast_to=Message)


class AsyncMessages:
    _client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    @overload
    async def send(self, options: SendMessageOptions) -> ZendResponse[SendMessageResult]: ...

    @overload
    async def send(
        self, **kwargs: Unpack[SendMessageKwargs]
    ) -> ZendResponse[SendMessageResult]: ...

    async def send(
        self, options: SendMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[SendMessageResult]:
        body = resolve_options(SendMessageOptions, options, kwargs)
        return await self._client.request(
            "POST",
            "/messages",
            json_body=body,
            cast_to=SendMessageResult,
        )

    @overload
    async def send_bulk(self, options: BulkMessageOptions) -> ZendResponse[BulkMessageResult]: ...

    @overload
    async def send_bulk(
        self, **kwargs: Unpack[BulkMessageKwargs]
    ) -> ZendResponse[BulkMessageResult]: ...

    async def send_bulk(
        self, options: BulkMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[BulkMessageResult]:
        body = resolve_options(BulkMessageOptions, options, kwargs)
        return await self._client.request(
            "POST",
            "/messages/bulk",
            json_body=body,
            cast_to=BulkMessageResult,
        )

    async def get(self, id: str) -> ZendResponse[Message]:
        return await self._client.request("GET", f"/messages/{path_segment(id)}", cast_to=Message)

    @overload
    async def list(self, params: ListParams) -> ZendResponse[MessageList]: ...

    @overload
    async def list(self, **kwargs: Unpack[ListParamsKwargs]) -> ZendResponse[MessageList]: ...

    async def list(
        self, params: ListParams | None = None, **kwargs: Any
    ) -> ZendResponse[MessageList]:
        query = resolve_optional_options(ListParams, params, kwargs)
        return await self._client.request(
            "GET",
            "/messages",
            query=query.to_query() if query else None,
            cast_to=MessageList,
        )

    async def cancel(self, id: str) -> ZendResponse[Message]:
        return await self._client.request(
            "PUT", f"/messages/{path_segment(id)}/cancel", cast_to=Message
        )

    async def retry(self, id: str) -> ZendResponse[Message]:
        return await self._client.request(
            "PUT", f"/messages/{path_segment(id)}/retry", cast_to=Message
        )
