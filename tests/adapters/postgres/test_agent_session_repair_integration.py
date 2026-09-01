from __future__ import annotations

import asyncio
import json
import os
import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

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
from amesh.executor import TaskCompletion, TaskExecutionContext
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)
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
    def __init__(self) -> None:
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
        if len(self.requests) > 1:
            action["rationale"] = "Repaired with a schema-valid public rationale."
        return ModelProviderResponse(
            payload={
                "choices": [{"message": {"content": json.dumps(action)}}],
                "usage": {
                    "prompt_tokens": 4,
                    "completion_tokens": 1,
                    "total_tokens": 5,
                    "cost": 0.001,
                },
            }
        )


async def _unused_mcp(*args: Any, **kwargs: Any) -> TaskCompletion:
    del args, kwargs
    raise AssertionError("the repair-only session must not dispatch a tool")


def test_real_pi_repair_has_unique_durable_postgres_progress() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        node = shutil.which("node")
        if node is None or not _PI_PACKAGE.exists():
            pytest.fail("Pi/PostgreSQL repair qualification requires the installed Pi harness")

        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        resources = PostgresAgentResourceRepository(engine)
        sessions = PostgresAgentSessionRepository(engine)
        invocations = PostgresAgentPrimitiveRepository(engine)
        executions = PostgresExecutionRepository(engine)
        provider = _InvalidThenValidProvider()
        try:
            await apply_migrations(database.database_url, migration_directory())
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
                        maxTurns=2,
                        maxLoopIterations=1,
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

            completed = await handler(flow.tasks[0], context)

            assert isinstance(completed, TaskCompletion)
            assert completed.output["result"] == {"answer": "fixed"}
            assert len(provider.requests) == 2
            detail = await sessions.get_session("default", task_run.task_run_id, 1)
            assert detail.session.state is AgentSessionState.SUCCEEDED
            assert detail.session.counters.repair_attempts == 1
            assert detail.session.counters.total_tokens == 10
            assert detail.session.counters.cost_usd == Decimal("0.002")
            rejected = [event for event in detail.events if event.event_type == "output.rejected"]
            assert len(rejected) == 1
            assert rejected[0].payload["repairScheduled"] is True

            progress_frames = [
                event.payload["frame"]
                for event in detail.events
                if event.event_type == "progress.frame"
            ]
            sources: dict[str, list[int]] = {}
            for frame in progress_frames:
                sources.setdefault(frame["sourceId"], []).append(frame["sourceSequence"])
            assert len(sources) >= 2
            assert all(
                sequences == list(range(1, len(sequences) + 1)) for sequences in sources.values()
            )

            restarted = PostgresAgentSessionRepository(engine)
            replayed = await restarted.get_session("default", task_run.task_run_id, 1)
            assert replayed.session.state is AgentSessionState.SUCCEEDED
            assert replayed.session.counters.total_tokens == 10
            assert [
                event.payload["frame"]
                for event in replayed.events
                if event.event_type == "progress.frame"
            ] == progress_frames
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
