"""Shared types and response envelopes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, NoReturn, TypeAlias, TypeGuard, TypeVar

from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired, TypedDict

from zend.client.error import ZendError

T = TypeVar("T")


class ZendRequestModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )


class ZendResponseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class ZendBaseModel(ZendResponseModel):
    """Backward-compatible base for tolerant response models."""


class ListParams(ZendRequestModel):
    limit: int | None = None
    offset: int | None = None

    def to_query(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


class ListParamsKwargs(TypedDict):
    limit: NotRequired[int | None]
    offset: NotRequired[int | None]


@dataclass(frozen=True, slots=True)
class ZendSuccess(Generic[T]):
    """A successful Zend response."""

    data: T
    error: None = None

    def __post_init__(self) -> None:
        if self.error is not None:
            raise ValueError("ZendSuccess.error must be None")

    def unwrap(self) -> T:
        return self.data


@dataclass(frozen=True, slots=True)
class ZendFailure:
    """A failed Zend response."""

    error: ZendError
    data: None = None

    def __post_init__(self) -> None:
        if not isinstance(self.error, ZendError):
            raise TypeError("ZendFailure.error must be a ZendError")
        if self.data is not None:
            raise ValueError("ZendFailure.data must be None")

    def unwrap(self) -> NoReturn:
        raise self.error


ZendResponse: TypeAlias = ZendSuccess[T] | ZendFailure


def is_success(response: ZendResponse[T]) -> TypeGuard[ZendSuccess[T]]:
    """Narrow a response to :class:`ZendSuccess` for static type checkers."""
    return response.error is None
