from __future__ import annotations

from pydantic import AliasChoices, Field

from zend.common.types import ZendBaseModel


class EmailAttachment(ZendBaseModel):
    """File attachment. ``content`` is raw bytes or a base64-encoded string."""

    filename: str
    content: bytes | str
    content_type: str | None = Field(
        default=None,
        validation_alias=AliasChoices("content_type", "contentType"),
    )


class SendEmailOptions(ZendBaseModel):
    from_: str = Field(
        validation_alias=AliasChoices("from", "from_"),
        serialization_alias="from",
    )
    to: str
    subject: str
    html: str
    text: str | None = None
    attachments: list[EmailAttachment] | None = None


class Email(ZendBaseModel):
    id: str
    status: str | None = None
    from_: str | None = Field(
        default=None,
        validation_alias=AliasChoices("from", "from_"),
        serialization_alias="from",
    )
    to: str | None = None
    subject: str | None = None
    html: str | None = None
    text: str | None = None
    cost: float | None = None
    user_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("user_id", "userId"),
    )
    external_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("external_id", "externalId"),
    )
    delivered_at: str | None = Field(
        default=None,
        validation_alias=AliasChoices("delivered_at", "deliveredAt"),
    )
    created_at: str | None = Field(
        default=None,
        validation_alias=AliasChoices("created_at", "createdAt"),
    )
    updated_at: str | None = Field(
        default=None,
        validation_alias=AliasChoices("updated_at", "updatedAt"),
    )


EmailList = list[Email]
