from __future__ import annotations

from typing import Any

from zend._client import AsyncHttpClient, HttpClient
from zend._response import ZendResponse
from zend.types.templates import ListTemplatesParams, Template, TemplateList


class Templates:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def list(
        self, params: ListTemplatesParams | None = None, **kwargs: Any
    ) -> ZendResponse[TemplateList]:
        query = (
            ListTemplatesParams.model_validate(params or kwargs) if (params or kwargs) else None
        )
        return self._client.request(
            "GET",
            "/templates",
            query=query.to_query() if query else None,
            cast_to=TemplateList,
        )

    def get(self, id: str) -> ZendResponse[Template]:
        return self._client.request("GET", f"/templates/{id}", cast_to=Template)


class AsyncTemplates:
    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client

    async def list(
        self, params: ListTemplatesParams | None = None, **kwargs: Any
    ) -> ZendResponse[TemplateList]:
        query = (
            ListTemplatesParams.model_validate(params or kwargs) if (params or kwargs) else None
        )
        return await self._client.request(
            "GET",
            "/templates",
            query=query.to_query() if query else None,
            cast_to=TemplateList,
        )

    async def get(self, id: str) -> ZendResponse[Template]:
        return await self._client.request("GET", f"/templates/{id}", cast_to=Template)
