from __future__ import annotations

from datetime import UTC, datetime

import pytest

from amesh.domain import KeyValueType, KeyValueWrite, normalize_resource_path


@pytest.mark.parametrize(
    ("value_type", "value", "expected"),
    [
        (KeyValueType.STRING, "stable", "stable"),
        (KeyValueType.NUMBER, 42.5, 42.5),
        (KeyValueType.BOOLEAN, True, True),
        (KeyValueType.DATETIME, "2026-08-22T10:30:00+08:00", "2026-08-22T02:30:00Z"),
        (KeyValueType.DATE, "2026-08-22", "2026-08-22"),
        (KeyValueType.DURATION, "PT15M", "PT15M"),
        (KeyValueType.JSON, {"enabled": True}, {"enabled": True}),
    ],
)
def test_key_values_preserve_declared_types(
    value_type: KeyValueType,
    value: object,
    expected: object,
) -> None:
    write = KeyValueWrite(
        type=value_type,
        value=value,
        expiresAt=datetime(2026, 8, 23, tzinfo=UTC),
    )

    assert write.value == expected


@pytest.mark.parametrize("path", ("", "../secret", "config//value", "/./value"))
def test_namespace_file_paths_reject_ambiguous_segments(path: str) -> None:
    with pytest.raises(ValueError, match="normalized relative path"):
        normalize_resource_path(path)
