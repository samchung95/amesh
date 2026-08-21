from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository, PostgresMetadataRepository
from amesh.domain import new_runtime_id
from amesh.dsl import FlowDefinition
from amesh.ports import (
    AssetMetadata,
    ExecutionLogEntry,
    ExecutionMetric,
    LogLevel,
    MetadataVersionConflict,
    MetricKind,
    WorkerMetadata,
    WorkerStatus,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


async def _cleanup(
    engine: AsyncEngine,
    *,
    execution_id: UUID,
    worker_id: UUID,
    namespace: str,
) -> None:
    async with engine.begin() as connection:
        parameters = {"execution_id": execution_id}
        for table in ("execution_logs", "execution_metrics"):
            await connection.execute(
                text(f"DELETE FROM {table} WHERE execution_id = :execution_id"),
                parameters,
            )
        await connection.execute(
            text("DELETE FROM messages_outbox WHERE partition_key = :partition_key"),
            {"partition_key": f"execution:{execution_id}"},
        )
        await connection.execute(
            text(
                "DELETE FROM task_attempts WHERE task_run_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = :execution_id)"
            ),
            parameters,
        )
        for table in ("task_run_events", "task_runs", "execution_events"):
            await connection.execute(
                text(f"DELETE FROM {table} WHERE execution_id = :execution_id"),
                parameters,
            )
        await connection.execute(
            text("DELETE FROM executions WHERE id = :execution_id"),
            parameters,
        )
        await connection.execute(text("DELETE FROM workers WHERE id = :id"), {"id": worker_id})
        await connection.execute(
            text("DELETE FROM assets WHERE external_key = :key"),
            {"key": f"catalog/{namespace}"},
        )
        tenant_id = await connection.scalar(text("SELECT id FROM tenants WHERE slug = 'default'"))
        await connection.execute(
            text(
                "UPDATE flows SET active_revision = NULL "
                "WHERE tenant_id = :tenant_id AND namespace_id IN "
                "(SELECT id FROM namespaces WHERE tenant_id = :tenant_id AND name = :namespace)"
            ),
            {"tenant_id": tenant_id, "namespace": namespace},
        )
        await connection.execute(
            text(
                "DELETE FROM trigger_definitions WHERE flow_revision_id IN ("
                "SELECT flow_revisions.id FROM flow_revisions "
                "JOIN flows ON flows.id = flow_revisions.flow_id "
                "JOIN namespaces ON namespaces.id = flows.namespace_id "
                "WHERE namespaces.name = :namespace)"
            ),
            {"namespace": namespace},
        )
        for table in ("flow_revisions", "flows", "namespaces"):
            await connection.execute(
                text(
                    f"DELETE FROM {table} WHERE tenant_id = :tenant_id AND "
                    + (
                        "name = :namespace"
                        if table == "namespaces"
                        else (
                            "namespace_id IN (SELECT id FROM namespaces WHERE name = :namespace)"
                            if table == "flows"
                            else "flow_id IN (SELECT id FROM flows WHERE namespace_id IN "
                            "(SELECT id FROM namespaces WHERE name = :namespace))"
                        )
                    )
                ),
                {"tenant_id": tenant_id, "namespace": namespace},
            )


def test_metadata_repository_round_trip_constraints_and_rls() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        executions = PostgresExecutionRepository(engine)
        metadata = PostgresMetadataRepository(engine)
        namespace = f"tests.metadata.{uuid4().hex}"
        flow = FlowDefinition.model_validate(
            {
                "id": "metadata_contract",
                "namespace": namespace,
                "triggers": [
                    {
                        "id": "hourly",
                        "type": "core.cron",
                        "cron": "0 * * * *",
                        "timezone": "UTC",
                    }
                ],
                "tasks": [{"id": "done", "type": "core.return"}],
            }
        )
        execution = await executions.create_execution(flow, tenant_id="default", inputs={})
        task = (await executions.list_task_runs(execution.execution_id, tenant_id="default"))[0]
        now = datetime.now(UTC)
        worker_id = new_runtime_id()
        worker = WorkerMetadata(
            worker_id=worker_id,
            worker_group="metadata-tests",
            instance_name=f"worker-{uuid4().hex}",
            version="test",
            status=WorkerStatus.READY,
            capabilities={"runner": "local"},
            labels={"suite": "metadata"},
            last_heartbeat_at=now,
        )
        try:
            triggers = await metadata.list_flow_triggers(
                namespace,
                flow.id,
                tenant_id="default",
            )
            assert [(item.trigger_key, item.trigger_type, item.enabled) for item in triggers] == [
                ("hourly", "core.cron", True)
            ]

            registered = await metadata.register_worker(
                worker,
                tenant_id="default",
                actor_id="test:metadata",
            )
            heartbeat = await metadata.heartbeat_worker(
                worker_id,
                tenant_id="default",
                status=WorkerStatus.DEGRADED,
                last_heartbeat_at=now,
                expected_version=registered.resource_version,
                actor_id="test:metadata",
            )
            assert heartbeat.resource_version == registered.resource_version + 1
            assert heartbeat in await metadata.list_workers(tenant_id="default")
            with pytest.raises(MetadataVersionConflict, match="stale"):
                await metadata.heartbeat_worker(
                    worker_id,
                    tenant_id="default",
                    status=WorkerStatus.READY,
                    last_heartbeat_at=now,
                    expected_version=registered.resource_version,
                    actor_id="test:metadata",
                )

            log = ExecutionLogEntry(
                log_id=new_runtime_id(),
                execution_id=execution.execution_id,
                task_run_id=task.task_run_id,
                level=LogLevel.INFO,
                logger="test.metadata",
                message="task metadata persisted",
                fields={"credential": "[redacted]"},
                redacted=True,
                occurred_at=now,
            )
            metric = ExecutionMetric(
                metric_id=new_runtime_id(),
                execution_id=execution.execution_id,
                task_run_id=task.task_run_id,
                metric_name="task.duration",
                metric_kind=MetricKind.TIMER,
                metric_value=Decimal("1.25"),
                unit="seconds",
                labels={"task": task.task_id},
                occurred_at=now,
            )
            assert await metadata.append_log(log, tenant_id="default") == log
            assert await metadata.append_metric(metric, tenant_id="default") == metric
            assert await metadata.list_logs(execution.execution_id, tenant_id="default") == [log]
            assert await metadata.list_metrics(execution.execution_id, tenant_id="default") == [
                metric
            ]

            asset = AssetMetadata(
                asset_id=new_runtime_id(),
                provider="test-catalog",
                external_key=f"catalog/{namespace}",
                asset_type="dataset",
                display_name="Metadata contract",
                metadata={"classification": "internal"},
            )
            created = await metadata.upsert_asset(
                asset,
                tenant_id="default",
                actor_id="test:metadata",
            )
            updated = await metadata.upsert_asset(
                asset.model_copy(update={"display_name": "Metadata contract v2"}),
                tenant_id="default",
                actor_id="test:metadata",
                expected_version=created.resource_version,
            )
            assert updated.resource_version == 2
            assert updated in await metadata.list_assets(tenant_id="default")
            with pytest.raises(MetadataVersionConflict, match="stale"):
                await metadata.upsert_asset(
                    asset,
                    tenant_id="default",
                    actor_id="test:metadata",
                    expected_version=created.resource_version,
                )

            with pytest.raises(DBAPIError):
                async with engine.begin() as connection:
                    await connection.execute(
                        text("UPDATE executions SET state = 'INVALID' WHERE id = :id"),
                        {"id": execution.execution_id},
                    )

            async with engine.connect() as connection:
                policies = set(
                    await connection.scalars(
                        text(
                            "SELECT tablename FROM pg_policies "
                            "WHERE policyname = 'tenant_runtime_isolation'"
                        )
                    )
                )
            assert {
                "assets",
                "execution_logs",
                "execution_metrics",
                "trigger_definitions",
            } <= policies
        finally:
            await _cleanup(
                engine,
                execution_id=execution.execution_id,
                worker_id=worker_id,
                namespace=namespace,
            )
            await engine.dispose()

    asyncio.run(scenario())
