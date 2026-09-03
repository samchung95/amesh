from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from amesh.domain.agent_session_reducer import (
    InvalidAgentSessionTransition,
    reduce_agent_session,
)
from amesh.domain.agent_sessions import (
    AgentSessionEvent,
    AgentSessionEventType,
    AgentSessionPhase,
    AgentSessionRecord,
    AgentSessionStart,
    AgentSessionState,
    AgentSessionTransition,
)

_RUNNING = AgentSessionState.RUNNING
_SUCCEEDED = AgentSessionState.SUCCEEDED
_FAILED = AgentSessionState.FAILED

_LEGAL_TRANSITIONS = frozenset(
    {
        (
            AgentSessionPhase.READY,
            AgentSessionEventType.SESSION_STARTED,
            _RUNNING,
            AgentSessionPhase.READY,
        ),
        (
            AgentSessionPhase.READY,
            AgentSessionEventType.CONTEXT_PROJECTED,
            _RUNNING,
            AgentSessionPhase.MODEL,
        ),
        (
            AgentSessionPhase.READY,
            AgentSessionEventType.CONTEXT_COMPACTED,
            _RUNNING,
            AgentSessionPhase.MODEL,
        ),
        (
            AgentSessionPhase.MODEL,
            AgentSessionEventType.CONTEXT_PROJECTED,
            _RUNNING,
            AgentSessionPhase.MODEL,
        ),
        (
            AgentSessionPhase.MODEL,
            AgentSessionEventType.CONTEXT_COMPACTED,
            _RUNNING,
            AgentSessionPhase.MODEL,
        ),
        (
            AgentSessionPhase.MODEL,
            AgentSessionEventType.MODEL_RESPONSE,
            _RUNNING,
            AgentSessionPhase.POLICY,
        ),
        (
            AgentSessionPhase.POLICY,
            AgentSessionEventType.POLICY_AUTHORIZED,
            _RUNNING,
            AgentSessionPhase.TOOL,
        ),
        (
            AgentSessionPhase.POLICY,
            AgentSessionEventType.POLICY_AUTHORIZED,
            _RUNNING,
            AgentSessionPhase.APPROVAL,
        ),
        (
            AgentSessionPhase.TOOL,
            AgentSessionEventType.TOOL_RESULT,
            _RUNNING,
            AgentSessionPhase.READY,
        ),
        (
            AgentSessionPhase.APPROVAL,
            AgentSessionEventType.TOOL_RESULT,
            _RUNNING,
            AgentSessionPhase.READY,
        ),
        (
            AgentSessionPhase.POLICY,
            AgentSessionEventType.EVALUATION_COMPLETED,
            _RUNNING,
            AgentSessionPhase.VALIDATING,
        ),
        (
            AgentSessionPhase.VALIDATING,
            AgentSessionEventType.EVALUATION_COMPLETED,
            _RUNNING,
            AgentSessionPhase.VALIDATING,
        ),
        (
            AgentSessionPhase.POLICY,
            AgentSessionEventType.RELEASE_APPROVED,
            _RUNNING,
            AgentSessionPhase.APPROVAL,
        ),
        (
            AgentSessionPhase.VALIDATING,
            AgentSessionEventType.RELEASE_APPROVED,
            _RUNNING,
            AgentSessionPhase.APPROVAL,
        ),
        (
            AgentSessionPhase.POLICY,
            AgentSessionEventType.MEMORY_WRITTEN,
            _RUNNING,
            AgentSessionPhase.VALIDATING,
        ),
        (
            AgentSessionPhase.APPROVAL,
            AgentSessionEventType.MEMORY_WRITTEN,
            _RUNNING,
            AgentSessionPhase.VALIDATING,
        ),
        (
            AgentSessionPhase.VALIDATING,
            AgentSessionEventType.MEMORY_WRITTEN,
            _RUNNING,
            AgentSessionPhase.VALIDATING,
        ),
        (
            AgentSessionPhase.POLICY,
            AgentSessionEventType.OUTPUT_ACCEPTED,
            _SUCCEEDED,
            AgentSessionPhase.COMPLETE,
        ),
        (
            AgentSessionPhase.APPROVAL,
            AgentSessionEventType.OUTPUT_ACCEPTED,
            _SUCCEEDED,
            AgentSessionPhase.COMPLETE,
        ),
        (
            AgentSessionPhase.VALIDATING,
            AgentSessionEventType.OUTPUT_ACCEPTED,
            _SUCCEEDED,
            AgentSessionPhase.COMPLETE,
        ),
    }
    | {
        (phase, AgentSessionEventType.OUTPUT_REJECTED, state, target_phase)
        for phase in (
            AgentSessionPhase.READY,
            AgentSessionPhase.POLICY,
            AgentSessionPhase.VALIDATING,
        )
        for state, target_phase in (
            (_RUNNING, AgentSessionPhase.READY),
            (_FAILED, AgentSessionPhase.COMPLETE),
        )
    }
    | {
        (phase, AgentSessionEventType.SESSION_FAILED, _FAILED, AgentSessionPhase.COMPLETE)
        for phase in AgentSessionPhase
        if phase is not AgentSessionPhase.COMPLETE
    }
)


