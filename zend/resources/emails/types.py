from __future__ import annotations

from pydantic import AliasChoices, Field
from typing_extensions import NotRequired, Required, TypedDict

from zend.common.types import ZendRequestModel, ZendResponseModel


class EmailAttachmentInput(TypedDict):
    filename: Required[str]
    content: Required[bytes | str]
    content_type: NotRequired[str | None]


class SendEmailKwargs(TypedDict):
    from_: Required[str]
    to: Required[str]
    subject: Required[str]
    html: Required[str]
    text: NotRequired[str | None]
    attachments: NotRequired[list[EmailAttachment | EmailAttachmentInput] | None]


class EmailAttachment(ZendRequestModel):
    """File attachment. ``content`` is raw bytes or a base64-encoded string."""

    filename: str
    content: bytes | str
    content_type: str | None = Field(
        default=None,
        validation_alias=AliasChoices("content_type", "contentType"),
    )


class SendEmailOptions(ZendRequestModel):
    from_: str = Field(
        validation_alias=AliasChoices("from", "from_"),
        serialization_alias="from",
    )
    to: str
    subject: str
    html: str
    text: str | None = None
    attachments: list[EmailAttachment] | None = None


class Email(ZendResponseModel):
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
