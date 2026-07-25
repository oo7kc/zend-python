from __future__ import annotations

import re
from typing import Any

_CAMEL = re.compile(r"[A-Z]")


def to_snake_key(key: str) -> str:
    return _CAMEL.sub(lambda m: f"_{m.group(0).lower()}", key)


def to_snake_case(value: Any, pass_through: list[str] | None = None) -> Any:
    """Recursively convert dict keys to snake_case.

    Keys listed in ``pass_through`` (snake_case names) leave their *values*
    untouched so nested maps like ``template_params`` keep caller-provided
    key casing (mirrors Node ``passThrough``).
    """
    skip = set(pass_through or [])
    if isinstance(value, list):
        return [to_snake_case(v, pass_through) for v in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            snake = to_snake_key(k) if any(c.isupper() for c in k) else k
            if snake in skip or k in skip:
                out[snake] = v
            else:
                out[snake] = to_snake_case(v, pass_through)
        return out
    return value
