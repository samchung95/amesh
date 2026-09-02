from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


class RecoveryExercise(BaseModel):
    model_config = ConfigDict(frozen=True)

    exercise_id: UUID = Field(alias="id")
    checkpoint_id: UUID
    profile: str
    scheduled: bool
    state: Literal["RUNNING", "PASSED", "FAILED"]
    actor_id: str
    started_at: datetime
    completed_at: datetime | None
    rpo_seconds: float | None = Field(default=None, ge=0)
    rto_seconds: float | None = Field(default=None, ge=0)
    postgres_client_version: str | None
    restored_schema_version: str | None
    objects_total: int = Field(ge=0)
    objects_verified: int = Field(ge=0)
    reconciliation: dict[str, Any]
    projections: dict[str, Any]
    readiness: dict[str, Any]
    unresolved_gaps: list[str]


class OperationsRepository(Protocol):
    async def record_backup_checkpoint(
        self,
        object_manifest_uri: str,
        object_manifest_checksum: str,
        *,
        created_by: str,
        database_lsn: str | None = None,
    ) -> BackupCheckpoint: ...

    async def latest_backup_checkpoint(self) -> BackupCheckpoint | None: ...

    async def inspect_table_maintenance(self) -> list[TableMaintenanceStatus]: ...

    async def start_recovery_exercise(
        self,
        checkpoint_id: UUID,
        *,
        profile: str,
        scheduled: bool,
        actor_id: str,
    ) -> RecoveryExercise: ...

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
    ) -> RecoveryExercise: ...

    async def get_recovery_exercise(self, exercise_id: UUID) -> RecoveryExercise: ...

    async def prepare_restored_state(self) -> dict[str, int]: ...

    async def rebuild_disposable_projections(self) -> list[str]: ...


__all__ = [
    "BackupCheckpoint",
    "OperationsRepository",
    "RecoveryExercise",
    "TableMaintenanceStatus",
]
