from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Protocol
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

from amesh.ports import LogLevel, LogSourceStream, MetricKind


class TaskLogRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    level: LogLevel = LogLevel.INFO
    logger: str = Field(default="task", min_length=1, max_length=256)
    message: str
    fields: dict[str, Any] = Field(default_factory=dict)
    source_stream: LogSourceStream = Field(default=LogSourceStream.TASK, alias="sourceStream")
    trace_id: str | None = Field(default=None, alias="traceId", max_length=256)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="occurredAt")
    redacted: bool = False


class TaskMetricRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=256)
    kind: MetricKind = MetricKind.GAUGE
    value: Decimal
    unit: str | None = Field(default=None, max_length=64)
    labels: dict[str, str] = Field(default_factory=dict)


class TaskArtifactRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    uri: str = Field(min_length=1, max_length=4096)
    size_bytes: int = Field(alias="sizeBytes", ge=0)
    media_type: str | None = Field(default=None, alias="mediaType", max_length=255)
    checksum_sha256: str | None = Field(
        default=None,
        alias="checksumSha256",
        pattern=r"^[0-9a-f]{64}$",
    )

    @field_validator("uri")
    @classmethod
    def require_internal_storage_uri(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"s3", "azure", "gs"}
            or not parsed.netloc
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("artifact URI must use internal object storage")
        return value


class TaskExitMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    status: str = Field(default="SUCCESS", min_length=1, max_length=64)
    code: int | None = None
    reason: str | None = Field(default=None, max_length=4096)
    duration_ms: float | None = Field(default=None, alias="durationMs", ge=0)


class TaskCompletion(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    output: dict[str, Any] = Field(default_factory=dict)
    sensitive_output_keys: tuple[str, ...] = Field(default=(), alias="sensitiveOutputKeys")
    logs: tuple[TaskLogRecord, ...] = ()
    metrics: tuple[TaskMetricRecord, ...] = ()
    artifacts: tuple[TaskArtifactRecord, ...] = ()
    exit: TaskExitMetadata = Field(default_factory=TaskExitMetadata)


class TaskDeferral(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    resume_token: str = Field(alias="resumeToken", min_length=16, max_length=4096)
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskContextRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    tenant_id: str = Field(alias="tenantId")
    namespace: str
    execution_id: str = Field(alias="executionId")
    task_run_id: str = Field(alias="taskRunId")
    attempt: int = Field(ge=1)
    task_type: str = Field(alias="taskType")
    secret_scopes: tuple[str, ...] = Field(alias="secretScopes")
    declared_files: dict[str, str] = Field(alias="declaredFiles")
    key_values_required: bool = Field(default=False, alias="keyValuesRequired")


class TaskContextResources(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    secrets: dict[str, str] = Field(default_factory=dict)
    files: dict[str, str] = Field(default_factory=dict)
    key_values: dict[str, Any] = Field(default_factory=dict, alias="keyValues")


class TaskContextProvider(Protocol):
    async def resolve(self, request: TaskContextRequest) -> TaskContextResources: ...


TaskHandlerResult = dict[str, Any] | TaskCompletion | TaskDeferral
