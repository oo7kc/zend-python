from __future__ import annotations

from typing import Any, Literal

from pydantic import AliasChoices, Field

from zend.common.types import ZendBaseModel

Channel = Literal["sms", "whatsapp"]
MessageStatus = Literal[
    "pending",
    "queued",
    "processing",
    "sent",
    "delivered",
    "failed",
    "cancelled",
]
Priority = Literal["low", "normal", "high", "urgent"]
DeliveryPriority = Literal["cost", "speed", "reliability"]


def _alias(*names: str) -> AliasChoices:
    return AliasChoices(*names)


class SendMessageOptions(ZendBaseModel):
    to: str
    body: str | None = None
    preferred_channels: list[Channel] | None = Field(
        default=None,
        validation_alias=_alias("preferred_channels", "preferredChannels"),
    )
    template_id: str | None = Field(
        default=None,
        validation_alias=_alias("template_id", "templateId"),
    )
    template_params: dict[str, Any] | None = Field(
        default=None,
        validation_alias=_alias("template_params", "templateParams"),
    )
    sender_id: str | None = Field(
        default=None,
        validation_alias=_alias("sender_id", "senderId"),
    )
    scheduled_for: str | None = Field(
        default=None,
        validation_alias=_alias("scheduled_for", "scheduledFor"),
    )
    fallback_enabled: bool | None = Field(
        default=None,
        validation_alias=_alias("fallback_enabled", "fallbackEnabled"),
    )
    webhook_url: str | None = Field(
        default=None,
        validation_alias=_alias("webhook_url", "webhookUrl"),
    )
    priority: Priority | None = None
    delivery_priority: DeliveryPriority | None = Field(
        default=None,
        validation_alias=_alias("delivery_priority", "deliveryPriority"),
    )


class BulkMessageItem(ZendBaseModel):
    to: str
    body: str
    template_params: dict[str, Any] | None = Field(
        default=None,
        validation_alias=_alias("template_params", "templateParams"),
    )
    campaign_id: str | None = Field(
        default=None,
        validation_alias=_alias("campaign_id", "campaignId"),
    )


class BulkMessageOptions(ZendBaseModel):
    messages: list[BulkMessageItem]
    preferred_channels: list[Channel] | None = Field(
        default=None,
        validation_alias=_alias("preferred_channels", "preferredChannels"),
    )
    template_id: str | None = Field(
        default=None,
        validation_alias=_alias("template_id", "templateId"),
    )
    fallback_enabled: bool | None = Field(
        default=None,
        validation_alias=_alias("fallback_enabled", "fallbackEnabled"),
    )
    delivery_priority: DeliveryPriority | None = Field(
        default=None,
        validation_alias=_alias("delivery_priority", "deliveryPriority"),
    )
    webhook_url: str | None = Field(
        default=None,
        validation_alias=_alias("webhook_url", "webhookUrl"),
    )
    sender_id: str | None = Field(
        default=None,
        validation_alias=_alias("sender_id", "senderId"),
    )


class SendMessageResult(ZendBaseModel):
    id: str
    status: MessageStatus
    estimated_cost: float | None = Field(
        default=None,
        validation_alias=_alias("estimated_cost", "estimatedCost"),
    )
    message: str | None = None


class DeliveryAttempt(ZendBaseModel):
    channel: Channel
    status: str
    attempted_at: str | None = Field(
        default=None,
        validation_alias=_alias("attempted_at", "attemptedAt"),
    )
    cost: float | None = None
    error_message: str | None = Field(
        default=None,
        validation_alias=_alias("error_message", "errorMessage"),
    )


class Message(ZendBaseModel):
    id: str
    status: MessageStatus
    channel_used: Channel | None = Field(
        default=None,
        validation_alias=_alias("channel_used", "channelUsed"),
    )
    to: str | None = None
    body: str | None = None
    total_cost: float | None = Field(
        default=None,
        validation_alias=_alias("total_cost", "totalCost"),
    )
    delivery_attempts: list[DeliveryAttempt] | None = Field(
        default=None,
        validation_alias=_alias("delivery_attempts", "deliveryAttempts"),
    )
    created_at: str | None = Field(
        default=None,
        validation_alias=_alias("created_at", "createdAt"),
    )
    sent_at: str | None = Field(
        default=None,
        validation_alias=_alias("sent_at", "sentAt"),
    )
    error_message: str | None = Field(
        default=None,
        validation_alias=_alias("error_message", "errorMessage"),
    )


class MessageList(ZendBaseModel):
    messages: list[Message]
    total: int
    page: int | None = None
    pages: int | None = None


class BulkMessageResult(ZendBaseModel):
    total: int | None = None
    queued: int | None = None
    messages: list[SendMessageResult] | None = None
