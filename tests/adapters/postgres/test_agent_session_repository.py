from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAgentProgressSink,
    PostgresAgentResourceRepository,
    PostgresAgentSessionRepository,
    PostgresExecutionRepository,
)
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.domain import (
    AgentContextPolicy,
    AgentDefinitionSpec,
    AgentEvaluationPolicy,
    AgentHardLimits,
    AgentHarnessPin,
    AgentMemoryPolicy,
    AgentPermissions,
    AgentProgressActivity,
    AgentProgressFrame,
    AgentProgressLimitExceeded,
    AgentProgressLimits,
    AgentProgressStatus,
    AgentResolutionRequest,
    AgentResourceRef,
    AgentSessionCheckpoint,
    AgentSessionCounters,
    AgentSessionEventCursor,
    AgentSessionPhase,
    AgentSessionStart,
    AgentSessionState,
    AgentSessionTransition,
    AgentStatusDetail,
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
from amesh.ports import AgentProgressContext, AgentProgressReceipt

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
            service_session_id = uuid4()
            execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                trigger={"ameshAgentSessionId": str(service_session_id)},
            )
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
                    harness=AgentHarnessPin(
                        adapter="pi-agent-core",
                        adapterVersion="0.1.0",
                        protocol="amesh-agent-session-v1",
                    ),
                )
            )
            progress_context = AgentProgressContext(
                tenantId="default",
                serviceSessionId=service_session_id,
                executionId=execution.execution_id,
                taskRunId=task_run.task_run_id,
                attemptSessionId=record.session_id,
                attempt=1,
            )
            progress_started = AgentProgressFrame(
                attemptSessionId=record.session_id,
                attempt=1,
                activity=AgentProgressActivity.THINKING,
                status=AgentProgressStatus.STARTED,
                activityId="thinking:1",
                segmentId=uuid4(),
                sourceId="provider",
                sourceSequence=1,
                occurredAt=datetime.now(UTC),
            )
            progress_receipt = await sessions.append_progress(
                progress_context,
                progress_started,
            )
            duplicate_progress = await sessions.append_progress(
                progress_context,
                progress_started,
            )
            assert progress_receipt.event_index == 1
            assert duplicate_progress == progress_receipt.model_copy(update={"duplicate": True})
            timestamp_duplicate = await sessions.append_progress(
                progress_context,
                progress_started.model_copy(
                    update={"occurred_at": datetime(2027, 1, 1, tzinfo=UTC)}
                ),
            )
            assert timestamp_duplicate == progress_receipt.model_copy(update={"duplicate": True})
            with pytest.raises(ValueError, match="reused with different content"):
                await sessions.append_progress(
                    progress_context,
                    progress_started.model_copy(update={"activity_id": "thinking:conflict"}),
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
            assert first.version == duplicate.version == 2
            with pytest.raises(ValueError, match="closed progress segment"):
                await sessions.append_progress(
                    progress_context,
                    progress_started.model_copy(
                        update={
                            "status": AgentProgressStatus.DELTA,
                            "source_sequence": 2,
                            "occurred_at": datetime.now(UTC),
                        }
                    ),
                )

            progress_resumed = progress_started.model_copy(
                update={
                    "status": AgentProgressStatus.STARTED,
                    "segment_id": uuid4(),
                    "source_sequence": 2,
                    "occurred_at": datetime.now(UTC),
                }
            )
            resumed_receipt = await sessions.append_progress(
                progress_context,
                progress_resumed,
            )
            assert resumed_receipt.event_index == 3

            first_page = await sessions.list_progress_events(
                "default",
                service_session_id,
                limit=2,
            )
            assert [item.frame.activity for item in first_page] == [
                AgentProgressActivity.THINKING,
                AgentProgressActivity.MODEL,
            ]
            assert first_page[1].frame.detail is not None
            second_page = await sessions.list_progress_events(
                "default",
                service_session_id,
                after=AgentSessionEventCursor.decode(first_page[-1].cursor),
                limit=2,
            )
            assert [item.frame.activity for item in second_page] == [AgentProgressActivity.THINKING]
            assert second_page[0].event_id == resumed_receipt.event_id
            wrong_session_cursor = AgentSessionEventCursor(
                serviceSessionId=uuid4(),
                attemptSessionId=record.session_id,
                attempt=1,
                eventIndex=2,
            )
            with pytest.raises(ValueError, match="different service session"):
                await sessions.list_progress_events(
                    "default",
                    service_session_id,
                    after=wrong_session_cursor,
                )
            forged_position = AgentSessionEventCursor(
                serviceSessionId=service_session_id,
                attemptSessionId=uuid4(),
                attempt=1,
                eventIndex=2,
            )
            with pytest.raises(ValueError, match="does not identify a canonical event"):
                await sessions.list_progress_events(
                    "default",
                    service_session_id,
                    after=forged_position,
                )

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
            assert projected.version == duplicate_projection.version == 4

            restarted = PostgresAgentSessionRepository(engine)
            detail = await restarted.get_session("default", task_run.task_run_id, 1)
            assert detail.session.checkpoint.next_turn == 1
            assert detail.session.checkpoint.messages == transcript
            assert detail.session.checkpoint.last_context_receipt == projection.receipt
            assert detail.session.harness == AgentHarnessPin(
                adapter="pi-agent-core",
                adapterVersion="0.1.0",
                protocol="amesh-agent-session-v1",
            )
            assert len(detail.events) == 4
            assert detail.events[0].event_key == progress_started.event_key
            assert detail.events[1].event_key == "session.started"
            assert detail.events[2].event_key == progress_resumed.event_key
            assert detail.events[3].event_key == "turn:3:context"
            assert detail.events[3].payload["receiptDigest"] == (projection.receipt.receipt_digest)
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

            first_attempt_events = await sessions.list_progress_events(
                "default",
                service_session_id,
            )
            assert first_attempt_events[-1].frame.activity is AgentProgressActivity.TERMINAL
            retry_record = await sessions.start_session(
                AgentSessionStart(
                    tenantId="default",
                    namespace="agents.session-test",
                    executionId=execution.execution_id,
                    taskRunId=task_run.task_run_id,
                    attempt=2,
                    capabilityPinId=pin.pin_id,
                    envelopeDigest=pin.envelope_digest,
                    harness=AgentHarnessPin(
                        adapter="pi-agent-core",
                        adapterVersion="0.1.0",
                        protocol="amesh-agent-session-v1",
                    ),
                )
            )
            retry_frame = AgentProgressFrame(
                attemptSessionId=retry_record.session_id,
                attempt=2,
                activity=AgentProgressActivity.THINKING,
                status=AgentProgressStatus.STARTED,
                activityId="thinking:retry",
                segmentId=uuid4(),
                sourceId="provider:retry",
                sourceSequence=1,
                occurredAt=datetime.now(UTC),
            )
            await sessions.append_progress(
                AgentProgressContext(
                    tenantId="default",
                    serviceSessionId=service_session_id,
                    executionId=execution.execution_id,
                    taskRunId=task_run.task_run_id,
                    attemptSessionId=retry_record.session_id,
                    attempt=2,
                ),
                retry_frame,
            )
            retry_page = await sessions.list_progress_events(
                "default",
                service_session_id,
                after=AgentSessionEventCursor.decode(first_attempt_events[-1].cursor),
            )
            assert len(retry_page) == 1
            assert retry_page[0].frame.attempt == 2
            assert retry_page[0].frame.attempt_session_id == retry_record.session_id

            follow_execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                trigger={
                    "ameshAgentSessionId": str(service_session_id),
                    "ameshAgentSessionTurn": 2,
                    "ameshAgentSessionAttemptBase": 2,
                },
            )
            follow_task_run = (
                await executions.list_task_runs(
                    follow_execution.execution_id,
                    tenant_id="default",
                )
            )[0]
            follow_record = await sessions.start_session(
                AgentSessionStart(
                    tenantId="default",
                    namespace="agents.session-test",
                    executionId=follow_execution.execution_id,
                    taskRunId=follow_task_run.task_run_id,
                    attempt=3,
                    capabilityPinId=pin.pin_id,
                    envelopeDigest=pin.envelope_digest,
                    harness=AgentHarnessPin(
                        adapter="pi-agent-core",
                        adapterVersion="0.1.0",
                        protocol="amesh-agent-session-v1",
                    ),
                )
            )
            image_metadata = {
                "artifactReference": "namespace-file://agents.session-test/images/later.png",
                "contentAddress": "sha256:" + "c" * 64,
                "checksumSha256": "c" * 64,
                "mediaType": "image/png",
                "sizeBytes": 128,
            }
            await sessions.transition(
                follow_record.session_id,
                tenant_id="default",
                transition=AgentSessionTransition(
                    eventKey="session.started",
                    eventType="session.started",
                    payload={"inputImages": [image_metadata]},
                    phase=AgentSessionPhase.MODEL,
                    checkpoint=completed.checkpoint,
                    counters=completed.counters,
                ),
            )
            follow_frame = AgentProgressFrame(
                attemptSessionId=follow_record.session_id,
                attempt=3,
                activity=AgentProgressActivity.THINKING,
                status=AgentProgressStatus.STARTED,
                activityId="thinking:follow-up",
                segmentId=uuid4(),
                sourceId="provider:follow-up",
                sourceSequence=1,
                occurredAt=datetime.now(UTC),
            )
            await sessions.append_progress(
                AgentProgressContext(
                    tenantId="default",
                    serviceSessionId=service_session_id,
                    executionId=follow_execution.execution_id,
                    taskRunId=follow_task_run.task_run_id,
                    attemptSessionId=follow_record.session_id,
                    attempt=3,
                ),
                follow_frame,
            )

            assert await sessions.get_execution_by_service_session_id(
                "default", service_session_id
            ) == follow_execution.execution_id
            logical_sessions = await sessions.list_service_sessions("default")
            logical_session = next(
                row for row in logical_sessions if row[0] == service_session_id
            )
            assert logical_session[1] == follow_execution.execution_id
            assert logical_session[3] is not None
            assert logical_session[3].session_id == follow_record.session_id
            follow_detail = await sessions.get_session(
                "default", follow_task_run.task_run_id, 3
            )
            assert follow_detail.events[0].payload["inputImages"] == [image_metadata]

            reconnect_page = await sessions.list_progress_events(
                "default",
                service_session_id,
                after=AgentSessionEventCursor.decode(retry_page[-1].cursor),
            )
            assert [item.frame.attempt for item in reconnect_page] == [3, 3]
            assert reconnect_page[-1].frame.activity is AgentProgressActivity.THINKING
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


