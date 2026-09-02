from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.adapters.postgres.tenant_context import tenant_admin_transaction
from amesh.domain import new_runtime_id
from amesh.ports.operations import (
    BackupCheckpoint,
    OperationsRepository,
    RecoveryExercise,
    TableMaintenanceStatus,
)

_INSERT_BACKUP_CHECKPOINT = text(
    """
    INSERT INTO backup_checkpoints (
        id,
        database_lsn,
        object_manifest_uri,
        object_manifest_checksum,
        schema_version,
        created_by
    )
    VALUES (
        :checkpoint_id,
        COALESCE(CAST(CAST(:database_lsn AS text) AS pg_lsn), pg_current_wal_lsn()),
        :object_manifest_uri,
        :object_manifest_checksum,
        (SELECT max(version) FROM amesh_schema_migrations),
        :created_by
    )
    RETURNING
        id,
        database_lsn::text AS database_lsn,
        object_manifest_uri,
        object_manifest_checksum,
        schema_version,
        created_by,
        created_at
    """
)

_LATEST_BACKUP_CHECKPOINT = text(
    """
    SELECT
        id,
        database_lsn::text AS database_lsn,
        object_manifest_uri,
        object_manifest_checksum,
        schema_version,
        created_by,
        created_at
    FROM backup_checkpoints
    ORDER BY created_at DESC, id DESC
    LIMIT 1
    """
)

_TABLE_MAINTENANCE = text(
    """
    SELECT
        statistics.relname AS table_name,
        statistics.n_live_tup AS live_rows,
        statistics.n_dead_tup AS dead_rows,
        statistics.last_autovacuum,
        statistics.last_autoanalyze,
        pg_total_relation_size(statistics.relid) AS total_bytes,
        EXISTS (
            SELECT 1
            FROM pg_partitioned_table
            WHERE pg_partitioned_table.partrelid = statistics.relid
        ) AS partitioned
    FROM pg_stat_user_tables AS statistics
    ORDER BY pg_total_relation_size(statistics.relid) DESC, statistics.relname
    """
)

_START_RECOVERY_EXERCISE = text(
    """
    INSERT INTO recovery_exercises (
        id, checkpoint_id, profile, scheduled, actor_id
    ) VALUES (
        :exercise_id, :checkpoint_id, :profile, :scheduled, :actor_id
    )
    RETURNING *
    """
)

_COMPLETE_RECOVERY_EXERCISE = text(
    """
    UPDATE recovery_exercises
    SET state = :state,
        completed_at = clock_timestamp(),
        rpo_seconds = :rpo_seconds,
        rto_seconds = :rto_seconds,
        postgres_client_version = :postgres_client_version,
        restored_schema_version = :restored_schema_version,
        objects_total = :objects_total,
        objects_verified = :objects_verified,
        reconciliation = CAST(:reconciliation AS jsonb),
        projections = CAST(:projections AS jsonb),
        readiness = CAST(:readiness AS jsonb),
        unresolved_gaps = CAST(:unresolved_gaps AS jsonb)
    WHERE id = :exercise_id AND state = 'RUNNING'
    RETURNING *
    """
)

_GET_RECOVERY_EXERCISE = text("SELECT * FROM recovery_exercises WHERE id = :exercise_id")

_PREPARE_RESTORED_STATE = (
    text(
        """
        UPDATE service_instances
        SET state = 'STOPPED',
            generation = generation + 1,
            resource_version = resource_version + 1,
            stopped_at = clock_timestamp(),
            ownership = '{}'::jsonb,
            partitions = '{}'::jsonb
        WHERE state <> 'STOPPED'
        RETURNING id
        """
    ),
    text(
        """
        UPDATE workers
        SET status = 'STOPPED',
            cancellation_acknowledged = false,
            heartbeat_progress = '{}'::jsonb,
            resource_usage = '{}'::jsonb
        WHERE status <> 'STOPPED'
        RETURNING id
        """
    ),
    text(
        """
        UPDATE durable_work_queue
        SET lease_expires_at = clock_timestamp() - interval '1 second',
            updated_at = clock_timestamp()
        WHERE state = 'CLAIMED'
        RETURNING id
        """
    ),
    text(
        """
        UPDATE task_attempts
        SET lease_expires_at = clock_timestamp() - interval '1 second'
        WHERE state = 'RUNNING' AND worker_id IS NOT NULL
        RETURNING id
        """
    ),
    text(
        """
        UPDATE leases
        SET expires_at = clock_timestamp() - interval '1 second',
            fencing_token = fencing_token + 1,
            updated_at = clock_timestamp()
        WHERE expires_at > clock_timestamp()
        RETURNING resource_id
        """
    ),
    text(
        """
        UPDATE scheduler_states
        SET owner_id = NULL,
            lease_expires_at = NULL,
            fencing_token = fencing_token + 1,
            last_decision = 'ownership cleared after database restoration',
            updated_at = clock_timestamp()
        WHERE owner_id IS NOT NULL
        RETURNING trigger_definition_id
        """
    ),
)

