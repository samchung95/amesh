from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from amesh.domain.agent_progress import (
    AgentProgressActivity,
    AgentProgressFrame,
    AgentProgressLimitExceeded,
    AgentProgressLimits,
    AgentProgressSequenceState,
    AgentProgressStatus,
    AgentPublicSummaryDetail,
    AgentSessionEventCursor,
    AgentStatusDetail,
    accept_progress_frame,
    close_progress_segment,
    make_truncated_progress_frame,
    project_agent_session_lifecycle_frame,
)


def _frame(
    sequence: int,
    *,
    activity: AgentProgressActivity = AgentProgressActivity.THINKING,
    status: AgentProgressStatus = AgentProgressStatus.DELTA,
    segment_id: UUID | None,
    summary: str | None = "Working through the requested step.",
) -> AgentProgressFrame:
    detail = (
        AgentPublicSummaryDetail(text=summary)
        if summary is not None
        else AgentStatusDetail(code="tool.running", label="Tool is running")
    )
    return AgentProgressFrame(
        attemptSessionId=UUID("11111111-1111-4111-8111-111111111111"),
        attempt=1,
        turn=1,
        activity=activity,
        status=status,
        activityId="turn-1",
        segmentId=segment_id,
        sourceId="provider:fixture",
        sourceSequence=sequence,
        occurredAt=datetime(2026, 8, 31, 12, 0, sequence, tzinfo=UTC),
        detail=detail,
    )


def test_progress_contract_is_allowlisted_and_rejects_private_reasoning_fields() -> None:
    segment_id = uuid4()
    frame = _frame(1, status=AgentProgressStatus.STARTED, segment_id=segment_id)

    assert frame.schema_version == "amesh.agent-progress/v1"
    assert frame.event_key.startswith("progress:1:")
    assert "reasoning" not in frame.model_dump_json()

    payload = frame.model_dump(mode="json", by_alias=True)
    payload["reasoning"] = "private chain of thought"
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        AgentProgressFrame.model_validate(payload)

    detail = payload["detail"]
    assert isinstance(detail, dict)
    detail["scratchpad"] = "private"
    payload.pop("reasoning")
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        AgentProgressFrame.model_validate(payload)


def test_progress_frame_requires_timezone_and_segment_for_thinking() -> None:
    with pytest.raises(ValidationError, match="time-zone"):
        _frame(1, segment_id=uuid4()).model_copy(
            update={"occurred_at": datetime(2026, 8, 31, 12, 0)}
        ).model_validate(
            {
                **_frame(1, segment_id=uuid4()).model_dump(by_alias=True),
                "occurredAt": datetime(2026, 8, 31, 12, 0),
            }
        )

    with pytest.raises(ValidationError, match="thinking progress requires segmentId"):
        _frame(1, segment_id=None)


def test_progress_sequence_preserves_thinking_work_thinking_boundaries() -> None:
    first_segment = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    second_segment = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
    state = AgentProgressSequenceState()

    started = accept_progress_frame(
        state,
        _frame(1, status=AgentProgressStatus.STARTED, segment_id=first_segment),
    )
    state = started.state
    state = accept_progress_frame(state, _frame(2, segment_id=first_segment)).state
    state = accept_progress_frame(
        state,
        _frame(
            3,
            activity=AgentProgressActivity.TOOL,
            status=AgentProgressStatus.STARTED,
            segment_id=None,
            summary=None,
        ),
    ).state
    state = accept_progress_frame(
        state,
        _frame(4, status=AgentProgressStatus.STARTED, segment_id=second_segment),
    ).state

    assert first_segment in state.closed_segment_ids
    assert state.active_segment_id == second_segment
    assert state.segment_count == 2
    assert state.accepted_frame_count == 4

    with pytest.raises(ValueError, match="closed progress segment"):
        accept_progress_frame(state, _frame(5, segment_id=first_segment))


def test_progress_sequence_ignores_timestamp_for_idempotency_and_rejects_semantic_reuse() -> None:
    segment_id = uuid4()
    frame = _frame(1, status=AgentProgressStatus.STARTED, segment_id=segment_id)
    accepted = accept_progress_frame(AgentProgressSequenceState(), frame)
    duplicate = accept_progress_frame(accepted.state, frame)
    timestamp_only_duplicate = accept_progress_frame(
        accepted.state,
        frame.model_copy(
            update={"occurred_at": datetime(2027, 1, 1, tzinfo=UTC)},
        ),
    )

    assert duplicate.duplicate
    assert duplicate.state == accepted.state
    assert timestamp_only_duplicate.duplicate
    assert timestamp_only_duplicate.state == accepted.state
    assert (
        frame.fingerprint
        == frame.model_copy(update={"occurred_at": datetime(2027, 1, 1, tzinfo=UTC)}).fingerprint
    )

    conflicting = frame.model_copy(
        update={"detail": AgentPublicSummaryDetail(text="Different public summary")}
    )
    with pytest.raises(ValueError, match="source sequence was reused"):
        accept_progress_frame(accepted.state, conflicting)

    with pytest.raises(ValueError, match="sourceSequence must be contiguous"):
        accept_progress_frame(accepted.state, _frame(3, segment_id=segment_id))


