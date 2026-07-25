"""Case helpers — mirrors zend-node/test/common/case.test.ts."""

from __future__ import annotations

from datetime import datetime, timezone

from zend._case import to_snake_case


class TestToSnakeCase:
    def test_converts_nested_keys_and_arrays(self) -> None:
        assert to_snake_case(
            {
                "preferredChannels": ["sms"],
                "fallbackEnabled": True,
                "nested": {"senderId": "X"},
            }
        ) == {
            "preferred_channels": ["sms"],
            "fallback_enabled": True,
            "nested": {"sender_id": "X"},
        }

    def test_leaves_pass_through_map_values_verbatim_at_any_depth(self) -> None:
        assert to_snake_case(
            {
                "templateId": "t1",
                "templateParams": {"firstName": "John"},
                "messages": [{"templateParams": {"lastName": "Doe"}}],
            },
            ["templateParams"],
        ) == {
            "template_id": "t1",
            "template_params": {"firstName": "John"},
            "messages": [{"template_params": {"lastName": "Doe"}}],
        }

    def test_passes_primitives_through(self) -> None:
        assert to_snake_case("hello") == "hello"
        assert to_snake_case(42) == 42
        assert to_snake_case(None) is None

    def test_passes_non_plain_objects_through_verbatim(self) -> None:
        d = datetime(2024, 1, 1, tzinfo=timezone.utc)
        out = to_snake_case({"scheduledFor": d})
        assert out["scheduled_for"] is d
