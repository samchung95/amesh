from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .errors import VersionConflict


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
    AGENT = "AGENT"
    MODEL = "MODEL"
    TOOL = "TOOL"
    ERROR = "ERROR"
    APPROVAL = "APPROVAL"
    INTERVENTION = "INTERVENTION"
    CONTROL = "CONTROL"
    DECISION = "DECISION"


class AssetAccessMode(StrEnum):
    READ = "READ"
    WRITE = "WRITE"


class AssetHealth(StrEnum):
    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class AssetRegistrationSource(StrEnum):
    DECLARED = "DECLARED"
    PLUGIN_EVENT = "PLUGIN_EVENT"


class LineageEvidenceKind(StrEnum):
    DECLARED = "DECLARED"
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"


class MetadataVersionConflict(VersionConflict):
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
    logical_path: str | None = Field(default=None, max_length=4096)
    lineage: tuple[str, ...] = ()
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
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    asset_id: UUID = Field(alias="assetId")
    namespace: str = Field(default="default", min_length=1, max_length=255)
    provider: str = Field(min_length=1, max_length=128)
    account: str = Field(default="default", min_length=1, max_length=255)
    location: str = Field(default="global", min_length=1, max_length=512)
    external_key: str = Field(alias="externalKey", min_length=1, max_length=1024)
    asset_type: str = Field(alias="assetType", min_length=1, max_length=128)
    display_name: str = Field(alias="displayName", min_length=1, max_length=512)
    description: str = Field(default="", max_length=4096)
    owner: str | None = Field(default=None, max_length=255)
    contacts: tuple[str, ...] = ()
    domain_group: str | None = Field(default=None, alias="domainGroup", max_length=255)
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict, alias="customMetadata")
    labels: dict[str, str] = Field(default_factory=dict)
    health: AssetHealth = AssetHealth.UNKNOWN
    last_materialization_at: datetime | None = Field(default=None, alias="lastMaterializationAt")
    source: AssetRegistrationSource = AssetRegistrationSource.DECLARED


class PersistedAsset(AssetMetadata):
    tenant_id: str = Field(alias="tenantId")
    resource_version: int = Field(alias="resourceVersion", ge=1)
    created_by: str = Field(alias="createdBy")
    updated_by: str = Field(alias="updatedBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class AssetObservationCreate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    asset: AssetMetadata
    access_mode: AssetAccessMode = Field(alias="accessMode")
    evidence_kind: LineageEvidenceKind = Field(
        default=LineageEvidenceKind.OBSERVED, alias="evidenceKind"
    )
    confidence: float = Field(default=1.0, ge=0, le=1)
    flow_id: str | None = Field(default=None, alias="flowId", max_length=255)
    execution_id: UUID | None = Field(default=None, alias="executionId")
    task_run_id: UUID | None = Field(default=None, alias="taskRunId")
    artifact_id: UUID | None = Field(default=None, alias="artifactId")
    metadata: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime | None = Field(default=None, alias="observedAt")


class AssetObservation(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    observation_id: UUID = Field(alias="observationId")
    asset_id: UUID = Field(alias="assetId")
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    access_mode: AssetAccessMode = Field(alias="accessMode")
    evidence_kind: LineageEvidenceKind = Field(alias="evidenceKind")
    confidence: float = Field(ge=0, le=1)
    flow_id: str | None = Field(default=None, alias="flowId")
    execution_id: UUID | None = Field(default=None, alias="executionId")
    task_run_id: UUID | None = Field(default=None, alias="taskRunId")
    artifact_id: UUID | None = Field(default=None, alias="artifactId")
    metadata: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime = Field(alias="observedAt")
    created_by: str = Field(alias="createdBy")


class AssetLineageDeclaration(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    upstream_asset_id: UUID = Field(alias="upstreamAssetId")
    downstream_asset_id: UUID = Field(alias="downstreamAssetId")
    evidence_kind: LineageEvidenceKind = Field(
        default=LineageEvidenceKind.DECLARED, alias="evidenceKind"
    )
    confidence: float = Field(default=1.0, ge=0, le=1)
    flow_id: str | None = Field(default=None, alias="flowId", max_length=255)
    execution_id: UUID | None = Field(default=None, alias="executionId")
    task_run_id: UUID | None = Field(default=None, alias="taskRunId")
    artifact_id: UUID | None = Field(default=None, alias="artifactId")
    metadata: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime | None = Field(default=None, alias="observedAt")


class AssetLineageEdge(AssetLineageDeclaration):
    edge_id: UUID = Field(alias="edgeId")
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    created_by: str = Field(alias="createdBy")
    observed_at: datetime = Field(alias="observedAt")


class AssetCatalogEntry(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    asset: PersistedAsset
    upstream: tuple[PersistedAsset, ...] = ()
    downstream: tuple[PersistedAsset, ...] = ()
    observations: tuple[AssetObservation, ...] = ()
    edges: tuple[AssetLineageEdge, ...] = ()


class AssetCatalogExport(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    format: str = "openlineage"
    generated_at: datetime = Field(alias="generatedAt")
    producer: str
    events: tuple[dict[str, Any], ...]


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

    async def get_asset(self, asset_id: UUID, *, tenant_id: str) -> PersistedAsset: ...

    async def record_asset_observation(
        self,
        observation: AssetObservationCreate,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> AssetObservation: ...

    async def declare_asset_lineage(
        self,
        declaration: AssetLineageDeclaration,
        *,
        tenant_id: str,
        namespace: str,
        actor_id: str,
    ) -> AssetLineageEdge: ...

    async def get_asset_catalog_entry(
        self, asset_id: UUID, *, tenant_id: str
    ) -> AssetCatalogEntry: ...

    async def export_asset_catalog(
        self, *, tenant_id: str, namespace: str | None = None
    ) -> AssetCatalogExport: ...
