from __future__ import annotations

from typing import Any

from zend._client import AsyncHttpClient, HttpClient
from zend._response import ZendResponse
from zend.types.common import ListParams
from zend.types.messages import (
    BulkMessageOptions,
    BulkMessageResult,
    Message,
    MessageList,
    SendMessageOptions,
    SendMessageResult,
)

_PASS_THROUGH = ["template_params"]


class Messages:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def send(
        self, options: SendMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[SendMessageResult]:
        body = SendMessageOptions.model_validate(options or kwargs)
        return self._client.request(
            "POST",
            "/messages",
            json_body=body,
            pass_through=_PASS_THROUGH,
            cast_to=SendMessageResult,
        )

    def send_bulk(
        self, options: BulkMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[BulkMessageResult]:
        body = BulkMessageOptions.model_validate(options or kwargs)
        return self._client.request(
            "POST",
            "/messages/bulk",
            json_body=body,
            pass_through=_PASS_THROUGH,
            cast_to=BulkMessageResult,
        )

    def get(self, id: str) -> ZendResponse[Message]:
        return self._client.request("GET", f"/messages/{id}", cast_to=Message)

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

    async def send(
        self, options: SendMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[SendMessageResult]:
        body = SendMessageOptions.model_validate(options or kwargs)
        return await self._client.request(
            "POST",
            "/messages",
            json_body=body,
            pass_through=_PASS_THROUGH,
            cast_to=SendMessageResult,
        )

    async def send_bulk(
        self, options: BulkMessageOptions | None = None, **kwargs: Any
    ) -> ZendResponse[BulkMessageResult]:
        body = BulkMessageOptions.model_validate(options or kwargs)
        return await self._client.request(
            "POST",
            "/messages/bulk",
            json_body=body,
            pass_through=_PASS_THROUGH,
            cast_to=BulkMessageResult,
        )

    async def get(self, id: str) -> ZendResponse[Message]:
        return await self._client.request("GET", f"/messages/{id}", cast_to=Message)

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