def _record(
    phase: AgentSessionPhase,
    *,
    state: AgentSessionState = AgentSessionState.RUNNING,
) -> AgentSessionRecord:
    return AgentSessionRecord(
        **AgentSessionStart(
            tenantId="default",
            namespace="tests.sessions",
            executionId=uuid4(),
            taskRunId=uuid4(),
            attempt=1,
            capabilityPinId=uuid4(),
            envelopeDigest="sha256:" + "a" * 64,
        ).model_dump(mode="python", by_alias=True),
        state=state,
        phase=phase,
    )


def _transition(
    event_type: AgentSessionEventType | str,
    state: AgentSessionState,
    phase: AgentSessionPhase,
) -> AgentSessionTransition:
    payload: dict[str, object] = {}
    if event_type == AgentSessionEventType.POLICY_AUTHORIZED:
        payload = {"approval": {"required": phase is AgentSessionPhase.APPROVAL}}
    elif event_type == AgentSessionEventType.OUTPUT_REJECTED:
        payload = {"repairScheduled": state is AgentSessionState.RUNNING}
    return AgentSessionTransition(
        eventKey="test:event",
        eventType=event_type,
        payload=payload,
        checkpoint={},
        counters={},
        finalResult=({} if event_type == AgentSessionEventType.OUTPUT_ACCEPTED else None),
    )


def test_agent_session_reducer_accepts_exactly_the_declared_transition_matrix() -> None:
    for source_phase, event_type, target_state, target_phase in _LEGAL_TRANSITIONS:
        record = _record(source_phase)
        reduced = reduce_agent_session(
            record,
            _transition(event_type, target_state, target_phase),
        )
        assert (reduced.state, reduced.phase) == (target_state, target_phase)
        assert reduced.version == record.version + 1
        assert (record.state, record.phase) == (_RUNNING, source_phase)

    legal_sources = {(source, event) for source, event, _, _ in _LEGAL_TRANSITIONS}
    for source_phase in AgentSessionPhase:
        record = _record(source_phase)
        for event_type in AgentSessionEventType:
            if (source_phase, event_type) in legal_sources:
                continue
            with pytest.raises(InvalidAgentSessionTransition):
                reduce_agent_session(
                    record,
                    _transition(event_type, AgentSessionState.FAILED, AgentSessionPhase.COMPLETE),
                )


@pytest.mark.parametrize("state", [AgentSessionState.SUCCEEDED, AgentSessionState.FAILED])
def test_agent_session_reducer_rejects_every_event_after_terminal_state(
    state: AgentSessionState,
) -> None:
    record = _record(AgentSessionPhase.COMPLETE, state=state)
    for event_type in AgentSessionEventType:
        with pytest.raises(InvalidAgentSessionTransition, match=f"already {state.value}"):
            reduce_agent_session(
                record,
                _transition(event_type, AgentSessionState.FAILED, AgentSessionPhase.COMPLETE),
            )


