from __future__ import annotations

import json
from collections.abc import Mapping
from copy import deepcopy
from decimal import Decimal
from typing import Any

from amesh.domain import AgentMeshDefinition, AgentMeshSessionBudget, FailureCategory
from amesh.dsl import FlowDefinition, PlannedTask, visible_output_ids
from amesh.dsl.models import TaskDefinition
from amesh.expressions import ExpressionContext, redact_secret_values
from amesh.ports import PersistedExecution, PersistedTaskRun, TaskRunState

from .loops import LoopIterationContext
from .task_results import _canonical_json_default


def _aggregate_flowable_result(
    node: PlannedTask,
    children: list[PersistedTaskRun],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "mode": node.mode,
        "failurePolicy": node.failure_policy.value,
        "childOrder": [child.task_id for child in children],
        "children": {
            child.task_id: {
                "state": child.state.value,
                "output": child.result if child.state is TaskRunState.SUCCESS else None,
                "error": (
                    (child.result or {}).get("error")
                    if child.state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
                    else None
                ),
            }
            for child in children
        },
    }
    if node.mode == "AGENT_MESH":
        definition = _agent_mesh_definition(node)
        usage = _agent_mesh_usage(node, definition, children)
        result["agentMesh"] = {
            "schemaVersion": "amesh.agent-mesh/v1",
            "topology": definition.topology.value,
            "members": [
                member.model_dump(mode="json", by_alias=True) for member in definition.members
            ],
            "budget": definition.budget.model_dump(mode="json", by_alias=True),
            "usage": usage,
            "routing": [
                child.result["agentRoute"]
                for child in children
                if child.result is not None and "agentRoute" in child.result
            ],
            "handoffs": [
                child.result["agentHandoff"]
                for child in children
                if child.result is not None and "agentHandoff" in child.result
            ],
            "nondeterministic": True,
            "nondeterminismDisclosure": (
                "Topology, routing, policy and budgets are deterministic; model outputs are not."
            ),
        }
    return result


def _agent_mesh_definition(node: PlannedTask) -> AgentMeshDefinition:
    extra = node.task.configuration.handler_view()
    return AgentMeshDefinition.model_validate(
        {
            "topology": extra.get("topology"),
            "members": extra.get("members"),
            "budget": extra.get("budget"),
        }
    )


def _agent_mesh_usage(
    node: PlannedTask,
    definition: AgentMeshDefinition,
    children: list[PersistedTaskRun],
) -> dict[str, object]:
    member_tasks = {member.task for member in definition.members}
    sessions = 0
    total_tokens = 0
    total_cost = Decimal(0)
    tool_calls = 0
    for child in children:
        if child.task_id not in member_tasks:
            continue
        counters: object | None = None
        if child.result is not None:
            session = child.result.get("session")
            if isinstance(session, dict):
                counters = session.get("counters")
        if counters is None:
            failure = child.evidence.get("agentSession")
            if isinstance(failure, dict):
                counters = failure.get("counters")
        if not isinstance(counters, dict):
            continue
        sessions += 1
        total_tokens += _mesh_counter_int(counters, "totalTokens")
        total_cost += Decimal(str(counters.get("costUsd", "0")))
        tool_calls += _mesh_counter_int(counters, "toolCalls")
    return {
        "sessions": sessions,
        "totalTokens": total_tokens,
        "costUsd": str(total_cost),
        "toolCalls": tool_calls,
        "reservedDurationSeconds": sum(
            AgentMeshSessionBudget.model_validate(
                child.configuration.handler_view().get("meshBudget")
            ).max_duration_seconds
            for child in node.task.tasks
            if child.id in member_tasks
        ),
    }


def _mesh_counter_int(counters: Mapping[str, object], key: str) -> int:
    value = counters.get(key, 0)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _agent_mesh_budget_error(
    node: PlannedTask,
    children: list[PersistedTaskRun],
) -> str | None:
    if node.mode != "AGENT_MESH":
        return None
    definition = _agent_mesh_definition(node)
    usage = _agent_mesh_usage(node, definition, children)
    exceeded: list[str] = []
    if _mesh_counter_int(usage, "sessions") > definition.budget.max_sessions:
        exceeded.append("maxSessions")
    if _mesh_counter_int(usage, "totalTokens") > definition.budget.max_total_tokens:
        exceeded.append("maxTotalTokens")
    if Decimal(str(usage["costUsd"])) > definition.budget.max_cost_usd:
        exceeded.append("maxCostUsd")
    if _mesh_counter_int(usage, "toolCalls") > definition.budget.max_tool_calls:
        exceeded.append("maxToolCalls")
    if exceeded:
        return "agent.mesh exceeded parent budget: " + ", ".join(exceeded)
    return None


def _template_visible_output_ids(
    task_id: str,
    tasks_by_id: Mapping[str, TaskDefinition],
) -> frozenset[str]:
    visible: set[str] = set()
    pending = list(tasks_by_id[task_id].depends_on)
    while pending:
        dependency = pending.pop()
        if dependency in visible:
            continue
        visible.add(dependency)
        pending.extend(tasks_by_id[dependency].depends_on)
    return frozenset(visible)


