from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository, PostgresRetentionRepository
from amesh.domain.retention import (
    LifecycleLegalHoldDraft,
    LifecyclePolicyDraft,
    LifecycleResourceType,
    LifecycleScope,
)
from amesh.dsl import FlowDefinition
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
)
from amesh.ports import LifecycleVersionConflict, ObjectLifecycleResult, ObjectMetadata
from amesh.retention import RetentionService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class RecordingObjectStore:
    def __init__(self) -> None:
        self.deleted: list[tuple[str, str]] = []
        self.legal_hold = True

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        return ObjectMetadata(
            uri=uri,
            tenant_id=tenant_id,
            size=4096,
            checksum_sha256="a" * 64,
            legal_hold=self.legal_hold,
        )

    async def apply_lifecycle(
        self,
        tenant_id: str,
        uri: str,
        *,
        retention_until: datetime | None,
        legal_hold: bool,
        referenced: bool,
        delete: bool = False,
    ) -> ObjectLifecycleResult:
        assert retention_until is None
        assert not referenced and delete
        if legal_hold:
            return ObjectLifecycleResult(
                metadata=await self.head(tenant_id, uri),
                blocked_by="legal_hold",
            )
        self.deleted.append((tenant_id, uri))
        return ObjectLifecycleResult(
            metadata=await self.head(tenant_id, uri),
            deleted=True,
            deletion_marker=True,
        )


