from __future__ import annotations

from .agent_sessions import (
    AgentSessionEventType,
    AgentSessionPhase,
    AgentSessionRecord,
    AgentSessionState,
    AgentSessionTransition,
)


class InvalidAgentSessionTransition(ValueError):
    """Raised when a lifecycle event is not legal for the current session state."""


_Target = tuple[AgentSessionState, AgentSessionPhase]
_TransitionKey = tuple[AgentSessionPhase, AgentSessionEventType]

_RUNNING_READY: _Target = (AgentSessionState.RUNNING, AgentSessionPhase.READY)
_RUNNING_MODEL: _Target = (AgentSessionState.RUNNING, AgentSessionPhase.MODEL)
_RUNNING_POLICY: _Target = (AgentSessionState.RUNNING, AgentSessionPhase.POLICY)
_RUNNING_APPROVAL: _Target = (AgentSessionState.RUNNING, AgentSessionPhase.APPROVAL)
_RUNNING_TOOL: _Target = (AgentSessionState.RUNNING, AgentSessionPhase.TOOL)
_RUNNING_VALIDATING: _Target = (AgentSessionState.RUNNING, AgentSessionPhase.VALIDATING)
_SUCCEEDED: _Target = (AgentSessionState.SUCCEEDED, AgentSessionPhase.COMPLETE)
_FAILED: _Target = (AgentSessionState.FAILED, AgentSessionPhase.COMPLETE)

_ALLOWED_TRANSITIONS: dict[_TransitionKey, frozenset[_Target]] = {
    (AgentSessionPhase.READY, AgentSessionEventType.SESSION_STARTED): frozenset({_RUNNING_READY}),
    (AgentSessionPhase.READY, AgentSessionEventType.CONTEXT_PROJECTED): frozenset({_RUNNING_MODEL}),
    (AgentSessionPhase.READY, AgentSessionEventType.CONTEXT_COMPACTED): frozenset({_RUNNING_MODEL}),
    (AgentSessionPhase.MODEL, AgentSessionEventType.CONTEXT_PROJECTED): frozenset({_RUNNING_MODEL}),
    (AgentSessionPhase.MODEL, AgentSessionEventType.CONTEXT_COMPACTED): frozenset({_RUNNING_MODEL}),
    (AgentSessionPhase.MODEL, AgentSessionEventType.MODEL_RESPONSE): frozenset({_RUNNING_POLICY}),
    (AgentSessionPhase.POLICY, AgentSessionEventType.POLICY_AUTHORIZED): frozenset(
        {_RUNNING_APPROVAL, _RUNNING_TOOL}
    ),
    (AgentSessionPhase.TOOL, AgentSessionEventType.TOOL_RESULT): frozenset({_RUNNING_READY}),
    (AgentSessionPhase.APPROVAL, AgentSessionEventType.TOOL_RESULT): frozenset({_RUNNING_READY}),
    (AgentSessionPhase.POLICY, AgentSessionEventType.EVALUATION_COMPLETED): frozenset(
        {_RUNNING_VALIDATING}
    ),
    (AgentSessionPhase.VALIDATING, AgentSessionEventType.EVALUATION_COMPLETED): frozenset(
        {_RUNNING_VALIDATING}
    ),
    (AgentSessionPhase.POLICY, AgentSessionEventType.RELEASE_APPROVED): frozenset(
        {_RUNNING_APPROVAL}
    ),
    (AgentSessionPhase.VALIDATING, AgentSessionEventType.RELEASE_APPROVED): frozenset(
        {_RUNNING_APPROVAL}
    ),
    (AgentSessionPhase.POLICY, AgentSessionEventType.MEMORY_WRITTEN): frozenset(
        {_RUNNING_VALIDATING}
    ),
    (AgentSessionPhase.APPROVAL, AgentSessionEventType.MEMORY_WRITTEN): frozenset(
        {_RUNNING_VALIDATING}
    ),
    (AgentSessionPhase.VALIDATING, AgentSessionEventType.MEMORY_WRITTEN): frozenset(
        {_RUNNING_VALIDATING}
    ),
    (AgentSessionPhase.POLICY, AgentSessionEventType.OUTPUT_REJECTED): frozenset(
        {_RUNNING_READY, _FAILED}
    ),
    (AgentSessionPhase.READY, AgentSessionEventType.OUTPUT_REJECTED): frozenset(
        {_RUNNING_READY, _FAILED}
    ),
    (AgentSessionPhase.VALIDATING, AgentSessionEventType.OUTPUT_REJECTED): frozenset(
        {_RUNNING_READY, _FAILED}
    ),
    (AgentSessionPhase.POLICY, AgentSessionEventType.OUTPUT_ACCEPTED): frozenset({_SUCCEEDED}),
    (AgentSessionPhase.APPROVAL, AgentSessionEventType.OUTPUT_ACCEPTED): frozenset({_SUCCEEDED}),
    (AgentSessionPhase.VALIDATING, AgentSessionEventType.OUTPUT_ACCEPTED): frozenset({_SUCCEEDED}),
}

for _phase in AgentSessionPhase:
    if _phase is not AgentSessionPhase.COMPLETE:
        _ALLOWED_TRANSITIONS[(_phase, AgentSessionEventType.SESSION_FAILED)] = frozenset({_FAILED})


def reduce_agent_session(
    record: AgentSessionRecord,
    transition: AgentSessionTransition,
) -> AgentSessionRecord:
    """Reduce one session lifecycle transition without I/O or ambient state."""

    try:
        event_type = AgentSessionEventType(transition.event_type)
    except ValueError as exc:
        raise InvalidAgentSessionTransition(
            f"unsupported agent session event {transition.event_type!r}"
        ) from exc
    if record.state is not AgentSessionState.RUNNING:
        raise InvalidAgentSessionTransition(
            f"agent session {record.session_id} is already {record.state.value}"
        )
    if event_type is AgentSessionEventType.SESSION_STARTED and record.version != 0:
        raise InvalidAgentSessionTransition("agent session has already started")
    if event_type is AgentSessionEventType.OUTPUT_ACCEPTED and transition.final_result is None:
        raise InvalidAgentSessionTransition("a successful agent session requires a final result")
    target = (transition.state, transition.phase)
    allowed = _ALLOWED_TRANSITIONS.get((record.phase, event_type), frozenset())
    if target not in allowed:
        raise InvalidAgentSessionTransition(
            f"{event_type.value} to {transition.state.value}/{transition.phase.value} "
            f"is not legal from {record.state.value}/{record.phase.value}"
        )
    return record.model_copy(
        update={
            "state": transition.state,
            "phase": transition.phase,
            "version": record.version + 1,
            "checkpoint": transition.checkpoint,
            "counters": transition.counters,
            "final_result": transition.final_result,
            "error": transition.error,
            "harness": transition.harness or record.harness,
        }
    )