def _expression_context(
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_run: PersistedTaskRun,
    task: TaskDefinition,
    outputs: Mapping[str, dict[str, Any]],
    *,
    iteration: LoopIterationContext | None = None,
    failure_category: FailureCategory | None = None,
    error: str | None = None,
    handler_error: Mapping[str, Any] | None = None,
) -> ExpressionContext:
    return ExpressionContext(
        flow={
            "id": flow.id,
            "namespace": flow.namespace,
            "revision": flow.revision,
        },
        execution={
            "id": str(execution.execution_id),
            "state": execution.state.value,
            "startDate": execution.created_at,
            "tenantId": execution.tenant_id,
        },
        task=task.model_dump(mode="json", by_alias=True),
        taskrun={
            "id": str(task_run.task_run_id),
            "attempt": task_run.current_attempt,
            "state": task_run.state.value,
            "failureCategory": failure_category.value if failure_category is not None else None,
            "error": error,
        },
        trigger=_user_trigger_context(execution),
        inputs=execution.inputs,
        outputs=outputs,
        variables=flow.variables,
        labels=flow.labels,
        namespace={"id": flow.namespace},
        iteration=iteration.as_mapping() if iteration is not None else {},
        error=handler_error or {},
    )


def _flowable_expression_context(
    flow: FlowDefinition,
    execution: PersistedExecution,
    node: PlannedTask,
    task_run: PersistedTaskRun,
    plan: tuple[PlannedTask, ...],
    by_task_id: Mapping[str, PersistedTaskRun],
    *,
    handler_error: Mapping[str, Any] | None = None,
) -> ExpressionContext:
    visible = visible_output_ids(node.task.id, plan)
    outputs = {
        task_id: task_state.result or {}
        for task_id, task_state in by_task_id.items()
        if task_id in visible and task_state.state is TaskRunState.SUCCESS
    }
    return _expression_context(
        flow,
        execution,
        task_run,
        node.task,
        outputs,
        handler_error=handler_error,
    )


def _user_trigger_context(execution: PersistedExecution) -> dict[str, Any]:
    return {key: value for key, value in execution.trigger.items() if not key.startswith("_amesh")}


def _descends_from(
    candidate: PlannedTask,
    ancestor: PlannedTask,
    by_node_id: Mapping[str, PlannedTask],
) -> bool:
    parent_id = candidate.parent_id
    while parent_id is not None:
        if parent_id == ancestor.task.id:
            return True
        parent = by_node_id.get(parent_id)
        parent_id = parent.parent_id if parent is not None else None
    return False


def _branch_evidence(evidence: Mapping[str, Any]) -> dict[str, object] | None:
    control = evidence.get("control")
    if not isinstance(control, Mapping):
        return None
    branch = control.get("branch")
    return dict(branch) if isinstance(branch, Mapping) else None


def _merge_task_control(
    evidence: Mapping[str, Any],
    key: str,
    value: Mapping[str, object],
) -> dict[str, object]:
    merged = deepcopy(dict(evidence))
    existing = merged.get("control")
    control = dict(existing) if isinstance(existing, Mapping) else {}
    control[key] = dict(value)
    merged["control"] = control
    return merged


def _merge_control_evidence(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> dict[str, object]:
    merged = deepcopy(dict(left))
    for source in (left, right):
        control = source.get("control")
        if not isinstance(control, Mapping):
            continue
        existing = merged.get("control")
        combined = dict(existing) if isinstance(existing, Mapping) else {}
        combined.update(dict(control))
        merged["control"] = combined
    return merged


def _merge_completion_evidence(
    completion: Mapping[str, object],
    condition: Mapping[str, object],
) -> dict[str, object]:
    merged = dict(completion)
    control = condition.get("control")
    if isinstance(control, Mapping):
        merged["control"] = dict(control)
    return merged


def _sensitive_input_values(
    flow: FlowDefinition,
    execution: PersistedExecution,
) -> tuple[Any, ...]:
    return tuple(
        execution.inputs[definition.id]
        for definition in flow.inputs
        if definition.sensitive and definition.id in execution.inputs
    )


def _redact_condition_value(value: Any, sensitive_values: tuple[Any, ...]) -> Any:
    for sensitive in sensitive_values:
        try:
            if value == sensitive:
                return "[REDACTED]"
        except (TypeError, ValueError):
            pass
    if isinstance(value, str):
        redacted = value
        for sensitive in sensitive_values:
            if isinstance(sensitive, str) and sensitive:
                redacted = redacted.replace(sensitive, "[REDACTED]")
        return redacted
    if isinstance(value, list):
        return [_redact_condition_value(item, sensitive_values) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_condition_value(item, sensitive_values) for item in value)
    if isinstance(value, Mapping):
        return {key: _redact_condition_value(item, sensitive_values) for key, item in value.items()}
    return redact_secret_values(value)


def _redacted_condition_inputs(
    flow: FlowDefinition,
    execution: PersistedExecution,
    context: ExpressionContext,
) -> dict[str, object]:
    values = context.public_values()
    redacted = redact_secret_values(
        _redact_condition_value(
            values,
            _sensitive_input_values(flow, execution),
        )
    )
    return dict(json.loads(json.dumps(redacted, default=_canonical_json_default)))


def switch_case_key(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.lower() in {"true", "false", "null"}:
            return normalized.lower()
        return normalized
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