def test_execution_retention_previews_holds_and_resumable_authoritative_purge() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        try:
            executions = PostgresExecutionRepository(engine)
            repository = PostgresRetentionRepository(engine)
            object_store = RecordingObjectStore()
            service = RetentionService(repository, object_store)
            instance_policy = await repository.save_policy(
                "default",
                LifecyclePolicyDraft(
                    resourceType=LifecycleResourceType.METRIC,
                    scope=LifecycleScope.INSTANCE,
                    retentionDays=90,
                    reason="instance metric retention default",
                ),
                actor_id="user:instance-admin",
            )
            with pytest.raises(
                LifecycleVersionConflict,
                match="version changed or is unavailable",
            ):
                await repository.save_policy(
                    "default",
                    LifecyclePolicyDraft(
                        resourceType=LifecycleResourceType.METRIC,
                        scope=LifecycleScope.TENANT,
                        retentionDays=30,
                        reason="must not convert an instance policy",
                    ),
                    actor_id="user:tenant-operator",
                    policy_id=instance_policy.policy_id,
                    expected_version=instance_policy.version,
                )
            flow = FlowDefinition.model_validate(
                {
                    "id": "retained",
                    "namespace": "tests.retention",
                    "tasks": [{"id": "done", "type": "core.return"}],
                }
            )
            execution = await executions.create_execution(
                flow, tenant_id="default", inputs={"pii": "remove"}
            )
            task = (await executions.list_task_runs(execution.execution_id, tenant_id="default"))[0]
            old = datetime.now(UTC) - timedelta(days=10)
            artifact_uri = "amesh://tenants/default/executions/result.bin"
            async with engine.begin() as connection:
                tenant_uuid = await connection.scalar(
                    text("SELECT id FROM tenants WHERE slug = 'default'")
                )
                await connection.execute(
                    text(
                        """
                        UPDATE executions SET state = 'SUCCESS', created_at = :old,
                            updated_at = :old, terminal_at = :old
                        WHERE id = :execution_id
                        """
                    ),
                    {"old": old, "execution_id": execution.execution_id},
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO execution_logs (
                            id, tenant_id, execution_id, task_run_id, level, logger,
                            message, fields, redacted, occurred_at
                        ) VALUES (
                            gen_random_uuid(), :tenant_id, :execution_id, :task_run_id,
                            'INFO', 'retention-test', 'remove me', '{}'::jsonb, true, :old
                        )
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "execution_id": execution.execution_id,
                        "task_run_id": task.task_run_id,
                        "old": old,
                    },
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO execution_artifacts (
                            id, tenant_id, execution_id, task_run_id, attempt, uri,
                            size_bytes, media_type, occurred_at
                        ) VALUES (
                            gen_random_uuid(), :tenant_id, :execution_id, :task_run_id, 1,
                            :uri, 4096, 'application/octet-stream', :old
                        )
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "execution_id": execution.execution_id,
                        "task_run_id": task.task_run_id,
                        "uri": artifact_uri,
                        "old": old,
                    },
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO search_documents (
                            tenant_id, document_type, document_id, namespace, title,
                            occurred_at, source_updated_at
                        ) VALUES (
                            :tenant_id, 'EXECUTION', :document_id, 'tests.retention',
                            'retained execution', :old, :old
                        )
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "document_id": str(execution.execution_id),
                        "old": old,
                    },
                )

            policy = await repository.save_policy(
                "default",
                LifecyclePolicyDraft(
                    resourceType=LifecycleResourceType.EXECUTION,
                    scope=LifecycleScope.NAMESPACE,
                    namespace="tests.retention",
                    retentionDays=1,
                    batchSize=1,
                    reason="remove expired execution payloads",
                ),
                actor_id="user:operator",
            )
            hold = await repository.create_hold(
                "default",
                LifecycleLegalHoldDraft(
                    name="case-608",
                    reason="preserve this execution during review",
                    resourceType=LifecycleResourceType.EXECUTION,
                    resourceId=str(execution.execution_id),
                ),
                actor_id="user:operator",
            )
            blocked = await repository.preview(
                "default",
                policy.policy_id,
                actor_id="user:operator",
                reason="preview held execution",
            )
            assert blocked.estimated_records == 0
            assert blocked.protected_records == 1

            await repository.release_hold("default", hold.hold_id, actor_id="user:operator")
            preview = await repository.preview(
                "default",
                policy.policy_id,
                actor_id="user:operator",
                reason="confirm expired execution impact",
            )
            assert preview.estimated_records >= 4
            assert preview.estimated_bytes >= 4096
            with pytest.raises(ValueError, match="confirmation must exactly match"):
                await repository.confirm("default", preview.job_id, "PURGE")

            failed = await service.confirm_and_process(
                "default",
                preview.job_id,
                preview.confirmation_phrase,
            )
            assert failed.state == "FAILED"
            assert failed.retry_count == 1
            assert object_store.deleted == []
            object_store.legal_hold = False
            completed = await service.process_once("default", preview.job_id)
            assert completed.state == "SUCCEEDED"
            assert completed.processed_records > 0
            assert object_store.deleted == [("default", artifact_uri)]
            retained_execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={"keep": "specific policy"},
            )
            retained_task = (
                await executions.list_task_runs(
                    retained_execution.execution_id,
                    tenant_id="default",
                )
            )[0]
            async with engine.begin() as connection:
                tenant_uuid = await connection.scalar(
                    text("SELECT id FROM tenants WHERE slug = 'default'")
                )
                await connection.execute(
                    text(
                        """
                        UPDATE executions SET state = 'SUCCESS', created_at = :old,
                            updated_at = :old, terminal_at = :old
                        WHERE id = :execution_id
                        """
                    ),
                    {"old": old, "execution_id": retained_execution.execution_id},
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO execution_logs (
                            id, tenant_id, execution_id, task_run_id, level, logger,
                            message, fields, redacted, occurred_at
                        ) VALUES (
                            gen_random_uuid(), :tenant_id, :execution_id, :task_run_id,
                            'INFO', 'retention-test', 'keep me', '{}'::jsonb, true, :old
                        )
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "execution_id": retained_execution.execution_id,
                        "task_run_id": retained_task.task_run_id,
                        "old": old,
                    },
                )
            broad_log_policy = await repository.save_policy(
                "default",
                LifecyclePolicyDraft(
                    resourceType=LifecycleResourceType.LOG,
                    scope=LifecycleScope.TENANT,
                    retentionDays=1,
                    reason="broad task log lifecycle",
                ),
                actor_id="user:operator",
            )
            scheduled_policy = await repository.save_policy(
                "default",
                LifecyclePolicyDraft(
                    resourceType=LifecycleResourceType.LOG,
                    scope=LifecycleScope.NAMESPACE,
                    namespace="tests.retention",
                    retentionDays=30,
                    scheduleIntervalMinutes=5,
                    reason="specific scheduled task log lifecycle",
                ),
                actor_id="user:operator",
            )
            broad_preview = await repository.preview(
                "default",
                broad_log_policy.policy_id,
                actor_id="user:operator",
                reason="verify namespace policy precedence",
            )
            assert broad_preview.estimated_records == 0
            async with engine.begin() as connection:
                await connection.execute(
                    text("UPDATE lifecycle_policies SET next_run_at = :old WHERE id = :policy_id"),
                    {"old": old, "policy_id": scheduled_policy.policy_id},
                )
            scheduled = await service.run_scheduled_once(("default",))
            assert scheduled.jobs_created == 1
            assert scheduled.batches_processed == 1
            async with engine.connect() as connection:
                row = (
                    (
                        await connection.execute(
                            text("SELECT lifecycle, inputs FROM executions WHERE id = :id"),
                            {"id": execution.execution_id},
                        )
                    )
                    .mappings()
                    .one()
                )
                assert row["lifecycle"] == "TOMBSTONED"
                assert row["inputs"] == {}
                assert (
                    int(
                        await connection.scalar(
                            text(
                                """
                            SELECT count(*) FROM execution_logs
                            WHERE execution_id = :id
                            """
                            ),
                            {"id": execution.execution_id},
                        )
                        or 0
                    )
                    == 0
                )
                assert (
                    int(
                        await connection.scalar(
                            text(
                                """
                            SELECT count(*) FROM lifecycle_job_items
                            WHERE job_id = :job_id AND state = 'DELETED'
                            """
                            ),
                            {"job_id": preview.job_id},
                        )
                        or 0
                    )
                    == 1
                )
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


