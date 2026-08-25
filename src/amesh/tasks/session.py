from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, cast

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from amesh.domain import (
    AgentCapabilityPin,
    AgentResolutionRequest,
    AgentSessionCheckpoint,
    AgentSessionCounters,
    AgentSessionPhase,
    AgentSessionRecord,
    AgentSessionStart,
    AgentSessionState,
    AgentSessionTransition,
    FailureCategory,
    McpToolImpact,
    ModelDataEgress,
    ModelFallbackMode,
)
from amesh.dsl.models import TaskDefinition
from amesh.executor import (
    TaskCompletion,
    TaskExecutionContext,
    TaskExecutionFailure,
    TaskHandler,
    TaskMetricRecord,
)
from amesh.ports import AgentResourceRepository, AgentSessionRepository


class InvalidAgentOutputPolicy(StrEnum):
    FAIL = "FAIL"
    REPAIR = "REPAIR"


class _AgentSessionTaskSpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    agent: str = Field(min_length=1, max_length=128)
    agent_revision: int = Field(alias="agentRevision", ge=1)
    session_input: dict[str, Any] = Field(alias="input")
    invalid_output_policy: InvalidAgentOutputPolicy = Field(
        default=InvalidAgentOutputPolicy.FAIL,
        alias="invalidOutputPolicy",
    )
    max_repair_attempts: int = Field(default=0, alias="maxRepairAttempts", ge=0, le=20)
    approval_task: str | None = Field(default=None, alias="approvalTask")
    data_handling: ModelDataEgress = Field(
        default=ModelDataEgress.DENY_SECRETS,
        alias="dataHandling",
    )
    business_assertions: tuple[dict[str, Any], ...] = Field(
        default=(),
        alias="businessAssertions",
        max_length=100,
    )

    @field_validator("business_assertions")
    @classmethod
    def validate_assertions(
        cls,
        value: tuple[dict[str, Any], ...],
    ) -> tuple[dict[str, Any], ...]:
        for schema in value:
            try:
                Draft202012Validator.check_schema(schema)
            except SchemaError as exc:
                raise ValueError(f"invalid business assertion schema: {exc.message}") from exc
        return value


def agent_session_handler(
    *,
    resources: AgentResourceRepository,
    sessions: AgentSessionRepository,
    model_handler: TaskHandler,
    mcp_handler: TaskHandler,
) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        spec = _parse_spec(task)
        async with sessions.session_guard(context.tenant_id, context.task_run_id, context.attempt):
            pin = await resources.resolve_agent(
                context.tenant_id,
                context.namespace,
                spec.agent,
                AgentResolutionRequest(
                    agentRevision=spec.agent_revision,
                    subjectRef=f"agent-session:{context.task_run_id}:{context.attempt}",
                ),
                actor_id=f"execution:{context.execution_id}",
            )
            _validate_boundary(task, context, spec, pin)
            record = await sessions.start_session(
                AgentSessionStart(
                    tenantId=context.tenant_id,
                    namespace=context.namespace,
                    executionId=context.execution_id,
                    taskRunId=context.task_run_id,
                    attempt=context.attempt,
                    capabilityPinId=pin.pin_id,
                    envelopeDigest=pin.envelope_digest,
                )
            )
            if record.state is AgentSessionState.SUCCEEDED and record.final_result is not None:
                return _completion(record, pin, record.final_result)
            if record.state is AgentSessionState.FAILED:
                raise TaskExecutionFailure(
                    record.error or "agent session previously failed",
                    FailureCategory.NON_RETRYABLE,
                    evidence=_failure_evidence(record, pin),
                )
            try:
                return await _drive_session(
                    task,
                    context,
                    spec,
                    pin,
                    record,
                    sessions,
                    model_handler,
                    mcp_handler,
                )
            except Exception as exc:
                safe_error = str(_redact(_safe_error(exc), tuple(context.secrets.values())))
                current = await sessions.get_session(
                    context.tenant_id,
                    context.task_run_id,
                    context.attempt,
                )
                record = current.session
                if record.state is AgentSessionState.RUNNING:
                    record = await sessions.transition(
                        record.session_id,
                        tenant_id=context.tenant_id,
                        transition=AgentSessionTransition(
                            eventKey="session.failed",
                            eventType="session.failed",
                            payload={
                                "phase": record.phase.value,
                                "error": safe_error,
                                "nondeterministic": True,
                            },
                            state=AgentSessionState.FAILED,
                            phase=AgentSessionPhase.COMPLETE,
                            checkpoint=record.checkpoint,
                            counters=record.counters,
                            error=safe_error,
                        ),
                    )
                category = (
                    exc.category
                    if isinstance(exc, TaskExecutionFailure)
                    else FailureCategory.NON_RETRYABLE
                )
                if record.counters.tool_calls > 0:
                    category = FailureCategory.NON_RETRYABLE
                raise TaskExecutionFailure(
                    safe_error,
                    category,
                    evidence=_failure_evidence(record, pin),
                ) from exc

    return run


