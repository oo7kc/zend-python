"""Shared types and response envelopes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from zend.client.error import ZendError

T = TypeVar("T")


class ZendBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class ListParams(ZendBaseModel):
    limit: int | None = None
    offset: int | None = None

    def to_query(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


@dataclass(frozen=True, slots=True)
class ZendResponse(Generic[T]):
    """Result envelope mirroring the Node SDK ``{ data, error }`` contract.

    Exactly one of ``data`` / ``error`` is set on a successful parse of a
    transport outcome (API and network failures populate ``error``).
    """

    data: T | None
    error: ZendError | None
