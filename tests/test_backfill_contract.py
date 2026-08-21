from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from amesh.domain import BackfillSelection, BackfillSelectionKind, TimeRangeSelection


def test_backfill_selectors_are_deterministic_and_bounded() -> None:
    ranged = BackfillSelection(
        timeRange=TimeRangeSelection(
            start=datetime(2026, 8, 22, 0, 0, tzinfo=UTC),
            end=datetime(2026, 8, 22, 0, 3, tzinfo=UTC),
            intervalSeconds=60,
        )
    )
    assert ranged.kind is BackfillSelectionKind.TIME_RANGE
    assert ranged.item_keys() == (
        "time:2026-08-22T00:00:00+00:00",
        "time:2026-08-22T00:01:00+00:00",
        "time:2026-08-22T00:02:00+00:00",
    )

    assert BackfillSelection(partitions=("b", "a", "b")).item_keys() == (
        "partition:b",
        "partition:a",
    )
    source = uuid4()
    assert BackfillSelection(sourceExecutionIds=(source, source)).item_keys() == (
        f"replay:{source}",
    )

    with pytest.raises(ValueError, match="safety limit"):
        ranged.item_keys(maximum=2)


def test_backfill_selection_rejects_ambiguous_or_naive_inputs() -> None:
    with pytest.raises(ValidationError, match="exactly one"):
        BackfillSelection(partitions=("one",), sourceExecutionIds=(uuid4(),))
    with pytest.raises(ValidationError, match="time zones"):
        BackfillSelection(occurrences=(datetime(2026, 8, 22),))
    with pytest.raises(ValidationError, match="must not be empty"):
        BackfillSelection(partitions=(" ",))