def test_progress_limit_rejects_and_historical_truncation_remains_readable() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, migration_directory())
            resources = PostgresAgentResourceRepository(engine)
            sessions = PostgresAgentSessionRepository(engine)
            executions = PostgresExecutionRepository(engine)
            model_policy = await resources.save_resource(
                "default",
                ModelPolicySpec(
                    key="progress-overflow-model",
                    namespace="agents.progress-overflow",
                    title="Progress overflow model",
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
                    key="progress-overflow-agent",
                    namespace="agents.progress-overflow",
                    title="Progress overflow agent",
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
                        maxTotalTokens=1_000,
                        maxCostUsd=Decimal("1"),
                        maxDurationSeconds=60,
                        maxToolCalls=2,
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
                    "id": "progress-overflow",
                    "namespace": "agents.progress-overflow",
                    "tasks": [{"id": "agent", "type": "agent.session"}],
                }
            )
            service_session_id = uuid4()
            execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                trigger={"ameshAgentSessionId": str(service_session_id)},
            )
            task_run = (
                await executions.list_task_runs(execution.execution_id, tenant_id="default")
            )[0]
            pin = await resources.resolve_agent(
                "default",
                "agents.progress-overflow",
                "progress-overflow-agent",
                AgentResolutionRequest(
                    agentRevision=agent.revision,
                    subjectRef=f"agent-session:{task_run.task_run_id}:1",
                ),
                actor_id="test",
            )
            record = await sessions.start_session(
                AgentSessionStart(
                    tenantId="default",
                    namespace="agents.progress-overflow",
                    executionId=execution.execution_id,
                    taskRunId=task_run.task_run_id,
                    attempt=1,
                    capabilityPinId=pin.pin_id,
                    envelopeDigest=pin.envelope_digest,
                    harness=AgentHarnessPin(
                        adapter="pi-agent-core",
                        adapterVersion="0.1.0",
                        protocol="amesh-agent-session-v1",
                    ),
                )
            )
            context = AgentProgressContext(
                tenantId="default",
                serviceSessionId=service_session_id,
                executionId=execution.execution_id,
                taskRunId=task_run.task_run_id,
                attemptSessionId=record.session_id,
                attempt=1,
            )
            limits = AgentProgressLimits(maxFramesPerSecond=1)
            occurred_at = datetime.now(UTC)
            segment_id = uuid4()
            first_frame = AgentProgressFrame(
                attemptSessionId=record.session_id,
                attempt=1,
                activity=AgentProgressActivity.THINKING,
                status=AgentProgressStatus.STARTED,
                activityId="thinking:overflow",
                segmentId=segment_id,
                sourceId="provider",
                sourceSequence=1,
                occurredAt=occurred_at,
            )
            first_receipt = await sessions.append_progress(
                context,
                first_frame,
                limits=limits,
            )
            assert first_receipt.duplicate is False
            assert first_receipt.truncated is False

            duplicate_receipt = await sessions.append_progress(
                context,
                first_frame,
                limits=limits,
            )
            assert duplicate_receipt.duplicate is True
            assert duplicate_receipt.truncated is False
            assert duplicate_receipt.event_id == first_receipt.event_id
            with pytest.raises(ValueError, match="reused with different content"):
                await sessions.append_progress(
                    context,
                    first_frame.model_copy(update={"activity_id": "thinking:conflict"}),
                    limits=limits,
                )

            overflow_frame = first_frame.model_copy(
                update={
                    "status": AgentProgressStatus.DELTA,
                    "source_sequence": 2,
                }
            )
            with pytest.raises(AgentProgressLimitExceeded, match="maxFramesPerSecond"):
                await sessions.append_progress(context, overflow_frame, limits=limits)

            progress_events = await sessions.list_progress_events(
                "default",
                service_session_id,
            )
            assert [event.frame.status for event in progress_events] == [
                AgentProgressStatus.STARTED,
            ]

            historical_frame = AgentProgressFrame(
                attemptSessionId=record.session_id,
                attempt=1,
                activity=AgentProgressActivity.TERMINAL,
                status=AgentProgressStatus.TRUNCATED,
                activityId="progress.truncated",
                segmentId=segment_id,
                sourceId=f"amesh:progress-limit:{record.session_id}",
                sourceSequence=1,
                occurredAt=occurred_at,
            )
            with pytest.raises(ValueError, match="historical-only"):
                await sessions.append_progress(context, historical_frame, limits=limits)

            historical_event_id = uuid4()
            async with tenant_transaction(engine, "default") as (connection, tenant_uuid):
                await connection.execute(
                    text(
                        """
                        INSERT INTO agent_session_events (
                            event_id, tenant_id, execution_id, task_run_id, session_id,
                            event_index, event_key, event_type, payload
                        ) VALUES (
                            :event_id, :tenant_id, :execution_id, :task_run_id, :session_id,
                            2, :event_key, 'progress.frame', CAST(:payload AS jsonb)
                        )
                        """
                    ),
                    {
                        "event_id": historical_event_id,
                        "tenant_id": tenant_uuid,
                        "execution_id": execution.execution_id,
                        "task_run_id": task_run.task_run_id,
                        "session_id": record.session_id,
                        "event_key": historical_frame.event_key,
                        "payload": json.dumps(
                            {
                                "schemaVersion": "amesh.agent-progress/v1",
                                "frame": historical_frame.model_dump(
                                    mode="json",
                                    by_alias=True,
                                ),
                            }
                        ),
                    },
                )
                await connection.execute(
                    text(
                        """
                        UPDATE agent_sessions
                        SET version = 2
                        WHERE tenant_id = :tenant_id AND session_id = :session_id
                        """
                    ),
                    {"tenant_id": tenant_uuid, "session_id": record.session_id},
                )

            await engine.dispose()
            engine = create_async_engine(database.database_url)
            restarted = PostgresAgentSessionRepository(engine)
            historical_receipt = await restarted.append_progress(
                context,
                historical_frame,
                limits=limits,
            )
            assert historical_receipt.event_id == historical_event_id
            assert historical_receipt.duplicate is True
            assert historical_receipt.truncated is True

            restarted_duplicate = await restarted.append_progress(
                context,
                first_frame.model_copy(update={"occurred_at": datetime(2027, 1, 1, tzinfo=UTC)}),
                limits=limits,
            )
            assert restarted_duplicate.duplicate is True
            assert restarted_duplicate.truncated is False
            assert restarted_duplicate.event_id == first_receipt.event_id
            with pytest.raises(ValueError, match="reused with different content"):
                await restarted.append_progress(
                    context,
                    first_frame.model_copy(update={"activity_id": "thinking:conflict"}),
                    limits=limits,
                )

            checkpoint = AgentSessionCheckpoint(
                messages=(
                    {"role": "user", "content": "Find the answer."},
                    {"role": "assistant", "content": "The answer is 42."},
                ),
                nextTurn=2,
            )
            counters = AgentSessionCounters(
                turns=2,
                toolCalls=1,
                totalTokens=321,
                costUsd=Decimal("0.045"),
            )
            tool_evidence = {
                "toolCallId": "call-1",
                "toolName": "test.lookup",
                "result": {"value": 42},
            }
            await restarted.transition(
                record.session_id,
                tenant_id="default",
                transition=AgentSessionTransition(
                    eventKey="tool:call-1:result",
                    eventType="tool.result",
                    payload=tool_evidence,
                    phase=AgentSessionPhase.MODEL,
                    checkpoint=checkpoint,
                    counters=counters,
                ),
            )
            completed = await restarted.transition(
                record.session_id,
                tenant_id="default",
                transition=AgentSessionTransition(
                    eventKey="session.completed",
                    eventType="output.accepted",
                    payload={"schemaValid": True},
                    state=AgentSessionState.SUCCEEDED,
                    phase=AgentSessionPhase.COMPLETE,
                    checkpoint=checkpoint,
                    counters=counters,
                    finalResult={"answer": 42},
                ),
            )
            assert completed.state is AgentSessionState.SUCCEEDED

            verified = PostgresAgentSessionRepository(engine)
            detail = await verified.get_session("default", task_run.task_run_id, 1)
            assert detail.session.state is AgentSessionState.SUCCEEDED
            assert detail.session.final_result == {"answer": 42}
            assert detail.session.counters.total_tokens == 321
            assert detail.session.counters.cost_usd == Decimal("0.045")
            assert detail.session.counters.tool_calls == 1
            assert [event.event_type for event in detail.events] == [
                "progress.frame",
                "progress.frame",
                "tool.result",
                "output.accepted",
            ]
            assert detail.events[2].payload == tool_evidence
            truncated_events = [
                event
                for event in detail.events
                if event.event_type == "progress.frame"
                and event.payload["frame"]["status"] == AgentProgressStatus.TRUNCATED.value
            ]
            assert len(truncated_events) == 1
            assert truncated_events[0].event_id == historical_event_id

            async with engine.connect() as sql:
                evidence_rows = (
                    (
                        await sql.execute(
                            text(
                                "SELECT event_type FROM execution_evidence_events "
                                "WHERE execution_id = :execution_id "
                                "AND event_type IN ('agent.tool.result', 'agent.output.accepted') "
                                "ORDER BY cursor"
                            ),
                            {"execution_id": execution.execution_id},
                        )
                    )
                    .scalars()
                    .all()
                )
            assert evidence_rows == ["agent.tool.result", "agent.output.accepted"]
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


