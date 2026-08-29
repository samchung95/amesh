from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from amesh.config import ConfigurationSnapshot
from amesh.domain import (
    AgentContextReceipt,
    AgentHarnessPin,
    AgentSessionCounters,
    AgentSessionEvent,
    AgentSessionPhase,
    AgentSessionState,
    BlueprintDefinition,
    CredentialMetadata,
    CredentialScope,
    ExecutionEvent,
    ExecutionSnapshot,
    ExecutionState,
    FeatureFlag,
    FeatureFlagScope,
    FlowLifecycle,
    ModelDataEgress,
    NamespaceId,
    PermissionAction,
    PrincipalType,
    TenantPolicy,
    TenantSlug,
)
from amesh.dsl import CheckDefinition, FlowValidationResult
from amesh.dsl.models import RetryPolicy
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
    dependencies: dict[str, str] = Field(default_factory=dict)
    roles: dict[str, str] = Field(default_factory=dict)
    degraded_dependencies: tuple[str, ...] = ()
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


class McpConnectionDiscoveryRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    endpoint: str = Field(min_length=1, max_length=4096)
    credential_ref: str = Field(alias="credentialRef", min_length=1, max_length=255)
    timeout_seconds: float = Field(default=30, alias="timeoutSeconds", gt=0, le=300)


class McpConnectionTestStatus(StrEnum):
    PASSED = "PASSED"
    SCHEMA_DRIFT = "SCHEMA_DRIFT"
    UNAVAILABLE = "UNAVAILABLE"


class McpConnectionTestRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    revision: int = Field(ge=1)
    timeout_seconds: float = Field(default=30, alias="timeoutSeconds", gt=0, le=300)


