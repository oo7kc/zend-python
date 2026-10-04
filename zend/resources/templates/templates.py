from __future__ import annotations

from typing import Any, overload

from typing_extensions import Unpack

from zend.client.http_client import AsyncHttpClient, HttpClient
from zend.common.types import ZendResponse
from zend.common.url import path_segment
from zend.common.validation import resolve_optional_options
from zend.resources.templates.types import (
    ListTemplatesKwargs,
    ListTemplatesParams,
    Template,
    TemplateList,
)


class Templates:
    _client: HttpClient

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @overload
    def list(self, params: ListTemplatesParams) -> ZendResponse[TemplateList]: ...

    @overload
    def list(self, **kwargs: Unpack[ListTemplatesKwargs]) -> ZendResponse[TemplateList]: ...

    def list(
        self, params: ListTemplatesParams | None = None, **kwargs: Any
    ) -> ZendResponse[TemplateList]:
        query = resolve_optional_options(ListTemplatesParams, params, kwargs)
        return self._client.request(
            "GET",
            "/templates",
            query=query.to_query() if query else None,
            cast_to=TemplateList,
        )

    def get(self, id: str) -> ZendResponse[Template]:
        return self._client.request("GET", f"/templates/{path_segment(id)}", cast_to=Template)


class AsyncTemplates:
    _client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    @overload
    async def list(self, params: ListTemplatesParams) -> ZendResponse[TemplateList]: ...

    @overload
    async def list(self, **kwargs: Unpack[ListTemplatesKwargs]) -> ZendResponse[TemplateList]: ...

    async def list(
        self, params: ListTemplatesParams | None = None, **kwargs: Any
    ) -> ZendResponse[TemplateList]:
        query = resolve_optional_options(ListTemplatesParams, params, kwargs)
        return await self._client.request(
            "GET",
            "/templates",
            query=query.to_query() if query else None,
            cast_to=TemplateList,
        )

    async def get(self, id: str) -> ZendResponse[Template]:
        return await self._client.request("GET", f"/templates/{path_segment(id)}", cast_to=Template)