async def _drive_session(
    task: TaskDefinition,
    context: TaskExecutionContext,
    spec: _AgentSessionTaskSpec,
    pin: AgentCapabilityPin,
    record: AgentSessionRecord,
    sessions: AgentSessionRepository,
    model_handler: TaskHandler,
    mcp_handler: TaskHandler,
) -> TaskCompletion:
    envelope = pin.envelope
    if record.version == 0:
        messages = _initial_messages(spec, pin, tuple(context.secrets.values()))
        checkpoint = AgentSessionCheckpoint(messages=messages, nextTurn=1)
        record = await sessions.transition(
            record.session_id,
            tenant_id=context.tenant_id,
            transition=AgentSessionTransition(
                eventKey="session.started",
                eventType="session.started",
                payload={
                    "agentRevision": spec.agent_revision,
                    "envelopeDigest": pin.envelope_digest,
                    "hardLimits": envelope.hard_limits.model_dump(mode="json", by_alias=True),
                    "nondeterminismDisclosure": envelope.output_nondeterminism_disclosure,
                },
                phase=AgentSessionPhase.READY,
                checkpoint=checkpoint,
                counters=AgentSessionCounters(),
            ),
        )

    while True:
        await _check_cancellation(context)
        _check_limits(record, pin)
        action: dict[str, Any]
        if record.checkpoint.pending_action is not None:
            action = record.checkpoint.pending_action
            turn = record.checkpoint.pending_turn
            if turn is None:
                raise RuntimeError("agent checkpoint has a pending action without its turn")
        else:
            turn = record.checkpoint.next_turn
            model_output = await _invoke_model_turn(
                task,
                context,
                pin,
                record,
                model_handler,
            )
            raw_action = model_output.get("structuredOutput")
            if not isinstance(raw_action, dict):
                raise ValueError("agent model turn did not return a structured action")
            action = _normalize_action(raw_action)
            counters = _consume_model_budget(record.counters, model_output, pin)
            safe_action = cast(
                dict[str, Any],
                _redact(action, tuple(context.secrets.values())),
            )
            checkpoint = AgentSessionCheckpoint(
                messages=(
                    *record.checkpoint.messages,
                    {"role": "assistant", "content": json.dumps(safe_action, sort_keys=True)},
                ),
                nextTurn=turn + 1,
                lastAcceptedOperation=f"model:{turn}",
                pendingAction=safe_action,
                pendingTurn=turn,
            )
            record = await sessions.transition(
                record.session_id,
                tenant_id=context.tenant_id,
                transition=AgentSessionTransition(
                    eventKey=f"turn:{turn}:model",
                    eventType="model.response",
                    payload={
                        "turn": turn,
                        "action": safe_action.get("action"),
                        "model": model_output.get("model"),
                        "usage": model_output.get("usage", {}),
                        "costUsd": model_output.get("costUsd", "0"),
                        "counters": counters.model_dump(mode="json", by_alias=True),
                        "nondeterministic": True,
                        "envelopeDigest": pin.envelope_digest,
                    },
                    phase=AgentSessionPhase.POLICY,
                    checkpoint=checkpoint,
                    counters=counters,
                ),
            )

        action_type = action.get("action")
        if action_type == "final":
            output = action.get("output")
            validation_error: str | None
            if not isinstance(output, dict):
                validation_error = "final agent output must be an object"
            else:
                validation_error = _output_validation_error(output, spec, pin)
            if validation_error is None and isinstance(output, dict):
                record = await sessions.transition(
                    record.session_id,
                    tenant_id=context.tenant_id,
                    transition=AgentSessionTransition(
                        eventKey=f"turn:{turn}:completed",
                        eventType="output.accepted",
                        payload={
                            "turn": turn,
                            "schemaValid": True,
                            "businessAssertionsPassed": len(spec.business_assertions),
                            "counters": record.counters.model_dump(mode="json", by_alias=True),
                            "result": _redact(output, tuple(context.secrets.values())),
                        },
                        state=AgentSessionState.SUCCEEDED,
                        phase=AgentSessionPhase.COMPLETE,
                        checkpoint=record.checkpoint,
                        counters=record.counters,
                        finalResult=output,
                    ),
                )
                return _completion(record, pin, output)
            record = await _handle_invalid_output(
                context,
                spec,
                record,
                sessions,
                turn,
                validation_error or "output validation failed",
            )
            continue

        if action_type != "tool":
            raise ValueError("agent action must be 'tool' or 'final'")
        record = await _dispatch_tool(
            task,
            context,
            spec,
            pin,
            record,
            sessions,
            mcp_handler,
            turn,
            action,
        )