def test_progress_burst_is_complete_idempotent_and_restart_safe() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, migration_directory())
            resources = PostgresAgentResourceRepository(engine)
            sessions = PostgresAgentSessionRepository(engine)
            executions = PostgresExecutionRepository(engine)
            model_policy = await resources.save_resource(
                "default",
                ModelPolicySpec(
                    key="progress-burst-model",
                    namespace="agents.progress-burst",
                    title="Progress burst model",
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
                    key="progress-burst-agent",
                    namespace="agents.progress-burst",
                    title="Progress burst agent",
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
                        maxTotalTokens=1_000,
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
                    "id": "progress-burst",
                    "namespace": "agents.progress-burst",
                    "tasks": [{"id": "agent", "type": "agent.session"}],
                }
            )
            service_session_id = uuid4()
            execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                trigger={"ameshAgentSessionId": str(service_session_id)},
            )
            task_run = (
                await executions.list_task_runs(execution.execution_id, tenant_id="default")
            )[0]
            pin = await resources.resolve_agent(
                "default",
                "agents.progress-burst",
                "progress-burst-agent",
                AgentResolutionRequest(
                    agentRevision=agent.revision,
                    subjectRef=f"agent-session:{task_run.task_run_id}:1",
                ),
                actor_id="test",
            )
            record = await sessions.start_session(
                AgentSessionStart(
                    tenantId="default",
                    namespace="agents.progress-burst",
                    executionId=execution.execution_id,
                    taskRunId=task_run.task_run_id,
                    attempt=1,
                    capabilityPinId=pin.pin_id,
                    envelopeDigest=pin.envelope_digest,
                    harness=AgentHarnessPin(
                        adapter="pi-agent-core",
                        adapterVersion="0.1.0",
                        protocol="amesh-agent-session-v1",
                    ),
                )
            )
            context = AgentProgressContext(
                tenantId="default",
                serviceSessionId=service_session_id,
                executionId=execution.execution_id,
                taskRunId=task_run.task_run_id,
                attemptSessionId=record.session_id,
                attempt=1,
            )
            burst_count = 24
            occurred_at = datetime.now(UTC)
            segment_id = uuid4()
            frames = tuple(
                AgentProgressFrame(
                    attemptSessionId=record.session_id,
                    attempt=1,
                    activity=AgentProgressActivity.THINKING,
                    status=(
                        AgentProgressStatus.STARTED
                        if source_sequence == 1
                        else AgentProgressStatus.DELTA
                    ),
                    activityId=f"thinking:{source_sequence}",
                    segmentId=segment_id,
                    sourceId="provider",
                    sourceSequence=source_sequence,
                    occurredAt=occurred_at,
                )
                for source_sequence in range(1, burst_count + 1)
            )

            async def append_frames(
                repository: PostgresAgentSessionRepository,
                submitted_frames: tuple[AgentProgressFrame, ...],
            ) -> tuple[AgentProgressReceipt, ...]:
                appended: list[AgentProgressReceipt] = []
                for submitted_frame in submitted_frames:
                    appended.append(await repository.append_progress(context, submitted_frame))
                return tuple(appended)

            receipts = await append_frames(sessions, frames)
            assert len(receipts) == burst_count
            assert [receipt.event_index for receipt in receipts] == list(
                range(1, burst_count + 1)
            )
            assert all(not receipt.duplicate and not receipt.truncated for receipt in receipts)
            assert [
                AgentSessionEventCursor.decode(receipt.cursor).event_index
                for receipt in receipts
            ] == list(range(1, burst_count + 1))

            progress_events = await sessions.list_progress_events(
                "default",
                service_session_id,
                limit=100,
            )
            assert [event.event_index for event in progress_events] == list(
                range(1, burst_count + 1)
            )
            assert [event.frame for event in progress_events] == list(frames)
            assert all(
                event.frame.status is not AgentProgressStatus.TRUNCATED
                for event in progress_events
            )

            sink = PostgresAgentProgressSink(sessions)
            await sink.close_active_segment(context, occurred_at=datetime.now(UTC))
            await sink.close_active_segment(context, occurred_at=datetime.now(UTC))
            closed_events = await sessions.list_progress_events(
                "default",
                service_session_id,
                limit=100,
            )
            assert [event.frame for event in closed_events[:-1]] == list(frames)
            closure = closed_events[-1].frame
            assert closure.activity is AgentProgressActivity.TERMINAL
            assert closure.status is AgentProgressStatus.FAILED
            assert closure.activity_id == "progress.interrupted"
            assert closure.segment_id == segment_id
            assert closure.detail == AgentStatusDetail(
                code="progress.interrupted",
                label="Progress producer stopped",
            )

            detail = await sessions.get_session("default", task_run.task_run_id, 1)
            assert detail.session.version == burst_count + 1
            assert [event.event_index for event in detail.events] == list(
                range(1, burst_count + 2)
            )

            async with tenant_transaction(engine, "default") as (connection, tenant_uuid):
                evidence_indexes = (
                    await connection.execute(
                        text(
                            """
                            SELECT payload ->> 'eventIndex'
                            FROM execution_evidence_events
                            WHERE tenant_id = :tenant_id
                              AND execution_id = :execution_id
                              AND event_type = 'agent.progress.frame'
                              AND payload ->> 'sessionId' = :session_id
                            ORDER BY cursor
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "execution_id": execution.execution_id,
                            "session_id": str(record.session_id),
                        },
                    )
                ).scalars().all()
            assert [int(index) for index in evidence_indexes] == list(range(1, burst_count + 2))

            retry_receipts = await append_frames(sessions, frames)
            assert [receipt.event_id for receipt in retry_receipts] == [
                receipt.event_id for receipt in receipts
            ]
            assert all(receipt.duplicate and not receipt.truncated for receipt in retry_receipts)

            conflicting_frame = frames[0].model_copy(update={"activity_id": "thinking:conflict"})
            with pytest.raises(ValueError, match="reused with different content"):
                await sessions.append_progress(context, conflicting_frame)
            unchanged = await sessions.get_session("default", task_run.task_run_id, 1)
            assert unchanged.session.version == burst_count + 1
            assert [event.event_type for event in unchanged.events] == [
                "progress.frame"
            ] * (burst_count + 1)

            await engine.dispose()
            engine = create_async_engine(database.database_url)
            restarted = PostgresAgentSessionRepository(engine)
            restarted_retry = await append_frames(restarted, frames)
            assert [receipt.event_id for receipt in restarted_retry] == [
                receipt.event_id for receipt in receipts
            ]
            assert all(receipt.duplicate and not receipt.truncated for receipt in restarted_retry)
            restarted_sink = PostgresAgentProgressSink(restarted)
            await restarted_sink.close_active_segment(context, occurred_at=datetime.now(UTC))
            restarted_detail = await restarted.get_session("default", task_run.task_run_id, 1)
            assert restarted_detail.session.version == burst_count + 1
            restarted_progress = await restarted.list_progress_events(
                "default",
                service_session_id,
                limit=100,
            )
            assert [event.frame for event in restarted_progress] == [
                event.frame for event in closed_events
            ]
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


def test_service_session_list_filters_owner_before_limit() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        sessions = PostgresAgentSessionRepository(engine)
        executions = PostgresExecutionRepository(engine)
        owner_id = str(uuid4())
        foreign_owner_id = str(uuid4())
        owner_service_session_id = uuid4()
        try:
            await apply_migrations(database.database_url, migration_directory())
            flow = FlowDefinition.model_validate(
                {
                    "id": "service-session-list",
                    "namespace": "agents.session-list",
                    "tasks": [{"id": "agent", "type": "agent.session"}],
                }
            )
            owner_execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                trigger={
                    "ameshAgentSessionId": str(owner_service_session_id),
                    "ameshAgentRef": "agents.session-list/helper@1",
                    "ameshActorId": owner_id,
                },
                actor_id=owner_id,
            )

            async with tenant_transaction(engine, "default") as (connection, tenant_uuid):
                owner_row = (
                    (
                        await connection.execute(
                            text(
                                """
                            SELECT flow_id, flow_revision_id, namespace_name, flow_key, created_at
                            FROM executions
                            WHERE tenant_id = :tenant_id AND id = :execution_id
                            """
                            ),
                            {
                                "tenant_id": tenant_uuid,
                                "execution_id": owner_execution.execution_id,
                            },
                        )
                    )
                    .mappings()
                    .one()
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO executions (
                            id,
                            tenant_id,
                            flow_id,
                            flow_revision_id,
                            namespace_name,
                            flow_key,
                            state,
                            version,
                            inputs,
                            trigger_context,
                            labels,
                            created_at,
                            updated_at
                        )
                        SELECT
                            gen_random_uuid(),
                            :tenant_id,
                            :flow_id,
                            :flow_revision_id,
                            :namespace_name,
                            :flow_key,
                            'QUEUED',
                            2,
                            '{}'::jsonb,
                            jsonb_build_object(
                                'ameshAgentSessionId', gen_random_uuid()::text,
                                'ameshAgentRef', 'agents.session-list/helper@1',
                                'ameshActorId', CAST(:foreign_owner_id AS text)
                            ),
                            '{}'::jsonb,
                            CAST(:created_at AS timestamptz)
                                + series.ordinal * interval '1 second',
                            CAST(:created_at AS timestamptz)
                                + series.ordinal * interval '1 second'
                        FROM generate_series(1, 101) AS series(ordinal)
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "flow_id": owner_row["flow_id"],
                        "flow_revision_id": owner_row["flow_revision_id"],
                        "namespace_name": owner_row["namespace_name"],
                        "flow_key": owner_row["flow_key"],
                        "foreign_owner_id": foreign_owner_id,
                        "created_at": owner_row["created_at"],
                    },
                )

            owner_rows = await sessions.list_service_sessions(
                "default",
                limit=100,
                owner_id=owner_id,
            )
            assert [row[0] for row in owner_rows] == [owner_service_session_id]

            privileged_rows = await sessions.list_service_sessions("default", limit=100)
            assert len(privileged_rows) == 100
            assert owner_service_session_id not in {row[0] for row in privileged_rows}
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
