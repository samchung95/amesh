from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain import (
    ExecutionEvent,
    ExecutionSnapshot,
    NamespaceId,
    PermissionAction,
    PrincipalType,
    TenantSlug,
)
from amesh.ports import PersistedExecution, PersistedTaskRun


class HealthResponse(BaseModel):
    status: str
    version: str


class ReduceExecutionRequest(BaseModel):
    snapshot: ExecutionSnapshot
    events: list[ExecutionEvent] = Field(min_length=1)


class ReduceExecutionResponse(BaseModel):
    snapshot: ExecutionSnapshot
    duplicate_events_ignored: int = 0


class RunnerMode(StrEnum):
    LOCAL = "local"
    KUBERNETES = "kubernetes"


class CreateExecutionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    namespace: str
    flow_id: str = Field(alias="flowId")
    inputs: dict[str, Any] = Field(default_factory=dict)
    runner: RunnerMode = RunnerMode.LOCAL
    idempotency_key: str | None = Field(default=None, alias="idempotencyKey")


class ExecutionDetail(BaseModel):
    execution: PersistedExecution
    task_runs: list[PersistedTaskRun] = Field(alias="taskRuns")


class TaskLog(BaseModel):
    task_id: str = Field(alias="taskId")
    attempt: int
    state: str
    output: dict[str, Any] | None = None


class AuthorizationExplanationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    principal_id: UUID = Field(alias="principalId")
    principal_type: PrincipalType = Field(alias="principalType")
    tenant_id: TenantSlug | None = Field(default=None, alias="tenantId")
    namespace: NamespaceId | None = None
    resource_type: str = Field(alias="resourceType", min_length=1, max_length=128)
    action: PermissionAction
