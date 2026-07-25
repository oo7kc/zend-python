"""normalize_response tests."""

from __future__ import annotations

from zend.common.normalize import normalize_response


class TestNormalizeResponse:
    def test_maps_id_and_drops_v(self) -> None:
        assert normalize_response({"_id": "abc", "__v": 0, "name": "x"}) == {
            "id": "abc",
            "name": "x",
        }

    def test_recurses_into_arrays_and_nested_documents(self) -> None:
        assert normalize_response(
            {"items": [{"_id": "a", "__v": 1}], "sub": {"_id": "b", "title": "t"}}
        ) == {"items": [{"id": "a"}], "sub": {"id": "b", "title": "t"}}

    def test_collapses_duplicate_id_when_clean_id_present(self) -> None:
        assert normalize_response({"id": "e1", "_id": "e1", "__v": 0, "name": "x"}) == {
            "id": "e1",
            "name": "x",
        }

    def test_leaves_already_clean_objects_unchanged(self) -> None:
        assert normalize_response({"id": "e1", "status": "sent"}) == {
            "id": "e1",
            "status": "sent",
        }

    def test_passes_primitives_through(self) -> None:
        assert normalize_response(None) is None
        assert normalize_response("x") == "x"
        assert normalize_response(7) == 7
