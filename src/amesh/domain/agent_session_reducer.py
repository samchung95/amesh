from __future__ import annotations

from .agent_sessions import (
    AgentSessionEventType,
    AgentSessionPhase,
    AgentSessionRecord,
    AgentSessionState,
    AgentSessionTransition,
)
from .agent_tool_plan import tool_invocation_key


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
    if event_type is AgentSessionEventType.RESEARCH_COMPLETED:
        if (
            record.phase is not AgentSessionPhase.POLICY
            or record.checkpoint.interaction_protocol == "STRUCTURED_V1"
            or record.checkpoint.interaction_stage != "RESEARCH"
            or transition.checkpoint.interaction_stage != "FINALIZATION"
            or transition.checkpoint.evidence_digest is None
        ):
            raise InvalidAgentSessionTransition("research.completed requires a research checkpoint")
        return _RUNNING, AgentSessionPhase.READY
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
    _validate_tool_plan_transition(record, transition)
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


def _validate_tool_plan_transition(
    record: AgentSessionRecord, transition: AgentSessionTransition
) -> None:
    previous = record.checkpoint.tool_plan
    current = transition.checkpoint.tool_plan
    if previous is not None and previous.mode == "UNORDERED":
        if (
            current is None
            or current.mode != previous.mode
            or current.plan_digest != previous.plan_digest
            or current.expanded_digest != previous.expanded_digest
            or current.occurrences != previous.occurrences
        ):
            raise InvalidAgentSessionTransition("unordered completion requirements cannot change")
        evidence = transition.payload.get("requiredToolPlanOccurrence")
        expected = previous
        if transition.event_type is AgentSessionEventType.TOOL_RESULT and evidence is not None:
            turn = transition.payload.get("turn")
            tool = transition.payload.get("tool")
            result = transition.payload.get("result")
            occurrence = next(
                (
                    item
                    for item in previous.missing_occurrences
                    if isinstance(evidence, dict)
                    and evidence.get("occurrenceId") == item.occurrence_id
                    and evidence.get("callDigest") == item.call_digest
                    and evidence.get("tool") == item.tool_name == tool
                ),
                None,
            )
            if (
                occurrence is None
                or type(turn) is not int
                or turn < 1
                or not isinstance(tool, str)
                or not isinstance(result, dict)
            ):
                raise InvalidAgentSessionTransition(
                    "completion evidence requires this tool's actual result"
                )
            expected = previous.record_result(
                occurrence,
                session_id=record.session_id,
                attempt_key=tool_invocation_key(record.session_id, turn, tool),
                result=result,
            )
        if current != expected:
            raise InvalidAgentSessionTransition(
                "completion evidence must match one actual tool result"
            )
    if current is None or current.mode != "UNORDERED":
        return
    if current.session_id != record.session_id:
        raise InvalidAgentSessionTransition("completion evidence belongs to another session")
    if previous is not None and previous.mode != "UNORDERED":
        raise InvalidAgentSessionTransition("unordered completion requirements cannot change")
    if previous is None and (
        transition.event_type is not AgentSessionEventType.SESSION_STARTED
        or any(entry.state.value != "PENDING" for entry in current.entries)
    ):
        raise InvalidAgentSessionTransition("unordered requirements must start unmet")
    if transition.event_type in {
        AgentSessionEventType.OUTPUT_ACCEPTED,
        AgentSessionEventType.RESEARCH_COMPLETED,
    } and (previous is None or not previous.is_complete):
        raise InvalidAgentSessionTransition("required tool plan is incomplete")
