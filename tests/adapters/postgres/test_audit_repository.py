from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresAuditRepository
from amesh.domain import new_runtime_id
from amesh.domain.audit import (
    AuditLegalHoldCreate,
    ComplianceEvidenceCategory,
    ComplianceEvidenceCreate,
)
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


def test_audit_ledger_redaction_integrity_retention_and_compliance_evidence() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        try:
            await apply_migrations(database.database_url, migration_directory())
            engine = create_async_engine(database.database_url)
            repository = PostgresAuditRepository(engine)
            now = datetime.now(UTC)
            async with engine.begin() as connection:
                tenant_id = await connection.scalar(
                    text("SELECT id FROM tenants WHERE slug = 'default'")
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO audit_events (
                            event_id, tenant_id, actor_id, action, resource_type,
                            resource_id, outcome, source, evidence, occurred_at
                        ) VALUES (
                            :event_id, :tenant_id, 'user:test', 'secret.use', 'secret',
                            'database', 'SUCCESS', CAST(:source AS jsonb),
                            CAST(:evidence AS jsonb), :occurred_at
                        )
                        """
                    ),
                    {
                        "event_id": new_runtime_id(),
                        "tenant_id": tenant_id,
                        "source": json.dumps({"component": "test", "authorization": "canary-auth"}),
                        "evidence": json.dumps(
                            {"token": "canary-token", "nested": {"password": "canary-password"}}
                        ),
                        "occurred_at": now,
                    },
                )

            page = await repository.list_events(
                "default",
                actor_id="user:auditor",
                action="secret.use",
            )
            assert len(page.items) == 1
            event = page.items[0]
            assert event.reason == "completed"
            assert event.correlation_id == event.trace_id
            assert event.source["authorization"] == "[REDACTED]"
            assert event.evidence["token"] == "[REDACTED]"
            assert event.evidence["nested"]["password"] == "[REDACTED]"
            assert len(event.event_hash) == 64
            assert (await repository.verify_integrity("default", actor_id="user:auditor")).valid

            hold = await repository.create_legal_hold(
                "default",
                AuditLegalHoldCreate(
                    name="investigation",
                    reason="retain audit evidence",
                    startsAt=now - timedelta(days=1),
                    endsAt=now + timedelta(days=1),
                ),
                actor_id="user:auditor",
            )
            async with engine.begin() as connection:
                await connection.execute(
                    text("UPDATE audit_events SET retention_until = :expired"),
                    {"expired": now - timedelta(seconds=1)},
                )
            blocked = await repository.purge_retained("default", actor_id="user:auditor")
            assert blocked.deleted_events == 0
            assert blocked.stopped_by_legal_hold

            await repository.release_legal_hold(
                "default",
                hold.hold_id,
                actor_id="user:auditor",
            )
            async with engine.begin() as connection:
                await connection.execute(
                    text("UPDATE audit_events SET retention_until = :expired"),
                    {"expired": now - timedelta(seconds=1)},
                )
            purged = await repository.purge_retained("default", actor_id="user:auditor")
            assert purged.deleted_events > 0
            assert purged.anchor_hash is not None
            assert not purged.stopped_by_legal_hold
            assert (await repository.verify_integrity("default", actor_id="user:auditor")).valid

            compliance = await repository.create_compliance_evidence(
                "default",
                ComplianceEvidenceCreate(
                    category=ComplianceEvidenceCategory.BACKUP_RESTORE,
                    title="Local restore rehearsal",
                    source="pytest",
                    occurredAt=now,
                    payload={"result": "passed", "apiKey": "canary-api-key"},
                ),
                actor_id="user:auditor",
            )
            assert compliance.payload["apiKey"] == "[REDACTED]"
            snapshot = await repository.compliance_snapshot(
                "default",
                actor_id="user:auditor",
                occurred_from=None,
                occurred_to=None,
                max_audit_events=100,
            )
            assert snapshot.backup_restore_evidence[0]["payload"]["apiKey"] == "[REDACTED]"

            async with engine.begin() as connection:
                latest_event_id = await connection.scalar(
                    text("SELECT event_id FROM audit_events ORDER BY id DESC LIMIT 1")
                )
                await connection.execute(
                    text(
                        """
                        UPDATE audit_events
                        SET evidence = evidence || '{"tampered": true}'::jsonb
                        WHERE event_id = :event_id
                        """
                    ),
                    {"event_id": latest_event_id},
                )
            invalid = await repository.verify_integrity("default", actor_id="user:auditor")
            assert not invalid.valid
            assert invalid.reason == "HASH_MISMATCH"
            await engine.dispose()
        finally:
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
