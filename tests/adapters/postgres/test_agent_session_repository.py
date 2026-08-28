from __future__ import annotations

import asyncio
import os
from decimal import Decimal

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAgentResourceRepository,
    PostgresAgentSessionRepository,
    PostgresExecutionRepository,
)
from amesh.domain import (
    AgentContextPolicy,
    AgentDefinitionSpec,
    AgentEvaluationPolicy,
    AgentHardLimits,
    AgentMemoryPolicy,
    AgentPermissions,
    AgentResolutionRequest,
    AgentResourceRef,
    AgentSessionCheckpoint,
    AgentSessionCounters,
    AgentSessionPhase,
    AgentSessionStart,
    AgentSessionState,
    AgentSessionTransition,
    ModelPolicySpec,
    ModelProviderSpec,
    ModelRoute,
    project_agent_context,
)
from amesh.dsl import FlowDefinition
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_session_journal_is_idempotent_recoverable_and_projected_to_execution_evidence() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        resources = PostgresAgentResourceRepository(engine)
        sessions = PostgresAgentSessionRepository(engine)
        executions = PostgresExecutionRepository(engine)
        try:
            await apply_migrations(database.database_url, migration_directory())
            model_policy = await resources.save_resource(
                "default",
                ModelPolicySpec(
                    key="luna",
                    namespace="agents.session-test",
                    title="Luna",
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
                    namespace="agents.session-test",
                    title="Helper",
                    instructions="Return a result.",
                    inputSchema={"type": "object"},
                    outputSchema={"type": "object"},
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
                    "id": "session-journal",
                    "namespace": "agents.session-test",
                    "tasks": [{"id": "agent", "type": "agent.session"}],
                }
            )
            execution = await executions.create_execution(flow, tenant_id="default", inputs={})
            task_run = (
                await executions.list_task_runs(execution.execution_id, tenant_id="default")
            )[0]
            pin = await resources.resolve_agent(
                "default",
                "agents.session-test",
                "helper",
                AgentResolutionRequest(
                    agentRevision=agent.revision,
                    subjectRef=f"agent-session:{task_run.task_run_id}:1",
                ),
                actor_id="test",
            )
            record = await sessions.start_session(
                AgentSessionStart(
                    tenantId="default",
                    namespace="agents.session-test",
                    executionId=execution.execution_id,
                    taskRunId=task_run.task_run_id,
                    attempt=1,
                    capabilityPinId=pin.pin_id,
                    envelopeDigest=pin.envelope_digest,
                )
            )
            transcript = (
                {"role": "system", "content": "Pinned"},
                {"role": "user", "content": "Input"},
                {"role": "assistant", "content": "Tool one"},
                {"role": "user", "content": "Result one"},
                {"role": "assistant", "content": "Tool two"},
                {"role": "user", "content": "Result two"},
            )
            transition = AgentSessionTransition(
                eventKey="session.started",
                eventType="session.started",
                payload={"envelopeDigest": pin.envelope_digest},
                phase=AgentSessionPhase.MODEL,
                checkpoint=AgentSessionCheckpoint(messages=transcript, nextTurn=1),
                counters=AgentSessionCounters(),
            )
            first = await sessions.transition(
                record.session_id,
                tenant_id="default",
                transition=transition,
            )
            duplicate = await sessions.transition(
                record.session_id,
                tenant_id="default",
                transition=transition,
            )
            assert first.version == duplicate.version == 1

            projection = project_agent_context(
                transcript,
                AgentContextPolicy(
                    maxMessages=5,
                    maxBytes=10_000,
                    maxEstimatedTokens=10_000,
                ),
                turn=3,
            )
            context_transition = AgentSessionTransition(
                eventKey="turn:3:context",
                eventType="context.compacted",
                payload=projection.receipt.model_dump(mode="json", by_alias=True),
                phase=AgentSessionPhase.MODEL,
                checkpoint=first.checkpoint.model_copy(
                    update={"last_context_receipt": projection.receipt}
                ),
                counters=first.counters,
            )
            projected = await sessions.transition(
                record.session_id,
                tenant_id="default",
                transition=context_transition,
            )
            duplicate_projection = await sessions.transition(
                record.session_id,
                tenant_id="default",
                transition=context_transition,
            )
            assert projected.version == duplicate_projection.version == 2

            restarted = PostgresAgentSessionRepository(engine)
            detail = await restarted.get_session("default", task_run.task_run_id, 1)
            assert detail.session.checkpoint.next_turn == 1
            assert detail.session.checkpoint.messages == transcript
            assert detail.session.checkpoint.last_context_receipt == projection.receipt
            assert len(detail.events) == 2
            assert detail.events[0].event_key == "session.started"
            assert detail.events[1].event_key == "turn:3:context"
            assert detail.events[1].payload["receiptDigest"] == (projection.receipt.receipt_digest)
            assert (
                await restarted.list_execution_sessions("amesh-system", execution.execution_id)
                == ()
            )
            async with engine.connect() as sql:
                evidence_count = await sql.scalar(
                    text(
                        "SELECT count(*) FROM execution_evidence_events "
                        "WHERE execution_id = :execution_id "
                        "AND event_type = 'agent.session.started'"
                    ),
                    {"execution_id": execution.execution_id},
                )
            assert evidence_count == 1
            async with engine.connect() as sql:
                compaction_evidence_count = await sql.scalar(
                    text(
                        "SELECT count(*) FROM execution_evidence_events "
                        "WHERE execution_id = :execution_id "
                        "AND event_type = 'agent.context.compacted'"
                    ),
                    {"execution_id": execution.execution_id},
                )
            assert compaction_evidence_count == 1

            completed = await sessions.transition(
                record.session_id,
                tenant_id="default",
                transition=AgentSessionTransition(
                    eventKey="session.completed",
                    eventType="output.accepted",
                    payload={"schemaValid": True},
                    state=AgentSessionState.SUCCEEDED,
                    phase=AgentSessionPhase.COMPLETE,
                    checkpoint=projected.checkpoint,
                    counters=projected.counters,
                    finalResult={"answer": "ok"},
                ),
            )
            assert completed.completed_at is not None
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
