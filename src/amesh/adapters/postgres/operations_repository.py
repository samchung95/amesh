from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.domain import new_runtime_id

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
        pg_current_wal_lsn(),
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


class BackupCheckpoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    checkpoint_id: UUID = Field(alias="id")
    database_lsn: str
    object_manifest_uri: str
    object_manifest_checksum: str = Field(pattern=r"^[0-9a-f]{64}$")
    schema_version: str
    created_by: str
    created_at: datetime


class TableMaintenanceStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    table_name: str
    live_rows: int = Field(ge=0)
    dead_rows: int = Field(ge=0)
    last_autovacuum: datetime | None
    last_autoanalyze: datetime | None
    total_bytes: int = Field(ge=0)
    partitioned: bool


class PostgresOperationsRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def record_backup_checkpoint(
        self,
        object_manifest_uri: str,
        object_manifest_checksum: str,
        *,
        created_by: str,
    ) -> BackupCheckpoint:
        if not object_manifest_uri:
            raise ValueError("object manifest URI is required")
        if len(object_manifest_checksum) != 64 or any(
            character not in "0123456789abcdef" for character in object_manifest_checksum
        ):
            raise ValueError("object manifest checksum must be a lowercase SHA-256 digest")
        async with self._engine.begin() as connection:
            row = (
                (
                    await connection.execute(
                        _INSERT_BACKUP_CHECKPOINT,
                        {
                            "checkpoint_id": new_runtime_id(),
                            "object_manifest_uri": object_manifest_uri,
                            "object_manifest_checksum": object_manifest_checksum,
                            "created_by": created_by,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return BackupCheckpoint.model_validate(row)

    async def latest_backup_checkpoint(self) -> BackupCheckpoint | None:
        async with self._engine.connect() as connection:
            row = (await connection.execute(_LATEST_BACKUP_CHECKPOINT)).mappings().one_or_none()
        return BackupCheckpoint.model_validate(row) if row is not None else None

    async def inspect_table_maintenance(self) -> list[TableMaintenanceStatus]:
        async with self._engine.connect() as connection:
            rows = (await connection.execute(_TABLE_MAINTENANCE)).mappings().all()
        return [TableMaintenanceStatus.model_validate(row) for row in rows]
