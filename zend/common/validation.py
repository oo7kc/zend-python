from __future__ import annotations

from collections.abc import Mapping
from typing import TypeVar

from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def resolve_options(
    model_type: type[ModelT],
    options: ModelT | None,
    kwargs: Mapping[str, object],
) -> ModelT:
    """Validate either an options model or keyword arguments, never both."""
    if options is not None:
        if kwargs:
            raise TypeError(f"Pass either {model_type.__name__} or keyword arguments, not both")
        return model_type.model_validate(options)
    return model_type.model_validate(dict(kwargs))


def resolve_optional_options(
    model_type: type[ModelT],
    options: ModelT | None,
    kwargs: Mapping[str, object],
) -> ModelT | None:
    """Resolve optional list parameters while rejecting mixed calling styles."""
    if options is None and not kwargs:
        return None
    return resolve_options(model_type, options, kwargs)
