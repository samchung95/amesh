from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresOperationsRepository
from amesh.config import Settings
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
)
from amesh.postgres_qualification import qualify_postgres

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_backup_checkpoint_and_maintenance_inventory_are_durable() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, MIGRATIONS)
            repository = PostgresOperationsRepository(engine)
            created = await repository.record_backup_checkpoint(
                "s3://amesh/backups/manifest.json",
                "a" * 64,
                created_by="test:backup",
            )

            assert created.database_lsn
            assert created.schema_version == "0026_disaster_recovery.sql"
            assert await repository.latest_backup_checkpoint() == created
            exercise = await repository.start_recovery_exercise(
                created.checkpoint_id,
                profile="v1",
                scheduled=True,
                actor_id="test:recovery",
            )
            completed = await repository.complete_recovery_exercise(
                exercise.exercise_id,
                passed=True,
                rpo_seconds=1.0,
                rto_seconds=2.0,
                postgres_client_version="pg_restore 17",
                restored_schema_version="0026_disaster_recovery.sql",
                objects_total=2,
                objects_verified=2,
                reconciliation={"unresolved": 0},
                projections={"count": 0},
                readiness={"ready": True},
                unresolved_gaps=[],
            )
            assert completed.state == "PASSED"
            assert await repository.get_recovery_exercise(exercise.exercise_id) == completed
            maintenance = await repository.inspect_table_maintenance()
            backup_table = next(
                item for item in maintenance if item.table_name == "backup_checkpoints"
            )
            assert backup_table.total_bytes > 0
            assert not backup_table.partitioned
            report = await qualify_postgres(
                Settings(_env_file=None, database_url=database.database_url),
                profile="self-managed",
                require_tls=False,
                latency_samples=5,
                max_p95_ms=1_000,
            )
            assert report["passed"]
            assert report["postgresMajor"] in {15, 16, 17, 18}
            assert sorted(report["queryPlans"]) == [
                "outbox_publish",
                "queue_claim",
                "scheduler_due",
            ]
            assert report["latestBackupCheckpoint"]["object_manifest_checksum"] == "a" * 64
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
