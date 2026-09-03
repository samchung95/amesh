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


_TransitionKey = tuple[AgentSessionPhase, AgentSessionEventType]

_RUNNING = AgentSessionState.RUNNING
_COMPLETE = AgentSessionPhase.COMPLETE

_FIXED_TARGETS: dict[_TransitionKey, AgentSessionPhase] = {
    (AgentSessionPhase.READY, AgentSessionEventType.SESSION_STARTED): AgentSessionPhase.READY,
    (AgentSessionPhase.READY, AgentSessionEventType.CONTEXT_PROJECTED): AgentSessionPhase.MODEL,
    (AgentSessionPhase.READY, AgentSessionEventType.CONTEXT_COMPACTED): AgentSessionPhase.MODEL,
    (AgentSessionPhase.MODEL, AgentSessionEventType.CONTEXT_PROJECTED): AgentSessionPhase.MODEL,
    (AgentSessionPhase.MODEL, AgentSessionEventType.CONTEXT_COMPACTED): AgentSessionPhase.MODEL,
    (AgentSessionPhase.MODEL, AgentSessionEventType.MODEL_RESPONSE): AgentSessionPhase.POLICY,
    (AgentSessionPhase.TOOL, AgentSessionEventType.TOOL_RESULT): AgentSessionPhase.READY,
    (AgentSessionPhase.APPROVAL, AgentSessionEventType.TOOL_RESULT): AgentSessionPhase.READY,
    (AgentSessionPhase.POLICY, AgentSessionEventType.EVALUATION_COMPLETED): (
        AgentSessionPhase.VALIDATING
    ),
    (AgentSessionPhase.VALIDATING, AgentSessionEventType.EVALUATION_COMPLETED): (
        AgentSessionPhase.VALIDATING
    ),
    (AgentSessionPhase.POLICY, AgentSessionEventType.RELEASE_APPROVED): AgentSessionPhase.APPROVAL,
    (AgentSessionPhase.VALIDATING, AgentSessionEventType.RELEASE_APPROVED): (
        AgentSessionPhase.APPROVAL
    ),
    (AgentSessionPhase.POLICY, AgentSessionEventType.MEMORY_WRITTEN): (
        AgentSessionPhase.VALIDATING
    ),
    (AgentSessionPhase.APPROVAL, AgentSessionEventType.MEMORY_WRITTEN): (
        AgentSessionPhase.VALIDATING
    ),
    (AgentSessionPhase.VALIDATING, AgentSessionEventType.MEMORY_WRITTEN): (
        AgentSessionPhase.VALIDATING
    ),
}


def _required_bool(transition: AgentSessionTransition, key: str) -> bool:
    value = transition.payload.get(key)
    if not isinstance(value, bool):
        raise InvalidAgentSessionTransition(
            f"{transition.event_type.value} requires boolean payload field {key!r}"
        )
    return value


def _target_for(
    record: AgentSessionRecord,
    transition: AgentSessionTransition,
) -> tuple[AgentSessionState, AgentSessionPhase]:
    event_type = transition.event_type
    if event_type is AgentSessionEventType.SESSION_FAILED:
        if record.phase is AgentSessionPhase.COMPLETE:
            raise InvalidAgentSessionTransition("session.failed is not legal from RUNNING/COMPLETE")
        return AgentSessionState.FAILED, _COMPLETE
    if event_type is AgentSessionEventType.OUTPUT_ACCEPTED:
        if record.phase not in {
            AgentSessionPhase.POLICY,
            AgentSessionPhase.APPROVAL,
            AgentSessionPhase.VALIDATING,
        }:
            raise InvalidAgentSessionTransition(
                f"output.accepted is not legal from RUNNING/{record.phase.value}"
            )
        return AgentSessionState.SUCCEEDED, _COMPLETE
    if event_type is AgentSessionEventType.OUTPUT_REJECTED:
        if record.phase not in {
            AgentSessionPhase.READY,
            AgentSessionPhase.POLICY,
            AgentSessionPhase.VALIDATING,
        }:
            raise InvalidAgentSessionTransition(
                f"output.rejected is not legal from RUNNING/{record.phase.value}"
            )
        if _required_bool(transition, "repairScheduled"):
            return _RUNNING, AgentSessionPhase.READY
        return AgentSessionState.FAILED, _COMPLETE
    if event_type is AgentSessionEventType.POLICY_AUTHORIZED:
        if record.phase is not AgentSessionPhase.POLICY:
            raise InvalidAgentSessionTransition(
                f"policy.authorized is not legal from RUNNING/{record.phase.value}"
            )
        approval = transition.payload.get("approval")
        if not isinstance(approval, dict) or not isinstance(approval.get("required"), bool):
            raise InvalidAgentSessionTransition(
                "policy.authorized requires boolean payload field 'approval.required'"
            )
        phase = AgentSessionPhase.APPROVAL if approval["required"] else AgentSessionPhase.TOOL
        return _RUNNING, phase
    fixed_phase = _FIXED_TARGETS.get((record.phase, event_type))
    if fixed_phase is None:
        raise InvalidAgentSessionTransition(
            f"{event_type.value} is not legal from RUNNING/{record.phase.value}"
        )
    return _RUNNING, fixed_phase


def reduce_agent_session(
    record: AgentSessionRecord,
    transition: AgentSessionTransition,
) -> AgentSessionRecord:
    """Reduce one session lifecycle transition without I/O or ambient state."""

    if record.state is not AgentSessionState.RUNNING:
        raise InvalidAgentSessionTransition(
            f"agent session {record.session_id} is already {record.state.value}"
        )
    if transition.event_type is AgentSessionEventType.SESSION_STARTED and record.version != 0:
        raise InvalidAgentSessionTransition("agent session has already started")
    if (
        transition.event_type is AgentSessionEventType.OUTPUT_ACCEPTED
        and transition.final_result is None
    ):
        raise InvalidAgentSessionTransition("a successful agent session requires a final result")
    state, phase = _target_for(record, transition)
    return record.model_copy(
        update={
            "state": state,
            "phase": phase,
            "version": record.version + 1,
            "checkpoint": transition.checkpoint,
            "counters": transition.counters,
            "final_result": transition.final_result,
            "error": transition.error,
            "harness": transition.harness or record.harness,
        }
    )
