from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from amesh.domain import (
    CredentialMetadata,
    CredentialScope,
    ExecutionEvent,
    ExecutionSnapshot,
    NamespaceId,
    PermissionAction,
    PrincipalType,
    TenantPolicy,
    TenantSlug,
)
from amesh.executor import TaskCompletion
from amesh.ports import ExecutionInterventionAction, PersistedExecution, PersistedTaskRun


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadinessResponse(HealthResponse):
    database: str
    migrations_applied: int
    migrations_expected: int
    latest_migration: str | None = None
    error: str | None = None


class ProblemDetail(BaseModel):
    type: str
    title: str
    status: int
    detail: str | list[dict[str, Any]]
    code: str
    instance: str
    errors: list[dict[str, Any]] | None = None


class UiSessionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    principal_id: UUID = Field(alias="principalId")
    principal_type: PrincipalType = Field(alias="principalType")
    display: str
    tenant_id: str = Field(alias="tenantId")
    namespace: str | None = None
    capabilities: dict[str, bool]
    telemetry_enabled: bool = Field(alias="telemetryEnabled")
    server_version: str = Field(alias="serverVersion")


class LoginRequest(BaseModel):
    provider: str = Field(default="local", min_length=1, max_length=128)
    identifier: str = Field(min_length=1, max_length=255)
    password: SecretStr = Field(min_length=1, max_length=1024, repr=False)


class LoginResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    principal_id: UUID = Field(alias="principalId")
    display: str
    idle_expires_at: datetime = Field(alias="idleExpiresAt")
    absolute_expires_at: datetime = Field(alias="absoluteExpiresAt")


class SetLocalPasswordRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    new_password: SecretStr = Field(alias="newPassword", min_length=12, max_length=1024, repr=False)


class ChangeLocalPasswordRequest(SetLocalPasswordRequest):
    identifier: str = Field(min_length=1, max_length=255)
    current_password: SecretStr = Field(
        alias="currentPassword",
        min_length=1,
        max_length=1024,
        repr=False,
    )


class RevokedSessionsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    revoked_count: int = Field(alias="revokedCount", ge=0)


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


class BulkExecutionRequest(BaseModel):
    items: list[CreateExecutionRequest] = Field(min_length=1, max_length=100)


class BulkExecutionItemResult(BaseModel):
    index: int = Field(ge=0)
    status: int
    execution: ExecutionDetail | None = None
    error: ProblemDetail | None = None


class FlowGraphNode(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(alias="taskId")
    label: str
    task_type: str = Field(alias="taskType")
    order: int = Field(ge=0)
    depth: int = Field(ge=0)
    parent_id: str | None = Field(default=None, alias="parentId")
    dependencies: tuple[str, ...] = ()
    children: tuple[str, ...] = ()
    mode: str | None = None
    failure_policy: str = Field(alias="failurePolicy")
    max_concurrency: int | None = Field(default=None, alias="maxConcurrency")
    state: str | None = None
    result: dict[str, Any] | None = None
    iteration_count: int | None = Field(default=None, alias="iterationCount", ge=0)


class FlowGraphEdge(BaseModel):
    source: str
    target: str
    kind: Literal["contains", "dependsOn"]


class FlowGraph(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    namespace: str
    flow_id: str = Field(alias="flowId")
    revision: int = Field(ge=1)
    nodes: tuple[FlowGraphNode, ...]
    edges: tuple[FlowGraphEdge, ...]


class ResumeTaskRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resume_token: str = Field(alias="resumeToken", min_length=16, max_length=4096)
    completion: TaskCompletion


class ExecutionInterventionPreviewRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    action: ExecutionInterventionAction
    grace_seconds: float = Field(default=30, ge=0, alias="graceSeconds")
    checkpoint_task_id: str | None = Field(default=None, alias="checkpointTaskId")


class ExecutionInterventionRequest(ExecutionInterventionPreviewRequest):
    expected_version: int = Field(alias="expectedVersion", ge=0)
    expected_epoch: int = Field(alias="expectedEpoch", ge=1)
    reason: str = Field(min_length=1, max_length=1024)


class BackfillActionRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1024)


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


class IssueCredentialRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=128)
    scopes: tuple[CredentialScope, ...] = Field(min_length=1)
    audience: str = Field(default="amesh-api", min_length=1, max_length=128)
    expires_at: datetime = Field(alias="expiresAt")
    rate_limit_per_minute: int = Field(default=600, alias="rateLimitPerMinute", ge=1, le=1_000_000)


class IssuedCredentialResponse(BaseModel):
    metadata: CredentialMetadata
    token: str


class RotateCredentialRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    overlap_seconds: int = Field(default=300, alias="overlapSeconds", ge=0, le=86_400)


class ExchangeCredentialRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scopes: tuple[CredentialScope, ...] = Field(min_length=1)
    audience: str = Field(min_length=1, max_length=128)
    expires_in_seconds: int = Field(alias="expiresInSeconds", ge=1, le=3_600)
    rate_limit_per_minute: int = Field(default=600, alias="rateLimitPerMinute", ge=1, le=1_000_000)


class RevokedCredentialsResponse(BaseModel):
    revoked_count: int = Field(alias="revokedCount", ge=0)


class CreateTenantRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    slug: str
    display_name: str = Field(alias="displayName", min_length=1, max_length=255)
    policy: TenantPolicy = Field(default_factory=TenantPolicy)
