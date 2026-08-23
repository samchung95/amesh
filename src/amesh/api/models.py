from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from amesh.config import ConfigurationSnapshot
from amesh.domain import (
    BlueprintDefinition,
    CredentialMetadata,
    CredentialScope,
    ExecutionEvent,
    ExecutionSnapshot,
    FeatureFlag,
    FeatureFlagScope,
    FlowLifecycle,
    NamespaceId,
    PermissionAction,
    PrincipalType,
    TenantPolicy,
    TenantSlug,
)
from amesh.dsl import CheckDefinition, FlowValidationResult
from amesh.executor import TaskCompletion
from amesh.ports import (
    CheckPolicySource,
    ExecutionEvidenceEvent,
    ExecutionInterventionAction,
    PersistedExecution,
    PersistedTaskRun,
    PersistedTaskRunSummary,
    TaskCacheMode,
)


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
    detail: Any
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


class FeatureFlagUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scope: FeatureFlagScope
    enabled: bool
    tenant_id: str | None = Field(default=None, alias="tenantId")
    namespace: str | None = None
    description: str = Field(default="", max_length=4096)
    expected_version: int | None = Field(default=None, alias="expectedVersion", ge=1)


class FlowRevisionLifecycleRequest(BaseModel):
    lifecycle: FlowLifecycle
    reason: str | None = Field(default=None, max_length=4096)


class FlowRevisionRestoreRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=4096)


class FlowDocumentExport(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    namespace: str
    flow_id: str = Field(alias="flowId")
    revision: int = Field(ge=1)
    semantic_hash: str = Field(alias="semanticHash")
    document: dict[str, Any]


class FlowEditorSchemaResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["amesh.flow-editor/v1"] = Field(alias="schemaVersion")
    flow_schema: dict[str, Any] = Field(alias="flowSchema")
    resource_catalog: dict[str, Any] = Field(alias="resourceCatalog")
    expression_context: dict[str, str] = Field(alias="expressionContext")


class FlowFormatResponse(BaseModel):
    document: str | None = None
    validation: FlowValidationResult


class ExpressionPreviewRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=65_536)
    context: dict[str, Any] = Field(default_factory=dict)


class ExpressionPreviewResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    result: Any
    redacted_context: dict[str, Any] = Field(alias="redactedContext")
    compatibility_version: str = Field(alias="compatibilityVersion")


class BlueprintDraftResponse(BaseModel):
    blueprint: BlueprintDefinition
    document: str
    validation: FlowValidationResult


class PlaygroundSimulationRequest(BaseModel):
    expression: str | None = Field(default=None, max_length=65_536)
    context: dict[str, Any] = Field(default_factory=dict)
    fragment: str | None = Field(default=None, max_length=131_072)

    @model_validator(mode="after")
    def require_subject(self) -> PlaygroundSimulationRequest:
        if not (self.expression and self.expression.strip()) and not (
            self.fragment and self.fragment.strip()
        ):
            raise ValueError("playground requires an expression or flow fragment")
        return self


class PlaygroundStep(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(alias="taskId")
    task_type: str = Field(alias="taskType")
    dependencies: tuple[str, ...]
    simulated: bool
    reason: str


class PlaygroundSafety(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    persisted: bool = False
    executed: bool = False
    credential_access: bool = Field(default=False, alias="credentialAccess")
    infrastructure_access: bool = Field(default=False, alias="infrastructureAccess")


class PlaygroundSimulationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    expression_result: Any = Field(default=None, alias="expressionResult")
    redacted_context: dict[str, Any] = Field(default_factory=dict, alias="redactedContext")
    validation: FlowValidationResult | None = None
    steps: tuple[PlaygroundStep, ...] = ()
    safety: PlaygroundSafety = Field(default_factory=PlaygroundSafety)
    compatibility_version: str = Field(alias="compatibilityVersion")


class ConfigurationDiagnosticBundle(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: int = Field(default=1, alias="schemaVersion")
    generated_at: datetime = Field(alias="generatedAt")
    tenant_id: str = Field(alias="tenantId")
    namespace: str | None = None
    configuration: ConfigurationSnapshot
    feature_flags: tuple[FeatureFlag, ...] = Field(alias="featureFlags")


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
    DOCKER = "docker"
    KUBERNETES = "kubernetes"


class CreateExecutionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    namespace: str
    flow_id: str = Field(alias="flowId")
    inputs: dict[str, Any] = Field(default_factory=dict)
    runner: RunnerMode = RunnerMode.LOCAL
    idempotency_key: str | None = Field(default=None, alias="idempotencyKey")
    cache_mode: TaskCacheMode = Field(default=TaskCacheMode.USE, alias="cacheMode")


class TaskCachePurgeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key_prefix: str | None = Field(default=None, alias="keyPrefix", min_length=1, max_length=1024)
    namespace: str | None = Field(default=None, min_length=1, max_length=255)
    flow_id: str | None = Field(default=None, alias="flowId", min_length=1, max_length=128)
    task_id: str | None = Field(default=None, alias="taskId", min_length=1, max_length=128)
    reason: str = Field(min_length=1, max_length=4096)

    @model_validator(mode="after")
    def require_scope(self) -> TaskCachePurgeRequest:
        if not any((self.key_prefix, self.namespace, self.flow_id, self.task_id)):
            raise ValueError("cache purge requires keyPrefix or a resource scope")
        return self


class TriggerActionRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=4096)


class ExecutionDetail(BaseModel):
    execution: PersistedExecution
    task_runs: list[PersistedTaskRun] = Field(alias="taskRuns")
    task_run_summary: PersistedTaskRunSummary | None = Field(
        default=None,
        alias="taskRunSummary",
    )
    task_run_offset: int = Field(default=0, alias="taskRunOffset", ge=0)


class FlowDataContract(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    namespace: str
    flow_id: str = Field(alias="flowId")
    revision: int = Field(ge=1)
    input_schema: dict[str, Any] = Field(alias="inputSchema")
    outputs: dict[str, Any] = Field(default_factory=dict)
    variables: dict[str, Any] = Field(default_factory=dict)


class FlowMetadataResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    namespace: str
    flow_id: str = Field(alias="flowId")
    revision: int = Field(ge=1)
    labels: dict[str, str]
    plugin_resolution: dict[str, Any] = Field(alias="pluginResolution")


class NamespaceFileMoveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    destination_path: str = Field(alias="destinationPath", min_length=1, max_length=1024)
    expected_version: int | None = Field(default=None, alias="expectedVersion", ge=0)


class NamespaceResourceImportResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    files: int = Field(ge=0)
    key_values: int = Field(alias="keyValues", ge=0)
    secret_bindings: int = Field(alias="secretBindings", ge=0)


class ExecutionEvidencePage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ExecutionEvidenceEvent]
    next_cursor: str | None = Field(default=None, alias="nextCursor")


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
    lifecycle_phase: str = Field(default="MAIN", alias="lifecyclePhase")
    handler_owner_id: str | None = Field(default=None, alias="handlerOwnerId")


class FlowGraphEdge(BaseModel):
    source: str
    target: str
    kind: Literal["contains", "dependsOn", "handles"]


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


class CheckPolicyUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: CheckPolicySource = CheckPolicySource.NAMESPACE
    task_type: str | None = Field(default=None, alias="taskType", max_length=256)
    definition: CheckDefinition
    enabled: bool = True


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
