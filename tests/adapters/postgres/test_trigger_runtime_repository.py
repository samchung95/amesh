from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresExecutionRepository,
    PostgresTriggerRuntimeRepository,
)
from amesh.dsl import FlowDefinition
from amesh.executor import InProcessExecutor, TaskExecutionContext
from amesh.model_continuations import TriggerPayloadProtector
from amesh.ports import TriggerOccurrenceState
from amesh.worker import process_trigger_occurrences_once

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def _webhook_flow(revision: int = 1, *, paused: bool = False) -> FlowDefinition:
    return FlowDefinition.model_validate(
        {
            "id": "receiver",
            "namespace": "tests.triggers",
            "revision": revision,
            "tasks": [{"id": "result", "type": "test.echo"}],
            "triggers": [
                {
                    "id": "incoming",
                    "type": "core.webhook",
                    "paused": paused,
                    "maxPending": 1,
                    "maxAttempts": 2,
                    "retryDelay": "PT0.01S",
                }
            ],
        }
    )


def test_trigger_revision_occurrence_retry_pause_replay_and_checkpoint_are_durable(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            executions = PostgresExecutionRepository(engine)
            runtime = PostgresTriggerRuntimeRepository(engine)
            first_flow = _webhook_flow()
            await executions.apply_flow(first_flow, tenant_id="default")

            states = await runtime.list_runtime_states(tenant_id="default", active=True)
            assert [(item.flow_revision, item.trigger_id, item.active) for item in states] == [
                (1, "incoming", True)
            ]
            accepted = await runtime.accept_occurrence(
                tenant_id="default",
                namespace=first_flow.namespace,
                flow_id=first_flow.id,
                flow_revision=first_flow.revision,
                trigger_id="incoming",
                occurrence_key="event-1",
                payload={"message": "one"},
                metadata={"observedAt": datetime.now(UTC).isoformat()},
                max_pending=1,
                max_attempts=2,
                retry_delay=timedelta(milliseconds=10),
            )
            assert accepted.accepted and not accepted.duplicate
            duplicate = await runtime.accept_occurrence(
                tenant_id="default",
                namespace=first_flow.namespace,
                flow_id=first_flow.id,
                flow_revision=first_flow.revision,
                trigger_id="incoming",
                occurrence_key="event-1",
                payload={"message": "one"},
                metadata={},
                max_pending=1,
                max_attempts=2,
                retry_delay=timedelta(milliseconds=10),
            )
            assert duplicate.duplicate
            assert duplicate.occurrence.occurrence_id == accepted.occurrence.occurrence_id

            owner = uuid4()
            first_claim = await runtime.claim_occurrence(
                accepted.occurrence.occurrence_id,
                tenant_id="default",
                owner_id=owner,
                lease_duration=timedelta(seconds=5),
            )
            retrying = await runtime.fail_occurrence(
                first_claim.occurrence_id,
                tenant_id="default",
                owner_id=owner,
                fencing_token=first_claim.fencing_token,
                error="connector unavailable",
                retry_delay=timedelta(milliseconds=10),
            )
            assert retrying.state is TriggerOccurrenceState.RETRY_WAIT
            await asyncio.sleep(0.02)
            second_claim = await runtime.claim_occurrence(
                retrying.occurrence_id,
                tenant_id="default",
                owner_id=owner,
                lease_duration=timedelta(seconds=5),
            )
            dead_letter = await runtime.fail_occurrence(
                second_claim.occurrence_id,
                tenant_id="default",
                owner_id=owner,
                fencing_token=second_claim.fencing_token,
                error="connector still unavailable",
                retry_delay=timedelta(milliseconds=10),
            )
            assert dead_letter.state is TriggerOccurrenceState.DEAD_LETTERED

            replayed = await runtime.replay_occurrence(
                dead_letter.occurrence_id,
                tenant_id="default",
                actor_id="test:operator",
                reason="source recovered",
            )
            assert replayed.replay_of == dead_letter.occurrence_id
            assert replayed.state is TriggerOccurrenceState.ACCEPTED

            paused = await runtime.set_paused(
                tenant_id="default",
                namespace=first_flow.namespace,
                flow_id=first_flow.id,
                trigger_id="incoming",
                paused=True,
                actor_id="test:operator",
                reason="maintenance",
            )
            assert paused.paused
            deferred = await runtime.accept_occurrence(
                tenant_id="default",
                namespace=first_flow.namespace,
                flow_id=first_flow.id,
                flow_revision=first_flow.revision,
                trigger_id="incoming",
                occurrence_key="event-2",
                payload={},
                metadata={},
                max_pending=10,
                max_attempts=2,
                retry_delay=timedelta(milliseconds=10),
            )
            assert deferred.occurrence.state is TriggerOccurrenceState.DEFERRED
            resumed = await runtime.set_paused(
                tenant_id="default",
                namespace=first_flow.namespace,
                flow_id=first_flow.id,
                trigger_id="incoming",
                paused=False,
                actor_id="test:operator",
                reason="maintenance complete",
            )
            assert not resumed.paused
            assert (
                await runtime.get_occurrence(deferred.occurrence.occurrence_id, tenant_id="default")
            ).state is TriggerOccurrenceState.ACCEPTED

            checkpointed = await runtime.update_checkpoint(
                tenant_id="default",
                trigger_definition_id=states[0].trigger_definition_id,
                checkpoint={"offset": 42},
                cursor="partition-0:42",
                evaluated_at=datetime.now(UTC),
                next_evaluation_at=datetime.now(UTC) + timedelta(minutes=1),
                decision="poll batch committed",
            )
            assert checkpointed.checkpoint == {"offset": 42}
            assert checkpointed.cursor == "partition-0:42"

            await executions.apply_flow(_webhook_flow(2), tenant_id="default")
            all_states = await runtime.list_runtime_states(tenant_id="default", active=None)
            assert [(item.flow_revision, item.active) for item in all_states] == [
                (2, True),
                (1, False),
            ]
            async with engine.connect() as connection:
                assert (
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM audit_events "
                            "WHERE action IN ('trigger.pause', 'trigger.resume', "
                            "'trigger.occurrence.replay')"
                        )
                    )
                    == 3
                )
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_sensitive_trigger_payload_retries_from_protected_storage(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            key = Fernet.generate_key().decode("ascii")
            runtime = PostgresTriggerRuntimeRepository(
                engine,
                TriggerPayloadProtector(primary_key_id="current", keys={"current": key}),
            )
            executions = PostgresExecutionRepository(engine)
            flow = FlowDefinition.model_validate(
                {
                    "id": "protected-receiver",
                    "namespace": "tests.triggers",
                    "inputs": [{"id": "token", "type": "STRING", "sensitive": True}],
                    "tasks": [{"id": "result", "type": "test.echo"}],
                    "triggers": [{"id": "incoming", "type": "core.webhook"}],
                }
            )
            await executions.apply_flow(flow, tenant_id="default")
            secret = "sensitive-webhook-value"
            accepted = await runtime.accept_occurrence(
                tenant_id="default",
                namespace=flow.namespace,
                flow_id=flow.id,
                flow_revision=flow.revision,
                trigger_id="incoming",
                occurrence_key="webhook:protected",
                payload={"token": "[REDACTED]"},
                recoverable_payload={"token": secret},
                metadata={"source": "webhook"},
                max_pending=3,
                max_attempts=2,
                retry_delay=timedelta(milliseconds=10),
            )
            assert accepted.occurrence.payload == {"token": "[REDACTED]"}
            async with engine.connect() as connection:
                row = (
                    await connection.execute(
                        text(
                            "SELECT payload::text, protected_payload_ciphertext "
                            "FROM trigger_occurrences WHERE occurrence_id = :id"
                        ),
                        {"id": accepted.occurrence.occurrence_id},
                    )
                ).one()
            assert secret not in row[0]
            assert row[1] is not None and secret.encode() not in bytes(row[1])
            assert await runtime.get_recoverable_payload(
                accepted.occurrence.occurrence_id,
                tenant_id="default",
            ) == {"token": secret}

            processed = await process_trigger_occurrences_once(
                executions,
                runtime,
                tenant_ids=["default"],
                worker_id=uuid4(),
            )
            assert processed == 1
            launched = await runtime.get_occurrence(
                accepted.occurrence.occurrence_id,
                tenant_id="default",
            )
            assert launched.execution_id is not None
            execution = await executions.get_execution(
                launched.execution_id,
                tenant_id="default",
            )
            assert execution.inputs["token"] == secret

            replay = await runtime.replay_occurrence(
                accepted.occurrence.occurrence_id,
                tenant_id="default",
                actor_id="reviewer",
                reason="verify protected replay",
            )
            assert replay.payload == {"token": "[REDACTED]"}
            assert (
                await process_trigger_occurrences_once(
                    executions,
                    runtime,
                    tenant_ids=["default"],
                    worker_id=uuid4(),
                )
                == 1
            )
            replayed = await runtime.get_occurrence(
                replay.occurrence_id,
                tenant_id="default",
            )
            assert replayed.execution_id is not None
            replayed_execution = await executions.get_execution(
                replayed.execution_id,
                tenant_id="default",
            )
            assert replayed_execution.inputs["token"] == secret
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_flow_completion_is_transactionally_routed_without_source_polling(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            executions = PostgresExecutionRepository(engine)
            runtime = PostgresTriggerRuntimeRepository(engine)
            source = FlowDefinition.model_validate(
                {
                    "id": "source",
                    "namespace": "tests.flow-trigger",
                    "tasks": [{"id": "emit", "type": "test.echo"}],
                }
            )
            target = FlowDefinition.model_validate(
                {
                    "id": "target",
                    "namespace": "tests.flow-trigger",
                    "tasks": [{"id": "receive", "type": "test.echo"}],
                    "triggers": [
                        {
                            "id": "after-source",
                            "type": "core.flow",
                            "flowId": "source",
                            "states": ["SUCCESS"],
                        }
                    ],
                }
            )
            await executions.apply_flow(source, tenant_id="default")
            await executions.apply_flow(target, tenant_id="default")
            source_execution = await executions.create_execution(
                source,
                tenant_id="default",
                inputs={"message": "complete"},
            )

            async def echo(_task: object, context: TaskExecutionContext) -> dict[str, str]:
                del context
                return {"message": "complete"}

            await InProcessExecutor(
                executions,
                handlers={"test.echo": echo},
            ).run_to_completion(source, source_execution.execution_id, tenant_id="default")

            occurrences = await runtime.list_occurrences(
                tenant_id="default",
                flow_id="target",
            )
            assert len(occurrences) == 1
            assert occurrences[0].state is TriggerOccurrenceState.ACCEPTED
            assert occurrences[0].payload["sourceExecutionId"] == str(source_execution.execution_id)

            processed = await process_trigger_occurrences_once(
                executions,
                runtime,
                tenant_ids=["default"],
                worker_id=uuid4(),
            )
            assert processed == 1
            launched = await runtime.get_occurrence(
                occurrences[0].occurrence_id,
                tenant_id="default",
            )
            assert launched.state is TriggerOccurrenceState.SUCCEEDED
            assert launched.execution_id is not None
            downstream = await executions.get_execution(
                launched.execution_id,
                tenant_id="default",
            )
            assert downstream.flow_id == "target"
            assert downstream.trigger["source"] == "event"
            assert downstream.trigger["sourceExecutionId"] == str(source_execution.execution_id)
        finally:
            await engine.dispose()

    asyncio.run(scenario())
