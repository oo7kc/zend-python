from __future__ import annotations

import base64
from typing import Any, overload

from zend.client.http_client import AsyncHttpClient, HttpClient
from zend.common.types import ListParams, ZendResponse
from zend.resources.emails.types import Email, EmailList, SendEmailOptions


def _encode_attachments(options: SendEmailOptions) -> dict[str, Any]:
    data = options.model_dump(by_alias=True, exclude_none=True)
    if "from_" in data and "from" not in data:
        data["from"] = data.pop("from_")
    attachments = data.get("attachments")
    if not attachments:
        return data
    encoded = []
    for item in attachments:
        content = item["content"]
        if isinstance(content, bytes):
            item = {**item, "content": base64.b64encode(content).decode("ascii")}
        encoded.append(item)
    data["attachments"] = encoded
    return data


class Emails:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @overload
    def send(self, options: SendEmailOptions) -> ZendResponse[Email]:
        ...

    @overload
    def send(self, **kwargs: Any) -> ZendResponse[Email]:
        ...

    def send(self, options: SendEmailOptions | None = None, **kwargs: Any) -> ZendResponse[Email]:
        body = SendEmailOptions.model_validate(options or kwargs)
        return self._client.request(
            "POST",
            "/email/send",
            json_body=_encode_attachments(body),
            cast_to=Email,
        )

    def get(self, id: str) -> ZendResponse[Email]:
        return self._client.request("GET", f"/email/messages/{id}", cast_to=Email)

    @overload
    def list(self, params: ListParams) -> ZendResponse[EmailList]:
        ...

    @overload
    def list(self, **kwargs: Any) -> ZendResponse[EmailList]:
        ...

    def list(self, params: ListParams | None = None, **kwargs: Any) -> ZendResponse[EmailList]:
        query = ListParams.model_validate(params or kwargs) if (params or kwargs) else None
        return self._client.request(
            "GET",
            "/email/messages",
            query=query.to_query() if query else None,
            cast_to=EmailList,
        )


class AsyncEmails:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    @overload
    async def send(self, options: SendEmailOptions) -> ZendResponse[Email]:
        ...

    @overload
    async def send(self, **kwargs: Any) -> ZendResponse[Email]:
        ...

    async def send(
        self, options: SendEmailOptions | None = None, **kwargs: Any
    ) -> ZendResponse[Email]:
        body = SendEmailOptions.model_validate(options or kwargs)
        return await self._client.request(
            "POST",
            "/email/send",
            json_body=_encode_attachments(body),
            cast_to=Email,
        )

    async def get(self, id: str) -> ZendResponse[Email]:
        return await self._client.request("GET", f"/email/messages/{id}", cast_to=Email)

    @overload
    async def list(self, params: ListParams) -> ZendResponse[EmailList]:
        ...

    @overload
    async def list(self, **kwargs: Any) -> ZendResponse[EmailList]:
        ...

    async def list(
        self, params: ListParams | None = None, **kwargs: Any
    ) -> ZendResponse[EmailList]:
        query = ListParams.model_validate(params or kwargs) if (params or kwargs) else None
        return await self._client.request(
            "GET",
            "/email/messages",
            query=query.to_query() if query else None,
            cast_to=EmailList,
        )
