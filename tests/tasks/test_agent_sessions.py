from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest

from amesh.domain import (
    AgentCapabilityPin,
    AgentEvaluationPolicy,
    AgentHardLimits,
    AgentMemoryPolicy,
    AgentPermissions,
    AgentResourceKind,
    AgentSessionDetail,
    AgentSessionEvent,
    AgentSessionRecord,
    AgentSessionStart,
    AgentSessionState,
    AgentSessionTransition,
    EffectiveCapabilityEnvelope,
    FailureCategory,
    InstructionFragment,
    McpToolImpact,
    ModelFallbackMode,
    ModelProviderSpec,
    ModelRoute,
    ResolvedResourcePin,
    ResolvedToolPin,
    new_runtime_id,
)
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext, TaskExecutionFailure
from amesh.tasks import agent_session_handler


class MemoryResources:
    def __init__(self, pin: AgentCapabilityPin) -> None:
        self.pin = pin
        self.subjects: list[str] = []

    async def resolve_agent(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        request: Any,
        *,
        actor_id: str,
    ) -> AgentCapabilityPin:
        assert tenant_id == self.pin.tenant_id
        assert namespace == self.pin.namespace
        assert key == "helper"
        assert actor_id.startswith("execution:")
        self.subjects.append(request.subject_ref)
        return self.pin

    async def save_resource(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    async def get_resource(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    async def list_resources(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class MemorySessions:
    def __init__(self) -> None:
        self.records: dict[tuple[str, UUID, int], AgentSessionRecord] = {}
        self.events: dict[UUID, list[AgentSessionEvent]] = {}

    @asynccontextmanager
    async def session_guard(
        self,
        tenant_id: str,
        task_run_id: UUID,
        attempt: int,
    ) -> AsyncIterator[None]:
        del tenant_id, task_run_id, attempt
        yield

    async def start_session(self, start: AgentSessionStart) -> AgentSessionRecord:
        key = (start.tenant_id, start.task_run_id, start.attempt)
        record = self.records.get(key)
        if record is None:
            record = AgentSessionRecord(**start.model_dump(mode="python", by_alias=True))
            self.records[key] = record
            self.events[record.session_id] = []
        return record

    async def transition(
        self,
        session_id: UUID,
        *,
        tenant_id: str,
        transition: AgentSessionTransition,
    ) -> AgentSessionRecord:
        key, record = next(
            (
                (key, item)
                for key, item in self.records.items()
                if item.session_id == session_id and item.tenant_id == tenant_id
            ),
            (None, None),
        )
        assert key is not None and record is not None
        existing = next(
            (event for event in self.events[session_id] if event.event_key == transition.event_key),
            None,
        )
        if existing is not None:
            return record
        now = datetime.now(UTC)
        updated = record.model_copy(
            update={
                "state": transition.state,
                "phase": transition.phase,
                "version": record.version + 1,
                "checkpoint": transition.checkpoint,
                "counters": transition.counters,
                "final_result": transition.final_result,
                "error": transition.error,
                "updated_at": now,
                "completed_at": (
                    now if transition.state is not AgentSessionState.RUNNING else None
                ),
            }
        )
        self.records[key] = updated
        self.events[session_id].append(
            AgentSessionEvent(
                sessionId=session_id,
                eventIndex=updated.version,
                eventKey=transition.event_key,
                eventType=transition.event_type,
                payload=transition.payload,
            )
        )
        return updated

    async def get_session(
        self,
        tenant_id: str,
        task_run_id: UUID,
        attempt: int,
    ) -> AgentSessionDetail:
        record = self.records[(tenant_id, task_run_id, attempt)]
        return AgentSessionDetail(session=record, events=tuple(self.events[record.session_id]))

    async def list_execution_sessions(
        self,
        tenant_id: str,
        execution_id: UUID,
    ) -> tuple[AgentSessionRecord, ...]:
        return tuple(
            record
            for record in self.records.values()
            if record.tenant_id == tenant_id and record.execution_id == execution_id
        )


class ScriptedModel:
    def __init__(self, actions: list[dict[str, Any]]) -> None:
        self.actions = actions
        self.calls: list[TaskDefinition] = []

    async def __call__(
        self,
        task: TaskDefinition,
        context: TaskExecutionContext,
    ) -> TaskCompletion:
        del context
        self.calls.append(task)
        action = self.actions.pop(0)
        return TaskCompletion(
            output={
                "structuredOutput": action,
                "model": "openai/gpt-5.6-luna",
                "usage": {"total_tokens": 5},
                "costUsd": "0.001",
            }
        )


class SimulatedWorkerCrash(BaseException):
    pass


class ScriptedMcp:
    def __init__(self, *, crash_once: bool = False) -> None:
        self.crash_once = crash_once
        self.calls: list[TaskDefinition] = []
        self.effects = 0
        self.results: dict[str, TaskCompletion] = {}

    async def __call__(
        self,
        task: TaskDefinition,
        context: TaskExecutionContext,
    ) -> TaskCompletion:
        del context
        self.calls.append(task)
        assert task.model_extra is not None
        invocation_key = str(task.model_extra["invocationKey"])
        if invocation_key not in self.results:
            self.effects += 1
            self.results[invocation_key] = TaskCompletion(
                output={"structuredContent": {"value": "found"}}
            )
        if self.crash_once:
            self.crash_once = False
            raise SimulatedWorkerCrash
        return self.results[invocation_key]


def _pin(
    *,
    impact: McpToolImpact = McpToolImpact.READ_ONLY,
    max_turns: int = 4,
    max_loops: int = 3,
) -> AgentCapabilityPin:
    agent_id = uuid4()
    route = ModelRoute(
        routeId="luna",
        provider=ModelProviderSpec(
            endpoint="https://openrouter.ai/api/v1/chat/completions",
            credentialRef="openrouter",
        ),
        model="openai/gpt-5.6-luna",
    )
    agent = ResolvedResourcePin(
        resourceId=agent_id,
        kind=AgentResourceKind.AGENT,
        key="helper",
        revision=1,
        digest="sha256:" + "1" * 64,
    )
    tool = ResolvedToolPin(
        connectionId=uuid4(),
        connectionKey="catalog",
        connectionRevision=1,
        connectionDigest="sha256:" + "2" * 64,
        toolName="lookup",
        schemaDigest="sha256:" + "3" * 64,
        impact=impact,
    )
    envelope = EffectiveCapabilityEnvelope(
        agent=agent,
        resources=(agent,),
        instructions=(
            InstructionFragment(sourceKind="AGENT", sourceKey="helper", order=-1, content="Help."),
        ),
        promptVariables={},
        modelRoutes=(route,),
        fallbackMode=ModelFallbackMode.DISABLED,
        outputNondeterminismDisclosure="Model output is nondeterministic.",
        tools=(tool,),
        inputSchema={
            "type": "object",
            "properties": {"question": {"type": "string"}},
            "required": ["question"],
            "additionalProperties": False,
        },
        outputSchema={
            "type": "object",
            "properties": {"answer": {"type": "string"}},
            "required": ["answer"],
            "additionalProperties": False,
        },
        memoryPolicy=AgentMemoryPolicy(),
        permissions=AgentPermissions(
            toolAllowlist=("lookup",),
            secretScopes=("openrouter", "mcp-token"),
            networkHosts=("openrouter.ai", "mcp.example.test"),
            allowHighImpactTools=impact is McpToolImpact.HIGH_IMPACT,
        ),
        hardLimits=AgentHardLimits(
            maxTotalTokens=100,
            maxCostUsd=Decimal("1"),
            maxDurationSeconds=60,
            maxToolCalls=2,
            maxTurns=max_turns,
            maxLoopIterations=max_loops,
            maxRecursionDepth=0,
            maxConcurrency=1,
        ),
        evaluationPolicy=AgentEvaluationPolicy(),
    )
    return AgentCapabilityPin(
        tenantId="default",
        namespace="agents.demo",
        subjectRef="fixture",
        envelopeDigest=envelope.digest,
        envelope=envelope,
        createdBy="author",
        createdAt=datetime.now(UTC),
    )


def _context(*, outputs: dict[str, dict[str, Any]] | None = None) -> TaskExecutionContext:
    return TaskExecutionContext(
        tenant_id="default",
        namespace="agents.demo",
        execution_id=uuid4(),
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=new_runtime_id(),
        inputs={},
        outputs=outputs or {},
        variables={},
        secret_scopes=("openrouter", "mcp-token"),
        secrets={"openrouter": "router-secret", "mcp-token": "mcp-secret"},
    )


def _task(
    *,
    approval: bool = False,
    repair: bool = False,
    question: str = "Find it",
) -> TaskDefinition:
    payload: dict[str, Any] = {
        "id": "session",
        "type": "agent.session",
        "agent": "helper",
        "agentRevision": 1,
        "input": {"question": question},
        "invalidOutputPolicy": "REPAIR" if repair else "FAIL",
        "maxRepairAttempts": 1 if repair else 0,
        "contract": {"secretScopes": ["openrouter", "mcp-token"]},
    }
    if approval:
        payload.update({"dependsOn": ["approve"], "approvalTask": "approve"})
    return TaskDefinition.model_validate(payload)


def test_session_resumes_pending_tool_without_repeating_accepted_model_turn() -> None:
    async def scenario() -> None:
        pin = _pin()
        sessions = MemorySessions()
        model = ScriptedModel(
            [
                {
                    "action": "tool",
                    "tool": "lookup",
                    "arguments": '{"key":"one"}',
                    "output": None,
                    "rationale": "Need evidence",
                },
                {
                    "action": "final",
                    "tool": "lookup",
                    "arguments": None,
                    "output": {"answer": "found"},
                    "rationale": "Done",
                },
            ]
        )
        mcp = ScriptedMcp(crash_once=True)
        handler = agent_session_handler(
            resources=MemoryResources(pin),
            sessions=sessions,
            model_handler=model,
            mcp_handler=mcp,
        )
        context = _context()
        with pytest.raises(SimulatedWorkerCrash):
            await handler(_task(question="router-secret"), context)
        detail = await sessions.get_session("default", context.task_run_id, 1)
        assert detail.session.checkpoint.pending_action is not None
        assert "router-secret" not in repr(detail)
        assert "[REDACTED]" in repr(detail)
        assert len(model.calls) == 1

        completed = await handler(_task(question="router-secret"), context)
        assert isinstance(completed, TaskCompletion)
        assert completed.output["result"] == {"answer": "found"}
        assert completed.output["session"]["counters"] == {
            "turns": 2,
            "loopIterations": 1,
            "toolCalls": 1,
            "totalTokens": 10,
            "costUsd": "0.002",
            "repairAttempts": 0,
        }
        assert len(model.calls) == 2
        assert len(mcp.calls) == 2
        assert mcp.effects == 1
        assert model.calls[0].model_extra is not None
        assert mcp.calls[1].model_extra is not None
        assert model.calls[0].model_extra["invocationKey"].endswith("turn:1:route:luna")
        assert mcp.calls[1].model_extra["invocationKey"].endswith("turn:1:tool:lookup")
        detail = await sessions.get_session("default", context.task_run_id, 1)
        assert detail.session.state is AgentSessionState.SUCCEEDED
        assert [event.event_type for event in detail.events] == [
            "session.started",
            "model.response",
            "policy.authorized",
            "tool.result",
            "model.response",
            "output.accepted",
        ]

    asyncio.run(scenario())


def test_session_repairs_invalid_output_within_hard_turn_limit() -> None:
    async def scenario() -> None:
        pin = _pin()
        sessions = MemorySessions()
        model = ScriptedModel(
            [
                {
                    "action": "final",
                    "tool": "lookup",
                    "arguments": {},
                    "output": {"answer": 42},
                    "rationale": "Draft",
                },
                {
                    "action": "final",
                    "tool": "lookup",
                    "arguments": None,
                    "output": {"answer": "fixed"},
                    "rationale": "Repaired",
                },
            ]
        )
        handler = agent_session_handler(
            resources=MemoryResources(pin),
            sessions=sessions,
            model_handler=model,
            mcp_handler=ScriptedMcp(),
        )
        result = await handler(_task(repair=True), _context())
        assert isinstance(result, TaskCompletion)
        assert result.output["result"] == {"answer": "fixed"}
        assert result.output["session"]["counters"]["repairAttempts"] == 1

    asyncio.run(scenario())


def test_session_stops_runaway_loop_and_denies_high_impact_without_approval() -> None:
    action = {
        "action": "tool",
        "tool": "lookup",
        "arguments": {"key": "one"},
        "output": {},
        "rationale": "Continue",
    }

    async def scenario() -> None:
        runaway_sessions = MemorySessions()
        runaway_mcp = ScriptedMcp()
        runaway = agent_session_handler(
            resources=MemoryResources(_pin(max_turns=1, max_loops=0)),
            sessions=runaway_sessions,
            model_handler=ScriptedModel([action]),
            mcp_handler=runaway_mcp,
        )
        with pytest.raises(TaskExecutionFailure, match="maxTurns") as stopped:
            await runaway(_task(), _context())
        assert stopped.value.category is FailureCategory.NON_RETRYABLE
        assert len(runaway_mcp.calls) == 1

        denied_mcp = ScriptedMcp()
        denied = agent_session_handler(
            resources=MemoryResources(_pin(impact=McpToolImpact.HIGH_IMPACT)),
            sessions=MemorySessions(),
            model_handler=ScriptedModel([action]),
            mcp_handler=denied_mcp,
        )
        with pytest.raises(TaskExecutionFailure, match="APPROVED") as rejection:
            await denied(_task(approval=True), _context())
        assert rejection.value.category is FailureCategory.NON_RETRYABLE
        assert denied_mcp.calls == []

    asyncio.run(scenario())