async def _invoke_model_turn(
    task: TaskDefinition,
    context: TaskExecutionContext,
    pin: AgentCapabilityPin,
    record: AgentSessionRecord,
    model_handler: TaskHandler,
) -> dict[str, Any]:
    limits = pin.envelope.hard_limits
    remaining_tokens = limits.max_total_tokens - record.counters.total_tokens
    remaining_cost = limits.max_cost_usd - record.counters.cost_usd
    remaining_seconds = limits.max_duration_seconds - _elapsed_seconds(record)
    if remaining_tokens < 1:
        raise ValueError("agent session exhausted maxTotalTokens")
    if remaining_cost < 0:
        raise ValueError("agent session exhausted maxCostUsd")
    if remaining_seconds <= 0:
        raise TaskExecutionFailure(
            "agent session exhausted maxDurationSeconds", FailureCategory.TIMED_OUT
        )

    last_error: TaskExecutionFailure | None = None
    for route_index, route in enumerate(pin.envelope.model_routes):
        model_task = TaskDefinition.model_validate(
            {
                "id": "agent-model-turn",
                "type": "agent.structured",
                "provider": route.provider.model_dump(mode="json", by_alias=True),
                "model": route.model,
                "messages": list(record.checkpoint.messages),
                "outputSchema": _action_schema(pin),
                "schemaName": "amesh_agent_action",
                "parameters": {
                    key: value
                    for key, value in route.parameters.items()
                    if key in {"temperature", "topP", "seed"}
                },
                "budget": {
                    "maxTotalTokens": remaining_tokens,
                    "maxCompletionTokens": min(remaining_tokens, 4096),
                    "maxCostUsd": str(remaining_cost),
                },
                "dataHandling": {
                    "egress": "REDACT_SECRETS",
                    "promptRetention": "REDACTED",
                },
                "timeoutSeconds": min(task.timeout_seconds or 60, float(remaining_seconds)),
                "invocationKey": (
                    f"session:{record.session_id}:turn:{record.checkpoint.next_turn}:"
                    f"route:{route.route_id}"
                ),
                "contract": {"secretScopes": [route.provider.credential_ref]},
            }
        )
        try:
            completion = await model_handler(model_task, context)
            if not isinstance(completion, TaskCompletion):
                raise TypeError("model handler did not return TaskCompletion")
            return completion.output
        except TaskExecutionFailure as exc:
            last_error = exc
            can_fallback = (
                pin.envelope.fallback_mode is ModelFallbackMode.ORDERED
                and route_index + 1 < len(pin.envelope.model_routes)
                and exc.category
                in {
                    FailureCategory.RETRYABLE,
                    FailureCategory.INFRASTRUCTURE,
                    FailureCategory.TIMED_OUT,
                }
            )
            if not can_fallback:
                raise
    if last_error is not None:
        raise last_error
    raise RuntimeError("agent model policy has no route")


