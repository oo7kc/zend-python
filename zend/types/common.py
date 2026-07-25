from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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
