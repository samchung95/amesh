from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkerStatus(StrEnum):
    STARTING = "STARTING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    DRAINING = "DRAINING"
    STOPPED = "STOPPED"


class LogLevel(StrEnum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class MetricKind(StrEnum):
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    TIMER = "TIMER"
    CUSTOM = "CUSTOM"


class LogSourceStream(StrEnum):
    TASK = "TASK"
    STDOUT = "STDOUT"
    STDERR = "STDERR"
    PLUGIN = "PLUGIN"
    SYSTEM = "SYSTEM"


class ExecutionEvidenceKind(StrEnum):
    STATE = "STATE"
    LOG = "LOG"
    METRIC = "METRIC"
    OUTPUT = "OUTPUT"
    ARTIFACT = "ARTIFACT"


class MetadataVersionConflict(RuntimeError):
    """Raised when a metadata write uses a stale resource version."""


class PersistedTrigger(BaseModel):
    model_config = ConfigDict(frozen=True)

    trigger_id: UUID
    flow_revision_id: UUID
    tenant_id: str
    namespace: str
    flow_id: str
    trigger_key: str
    trigger_type: str
    definition: dict[str, Any]
    enabled: bool
    created_by: str
    created_at: datetime


class WorkerMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    worker_id: UUID
    worker_group: str = Field(min_length=1, max_length=128)
    instance_name: str = Field(min_length=1, max_length=256)
    version: str = Field(min_length=1, max_length=128)
    status: WorkerStatus
    capabilities: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)
    last_heartbeat_at: datetime


class PersistedWorker(WorkerMetadata):
    tenant_id: str
    resource_version: int = Field(ge=1)
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class ExecutionLogEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    log_id: UUID
    execution_id: UUID
    task_run_id: UUID | None = None
    attempt: int = Field(default=1, ge=1)
    worker_id: UUID | None = None
    trace_id: str | None = Field(default=None, max_length=256)
    source_stream: LogSourceStream = LogSourceStream.TASK
    level: LogLevel
    logger: str = Field(min_length=1, max_length=256)
    message: str
    fields: dict[str, Any] = Field(default_factory=dict)
    redacted: bool = False
    occurred_at: datetime
    ingested_at: datetime | None = None


class ExecutionMetric(BaseModel):
    model_config = ConfigDict(frozen=True)

    metric_id: UUID
    execution_id: UUID
    task_run_id: UUID | None = None
    attempt: int = Field(default=1, ge=1)
    metric_name: str = Field(min_length=1, max_length=256)
    metric_kind: MetricKind
    metric_value: Decimal
    unit: str | None = Field(default=None, max_length=64)
    labels: dict[str, str] = Field(default_factory=dict)
    occurred_at: datetime
    ingested_at: datetime | None = None


class ExecutionOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    output_id: UUID
    execution_id: UUID
    task_run_id: UUID
    attempt: int = Field(ge=1)
    value: dict[str, Any]
    size_bytes: int = Field(ge=0)
    sensitive: bool = False
    occurred_at: datetime
    ingested_at: datetime


class ExecutionArtifact(BaseModel):
    model_config = ConfigDict(frozen=True)

    artifact_id: UUID
    execution_id: UUID
    task_run_id: UUID
    attempt: int = Field(ge=1)
    uri: str
    size_bytes: int = Field(ge=0)
    media_type: str | None = None
    checksum_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    occurred_at: datetime
    ingested_at: datetime


class ExecutionEvidenceEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    cursor: int = Field(ge=1)
    event_id: UUID
    execution_id: UUID
    task_run_id: UUID | None = None
    kind: ExecutionEvidenceKind
    event_type: str
    payload: dict[str, Any]
    occurred_at: datetime
    ingested_at: datetime


class AssetMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    asset_id: UUID
    provider: str = Field(min_length=1, max_length=128)
    external_key: str = Field(min_length=1, max_length=512)
    asset_type: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=512)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PersistedAsset(AssetMetadata):
    tenant_id: str
    resource_version: int = Field(ge=1)
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class MetadataRepository(Protocol):
    async def replace_flow_triggers(
        self,
        flow_revision_id: UUID,
        definitions: tuple[dict[str, Any], ...],
        *,
        tenant_id: str,
        actor_id: str,
    ) -> list[PersistedTrigger]: ...

    async def list_flow_triggers(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
    ) -> list[PersistedTrigger]: ...

    async def register_worker(
        self,
        worker: WorkerMetadata,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> PersistedWorker: ...

    async def heartbeat_worker(
        self,
        worker_id: UUID,
        *,
        tenant_id: str,
        status: WorkerStatus,
        last_heartbeat_at: datetime,
        expected_version: int,
        actor_id: str,
    ) -> PersistedWorker: ...

    async def list_workers(self, *, tenant_id: str) -> list[PersistedWorker]: ...

    async def append_log(
        self,
        entry: ExecutionLogEntry,
        *,
        tenant_id: str,
    ) -> ExecutionLogEntry: ...

    async def list_logs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionLogEntry]: ...

    async def append_metric(
        self,
        metric: ExecutionMetric,
        *,
        tenant_id: str,
    ) -> ExecutionMetric: ...

    async def list_metrics(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionMetric]: ...

    async def list_outputs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionOutput]: ...

    async def list_artifacts(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionArtifact]: ...

    async def list_evidence_events(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        after_cursor: int = 0,
        limit: int = 500,
    ) -> list[ExecutionEvidenceEvent]: ...

    async def upsert_asset(
        self,
        asset: AssetMetadata,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> PersistedAsset: ...

    async def list_assets(self, *, tenant_id: str) -> list[PersistedAsset]: ...