async def _dispatch_tool(
    task: TaskDefinition,
    context: TaskExecutionContext,
    spec: _AgentSessionTaskSpec,
    pin: AgentCapabilityPin,
    record: AgentSessionRecord,
    sessions: AgentSessionRepository,
    mcp_handler: TaskHandler,
    turn: int,
    action: dict[str, Any],
) -> AgentSessionRecord:
    limits = pin.envelope.hard_limits
    if record.counters.tool_calls >= limits.max_tool_calls:
        raise ValueError("agent session exhausted maxToolCalls")
    tool_name = action.get("tool")
    arguments = action.get("arguments")
    if not isinstance(tool_name, str) or not tool_name:
        raise ValueError("tool action requires a tool name")
    if not isinstance(arguments, dict):
        raise ValueError("tool action arguments must be an object")
    tool = next((item for item in pin.envelope.tools if item.tool_name == tool_name), None)
    if tool is None:
        raise PermissionError(f"model proposed unpinned tool {tool_name!r}")

    needs_approval = tool.impact is McpToolImpact.HIGH_IMPACT or (
        spec.data_handling is ModelDataEgress.ALLOW
    )
    approval_payload: dict[str, Any] = {"required": needs_approval}
    if needs_approval:
        _require_approval(task, context, spec)
        approval_payload.update({"task": spec.approval_task, "decision": "APPROVED"})
    record = await sessions.transition(
        record.session_id,
        tenant_id=context.tenant_id,
        transition=AgentSessionTransition(
            eventKey=f"turn:{turn}:policy",
            eventType="policy.authorized",
            payload={
                "turn": turn,
                "tool": tool_name,
                "impact": tool.impact.value,
                "approval": approval_payload,
                "envelopeDigest": pin.envelope_digest,
            },
            phase=(AgentSessionPhase.APPROVAL if needs_approval else AgentSessionPhase.TOOL),
            checkpoint=record.checkpoint,
            counters=record.counters,
        ),
    )
    await _check_cancellation(context)
    if _remaining_seconds(record, pin) <= 0:
        raise TaskExecutionFailure(
            "agent session exhausted maxDurationSeconds",
            FailureCategory.TIMED_OUT,
        )
    mcp_task = TaskDefinition.model_validate(
        {
            "id": "agent-tool-call",
            "type": "agent.mcp",
            "dependsOn": list(task.depends_on),
            "connection": tool.connection_key,
            "revision": tool.connection_revision,
            "tool": tool.tool_name,
            "arguments": arguments,
            "dataHandling": spec.data_handling.value,
            "allowWrite": tool.impact is not McpToolImpact.READ_ONLY,
            "approvalTask": spec.approval_task,
            "invocationKey": f"session:{record.session_id}:turn:{turn}:tool:{tool.tool_name}",
            "timeoutSeconds": min(
                task.timeout_seconds or 30, float(_remaining_seconds(record, pin))
            ),
            "contract": {
                "secretScopes": list(pin.envelope.permissions.secret_scopes),
            },
        }
    )
    completion = await mcp_handler(mcp_task, context)
    output = completion.output if isinstance(completion, TaskCompletion) else completion
    if not isinstance(output, dict):
        raise TypeError("MCP handler returned a non-object result")
    safe_output = cast(dict[str, Any], _redact(output, tuple(context.secrets.values())))
    counters = record.counters.model_copy(update={"tool_calls": record.counters.tool_calls + 1})
    checkpoint = AgentSessionCheckpoint(
        messages=(
            *record.checkpoint.messages,
            {
                "role": "user",
                "content": json.dumps(
                    {"tool": tool_name, "result": safe_output},
                    sort_keys=True,
                ),
            },
        ),
        nextTurn=record.checkpoint.next_turn,
        lastAcceptedOperation=f"tool:{turn}:{tool_name}",
        pendingAction=None,
        pendingTurn=None,
    )
    return await sessions.transition(
        record.session_id,
        tenant_id=context.tenant_id,
        transition=AgentSessionTransition(
            eventKey=f"turn:{turn}:tool",
            eventType="tool.result",
            payload={
                "turn": turn,
                "tool": tool_name,
                "impact": tool.impact.value,
                "result": safe_output,
                "toolCalls": counters.tool_calls,
            },
            phase=AgentSessionPhase.READY,
            checkpoint=checkpoint,
            counters=counters,
        ),
    )


