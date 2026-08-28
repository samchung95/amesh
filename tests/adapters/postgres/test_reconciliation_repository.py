from __future__ import annotations

import asyncio
import os
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresDurableTransport,
    PostgresExecutionRepository,
    PostgresReconciliationRepository,
)
from amesh.domain import (
    ReconciliationDisposition,
    ReconciliationInvariant,
    ReconciliationRequest,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.dsl.models import TriggerDefinition
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
)
from amesh.ports import DurableEnvelope

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def _envelope(*, worker_id: str) -> DurableEnvelope:
    message_id = uuid4()
    return DurableEnvelope(
        message_id=message_id,
        message_type="DispatchTaskRun",
        schema_version=1,
        tenant_id="default",
        partition_key=f"execution:{message_id}",
        correlation_id=uuid4(),
        produced_at="2026-08-22T00:00:00Z",
        trace_context={},
        payload={"workerId": worker_id},
    )


def test_reconciliation_repairs_safe_state_and_quarantines_ambiguity() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, MIGRATIONS)
            execution_repository = PostgresExecutionRepository(engine)
            reconciliation = PostgresReconciliationRepository(engine)
            flow = FlowDefinition(
                id="reconcile_execution",
                namespace=f"tests.reconciliation.{uuid4().hex}",
                triggers=[
                    TriggerDefinition.model_validate(
                        {
                            "id": "interval",
                            "type": "core.interval",
                            "interval": "PT5M",
                        }
                    )
                ],
                tasks=[TaskDefinition(id="one", type="core.return", value="ok")],
            )
            execution = await execution_repository.create_execution(
                flow,
                tenant_id="default",
                inputs={},
            )
            async with engine.begin() as connection:
                event_id = await connection.scalar(
                    text(
                        "SELECT event_id FROM execution_events "
                        "WHERE execution_id = :execution_id ORDER BY sequence LIMIT 1"
                    ),
                    {"execution_id": execution.execution_id},
                )
                task_event_id = await connection.scalar(
                    text(
                        "SELECT event_id FROM task_run_events "
                        "WHERE execution_id = :execution_id ORDER BY sequence LIMIT 1"
                    ),
                    {"execution_id": execution.execution_id},
                )
                await connection.execute(
                    text(
                        "DELETE FROM messages_outbox "
                        "WHERE message_id IN (:event_id, :task_event_id)"
                    ),
                    {"event_id": event_id, "task_event_id": task_event_id},
                )
                await connection.execute(
                    text(
                        "UPDATE task_run_events SET event_type = 'TaskRunStarted', "
                        "payload = '{\"dispatch\": true}'::jsonb "
                        "WHERE event_id = :task_event_id"
                    ),
                    {"task_event_id": task_event_id},
                )
                await connection.execute(
                    text(
                        "UPDATE task_runs SET state = 'RUNNING', current_attempt = 1, "
                        "updated_at = clock_timestamp() - interval '10 minutes' "
                        "WHERE execution_id = :execution_id"
                    ),
                    {"execution_id": execution.execution_id},
                )
                await connection.execute(
                    text(
                        "UPDATE executions SET updated_at = "
                        "clock_timestamp() - interval '10 minutes' WHERE id = :execution_id"
                    ),
                    {"execution_id": execution.execution_id},
                )

            dry_run = await reconciliation.run(
                ReconciliationRequest.model_validate(
                    {
                        "mode": "DRY_RUN",
                        "executionId": execution.execution_id,
                        "staleAfterSeconds": 30,
                        "idempotencyKey": "execution-dry-run",
                        "reason": "inspect execution invariants",
                    }
                ),
                tenant_id="default",
                actor_id="test:reconciler",
            )
            assert {finding.invariant for finding in dry_run.findings} == {
                ReconciliationInvariant.ORPHAN_TASK_RUN,
                ReconciliationInvariant.STUCK_EXECUTION,
                ReconciliationInvariant.MISSING_DISPATCH,
                ReconciliationInvariant.UNPROJECTED_EVENT,
            }
            assert all(
                finding.disposition is ReconciliationDisposition.DETECTED
                for finding in dry_run.findings
            )
            async with engine.connect() as connection:
                assert (
                    await connection.scalar(
                        text("SELECT count(*) FROM messages_outbox WHERE message_id = :event_id"),
                        {"event_id": event_id},
                    )
                    == 0
                )

            applied_request = ReconciliationRequest.model_validate(
                {
                    "mode": "APPLY",
                    "executionId": execution.execution_id,
                    "staleAfterSeconds": 30,
                    "maxRepairs": 10,
                    "idempotencyKey": "execution-apply",
                    "reason": "repair safe state and quarantine ambiguous state",
                }
            )
            applied = await reconciliation.run(
                applied_request,
                tenant_id="default",
                actor_id="test:reconciler",
            )
            dispositions = {finding.invariant: finding.disposition for finding in applied.findings}
            assert dispositions[ReconciliationInvariant.UNPROJECTED_EVENT] is (
                ReconciliationDisposition.REPAIRED
            )
            assert dispositions[ReconciliationInvariant.MISSING_DISPATCH] is (
                ReconciliationDisposition.REPAIRED
            )
            assert dispositions[ReconciliationInvariant.ORPHAN_TASK_RUN] is (
                ReconciliationDisposition.QUARANTINED
            )
            assert dispositions[ReconciliationInvariant.STUCK_EXECUTION] is (
                ReconciliationDisposition.QUARANTINED
            )
            assert applied.repairs_applied == 2
            assert applied.unresolved_count == 2
            repeated = await reconciliation.run(
                applied_request,
                tenant_id="default",
                actor_id="test:reconciler",
            )
            assert repeated.run_id == applied.run_id

            converged = await reconciliation.run(
                ReconciliationRequest.model_validate(
                    {
                        "executionId": execution.execution_id,
                        "staleAfterSeconds": 30,
                        "idempotencyKey": "execution-convergence",
                        "reason": "confirm safe projection repair converged",
                    }
                ),
                tenant_id="default",
                actor_id="test:reconciler",
            )
            assert ReconciliationInvariant.UNPROJECTED_EVENT not in {
                finding.invariant for finding in converged.findings
            }
            assert ReconciliationInvariant.MISSING_DISPATCH not in {
                finding.invariant for finding in converged.findings
            }

            async with engine.connect() as connection:
                trigger_id = await connection.scalar(
                    text(
                        "SELECT triggers.id FROM trigger_definitions AS triggers "
                        "JOIN flow_revisions AS revisions "
                        "ON revisions.id = triggers.flow_revision_id "
                        "JOIN flows ON flows.id = revisions.flow_id "
                        "WHERE flows.flow_key = :flow_key"
                    ),
                    {"flow_key": flow.id},
                )
            schedule = await reconciliation.run(
                ReconciliationRequest.model_validate(
                    {
                        "mode": "APPLY",
                        "triggerDefinitionId": trigger_id,
                        "maxRepairs": 1,
                        "idempotencyKey": "schedule-apply",
                        "reason": "rebuild schedule projection",
                    }
                ),
                tenant_id="default",
                actor_id="test:reconciler",
            )
            assert len(schedule.findings) == 1
            assert schedule.findings[0].invariant is (
                ReconciliationInvariant.MISSING_SCHEDULE_PROJECTION
            )
            assert schedule.findings[0].disposition is ReconciliationDisposition.REPAIRED
            assert await reconciliation.get(schedule.run_id, tenant_id="default") == schedule
            listed = await reconciliation.list_runs(tenant_id="default")
            assert next(item.run_id for item in listed) == schedule.run_id
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