def test_canonical_non_progress_event_permanently_closes_active_segment() -> None:
    segment_id = uuid4()
    state = accept_progress_frame(
        AgentProgressSequenceState(),
        _frame(1, status=AgentProgressStatus.STARTED, segment_id=segment_id),
    ).state

    state = close_progress_segment(state)

    assert state.active_segment_id is None
    assert segment_id in state.closed_segment_ids
    with pytest.raises(ValueError, match="closed progress segment"):
        accept_progress_frame(state, _frame(2, segment_id=segment_id))


def test_terminal_progress_closes_partial_segment_and_enforces_limits() -> None:
    segment_id = uuid4()
    limits = AgentProgressLimits(maxFramesPerSegment=2, maxFramesPerSession=4)
    state = accept_progress_frame(
        AgentProgressSequenceState(),
        _frame(1, status=AgentProgressStatus.STARTED, segment_id=segment_id),
        limits=limits,
    ).state
    state = accept_progress_frame(
        state,
        _frame(2, status=AgentProgressStatus.TRUNCATED, segment_id=segment_id),
        limits=limits,
    ).state

    assert state.active_segment_id is None
    assert segment_id in state.closed_segment_ids

    with pytest.raises(ValueError, match="progress stream was truncated"):
        accept_progress_frame(state, _frame(3, segment_id=segment_id), limits=limits)


def test_progress_limit_overflow_is_typed_for_sink_truncation() -> None:
    segment_id = uuid4()
    limits = AgentProgressLimits(maxFramesPerSegment=1)
    state = accept_progress_frame(
        AgentProgressSequenceState(),
        _frame(1, status=AgentProgressStatus.STARTED, segment_id=segment_id),
        limits=limits,
    ).state

    with pytest.raises(AgentProgressLimitExceeded, match="maxFramesPerSegment"):
        accept_progress_frame(state, _frame(2, segment_id=segment_id), limits=limits)

    truncated = make_truncated_progress_frame(_frame(2, segment_id=segment_id), state)
    assert truncated.activity is AgentProgressActivity.TERMINAL
    assert truncated.status is AgentProgressStatus.TRUNCATED
    assert len(truncated.model_dump_json(by_alias=True).encode()) <= AgentProgressLimits().max_frame_bytes
    assert "private" not in truncated.model_dump_json()
    after_truncation = accept_progress_frame(state, truncated, limits=limits).state
    with pytest.raises(ValueError, match="progress stream was truncated"):
        accept_progress_frame(after_truncation, _frame(3, segment_id=segment_id), limits=limits)


def test_progress_rate_frame_and_session_limits_are_bounded() -> None:
    segment_id = uuid4()
    limits = AgentProgressLimits(maxFramesPerSecond=1, maxFramesPerSession=2)
    state = accept_progress_frame(
        AgentProgressSequenceState(),
        _frame(1, status=AgentProgressStatus.STARTED, segment_id=segment_id),
        limits=limits,
    ).state
    with pytest.raises(AgentProgressLimitExceeded, match="maxFramesPerSecond"):
        accept_progress_frame(state, _frame(2, segment_id=segment_id), limits=limits)

    later = _frame(2, segment_id=segment_id).model_copy(
        update={"occurred_at": datetime(2026, 8, 31, 12, 0, 3, tzinfo=UTC)}
    )
    state = accept_progress_frame(state, later, limits=limits).state
    with pytest.raises(AgentProgressLimitExceeded, match="maxFramesPerSession"):
        accept_progress_frame(
            state,
            _frame(3, segment_id=segment_id).model_copy(
                update={"occurred_at": datetime(2026, 8, 31, 12, 0, 3, tzinfo=UTC)}
            ),
            limits=limits,
        )