async def _handle_invalid_output(
    context: TaskExecutionContext,
    spec: _AgentSessionTaskSpec,
    record: AgentSessionRecord,
    sessions: AgentSessionRepository,
    turn: int,
    error: str,
) -> AgentSessionRecord:
    repairs = record.counters.repair_attempts
    can_repair = (
        spec.invalid_output_policy is InvalidAgentOutputPolicy.REPAIR
        and repairs < spec.max_repair_attempts
    )
    counters = record.counters.model_copy(update={"repair_attempts": repairs + 1})
    checkpoint = AgentSessionCheckpoint(
        messages=(
            *record.checkpoint.messages,
            {
                "role": "user",
                "content": (
                    "The proposed final output was rejected by AMESH validation: "
                    f"{error}. Return a corrected action."
                ),
            },
        ),
        nextTurn=record.checkpoint.next_turn,
        lastAcceptedOperation=record.checkpoint.last_accepted_operation,
        pendingAction=None,
        pendingTurn=None,
    )
    if not can_repair:
        failed = await sessions.transition(
            record.session_id,
            tenant_id=context.tenant_id,
            transition=AgentSessionTransition(
                eventKey=f"turn:{turn}:output-rejected",
                eventType="output.rejected",
                payload={"turn": turn, "error": error, "repairScheduled": False},
                state=AgentSessionState.FAILED,
                phase=AgentSessionPhase.COMPLETE,
                checkpoint=checkpoint,
                counters=counters,
                error=error,
            ),
        )
        raise TaskExecutionFailure(
            error,
            FailureCategory.NON_RETRYABLE,
            evidence={"agentSession": {"sessionId": str(failed.session_id)}},
        )
    return await sessions.transition(
        record.session_id,
        tenant_id=context.tenant_id,
        transition=AgentSessionTransition(
            eventKey=f"turn:{turn}:output-rejected",
            eventType="output.rejected",
            payload={"turn": turn, "error": error, "repairScheduled": True},
            phase=AgentSessionPhase.READY,
            checkpoint=checkpoint,
            counters=counters,
        ),
    )


def _parse_spec(task: TaskDefinition) -> _AgentSessionTaskSpec:
    try:
        return _AgentSessionTaskSpec.model_validate(task.model_extra or {})
    except ValidationError as exc:
        raise ValueError(f"task {task.id!r} agent session configuration is invalid: {exc}") from exc


def _validate_boundary(
    task: TaskDefinition,
    context: TaskExecutionContext,
    spec: _AgentSessionTaskSpec,
    pin: AgentCapabilityPin,
) -> None:
    envelope = pin.envelope
    try:
        Draft202012Validator(envelope.input_schema).validate(spec.session_input)
    except JsonSchemaValidationError as exc:
        raise ValueError(f"agent input failed schema: {exc.message}") from exc
    declared = set(task.contract.secret_scopes)
    permitted = set(envelope.permissions.secret_scopes)
    if not permitted.issubset(declared):
        raise PermissionError("agent secretScopes must be declared by the session task contract")
    unavailable = permitted - set(context.secrets)
    if unavailable:
        raise PermissionError(
            f"agent session secrets are unavailable: {', '.join(sorted(unavailable))}"
        )
    if envelope.hard_limits.max_concurrency < 1:
        raise ValueError("agent session requires maxConcurrency of at least one")
    if envelope.evaluation_policy.required_evaluations:
        raise ValueError("required agent evaluations are unavailable until EPIC-809")
    if envelope.evaluation_policy.require_human_release:
        raise ValueError("human release gates are unavailable until EPIC-809")
    if spec.invalid_output_policy is InvalidAgentOutputPolicy.FAIL and spec.max_repair_attempts:
        raise ValueError("maxRepairAttempts requires invalidOutputPolicy REPAIR")