def test_agent_session_transition_rejects_unknown_kinds_and_caller_selected_targets() -> None:
    with pytest.raises(ValidationError, match="eventType"):
        _transition("future.lifecycle.event", _RUNNING, AgentSessionPhase.READY)
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        AgentSessionTransition(
            eventKey="test:event",
            eventType=AgentSessionEventType.SESSION_STARTED,
            state=AgentSessionState.FAILED,
            phase=AgentSessionPhase.COMPLETE,
            checkpoint={},
            counters={},
        )


@pytest.mark.parametrize(
    ("phase", "event_type", "message"),
    [
        (
            AgentSessionPhase.POLICY,
            AgentSessionEventType.POLICY_AUTHORIZED,
            "approval.required",
        ),
        (
            AgentSessionPhase.VALIDATING,
            AgentSessionEventType.OUTPUT_REJECTED,
            "repairScheduled",
        ),
    ],
)
def test_agent_session_reducer_rejects_events_without_typed_transition_facts(
    phase: AgentSessionPhase,
    event_type: AgentSessionEventType,
    message: str,
) -> None:
    transition = AgentSessionTransition(
        eventKey="test:event",
        eventType=event_type,
        payload={},
        checkpoint={},
        counters={},
    )

    with pytest.raises(InvalidAgentSessionTransition, match=message):
        reduce_agent_session(_record(phase), transition)


def test_agent_session_reducer_rejects_a_second_start_with_a_new_event_key() -> None:
    initial = _record(AgentSessionPhase.READY)
    record = initial.model_copy(
        update={
            "version": 1,
            "checkpoint": initial.checkpoint.model_copy(
                update={"messages": ({"role": "system", "content": "started"},)}
            ),
        }
    )

    with pytest.raises(InvalidAgentSessionTransition, match="already started"):
        reduce_agent_session(
            record,
            _transition(
                AgentSessionEventType.SESSION_STARTED,
                AgentSessionState.RUNNING,
                AgentSessionPhase.READY,
            ),
        )


def test_agent_session_reducer_rejects_success_without_a_final_result() -> None:
    record = _record(AgentSessionPhase.POLICY)
    transition = _transition(
        AgentSessionEventType.OUTPUT_ACCEPTED,
        AgentSessionState.SUCCEEDED,
        AgentSessionPhase.COMPLETE,
    ).model_copy(update={"final_result": None})

    with pytest.raises(InvalidAgentSessionTransition, match="requires a final result"):
        reduce_agent_session(record, transition)


def test_agent_session_event_wire_values_and_historical_strings_remain_compatible() -> None:
    assert tuple(item.value for item in AgentSessionEventType) == (
        "session.started",
        "context.projected",
        "context.compacted",
        "model.response",
        "policy.authorized",
        "release.approved",
        "tool.result",
        "evaluation.completed",
        "memory.written",
        "output.rejected",
        "output.accepted",
        "session.failed",
    )
    session_id = uuid4()
    historical = AgentSessionEvent(
        sessionId=session_id,
        eventIndex=1,
        eventKey="future:event",
        eventType="future.event",
    )
    assert historical.model_dump(mode="json", by_alias=True)["eventType"] == "future.event"
    round_trip = AgentSessionEvent.model_validate(historical.model_dump(mode="json", by_alias=True))
    assert round_trip == historical
    transition = _transition(
        AgentSessionEventType.SESSION_STARTED,
        AgentSessionState.RUNNING,
        AgentSessionPhase.READY,
    )
    assert transition.model_dump(mode="json", by_alias=True)["eventType"] == "session.started"


def test_agent_session_models_retain_alias_serialization_compatibility() -> None:
    record = _record(AgentSessionPhase.READY)
    start = AgentSessionStart.model_validate(record.model_dump(mode="json", by_alias=True))
    transition = _transition(
        AgentSessionEventType.SESSION_STARTED,
        AgentSessionState.RUNNING,
        AgentSessionPhase.READY,
    )

    for model in (start, record, transition, record.checkpoint, record.counters):
        payload = model.model_dump(mode="json", by_alias=True)
        assert type(model).model_validate(payload) == model

    payload = record.model_dump(mode="json", by_alias=True)
    assert "sessionId" in payload
    assert "executionId" in payload
    assert "taskRunId" in payload
    assert "createdAt" in payload