class McpConnectionTestPin(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: str = Field(min_length=1, max_length=255)
    revision: int = Field(ge=1)
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class McpConnectionTestResponse(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    status: McpConnectionTestStatus
    evidence_id: UUID = Field(alias="evidenceId")
    connection_pin: McpConnectionTestPin = Field(alias="connectionPin")
    observed_digest: str | None = Field(
        default=None,
        alias="observedDigest",
        pattern=r"^sha256:[0-9a-f]{64}$",
    )
    checked_tool_count: int = Field(alias="checkedToolCount", ge=0)
    diagnostic: str | None = Field(default=None, max_length=4096)
    redacted: bool = True
    effect_boundary: Literal["DISCOVERY_ONLY"] = Field(
        default="DISCOVERY_ONLY",
        alias="effectBoundary",
    )


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
    component_health: dict[str, str] = Field(alias="componentHealth")
    version_matrix: dict[str, str] = Field(alias="versionMatrix")
    recent_errors: tuple[dict[str, Any], ...] = Field(alias="recentErrors")
    selected_metrics: dict[str, float] = Field(alias="selectedMetrics")


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


class ScimMember(BaseModel):
    value: UUID
    display: str | None = None


class ScimUserRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schemas: tuple[str, ...] = ("urn:ietf:params:scim:schemas:core:2.0:User",)
    external_id: str | None = Field(default=None, alias="externalId", max_length=2048)
    user_name: str = Field(alias="userName", min_length=1, max_length=128)
    display_name: str | None = Field(default=None, alias="displayName", max_length=255)
    active: bool = True


class ScimGroupRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schemas: tuple[str, ...] = ("urn:ietf:params:scim:schemas:core:2.0:Group",)
    external_id: str | None = Field(default=None, alias="externalId", max_length=2048)
    display_name: str = Field(alias="displayName", min_length=1, max_length=255)
    members: tuple[ScimMember, ...] = ()


class ScimPatchOperation(BaseModel):
    op: str = Field(min_length=3, max_length=16)
    path: str | None = Field(default=None, max_length=255)
    value: Any = None


class ScimPatchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schemas: tuple[str, ...] = ("urn:ietf:params:scim:api:messages:2.0:PatchOp",)
    operations: tuple[ScimPatchOperation, ...] = Field(alias="Operations", min_length=1)


class ScimResourceMeta(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_type: str = Field(alias="resourceType")
    created: datetime
    last_modified: datetime = Field(alias="lastModified")
    version: str
    location: str


class ScimUserResource(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schemas: tuple[str, ...] = ("urn:ietf:params:scim:schemas:core:2.0:User",)
    id: UUID
    external_id: str | None = Field(default=None, alias="externalId")
    user_name: str = Field(alias="userName")
    display_name: str = Field(alias="displayName")
    active: bool
    meta: ScimResourceMeta


class ScimGroupResource(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schemas: tuple[str, ...] = ("urn:ietf:params:scim:schemas:core:2.0:Group",)
    id: UUID
    external_id: str | None = Field(default=None, alias="externalId")
    display_name: str = Field(alias="displayName")
    members: tuple[ScimMember, ...] = ()
    meta: ScimResourceMeta


class ScimListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schemas: tuple[str, ...] = ("urn:ietf:params:scim:api:messages:2.0:ListResponse",)
    total_results: int = Field(alias="totalResults", ge=0)
    start_index: int = Field(default=1, alias="startIndex", ge=1)
    items_per_page: int = Field(alias="itemsPerPage", ge=0)
    resources: tuple[ScimUserResource | ScimGroupResource, ...] = Field(alias="Resources")


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
    flow_revision: int | None = Field(default=None, alias="flowRevision", ge=1)
    inputs: dict[str, Any] = Field(default_factory=dict)
    runner: RunnerMode = RunnerMode.LOCAL
    idempotency_key: str | None = Field(default=None, alias="idempotencyKey")
    cache_mode: TaskCacheMode = Field(default=TaskCacheMode.USE, alias="cacheMode")


class KestraExecutionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    inputs: dict[str, Any] = Field(default_factory=dict)
    runner: RunnerMode = RunnerMode.LOCAL
    idempotency_key: str | None = Field(default=None, alias="idempotencyKey")


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


class AgentSessionSummary(BaseModel):
    """Redacted session state safe for execution-scoped inspection."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: UUID = Field(alias="sessionId")
    tenant_id: str = Field(alias="tenantId")
    namespace: NamespaceId
    agent_ref: str | None = Field(default=None, alias="agentRef")
    model_profile: str | None = Field(default=None, alias="modelProfile")
    execution_id: UUID = Field(alias="executionId")
    task_run_id: UUID = Field(alias="taskRunId")
    attempt: int = Field(ge=1)
    capability_pin_id: UUID = Field(alias="capabilityPinId")
    envelope_digest: str = Field(alias="envelopeDigest")
    state: AgentSessionState
    phase: AgentSessionPhase
    version: int = Field(ge=0)
    counters: AgentSessionCounters
    harness: AgentHarnessPin | None = None
    context_receipt: AgentContextReceipt | None = Field(
        default=None,
        alias="contextReceipt",
    )
    final_result: dict[str, Any] | None = Field(default=None, alias="finalResult")
    error: str | None = Field(default=None, max_length=4096)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")


class AgentSessionDetailResponse(BaseModel):
    """Bounded, redacted session projection with resumable event pagination."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session: AgentSessionSummary
    events: tuple[AgentSessionEvent, ...]
    next_event_index: int | None = Field(default=None, alias="nextEventIndex", ge=1)


class AgentSessionCreateRequest(BaseModel):
    """Harness-neutral request for one bounded agent session."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    namespace: NamespaceId | None = None
    agent: str | None = Field(default=None, min_length=1, max_length=128)
    agent_revision: int | None = Field(default=None, alias="agentRevision", ge=1)
    agent_ref: str | None = Field(default=None, alias="agentRef", min_length=3, max_length=512)
    model_profile: str | None = Field(default=None, alias="modelProfile", max_length=512)
    harness: str | None = Field(default=None, min_length=1, max_length=64)
    budgets: dict[str, Any] | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    invalid_output_policy: Literal["FAIL", "REPAIR"] = Field(
        default="FAIL", alias="invalidOutputPolicy"
    )
    max_repair_attempts: int = Field(default=0, alias="maxRepairAttempts", ge=0, le=20)
    approval_task: str | None = Field(default=None, alias="approvalTask", max_length=128)
    data_handling: ModelDataEgress = Field(
        default=ModelDataEgress.DENY_SECRETS,
        alias="dataHandling",
    )
    business_assertions: tuple[dict[str, Any], ...] = Field(
        default=(), alias="businessAssertions", max_length=100
    )
    memory_read_keys: tuple[str, ...] = Field(default=(), alias="memoryReadKeys", max_length=100)
    memory_write_key: str | None = Field(
        default=None, alias="memoryWriteKey", min_length=1, max_length=128
    )
    timeout_seconds: float | None = Field(default=None, alias="timeoutSeconds", gt=0)
    retry: RetryPolicy = Field(default_factory=RetryPolicy)
    runner: RunnerMode = RunnerMode.LOCAL
    idempotency_key: str | None = Field(default=None, alias="idempotencyKey", max_length=256)

    @model_validator(mode="after")
    def normalize_agent_ref(self) -> AgentSessionCreateRequest:
        if self.agent_ref is not None:
            at = self.agent_ref.rfind("@")
            slash = self.agent_ref.rfind("/", 0, at)
            if at <= 0 or slash <= 0 or at == len(self.agent_ref) - 1:
                raise ValueError("agentRef must be <namespace>/<agent>@<revision>")
            try:
                revision = int(self.agent_ref[at + 1 :])
            except ValueError as exc:
                raise ValueError("agentRef revision must be an integer") from exc
            if revision < 1:
                raise ValueError("agentRef revision must be positive")
            if any(
                value is not None for value in (self.namespace, self.agent, self.agent_revision)
            ) and (
                self.namespace != self.agent_ref[:slash]
                or self.agent != self.agent_ref[slash + 1 : at]
                or self.agent_revision != revision
            ):
                raise ValueError("agentRef conflicts with namespace, agent, or agentRevision")
            return self.model_copy(
                update={
                    "namespace": self.agent_ref[:slash],
                    "agent": self.agent_ref[slash + 1 : at],
                    "agent_revision": revision,
                }
            )
        if self.namespace is None or self.agent is None or self.agent_revision is None:
            raise ValueError("agentRef or namespace, agent, and agentRevision is required")
        return self


class AgentSessionLaunchResponse(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: UUID = Field(alias="sessionId")
    execution_id: UUID = Field(alias="executionId")
    task_run_id: UUID = Field(alias="taskRunId")
    attempt: int = Field(default=1, ge=1)
    execution_state: ExecutionState = Field(alias="executionState")
    session: AgentSessionSummary | None = None


class AgentSessionControlSummary(BaseModel):
    """Provider-neutral control-room projection for standalone sessions."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: UUID = Field(alias="sessionId")
    tenant_id: str | None = Field(default=None, alias="tenantId")
    namespace: NamespaceId | None = None
    execution_id: UUID | None = Field(default=None, alias="executionId")
    task_run_id: UUID | None = Field(default=None, alias="taskRunId")
    attempt: int | None = Field(default=None, ge=1)
    capability_pin_id: UUID | None = Field(default=None, alias="capabilityPinId")
    envelope_digest: str | None = Field(default=None, alias="envelopeDigest")
    agent_ref: str | None = Field(default=None, alias="agentRef")
    model_profile: str | None = Field(default=None, alias="modelProfile")
    harness: AgentHarnessPin | None = None
    version: int | None = None
    execution_epoch: int | None = Field(default=None, alias="executionEpoch")
    state: Literal[
        "CREATED",
        "QUEUED",
        "RUNNING",
        "PAUSED",
        "CANCELLING",
        "CANCELLED",
        "SUCCEEDED",
        "FAILED",
        "WARNING",
        "RESTARTING",
    ]
    phase: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    counters: AgentSessionCounters | None = None
    budgets: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    final_result: dict[str, Any] | None = Field(default=None, alias="finalResult")
    error: str | None = None


class AgentSessionHarnessCatalogEntry(BaseModel):
    """Public harness metadata; operational commands and credentials are excluded."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    adapter: str
    adapter_version: str = Field(alias="adapterVersion")
    protocol: str


class AgentSessionServiceDetailResponse(BaseModel):
    """Control-room projection that remains available before an attempt starts."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session: AgentSessionControlSummary
    events: tuple[AgentSessionEvent, ...]
    next_event_index: int | None = Field(default=None, alias="nextEventIndex", ge=1)


class AgentSessionServiceItem(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: UUID = Field(alias="sessionId")
    attempt_session_id: UUID | None = Field(default=None, alias="attemptSessionId")
    session: AgentSessionControlSummary


class AgentSessionResultResponse(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: UUID = Field(alias="sessionId")
    state: Literal[
        "CREATED",
        "QUEUED",
        "RUNNING",
        "PAUSED",
        "CANCELLING",
        "CANCELLED",
        "SUCCEEDED",
        "FAILED",
        "WARNING",
        "RESTARTING",
    ]
    result: dict[str, Any] | None = None
    error: str | None = None


class AgentSessionControlRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    expected_version: int | None = Field(default=None, alias="expectedVersion", ge=0)
    expected_epoch: int | None = Field(default=None, alias="expectedEpoch", ge=1)
    reason: str = Field(
        default="Operator requested session control.", min_length=1, max_length=1024
    )
    grace_seconds: float = Field(default=30, ge=0, alias="graceSeconds")


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
    branch_id: str | None = Field(default=None, alias="branchId")
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
