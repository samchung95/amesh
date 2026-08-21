from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

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
