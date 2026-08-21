from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class TaskLogRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    level: str = Field(default="INFO", min_length=1, max_length=32)
    message: str
    fields: dict[str, Any] = Field(default_factory=dict)
    redacted: bool = False


class TaskMetricRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=256)
    value: Decimal
    unit: str | None = Field(default=None, max_length=64)
    labels: dict[str, str] = Field(default_factory=dict)


class TaskArtifactRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    uri: str = Field(min_length=1, max_length=4096)
    size_bytes: int = Field(alias="sizeBytes", ge=0)
    media_type: str | None = Field(default=None, alias="mediaType", max_length=255)


class TaskExitMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    status: str = Field(default="SUCCESS", min_length=1, max_length=64)
    code: int | None = None
    reason: str | None = Field(default=None, max_length=4096)
    duration_ms: float | None = Field(default=None, alias="durationMs", ge=0)


class TaskCompletion(BaseModel):
    model_config = ConfigDict(frozen=True)

    output: dict[str, Any] = Field(default_factory=dict)
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
    execution_id: str = Field(alias="executionId")
    task_run_id: str = Field(alias="taskRunId")
    attempt: int = Field(ge=1)
    task_type: str = Field(alias="taskType")
    secret_scopes: tuple[str, ...] = Field(alias="secretScopes")
    declared_files: dict[str, str] = Field(alias="declaredFiles")


class TaskContextResources(BaseModel):
    model_config = ConfigDict(frozen=True)

    secrets: dict[str, str] = Field(default_factory=dict)
    files: dict[str, str] = Field(default_factory=dict)


class TaskContextProvider(Protocol):
    async def resolve(self, request: TaskContextRequest) -> TaskContextResources: ...


TaskHandlerResult = dict[str, Any] | TaskCompletion | TaskDeferral
