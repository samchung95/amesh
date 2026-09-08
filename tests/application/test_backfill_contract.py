from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from amesh.domain import (
    BackfillReplaySource,
    BackfillResourcePin,
    BackfillSelection,
    BackfillSelectionKind,
    BackfillSpec,
    TimeRangeSelection,
    frozen_input_digest,
)


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


def test_replay_requires_frozen_inputs_and_exact_resource_pins() -> None:
    source = uuid4()
    pins = (BackfillResourcePin(key="flow", revision=3, digest="a" * 64),)
    attestation = BackfillReplaySource(
        sourceExecutionId=source,
        frozenInputDigest=frozen_input_digest({"value": 1}),
        resourcePins=pins,
    )
    spec = BackfillSpec(
        namespace="tests.replay",
        flowId="flow",
        flowRevision=3,
        selection=BackfillSelection(sourceExecutionIds=(source,)),
        replaySources=(attestation,),
        idempotencyKey="replay-contract-1",
    )
    assert spec.replay_sources == (attestation,)

    with pytest.raises(ValidationError, match="attestations"):
        BackfillSpec(
            namespace="tests.replay",
            flowId="flow",
            flowRevision=3,
            selection=BackfillSelection(sourceExecutionIds=(source,)),
            idempotencyKey="replay-contract-2",
        )
    with pytest.raises(ValidationError, match="overrides"):
        BackfillSpec(
            namespace="tests.replay",
            flowId="flow",
            flowRevision=3,
            selection=BackfillSelection(sourceExecutionIds=(source,)),
            replaySources=(attestation,),
            idempotencyKey="replay-contract-3",
            inputs={"value": 2},
        )
    with pytest.raises(ValidationError, match="idempotency"):
        BackfillSpec(
            namespace="tests.replay",
            flowId="flow",
            flowRevision=3,
            selection=BackfillSelection(sourceExecutionIds=(source,)),
            replaySources=(attestation,),
        )