def test_reconciliation_rate_limits_and_recovers_expired_leases() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, MIGRATIONS)
            transport = PostgresDurableTransport(engine)
            reconciliation = PostgresReconciliationRepository(engine)
            worker_id = uuid4()
            for _ in range(2):
                await transport.enqueue("task-dispatch", _envelope(worker_id=str(worker_id)))
            claims = await transport.claim(
                "task-dispatch",
                str(worker_id),
                tenant_id="default",
                limit=2,
                lease_duration=timedelta(minutes=1),
            )
            assert len(claims) == 2
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE durable_work_queue SET lease_expires_at = "
                        "clock_timestamp() - interval '1 second' WHERE claimed_by = :worker_id"
                    ),
                    {"worker_id": str(worker_id)},
                )

            limited = await reconciliation.run(
                ReconciliationRequest.model_validate(
                    {
                        "mode": "APPLY",
                        "workerId": worker_id,
                        "maxRepairs": 1,
                        "idempotencyKey": "limited-expired-leases",
                        "reason": "bounded recovery",
                    }
                ),
                tenant_id="default",
                actor_id="test:reconciler",
            )
            assert limited.repairs_applied == 1
            assert [finding.disposition for finding in limited.findings].count(
                ReconciliationDisposition.REPAIRED
            ) == 1
            assert [finding.disposition for finding in limited.findings].count(
                ReconciliationDisposition.DETECTED
            ) == 1
            assert (
                await reconciliation.run(
                    ReconciliationRequest.model_validate(
                        {
                            "mode": "APPLY",
                            "workerId": worker_id,
                            "maxRepairs": 1,
                            "idempotencyKey": "finish-expired-leases",
                            "reason": "finish bounded recovery",
                        }
                    ),
                    tenant_id="default",
                    actor_id="test:reconciler",
                )
            ).repairs_applied == 1
            converged = await reconciliation.run(
                ReconciliationRequest.model_validate(
                    {
                        "workerId": worker_id,
                        "idempotencyKey": "expired-lease-convergence",
                        "reason": "confirm queue recovery converged",
                    }
                ),
                tenant_id="default",
                actor_id="test:reconciler",
            )
            assert converged.findings == ()
            async with engine.connect() as connection:
                actions = (
                    (
                        await connection.execute(
                            text(
                                "SELECT action FROM audit_events "
                                "WHERE actor_id = 'test:reconciler' ORDER BY id"
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
            assert actions.count("reconciliation.repair") == 2
            assert actions.count("reconciliation.defer") == 1
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