def test_session_policy_retention_is_terminal_bounded_and_tenant_isolated() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        try:
            executions = PostgresExecutionRepository(engine)
            repository = PostgresRetentionRepository(engine)
            service = RetentionService(repository, RecordingObjectStore())
            flow = FlowDefinition.model_validate(
                {
                    "id": "session-retention",
                    "namespace": "tests.session-retention",
                    "tasks": [{"id": "done", "type": "core.return"}],
                }
            )
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        """
                        INSERT INTO tenants (
                            slug, display_name, status, version, storage_prefix,
                            created_by, updated_by
                        ) VALUES (
                            'other', 'Other tenant', 'ACTIVE', 1, 'tenants/other/',
                            'test', 'test'
                        )
                        """
                    )
                )

            async def create_old(
                tenant_id: str,
                *,
                trigger: dict[str, object] | None = None,
                state: str = "SUCCESS",
            ) -> object:
                execution = await executions.create_execution(
                    flow,
                    tenant_id=tenant_id,
                    inputs={"sensitive": "payload"},
                    trigger=trigger,
                )
                old = datetime.now(UTC) - timedelta(days=2)
                async with engine.begin() as connection:
                    await connection.execute(
                        text(
                            """
                            UPDATE executions
                            SET state = :state, created_at = :created_at,
                                updated_at = :created_at, terminal_at = :terminal_at
                            WHERE id = :execution_id
                            """
                        ),
                        {
                            "state": state,
                            "created_at": old,
                            "terminal_at": old if state == "SUCCESS" else None,
                            "execution_id": execution.execution_id,
                        },
                    )
                return execution

            session_trigger = {
                "ameshAgentSessionId": str(uuid4()),
                "ameshAgentSessionPolicy": {
                    "policies": [{"policyId": str(uuid4()), "revision": 1}],
                    "retentionSeconds": 0,
                },
            }
            eligible = await create_old("default", trigger=session_trigger)
            active = await create_old("default", trigger=session_trigger, state="RUNNING")
            paused = await create_old("default", trigger=session_trigger, state="PAUSED")
            held = await create_old("default", trigger=session_trigger)
            non_session = await create_old("default")
            cross_tenant = await create_old("other", trigger=session_trigger)
            hold = await repository.create_hold(
                "default",
                LifecycleLegalHoldDraft(
                    name="session-case",
                    reason="preserve held session evidence",
                    resourceType=LifecycleResourceType.EXECUTION,
                    resourceId=str(held.execution_id),
                ),
                actor_id="user:retention",
            )
            del hold
            policy = await repository.save_policy(
                "default",
                LifecyclePolicyDraft(
                    resourceType=LifecycleResourceType.EXECUTION,
                    scope=LifecycleScope.NAMESPACE,
                    namespace=flow.namespace,
                    retentionDays=30,
                    reason="session retention lifecycle boundary",
                ),
                actor_id="user:retention",
            )
            preview = await repository.preview(
                "default",
                policy.policy_id,
                actor_id="user:retention",
                reason="preview session policy retention",
            )
            assert preview.estimated_records >= 1
            assert preview.protected_records == 1
            completed = await service.confirm_and_process(
                "default", preview.job_id, preview.confirmation_phrase
            )
            assert completed.state.value == "SUCCEEDED"

            async with engine.connect() as connection:
                rows = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT id, lifecycle, state, inputs
                                FROM executions
                                WHERE id = ANY(CAST(:ids AS uuid[]))
                                """
                            ),
                            {
                                "ids": [
                                    eligible.execution_id,
                                    active.execution_id,
                                    paused.execution_id,
                                    held.execution_id,
                                    non_session.execution_id,
                                ]
                            },
                        )
                    )
                    .mappings()
                    .all()
                )
            by_id = {row["id"]: row for row in rows}
            assert by_id[eligible.execution_id]["lifecycle"] == "TOMBSTONED"
            assert by_id[eligible.execution_id]["inputs"] == {}
            assert by_id[active.execution_id]["lifecycle"] != "TOMBSTONED"
            assert by_id[paused.execution_id]["lifecycle"] != "TOMBSTONED"
            assert by_id[held.execution_id]["lifecycle"] != "TOMBSTONED"
            assert by_id[non_session.execution_id]["lifecycle"] != "TOMBSTONED"
            async with engine.connect() as connection:
                lifecycle_events = await connection.scalar(
                    text(
                        """
                        SELECT count(*) FROM lifecycle_events
                        WHERE tenant_id = (SELECT id FROM tenants WHERE slug = 'default')
                          AND job_id = :job_id
                          AND event_type = 'LifecyclePurgeCompleted'
                        """
                    ),
                    {"job_id": preview.job_id},
                )
                other_lifecycle = await connection.scalar(
                    text("SELECT lifecycle FROM executions WHERE id = :id"),
                    {"id": cross_tenant.execution_id},
                )
            assert lifecycle_events == 1
            assert other_lifecycle != "TOMBSTONED"
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