def test_default_progress_limits_preserve_a_high_rate_activity_stream() -> None:
    segment_id = uuid4()
    occurred_at = datetime(2026, 8, 31, 12, 0, tzinfo=UTC)
    state = AgentProgressSequenceState()
    first = _frame(
        1,
        status=AgentProgressStatus.STARTED,
        segment_id=segment_id,
    ).model_copy(update={"occurred_at": occurred_at})

    for sequence in range(1, 65):
        frame = first.model_copy(
            update={
                "source_sequence": sequence,
                "status": (
                    AgentProgressStatus.STARTED
                    if sequence == 1
                    else AgentProgressStatus.DELTA
                ),
            }
        )
        state = accept_progress_frame(state, frame).state

    assert state.accepted_frame_count == 64
    assert state.truncated is False


def test_frame_size_and_segment_count_limits_are_typed() -> None:
    segment_id = uuid4()
    oversized = _frame(1, status=AgentProgressStatus.STARTED, segment_id=segment_id)
    limits = AgentProgressLimits(maxFrameBytes=512)
    oversized = oversized.model_copy(
        update={"detail": AgentPublicSummaryDetail(text="x" * 4096)}
    )
    with pytest.raises(AgentProgressLimitExceeded, match="maxFrameBytes"):
        accept_progress_frame(AgentProgressSequenceState(), oversized, limits=limits)

    first = accept_progress_frame(
        AgentProgressSequenceState(),
        _frame(1, status=AgentProgressStatus.STARTED, segment_id=segment_id),
        limits=AgentProgressLimits(maxSegmentsPerSession=1),
    ).state
    second = _frame(2, status=AgentProgressStatus.STARTED, segment_id=uuid4())
    with pytest.raises(AgentProgressLimitExceeded, match="maxSegmentsPerSession"):
        accept_progress_frame(
            first,
            second,
            limits=AgentProgressLimits(maxSegmentsPerSession=1),
        )


def test_attempt_aware_cursor_round_trips_and_is_bound_to_logical_session() -> None:
    service_session_id = uuid4()
    cursor = AgentSessionEventCursor(
        serviceSessionId=service_session_id,
        attemptSessionId=uuid4(),
        attempt=3,
        eventIndex=17,
    )

    token = cursor.encode()
    decoded = AgentSessionEventCursor.decode(token)

    assert decoded == cursor
    assert decoded.position == (3, 17)
    decoded.require_service_session(service_session_id)
    with pytest.raises(ValueError, match="different service session"):
        decoded.require_service_session(uuid4())

    with pytest.raises(ValueError, match="invalid agent-session cursor"):
        AgentSessionEventCursor.decode("not-a-cursor")

    with pytest.raises(ValidationError, match="initial cursor"):
        AgentSessionEventCursor(
            serviceSessionId=service_session_id,
            attemptSessionId=None,
            attempt=0,
            eventIndex=1,
        )


def test_lifecycle_projection_is_typed_stable_and_drops_generic_payload() -> None:
    attempt_session_id = uuid4()
    event_id = uuid4()
    occurred_at = datetime(2026, 8, 31, 13, 0, tzinfo=UTC)

    tool = project_agent_session_lifecycle_frame(
        attempt_session_id=attempt_session_id,
        attempt=2,
        event_id=event_id,
        event_index=7,
        event_type="tool.result",
        payload={
            "turn": 3,
            "reasoning": "must never escape",
            "result": {"secret": "must never escape"},
        },
        occurred_at=occurred_at,
    )

    assert tool.activity is AgentProgressActivity.TOOL
    assert tool.status is AgentProgressStatus.COMPLETED
    assert tool.turn == 3
    assert tool.activity_id == f"journal:{event_id}"
    assert tool.source_id == f"journal:{attempt_session_id}"
    assert tool.source_sequence == 7
    assert "reasoning" not in tool.model_dump_json()
    assert "secret" not in tool.model_dump_json()

    terminal = project_agent_session_lifecycle_frame(
        attempt_session_id=attempt_session_id,
        attempt=2,
        event_id=uuid4(),
        event_index=8,
        event_type="output.accepted",
        payload={"result": {"private": True}},
        occurred_at=occurred_at,
    )
    assert terminal.activity is AgentProgressActivity.TERMINAL
    assert terminal.status is AgentProgressStatus.COMPLETED

    rejected = project_agent_session_lifecycle_frame(
        attempt_session_id=attempt_session_id,
        attempt=2,
        event_id=uuid4(),
        event_index=9,
        event_type="output.rejected",
        payload={"repairScheduled": False, "error": "private validation detail"},
        occurred_at=occurred_at,
    )
    assert rejected.activity is AgentProgressActivity.TERMINAL
    assert rejected.status is AgentProgressStatus.FAILED
    assert "private validation detail" not in rejected.model_dump_json()
