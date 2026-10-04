from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, Field
from typing_extensions import NotRequired, Required, TypedDict

from zend.common.types import ZendRequestModel, ZendResponseModel

VoiceGender = Literal["female", "male"]


class VoiceFallbackInput(TypedDict):
    sms: Required[bool]
    sms_text: NotRequired[str | None]
    sender_id: NotRequired[str | None]


class SendVoiceKwargs(TypedDict):
    recipients: Required[list[str]]
    text: NotRequired[str | None]
    voice_url: NotRequired[str | None]
    voice: NotRequired[VoiceGender | None]
    retry: NotRequired[bool | None]
    callback_url: NotRequired[str | None]
    fallback: NotRequired[VoiceFallback | VoiceFallbackInput | None]


def _alias(*names: str) -> AliasChoices:
    return AliasChoices(*names)


class VoiceFallback(ZendRequestModel):
    sms: bool
    sms_text: str | None = Field(
        default=None,
        validation_alias=_alias("sms_text", "smsText"),
    )
    sender_id: str | None = Field(
        default=None,
        validation_alias=_alias("sender_id", "senderId"),
    )


class SendVoiceOptions(ZendRequestModel):
    recipients: list[str]
    text: str | None = None
    voice_url: str | None = Field(
        default=None,
        validation_alias=_alias("voice_url", "voiceUrl"),
    )
    voice: VoiceGender | None = None
    retry: bool | None = None
    callback_url: str | None = Field(
        default=None,
        validation_alias=_alias("callback_url", "callbackUrl"),
    )
    fallback: VoiceFallback | None = None


class VoiceSendResult(ZendResponseModel):
    batch_id: str = Field(validation_alias=_alias("batch_id", "batchId"))
    recipients: int
    message_ids: list[str] = Field(validation_alias=_alias("message_ids", "messageIds"))
    status: str
    credits_reserved: float | None = Field(
        default=None,
        validation_alias=_alias("credits_reserved", "creditsReserved"),
    )


class VoiceCounts(ZendResponseModel):
    total: int
    answered: int
    no_answer: int = Field(validation_alias=_alias("no_answer", "noAnswer"))
    busy: int
    failed: int
    fallback_sent: int = Field(validation_alias=_alias("fallback_sent", "fallbackSent"))


class VoiceBatch(ZendResponseModel):
    batch_id: str = Field(validation_alias=_alias("batch_id", "batchId"))
    source: str | None = None
    text: str | None = None
    voice: str | None = None
    audio_url: str | None = Field(
        default=None,
        validation_alias=_alias("audio_url", "audioUrl"),
    )
    status: str
    counts: VoiceCounts | None = None
    unit_cost: float | None = Field(
        default=None,
        validation_alias=_alias("unit_cost", "unitCost"),
    )
    credits_reserved: float | None = Field(
        default=None,
        validation_alias=_alias("credits_reserved", "creditsReserved"),
    )
    error_message: str | None = Field(
        default=None,
        validation_alias=_alias("error_message", "errorMessage"),
    )
    created_at: str | None = Field(
        default=None,
        validation_alias=_alias("created_at", "createdAt"),
    )


class VoiceRecipient(ZendResponseModel):
    id: str
    to: str
    status: str
    error_message: str | None = Field(
        default=None,
        validation_alias=_alias("error_message", "errorMessage"),
    )
    voice_refunded: bool | None = Field(
        default=None,
        validation_alias=_alias("voice_refunded", "voiceRefunded"),
    )
    fallback_sms_sent: bool | None = Field(
        default=None,
        validation_alias=_alias("fallback_sms_sent", "fallbackSmsSent"),
    )


class VoiceBatchDetail(ZendResponseModel):
    batch: VoiceBatch
    recipients: list[VoiceRecipient]


class VoiceBatchList(ZendResponseModel):
    batches: list[VoiceBatch]
    total: int
    page: int | None = None
    limit: int | None = None


class VoiceUpload(ZendResponseModel):
    url: str
