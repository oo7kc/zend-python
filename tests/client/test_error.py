"""ZendError tests."""

from __future__ import annotations

from zend import ZendError


class TestZendError:
    def test_is_an_exception_with_the_given_fields(self) -> None:
        e = ZendError("nope", name="validation_error", status_code=422, code="bad")
        assert isinstance(e, Exception)
        assert isinstance(e, ZendError)
        assert str(e) == "nope"
        assert e.name == "validation_error"
        assert e.status_code == 422
        assert e.code == "bad"

    def test_defaults_name_to_zend_error(self) -> None:
        assert ZendError("x").name == "ZendError"
