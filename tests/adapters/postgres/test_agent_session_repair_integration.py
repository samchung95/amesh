from __future__ import annotations

import asyncio
import json
import os
import shutil
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.agent_session_harness import PiAgentSessionHarness
from amesh.adapters.postgres import (
    PostgresAgentPrimitiveRepository,
    PostgresAgentProgressSink,
    PostgresAgentResourceRepository,
    PostgresAgentSessionRepository,
    PostgresExecutionRepository,
)
from amesh.domain import (
    AgentDefinitionSpec,
    AgentEvaluationPolicy,
    AgentHardLimits,
    AgentMemoryPolicy,
    AgentPermissions,
    AgentResourceRef,
    AgentSessionState,
    ModelPolicySpec,
    ModelProviderSpec,
    ModelRoute,
    new_runtime_id,
)
from amesh.dsl import FlowDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext, TaskExecutionFailure
from amesh.ports import ModelProviderResponse
from amesh.tasks import agent_llm_handler, agent_session_handler

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
_ROOT = Path(__file__).resolve().parents[3]
_PI_WORKER = _ROOT / "harnesses" / "pi" / "src" / "worker.mjs"
_PI_PACKAGE = _ROOT / "harnesses" / "pi" / "node_modules" / "@earendil-works" / "pi-agent-core"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class _InvalidThenValidProvider:
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self.requests: list[Any] = []

    async def invoke(self, request: Any, access: Any) -> ModelProviderResponse:
        del access
        self.requests.append(request)
        action: dict[str, Any] = {
            "action": "final",
            "tool": "none",
            "arguments": None,
            "output": {"answer": "fixed"},
        }
        invalid = self.kind == "exhausted" or (len(self.requests) == 1 and self.kind != "valid")
        if not invalid or self.kind != "schema":
            action["rationale"] = "Repaired with a schema-valid public rationale."
        if invalid and self.kind in {"business", "exhausted"}:
            action["output"] = {"answer": "wrong"}
        content = "{broken" if invalid and self.kind == "json" else json.dumps(action)
        return ModelProviderResponse(
            payload={
                "choices": [{"message": {"content": content}}],
                "usage": {
                    "prompt_tokens": 4,
                    "completion_tokens": 1,
                    "total_tokens": 5,
                    "cost": 0.001,
                },
            }
        )

    async def stream(self, request: Any, access: Any):
        from amesh.adapters.openai_compatible import OpenAICompatibleModelProvider

        response = await self.invoke(request, access)
        content = response.payload["choices"][0]["message"]["content"]
        chunks = [
            {"choices": [{"delta": {"content": content[: len(content) // 2]}}]},
            {
                "choices": [
                    {"delta": {"content": content[len(content) // 2 :]}, "finish_reason": "stop"}
                ],
                "usage": response.payload["usage"],
            },
        ]
        body = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks) + "data: [DONE]\n\n"
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda _: httpx.Response(
                    200, headers={"content-type": "text/event-stream"}, content=body
                )
            )
        ) as client:
            async for event in OpenAICompatibleModelProvider(client).stream(request, access):
                yield event


async def _unused_mcp(*args: Any, **kwargs: Any) -> TaskCompletion:
    del args, kwargs
    raise AssertionError("the repair-only session must not dispatch a tool")


@pytest.mark.parametrize(
    "mode",
    [
        "unary-schema",
        "stream-schema",
        "stream-json",
        "stream-business",
        "stream-valid",
        "stream-exhausted",
    ],
)
def test_real_pi_repair_has_unique_durable_postgres_progress(
    migrated_test_database_url: str,
    mode: str,
) -> None:
    async def scenario() -> None:
        node = shutil.which("node")
        if node is None or not _PI_PACKAGE.exists():
            pytest.fail("Pi/PostgreSQL repair qualification requires the installed Pi harness")

        engine = create_async_engine(migrated_test_database_url)
        resources = PostgresAgentResourceRepository(engine)
        sessions = PostgresAgentSessionRepository(engine)
        invocations = PostgresAgentPrimitiveRepository(engine)
        executions = PostgresExecutionRepository(engine)
        transport, kind = mode.split("-")
        provider = _InvalidThenValidProvider(kind)
        expected_calls = 1 if kind == "valid" else 2
        try:
            model_policy = await resources.save_resource(
                "default",
                ModelPolicySpec(
                    key="repair-model",
                    namespace="agents.repair-test",
                    title="Repair model",
                    routes=(
                        ModelRoute(
                            routeId="primary",
                            provider=ModelProviderSpec(
                                endpoint="https://openrouter.ai/api/v1/chat/completions",
                                credentialRef="openrouter",
                            ),
                            model="openai/gpt-5.6-luna",
                            parameters={"transportMode": transport.upper()},
                        ),
                    ),
                    outputNondeterminismDisclosure="Model output can vary.",
                ),
                actor_id="test",
            )
            agent = await resources.save_resource(
                "default",
                AgentDefinitionSpec(
                    key="helper",
                    namespace="agents.repair-test",
                    title="Repair helper",
                    instructions="Return the requested structured result.",
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
                    modelPolicy=AgentResourceRef(
                        key=model_policy.key,
                        revision=model_policy.revision,
                    ),
                    memoryPolicy=AgentMemoryPolicy(),
                    permissions=AgentPermissions(
                        secretScopes=("openrouter",),
                        networkHosts=("openrouter.ai",),
                    ),
                    hardLimits=AgentHardLimits(
                        maxTotalTokens=100,
                        maxCostUsd=Decimal("1"),
                        maxDurationSeconds=60,
                        maxToolCalls=0,
                        maxTurns=4,
                        maxLoopIterations=4,
                        maxRecursionDepth=0,
                        maxConcurrency=1,
                    ),
                    evaluationPolicy=AgentEvaluationPolicy(),
                ),
                actor_id="test",
            )
            flow = FlowDefinition.model_validate(
                {
                    "id": "pi-postgres-repair",
                    "namespace": "agents.repair-test",
                    "tasks": [
                        {
                            "id": "session",
                            "type": "agent.session",
                            "agent": "helper",
                            "agentRevision": agent.revision,
                            "input": {"question": "Return a fixed answer."},
                            "invalidOutputPolicy": "REPAIR",
                            "maxRepairAttempts": 1,
                            "businessAssertions": [{"properties": {"answer": {"const": "fixed"}}}],
                            "contract": {"secretScopes": ["openrouter"]},
                        }
                    ],
                }
            )
            execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                trigger={},
            )
            task_run = (
                await executions.list_task_runs(execution.execution_id, tenant_id="default")
            )[0]
            context = TaskExecutionContext(
                tenant_id="default",
                namespace=flow.namespace,
                execution_id=execution.execution_id,
                task_run_id=task_run.task_run_id,
                attempt=1,
                attempt_id=new_runtime_id(),
                inputs={},
                outputs={},
                variables={},
                secret_scopes=("openrouter",),
                secrets={"openrouter": "test-only-secret"},
            )
            progress = PostgresAgentProgressSink(sessions)
            model = agent_llm_handler(
                provider=provider,
                repository=invocations,
                progress_sink=progress,
            )
            handler = agent_session_handler(
                resources=resources,
                sessions=sessions,
                model_handler=model,
                mcp_handler=_unused_mcp,
                harness=PiAgentSessionHarness((node, str(_PI_WORKER))),
                progress_sink=progress,
            )

            if kind == "exhausted":
                with pytest.raises(TaskExecutionFailure):
                    await handler(flow.tasks[0], context)
                failed = (await sessions.get_session("default", task_run.task_run_id, 1)).session
                assert failed.state is AgentSessionState.FAILED
                assert failed.final_result is None
                assert failed.counters.total_tokens == 10
                with pytest.raises(TaskExecutionFailure):
                    await handler(flow.tasks[0], context)
                assert len(provider.requests) == 2
                return

            completed = await handler(flow.tasks[0], context)

            assert isinstance(completed, TaskCompletion)
            assert completed.output["result"] == {"answer": "fixed"}
            assert len(provider.requests) == expected_calls
            detail = await sessions.get_session("default", task_run.task_run_id, 1)
            assert detail.session.state is AgentSessionState.SUCCEEDED
            assert detail.session.counters.repair_attempts == expected_calls - 1
            assert detail.session.counters.total_tokens == 5 * expected_calls
            assert detail.session.counters.cost_usd == Decimal("0.001") * expected_calls
            rejected = [event for event in detail.events if event.event_type == "output.rejected"]
            assert len(rejected) == expected_calls - 1
            if rejected:
                assert rejected[0].payload["repairScheduled"] is True

            progress_frames = [
                event.payload["frame"]
                for event in detail.events
                if event.event_type == "progress.frame"
            ]
            sources: dict[str, list[int]] = {}
            for frame in progress_frames:
                sources.setdefault(frame["sourceId"], []).append(frame["sourceSequence"])
            assert len(sources) >= expected_calls
            assert all(
                sequences == list(range(1, len(sequences) + 1)) for sequences in sources.values()
            )

            restarted = PostgresAgentSessionRepository(engine)
            replayed = await restarted.get_session("default", task_run.task_run_id, 1)
            assert replayed.session.state is AgentSessionState.SUCCEEDED
            assert replayed.session.counters.total_tokens == 5 * expected_calls
            assert [
                event.payload["frame"]
                for event in replayed.events
                if event.event_type == "progress.frame"
            ] == progress_frames

            # Ordinary messages must retain the original pin, including after restart.
            original = detail.session
            previous = original
            for turn in (2, 3):
                trigger = {
                    "ameshAgentSessionId": str(original.session_id),
                    "ameshAgentSessionAttemptBase": previous.attempt,
                    "ameshAgentSessionResumeFrom": {
                        "sessionId": str(previous.session_id),
                        "taskRunId": str(previous.task_run_id),
                        "attempt": previous.attempt,
                        "capabilityPinId": str(previous.capability_pin_id),
                        "envelopeDigest": previous.envelope_digest,
                    },
                }
                follow_execution = await executions.create_execution(
                    flow, tenant_id="default", inputs={}, trigger=trigger
                )
                follow_task = (
                    await executions.list_task_runs(
                        follow_execution.execution_id, tenant_id="default"
                    )
                )[0]
                follow_context = replace(
                    context,
                    execution_id=follow_execution.execution_id,
                    task_run_id=follow_task.task_run_id,
                    attempt_id=new_runtime_id(),
                    trigger=trigger,
                )
                handler = agent_session_handler(
                    resources=PostgresAgentResourceRepository(engine),
                    sessions=restarted,
                    model_handler=model,
                    mcp_handler=_unused_mcp,
                    harness=PiAgentSessionHarness((node, str(_PI_WORKER))),
                    progress_sink=progress,
                )
                follow_result = await handler(flow.tasks[0], follow_context)
                current = (
                    await restarted.get_session("default", follow_task.task_run_id, turn)
                ).session
                assert current.capability_pin_id == original.capability_pin_id
                assert current.envelope_digest == original.envelope_digest
                assert current.harness == original.harness
                assert (
                    tuple(provider.requests[-1].payload["messages"][:-1])
                    == previous.checkpoint.messages
                )
                assert follow_result.output["result"] == {"answer": "fixed"}
                assert await handler(flow.tasks[0], follow_context) == follow_result
                assert len(provider.requests) == expected_calls + turn - 1
                previous = current
        finally:
            await engine.dispose()

    asyncio.run(scenario())
