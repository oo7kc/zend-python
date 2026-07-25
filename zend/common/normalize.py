from __future__ import annotations

from typing import Any


def _is_plain_dict(value: Any) -> bool:
    return isinstance(value, dict)


def normalize_response(value: Any) -> Any:
    """Map MongoDB ``_id`` → ``id`` and drop ``__v``, recursively."""
    if isinstance(value, list):
        return [normalize_response(v) for v in value]
    if _is_plain_dict(value):
        out: dict[str, Any] = {}
        for key, v in value.items():
            if key == "__v":
                continue
            if key == "_id":
                # Prefer an existing clean ``id`` if already present.
                if "id" not in value:
                    out["id"] = normalize_response(v)
                continue
            out[key] = normalize_response(v)
        return out
    return value