def _initial_messages(
    spec: _AgentSessionTaskSpec,
    pin: AgentCapabilityPin,
    secrets: tuple[str, ...],
) -> tuple[dict[str, Any], ...]:
    instructions = "\n\n".join(fragment.content for fragment in pin.envelope.instructions)
    tool_lines = [
        f"- {tool.tool_name} ({tool.impact.value}, pinned schema {tool.schema_digest})"
        for tool in pin.envelope.tools
    ]
    system = (
        f"{instructions}\n\n"
        "AMESH supervises this bounded session. Return exactly one structured action. "
        "Use action='tool' to propose one listed tool, or action='final' with the required output. "
        "For a tool action, encode the arguments object as a JSON string and set output to null. "
        "For a final action, set arguments to null and return the required output object. "
        "You cannot invoke tools directly or expand your authority.\n"
        f"Available tools:\n{chr(10).join(tool_lines) if tool_lines else '- none'}"
    )
    safe_input = _redact(spec.session_input, secrets)
    return (
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps({"input": safe_input}, sort_keys=True)},
    )


def _action_schema(pin: AgentCapabilityPin) -> dict[str, Any]:
    tool_names = [str(tool.tool_name) for tool in pin.envelope.tools]
    return {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["tool", "final"]},
            "tool": {
                "type": "string",
                "enum": tool_names if tool_names else ["none"],
            },
            "arguments": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
            },
            "output": {
                "anyOf": [pin.envelope.output_schema, {"type": "null"}],
            },
            "rationale": {"type": "string"},
        },
        "required": ["action", "tool", "arguments", "output", "rationale"],
        "additionalProperties": False,
    }


def _normalize_action(action: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(action)
    for field in ("arguments", "output"):
        value = normalized.get(field)
        if value is None:
            normalized[field] = {}
            continue
        if isinstance(value, dict):
            continue
        if not isinstance(value, str):
            raise ValueError(f"agent action {field} must be a JSON object string")
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"agent action {field} is not valid JSON") from exc
        if not isinstance(decoded, dict):
            raise ValueError(f"agent action {field} must decode to an object")
        normalized[field] = decoded
    return normalized


def _consume_model_budget(
    counters: AgentSessionCounters,
    output: dict[str, Any],
    pin: AgentCapabilityPin,
) -> AgentSessionCounters:
    usage = output.get("usage")
    if not isinstance(usage, dict):
        raise RuntimeError("agent model response omitted usage")
    total_tokens = usage.get("total_tokens")
    if not isinstance(total_tokens, int) or isinstance(total_tokens, bool):
        raise RuntimeError("agent model response omitted total_tokens")
    try:
        cost = Decimal(str(output.get("costUsd")))
    except (InvalidOperation, ValueError) as exc:
        raise RuntimeError("agent model response omitted costUsd") from exc
    updated = AgentSessionCounters(
        turns=counters.turns + 1,
        loopIterations=max(0, counters.turns),
        toolCalls=counters.tool_calls,
        totalTokens=counters.total_tokens + total_tokens,
        costUsd=counters.cost_usd + cost,
        repairAttempts=counters.repair_attempts,
    )
    limits = pin.envelope.hard_limits
    if updated.total_tokens > limits.max_total_tokens:
        raise ValueError("agent session exceeded maxTotalTokens")
    if updated.cost_usd > limits.max_cost_usd:
        raise ValueError("agent session exceeded maxCostUsd")
    return updated


