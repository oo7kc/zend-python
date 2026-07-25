from __future__ import annotations

from typing import Any, overload

from zend.client.http_client import AsyncHttpClient, HttpClient
from zend.common.types import ListParams, ZendResponse
from zend.resources.messages.types import (
    BulkMessageOptions,
    BulkMessageResult,
    Message,
    MessageList,
    SendMessageOptions,
    SendMessageResult,
)


class Messages:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @overload
    def send(self, options: SendMessageOptions) -> ZendResponse[SendMessageResult]:
        ...

    @overload
    def send(self, **kwargs: Any) -> ZendResponse[SendMessageResult]:
        ...

    def send(
        self, options: SendMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[SendMessageResult]:
        body = SendMessageOptions.model_validate(options or kwargs)
        return self._client.request(
            "POST",
            "/messages",
            json_body=body,
            cast_to=SendMessageResult,
        )

    @overload
    def send_bulk(self, options: BulkMessageOptions) -> ZendResponse[BulkMessageResult]:
        ...

    @overload
    def send_bulk(self, **kwargs: Any) -> ZendResponse[BulkMessageResult]:
        ...

    def send_bulk(
        self, options: BulkMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[BulkMessageResult]:
        body = BulkMessageOptions.model_validate(options or kwargs)
        return self._client.request(
            "POST",
            "/messages/bulk",
            json_body=body,
            cast_to=BulkMessageResult,
        )

    def get(self, id: str) -> ZendResponse[Message]:
        return self._client.request("GET", f"/messages/{id}", cast_to=Message)

    @overload
    def list(self, params: ListParams) -> ZendResponse[MessageList]:
        ...

    @overload
    def list(self, **kwargs: Any) -> ZendResponse[MessageList]:
        ...

    def list(self, params: ListParams | None = None, **kwargs: Any) -> ZendResponse[MessageList]:
        query = ListParams.model_validate(params or kwargs) if (params or kwargs) else None
        return self._client.request(
            "GET",
            "/messages",
            query=query.to_query() if query else None,
            cast_to=MessageList,
        )

    def cancel(self, id: str) -> ZendResponse[Message]:
        return self._client.request("PUT", f"/messages/{id}/cancel", cast_to=Message)

    def retry(self, id: str) -> ZendResponse[Message]:
        return self._client.request("PUT", f"/messages/{id}/retry", cast_to=Message)


class AsyncMessages:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    @overload
    async def send(self, options: SendMessageOptions) -> ZendResponse[SendMessageResult]:
        ...

    @overload
    async def send(self, **kwargs: Any) -> ZendResponse[SendMessageResult]:
        ...

    async def send(
        self, options: SendMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[SendMessageResult]:
        body = SendMessageOptions.model_validate(options or kwargs)
        return await self._client.request(
            "POST",
            "/messages",
            json_body=body,
            cast_to=SendMessageResult,
        )

    @overload
    async def send_bulk(
        self, options: BulkMessageOptions
    ) -> ZendResponse[BulkMessageResult]:
        ...

    @overload
    async def send_bulk(self, **kwargs: Any) -> ZendResponse[BulkMessageResult]:
        ...

    async def send_bulk(
        self, options: BulkMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[BulkMessageResult]:
        body = BulkMessageOptions.model_validate(options or kwargs)
        return await self._client.request(
            "POST",
            "/messages/bulk",
            json_body=body,
            cast_to=BulkMessageResult,
        )

    async def get(self, id: str) -> ZendResponse[Message]:
        return await self._client.request("GET", f"/messages/{id}", cast_to=Message)

    @overload
    async def list(self, params: ListParams) -> ZendResponse[MessageList]:
        ...

    @overload
    async def list(self, **kwargs: Any) -> ZendResponse[MessageList]:
        ...

    async def list(
        self, params: ListParams | None = None, **kwargs: Any
    ) -> ZendResponse[MessageList]:
        query = ListParams.model_validate(params or kwargs) if (params or kwargs) else None
        return await self._client.request(
            "GET",
            "/messages",
            query=query.to_query() if query else None,
            cast_to=MessageList,
        )

    async def cancel(self, id: str) -> ZendResponse[Message]:
        return await self._client.request("PUT", f"/messages/{id}/cancel", cast_to=Message)

    async def retry(self, id: str) -> ZendResponse[Message]:
        return await self._client.request("PUT", f"/messages/{id}/retry", cast_to=Message)