_RESTORED_STATE_LABELS = (
    "serviceInstancesStopped",
    "workersStopped",
    "queueClaimsExpired",
    "taskAttemptLeasesExpired",
    "genericLeasesExpired",
    "schedulerOwnersCleared",
)

_REBUILD_DISPOSABLE_PROJECTIONS = text(
    "SELECT projection_name, refreshed FROM amesh_rebuild_disposable_projections()"
)


class PostgresOperationsRepository(OperationsRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def record_backup_checkpoint(
        self,
        object_manifest_uri: str,
        object_manifest_checksum: str,
        *,
        created_by: str,
        database_lsn: str | None = None,
    ) -> BackupCheckpoint:
        if not object_manifest_uri:
            raise ValueError("object manifest URI is required")
        if len(object_manifest_checksum) != 64 or any(
            character not in "0123456789abcdef" for character in object_manifest_checksum
        ):
            raise ValueError("object manifest checksum must be a lowercase SHA-256 digest")
        async with tenant_admin_transaction(self._engine) as connection:
            row = (
                (
                    await connection.execute(
                        _INSERT_BACKUP_CHECKPOINT,
                        {
                            "checkpoint_id": new_runtime_id(),
                            "object_manifest_uri": object_manifest_uri,
                            "object_manifest_checksum": object_manifest_checksum,
                            "created_by": created_by,
                            "database_lsn": database_lsn,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return BackupCheckpoint.model_validate(row)

    async def latest_backup_checkpoint(self) -> BackupCheckpoint | None:
        async with tenant_admin_transaction(self._engine) as connection:
            row = (await connection.execute(_LATEST_BACKUP_CHECKPOINT)).mappings().one_or_none()
        return BackupCheckpoint.model_validate(row) if row is not None else None

    async def inspect_table_maintenance(self) -> list[TableMaintenanceStatus]:
        async with tenant_admin_transaction(self._engine) as connection:
            rows = (await connection.execute(_TABLE_MAINTENANCE)).mappings().all()
        return [TableMaintenanceStatus.model_validate(row) for row in rows]

    async def start_recovery_exercise(
        self,
        checkpoint_id: UUID,
        *,
        profile: str,
        scheduled: bool,
        actor_id: str,
    ) -> RecoveryExercise:
        if not profile.strip():
            raise ValueError("recovery profile is required")
        async with tenant_admin_transaction(self._engine) as connection:
            row = (
                (
                    await connection.execute(
                        _START_RECOVERY_EXERCISE,
                        {
                            "exercise_id": new_runtime_id(),
                            "checkpoint_id": checkpoint_id,
                            "profile": profile,
                            "scheduled": scheduled,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return RecoveryExercise.model_validate(row)

    async def complete_recovery_exercise(
        self,
        exercise_id: UUID,
        *,
        passed: bool,
        rpo_seconds: float,
        rto_seconds: float,
        postgres_client_version: str,
        restored_schema_version: str | None,
        objects_total: int,
        objects_verified: int,
        reconciliation: dict[str, Any],
        projections: dict[str, Any],
        readiness: dict[str, Any],
        unresolved_gaps: list[str],
    ) -> RecoveryExercise:
        async with tenant_admin_transaction(self._engine) as connection:
            row = (
                (
                    await connection.execute(
                        _COMPLETE_RECOVERY_EXERCISE,
                        {
                            "exercise_id": exercise_id,
                            "state": "PASSED" if passed else "FAILED",
                            "rpo_seconds": rpo_seconds,
                            "rto_seconds": rto_seconds,
                            "postgres_client_version": postgres_client_version,
                            "restored_schema_version": restored_schema_version,
                            "objects_total": objects_total,
                            "objects_verified": objects_verified,
                            "reconciliation": json.dumps(reconciliation),
                            "projections": json.dumps(projections),
                            "readiness": json.dumps(readiness),
                            "unresolved_gaps": json.dumps(unresolved_gaps),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError(f"running recovery exercise {exercise_id} does not exist")
        return RecoveryExercise.model_validate(row)

    async def get_recovery_exercise(self, exercise_id: UUID) -> RecoveryExercise:
        async with tenant_admin_transaction(self._engine) as connection:
            row = (
                (
                    await connection.execute(
                        _GET_RECOVERY_EXERCISE,
                        {"exercise_id": exercise_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError(f"recovery exercise {exercise_id} does not exist")
        return RecoveryExercise.model_validate(row)

    async def prepare_restored_state(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        async with tenant_admin_transaction(self._engine) as connection:
            for label, statement in zip(
                _RESTORED_STATE_LABELS,
                _PREPARE_RESTORED_STATE,
                strict=True,
            ):
                rows = (await connection.execute(statement)).all()
                counts[label] = len(rows)
        return counts

    async def rebuild_disposable_projections(self) -> list[str]:
        async with tenant_admin_transaction(self._engine) as connection:
            rows = (await connection.execute(_REBUILD_DISPOSABLE_PROJECTIONS)).mappings().all()
        return [str(row["projection_name"]) for row in rows if row["refreshed"]]


__all__ = [
    "BackupCheckpoint",
    "PostgresOperationsRepository",
    "RecoveryExercise",
    "TableMaintenanceStatus",
]