def _check_limits(record: AgentSessionRecord, pin: AgentCapabilityPin) -> None:
    limits = pin.envelope.hard_limits
    counters = record.counters
    if counters.turns >= limits.max_turns:
        raise ValueError("agent session exhausted maxTurns")
    if counters.loop_iterations >= limits.max_loop_iterations and counters.turns > 0:
        raise ValueError("agent session exhausted maxLoopIterations")
    if counters.tool_calls > limits.max_tool_calls:
        raise ValueError("agent session exceeded maxToolCalls")
    if counters.total_tokens >= limits.max_total_tokens:
        raise ValueError("agent session exhausted maxTotalTokens")
    if counters.cost_usd > limits.max_cost_usd:
        raise ValueError("agent session exceeded maxCostUsd")
    if _remaining_seconds(record, pin) <= 0:
        raise TaskExecutionFailure(
            "agent session exhausted maxDurationSeconds", FailureCategory.TIMED_OUT
        )


def _elapsed_seconds(record: AgentSessionRecord) -> float:
    return max(0.0, (datetime.now(UTC) - record.created_at).total_seconds())


def _remaining_seconds(record: AgentSessionRecord, pin: AgentCapabilityPin) -> int:
    return int(pin.envelope.hard_limits.max_duration_seconds - _elapsed_seconds(record))


async def _check_cancellation(context: TaskExecutionContext) -> None:
    if await context.cancellation.requested():
        raise TaskExecutionFailure("agent session was cancelled", FailureCategory.CANCELLED)


def _output_validation_error(
    output: dict[str, Any],
    spec: _AgentSessionTaskSpec,
    pin: AgentCapabilityPin,
) -> str | None:
    errors = sorted(
        Draft202012Validator(pin.envelope.output_schema).iter_errors(output),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        return f"output schema failed: {errors[0].message}"
    for index, assertion in enumerate(spec.business_assertions, start=1):
        errors = list(Draft202012Validator(assertion).iter_errors(output))
        if errors:
            return f"business assertion {index} failed: {errors[0].message}"
    return None


def _require_approval(
    task: TaskDefinition,
    context: TaskExecutionContext,
    spec: _AgentSessionTaskSpec,
) -> None:
    approval = context.outputs.get(spec.approval_task) if spec.approval_task else None
    if not isinstance(approval, dict) or approval.get("decision") != "APPROVED":
        raise PermissionError("agent action requires an APPROVED approvalTask output")
    if spec.approval_task not in task.depends_on:
        raise PermissionError("approvalTask must be a direct task dependency")


def _completion(
    record: AgentSessionRecord,
    pin: AgentCapabilityPin,
    output: dict[str, Any],
) -> TaskCompletion:
    counters = record.counters
    result = {
        "result": output,
        "session": {
            "sessionId": str(record.session_id),
            "state": record.state.value,
            "phase": record.phase.value,
            "capabilityPinId": str(record.capability_pin_id),
            "envelopeDigest": pin.envelope_digest,
            "counters": counters.model_dump(mode="json", by_alias=True),
            "nondeterministic": True,
            "nondeterminismDisclosure": pin.envelope.output_nondeterminism_disclosure,
        },
    }
    return TaskCompletion(
        output=result,
        metrics=(
            TaskMetricRecord(
                name="agent.session.turns", value=Decimal(counters.turns), unit="turns"
            ),
            TaskMetricRecord(
                name="agent.session.tool_calls",
                value=Decimal(counters.tool_calls),
                unit="calls",
            ),
            TaskMetricRecord(
                name="agent.session.tokens",
                value=Decimal(counters.total_tokens),
                unit="tokens",
            ),
            TaskMetricRecord(name="agent.session.cost", value=counters.cost_usd, unit="USD"),
        ),
    )


def _failure_evidence(
    record: AgentSessionRecord,
    pin: AgentCapabilityPin,
) -> dict[str, object]:
    return {
        "agentSession": {
            "sessionId": str(record.session_id),
            "state": record.state.value,
            "phase": record.phase.value,
            "envelopeDigest": pin.envelope_digest,
            "counters": record.counters.model_dump(mode="json", by_alias=True),
            "nondeterministic": True,
        }
    }


def _safe_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: {str(exc)[:2000]}"


def _redact(value: Any, secrets: tuple[str, ...]) -> Any:
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            if secret:
                redacted = redacted.replace(secret, "[REDACTED]")
        return redacted
    if isinstance(value, dict):
        return {str(key): _redact(item, secrets) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_redact(item, secrets) for item in value]
    return value
