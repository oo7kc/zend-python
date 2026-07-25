from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from zend._errors import ZendError

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ZendResponse(Generic[T]):
    """Result envelope mirroring the Node SDK ``{ data, error }`` contract.

    Exactly one of ``data`` / ``error`` is set on a successful parse of a
    transport outcome (API and network failures populate ``error``).
    """

    data: T | None
    error: ZendError | None
