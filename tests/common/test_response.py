"""Typed Zend response envelope tests."""

from __future__ import annotations

import pytest

from zend import ZendError, ZendFailure, ZendSuccess, is_success


def test_success_unwraps_and_narrows() -> None:
    response = ZendSuccess(data={"id": "m1"})

    assert is_success(response)
    assert response.unwrap() == {"id": "m1"}
    assert response.error is None


def test_failure_unwrap_raises_contained_error() -> None:
    error = ZendError("failed")
    response = ZendFailure(error=error)

    assert not is_success(response)
    with pytest.raises(ZendError, match="failed"):
        response.unwrap()


def test_envelope_rejects_invalid_states() -> None:
    with pytest.raises(ValueError, match="error must be None"):
        ZendSuccess(data="bad", error=ZendError("also bad"))  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="data must be None"):
        ZendFailure(error=ZendError("bad"), data="also bad")  # type: ignore[arg-type]
