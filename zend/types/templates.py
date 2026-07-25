from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, Field

from zend.types.common import ZendBaseModel


def _alias(*names: str) -> AliasChoices:
    return AliasChoices(*names)


class TemplateVariable(ZendBaseModel):
    name: str
    type: str
    default_value: str | None = Field(
        default=None,
        validation_alias=_alias("default_value", "defaultValue"),
    )
    required: bool | None = None


class TemplateChannelVariant(ZendBaseModel):
    channel: str
    content: str
    media_url: str | None = Field(
        default=None,
        validation_alias=_alias("media_url", "mediaUrl"),
    )
    media_type: str | None = Field(
        default=None,
        validation_alias=_alias("media_type", "mediaType"),
    )
    header: str | None = None
    footer: str | None = None


class Template(ZendBaseModel):
    id: str
    name: str
    description: str | None = None
    category: str
    system_category: str | None = Field(
        default=None,
        validation_alias=_alias("system_category", "systemCategory"),
    )
    status: str
    visibility: str | None = None
    is_whatsapp_approved: bool | None = Field(
        default=None,
        validation_alias=_alias("is_whatsapp_approved", "isWhatsappApproved"),
    )
    variables: list[TemplateVariable] | None = None
    channel_variants: list[TemplateChannelVariant] | None = Field(
        default=None,
        validation_alias=_alias("channel_variants", "channelVariants"),
    )
    usage_count: int | None = Field(
        default=None,
        validation_alias=_alias("usage_count", "usageCount"),
    )
    created_at: str | None = Field(
        default=None,
        validation_alias=_alias("created_at", "createdAt"),
    )
    approved_at: str | None = Field(
        default=None,
        validation_alias=_alias("approved_at", "approvedAt"),
    )


class TemplateList(ZendBaseModel):
    templates: list[Template]
    total: int


class ListTemplatesParams(ZendBaseModel):
    category: str | None = None
    status: str | None = None
    limit: int | None = None
    offset: int | None = None

    def to_query(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)
