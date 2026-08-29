from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import secrets
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from contextlib import asynccontextmanager, suppress
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from http import HTTPStatus
from pathlib import Path
from time import perf_counter
from typing import Annotated, Any, Literal, NoReturn
from urllib.parse import parse_qs
from uuid import NAMESPACE_URL, UUID, uuid5

import yaml
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi import Path as PathParameter
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from opentelemetry.trace import SpanKind
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse, PlainTextResponse, RedirectResponse, StreamingResponse

from amesh import __version__
from amesh.adapters.agent_session_registry import (
    AGENT_SESSION_HARNESS_REGISTRY,
    create_agent_session_harness,
)
from amesh.adapters.docker import DockerContainerRunner
from amesh.adapters.kubernetes import KubernetesJobRunner, ProfiledKubernetesJobRunner
from amesh.adapters.local import LocalProcessRunner
from amesh.adapters.openai_session import (
    CanonicalSessionRequest,
    CanonicalSessionResult,
    HarnessProvenance,
    OpenAIChatCompletionRequest,
    OpenAIChatCompletionResponse,
    OpenAICompatibleSessionAdapter,
    OpenAIResponse,
    OpenAIResponseRequest,
    openai_response_sse_events,
    openai_sse_events,
)
from amesh.adapters.postgres import (
    PostgresAdmissionPolicyRepository,
    PostgresAgentMemoryRepository,
    PostgresAgentPrimitiveRepository,
    PostgresAgentResourceRepository,
    PostgresAgentSessionRepository,
    PostgresAuditRepository,
    PostgresAuthenticationRepository,
    PostgresAuthorizationRepository,
    PostgresBackfillRepository,
    PostgresCheckRepository,
    PostgresCredentialRepository,
    PostgresDashboardRepository,
    PostgresEvidenceBundleRepository,
    PostgresExecutionRepository,
    PostgresFeatureFlagRepository,
    PostgresFederationRepository,
    PostgresFlowTestRepository,
    PostgresHumanTaskRepository,
    PostgresMetadataRepository,
    PostgresOperationalControlRepository,
    PostgresPluginPolicyRepository,
    PostgresPromotionRepository,
    PostgresRealtimeRepository,
    PostgresReconciliationRepository,
    PostgresRetentionRepository,
    PostgresSearchRepository,
    PostgresServiceRegistryRepository,
    PostgresSharedResourceRepository,
    PostgresTaskCacheRepository,
    PostgresTenantRepository,
    PostgresTriggerRuntimeRepository,
    PostgresUpgradeRepository,
    PostgresWorkerRepository,
)
from amesh.adapters.postgres.human_task_repository import (
    HumanTaskConflict,
    WorkflowAppVersionConflict,
)
from amesh.adapters.postgres.operational_control_repository import (
    OperationalControlVersionConflict,
)
from amesh.admission_policy import AdmissionPolicyService, policy_input_from_flow
from amesh.api.contracts import (
    CollectionQuery,
    _decode_cursor,
    _encode_cursor,
    collection_response,
    default_limited_collection_query,
)
from amesh.api.evidence_models import EvidenceBundlePageResponse
from amesh.api.models import (
    AgentSessionControlRequest,
    AgentSessionControlSummary,
    AgentSessionCreateRequest,
    AgentSessionDetailResponse,
    AgentSessionHarnessCatalogEntry,
    AgentSessionLaunchResponse,
    AgentSessionResultResponse,
    AgentSessionServiceDetailResponse,
    AgentSessionServiceItem,
    AgentSessionSummary,
    AuthorizationExplanationRequest,
    BackfillActionRequest,
    BlueprintDraftResponse,
    BulkExecutionItemResult,
    BulkExecutionRequest,
    ChangeLocalPasswordRequest,
    CheckPolicyUpsertRequest,
    ConfigurationDiagnosticBundle,
    CreateExecutionRequest,
    CreateTenantRequest,
    ExchangeCredentialRequest,
    ExecutionDetail,
    ExecutionEvidencePage,
    ExecutionInterventionPreviewRequest,
    ExecutionInterventionRequest,
    ExpressionPreviewRequest,
    ExpressionPreviewResponse,
    FeatureFlagUpsertRequest,
    FlowDataContract,
    FlowDocumentExport,
    FlowEditorSchemaResponse,
    FlowFormatResponse,
    FlowGraph,
    FlowGraphEdge,
    FlowGraphNode,
    FlowMetadataResponse,
    FlowRevisionLifecycleRequest,
    FlowRevisionRestoreRequest,
    HealthResponse,
    IssueCredentialRequest,
    IssuedCredentialResponse,
    KestraExecutionRequest,
    LoginRequest,
    LoginResponse,
    McpConnectionDiscoveryRequest,
    McpConnectionTestPin,
    McpConnectionTestRequest,
    McpConnectionTestResponse,
    McpConnectionTestStatus,
    NamespaceFileMoveRequest,
    NamespaceResourceImportResult,
    PlaygroundSafety,
    PlaygroundSimulationRequest,
    PlaygroundSimulationResponse,
    PlaygroundStep,
    ProblemDetail,
    ReadinessResponse,
    ReduceExecutionRequest,
    ReduceExecutionResponse,
    ResumeTaskRequest,
    RevokedCredentialsResponse,
    RevokedSessionsResponse,
    RotateCredentialRequest,
    RunnerMode,
    ScimGroupRequest,
    ScimGroupResource,
    ScimListResponse,
    ScimMember,
    ScimPatchRequest,
    ScimResourceMeta,
    ScimUserRequest,
    ScimUserResource,
    SetLocalPasswordRequest,
    TaskCachePurgeRequest,
    TaskLog,
    TriggerActionRequest,
    UiSessionResponse,
)
from amesh.api.promotion import build_promotion_router
from amesh.audit import AuditArtifact, AuditArtifactService
from amesh.authentication import (
    AuthenticationRateLimited,
    AuthenticationService,
    InvalidAuthentication,
    InvalidCsrf,
    LocalAuthenticationDisabled,
    PasswordPolicyError,
)
from amesh.authorization import AuthorizationDenied, AuthorizationService
from amesh.backfills import BackfillService
from amesh.capability_catalog import (
    CapabilityCatalog,
    CapabilityKind,
    CapabilitySource,
    CapabilitySourceAccess,
    CapabilitySourceAccessStatus,
    CapabilityStatus,
    build_capability_catalog,
    filter_capability_catalog,
)
from amesh.config import (
    ConfigurationLoadError,
    ConfigurationManager,
    ConfigurationSnapshot,
    NonReloadableConfigurationChanged,
    ScimProviderConfig,
    Settings,
    get_configuration_manager,
    get_settings,
)
from amesh.credentials import CredentialOperationError, CredentialService, InvalidCredential
from amesh.dashboards import (
    apply_dashboard_filters,
    builtin_dashboard,
    builtin_dashboards,
    can_edit_dashboard,
    can_view_dashboard,
)
from amesh.database import create_database_engine
from amesh.determinism import DeterminismPolicyPin
from amesh.domain import (
    ActorContext,
    AdministrationApplyRequest,
    AdministrationApprovalError,
    AdministrationAuditEntry,
    AdministrationControl,
    AdministrationControlDraft,
    AdministrationControlKey,
    AdministrationImpactPreview,
    AdmissionBehavior,
    AdmissionDecision,
    AdmissionDiagnostics,
    AdmissionResourceType,
    AdmissionScope,
    AgentCapabilityPin,
    AgentEnvelopePreview,
    AgentEvaluationPreview,
    AgentEvaluationSpec,
    AgentHarnessPin,
    AgentMemoryMetadata,
    AgentResolutionRequest,
    AgentResourceKind,
    AgentResourceRevision,
    AgentResourceSpec,
    AgentRevisionComparison,
    AgentRouteDecision,
    AgentRouteRequest,
    AgentSessionDetail,
    AgentSessionState,
    Announcement,
    AnnouncementAudience,
    AnnouncementCreateRequest,
    ArtifactRef,
    AuditEventPage,
    AuditExportDestination,
    AuditExportFormat,
    AuditExportReceipt,
    AuditExportRequest,
    AuditIntegrityReport,
    AuditLegalHold,
    AuditLegalHoldCreate,
    AuditRetentionPolicy,
    AuditRetentionPolicyUpdate,
    AuditRetentionResult,
    AuthenticationProviderDescriptor,
    AuthorizationDecision,
    AuthorizationRequest,
    BackfillPreview,
    BackfillRecord,
    BackfillSpec,
    BackfillState,
    BlueprintCatalogSource,
    BlueprintDefinition,
    BlueprintInstantiationRequest,
    BlueprintSummary,
    ComplianceEvidenceCreate,
    ComplianceEvidenceRecord,
    CompliancePackageRequest,
    ConcurrencyLimit,
    ConfigurationMigration,
    ConfigurationMigrationRequest,
    CredentialMetadata,
    DashboardDataSource,
    DashboardDefinition,
    DashboardFilters,
    DashboardQuery,
    DashboardQueryResult,
    DashboardRender,
    DashboardSpec,
    DashboardWidgetResult,
    EffectiveCapabilityEnvelope,
    EffectivePluginPolicy,
    ExecutionState,
    FeatureFlag,
    FeatureFlagDecision,
    FeatureFlagScope,
    FlowLifecycle,
    FlowRevisionDiff,
    FlowRevisionRecord,
    FlowRevisionSource,
    FlowTestDefinition,
    FlowTestDefinitionCreateRequest,
    FlowTestQualityGate,
    FlowTestQualityGateUpdate,
    FlowTestRunRequest,
    FlowTestRunResult,
    InvalidTransition,
    IssuedBrowserSession,
    IssuedCredential,
    KeyValueChange,
    KeyValueEntry,
    KeyValueWrite,
    McpConnectionRevision,
    McpConnectionSpec,
    McpDiscoveryResult,
    ModelPolicySpec,
    NamespaceAuthorizationBoundary,
    NamespaceFile,
    NamespaceFileVersion,
    NamespaceResourceBundle,
    OperationalBoundary,
    OperationalControl,
    OperationalControlActionRequest,
    OperationalControlCreateRequest,
    OperationalControlEvent,
    OperationalControlScope,
    PermissionAction,
    PersistedEventMigration,
    PersistedEventMigrationRequest,
    PluginPolicyDecision,
    PluginPolicyImpactPreview,
    PluginPolicyRule,
    PluginPolicyRuleCreate,
    PluginPolicyScope,
    PluginPolicyStage,
    PluginQuarantine,
    PluginQuarantineCreate,
    PolicyDecision,
    PolicyDocument,
    PolicyEvaluationRequest,
    PolicyFixture,
    PolicyFixtureResult,
    PolicyRevision,
    PolicyScope,
    PolicyStage,
    PrincipalDefinition,
    PrincipalType,
    ProviderMigrationDiagnostic,
    ReconciliationRequest,
    ReconciliationRun,
    ResourceVersionConflict,
    RoleBinding,
    RoleDefinition,
    ScimResourceRecord,
    SearchDocumentType,
    SearchProjectionControlRequest,
    SearchProjectionStatus,
    SearchProjectionVerification,
    SearchRebuildRequest,
    SearchRequest,
    SearchResponse,
    SecretBinding,
    SecretBindingWrite,
    ServiceDrainRequest,
    ServiceInstance,
    ServiceLiveness,
    ServiceRole,
    ServiceState,
    ServiceTopology,
    TenantDefinition,
    TenantExport,
    TenantPolicy,
    TenantSlug,
    UpgradePolicy,
    UpgradeReport,
    UpgradeReportRequest,
    administration_control_flag,
    administration_controls,
    canonical_hash,
    compare_agent_revisions,
    evaluate_deterministic_output,
    get_blueprint,
    instantiate_blueprint,
    issue_administration_preview,
    list_blueprints,
    new_runtime_id,
    provider_migration_diagnostic,
    reduce_execution,
    route_agent,
    verify_administration_approval,
)
from amesh.domain import (
    AuthenticationRequest as ProviderAuthenticationRequest,
)
from amesh.domain.flow_revisions import compare_flow_revisions
from amesh.domain.human_tasks import (
    HumanTask,
    HumanTaskActionRequest,
    HumanTaskNotification,
    WorkflowApp,
    WorkflowAppLaunchRequest,
    WorkflowAppSpec,
    WorkflowAppUpsertRequest,
    form_from_flow,
)
from amesh.domain.retention import (
    LifecycleExecuteRequest,
    LifecycleJob,
    LifecycleLegalHold,
    LifecycleLegalHoldDraft,
    LifecyclePolicy,
    LifecyclePolicyDraft,
    LifecyclePreviewRequest,
    LifecycleScope,
)
from amesh.domain.runner import RunnerId, RunnerPolicySet, RunnerPolicyViolation
from amesh.dsl import (
    FlowDefinition,
    FlowDocumentError,
    FlowValidationResult,
    TaskDefinition,
    compile_execution_tasks,
    validate_flow_document,
)
from amesh.evidence_bundle import (
    EvidenceConflictError,
    EvidenceNotFoundError,
    EvidenceUnavailableError,
    FilesystemEvidenceObjectStore,
)
from amesh.executor import (
    InProcessExecutor,
    SubflowCoordinator,
    TaskHandler,
    TaskResourceLimitError,
    docker_container_handler,
    kubernetes_job_handler,
    local_process_handler,
    normalize_task_completion,
    preview_execution_intervention,
    required_runner_ids,
    selecting_runner_handler,
    subflow_task_handler,
)
from amesh.expressions import NativeExpressionEngine
from amesh.expressions.contracts import ExpressionError
from amesh.external_orchestration import (
    ExternalOrchestrationProfile,
    correlation_id_is_valid,
    error_category,
    external_orchestration_profile,
)
from amesh.federation import (
    FederationProviderUnavailable,
    FederationRejected,
    IdentityFederationService,
    LdapAuthenticationProvider,
)
from amesh.flow_testing import FlowTestService
from amesh.frontend import SpaStaticFiles, find_frontend_dist
from amesh.human_tasks import HumanTaskService, approval_task_handler
from amesh.kestra_compatibility import (
    KestraFlowImport,
    compatibility_manifest,
    import_kestra_flow,
)
from amesh.mcp_server import create_amesh_mcp_application, create_amesh_mcp_server
from amesh.model_continuations import (
    configured_model_continuation_protector,
    configured_trigger_payload_protector,
)
from amesh.networking import (
    ForwardedHeaderRejected,
    NetworkDiagnosticBundle,
    apply_trusted_forwarded_headers,
    build_network_diagnostics,
)
from amesh.observability import (
    ADMISSION_PRESSURE,
    HTTP_REQUEST_DURATION,
    HTTP_REQUESTS,
    configure_observability,
    diagnostic_metric_samples,
    instrument_database,
    observe_operation,
    propagated_trace_context,
    recent_redacted_logs,
)
from amesh.plugin_sdk import (
    PluginCatalogManager,
    PluginCatalogSnapshot,
    PluginContractError,
    PluginRegistryIndex,
    PluginRegistryPackage,
    PluginRegistryPublishRequest,
    PluginRegistryYankRequest,
    PluginResolver,
)
from amesh.plugins import (
    IsolatedPluginRuntime,
    IsolatedPluginRuntimeSnapshot,
    PluginPolicyDenied,
    PluginPolicyService,
    SelfHostedPluginRegistry,
    TrustedPluginRuntime,
    TrustedPluginRuntimeSnapshot,
    build_isolated_runtime,
    build_plugin_catalog,
    build_trusted_runtime,
)
from amesh.ports import (
    AssetCatalogEntry,
    AssetCatalogExport,
    AssetLineageDeclaration,
    AssetLineageEdge,
    AssetMetadata,
    AssetObservation,
    AssetObservationCreate,
    CheckComplianceSummary,
    CheckEvaluation,
    CheckOutcome,
    CredentialRateLimitExceeded,
    ExecutionArtifact,
    ExecutionEvidenceEvent,
    ExecutionInterventionAction,
    ExecutionInterventionPreview,
    ExecutionInterventionRecord,
    ExecutionLaunchSource,
    ExecutionStateConflictError,
    FeatureFlagVersionConflict,
    FlowTestVersionConflict,
    LastAdministratorError,
    MetadataVersionConflict,
    NamespaceCheckPolicy,
    PersistedAsset,
    PersistedExecution,
    PersistedFlow,
    PersistedIterationSummary,
    PersistedSubflow,
    PersistedTaskRun,
    PersistedTaskRunSummary,
    ReconciliationAlreadyRunningError,
    RunnerCapabilities,
    ServiceFenceError,
    TaskCacheEntry,
    TaskCachePurgeResult,
    TaskStateConflictError,
    TenantQuotaExceeded,
    TenantUnavailableError,
    TriggerOccurrence,
    TriggerOccurrenceState,
    TriggerRuntimeState,
    WorkerFenceError,
    WorkerInventory,
)
from amesh.ports.dashboard_repository import DashboardQueryTimeout, DashboardVersionConflict
from amesh.ports.federation_repository import (
    AmbiguousFederatedIdentity,
    FederationReplayRejected,
    FederationStateRejected,
)
from amesh.ports.search_repository import SearchCursorError, SearchUnavailableError
from amesh.preflight import DependencyCondition, run_preflight
from amesh.promotion import PromotionService
from amesh.quality import (
    ConfigurationPin,
    DurableDifferentialService,
    PostgresDifferentialShadowRepository,
    RunObservation,
    ShadowRunContext,
    build_differential_application_router,
)
from amesh.realtime import (
    ProvisionedWebhookSubscription,
    RealtimeEvent,
    RealtimeEventPage,
    RealtimeFilter,
    RealtimeSeverity,
    WebhookDelivery,
    WebhookDeliveryHistory,
    WebhookSubscription,
    WebhookSubscriptionCreate,
    derive_webhook_secret,
    redact_realtime_payload,
)
from amesh.reconciliation import ReconciliationService
from amesh.retention import RetentionService
from amesh.scheduler import CronScheduler, SchedulePreview
from amesh.simulation import (
    SimulationComparison,
    SimulationPlan,
    SimulationPolicyDecision,
    SimulationRequest,
    compare_simulation_plans,
    simulate_flow,
)
from amesh.storage.factory import build_object_store
from amesh.tasks import (
    HttpTaskPolicy,
    agent_llm_handler,
    agent_mcp_handler,
    agent_mesh_handlers,
    agent_session_handler,
    core_utility_handlers,
    discover_mcp_server,
    script_task_handlers,
)
from amesh.tasks.http import validate_http_destination
from amesh.tenancy import TenantService
from amesh.upgrade import UpgradeService
from amesh.workflow.data_contracts import (
    DataContractError,
    flow_input_contract,
    redact_matching_values,
    redact_sensitive_inputs,
    redact_sensitive_outputs,
    sensitive_execution_values,
    stage_file_inputs,
    validate_flow_inputs,
)
from amesh.workflow.metadata import (
    NamespaceWorkflowMetadata,
    NamespaceWorkflowMetadataUpdate,
    NamespaceWorkflowMetadataView,
)
from amesh.workflow.shared_resources import (
    NamespaceResourceService,
    SharedResourceContextProvider,
)
from amesh.workflow.working_directory import WorkingDirectoryManager

LOGGER = logging.getLogger("amesh.api")

_EDITOR_CONTEXT_KEYS = frozenset(
    {
        "flow",
        "execution",
        "task",
        "taskrun",
        "trigger",
        "inputs",
        "outputs",
        "vars",
        "labels",
        "namespace",
        "iteration",
        "error",
    }
)
_SENSITIVE_EDITOR_KEY_PARTS = frozenset(
    {"password", "secret", "token", "credential", "api_key", "apikey"}
)


def _redact_editor_context(context: Mapping[str, object]) -> dict[str, object]:
    def sanitize(value: object) -> object:
        if isinstance(value, Mapping):
            return {
                str(key): (
                    "[REDACTED]"
                    if any(
                        part in str(key).lower().replace("-", "_")
                        for part in _SENSITIVE_EDITOR_KEY_PARTS
                    )
                    else sanitize(item)
                )
                for key, item in value.items()
            }
        if isinstance(value, list | tuple):
            return [sanitize(item) for item in value]
        return value

    return {key: sanitize(value) for key, value in context.items() if key in _EDITOR_CONTEXT_KEYS}


def _playground_flow(fragment: str) -> dict[str, object]:
    try:
        loaded = yaml.safe_load(fragment)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid playground YAML: {exc}") from exc
    if isinstance(loaded, list):
        document: dict[str, object] = {"tasks": loaded}
    elif isinstance(loaded, dict) and "tasks" in loaded:
        document = dict(loaded)
    elif isinstance(loaded, dict) and {"id", "type"} <= loaded.keys():
        document = {"tasks": [loaded]}
    else:
        raise ValueError("flow fragment must be a task, a task list, or a flow with tasks")
    document.setdefault("apiVersion", "amesh.flow/v1")
    document.setdefault("id", "playground_preview")
    document.setdefault("namespace", "playground.local")
    return document


def _playground_steps(document: Mapping[str, object]) -> tuple[PlaygroundStep, ...]:
    tasks = document.get("tasks", [])
    if not isinstance(tasks, list):
        return ()
    deterministic_types = {"core.log", "core.return"}
    return tuple(
        PlaygroundStep(
            taskId=str(task.get("id", "unknown")),
            taskType=str(task.get("type", "unknown")),
            dependencies=tuple(str(value) for value in task.get("dependsOn", [])),
            simulated=task.get("type") in deterministic_types,
            reason=(
                "deterministic local preview"
                if task.get("type") in deterministic_types
                else "validated only; the playground never invokes this resource"
            ),
        )
        for task in tasks
        if isinstance(task, dict)
    )


_AMESH_MCP_APPLICATION: Starlette | None = None


@asynccontextmanager
async def _application_lifespan(_: FastAPI) -> AsyncIterator[None]:
    if _AMESH_MCP_APPLICATION is None:
        yield
        return
    async with _AMESH_MCP_APPLICATION.router.lifespan_context(_AMESH_MCP_APPLICATION):
        yield


app = FastAPI(
    title="AMESH",
    version=__version__,
    description=(
        "Clean-room durable workflow MVP with validated flow management, "
        "execution control, webhook triggers and execution logs."
    ),
    lifespan=_application_lifespan,
)


@app.get(
    "/api/v1/orchestration/profile",
    response_model=ExternalOrchestrationProfile,
    tags=["external-orchestration"],
)
async def get_external_orchestration_profile() -> ExternalOrchestrationProfile:
    """Publish the client-neutral contract without exposing tenant data."""

    return external_orchestration_profile()


def _problem_response(
    request: Request,
    *,
    status_code: int,
    detail: str | list[dict[str, object]],
    code: str | None = None,
    headers: Mapping[str, str] | None = None,
    errors: object | None = None,
) -> JSONResponse:
    title = HTTPStatus(status_code).phrase
    problem_code = code or f"HTTP_{status_code}"
    content: dict[str, object] = {
        "type": f"urn:amesh:problem:{problem_code.lower()}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "code": problem_code,
        "instance": request.url.path,
    }
    if errors is not None:
        content["errors"] = errors
    response_headers = dict(headers or {})
    response_headers.setdefault(
        "X-Amesh-Error-Category",
        error_category(status_code, problem_code),
    )
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=response_headers,
        media_type="application/problem+json",
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, (str, list)) else str(exc.detail)
    if request.url.path.startswith("/v1/"):
        return _openai_error_response(
            status_code=exc.status_code,
            message=str(detail),
            code=None,
            headers=exc.headers,
        )
    return _problem_response(
        request,
        status_code=exc.status_code,
        detail=detail,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    if request.url.path.startswith("/v1/"):
        return _openai_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Request validation failed",
            code="REQUEST_VALIDATION_FAILED",
        )
    return _problem_response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Request validation failed",
        code="REQUEST_VALIDATION_FAILED",
        errors=jsonable_encoder(exc.errors()),
    )


def _openai_error_response(
    *,
    status_code: int,
    message: str,
    code: str | None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "type": "invalid_request_error" if status_code < 500 else "server_error",
                "param": None,
                "code": code,
            }
        },
        headers=headers,
    )


@app.exception_handler(TenantUnavailableError)
async def tenant_unavailable_handler(
    request: Request,
    exc: TenantUnavailableError,
) -> JSONResponse:
    del exc
    return _problem_response(
        request,
        status_code=status.HTTP_404_NOT_FOUND,
        detail="tenant unavailable",
    )


@app.middleware("http")
async def observe_http(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started = perf_counter()
    client_correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id_is_valid(client_correlation_id):
        invalid_response = _problem_response(
            request,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Correlation-ID must be 1-255 characters without surrounding whitespace",
            code="INVALID_CORRELATION_ID",
        )
        invalid_response.headers["X-Amesh-Error-Category"] = "terminal"
        return invalid_response
    if client_correlation_id is None:
        client_correlation_id = str(new_runtime_id())
    request.state.client_correlation_id = client_correlation_id
    try:
        settings = get_settings()
        apply_trusted_forwarded_headers(
            request.scope,
            request.headers,
            settings.network_trusted_proxy_ranges,
        )
    except ForwardedHeaderRejected as exc:
        return _problem_response(
            request,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
            code="UNTRUSTED_FORWARDED_HEADERS",
        )
    with observe_operation(
        "api",
        "request",
        carrier=request.headers,
        kind=SpanKind.SERVER,
        attributes={"http.request.method": request.method},
    ) as span:
        response = await call_next(request)
        route = request.scope.get("route")
        route_path = getattr(route, "path", "unmatched")
        status_code = str(response.status_code)
        span.set_attribute("http.route", route_path)
        span.set_attribute("http.response.status_code", response.status_code)
        HTTP_REQUESTS.labels(request.method, route_path, status_code).inc()
        HTTP_REQUEST_DURATION.labels(request.method, route_path).inc(perf_counter() - started)
        trace_context = propagated_trace_context()
        if "traceparent" in trace_context:
            response.headers["traceparent"] = trace_context["traceparent"]
        response.headers["X-Correlation-ID"] = client_correlation_id
        if response.status_code >= 400 and "X-Amesh-Error-Category" not in response.headers:
            response.headers["X-Amesh-Error-Category"] = error_category(response.status_code)
        LOGGER.info(
            "http request",
            extra={
                "http_method": request.method,
                "http_route": route_path,
                "http_status": response.status_code,
            },
        )
        return response


@lru_cache
def database_engine() -> AsyncEngine:
    settings = get_settings()
    return instrument_database(
        create_database_engine(settings),
        slow_query_seconds=settings.database_slow_query_seconds,
    )


@lru_cache
def read_database_engine() -> AsyncEngine:
    settings = get_settings()
    return instrument_database(
        create_database_engine(settings, read_replica=True),
        slow_query_seconds=settings.database_slow_query_seconds,
    )


@lru_cache
def get_plugin_catalog_manager() -> PluginCatalogManager:
    return build_plugin_catalog(get_settings())


PluginCatalogDependency = Annotated[
    PluginCatalogManager,
    Depends(get_plugin_catalog_manager),
]


@lru_cache
def get_plugin_policy_repository() -> PostgresPluginPolicyRepository:
    return PostgresPluginPolicyRepository(database_engine())


PluginPolicyRepositoryDependency = Annotated[
    PostgresPluginPolicyRepository,
    Depends(get_plugin_policy_repository),
]


@lru_cache
def get_plugin_policy_service() -> PluginPolicyService:
    settings = get_settings()
    return PluginPolicyService(
        get_plugin_policy_repository(),
        get_plugin_catalog_manager(),
        default_allow=settings.plugin_trust_mode == "development",
    )


PluginPolicyServiceDependency = Annotated[
    PluginPolicyService,
    Depends(get_plugin_policy_service),
]


@lru_cache
def get_admission_policy_repository() -> PostgresAdmissionPolicyRepository:
    return PostgresAdmissionPolicyRepository(database_engine())


AdmissionPolicyRepositoryDependency = Annotated[
    PostgresAdmissionPolicyRepository,
    Depends(get_admission_policy_repository),
]


@lru_cache
def get_admission_policy_service() -> AdmissionPolicyService:
    return AdmissionPolicyService(get_admission_policy_repository())


AdmissionPolicyServiceDependency = Annotated[
    AdmissionPolicyService,
    Depends(get_admission_policy_service),
]


async def _enforce_repository_admission_policy(
    flow: FlowDefinition,
    tenant_id: str,
    stage: PolicyStage,
    actor_id: str,
    inputs: dict[str, object] | None,
    task: TaskDefinition | None,
    execution_id: UUID | None,
    task_run_id: UUID | None,
) -> PolicyDecision:
    return await get_admission_policy_service().enforce_flow(
        flow,
        tenant_id,
        stage,
        actor_id,
        inputs=inputs,
        task=task,
        execution_id=execution_id,
        task_run_id=task_run_id,
    )


@lru_cache
def get_self_hosted_plugin_registry() -> SelfHostedPluginRegistry:
    settings = get_settings()
    trusted_keys = {
        key_id: secret.get_secret_value().encode("utf-8")
        for key_id, secret in settings.plugin_registry_verification_keys.items()
    }
    return SelfHostedPluginRegistry(
        settings.plugin_registry_root,
        key_id=settings.plugin_registry_signing_key_id,
        signing_key=settings.plugin_registry_signing_key.get_secret_value().encode("utf-8"),
        trusted_keys=trusted_keys,
    )


SelfHostedPluginRegistryDependency = Annotated[
    SelfHostedPluginRegistry,
    Depends(get_self_hosted_plugin_registry),
]


@lru_cache
def get_trusted_plugin_runtime() -> TrustedPluginRuntime:
    return build_trusted_runtime(get_settings(), get_plugin_catalog_manager())


TrustedPluginRuntimeDependency = Annotated[
    TrustedPluginRuntime,
    Depends(get_trusted_plugin_runtime),
]


@lru_cache
def get_isolated_plugin_runtime() -> IsolatedPluginRuntime:
    return build_isolated_runtime(get_settings(), get_plugin_catalog_manager())


IsolatedPluginRuntimeDependency = Annotated[
    IsolatedPluginRuntime,
    Depends(get_isolated_plugin_runtime),
]


@lru_cache
def get_repository() -> PostgresExecutionRepository:
    catalog = get_plugin_catalog_manager()
    return PostgresExecutionRepository(
        database_engine(),
        plugin_resolution_provider=lambda flow: (
            PluginResolver(catalog.snapshot).resolve_flow(flow).revision_payload()
        ),
        plugin_policy_enforcer=get_plugin_policy_service().enforce_flow,
        admission_policy_enforcer=_enforce_repository_admission_policy,
    )


RepositoryDependency = Annotated[
    PostgresExecutionRepository,
    Depends(get_repository),
]


@lru_cache
def get_flow_test_repository() -> PostgresFlowTestRepository:
    return PostgresFlowTestRepository(database_engine())


FlowTestRepositoryDependency = Annotated[
    PostgresFlowTestRepository,
    Depends(get_flow_test_repository),
]


@lru_cache
def get_task_cache_repository() -> PostgresTaskCacheRepository:
    return PostgresTaskCacheRepository(database_engine())


TaskCacheRepositoryDependency = Annotated[
    PostgresTaskCacheRepository,
    Depends(get_task_cache_repository),
]


@lru_cache
def get_retention_repository() -> PostgresRetentionRepository:
    return PostgresRetentionRepository(database_engine())


@lru_cache
def get_retention_service() -> RetentionService:
    return RetentionService(
        get_retention_repository(),
        build_object_store(get_settings()),
    )


RetentionRepositoryDependency = Annotated[
    PostgresRetentionRepository,
    Depends(get_retention_repository),
]
RetentionServiceDependency = Annotated[
    RetentionService,
    Depends(get_retention_service),
]


@lru_cache
def get_trigger_runtime_repository() -> PostgresTriggerRuntimeRepository:
    settings = get_settings()
    return PostgresTriggerRuntimeRepository(
        database_engine(),
        configured_trigger_payload_protector(
            primary_key_id=settings.model_continuation_key_id,
            primary_key=settings.model_continuation_encryption_key,
            previous_key_id=settings.model_continuation_previous_key_id,
            previous_key=settings.model_continuation_previous_encryption_key,
        ),
    )


TriggerRuntimeRepositoryDependency = Annotated[
    PostgresTriggerRuntimeRepository,
    Depends(get_trigger_runtime_repository),
]


@lru_cache
def get_check_repository() -> PostgresCheckRepository:
    return PostgresCheckRepository(database_engine())


CheckRepositoryDependency = Annotated[
    PostgresCheckRepository,
    Depends(get_check_repository),
]


@lru_cache
def get_metadata_repository() -> PostgresMetadataRepository:
    return PostgresMetadataRepository(database_engine())


MetadataRepositoryDependency = Annotated[
    PostgresMetadataRepository,
    Depends(get_metadata_repository),
]


@lru_cache
def get_evidence_bundle_repository() -> PostgresEvidenceBundleRepository:
    object_root = os.getenv("AMESH_EVIDENCE_OBJECT_ROOT")
    object_store = FilesystemEvidenceObjectStore(object_root) if object_root else None
    return PostgresEvidenceBundleRepository(database_engine(), object_store=object_store)


EvidenceBundleRepositoryDependency = Annotated[
    PostgresEvidenceBundleRepository,
    Depends(get_evidence_bundle_repository),
]


@lru_cache
def get_promotion_repository() -> PostgresPromotionRepository:
    return PostgresPromotionRepository(database_engine())


@lru_cache
def get_promotion_service() -> PromotionService:
    return PromotionService(get_promotion_repository())


async def get_promotion_authorizer(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Callable[[str], Awaitable[None]]:
    async def authorize_release(action: str) -> None:
        selected_action = (
            PermissionAction.VIEW if action in {"view", "preview"} else PermissionAction.MANAGE
        )
        await authorize_request(
            authorization_service,
            actor,
            resource_type="release",
            action=selected_action,
            tenant_id=tenant_id,
        )

    return authorize_release


async def get_promotion_actor(actor: ActorDependency) -> str:
    return str(actor.principal_id)


@lru_cache
def get_differential_repository() -> PostgresDifferentialShadowRepository:
    return PostgresDifferentialShadowRepository(database_engine())


@lru_cache
def get_differential_service() -> DurableDifferentialService:
    return DurableDifferentialService(get_differential_repository())


def get_differential_executor() -> Callable[
    [ConfigurationPin, object, ShadowRunContext], RunObservation
]:
    """Return the neutral baseline executor used until a domain adapter is supplied."""

    def execute(
        configuration: ConfigurationPin,
        inputs: object,
        context: ShadowRunContext,
    ) -> RunObservation:
        del configuration, context
        return RunObservation(output=inputs)

    return execute


async def get_differential_authorizer(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Callable[[str], Awaitable[None]]:
    async def authorize_differential(action: str) -> None:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=(PermissionAction.EXECUTE if action == "execute" else PermissionAction.VIEW),
            tenant_id=tenant_id,
        )

    return authorize_differential


async def get_differential_actor(actor: ActorDependency) -> str:
    return str(actor.principal_id)


@lru_cache
def get_dashboard_repository() -> PostgresDashboardRepository:
    return PostgresDashboardRepository(database_engine())


DashboardRepositoryDependency = Annotated[
    PostgresDashboardRepository,
    Depends(get_dashboard_repository),
]


@lru_cache
def get_search_repository() -> PostgresSearchRepository:
    return PostgresSearchRepository(database_engine())


SearchRepositoryDependency = Annotated[
    PostgresSearchRepository,
    Depends(get_search_repository),
]


@lru_cache
def get_realtime_repository() -> PostgresRealtimeRepository:
    return PostgresRealtimeRepository(database_engine())


RealtimeRepositoryDependency = Annotated[
    PostgresRealtimeRepository,
    Depends(get_realtime_repository),
]


@lru_cache
def get_agent_primitive_repository() -> PostgresAgentPrimitiveRepository:
    return PostgresAgentPrimitiveRepository(database_engine())


AgentPrimitiveRepositoryDependency = Annotated[
    PostgresAgentPrimitiveRepository,
    Depends(get_agent_primitive_repository),
]


@lru_cache
def get_agent_resource_repository() -> PostgresAgentResourceRepository:
    return PostgresAgentResourceRepository(database_engine())


AgentResourceRepositoryDependency = Annotated[
    PostgresAgentResourceRepository,
    Depends(get_agent_resource_repository),
]


@lru_cache
def get_agent_memory_repository() -> PostgresAgentMemoryRepository:
    return PostgresAgentMemoryRepository(database_engine())


AgentMemoryRepositoryDependency = Annotated[
    PostgresAgentMemoryRepository,
    Depends(get_agent_memory_repository),
]


@lru_cache
def get_agent_session_repository() -> PostgresAgentSessionRepository:
    return PostgresAgentSessionRepository(database_engine())


AgentSessionRepositoryDependency = Annotated[
    PostgresAgentSessionRepository,
    Depends(get_agent_session_repository),
]


@lru_cache
def get_shared_resource_repository() -> PostgresSharedResourceRepository:
    return PostgresSharedResourceRepository(database_engine())


SharedResourceRepositoryDependency = Annotated[
    PostgresSharedResourceRepository,
    Depends(get_shared_resource_repository),
]


@lru_cache
def get_human_task_repository() -> PostgresHumanTaskRepository:
    return PostgresHumanTaskRepository(database_engine())


HumanTaskRepositoryDependency = Annotated[
    PostgresHumanTaskRepository,
    Depends(get_human_task_repository),
]


@lru_cache
def get_operational_control_repository() -> PostgresOperationalControlRepository:
    return PostgresOperationalControlRepository(database_engine())


OperationalControlRepositoryDependency = Annotated[
    PostgresOperationalControlRepository,
    Depends(get_operational_control_repository),
]


@lru_cache
def get_human_task_service() -> HumanTaskService:
    return HumanTaskService(
        get_human_task_repository(),
        get_repository(),
        token_pepper=get_settings().amesh_token_pepper.get_secret_value(),
    )


HumanTaskServiceDependency = Annotated[
    HumanTaskService,
    Depends(get_human_task_service),
]


@lru_cache
def get_namespace_resource_service() -> NamespaceResourceService:
    return NamespaceResourceService(
        get_shared_resource_repository(),
        build_object_store(get_settings()),
    )


NamespaceResourceServiceDependency = Annotated[
    NamespaceResourceService,
    Depends(get_namespace_resource_service),
]


@lru_cache
def get_replica_repository() -> PostgresExecutionRepository:
    return PostgresExecutionRepository(read_database_engine())


def get_read_repository(
    primary: RepositoryDependency,
) -> PostgresExecutionRepository:
    if get_settings().database_read_replica_url is None:
        return primary
    return get_replica_repository()


ReadRepositoryDependency = Annotated[
    PostgresExecutionRepository,
    Depends(get_read_repository),
]


@lru_cache
def get_backfill_repository() -> PostgresBackfillRepository:
    return PostgresBackfillRepository(database_engine())


BackfillRepositoryDependency = Annotated[
    PostgresBackfillRepository,
    Depends(get_backfill_repository),
]


@lru_cache
def get_backfill_service() -> BackfillService:
    return BackfillService(
        get_repository(),
        get_backfill_repository(),
        get_operational_control_repository(),
    )


BackfillServiceDependency = Annotated[
    BackfillService,
    Depends(get_backfill_service),
]
SettingsDependency = Annotated[Settings, Depends(get_settings)]
ConfigurationManagerDependency = Annotated[
    ConfigurationManager,
    Depends(get_configuration_manager),
]


@lru_cache
def get_authorization_repository() -> PostgresAuthorizationRepository:
    return PostgresAuthorizationRepository(database_engine())


@lru_cache
def get_audit_repository() -> PostgresAuditRepository:
    return PostgresAuditRepository(database_engine())


@lru_cache
def get_audit_artifact_service() -> AuditArtifactService:
    settings = get_settings()
    return AuditArtifactService(
        get_audit_repository(),
        signing_key=settings.webhook_signing_key.get_secret_value(),
        object_store=build_object_store(settings),
    )


@lru_cache
def get_authorization_service() -> AuthorizationService:
    return AuthorizationService(
        get_authorization_repository(),
        decision_audit=get_audit_repository(),
    )


AuthorizationServiceDependency = Annotated[
    AuthorizationService,
    Depends(get_authorization_service),
]
AuthorizationRepositoryDependency = Annotated[
    PostgresAuthorizationRepository,
    Depends(get_authorization_repository),
]
AuditRepositoryDependency = Annotated[PostgresAuditRepository, Depends(get_audit_repository)]
AuditArtifactServiceDependency = Annotated[
    AuditArtifactService,
    Depends(get_audit_artifact_service),
]


@lru_cache
def get_credential_repository() -> PostgresCredentialRepository:
    return PostgresCredentialRepository(database_engine())


@lru_cache
def get_credential_service() -> CredentialService:
    settings = get_settings()
    return CredentialService(
        get_credential_repository(),
        token_pepper=settings.amesh_token_pepper,
        previous_token_pepper=settings.amesh_previous_token_pepper,
    )


CredentialServiceDependency = Annotated[CredentialService, Depends(get_credential_service)]


@lru_cache
def get_authentication_repository() -> PostgresAuthenticationRepository:
    return PostgresAuthenticationRepository(database_engine())


@lru_cache
def get_federation_repository() -> PostgresFederationRepository:
    return PostgresFederationRepository(
        database_engine(),
        token_pepper=get_settings().amesh_token_pepper,
    )


@lru_cache
def get_authentication_service() -> AuthenticationService:
    settings = get_settings()
    federation_repository = get_federation_repository()
    return AuthenticationService(
        get_authentication_repository(),
        token_pepper=settings.amesh_token_pepper,
        policy=settings.auth_policy,
        session_idle_seconds=settings.auth_session_idle_seconds,
        session_absolute_seconds=settings.auth_session_absolute_seconds,
        session_rotation_seconds=settings.auth_session_rotation_seconds,
        session_overlap_seconds=settings.auth_session_overlap_seconds,
        login_rate_limit_per_minute=settings.auth_login_rate_limit_per_minute,
        login_max_failures=settings.auth_login_max_failures,
        login_lock_seconds=settings.auth_login_lock_seconds,
        providers=tuple(
            LdapAuthenticationProvider(provider, federation_repository)
            for provider in settings.identity_providers
            if provider.kind == "ldap"
        ),
    )


AuthenticationServiceDependency = Annotated[
    AuthenticationService,
    Depends(get_authentication_service),
]


@lru_cache
def get_federation_service() -> IdentityFederationService:
    settings = get_settings()
    return IdentityFederationService(
        get_federation_repository(),
        get_authentication_service(),
        settings.identity_providers,
    )


FederationServiceDependency = Annotated[
    IdentityFederationService,
    Depends(get_federation_service),
]


async def authenticate_scim_provider(
    settings: SettingsDependency,
    authorization: Annotated[str | None, Header()] = None,
) -> ScimProviderConfig:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="SCIM bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    supplied = authorization[7:]
    unavailable = False
    for provider in settings.scim_providers:
        try:
            configured = Path(provider.token_file).read_text(encoding="utf-8").strip()
        except OSError:
            unavailable = True
            continue
        if configured and secrets.compare_digest(supplied, configured):
            return provider
    if unavailable and settings.scim_providers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SCIM provider credential is unavailable",
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid SCIM bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )


ScimProviderDependency = Annotated[ScimProviderConfig, Depends(authenticate_scim_provider)]
FederationRepositoryDependency = Annotated[
    PostgresFederationRepository,
    Depends(get_federation_repository),
]


@lru_cache
def get_tenant_repository() -> PostgresTenantRepository:
    return PostgresTenantRepository(database_engine())


@lru_cache
def get_tenant_service() -> TenantService:
    return TenantService(get_tenant_repository())


TenantServiceDependency = Annotated[TenantService, Depends(get_tenant_service)]


@lru_cache
def get_feature_flag_repository() -> PostgresFeatureFlagRepository:
    return PostgresFeatureFlagRepository(database_engine())


FeatureFlagRepositoryDependency = Annotated[
    PostgresFeatureFlagRepository,
    Depends(get_feature_flag_repository),
]


@lru_cache
def get_worker_repository() -> PostgresWorkerRepository:
    return PostgresWorkerRepository(database_engine())


WorkerRepositoryDependency = Annotated[
    PostgresWorkerRepository,
    Depends(get_worker_repository),
]


@lru_cache
def get_reconciliation_service() -> ReconciliationService:
    return ReconciliationService(PostgresReconciliationRepository(database_engine()))


ReconciliationServiceDependency = Annotated[
    ReconciliationService,
    Depends(get_reconciliation_service),
]


@lru_cache
def get_service_registry_repository() -> PostgresServiceRegistryRepository:
    settings = get_settings()
    return PostgresServiceRegistryRepository(
        database_engine(),
        stale_after_seconds=settings.service_stale_after_seconds,
    )


ServiceRegistryRepositoryDependency = Annotated[
    PostgresServiceRegistryRepository,
    Depends(get_service_registry_repository),
]


@lru_cache
def get_upgrade_repository() -> PostgresUpgradeRepository:
    return PostgresUpgradeRepository(database_engine())


@lru_cache
def get_upgrade_service() -> UpgradeService:
    return UpgradeService(
        get_upgrade_repository(),
        get_service_registry_repository(),
        get_plugin_catalog_manager(),
        build_object_store(get_settings()),
    )


UpgradeRepositoryDependency = Annotated[
    PostgresUpgradeRepository,
    Depends(get_upgrade_repository),
]
UpgradeServiceDependency = Annotated[
    UpgradeService,
    Depends(get_upgrade_service),
]
_TENANT_SLUG_ADAPTER = TypeAdapter(TenantSlug)


_BOOTSTRAP_PRINCIPAL_ID = UUID("00000000-0000-7000-8000-000000000001")


async def authenticate_bearer_actor(
    settings: SettingsDependency,
    credential_service: CredentialService | None,
    authorization: str | None,
) -> ActorContext:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="valid bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expected = f"Bearer {settings.amesh_admin_token.get_secret_value()}"
    if (
        settings.app_env == "development"
        and settings.auth_mode == "development"
        and authorization is not None
        and secrets.compare_digest(authorization, expected)
    ):
        return ActorContext(
            principal_id=_BOOTSTRAP_PRINCIPAL_ID,
            principal_type=PrincipalType.SYSTEM,
            display="development-bootstrap-admin",
            bootstrap_admin=True,
        )
    if credential_service is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="valid bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await credential_service.authenticate_bearer(authorization)
    except CredentialRateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="credential rate limit exceeded",
            headers={"Retry-After": "60"},
        ) from exc
    except InvalidCredential as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="valid bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def authenticate_actor(
    request: Request,
    response: Response,
    settings: SettingsDependency,
    credential_service: CredentialServiceDependency,
    authentication_service: AuthenticationServiceDependency,
    authorization: Annotated[str | None, Header()] = None,
    csrf_header: Annotated[str | None, Header(alias="X-Amesh-CSRF")] = None,
) -> ActorContext:
    if authorization is not None:
        return await authenticate_bearer_actor(settings, credential_service, authorization)
    session_cookie = request.cookies.get(_session_cookie_name(settings))
    if session_cookie is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    require_csrf = request.method not in {"GET", "HEAD", "OPTIONS", "TRACE"}
    try:
        authenticated = await authentication_service.authenticate_session(
            session_cookie,
            csrf_cookie=request.cookies.get(_csrf_cookie_name(settings)),
            csrf_header=csrf_header,
            require_csrf=require_csrf,
        )
    except InvalidCsrf as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        ) from exc
    except InvalidAuthentication as exc:
        _clear_session_cookies(response, settings)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if authenticated.rotated_token is not None:
        remaining = max(
            0,
            int((authenticated.absolute_expires_at - datetime.now(UTC)).total_seconds()),
        )
        _set_session_cookie(
            response,
            settings,
            authenticated.rotated_token.get_secret_value(),
            max_age=remaining,
        )
    request.state.browser_session_id = authenticated.session_id
    return authenticated.actor


def _session_cookie_name(settings: Settings) -> str:
    return "amesh_session" if settings.app_env == "development" else "__Host-amesh_session"


def _csrf_cookie_name(settings: Settings) -> str:
    return "amesh_csrf" if settings.app_env == "development" else "__Host-amesh_csrf"


def _set_session_cookie(
    response: Response,
    settings: Settings,
    value: str,
    *,
    max_age: int,
) -> None:
    response.set_cookie(
        _session_cookie_name(settings),
        value,
        max_age=max_age,
        path="/",
        secure=settings.app_env != "development",
        httponly=True,
        samesite="lax",
    )


def _set_authentication_cookies(
    response: Response,
    settings: Settings,
    *,
    session_token: str,
    csrf_token: str,
    max_age: int,
) -> None:
    _set_session_cookie(response, settings, session_token, max_age=max_age)
    response.set_cookie(
        _csrf_cookie_name(settings),
        csrf_token,
        max_age=max_age,
        path="/",
        secure=settings.app_env != "development",
        httponly=False,
        samesite="lax",
    )


def _clear_session_cookies(response: Response, settings: Settings) -> None:
    secure = settings.app_env != "development"
    response.delete_cookie(
        _session_cookie_name(settings),
        path="/",
        secure=secure,
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(
        _csrf_cookie_name(settings),
        path="/",
        secure=secure,
        httponly=False,
        samesite="lax",
    )


def _set_issued_session_cookies(
    response: Response,
    settings: Settings,
    issued: IssuedBrowserSession,
) -> None:
    max_age = max(
        0,
        int((issued.absolute_expires_at - datetime.now(UTC)).total_seconds()),
    )
    _set_authentication_cookies(
        response,
        settings,
        session_token=issued.session_token.get_secret_value(),
        csrf_token=issued.csrf_token.get_secret_value(),
        max_age=max_age,
    )


def _urlencoded_form(body: bytes) -> dict[str, str]:
    try:
        decoded = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="form payload must be UTF-8") from exc
    return {key: values[-1] for key, values in parse_qs(decoded, keep_blank_values=True).items()}


def _saml_request_data(
    request: Request,
    *,
    post_data: dict[str, str] | None = None,
) -> dict[str, object]:
    port = request.url.port or (443 if request.url.scheme == "https" else 80)
    return {
        "https": "on" if request.url.scheme == "https" else "off",
        "http_host": request.url.hostname or "localhost",
        "server_port": str(port),
        "script_name": request.url.path,
        "get_data": dict(request.query_params),
        "post_data": post_data or {},
        "query_string": request.url.query,
    }


def _scim_filter_value(filter_value: str | None, attribute: str) -> str | None:
    if filter_value is None:
        return None
    matched = re.fullmatch(
        rf'\s*{re.escape(attribute)}\s+eq\s+"([^"]+)"\s*',
        filter_value,
        flags=re.IGNORECASE,
    )
    if matched is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'SCIM filter must use {attribute} eq "value"',
        )
    return matched.group(1)


def _scim_principal_handle(value: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", value.strip().lower()).strip("-_")
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"scim-{(slug or 'resource')[:80]}-{digest}"


def _scim_meta(record: ScimResourceRecord) -> ScimResourceMeta:
    plural = "Users" if record.resource_type == "User" else "Groups"
    return ScimResourceMeta(
        resourceType=record.resource_type,
        created=record.created_at,
        lastModified=record.updated_at,
        version=f'W/"{record.version}"',
        location=f"/scim/v2/{plural}/{record.principal_id}",
    )


def _scim_user_resource(record: ScimResourceRecord) -> ScimUserResource:
    return ScimUserResource(
        id=record.principal_id,
        externalId=record.external_id,
        userName=record.resource_name,
        displayName=record.display_name,
        active=record.enabled,
        meta=_scim_meta(record),
    )


def _scim_group_resource(record: ScimResourceRecord) -> ScimGroupResource:
    return ScimGroupResource(
        id=record.principal_id,
        externalId=record.external_id,
        displayName=record.display_name,
        members=tuple(ScimMember(value=member_id) for member_id in record.member_ids),
        meta=_scim_meta(record),
    )


def _scim_user_patch(payload: ScimPatchRequest) -> tuple[str | None, bool | None]:
    display_name: str | None = None
    active: bool | None = None
    for operation in payload.operations:
        if operation.op.lower() not in {"add", "replace"}:
            raise ValueError("SCIM users support add or replace for active and displayName")
        if operation.path is None and isinstance(operation.value, dict):
            if "displayName" in operation.value:
                display_name = str(operation.value["displayName"])
            if "active" in operation.value:
                active = bool(operation.value["active"])
        elif operation.path and operation.path.lower() == "displayname":
            display_name = str(operation.value)
        elif operation.path and operation.path.lower() == "active":
            if not isinstance(operation.value, bool):
                raise ValueError("SCIM active patch value must be boolean")
            active = operation.value
        else:
            raise ValueError("unsupported SCIM user patch path")
    return display_name, active


def _scim_member_values(value: object) -> set[UUID]:
    items = value if isinstance(value, list) else [value]
    members: set[UUID] = set()
    for item in items:
        if not isinstance(item, dict) or "value" not in item:
            raise ValueError("SCIM member values must contain a value UUID")
        members.add(UUID(str(item["value"])))
    return members


def _scim_group_patch(
    payload: ScimPatchRequest,
    current_members: tuple[UUID, ...],
) -> tuple[str | None, tuple[UUID, ...] | None]:
    display_name: str | None = None
    members = set(current_members)
    members_changed = False
    for operation in payload.operations:
        op = operation.op.lower()
        path = operation.path or ""
        if not path and isinstance(operation.value, dict):
            if "displayName" in operation.value:
                display_name = str(operation.value["displayName"])
            if "members" in operation.value:
                members = _scim_member_values(operation.value["members"])
                members_changed = True
            continue
        if path.lower() == "displayname" and op in {"add", "replace"}:
            display_name = str(operation.value)
        elif path.lower() == "members" and op in {"add", "replace"}:
            incoming = _scim_member_values(operation.value)
            members = incoming if op == "replace" else members | incoming
            members_changed = True
        elif op == "remove":
            matched = re.fullmatch(
                r'members\[value\s+eq\s+"([0-9a-fA-F-]{36})"\]',
                path,
                flags=re.IGNORECASE,
            )
            if matched is None:
                raise ValueError('SCIM member removal requires members[value eq "uuid"]')
            members.discard(UUID(matched.group(1)))
            members_changed = True
        else:
            raise ValueError("unsupported SCIM group patch operation")
    ordered = tuple(sorted(members, key=str)) if members_changed else None
    return display_name, ordered


ActorDependency = Annotated[ActorContext, Depends(authenticate_actor)]


class _TenantRequestContext(str):
    """Tenant slug carrying the request-local, deferred API quota charge."""

    _tenant_service: TenantService
    _quota_charge_lock: asyncio.Lock
    _quota_charged: bool

    def __new__(cls, value: str, tenant_service: TenantService) -> _TenantRequestContext:
        context = super().__new__(cls, value)
        context._tenant_service = tenant_service
        context._quota_charge_lock = asyncio.Lock()
        context._quota_charged = False
        return context

    async def charge_api_request(self) -> None:
        async with self._quota_charge_lock:
            if self._quota_charged:
                return
            await self._tenant_service.consume_api_request(str(self))
            self._quota_charged = True


def _request_control_boundaries(request: Request) -> tuple[OperationalBoundary, ...]:
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return ()
    path = request.url.path
    if path.startswith("/api/v1/operational-controls"):
        return ()
    boundaries = [OperationalBoundary.API_WRITES]
    authoring_roots = (
        "/api/v1/flows",
        "/api/v1/apps",
        "/api/v1/dashboards",
        "/api/v1/plugin-policy",
        "/api/v1/plugin-registry",
        "/api/v1/namespaces",
    )
    if path.startswith(authoring_roots):
        boundaries.append(OperationalBoundary.AUTHORING)
    return tuple(boundaries)


async def _enforce_request_controls(
    repository: PostgresOperationalControlRepository,
    request: Request,
    *,
    tenant_id: str,
) -> None:
    for boundary in _request_control_boundaries(request):
        decision = await repository.evaluate(
            boundary,
            tenant_id=tenant_id,
            namespace=request.path_params.get("namespace"),
            flow_id=request.path_params.get("flow_id"),
            component_id="webserver:api",
            component_role=ServiceRole.WEBSERVER.value,
        )
        if decision.blocked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail={
                    "message": f"{boundary.value.lower()} blocked by operational control",
                    "boundary": boundary.value,
                    "controlIds": [str(control.control_id) for control in decision.controls],
                },
            )


async def require_tenant_context(
    request: Request,
    settings: SettingsDependency,
    tenant_service: TenantServiceDependency,
    operational_controls: OperationalControlRepositoryDependency,
    tenant_header: Annotated[str | None, Header(alias="X-Amesh-Tenant")] = None,
) -> str:
    if tenant_header is None:
        if settings.tenancy_mode != "single":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Amesh-Tenant header required",
            )
        tenant_header = settings.single_tenant_slug
    try:
        tenant_slug = _TENANT_SLUG_ADAPTER.validate_python(tenant_header)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tenant unavailable",
        ) from None
    tenant_context = _TenantRequestContext(tenant_slug, tenant_service)
    await _enforce_request_controls(
        operational_controls,
        request,
        tenant_id=tenant_context,
    )
    return tenant_context


TenantDependency = Annotated[str, Depends(require_tenant_context)]


async def _charge_authorized_tenant_request(tenant_id: str | None) -> None:
    if not isinstance(tenant_id, _TenantRequestContext):
        return
    try:
        await tenant_id.charge_api_request()
    except TenantQuotaExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="tenant API request quota exceeded",
            headers={"Retry-After": "60"},
        ) from exc


async def authorize_request(
    service: AuthorizationService,
    actor: ActorContext,
    *,
    resource_type: str,
    action: PermissionAction,
    tenant_id: str | None = None,
    namespace: str | None = None,
) -> AuthorizationDecision:
    try:
        decision = await service.require(
            AuthorizationRequest(
                actor=actor,
                tenant_id=tenant_id,
                namespace=namespace,
                resource_type=resource_type,
                action=action,
            )
        )
    except AuthorizationDenied as exc:
        if tenant_id is not None and not exc.decision.matched_role_names:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="tenant unavailable",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized",
        ) from exc
    await _charge_authorized_tenant_request(tenant_id)
    return decision


app.include_router(
    build_promotion_router(
        get_promotion_service,
        require_tenant_context,
        get_promotion_authorizer,
        get_promotion_actor,
    )
)
app.include_router(
    build_differential_application_router(
        get_differential_service,
        get_differential_executor,
        require_tenant_context,
        get_differential_authorizer,
        get_differential_actor,
    )
)


def _agent_outbound_policy(settings: Settings) -> HttpTaskPolicy:
    return HttpTaskPolicy(
        allowed_hosts=settings.network_egress_allowed_hosts,
        allowed_private_hosts=frozenset(settings.core_http_allowed_private_hosts),
        maximum_response_bytes=settings.core_http_max_response_bytes,
        maximum_pages=settings.core_http_max_pages,
        maximum_redirects=settings.core_http_max_redirects,
        http_proxy_url=(
            settings.network_http_proxy_url.get_secret_value()
            if settings.network_http_proxy_url is not None
            else None
        ),
        https_proxy_url=(
            settings.network_https_proxy_url.get_secret_value()
            if settings.network_https_proxy_url is not None
            else None
        ),
        no_proxy=settings.network_no_proxy,
        ca_file=settings.network_outbound_ca_file,
        client_certificate_file=settings.network_outbound_client_certificate_file,
        client_key_file=settings.network_outbound_client_key_file,
    )


async def _agent_secret_value(
    namespace: str,
    credential_ref: str,
    *,
    repository: PostgresSharedResourceRepository,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> str:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="secret_binding",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        binding = await repository.get_secret_binding(
            namespace,
            credential_ref,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="credential binding unavailable",
        ) from exc
    credential = os.environ.get(binding.provider_reference)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="credential provider reference unavailable",
        )
    return credential


async def _discover_agent_mcp(
    request: McpConnectionDiscoveryRequest,
    namespace: str,
    *,
    shared_resources: PostgresSharedResourceRepository,
    settings: Settings,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> McpDiscoveryResult:
    credential = await _agent_secret_value(
        namespace,
        request.credential_ref,
        repository=shared_resources,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
    )
    try:
        return await discover_mcp_server(
            request.endpoint,
            credential,
            timeout_seconds=request.timeout_seconds,
            http_policy=_agent_outbound_policy(settings),
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        LOGGER.warning(
            "MCP discovery failed",
            extra={"namespace": namespace, "endpoint": request.endpoint},
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="MCP discovery failed",
        ) from exc


@app.post(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections/discover",
    response_model=McpDiscoveryResult,
    tags=["agents"],
)
async def discover_agent_mcp_connection(
    namespace: str,
    request: McpConnectionDiscoveryRequest,
    shared_resources: SharedResourceRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> McpDiscoveryResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.CREATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await _discover_agent_mcp(
        request,
        namespace,
        shared_resources=shared_resources,
        settings=settings,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
    )


@app.post(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections",
    response_model=McpConnectionRevision,
    status_code=status.HTTP_201_CREATED,
    tags=["agents"],
)
async def create_agent_mcp_connection_revision(
    namespace: str,
    spec: McpConnectionSpec,
    repository: AgentPrimitiveRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> McpConnectionRevision:
    if spec.namespace != namespace:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="connection namespace must match the route namespace",
        )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    discovery = await _discover_agent_mcp(
        McpConnectionDiscoveryRequest(
            endpoint=spec.endpoint,
            credentialRef=spec.credential_ref,
        ),
        namespace,
        shared_resources=shared_resources,
        settings=settings,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
    )
    live_tools = {tool.name: tool.schema_digest for tool in discovery.tools}
    pinned_tools = {tool.name: tool.schema_digest for tool in spec.tools}
    if any(live_tools.get(name) != digest for name, digest in pinned_tools.items()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="MCP tool schemas changed after discovery",
        )
    return await repository.save_mcp_connection(
        tenant_id,
        spec,
        actor_id=str(actor.principal_id),
    )


@app.get(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections",
    response_model=list[McpConnectionRevision],
    tags=["agents"],
)
async def list_agent_mcp_connections(
    namespace: str,
    repository: AgentPrimitiveRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[McpConnectionRevision]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(await repository.list_mcp_connections(tenant_id, namespace))


@app.get(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections/{key}",
    response_model=McpConnectionRevision,
    tags=["agents"],
)
async def get_agent_mcp_connection(
    namespace: str,
    key: str,
    repository: AgentPrimitiveRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> McpConnectionRevision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.get_mcp_connection(
            tenant_id,
            namespace,
            key,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP connection unavailable",
        ) from exc


@app.get(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/tools",
    response_model=list[dict[str, object]],
    tags=["agents"],
)
async def list_agent_mcp_connection_tools(
    namespace: str,
    key: str,
    repository: AgentPrimitiveRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> list[dict[str, object]]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        connection = await repository.get_mcp_connection(
            tenant_id,
            namespace,
            key,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP connection unavailable",
        ) from exc
    return [
        {
            "connectionKey": connection.spec.key,
            "connectionRevision": connection.revision,
            "connectionDigest": connection.digest,
            "credentialRef": connection.spec.credential_ref,
            "endpoint": connection.spec.endpoint,
            "toolName": tool.name,
            "description": tool.description,
            "schemaDigest": tool.schema_digest,
            "impact": tool.impact.value,
        }
        for tool in connection.spec.tools
    ]


@app.post(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/test",
    response_model=McpConnectionTestResponse,
    tags=["agents"],
)
async def test_agent_mcp_connection(
    namespace: str,
    key: str,
    request: McpConnectionTestRequest,
    repository: AgentPrimitiveRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    settings: SettingsDependency,
    audit_repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> McpConnectionTestResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        connection = await repository.get_mcp_connection(
            tenant_id,
            namespace,
            key,
            revision=request.revision,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP connection unavailable",
        ) from exc

    observed_digest: str | None
    diagnostic: str | None
    try:
        discovery = await _discover_agent_mcp(
            McpConnectionDiscoveryRequest(
                endpoint=connection.spec.endpoint,
                credentialRef=connection.spec.credential_ref,
                timeoutSeconds=request.timeout_seconds,
            ),
            namespace,
            shared_resources=shared_resources,
            settings=settings,
            actor=actor,
            authorization_service=authorization_service,
            tenant_id=tenant_id,
        )
    except HTTPException as exc:
        if exc.status_code in {
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        }:
            raise
        result_status = McpConnectionTestStatus.UNAVAILABLE
        observed_digest = None
        checked_tool_count = 0
        diagnostic = (
            "The MCP server could not be discovered under the configured network, "
            "credential, and timeout policy."
        )
    else:
        live_tools = {tool.name: tool.schema_digest for tool in discovery.tools}
        schema_drift = any(
            live_tools.get(tool.name) != tool.schema_digest for tool in connection.spec.tools
        )
        result_status = (
            McpConnectionTestStatus.SCHEMA_DRIFT if schema_drift else McpConnectionTestStatus.PASSED
        )
        observed_digest = discovery.digest
        checked_tool_count = len(connection.spec.tools)
        diagnostic = (
            "One or more pinned MCP tool schemas changed or disappeared; rediscover "
            "the server and save a new immutable connection revision."
            if schema_drift
            else None
        )

    evidence_id = await audit_repository.record_connection_test(
        tenant_id,
        actor_id=str(actor.principal_id),
        connection_key=connection.spec.key,
        connection_revision=connection.revision,
        connection_digest=connection.digest,
        status=result_status.value,
        observed_digest=observed_digest,
        checked_tool_count=checked_tool_count,
        diagnostic=diagnostic,
    )
    return McpConnectionTestResponse(
        status=result_status,
        evidenceId=evidence_id,
        connectionPin=McpConnectionTestPin(
            key=connection.spec.key,
            revision=connection.revision,
            digest=connection.digest,
        ),
        observedDigest=observed_digest,
        checkedToolCount=checked_tool_count,
        diagnostic=diagnostic,
    )


async def _capability_source_access(
    authorization_service: AuthorizationService,
    actor: ActorContext,
    *,
    source: CapabilitySource,
    resource_type: str,
    tenant_id: str,
    namespace: str | None,
) -> tuple[bool, CapabilitySourceAccess]:
    try:
        decision = await authorization_service.decide(
            AuthorizationRequest(
                actor=actor,
                tenant_id=tenant_id,
                namespace=namespace,
                resource_type=resource_type,
                action=PermissionAction.VIEW,
            )
        )
    except Exception:
        LOGGER.exception("Capability catalog authorization source unavailable")
        return False, CapabilitySourceAccess(
            source=source,
            status=CapabilitySourceAccessStatus.UNAVAILABLE,
            diagnostics=("Authorization policy could not evaluate this source.",),
        )
    if not decision.allowed:
        return False, CapabilitySourceAccess(
            source=source,
            status=CapabilitySourceAccessStatus.DENIED,
            diagnostics=("This source is not authorized for the current principal.",),
        )
    return True, CapabilitySourceAccess(
        source=source,
        status=CapabilitySourceAccessStatus.ALLOWED,
    )


@app.get(
    "/api/v1/namespaces/{namespace}/agent/capabilities/catalog",
    response_model=CapabilityCatalog,
    tags=["agents"],
)
async def get_agent_capability_catalog(
    namespace: str,
    resource_repository: AgentResourceRepositoryDependency,
    primitive_repository: AgentPrimitiveRepositoryDependency,
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    query: Annotated[str | None, Query(alias="q", min_length=1, max_length=255)] = None,
    kinds: Annotated[list[CapabilityKind] | None, Query(alias="kind")] = None,
    statuses: Annotated[list[CapabilityStatus] | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
) -> CapabilityCatalog:
    source_specs = (
        (CapabilitySource.AGENTS, "agent", namespace),
        (CapabilitySource.CONNECTIONS, "agent_connection", namespace),
        (CapabilitySource.PLUGINS, "plugin", None),
    )
    access: dict[CapabilitySource, CapabilitySourceAccess] = {}
    allowed: dict[CapabilitySource, bool] = {}
    for source, resource_type, source_namespace in source_specs:
        allowed[source], access[source] = await _capability_source_access(
            authorization_service,
            actor,
            source=source,
            resource_type=resource_type,
            tenant_id=tenant_id,
            namespace=source_namespace,
        )
    if any(allowed.values()):
        await _charge_authorized_tenant_request(tenant_id)

    agent_resources: tuple[AgentResourceRevision, ...] = ()
    connections: tuple[McpConnectionRevision, ...] = ()
    plugin_packages: tuple[PluginRegistryPackage, ...] = ()
    try:
        if allowed[CapabilitySource.AGENTS]:
            agent_resources = await resource_repository.list_resources(
                tenant_id,
                namespace,
            )
    except Exception:
        LOGGER.exception("Capability catalog agent resource source unavailable")
        access[CapabilitySource.AGENTS] = CapabilitySourceAccess(
            source=CapabilitySource.AGENTS,
            status=CapabilitySourceAccessStatus.UNAVAILABLE,
            diagnostics=("Agent resources are temporarily unavailable.",),
        )
    try:
        if allowed[CapabilitySource.CONNECTIONS]:
            connections = await primitive_repository.list_mcp_connections(
                tenant_id,
                namespace,
            )
    except Exception:
        LOGGER.exception("Capability catalog connection source unavailable")
        access[CapabilitySource.CONNECTIONS] = CapabilitySourceAccess(
            source=CapabilitySource.CONNECTIONS,
            status=CapabilitySourceAccessStatus.UNAVAILABLE,
            diagnostics=("MCP connections are temporarily unavailable.",),
        )
    try:
        if allowed[CapabilitySource.PLUGINS]:
            plugin_packages = registry.snapshot().packages
    except Exception:
        LOGGER.exception("Capability catalog plugin source unavailable")
        access[CapabilitySource.PLUGINS] = CapabilitySourceAccess(
            source=CapabilitySource.PLUGINS,
            status=CapabilitySourceAccessStatus.UNAVAILABLE,
            diagnostics=("Plugin packages are temporarily unavailable.",),
        )

    catalog = build_capability_catalog(
        agent_resources,
        connections,
        plugin_packages,
        namespace=namespace,
        source_access=(access[source] for source in CapabilitySource),
    )
    return filter_capability_catalog(
        catalog,
        query=query,
        kinds=kinds or (),
        statuses=statuses or (),
        limit=limit,
    )


@app.post(
    "/api/v1/namespaces/{namespace}/agent/resources",
    response_model=AgentResourceRevision,
    status_code=status.HTTP_201_CREATED,
    tags=["agents"],
)
async def create_agent_resource_revision(
    namespace: str,
    spec: AgentResourceSpec,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentResourceRevision:
    if spec.namespace != namespace:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resource namespace must match the route namespace",
        )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.save_resource(
        tenant_id,
        spec,
        actor_id=str(actor.principal_id),
    )


@app.get(
    "/api/v1/namespaces/{namespace}/agent/resources",
    response_model=list[AgentResourceRevision],
    tags=["agents"],
)
async def list_agent_resources(
    namespace: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    kind: AgentResourceKind | None = None,
) -> list[AgentResourceRevision]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(await repository.list_resources(tenant_id, namespace, kind=kind))


async def _agent_resource_or_404(
    repository: PostgresAgentResourceRepository,
    tenant_id: str,
    namespace: str,
    kind: AgentResourceKind,
    key: str,
    revision: int | None,
) -> AgentResourceRevision:
    try:
        return await repository.get_resource(
            tenant_id,
            namespace,
            kind,
            key,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="agent resource unavailable",
        ) from exc


@app.get(
    "/api/v1/namespaces/{namespace}/agent/resources/{kind}/{key}",
    response_model=AgentResourceRevision,
    tags=["agents"],
)
async def get_agent_resource(
    namespace: str,
    kind: AgentResourceKind,
    key: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> AgentResourceRevision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        kind,
        key,
        revision,
    )


@app.post(
    "/api/v1/namespaces/{namespace}/agent/definitions/{key}/resolve",
    response_model=AgentCapabilityPin,
    tags=["agents"],
)
async def resolve_agent_definition(
    namespace: str,
    key: str,
    request: AgentResolutionRequest,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentCapabilityPin:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.resolve_agent(
            tenant_id,
            namespace,
            key,
            request,
            actor_id=str(actor.principal_id),
        )
    except (LookupError, PermissionError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/namespaces/{namespace}/agent/definitions/{key}/preview",
    response_model=AgentEnvelopePreview,
    tags=["agents"],
)
async def preview_agent_definition(
    namespace: str,
    key: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    agent_revision: Annotated[int, Query(alias="agentRevision", ge=1)],
) -> AgentEnvelopePreview:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.preview_agent(
            tenant_id,
            namespace,
            key,
            agent_revision=agent_revision,
        )
    except (LookupError, PermissionError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/v1/namespaces/{namespace}/agent/mesh/routes/preview",
    response_model=AgentRouteDecision,
    tags=["agents"],
)
async def preview_agent_mesh_route(
    namespace: str,
    request: AgentRouteRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentRouteDecision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return route_agent(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/namespaces/{namespace}/agent/evaluations/{key}/fixtures/{fixture_key}/preview",
    response_model=AgentEvaluationPreview,
    tags=["agents"],
)
async def preview_agent_evaluation_fixture(
    namespace: str,
    key: str,
    fixture_key: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int, Query(ge=1)],
) -> AgentEvaluationPreview:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    resource = await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        AgentResourceKind.EVALUATION,
        key,
        revision,
    )
    if not isinstance(resource.spec, AgentEvaluationSpec):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="resource is not an evaluation",
        )
    fixture = next(
        (item for item in resource.spec.fixtures if item.key == fixture_key),
        None,
    )
    if fixture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="evaluation fixture unavailable",
        )
    return AgentEvaluationPreview(
        evaluationKey=resource.key,
        evaluationRevision=resource.revision,
        fixtureKey=fixture.key,
        input=fixture.input,
        recordedOutput=fixture.recorded_output,
        deterministic=evaluate_deterministic_output(
            resource.spec,
            fixture.recorded_output,
        ),
        judgeRequired=resource.spec.judge is not None,
    )


@app.get(
    "/api/v1/namespaces/{namespace}/agent/memory",
    response_model=list[AgentMemoryMetadata],
    tags=["agents"],
)
async def list_agent_memory_metadata(
    namespace: str,
    repository: AgentMemoryRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    agent_key: Annotated[str | None, Query(alias="agentKey")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[AgentMemoryMetadata]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(
        await repository.list_metadata(
            tenant_id,
            namespace,
            agent_key=agent_key,
            limit=limit,
        )
    )


@app.delete(
    "/api/v1/namespaces/{namespace}/agent/memory/{entry_id}",
    response_model=AgentMemoryMetadata,
    tags=["agents"],
)
async def delete_agent_memory_entry(
    namespace: str,
    entry_id: UUID,
    repository: AgentMemoryRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentMemoryMetadata:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        metadata = await repository.delete(
            tenant_id,
            namespace,
            entry_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="agent memory entry unavailable",
        ) from exc
    return metadata


@app.get(
    "/api/v1/namespaces/{namespace}/agent/definitions/{key}/compare",
    response_model=AgentRevisionComparison,
    tags=["agents"],
)
async def compare_agent_definition_revisions(
    namespace: str,
    key: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    from_revision: Annotated[int, Query(alias="fromRevision", ge=1)],
    to_revision: Annotated[int, Query(alias="toRevision", ge=1)],
) -> AgentRevisionComparison:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    previous = await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        AgentResourceKind.AGENT,
        key,
        from_revision,
    )
    current = await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        AgentResourceKind.AGENT,
        key,
        to_revision,
    )
    return compare_agent_revisions(previous, current)


@app.get(
    "/api/v1/namespaces/{namespace}/agent/model-policies/{key}/migration",
    response_model=ProviderMigrationDiagnostic,
    tags=["agents"],
)
async def diagnose_model_policy_migration(
    namespace: str,
    key: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    from_revision: Annotated[int, Query(alias="fromRevision", ge=1)],
    to_revision: Annotated[int, Query(alias="toRevision", ge=1)],
) -> ProviderMigrationDiagnostic:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    previous = await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        AgentResourceKind.MODEL_POLICY,
        key,
        from_revision,
    )
    current = await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        AgentResourceKind.MODEL_POLICY,
        key,
        to_revision,
    )
    if not isinstance(previous.spec, ModelPolicySpec) or not isinstance(
        current.spec,
        ModelPolicySpec,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="model-policy revisions have incompatible resource kinds",
        )
    return provider_migration_diagnostic(previous.spec, current.spec)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@app.get("/ready", response_model=ReadinessResponse, tags=["system"])
async def ready(
    response: Response,
    settings: SettingsDependency,
    service_registry: ServiceRegistryRepositoryDependency,
) -> ReadinessResponse:
    readiness = await run_preflight(
        settings,
        engine=database_engine(),
        check_storage=settings.readiness_check_storage,
    )
    dependencies = readiness.dependency_states
    registered_ready = True
    role_states = {role.value: "DISABLED" for role in ServiceRole}
    enabled_roles = {ServiceRole(value) for value in settings.service_enabled_roles}
    for role in enabled_roles:
        role_states[role.value] = DependencyCondition.UNAVAILABLE.value
    unready_roles: list[str] = []
    if readiness.ready:
        topology = await service_registry.topology()
        for role in enabled_roles:
            live = tuple(
                instance
                for instance in topology.instances
                if instance.role is role and instance.liveness is ServiceLiveness.LIVE
            )
            if any(instance.state is ServiceState.READY for instance in live):
                role_states[role.value] = ServiceState.READY.value
            elif any(instance.state is ServiceState.DEGRADED for instance in live):
                role_states[role.value] = ServiceState.DEGRADED.value
            elif any(instance.state is ServiceState.DRAINING for instance in live):
                role_states[role.value] = ServiceState.DRAINING.value
            elif live:
                role_states[role.value] = ServiceState.STARTING.value
            else:
                role_states[role.value] = DependencyCondition.UNAVAILABLE.value
            if role_states[role.value] != ServiceState.READY.value:
                unready_roles.append(role.value)
            dependencies[f"role:{role.value}"] = (
                DependencyCondition.READY.value
                if role_states[role.value] == ServiceState.READY.value
                else DependencyCondition.UNAVAILABLE.value
            )
        if settings.service_instance_name is not None:
            registered_ready = any(
                instance.role is ServiceRole.WEBSERVER
                and instance.instance_name == settings.service_instance_name
                and instance.liveness is ServiceLiveness.LIVE
                and instance.state is ServiceState.READY
                for instance in topology.instances
            )
        registered_ready = registered_ready and not unready_roles
        dependencies["service-registry"] = (
            DependencyCondition.READY.value
            if registered_ready
            else DependencyCondition.UNAVAILABLE.value
        )
    if not readiness.ready or not registered_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(
        status=("not-ready" if not readiness.ready or not registered_ready else readiness.status),
        version=__version__,
        database=(
            "ready"
            if dependencies.get("database") == DependencyCondition.READY.value
            else "unavailable"
        ),
        migrations_applied=readiness.migrations_applied,
        migrations_expected=readiness.migrations_expected,
        latest_migration=readiness.latest_migration,
        dependencies=dependencies,
        roles=role_states,
        degraded_dependencies=readiness.degraded_dependencies,
        error=(
            f"enabled service roles not ready: {', '.join(sorted(unready_roles))}"
            if unready_roles
            else "service instance is not ready"
            if not registered_ready
            else readiness.error
        ),
    )


@app.get("/api/v1/ui/session", response_model=UiSessionResponse, tags=["ui"])
async def get_ui_session(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
) -> UiSessionResponse:
    requested_capabilities = {
        "assets.view": ("asset", PermissionAction.VIEW),
        "assets.manage": ("asset", PermissionAction.UPDATE),
        "agents.view": ("agent", PermissionAction.VIEW),
        "agents.manage": ("agent", PermissionAction.MANAGE),
        "agents.execute": ("agent", PermissionAction.EXECUTE),
        "flows.view": ("flow", PermissionAction.VIEW),
        "flows.create": ("flow", PermissionAction.CREATE),
        "flows.update": ("flow", PermissionAction.UPDATE),
        "flowTests.view": ("flow_test", PermissionAction.VIEW),
        "flowTests.manage": ("flow_test", PermissionAction.UPDATE),
        "flowTests.execute": ("flow_test", PermissionAction.EXECUTE),
        "executions.view": ("execution", PermissionAction.VIEW),
        "executions.execute": ("execution", PermissionAction.EXECUTE),
        "executions.manage": ("execution", PermissionAction.MANAGE),
        "apps.view": ("app", PermissionAction.VIEW),
        "apps.manage": ("app", PermissionAction.UPDATE),
        "apps.execute": ("app", PermissionAction.EXECUTE),
        "humanTasks.view": ("human_task", PermissionAction.VIEW),
        "humanTasks.update": ("human_task", PermissionAction.UPDATE),
        "announcements.view": ("announcement", PermissionAction.VIEW),
        "operationalControls.manage": ("operational_control", PermissionAction.MANAGE),
        "dashboards.view": ("dashboard", PermissionAction.VIEW),
        "dashboards.manage": ("dashboard", PermissionAction.UPDATE),
        "search.view": ("search", PermissionAction.VIEW),
        "search.manage": ("search", PermissionAction.MANAGE),
        "triggers.view": ("trigger", PermissionAction.VIEW),
        "triggers.manage": ("trigger", PermissionAction.MANAGE),
        "checks.view": ("check", PermissionAction.VIEW),
        "checks.manage": ("check", PermissionAction.MANAGE),
        "namespaces.view": ("namespace", PermissionAction.VIEW),
        "namespaceResources.read": ("namespace_file", PermissionAction.LIST),
        "namespaceResources.write": ("namespace_file", PermissionAction.WRITE),
        "secretBindings.write": ("secret", PermissionAction.WRITE),
        "plugins.view": ("plugin", PermissionAction.VIEW),
        "releases.view": ("release", PermissionAction.VIEW),
        "releases.manage": ("release", PermissionAction.MANAGE),
        "administration.manage": ("tenant", PermissionAction.MANAGE),
    }
    decisions = await asyncio.gather(
        *(
            authorization_service.decide(
                AuthorizationRequest(
                    actor=actor,
                    tenant_id=tenant_id,
                    namespace=namespace,
                    resource_type=resource_type,
                    action=action,
                )
            )
            for resource_type, action in requested_capabilities.values()
        )
    )
    capabilities = {
        capability: decision.allowed
        for capability, decision in zip(requested_capabilities, decisions, strict=True)
    }
    if not any(capabilities.values()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tenant unavailable",
        )
    await _charge_authorized_tenant_request(tenant_id)
    return UiSessionResponse(
        principalId=actor.principal_id,
        principalType=actor.principal_type,
        display=actor.display,
        tenantId=tenant_id,
        namespace=namespace,
        capabilities=capabilities,
        telemetryEnabled=settings.product_telemetry_enabled,
        serverVersion=__version__,
    )


async def _asset_visible(
    asset: PersistedAsset,
    *,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> bool:
    decision = await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=asset.namespace,
            resource_type="asset",
            action=PermissionAction.VIEW,
        )
    )
    return decision.allowed


@app.get(
    "/api/v1/assets/export/openlineage",
    response_model=AssetCatalogExport,
    response_model_by_alias=True,
    tags=["assets"],
)
async def export_asset_catalog(
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: Annotated[str | None, Query(max_length=255)] = None,
) -> AssetCatalogExport:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="asset",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await metadata.export_asset_catalog(tenant_id=tenant_id, namespace=namespace)


@app.get(
    "/api/v1/assets",
    response_model=tuple[PersistedAsset, ...],
    response_model_by_alias=True,
    tags=["assets"],
)
async def list_assets(
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: Annotated[str | None, Query(max_length=255)] = None,
) -> tuple[PersistedAsset, ...]:
    if namespace is not None:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="asset",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
            namespace=namespace,
        )
    assets = tuple(
        asset
        for asset in await metadata.list_assets(tenant_id=tenant_id)
        if namespace is None or asset.namespace == namespace
    )
    visible = await asyncio.gather(
        *(
            _asset_visible(
                asset,
                actor=actor,
                authorization_service=authorization_service,
                tenant_id=tenant_id,
            )
            for asset in assets
        )
    )
    if namespace is None:
        if not assets:
            await authorize_request(
                authorization_service,
                actor,
                resource_type="asset",
                action=PermissionAction.VIEW,
                tenant_id=tenant_id,
            )
        elif any(visible):
            await _charge_authorized_tenant_request(tenant_id)
    return tuple(asset for asset, allowed in zip(assets, visible, strict=True) if allowed)


@app.post(
    "/api/v1/assets",
    response_model=PersistedAsset,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    tags=["assets"],
)
async def register_asset(
    payload: AssetMetadata,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> PersistedAsset:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="asset",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=payload.namespace,
    )
    try:
        return await metadata.upsert_asset(
            payload,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except MetadataVersionConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post(
    "/api/v1/assets/observations",
    response_model=AssetObservation,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    tags=["assets"],
)
async def record_asset_observation(
    payload: AssetObservationCreate,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AssetObservation:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="asset",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=payload.asset.namespace,
    )
    return await metadata.record_asset_observation(
        payload,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
    )


@app.post(
    "/api/v1/assets/lineage",
    response_model=AssetLineageEdge,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    tags=["assets"],
)
async def declare_asset_lineage(
    payload: AssetLineageDeclaration,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AssetLineageEdge:
    try:
        upstream = await metadata.get_asset(payload.upstream_asset_id, tenant_id=tenant_id)
        downstream = await metadata.get_asset(payload.downstream_asset_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="asset unavailable"
        ) from exc
    for asset in (upstream, downstream):
        await authorize_request(
            authorization_service,
            actor,
            resource_type="asset",
            action=PermissionAction.UPDATE,
            tenant_id=tenant_id,
            namespace=asset.namespace,
        )
    return await metadata.declare_asset_lineage(
        payload,
        tenant_id=tenant_id,
        namespace=downstream.namespace,
        actor_id=str(actor.principal_id),
    )


@app.get(
    "/api/v1/assets/{asset_id}",
    response_model=AssetCatalogEntry,
    response_model_by_alias=True,
    tags=["assets"],
)
async def get_asset_catalog_entry(
    asset_id: UUID,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AssetCatalogEntry:
    try:
        entry = await metadata.get_asset_catalog_entry(asset_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="asset unavailable"
        ) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="asset",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=entry.asset.namespace,
    )
    neighbors = entry.upstream + entry.downstream
    visibility = await asyncio.gather(
        *(
            _asset_visible(
                asset,
                actor=actor,
                authorization_service=authorization_service,
                tenant_id=tenant_id,
            )
            for asset in neighbors
        )
    )
    visible_ids = {
        asset.asset_id for asset, allowed in zip(neighbors, visibility, strict=True) if allowed
    }
    visible_ids.add(entry.asset.asset_id)
    return entry.model_copy(
        update={
            "upstream": tuple(item for item in entry.upstream if item.asset_id in visible_ids),
            "downstream": tuple(item for item in entry.downstream if item.asset_id in visible_ids),
            "edges": tuple(
                edge
                for edge in entry.edges
                if edge.upstream_asset_id in visible_ids and edge.downstream_asset_id in visible_ids
            ),
        }
    )


_DASHBOARD_DATA_RESOURCES = {
    DashboardDataSource.EXECUTIONS: "execution",
    DashboardDataSource.LOGS: "execution",
    DashboardDataSource.METRICS: "execution",
    DashboardDataSource.SLA: "check",
    DashboardDataSource.WORKERS: "worker",
    DashboardDataSource.ASSETS: "asset",
}
_DASHBOARD_ADMIN_ROLES = {"instance-admin", "tenant-admin", "namespace-admin"}


def _dashboard_admin(decision: AuthorizationDecision, actor: ActorContext) -> bool:
    return actor.bootstrap_admin or bool(
        _DASHBOARD_ADMIN_ROLES.intersection(decision.matched_role_names)
    )


async def _load_dashboard(
    dashboard_id: str,
    *,
    repository: PostgresDashboardRepository,
    tenant_id: str,
) -> DashboardDefinition:
    if dashboard_id.startswith("builtin."):
        try:
            return builtin_dashboard(dashboard_id, tenant_id)
        except LookupError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="dashboard unavailable"
            ) from exc
    try:
        return await repository.get_definition(dashboard_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="dashboard unavailable"
        ) from exc


async def _authorize_dashboard_source(
    query: DashboardQuery,
    *,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> AuthorizationDecision:
    return await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=query.filters.namespace,
            resource_type=_DASHBOARD_DATA_RESOURCES[query.source],
            action=PermissionAction.VIEW,
        )
    )


@app.get(
    "/api/v1/dashboards",
    response_model=list[DashboardDefinition],
    tags=["dashboards"],
)
async def list_dashboards(
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[DashboardDefinition]:
    decision = await authorize_request(
        authorization_service,
        actor,
        resource_type="dashboard",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    custom = await repository.list_definitions(tenant_id=tenant_id)
    principal_id = str(actor.principal_id)
    visible = [
        definition
        for definition in custom
        if _dashboard_admin(decision, actor) or can_view_dashboard(definition, principal_id)
    ]
    return [*builtin_dashboards(tenant_id), *visible]


@app.post(
    "/api/v1/dashboard-queries",
    response_model=DashboardQueryResult,
    tags=["dashboards"],
)
async def execute_dashboard_query(
    query: DashboardQuery,
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> DashboardQueryResult:
    decision = await _authorize_dashboard_source(
        query,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
    )
    if not decision.allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="dashboard data unavailable"
        )
    await _charge_authorized_tenant_request(tenant_id)
    try:
        return await repository.execute_query(query, tenant_id=tenant_id)
    except DashboardQueryTimeout as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc


@app.get(
    "/api/v1/dashboards/{dashboard_id}",
    response_model=DashboardDefinition,
    tags=["dashboards"],
)
async def get_dashboard(
    dashboard_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> DashboardDefinition:
    decision = await authorize_request(
        authorization_service,
        actor,
        resource_type="dashboard",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    definition = await _load_dashboard(dashboard_id, repository=repository, tenant_id=tenant_id)
    if not _dashboard_admin(decision, actor) and not can_view_dashboard(
        definition, str(actor.principal_id)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dashboard unavailable")
    return definition


@app.post(
    "/api/v1/dashboards/{dashboard_id}/render",
    response_model=DashboardRender,
    tags=["dashboards"],
)
async def render_dashboard(
    dashboard_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    filters: DashboardFilters,
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> DashboardRender:
    definition = await get_dashboard(
        dashboard_id,
        repository,
        actor,
        authorization_service,
        tenant_id,
    )
    widget_results: list[DashboardWidgetResult] = []
    for widget in definition.widgets:
        query = apply_dashboard_filters(widget.query, filters)
        decision = await _authorize_dashboard_source(
            query,
            actor=actor,
            authorization_service=authorization_service,
            tenant_id=tenant_id,
        )
        if not decision.allowed:
            result = DashboardQueryResult(
                columns=(),
                rows=(),
                freshAt=datetime.now(UTC),
                partial=False,
                sampled=query.sample_rate < 1,
                redacted=True,
                scannedRows=0,
                limit=query.limit,
            )
        else:
            try:
                result = await repository.execute_query(query, tenant_id=tenant_id)
            except DashboardQueryTimeout as exc:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"widget {widget.widget_id}: {exc}",
                ) from exc
        widget_results.append(DashboardWidgetResult(widgetId=widget.widget_id, result=result))
    return DashboardRender(dashboard=definition, widgets=tuple(widget_results))


@app.put(
    "/api/v1/dashboards/{dashboard_id}",
    response_model=DashboardDefinition,
    tags=["dashboards"],
)
async def put_dashboard(
    dashboard_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    spec: DashboardSpec,
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> DashboardDefinition:
    decision = await authorize_request(
        authorization_service,
        actor,
        resource_type="dashboard",
        action=PermissionAction.CREATE if expected_version is None else PermissionAction.UPDATE,
        tenant_id=tenant_id,
    )
    if dashboard_id.startswith("builtin.") or spec.source.value == "BUILTIN":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="built-in dashboards are immutable",
        )
    if expected_version is not None:
        existing = await _load_dashboard(dashboard_id, repository=repository, tenant_id=tenant_id)
        if not _dashboard_admin(decision, actor) and not can_edit_dashboard(
            existing, str(actor.principal_id)
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="dashboard unavailable"
            )
    try:
        return await repository.upsert_definition(
            dashboard_id,
            spec,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except DashboardVersionConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.delete(
    "/api/v1/dashboards/{dashboard_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["dashboards"],
)
async def delete_dashboard(
    dashboard_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int, Query(alias="expectedVersion", ge=1)],
) -> Response:
    decision = await authorize_request(
        authorization_service,
        actor,
        resource_type="dashboard",
        action=PermissionAction.DELETE,
        tenant_id=tenant_id,
    )
    definition = await _load_dashboard(dashboard_id, repository=repository, tenant_id=tenant_id)
    if not _dashboard_admin(decision, actor) and not can_edit_dashboard(
        definition, str(actor.principal_id)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dashboard unavailable")
    try:
        await repository.delete_definition(
            dashboard_id,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except DashboardVersionConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/v1/dashboards/{dashboard_id}/export", tags=["dashboards"])
async def export_dashboard(
    dashboard_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    format: Literal["yaml", "json"] = "yaml",
) -> Response:
    definition = await get_dashboard(
        dashboard_id,
        repository,
        actor,
        authorization_service,
        tenant_id,
    )
    payload = definition.model_dump(mode="json", by_alias=True)
    if format == "json":
        content = json.dumps(payload, indent=2, sort_keys=True)
        media_type = "application/json"
        suffix = "json"
    else:
        content = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
        media_type = "application/yaml"
        suffix = "yaml"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{dashboard_id}.{suffix}"'},
    )


_SEARCH_DATA_RESOURCES = {
    SearchDocumentType.FLOW: "flow",
    SearchDocumentType.EXECUTION: "execution",
    SearchDocumentType.TASK_RUN: "execution",
    SearchDocumentType.LOG: "execution",
    SearchDocumentType.METRIC: "execution",
    SearchDocumentType.ASSET: "asset",
    SearchDocumentType.AUDIT: "audit",
}


@app.post("/api/v1/search", response_model=SearchResponse, tags=["search"])
async def search_resources(
    request: SearchRequest,
    repository: SearchRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SearchResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="search",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=request.namespace,
    )
    requested_types = request.types or tuple(SearchDocumentType)
    decisions = await asyncio.gather(
        *(
            authorization_service.decide(
                AuthorizationRequest(
                    actor=actor,
                    tenant_id=tenant_id,
                    namespace=request.namespace,
                    resource_type=_SEARCH_DATA_RESOURCES[document_type],
                    action=PermissionAction.VIEW,
                )
            )
            for document_type in requested_types
        )
    )
    authorized = tuple(
        document_type
        for document_type, decision in zip(requested_types, decisions, strict=True)
        if decision.allowed
    )
    denied = tuple(
        document_type
        for document_type, decision in zip(requested_types, decisions, strict=True)
        if not decision.allowed
    )
    try:
        return await repository.search(
            request,
            tenant_id=tenant_id,
            authorized_types=authorized,
            denied_types=denied,
        )
    except SearchCursorError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SearchUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/search/status",
    response_model=SearchProjectionStatus,
    tags=["search"],
)
async def get_search_status(
    repository: SearchRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SearchProjectionStatus:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="search",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return await repository.status(tenant_id=tenant_id)
    except SearchUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/v1/search/rebuild",
    response_model=SearchProjectionStatus,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["search"],
)
async def rebuild_search_projection(
    request: SearchRebuildRequest,
    repository: SearchRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SearchProjectionStatus:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="search",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.request_rebuild(
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            reason=request.reason,
            document_types=request.types,
            from_time=request.from_time,
            to_time=request.to_time,
        )
    except SearchUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/search/verify",
    response_model=SearchProjectionVerification,
    tags=["search"],
)
async def verify_search_projection(
    repository: SearchRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SearchProjectionVerification:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="search",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.verify(tenant_id=tenant_id)
    except SearchUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/v1/search/control",
    response_model=SearchProjectionStatus,
    tags=["search"],
)
async def control_search_projection(
    request: SearchProjectionControlRequest,
    repository: SearchRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SearchProjectionStatus:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="search",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.set_enabled(
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            enabled=request.enabled,
            reason=request.reason,
        )
    except SearchUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/plugins",
    response_model=PluginCatalogSnapshot,
    tags=["plugins"],
)
async def list_plugins(
    catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginCatalogSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return catalog.snapshot


@app.get(
    "/api/v1/plugin-policy/effective",
    response_model=EffectivePluginPolicy,
    tags=["plugins"],
)
async def get_effective_plugin_policy(
    service: PluginPolicyServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
) -> EffectivePluginPolicy:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await service.effective_policy(tenant_id, namespace=namespace)


@app.get(
    "/api/v1/plugin-policy/decisions",
    response_model=tuple[PluginPolicyDecision, ...],
    tags=["plugins"],
)
async def list_plugin_policy_decisions(
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> tuple[PluginPolicyDecision, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_decisions(tenant_id, limit=limit)


@app.post(
    "/api/v1/plugin-policy/evaluate",
    response_model=PluginPolicyDecision,
    tags=["plugins"],
)
async def evaluate_flow_plugin_policy(
    request: Request,
    service: PluginPolicyServiceDependency,
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    stage: PluginPolicyStage = PluginPolicyStage.VALIDATION,
) -> PluginPolicyDecision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=(
            PermissionAction.MANAGE
            if stage is PluginPolicyStage.ADMINISTRATION
            else PermissionAction.VIEW
        ),
        tenant_id=tenant_id,
    )
    try:
        result = validate_flow_document(
            await request.body(),
            registry=plugin_catalog.resource_registry(),
        )
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if not result.valid or result.canonical is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[issue.model_dump(mode="json", by_alias=True) for issue in result.issues],
        )
    flow = FlowDefinition.model_validate(result.canonical)
    return await service.evaluate_flow(
        flow,
        tenant_id=tenant_id,
        stage=stage,
        actor_id=str(actor.principal_id),
    )


@app.get(
    "/api/v1/policies",
    response_model=tuple[PolicyRevision, ...],
    tags=["policies"],
)
async def list_admission_policies(
    repository: AdmissionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: str = "default",
) -> tuple[PolicyRevision, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.effective_revisions(tenant_id, namespace=namespace)


@app.post(
    "/api/v1/policies",
    response_model=PolicyRevision,
    status_code=status.HTTP_201_CREATED,
    tags=["policies"],
)
async def create_admission_policy(
    request: PolicyDocument,
    repository: AdmissionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PolicyRevision:
    await _authorize_admission_policy_change(
        request,
        actor,
        authorization_service,
        tenant_id,
    )
    return await repository.save_revision(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@app.post(
    "/api/v1/policies/evaluate",
    response_model=PolicyDecision,
    tags=["policies"],
)
async def evaluate_admission_policies(
    request: PolicyEvaluationRequest,
    service: AdmissionPolicyServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PolicyDecision:
    namespace = request.input.namespace.id
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    evaluated_input = request.input.model_copy(
        update={
            "actor": request.input.actor.model_copy(
                update={
                    "principal_id": str(actor.principal_id),
                    "principal_type": actor.principal_type.value,
                    "display": actor.display,
                }
            ),
            "tenant": request.input.tenant.model_copy(update={"id": tenant_id}),
        }
    )
    return await service.evaluate(request.model_copy(update={"input": evaluated_input}))


@app.post(
    "/api/v1/policies/flows/validate",
    response_model=PolicyDecision,
    tags=["policies"],
)
async def validate_flow_admission_policy(
    request: Request,
    service: AdmissionPolicyServiceDependency,
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PolicyDecision:
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="flow document exceeds the 2 MiB policy-validation limit",
        )
    try:
        result = validate_flow_document(
            body,
            registry=plugin_catalog.resource_registry(),
        )
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if not result.valid or result.canonical is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[issue.model_dump(mode="json", by_alias=True) for issue in result.issues],
        )
    flow = FlowDefinition.model_validate(result.canonical)
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=flow.namespace,
    )
    return await service.evaluate(
        PolicyEvaluationRequest(
            stage=PolicyStage.VALIDATE,
            input=policy_input_from_flow(
                flow,
                tenant_id=tenant_id,
                actor=actor,
            ),
        )
    )


@app.get(
    "/api/v1/policies/decisions",
    response_model=tuple[PolicyDecision, ...],
    tags=["policies"],
)
async def list_admission_policy_decisions(
    repository: AdmissionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> tuple[PolicyDecision, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_decisions(tenant_id, limit=limit)


@app.get(
    "/api/v1/policies/{policy_key}",
    response_model=PolicyRevision,
    tags=["policies"],
)
async def get_admission_policy(
    policy_key: str,
    repository: AdmissionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> PolicyRevision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return await repository.get_revision(
            tenant_id,
            policy_key,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.put(
    "/api/v1/policies/{policy_key}",
    response_model=PolicyRevision,
    tags=["policies"],
)
async def update_admission_policy(
    policy_key: str,
    request: PolicyDocument,
    repository: AdmissionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PolicyRevision:
    if policy_key != request.policy_key:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="policy key does not match request document",
        )
    await _authorize_admission_policy_change(
        request,
        actor,
        authorization_service,
        tenant_id,
    )
    return await repository.save_revision(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@app.post(
    "/api/v1/policies/{policy_key}/test",
    response_model=PolicyFixtureResult,
    tags=["policies"],
)
async def test_admission_policy(
    policy_key: str,
    request: PolicyFixture,
    service: AdmissionPolicyServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> PolicyFixtureResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=request.request.input.namespace.id,
    )
    try:
        return await service.test_fixture(
            tenant_id,
            policy_key,
            request,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/plugin-policy/rules",
    response_model=PluginPolicyRule,
    status_code=status.HTTP_201_CREATED,
    tags=["plugins"],
)
async def create_plugin_policy_rule(
    request: PluginPolicyRuleCreate,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginPolicyRule:
    await _authorize_plugin_policy_change(
        request.scope,
        request.namespace,
        actor,
        authorization_service,
        tenant_id,
    )
    return await repository.create_rule(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@app.put(
    "/api/v1/plugin-policy/rules/{rule_id}",
    response_model=PluginPolicyRule,
    tags=["plugins"],
)
async def update_plugin_policy_rule(
    rule_id: UUID,
    request: PluginPolicyRuleCreate,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginPolicyRule:
    await _authorize_plugin_policy_change(
        request.scope,
        request.namespace,
        actor,
        authorization_service,
        tenant_id,
    )
    try:
        return await repository.update_rule(
            tenant_id,
            rule_id,
            request,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get(
    "/api/v1/plugin-policy/rules/{rule_id}",
    response_model=PluginPolicyRule,
    tags=["plugins"],
)
async def get_plugin_policy_rule(
    rule_id: UUID,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginPolicyRule:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return await repository.get_rule(tenant_id, rule_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete(
    "/api/v1/plugin-policy/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["plugins"],
)
async def delete_plugin_policy_rule(
    rule_id: UUID,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    try:
        await repository.delete_rule(
            tenant_id,
            rule_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/api/v1/plugin-policy/quarantines/preview",
    response_model=PluginPolicyImpactPreview,
    tags=["plugins"],
)
async def preview_plugin_quarantine(
    request: PluginQuarantineCreate,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginPolicyImpactPreview:
    await _authorize_plugin_policy_change(
        request.scope,
        request.namespace,
        actor,
        authorization_service,
        tenant_id,
    )
    return await repository.impact_preview(tenant_id, request)


@app.post(
    "/api/v1/plugin-policy/quarantines",
    response_model=PluginQuarantine,
    status_code=status.HTTP_201_CREATED,
    tags=["plugins"],
)
async def quarantine_plugin_version(
    request: PluginQuarantineCreate,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginQuarantine:
    await _authorize_plugin_policy_change(
        request.scope,
        request.namespace,
        actor,
        authorization_service,
        tenant_id,
    )
    try:
        return await repository.create_quarantine(
            tenant_id,
            request,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post(
    "/api/v1/plugin-policy/quarantines/{quarantine_id}/release",
    response_model=PluginQuarantine,
    tags=["plugins"],
)
async def release_plugin_quarantine(
    quarantine_id: UUID,
    repository: PluginPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    reason: Annotated[str, Query(min_length=1, max_length=2048)],
) -> PluginQuarantine:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    try:
        return await repository.release_quarantine(
            tenant_id,
            quarantine_id,
            actor_id=str(actor.principal_id),
            reason=reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get(
    "/api/v1/plugins/trusted-runtime",
    response_model=TrustedPluginRuntimeSnapshot,
    tags=["plugins"],
)
async def trusted_plugin_runtime_status(
    runtime: TrustedPluginRuntimeDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> TrustedPluginRuntimeSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    await runtime.ensure_started()
    return runtime.snapshot()


@app.get(
    "/api/v1/plugins/isolated-runtime",
    response_model=IsolatedPluginRuntimeSnapshot,
    tags=["plugins"],
)
async def isolated_plugin_runtime_status(
    runtime: IsolatedPluginRuntimeDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> IsolatedPluginRuntimeSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    await runtime.ensure_configured()
    return runtime.snapshot()


@app.post(
    "/api/v1/plugins/refresh",
    response_model=PluginCatalogSnapshot,
    tags=["plugins"],
)
async def refresh_plugins(
    catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginCatalogSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    return catalog.refresh()


@app.post(
    "/api/v1/plugins/install",
    response_model=PluginCatalogSnapshot,
    tags=["plugins"],
)
async def install_plugin_bundle(
    request: Request,
    catalog: PluginCatalogDependency,
    policy: PluginPolicyServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    content_digest: Annotated[
        str,
        Query(alias="contentDigest", pattern=r"^sha256:[0-9a-f]{64}$"),
    ],
) -> PluginCatalogSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    content = await request.body()
    if len(content) > 64 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="plugin bundle exceeds the 64 MiB installation limit",
        )
    try:
        manifest = catalog.inspect_offline_bundle_bytes(
            content,
            expected_digest=content_digest,
        )
        await policy.enforce_manifest_administration(
            manifest,
            content_digest,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
        catalog.install_offline_bundle_bytes(content, expected_digest=content_digest)
    except PluginPolicyDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return catalog.snapshot


@app.get(
    "/api/v1/plugin-registry/index",
    response_model=PluginRegistryIndex,
    tags=["plugins"],
)
async def get_plugin_registry_index(
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginRegistryIndex:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return registry.snapshot()


@app.post(
    "/api/v1/plugin-registry/packages",
    response_model=PluginRegistryPackage,
    tags=["plugins"],
)
async def publish_plugin_registry_package(
    request: PluginRegistryPublishRequest,
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginRegistryPackage:
    del tenant_id
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    try:
        return registry.publish_request(request)
    except (OSError, ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/plugin-registry/packages/{name}/{version}",
    response_model=PluginRegistryPackage,
    tags=["plugins"],
)
async def get_plugin_registry_package(
    name: str,
    version: str,
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginRegistryPackage:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return registry.release(name, version)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/plugin-registry/packages/{name}/{version}/yank",
    response_model=PluginRegistryPackage,
    tags=["plugins"],
)
async def yank_plugin_registry_package(
    name: str,
    version: str,
    request: PluginRegistryYankRequest,
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginRegistryPackage:
    del tenant_id
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    try:
        return registry.yank(name, version, reason=request.reason)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get(
    "/api/v1/plugin-registry/blobs/{digest}",
    response_class=Response,
    tags=["plugins"],
)
async def download_plugin_registry_bundle(
    digest: Annotated[str, PathParameter(pattern=r"^[0-9a-f]{64}$")],
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        content = registry.download(f"sha256:{digest}")
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(content=content, media_type="application/vnd.amesh.plugin+zip")


@app.get(
    "/api/v1/plugin-registry/offline-export",
    response_class=Response,
    tags=["plugins"],
)
async def export_plugin_registry(
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return Response(
        content=registry.export_offline(),
        media_type="application/vnd.amesh.plugin-registry+zip",
        headers={"Content-Disposition": 'attachment; filename="amesh-plugin-registry.zip"'},
    )


@app.post(
    "/api/v1/plugin-registry/offline-import",
    response_model=PluginRegistryIndex,
    tags=["plugins"],
)
async def import_plugin_registry(
    request: Request,
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PluginRegistryIndex:
    del tenant_id
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
    )
    content = await request.body()
    if len(content) > 256 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="offline plugin registry bundle exceeds 256 MiB",
        )
    try:
        return registry.import_offline(content)
    except (OSError, ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/configuration",
    response_model=ConfigurationSnapshot,
    tags=["configuration"],
)
async def get_effective_configuration(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    configuration: ConfigurationManagerDependency,
) -> ConfigurationSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="configuration",
        action=PermissionAction.VIEW,
    )
    return configuration.snapshot()


@app.post(
    "/api/v1/configuration/reload",
    response_model=ConfigurationSnapshot,
    tags=["configuration"],
)
async def reload_configuration(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    configuration: ConfigurationManagerDependency,
    feature_flags: FeatureFlagRepositoryDependency,
) -> ConfigurationSnapshot:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="configuration",
        action=PermissionAction.MANAGE,
    )
    before = configuration.snapshot()
    try:
        after = configuration.reload()
    except NonReloadableConfigurationChanged as exc:
        await feature_flags.audit_configuration_reload(
            actor_id=str(actor.principal_id),
            outcome="REJECTED",
            changed_fields=exc.fields,
            reason="restart-required setting changed",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ConfigurationLoadError as exc:
        await feature_flags.audit_configuration_reload(
            actor_id=str(actor.principal_id),
            outcome="REJECTED",
            changed_fields=(),
            reason="candidate configuration failed validation",
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    before_entries = {entry.name: entry for entry in before.entries}
    changed = tuple(
        entry.name
        for entry in after.entries
        if before_entries[entry.name].value != entry.value
        or before_entries[entry.name].source != entry.source
    )
    configure_observability(configuration.settings)
    await feature_flags.audit_configuration_reload(
        actor_id=str(actor.principal_id),
        outcome="SUCCESS",
        changed_fields=changed,
        reason="reload accepted",
    )
    return after


@app.get(
    "/api/v1/configuration/diagnostics",
    response_model=ConfigurationDiagnosticBundle,
    tags=["configuration"],
)
async def get_configuration_diagnostics(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    configuration: ConfigurationManagerDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
) -> ConfigurationDiagnosticBundle:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        namespace=namespace,
        resource_type="configuration",
        action=PermissionAction.VIEW,
    )
    recent_errors = tuple(
        entry
        for entry in recent_redacted_logs(limit=50, tenant_id=tenant_id)
        if entry.get("level") in {"ERROR", "CRITICAL"}
    )
    return ConfigurationDiagnosticBundle(
        generatedAt=datetime.now(UTC),
        tenantId=tenant_id,
        namespace=namespace,
        configuration=configuration.snapshot(),
        featureFlags=await feature_flags.list_for_context(tenant_id, namespace=namespace),
        componentHealth={configuration.settings.service_role: "AVAILABLE"},
        versionMatrix={"amesh": __version__},
        recentErrors=recent_errors,
        selectedMetrics=diagnostic_metric_samples(),
    )


@app.get(
    "/api/v1/operations/network-diagnostics",
    response_model=NetworkDiagnosticBundle,
    tags=["operations"],
)
async def get_network_diagnostics(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
) -> NetworkDiagnosticBundle:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="configuration",
        action=PermissionAction.VIEW,
    )
    return await build_network_diagnostics(settings)


@app.get(
    "/api/v1/feature-flags",
    response_model=tuple[FeatureFlag, ...],
    tags=["configuration"],
)
async def list_feature_flags(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
) -> tuple[FeatureFlag, ...]:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        namespace=namespace,
        resource_type="feature_flag",
        action=PermissionAction.VIEW,
    )
    return await feature_flags.list_for_context(tenant_id, namespace=namespace)


@app.get(
    "/api/v1/feature-flags/{key}/evaluate",
    response_model=FeatureFlagDecision,
    tags=["configuration"],
)
async def evaluate_feature_flag(
    key: str,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
    default: bool = False,
) -> FeatureFlagDecision:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        namespace=namespace,
        resource_type="feature_flag",
        action=PermissionAction.VIEW,
    )
    return await feature_flags.evaluate(
        key,
        tenant_id,
        namespace=namespace,
        default=default,
    )


@app.put(
    "/api/v1/feature-flags/{key}",
    response_model=FeatureFlag,
    tags=["configuration"],
)
async def put_feature_flag(
    key: str,
    request: FeatureFlagUpsertRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
) -> FeatureFlag:
    if key.startswith("admin-"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="reserved administration controls require the guarded administration API",
        )
    if request.scope is FeatureFlagScope.INSTANCE:
        if request.tenant_id is not None or request.namespace is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="instance feature flag cannot declare tenant or namespace",
            )
        scope_tenant = None
        scope_namespace = None
    else:
        if request.tenant_id is not None and request.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant unavailable")
        scope_tenant = tenant_id
        scope_namespace = request.namespace
        if request.scope is FeatureFlagScope.TENANT and scope_namespace is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="tenant feature flag cannot declare namespace",
            )
        if request.scope is FeatureFlagScope.NAMESPACE and scope_namespace is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="namespace feature flag requires namespace",
            )
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=scope_tenant,
        namespace=scope_namespace,
        resource_type="feature_flag",
        action=PermissionAction.MANAGE,
    )
    flag = FeatureFlag(
        key=key,
        scope=request.scope,
        enabled=request.enabled,
        tenant_id=scope_tenant,
        namespace=scope_namespace,
        description=request.description,
        updated_by=str(actor.principal_id),
    )
    try:
        return await feature_flags.upsert(
            flag,
            actor_id=str(actor.principal_id),
            expected_version=request.expected_version,
        )
    except FeatureFlagVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="feature flag version changed",
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tenant unavailable"
        ) from exc


@app.get(
    "/api/v1/admin/controls",
    response_model=tuple[AdministrationControl, ...],
    tags=["administration"],
)
async def list_administration_controls(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
) -> tuple[AdministrationControl, ...]:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="configuration",
        action=PermissionAction.VIEW,
    )
    return administration_controls(await feature_flags.list_for_context(tenant_id))


@app.post(
    "/api/v1/admin/controls/preview",
    response_model=AdministrationImpactPreview,
    tags=["administration"],
)
async def preview_administration_control(
    draft: AdministrationControlDraft,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
) -> AdministrationImpactPreview:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="configuration",
        action=PermissionAction.MANAGE,
    )
    return issue_administration_preview(
        draft,
        actor_id=str(actor.principal_id),
        tenant_id=tenant_id,
        signing_key=settings.amesh_token_pepper.get_secret_value(),
    )


@app.put(
    "/api/v1/admin/controls/{key}",
    response_model=AdministrationControl,
    tags=["administration"],
)
async def apply_administration_control(
    key: AdministrationControlKey,
    request: AdministrationApplyRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
) -> AdministrationControl:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="configuration",
        action=PermissionAction.MANAGE,
    )
    actor_id = str(actor.principal_id)
    try:
        if request.draft.key is not key:
            raise AdministrationApprovalError("administration control path does not match draft")
        verify_administration_approval(
            request,
            actor_id=actor_id,
            tenant_id=tenant_id,
            signing_key=settings.amesh_token_pepper.get_secret_value(),
        )
    except AdministrationApprovalError as exc:
        await feature_flags.audit_administration_action(
            tenant_id,
            actor_id=actor_id,
            action="administration-control.apply",
            resource_id=key.value,
            outcome="REJECTED",
            reason=str(exc),
            evidence={"enabled": request.draft.enabled, "value": request.draft.value},
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    flag = administration_control_flag(request.draft, tenant_id=tenant_id, actor_id=actor_id)
    try:
        persisted = await feature_flags.upsert(
            flag,
            actor_id=actor_id,
            expected_version=request.draft.expected_version,
            administration_audit={
                "action": "administration-control.apply",
                "resourceId": key.value,
                "reason": request.draft.reason,
                "evidence": {"enabled": request.draft.enabled, "value": request.draft.value},
            },
        )
    except FeatureFlagVersionConflict as exc:
        await feature_flags.audit_administration_action(
            tenant_id,
            actor_id=actor_id,
            action="administration-control.apply",
            resource_id=key.value,
            outcome="REJECTED",
            reason="administration control version changed",
            evidence={"expectedVersion": request.draft.expected_version},
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="administration control version changed",
        ) from exc
    return next(control for control in administration_controls((persisted,)) if control.key is key)


@app.get(
    "/api/v1/admin/audit",
    response_model=tuple[AdministrationAuditEntry, ...],
    tags=["administration"],
)
async def list_administration_audit(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    feature_flags: FeatureFlagRepositoryDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> tuple[AdministrationAuditEntry, ...]:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="audit",
        action=PermissionAction.VIEW,
    )
    return await feature_flags.list_administration_audit(tenant_id, limit=limit)


@app.get(
    "/api/v1/announcements",
    response_model=tuple[Announcement, ...],
    tags=["operations"],
)
async def list_announcements(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    repository: OperationalControlRepositoryDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
    include_inactive: Annotated[bool, Query(alias="includeInactive")] = False,
) -> tuple[Announcement, ...]:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        namespace=namespace,
        resource_type="announcement",
        action=PermissionAction.VIEW,
    )
    return await repository.list_announcements(
        tenant_id,
        namespace=namespace,
        include_inactive=include_inactive,
    )


@app.post(
    "/api/v1/announcements",
    response_model=Announcement,
    status_code=status.HTTP_201_CREATED,
    tags=["operations"],
)
async def publish_announcement(
    request: AnnouncementCreateRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    repository: OperationalControlRepositoryDependency,
    tenant_id: TenantDependency,
) -> Announcement:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=None if request.audience is AnnouncementAudience.INSTANCE else tenant_id,
        namespace=request.namespace,
        resource_type="announcement",
        action=PermissionAction.MANAGE,
    )
    return await repository.create_announcement(
        request,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
    )


@app.delete(
    "/api/v1/announcements/{announcement_id}",
    response_model=Announcement,
    tags=["operations"],
)
async def deactivate_announcement(
    announcement_id: UUID,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    repository: OperationalControlRepositoryDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int, Query(alias="expectedVersion", ge=1)],
) -> Announcement:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="announcement",
        action=PermissionAction.MANAGE,
    )
    try:
        return await repository.deactivate_announcement(
            announcement_id,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except OperationalControlVersionConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/operational-controls",
    response_model=tuple[OperationalControl, ...],
    tags=["operations"],
)
async def list_operational_controls(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    repository: OperationalControlRepositoryDependency,
    tenant_id: TenantDependency,
) -> tuple[OperationalControl, ...]:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="operational_control",
        action=PermissionAction.VIEW,
    )
    return await repository.list_controls(tenant_id)


@app.post(
    "/api/v1/operational-controls",
    response_model=OperationalControl,
    status_code=status.HTTP_201_CREATED,
    tags=["operations"],
)
async def activate_operational_control(
    request: OperationalControlCreateRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    repository: OperationalControlRepositoryDependency,
    tenant_id: TenantDependency,
) -> OperationalControl:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=None if request.scope is OperationalControlScope.INSTANCE else tenant_id,
        namespace=request.namespace,
        resource_type="operational_control",
        action=PermissionAction.MANAGE,
    )
    return await repository.create_control(
        request,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
    )


@app.post(
    "/api/v1/operational-controls/{control_id}/actions",
    response_model=OperationalControl,
    tags=["operations"],
)
async def change_operational_control(
    control_id: UUID,
    request: OperationalControlActionRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    repository: OperationalControlRepositoryDependency,
    tenant_id: TenantDependency,
) -> OperationalControl:
    try:
        control = await repository.get_control(control_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=None if control.scope is OperationalControlScope.INSTANCE else tenant_id,
        namespace=control.namespace,
        resource_type="operational_control",
        action=PermissionAction.MANAGE,
    )
    try:
        return await repository.apply_action(
            control_id,
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except OperationalControlVersionConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/operational-control-events",
    response_model=tuple[OperationalControlEvent, ...],
    tags=["operations"],
)
async def list_operational_control_events(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    repository: OperationalControlRepositoryDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
) -> tuple[OperationalControlEvent, ...]:
    await authorize_request(
        authorization_service,
        actor,
        tenant_id=tenant_id,
        resource_type="audit",
        action=PermissionAction.VIEW,
    )
    return await repository.list_events(tenant_id, limit=limit)


@app.get(
    "/api/v1/auth/providers",
    response_model=tuple[AuthenticationProviderDescriptor, ...],
    tags=["authentication"],
)
async def list_authentication_providers(
    authentication_service: AuthenticationServiceDependency,
    federation_service: FederationServiceDependency,
    identifier: Annotated[str | None, Query(max_length=255)] = None,
    tenant: Annotated[str | None, Query(max_length=128)] = None,
) -> tuple[AuthenticationProviderDescriptor, ...]:
    routed = federation_service.descriptors(identifier=identifier, tenant=tenant)
    by_id = {provider.id: provider for provider in authentication_service.providers()}
    by_id.update({provider.id: provider for provider in routed})
    return tuple(by_id.values())


@app.get(
    "/api/v1/auth/federated/{provider_id}/start",
    response_class=RedirectResponse,
    tags=["authentication"],
)
async def begin_federated_login(
    provider_id: str,
    request: Request,
    federation_service: FederationServiceDependency,
    tenant: Annotated[str | None, Query(max_length=128)] = None,
    return_to: Annotated[str, Query(alias="returnTo", max_length=2048)] = "/",
) -> RedirectResponse:
    try:
        provider = federation_service.provider(provider_id)
        if provider.kind == "oidc":
            location = await federation_service.begin_oidc(
                provider_id,
                tenant=tenant,
                return_to=return_to,
            )
        elif provider.kind == "saml":
            location = await federation_service.begin_saml(
                provider_id,
                _saml_request_data(request),
                tenant=tenant,
                return_to=return_to,
            )
        else:
            raise FederationRejected("LDAP providers use password login")
    except FederationProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except FederationRejected as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RedirectResponse(location, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get(
    "/api/v1/auth/federated/{provider_id}/callback",
    response_class=RedirectResponse,
    tags=["authentication"],
)
async def complete_oidc_login(
    provider_id: str,
    response: Response,
    federation_service: FederationServiceDependency,
    settings: SettingsDependency,
    state_token: Annotated[str, Query(alias="state", min_length=1, max_length=2048)],
    code: Annotated[str | None, Query(max_length=4096)] = None,
    error: Annotated[str | None, Query(max_length=255)] = None,
) -> RedirectResponse:
    if error is not None or code is None:
        with suppress(FederationRejected, FederationStateRejected):
            await federation_service.reject_oidc(
                provider_id,
                state_token=state_token,
                reason=error or "authorization-code-missing",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="identity provider denied authentication",
        )
    try:
        issued, return_to = await federation_service.complete_oidc(
            provider_id,
            state_token=state_token,
            code=code,
        )
    except FederationProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except (
        AmbiguousFederatedIdentity,
        FederationRejected,
        FederationReplayRejected,
        FederationStateRejected,
        PermissionError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="federated authentication failed",
        ) from exc
    redirect = RedirectResponse(return_to, status_code=status.HTTP_303_SEE_OTHER)
    _set_issued_session_cookies(redirect, settings, issued)
    response.headers.update(redirect.headers)
    return redirect


@app.post(
    "/api/v1/auth/federated/{provider_id}/callback",
    response_class=RedirectResponse,
    tags=["authentication"],
)
async def complete_saml_login(
    provider_id: str,
    request: Request,
    response: Response,
    federation_service: FederationServiceDependency,
    settings: SettingsDependency,
) -> RedirectResponse:
    post_data = _urlencoded_form(await request.body())
    state_token = post_data.get("RelayState", "")
    if not state_token or "SAMLResponse" not in post_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid SAML callback")
    try:
        issued, return_to = await federation_service.complete_saml(
            provider_id,
            _saml_request_data(request, post_data=post_data),
            state_token=state_token,
        )
    except FederationProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except (
        AmbiguousFederatedIdentity,
        FederationRejected,
        FederationReplayRejected,
        FederationStateRejected,
        PermissionError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="federated authentication failed",
        ) from exc
    redirect = RedirectResponse(return_to, status_code=status.HTTP_303_SEE_OTHER)
    _set_issued_session_cookies(redirect, settings, issued)
    response.headers.update(redirect.headers)
    return redirect


@app.get(
    "/api/v1/auth/federated/{provider_id}/saml/metadata",
    response_class=PlainTextResponse,
    tags=["authentication"],
)
async def saml_service_provider_metadata(
    provider_id: str,
    federation_service: FederationServiceDependency,
) -> PlainTextResponse:
    try:
        metadata = federation_service.saml_metadata(provider_id)
    except (FederationProviderUnavailable, FederationRejected) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PlainTextResponse(metadata, media_type="application/samlmetadata+xml")


@app.get("/scim/v2/ServiceProviderConfig", tags=["scim"])
async def scim_service_provider_config(
    provider: ScimProviderDependency,
) -> dict[str, object]:
    del provider
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "patch": {"supported": True},
        "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
        "filter": {"supported": True, "maxResults": 200},
        "changePassword": {"supported": False},
        "sort": {"supported": False},
        "etag": {"supported": True},
        "authenticationSchemes": [
            {
                "type": "oauthbearertoken",
                "name": "Bearer token",
                "description": "Tenant-bound token loaded from a rotatable file",
                "specUri": "https://www.rfc-editor.org/rfc/rfc6750",
                "primary": True,
            }
        ],
    }


@app.get(
    "/scim/v2/Users",
    response_model=ScimListResponse,
    response_model_by_alias=True,
    tags=["scim"],
)
async def list_scim_users(
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
    filter_value: Annotated[str | None, Query(alias="filter", max_length=1024)] = None,
    start_index: Annotated[int, Query(alias="startIndex", ge=1)] = 1,
    count: Annotated[int, Query(ge=0, le=200)] = 100,
) -> ScimListResponse:
    handle = _scim_filter_value(filter_value, "userName")
    records = await repository.list_scim(provider.id, "User", handle=handle)
    selected = records[start_index - 1 : start_index - 1 + count]
    resources = tuple(_scim_user_resource(record) for record in selected)
    return ScimListResponse(
        totalResults=len(records),
        startIndex=start_index,
        itemsPerPage=len(resources),
        Resources=resources,
    )


@app.post(
    "/scim/v2/Users",
    response_model=ScimUserResource,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    tags=["scim"],
)
async def create_scim_user(
    payload: ScimUserRequest,
    response: Response,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimUserResource:
    try:
        record = await repository.create_scim(
            provider.id,
            "User",
            handle=_scim_principal_handle(payload.user_name),
            resource_name=payload.user_name,
            display_name=payload.display_name or payload.user_name,
            enabled=payload.active,
            external_id=payload.external_id,
            tenant=provider.tenant,
            role=provider.role,
        )
    except (ValueError, LookupError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    result = _scim_user_resource(record)
    response.headers["Location"] = result.meta.location
    response.headers["ETag"] = result.meta.version
    return result


@app.get(
    "/scim/v2/Users/{user_id}",
    response_model=ScimUserResource,
    response_model_by_alias=True,
    tags=["scim"],
)
async def get_scim_user(
    user_id: UUID,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimUserResource:
    try:
        return _scim_user_resource(await repository.get_scim(provider.id, "User", user_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.patch(
    "/scim/v2/Users/{user_id}",
    response_model=ScimUserResource,
    response_model_by_alias=True,
    tags=["scim"],
)
async def patch_scim_user(
    user_id: UUID,
    payload: ScimPatchRequest,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimUserResource:
    try:
        display_name, active = _scim_user_patch(payload)
        record = await repository.update_scim(
            provider.id,
            "User",
            user_id,
            display_name=display_name,
            enabled=active,
        )
        return _scim_user_resource(record)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.delete(
    "/scim/v2/Users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["scim"],
)
async def delete_scim_user(
    user_id: UUID,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> None:
    try:
        await repository.delete_scim(provider.id, "User", user_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get(
    "/scim/v2/Groups",
    response_model=ScimListResponse,
    response_model_by_alias=True,
    tags=["scim"],
)
async def list_scim_groups(
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
    filter_value: Annotated[str | None, Query(alias="filter", max_length=1024)] = None,
    start_index: Annotated[int, Query(alias="startIndex", ge=1)] = 1,
    count: Annotated[int, Query(ge=0, le=200)] = 100,
) -> ScimListResponse:
    handle = _scim_filter_value(filter_value, "displayName")
    records = await repository.list_scim(provider.id, "Group", handle=handle)
    selected = records[start_index - 1 : start_index - 1 + count]
    resources = tuple(_scim_group_resource(record) for record in selected)
    return ScimListResponse(
        totalResults=len(records),
        startIndex=start_index,
        itemsPerPage=len(resources),
        Resources=resources,
    )


@app.post(
    "/scim/v2/Groups",
    response_model=ScimGroupResource,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    tags=["scim"],
)
async def create_scim_group(
    payload: ScimGroupRequest,
    response: Response,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimGroupResource:
    try:
        record = await repository.create_scim(
            provider.id,
            "Group",
            handle=_scim_principal_handle(payload.display_name),
            resource_name=payload.display_name,
            display_name=payload.display_name,
            enabled=True,
            external_id=payload.external_id,
            tenant=provider.tenant,
            role=provider.role,
            member_ids=tuple(item.value for item in payload.members),
        )
    except (ValueError, LookupError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    result = _scim_group_resource(record)
    response.headers["Location"] = result.meta.location
    response.headers["ETag"] = result.meta.version
    return result


@app.get(
    "/scim/v2/Groups/{group_id}",
    response_model=ScimGroupResource,
    response_model_by_alias=True,
    tags=["scim"],
)
async def get_scim_group(
    group_id: UUID,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimGroupResource:
    try:
        return _scim_group_resource(await repository.get_scim(provider.id, "Group", group_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.patch(
    "/scim/v2/Groups/{group_id}",
    response_model=ScimGroupResource,
    response_model_by_alias=True,
    tags=["scim"],
)
async def patch_scim_group(
    group_id: UUID,
    payload: ScimPatchRequest,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimGroupResource:
    try:
        current = await repository.get_scim(provider.id, "Group", group_id)
        display_name, member_ids = _scim_group_patch(payload, current.member_ids)
        record = await repository.update_scim(
            provider.id,
            "Group",
            group_id,
            display_name=display_name,
            member_ids=member_ids,
        )
        return _scim_group_resource(record)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.delete(
    "/scim/v2/Groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["scim"],
)
async def delete_scim_group(
    group_id: UUID,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> None:
    try:
        await repository.delete_scim(provider.id, "Group", group_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def _authentication_source(request: Request) -> str:
    """Return the stable peer identifier used by the login throttle."""

    return request.client.host if request.client is not None else "unknown"


@app.post(
    "/api/v1/auth/login",
    response_model=LoginResponse,
    tags=["authentication"],
)
async def login(
    login_request: LoginRequest,
    request: Request,
    response: Response,
    authentication_service: AuthenticationServiceDependency,
    settings: SettingsDependency,
) -> LoginResponse:
    # Keep the login throttle key tied to the network peer only.  User-Agent is
    # attacker-controlled and would let a caller evade the source limit by
    # rotating an otherwise irrelevant header.
    source = _authentication_source(request)
    try:
        issued = await authentication_service.login(
            ProviderAuthenticationRequest(
                provider=login_request.provider,
                identifier=login_request.identifier,
                secret=login_request.password,
            ),
            source=source,
        )
    except AuthenticationRateLimited as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="authentication rate limit exceeded",
            headers={"Retry-After": "60"},
        ) from exc
    except LocalAuthenticationDisabled as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="local authentication is disabled by policy",
        ) from exc
    except FederationProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="identity provider is unavailable",
        ) from exc
    except InvalidAuthentication as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication failed",
        ) from exc
    max_age = max(
        0,
        int((issued.absolute_expires_at - datetime.now(UTC)).total_seconds()),
    )
    _set_authentication_cookies(
        response,
        settings,
        session_token=issued.session_token.get_secret_value(),
        csrf_token=issued.csrf_token.get_secret_value(),
        max_age=max_age,
    )
    return LoginResponse(
        principalId=issued.actor.principal_id,
        display=issued.actor.display,
        idleExpiresAt=issued.idle_expires_at,
        absoluteExpiresAt=issued.absolute_expires_at,
    )


@app.post(
    "/api/v1/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["authentication"],
)
async def logout(
    request: Request,
    response: Response,
    actor: ActorDependency,
    authentication_service: AuthenticationServiceDependency,
    settings: SettingsDependency,
) -> None:
    session_id = getattr(request.state, "browser_session_id", None)
    if session_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="logout requires a browser session",
        )
    await authentication_service.logout(session_id, actor_id=str(actor.principal_id))
    _clear_session_cookies(response, settings)


@app.post(
    "/api/v1/auth/logout-all",
    response_model=RevokedSessionsResponse,
    tags=["authentication"],
)
async def logout_all(
    response: Response,
    actor: ActorDependency,
    authentication_service: AuthenticationServiceDependency,
    settings: SettingsDependency,
) -> RevokedSessionsResponse:
    count = await authentication_service.revoke_all(
        actor.principal_id,
        actor_id=str(actor.principal_id),
    )
    _clear_session_cookies(response, settings)
    return RevokedSessionsResponse(revokedCount=count)


@app.post(
    "/api/v1/auth/password",
    response_model=RevokedSessionsResponse,
    tags=["authentication"],
)
async def change_local_password(
    password_request: ChangeLocalPasswordRequest,
    response: Response,
    actor: ActorDependency,
    authentication_service: AuthenticationServiceDependency,
    settings: SettingsDependency,
) -> RevokedSessionsResponse:
    if actor.principal_type is not PrincipalType.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="local password rotation requires a user session",
        )
    try:
        count = await authentication_service.change_local_password(
            actor.principal_id,
            identifier=password_request.identifier,
            current_password=password_request.current_password,
            new_password=password_request.new_password,
        )
    except InvalidAuthentication as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication failed",
        ) from exc
    except (LocalAuthenticationDisabled, PasswordPolicyError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    _clear_session_cookies(response, settings)
    return RevokedSessionsResponse(revokedCount=count)


@app.put(
    "/api/v1/admin/principals/{principal_id}/local-password",
    response_model=RevokedSessionsResponse,
    tags=["authentication"],
)
async def set_local_password(
    principal_id: UUID,
    password_request: SetLocalPasswordRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    authentication_service: AuthenticationServiceDependency,
) -> RevokedSessionsResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="principal",
        action=PermissionAction.MANAGE,
    )
    try:
        count = await authentication_service.set_local_password(
            principal_id,
            password_request.new_password,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ValueError, LocalAuthenticationDisabled, PasswordPolicyError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return RevokedSessionsResponse(revokedCount=count)


@app.delete(
    "/api/v1/admin/principals/{principal_id}/sessions",
    response_model=RevokedSessionsResponse,
    tags=["authentication"],
)
async def revoke_principal_sessions(
    principal_id: UUID,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    authentication_service: AuthenticationServiceDependency,
) -> RevokedSessionsResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="principal",
        action=PermissionAction.MANAGE,
    )
    count = await authentication_service.revoke_all(
        principal_id,
        actor_id=str(actor.principal_id),
    )
    return RevokedSessionsResponse(revokedCount=count)


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get(
    "/api/v1/blueprints",
    response_model=tuple[BlueprintSummary, ...],
    tags=["blueprints"],
)
async def get_blueprints(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    q: Annotated[str | None, Query(max_length=200)] = None,
    source: BlueprintCatalogSource | None = None,
) -> tuple[BlueprintSummary, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return list_blueprints(query=q, source=source)


@app.get(
    "/api/v1/blueprints/{blueprint_id}/{version}",
    response_model=BlueprintDefinition,
    tags=["blueprints"],
)
async def get_blueprint_version(
    blueprint_id: str,
    version: str,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> BlueprintDefinition:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return get_blueprint(blueprint_id, version)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/blueprints/{blueprint_id}/{version}/instantiate",
    response_model=BlueprintDraftResponse,
    tags=["blueprints"],
)
async def instantiate_blueprint_draft(
    blueprint_id: str,
    version: str,
    request: BlueprintInstantiationRequest,
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> BlueprintDraftResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.CREATE,
        tenant_id=tenant_id,
    )
    try:
        blueprint = get_blueprint(blueprint_id, version)
        document = instantiate_blueprint(blueprint, request)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    source = yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
    validation = validate_flow_document(source, registry=plugin_catalog.resource_registry())
    if not validation.valid:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="the selected blueprint produced an invalid draft",
        )
    return BlueprintDraftResponse(
        blueprint=blueprint,
        document=source,
        validation=validation,
    )


@app.post(
    "/api/v1/playground/simulate",
    response_model=PlaygroundSimulationResponse,
    tags=["blueprints"],
)
async def simulate_playground(
    request: PlaygroundSimulationRequest,
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PlaygroundSimulationResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    engine = NativeExpressionEngine()
    context = _redact_editor_context(request.context)
    expression_result: object = None
    if request.expression and request.expression.strip():
        try:
            expression_result = engine.preview_value(request.expression, context)
        except ExpressionError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": exc.code, "message": str(exc)},
            ) from exc
    validation: FlowValidationResult | None = None
    steps: tuple[PlaygroundStep, ...] = ()
    if request.fragment and request.fragment.strip():
        try:
            document = _playground_flow(request.fragment)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        validation = validate_flow_document(
            document,
            registry=plugin_catalog.resource_registry(),
        )
        steps = _playground_steps(document)
    return PlaygroundSimulationResponse(
        expressionResult=expression_result,
        redactedContext=context,
        validation=validation,
        steps=steps,
        safety=PlaygroundSafety(),
        compatibilityVersion=engine.compatibility_version,
    )


@app.post(
    "/api/v1/flows/validate",
    response_model=FlowValidationResult,
    tags=["flows"],
)
async def validate_flow(
    request: Request,
    plugin_catalog: PluginCatalogDependency,
) -> FlowValidationResult:
    maximum_bytes = 2 * 1024 * 1024
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            declared_length = int(content_length)
        except ValueError:
            declared_length = None
        if declared_length is not None and declared_length > maximum_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="flow document exceeds the 2 MiB foundation limit",
            )
    chunks: list[bytes] = []
    received_bytes = 0
    async for chunk in request.stream():
        received_bytes += len(chunk)
        if received_bytes > maximum_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="flow document exceeds the 2 MiB foundation limit",
            )
        chunks.append(chunk)
    body = b"".join(chunks)
    try:
        return validate_flow_document(body, registry=plugin_catalog.resource_registry())
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/compatibility/kestra/manifest",
    tags=["compatibility"],
)
async def get_kestra_compatibility_manifest() -> dict[str, object]:
    return compatibility_manifest()


@app.post(
    "/api/v1/main/flows/validate",
    response_model=KestraFlowImport,
    tags=["compatibility"],
)
async def validate_kestra_flow(request: Request) -> KestraFlowImport:
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="flow document exceeds the 2 MiB compatibility limit",
        )
    try:
        return import_kestra_flow(body)
    except (FlowDocumentError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/flows/editor/schema",
    response_model=FlowEditorSchemaResponse,
    tags=["flows"],
)
async def get_flow_editor_schema(
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowEditorSchemaResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return FlowEditorSchemaResponse(
        schemaVersion="amesh.flow-editor/v1",
        flowSchema=FlowDefinition.model_json_schema(by_alias=True),
        resourceCatalog=plugin_catalog.resource_registry().catalog(),
        expressionContext={
            "flow": "Current flow metadata.",
            "execution": "Execution identity, state and timing.",
            "task": "Current task definition.",
            "taskrun": "Current task-run state and attempt.",
            "trigger": "Trigger payload and metadata.",
            "inputs": "Validated flow inputs.",
            "outputs": "Completed task outputs by task ID.",
            "vars": "Flow variables.",
            "labels": "Execution and flow labels.",
            "namespace": "Namespace-scoped public context.",
            "iteration": "Loop iteration context.",
            "error": "Current failure context.",
        },
    )


@app.post(
    "/api/v1/flows/format",
    response_model=FlowFormatResponse,
    tags=["flows"],
)
async def format_flow(
    request: Request,
    plugin_catalog: PluginCatalogDependency,
) -> FlowFormatResponse:
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="flow document exceeds the 2 MiB foundation limit",
        )
    try:
        validation = validate_flow_document(
            body,
            registry=plugin_catalog.resource_registry(),
        )
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    document = None
    if validation.valid and validation.canonical is not None:
        document = yaml.safe_dump(
            validation.canonical,
            allow_unicode=True,
            sort_keys=False,
        )
    return FlowFormatResponse(document=document, validation=validation)


@app.post(
    "/api/v1/flows/expressions/preview",
    response_model=ExpressionPreviewResponse,
    tags=["flows"],
)
async def preview_flow_expression(
    request: ExpressionPreviewRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ExpressionPreviewResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    context = _redact_editor_context(request.context)
    engine = NativeExpressionEngine()
    try:
        result = engine.preview_value(request.expression, context)
    except ExpressionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    return ExpressionPreviewResponse(
        result=result,
        redactedContext=context,
        compatibilityVersion=engine.compatibility_version,
    )


@app.get(
    "/api/v1/apps",
    response_model=list[WorkflowApp],
    tags=["apps"],
)
async def list_workflow_apps(
    repository: HumanTaskRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
) -> list[WorkflowApp]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="app",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(await repository.list_apps(tenant_id=tenant_id, namespace=namespace))


@app.get(
    "/api/v1/apps/{namespace}/{app_id}",
    response_model=WorkflowApp,
    tags=["apps"],
)
async def get_workflow_app(
    namespace: str,
    app_id: str,
    repository: HumanTaskRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> WorkflowApp:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="app",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.get_app(
            namespace,
            app_id,
            tenant_id=tenant_id,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.put(
    "/api/v1/apps/{namespace}/{app_id}",
    response_model=WorkflowApp,
    tags=["apps"],
)
async def upsert_workflow_app(
    namespace: str,
    app_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    request: WorkflowAppUpsertRequest,
    repository: HumanTaskRepositoryDependency,
    execution_repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> WorkflowApp:
    try:
        await repository.get_app(namespace, app_id, tenant_id=tenant_id)
    except LookupError:
        action = PermissionAction.CREATE
    else:
        action = PermissionAction.UPDATE
    await authorize_request(
        authorization_service,
        actor,
        resource_type="app",
        action=action,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await execution_repository.get_flow(
            namespace,
            request.flow_id,
            tenant_id=tenant_id,
            revision=request.flow_revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    form = request.form or form_from_flow(flow)
    flow_input_ids = {definition.id for definition in flow.inputs}
    form_input_ids = {field.id for field in form.fields}
    unknown = sorted(form_input_ids - flow_input_ids)
    required_missing = sorted(
        definition.id
        for definition in flow.inputs
        if definition.required
        and not definition.has_default
        and definition.id not in form_input_ids
    )
    if unknown or required_missing:
        details = []
        if unknown:
            details.append("unknown form fields: " + ", ".join(unknown))
        if required_missing:
            details.append("required flow inputs missing from form: " + ", ".join(required_missing))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="; ".join(details),
        )
    resolved = WorkflowAppSpec.model_validate(
        {
            **request.model_dump(mode="json", by_alias=True, exclude={"expected_version"}),
            "flowRevision": flow.revision,
            "form": form.model_dump(mode="json", by_alias=True),
        }
    )
    try:
        return await repository.upsert_app(
            namespace,
            app_id,
            resolved,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=request.expected_version,
        )
    except WorkflowAppVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/v1/apps/{namespace}/{app_id}/launch",
    response_model=ExecutionDetail,
    tags=["apps"],
)
async def launch_workflow_app(
    namespace: str,
    app_id: str,
    request: WorkflowAppLaunchRequest,
    background_tasks: BackgroundTasks,
    repository: HumanTaskRepositoryDependency,
    execution_repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ExecutionDetail:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="app",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        workflow_app = await repository.get_app(namespace, app_id, tenant_id=tenant_id)
        flow = await execution_repository.get_flow(
            namespace,
            workflow_app.flow_id,
            tenant_id=tenant_id,
            revision=workflow_app.flow_revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    launch_request = CreateExecutionRequest(
        namespace=namespace,
        flowId=workflow_app.flow_id,
        inputs=request.inputs,
        idempotencyKey=request.idempotency_key,
    )
    return await _execute_flow(
        execution_repository,
        task_cache,
        flow,
        launch_request,
        settings,
        operational_controls=operational_controls,
        shared_resources=shared_resources,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        actor=actor,
        authorization_service=authorization_service,
        background_tasks=background_tasks,
        launch_source=ExecutionLaunchSource.API,
        idempotency_key=request.idempotency_key,
        respond_async=True,
    )


@app.get(
    "/api/v1/human-tasks",
    response_model=list[HumanTask],
    tags=["human-tasks"],
)
async def list_human_tasks(
    repository: HumanTaskRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
    include_closed: Annotated[bool, Query(alias="includeClosed")] = False,
) -> list[HumanTask]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="human_task",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    manage = await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=namespace,
            resource_type="human_task",
            action=PermissionAction.MANAGE,
        )
    )
    return list(
        await repository.list_tasks(
            actor.principal_id,
            tenant_id=tenant_id,
            namespace=namespace,
            include_closed=include_closed,
            include_all=manage.allowed,
        )
    )


@app.post(
    "/api/v1/human-tasks/{human_task_id}/actions",
    response_model=HumanTask,
    tags=["human-tasks"],
)
async def act_on_human_task(
    human_task_id: UUID,
    request: HumanTaskActionRequest,
    repository: HumanTaskRepositoryDependency,
    service: HumanTaskServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> HumanTask:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="human_task",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        task = await repository.get_task(
            human_task_id,
            actor.principal_id,
            tenant_id=tenant_id,
            include_all=True,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="human_task",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=task.namespace,
    )
    manage = await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=task.namespace,
            resource_type="human_task",
            action=PermissionAction.MANAGE,
        )
    )
    if not manage.allowed:
        try:
            await repository.get_task(
                human_task_id,
                actor.principal_id,
                tenant_id=tenant_id,
            )
        except LookupError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    try:
        return await service.apply_action(
            human_task_id,
            request,
            tenant_id=tenant_id,
            actor_id=actor.principal_id,
        )
    except (HumanTaskConflict, TaskStateConflictError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/human-task-notifications",
    response_model=list[HumanTaskNotification],
    tags=["human-tasks"],
)
async def list_human_task_notifications(
    repository: HumanTaskRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[HumanTaskNotification]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="human_task",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return list(
        await repository.list_notifications(
            actor.principal_id,
            tenant_id=tenant_id,
            limit=limit,
        )
    )


@app.put(
    "/api/v1/flows",
    response_model=PersistedFlow,
    tags=["flows"],
)
async def apply_flow(
    request: Request,
    response: Response,
    repository: RepositoryDependency,
    plugin_catalog: PluginCatalogDependency,
    operational_controls: OperationalControlRepositoryDependency,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
    revision_source: Annotated[str | None, Header(alias="X-AMESH-Source")] = None,
    source_commit: Annotated[str | None, Header(alias="X-AMESH-Commit")] = None,
    environment: Annotated[str | None, Header(alias="X-AMESH-Environment")] = None,
    deployment: Annotated[str | None, Header(alias="X-AMESH-Deployment")] = None,
) -> PersistedFlow:
    try:
        result = validate_flow_document(
            await request.body(),
            registry=plugin_catalog.resource_registry(),
        )
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if not result.valid or result.canonical is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[issue.model_dump(mode="json", by_alias=True) for issue in result.issues],
        )
    flow = FlowDefinition.model_validate(result.canonical)
    authoring_decision = await operational_controls.evaluate(
        OperationalBoundary.AUTHORING,
        tenant_id=tenant_id,
        namespace=flow.namespace,
        flow_id=flow.id,
        plugin_ids=tuple(node.task.type for node in compile_execution_tasks(flow)),
        component_id="webserver:flow-authoring",
        component_role=ServiceRole.WEBSERVER.value,
    )
    if authoring_decision.blocked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "message": "authoring blocked by operational control",
                "boundary": OperationalBoundary.AUTHORING.value,
                "controlIds": [str(control.control_id) for control in authoring_decision.controls],
            },
        )
    existing_revision: int | None = None
    try:
        existing = await repository.get_flow(flow.namespace, flow.id, tenant_id=tenant_id)
    except LookupError:
        write_action = PermissionAction.CREATE
    else:
        existing_revision = existing.revision
        write_action = PermissionAction.UPDATE
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=write_action,
        tenant_id=tenant_id,
        namespace=flow.namespace,
    )
    if flow.system:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="tenant",
            action=PermissionAction.MANAGE,
            tenant_id=tenant_id,
        )
    try:
        persisted = await repository.apply_flow(
            flow,
            tenant_id=tenant_id,
            expected_etag=if_match,
            actor_id=str(actor.principal_id),
            revision_source=FlowRevisionSource(
                source=revision_source,
                source_commit=source_commit,
                environment=environment,
                deployment={"reference": deployment} if deployment is not None else {},
            ),
        )
        gate = await flow_tests.get_gate(flow.namespace, tenant_id=tenant_id)
        if (
            gate is not None
            and gate.enabled
            and (existing_revision is None or persisted.revision > existing_revision)
        ):
            persisted = await repository.promote_flow_revision(
                flow.namespace,
                flow.id,
                persisted.revision,
                FlowLifecycle.DRAFT,
                tenant_id=tenant_id,
                actor_id=str(actor.principal_id),
                reason="namespace flow-test gate requires passing tests before ACTIVE promotion",
            )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc
    except PluginContractError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[error.model_dump(mode="json") for error in exc.errors],
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    response.headers["ETag"] = persisted.etag
    return persisted


@app.get(
    "/api/v1/flows",
    response_model=list[PersistedFlow],
    tags=["flows"],
)
async def list_flows(
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return collection_response(await repository.list_flows(tenant_id=tenant_id), query)


@app.get(
    "/api/v1/flows/{namespace}/{flow_id}/document",
    response_model=FlowDocumentExport,
    tags=["flows"],
)
async def export_flow_document(
    namespace: str,
    flow_id: str,
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> FlowDocumentExport:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    document = (
        json.loads(flow._persisted_canonical_definition)
        if flow._persisted_canonical_definition is not None
        else flow.model_dump(mode="json", by_alias=True, exclude_none=True)
    )
    return FlowDocumentExport(
        namespace=flow.namespace,
        flowId=flow.id,
        revision=flow.revision,
        semanticHash=flow._persisted_semantic_hash or canonical_hash(document),
        document=document,
    )


@app.put(
    "/api/v1/namespaces/{namespace}/workflow-metadata",
    response_model=NamespaceWorkflowMetadata,
    tags=["namespaces"],
)
async def upsert_namespace_workflow_metadata(
    namespace: str,
    request: NamespaceWorkflowMetadataUpdate,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceWorkflowMetadata:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.upsert_namespace_workflow_metadata(
            namespace,
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/namespaces/{namespace}/workflow-metadata",
    response_model=NamespaceWorkflowMetadataView,
    tags=["namespaces"],
)
async def get_namespace_workflow_metadata(
    namespace: str,
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceWorkflowMetadataView:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.get_namespace_workflow_metadata(
        namespace,
        tenant_id=tenant_id,
    )


@app.get(
    "/api/v1/flows/{namespace}/{flow_id}/metadata",
    response_model=FlowMetadataResponse,
    tags=["flows"],
)
async def get_flow_metadata(
    namespace: str,
    flow_id: str,
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowMetadataResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    persisted = next(
        (
            item
            for item in await repository.list_flows(tenant_id=tenant_id)
            if item.namespace == namespace and item.flow_id == flow_id
        ),
        None,
    )
    if persisted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="flow not found")
    revisions = await repository.list_flow_revisions(
        namespace,
        flow_id,
        tenant_id=tenant_id,
    )
    revision = next(item for item in revisions if item.revision == persisted.revision)
    return FlowMetadataResponse(
        namespace=namespace,
        flowId=flow_id,
        revision=persisted.revision,
        labels=persisted.metadata.labels,
        pluginResolution=revision.plugin_resolution,
    )


@app.get(
    "/api/v1/namespaces/{namespace}/files",
    response_model=list[NamespaceFile],
    tags=["namespace-resources"],
)
async def list_namespace_files(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    inherited: bool = True,
) -> list[NamespaceFile]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_files(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        inherited=inherited,
    )


@app.get(
    "/api/v1/namespaces/{namespace}/artifacts",
    response_model=list[ArtifactRef],
    tags=["namespace-resources"],
)
async def list_namespace_artifacts(
    namespace: str,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    inherited: bool = True,
) -> list[ArtifactRef]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await service.list_artifacts(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        inherited=inherited,
    )


@app.get(
    "/api/v1/namespaces/{namespace}/artifacts/{path:path}",
    response_model=ArtifactRef,
    tags=["namespace-resources"],
)
async def get_namespace_artifact(
    namespace: str,
    path: str,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    version: Annotated[int | None, Query(ge=1)] = None,
) -> ArtifactRef:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.READ,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await service.get_artifact(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            version=version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@app.put(
    "/api/v1/namespaces/{namespace}/files/{path:path}",
    response_model=NamespaceFile,
    tags=["namespace-resources"],
)
async def upload_namespace_file(
    namespace: str,
    path: str,
    request: Request,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=0)] = None,
) -> NamespaceFile:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await service.upload_file(
            namespace,
            path,
            await request.body(),
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            content_type=request.headers.get("content-type"),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@app.get(
    "/api/v1/namespaces/{namespace}/files/{path:path}/versions",
    response_model=list[NamespaceFileVersion],
    tags=["namespace-resources"],
)
async def list_namespace_file_versions(
    namespace: str,
    path: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[NamespaceFileVersion]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_file_versions(
        namespace,
        path,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
    )


@app.post(
    "/api/v1/namespaces/{namespace}/files/{path:path}/move",
    response_model=NamespaceFile,
    tags=["namespace-resources"],
)
async def move_namespace_file(
    namespace: str,
    path: str,
    request: NamespaceFileMoveRequest,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceFile:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.move_file(
            namespace,
            path,
            request.destination_path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=request.expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@app.get(
    "/api/v1/namespaces/{namespace}/files/{path:path}",
    response_class=StreamingResponse,
    tags=["namespace-resources"],
)
async def download_namespace_file(
    namespace: str,
    path: str,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    version: Annotated[int | None, Query(ge=1)] = None,
) -> StreamingResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.READ,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        selected, content = await service.download_file(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            version=version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    async def chunks() -> AsyncIterator[bytes]:
        yield content

    return StreamingResponse(
        chunks(),
        media_type=selected.content_type or "application/octet-stream",
        headers={
            "ETag": f'"sha256:{selected.checksum_sha256}"',
            "X-Amesh-File-Version": str(selected.version),
            "X-Content-Type-Options": "nosniff",
        },
    )


@app.delete(
    "/api/v1/namespaces/{namespace}/files/{path:path}",
    tags=["namespace-resources"],
)
async def delete_namespace_file(
    namespace: str,
    path: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=0)] = None,
) -> dict[str, int]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.DELETE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        version = await repository.delete_file(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    return {"resourceVersion": version}


@app.get(
    "/api/v1/namespaces/{namespace}/key-values",
    response_model=list[KeyValueEntry],
    tags=["namespace-resources"],
)
async def list_namespace_key_values(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[KeyValueEntry]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="key_value",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_key_values(
        namespace, tenant_id=tenant_id, actor_id=str(actor.principal_id)
    )


@app.get(
    "/api/v1/namespaces/{namespace}/key-values/changes",
    response_model=list[KeyValueChange],
    tags=["namespace-resources"],
)
async def list_namespace_key_value_changes(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    after: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[KeyValueChange]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="key_value",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_key_value_changes(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        after=after,
        limit=limit,
    )


@app.put(
    "/api/v1/namespaces/{namespace}/key-values/{key}",
    response_model=KeyValueEntry,
    tags=["namespace-resources"],
)
async def put_namespace_key_value(
    namespace: str,
    key: str,
    write: KeyValueWrite,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> KeyValueEntry:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="key_value",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.put_key_value(
            namespace,
            key,
            write,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc


@app.get(
    "/api/v1/namespaces/{namespace}/key-values/{key}",
    response_model=KeyValueEntry,
    tags=["namespace-resources"],
)
async def get_namespace_key_value(
    namespace: str,
    key: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> KeyValueEntry:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="key_value",
        action=PermissionAction.READ,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.get_key_value(
            namespace, key, tenant_id=tenant_id, actor_id=str(actor.principal_id)
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete(
    "/api/v1/namespaces/{namespace}/key-values/{key}",
    tags=["namespace-resources"],
)
async def delete_namespace_key_value(
    namespace: str,
    key: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> dict[str, bool]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="key_value",
        action=PermissionAction.DELETE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        deleted = await repository.delete_key_value(
            namespace,
            key,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    return {"deleted": deleted}


@app.get(
    "/api/v1/namespaces/{namespace}/secret-bindings",
    response_model=list[SecretBinding],
    tags=["namespace-resources"],
)
async def list_namespace_secret_bindings(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    inherited: bool = True,
) -> list[SecretBinding]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="secret",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_secret_bindings(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        inherited=inherited,
    )


@app.put(
    "/api/v1/namespaces/{namespace}/secret-bindings/{key}",
    response_model=SecretBinding,
    tags=["namespace-resources"],
)
async def put_namespace_secret_binding(
    namespace: str,
    key: str,
    write: SecretBindingWrite,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SecretBinding:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="secret",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.put_secret_binding(
            namespace,
            key,
            write,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc


@app.delete(
    "/api/v1/namespaces/{namespace}/secret-bindings/{key}",
    tags=["namespace-resources"],
)
async def delete_namespace_secret_binding(
    namespace: str,
    key: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> dict[str, bool]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="secret",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        deleted = await repository.delete_secret_binding(
            namespace,
            key,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    return {"deleted": deleted}


@app.get(
    "/api/v1/namespaces/{namespace}/resource-bundle",
    response_model=NamespaceResourceBundle,
    tags=["namespace-resources"],
)
async def export_namespace_resource_bundle(
    namespace: str,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceResourceBundle:
    for resource_type, action in (
        ("namespace_file", PermissionAction.READ),
        ("key_value", PermissionAction.READ),
        ("secret", PermissionAction.LIST),
    ):
        await authorize_request(
            authorization_service,
            actor,
            resource_type=resource_type,
            action=action,
            tenant_id=tenant_id,
            namespace=namespace,
        )
    return await service.export_bundle(
        namespace, tenant_id=tenant_id, actor_id=str(actor.principal_id)
    )


@app.post(
    "/api/v1/namespaces/{namespace}/resource-bundle",
    response_model=NamespaceResourceImportResult,
    tags=["namespace-resources"],
)
async def import_namespace_resource_bundle(
    namespace: str,
    bundle: NamespaceResourceBundle,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceResourceImportResult:
    for resource_type in ("namespace_file", "key_value", "secret"):
        await authorize_request(
            authorization_service,
            actor,
            resource_type=resource_type,
            action=PermissionAction.WRITE,
            tenant_id=tenant_id,
            namespace=namespace,
        )
    try:
        result = await service.import_bundle(
            namespace,
            bundle,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return NamespaceResourceImportResult.model_validate(result)


@app.get(
    "/api/v1/flows/{namespace}/{flow_id}/revisions",
    response_model=list[FlowRevisionRecord],
    tags=["flows"],
)
async def list_flow_revisions(
    namespace: str,
    flow_id: str,
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[FlowRevisionRecord]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_flow_revisions(namespace, flow_id, tenant_id=tenant_id)


@app.put(
    "/api/v1/flows/{namespace}/{flow_id}/tests",
    response_model=FlowTestDefinition,
    tags=["flow-tests"],
)
async def save_flow_test(
    namespace: str,
    flow_id: str,
    request: FlowTestDefinitionCreateRequest,
    repository: RepositoryDependency,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowTestDefinition:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=(
            PermissionAction.CREATE if request.expected_version is None else PermissionAction.UPDATE
        ),
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await FlowTestService(repository, flow_tests).save_definition(
            namespace,
            flow_id,
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FlowTestVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/flows/{namespace}/{flow_id}/tests",
    response_model=list[FlowTestDefinition],
    tags=["flow-tests"],
)
async def list_flow_tests(
    namespace: str,
    flow_id: str,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> list[FlowTestDefinition]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(
        await flow_tests.list_definitions(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
    )


@app.delete(
    "/api/v1/flows/{namespace}/{flow_id}/tests/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["flow-tests"],
)
async def delete_flow_test(
    namespace: str,
    flow_id: str,
    test_id: str,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int, Query(alias="expectedVersion", ge=1)],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        await flow_tests.delete_definition(
            namespace,
            flow_id,
            test_id,
            tenant_id=tenant_id,
            expected_version=expected_version,
            actor_id=str(actor.principal_id),
        )
    except FlowTestVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/api/v1/flows/{namespace}/{flow_id}/tests/runs",
    response_model=FlowTestRunResult,
    tags=["flow-tests"],
)
async def run_flow_tests(
    namespace: str,
    flow_id: str,
    request: FlowTestRunRequest,
    repository: RepositoryDependency,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int, Query(ge=1)],
) -> FlowTestRunResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await FlowTestService(repository, flow_tests).run(
            namespace,
            flow_id,
            revision,
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get(
    "/api/v1/flows/{namespace}/{flow_id}/tests/runs",
    response_model=list[FlowTestRunResult],
    tags=["flow-tests"],
)
async def list_flow_test_runs(
    namespace: str,
    flow_id: str,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[FlowTestRunResult]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(
        await flow_tests.list_runs(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
            limit=limit,
        )
    )


@app.get(
    "/api/v1/namespaces/{namespace}/flow-test-gate",
    response_model=FlowTestQualityGate | None,
    tags=["flow-tests"],
)
async def get_flow_test_gate(
    namespace: str,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowTestQualityGate | None:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await flow_tests.get_gate(namespace, tenant_id=tenant_id)


@app.put(
    "/api/v1/namespaces/{namespace}/flow-test-gate",
    response_model=FlowTestQualityGate,
    tags=["flow-tests"],
)
async def update_flow_test_gate(
    namespace: str,
    request: FlowTestQualityGateUpdate,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowTestQualityGate:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await flow_tests.upsert_gate(
            namespace,
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except FlowTestVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/diff",
    response_model=FlowRevisionDiff,
    tags=["flows"],
)
async def diff_flow_revisions(
    namespace: str,
    flow_id: str,
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    from_revision: Annotated[int, Query(alias="from", ge=1)],
    to_revision: Annotated[int, Query(alias="to", ge=1)],
) -> FlowRevisionDiff:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.diff_flow_revisions(
            namespace,
            flow_id,
            from_revision,
            to_revision,
            tenant_id=tenant_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/diff-draft",
    response_model=FlowRevisionDiff,
    tags=["flows"],
)
async def diff_flow_draft(
    namespace: str,
    flow_id: str,
    revision: int,
    request: Request,
    repository: ReadRepositoryDependency,
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowRevisionDiff:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="flow document exceeds the 2 MiB foundation limit",
        )
    try:
        validation = validate_flow_document(
            body,
            registry=plugin_catalog.resource_registry(),
        )
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if not validation.valid or validation.canonical is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[issue.model_dump(mode="json", by_alias=True) for issue in validation.issues],
        )
    try:
        stored = await repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    before = (
        json.loads(stored._persisted_canonical_definition)
        if stored._persisted_canonical_definition is not None
        else stored.model_dump(mode="json", by_alias=True, exclude_none=True)
    )
    draft_revision = validation.canonical.get("revision", revision)
    return compare_flow_revisions(
        before,
        validation.canonical,
        from_revision=revision,
        to_revision=(
            draft_revision if isinstance(draft_revision, int) and draft_revision >= 1 else revision
        ),
    )


@app.post(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/simulate",
    response_model=SimulationPlan,
    tags=["simulations"],
)
async def simulate_flow_revision(
    namespace: str,
    flow_id: str,
    revision: int,
    request: SimulationRequest,
    repository: ReadRepositoryDependency,
    policy: PluginPolicyServiceDependency,
    admission_policy: AdmissionPolicyServiceDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SimulationPlan:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
        revisions = await repository.list_flow_revisions(
            namespace,
            flow_id,
            tenant_id=tenant_id,
        )
        record = next(item for item in revisions if item.revision == revision)
        plugin_decision = await policy.preview_flow(
            flow,
            tenant_id=tenant_id,
            stage=PluginPolicyStage.EXECUTION,
            resolution_payload=record.plugin_resolution,
        )
        admission_decision = await _preview_simulation_admission_policy(
            admission_policy,
            flow,
            request,
            actor,
            tenant_id,
        )
    except (LookupError, StopIteration) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return simulate_flow(
        flow,
        request,
        semantic_hash=record.semantic_hash,
        plugin_set=record.plugin_resolution,
        tenant_id=tenant_id,
        policy_decisions=(_simulation_plugin_policy(plugin_decision),),
        determinism_policy_pins=_simulation_admission_policy_pins(admission_decision),
        signing_key=_simulation_signing_key(settings),
        signing_key_id="amesh-server/simulation-v1",
    )


@app.post(
    "/api/v1/flows/{namespace}/{flow_id}/simulations/compare",
    response_model=SimulationComparison,
    tags=["simulations"],
)
async def compare_flow_simulations(
    namespace: str,
    flow_id: str,
    request: SimulationRequest,
    repository: ReadRepositoryDependency,
    policy: PluginPolicyServiceDependency,
    admission_policy: AdmissionPolicyServiceDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    from_revision: Annotated[int, Query(alias="from", ge=1)],
    to_revision: Annotated[int, Query(alias="to", ge=1)],
) -> SimulationComparison:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        before_flow = await repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=from_revision,
        )
        after_flow = await repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=to_revision,
        )
        revisions = await repository.list_flow_revisions(
            namespace,
            flow_id,
            tenant_id=tenant_id,
        )
        records = {item.revision: item for item in revisions}
        before_record = records[from_revision]
        after_record = records[to_revision]
        before_policy = await policy.preview_flow(
            before_flow,
            tenant_id=tenant_id,
            stage=PluginPolicyStage.EXECUTION,
            resolution_payload=before_record.plugin_resolution,
        )
        after_policy = await policy.preview_flow(
            after_flow,
            tenant_id=tenant_id,
            stage=PluginPolicyStage.EXECUTION,
            resolution_payload=after_record.plugin_resolution,
        )
        before_admission = await _preview_simulation_admission_policy(
            admission_policy,
            before_flow,
            request,
            actor,
            tenant_id,
        )
        after_admission = await _preview_simulation_admission_policy(
            admission_policy,
            after_flow,
            request,
            actor,
            tenant_id,
        )
    except (KeyError, LookupError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    signing_key = _simulation_signing_key(settings)
    before = simulate_flow(
        before_flow,
        request,
        semantic_hash=before_record.semantic_hash,
        plugin_set=before_record.plugin_resolution,
        tenant_id=tenant_id,
        policy_decisions=(_simulation_plugin_policy(before_policy),),
        determinism_policy_pins=_simulation_admission_policy_pins(before_admission),
        signing_key=signing_key,
        signing_key_id="amesh-server/simulation-v1",
    )
    after = simulate_flow(
        after_flow,
        request,
        semantic_hash=after_record.semantic_hash,
        plugin_set=after_record.plugin_resolution,
        tenant_id=tenant_id,
        policy_decisions=(_simulation_plugin_policy(after_policy),),
        determinism_policy_pins=_simulation_admission_policy_pins(after_admission),
        signing_key=signing_key,
        signing_key_id="amesh-server/simulation-v1",
    )
    return SimulationComparison(
        before=before,
        after=after,
        diff=compare_simulation_plans(before, after),
    )


@app.put(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/lifecycle",
    response_model=PersistedFlow,
    tags=["flows"],
)
async def promote_flow_revision(
    namespace: str,
    flow_id: str,
    revision: int,
    request: FlowRevisionLifecycleRequest,
    repository: RepositoryDependency,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PersistedFlow:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        if request.lifecycle is FlowLifecycle.ACTIVE:
            decision = await FlowTestService(repository, flow_tests).gate_decision(
                namespace,
                flow_id,
                revision,
                tenant_id=tenant_id,
            )
            if not decision.allowed:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "FLOW_TEST_GATE_FAILED",
                        "reason": decision.reason,
                        "decision": decision.model_dump(mode="json", by_alias=True),
                    },
                )
        return await repository.promote_flow_revision(
            namespace,
            flow_id,
            revision,
            request.lifecycle,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            reason=request.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/restore",
    response_model=PersistedFlow,
    tags=["flows"],
)
async def restore_flow_revision(
    namespace: str,
    flow_id: str,
    revision: int,
    request: FlowRevisionRestoreRequest,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PersistedFlow:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.restore_flow_revision(
            namespace,
            flow_id,
            revision,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            reason=request.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.delete(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["flows"],
)
async def delete_flow_revision(
    namespace: str,
    flow_id: str,
    revision: int,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        await repository.delete_flow_revision(
            namespace,
            flow_id,
            revision,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/api/v1/flows/{namespace}/{flow_id}/graph",
    response_model=FlowGraph,
    tags=["flows"],
)
async def get_flow_graph(
    namespace: str,
    flow_id: str,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowGraph:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await repository.get_flow(namespace, flow_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _build_flow_graph(flow)


@app.get(
    "/api/v1/flows/{namespace}/{flow_id}/data-contract",
    response_model=FlowDataContract,
    tags=["flows"],
)
async def get_flow_data_contract(
    namespace: str,
    flow_id: str,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowDataContract:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await repository.get_flow(namespace, flow_id, tenant_id=tenant_id)
        return FlowDataContract(
            namespace=flow.namespace,
            flowId=flow.id,
            revision=flow.revision,
            inputSchema=flow_input_contract(flow),
            outputs=flow.outputs,
            variables=flow.variables,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DataContractError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/flows/{namespace}/{flow_id}/schedules/{trigger_id}/preview",
    response_model=SchedulePreview,
    tags=["triggers"],
)
async def preview_schedule(
    namespace: str,
    flow_id: str,
    trigger_id: str,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    after: datetime | None = None,
    count: int = 5,
) -> SchedulePreview:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await repository.get_flow(namespace, flow_id, tenant_id=tenant_id)
        trigger = next(item for item in flow.triggers if item.id == trigger_id)
        return CronScheduler(repository).preview(
            trigger,
            after=after or datetime.now(UTC),
            count=count,
            flow=flow,
        )
    except (LookupError, StopIteration) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="schedule not found"
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@app.post(
    "/api/v1/executions",
    response_model=ExecutionDetail,
    responses={
        status.HTTP_202_ACCEPTED: {
            "model": ExecutionDetail,
            "description": "Execution persisted and accepted for asynchronous processing",
        }
    },
    tags=["executions"],
)
async def create_execution(
    request: CreateExecutionRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-ID")] = None,
) -> ExecutionDetail:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=request.namespace,
    )
    try:
        flow = await repository.get_flow(
            request.namespace,
            request.flow_id,
            tenant_id=tenant_id,
            revision=request.flow_revision,
        )
    except LookupError as exc:
        error_detail = (
            f"flow {request.namespace}.{request.flow_id} revision "
            f"{request.flow_revision} does not exist"
            if request.flow_revision is not None
            else str(exc)
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_detail) from exc
    effective_idempotency_key = _resolve_idempotency_key(
        request.idempotency_key,
        idempotency_key,
    )
    respond_async = _prefers_async_response(prefer)
    detail = await _execute_flow(
        repository,
        task_cache,
        flow,
        request,
        settings,
        operational_controls=operational_controls,
        shared_resources=shared_resources,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        actor=actor,
        authorization_service=authorization_service,
        background_tasks=background_tasks,
        launch_source=ExecutionLaunchSource.API,
        idempotency_key=effective_idempotency_key,
        respond_async=respond_async,
        correlation_id=correlation_id,
    )
    if respond_async and detail.execution.state is ExecutionState.RUNNING:
        response.status_code = status.HTTP_202_ACCEPTED
        response.headers["Preference-Applied"] = "respond-async"
        response.headers["Location"] = f"/api/v1/executions/{detail.execution.execution_id}"
    persisted_correlation_id = detail.execution.trigger.get("correlationId")
    if isinstance(persisted_correlation_id, str):
        response.headers["X-Correlation-ID"] = persisted_correlation_id
    return detail


@app.post(
    "/api/v1/executions/bulk",
    response_model=list[BulkExecutionItemResult],
    status_code=status.HTTP_207_MULTI_STATUS,
    tags=["executions"],
)
async def create_executions_bulk(
    request: BulkExecutionRequest,
    background_tasks: BackgroundTasks,
    repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-ID")] = None,
) -> list[BulkExecutionItemResult]:
    respond_async = _prefers_async_response(prefer)
    results: list[BulkExecutionItemResult] = []
    for index, item in enumerate(request.items):
        try:
            await authorize_request(
                authorization_service,
                actor,
                resource_type="execution",
                action=PermissionAction.EXECUTE,
                tenant_id=tenant_id,
                namespace=item.namespace,
            )
            flow = await repository.get_flow(
                item.namespace,
                item.flow_id,
                tenant_id=tenant_id,
            )
            detail = await _execute_flow(
                repository,
                task_cache,
                flow,
                item,
                settings,
                operational_controls=operational_controls,
                shared_resources=shared_resources,
                tenant_id=tenant_id,
                actor_id=str(actor.principal_id),
                actor=actor,
                authorization_service=authorization_service,
                background_tasks=background_tasks,
                launch_source=ExecutionLaunchSource.API,
                idempotency_key=item.idempotency_key,
                respond_async=respond_async,
                correlation_id=correlation_id,
            )
        except (HTTPException, LookupError) as exc:
            item_status = exc.status_code if isinstance(exc, HTTPException) else 404
            item_detail = exc.detail if isinstance(exc, HTTPException) else str(exc)
            problem_code = f"HTTP_{item_status}"
            results.append(
                BulkExecutionItemResult(
                    index=index,
                    status=item_status,
                    error=ProblemDetail(
                        type=f"urn:amesh:problem:{problem_code.lower()}",
                        title=HTTPStatus(item_status).phrase,
                        status=item_status,
                        detail=item_detail if isinstance(item_detail, str) else str(item_detail),
                        code=problem_code,
                        instance=f"/api/v1/executions/bulk#item-{index}",
                    ),
                )
            )
            continue
        item_status = (
            status.HTTP_202_ACCEPTED
            if respond_async and detail.execution.state is ExecutionState.RUNNING
            else status.HTTP_200_OK
        )
        results.append(BulkExecutionItemResult(index=index, status=item_status, execution=detail))
    return results


@app.get(
    "/api/v1/task-cache",
    response_model=list[TaskCacheEntry],
    tags=["task-cache"],
)
async def list_task_cache_entries(
    task_cache: TaskCacheRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    key_prefix: Annotated[str | None, Query(alias="keyPrefix", max_length=1024)] = None,
    namespace: Annotated[str | None, Query(max_length=255)] = None,
    flow_id: Annotated[str | None, Query(alias="flowId", max_length=128)] = None,
    task_id: Annotated[str | None, Query(alias="taskId", max_length=128)] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[TaskCacheEntry]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="task_cache",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await task_cache.list_entries(
        tenant_id=tenant_id,
        key_prefix=key_prefix,
        namespace=namespace,
        flow_id=flow_id,
        task_id=task_id,
        limit=limit,
    )


@app.post(
    "/api/v1/task-cache/purge",
    response_model=TaskCachePurgeResult,
    tags=["task-cache"],
)
async def purge_task_cache_entries(
    request: TaskCachePurgeRequest,
    task_cache: TaskCacheRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> TaskCachePurgeResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="task_cache",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=request.namespace,
    )
    return await task_cache.purge(
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        reason=request.reason,
        key_prefix=request.key_prefix,
        namespace=request.namespace,
        flow_id=request.flow_id,
        task_id=request.task_id,
    )


@app.get(
    "/api/v1/check-policies",
    response_model=list[NamespaceCheckPolicy],
    tags=["checks"],
)
async def list_check_policies(
    checks: CheckRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: Annotated[str | None, Query(max_length=255)] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[NamespaceCheckPolicy]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="check",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await checks.list_policies(
        tenant_id=tenant_id,
        namespace=namespace,
        limit=limit,
    )


@app.put(
    "/api/v1/check-policies/{namespace}/{policy_key}",
    response_model=NamespaceCheckPolicy,
    tags=["checks"],
)
async def upsert_check_policy(
    namespace: str,
    policy_key: str,
    request: CheckPolicyUpsertRequest,
    checks: CheckRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceCheckPolicy:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="check",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await checks.upsert_policy(
            tenant_id=tenant_id,
            namespace=namespace,
            policy_key=policy_key,
            source=request.source,
            task_type=request.task_type,
            definition=request.definition,
            enabled=request.enabled,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/check-evaluations",
    response_model=list[CheckEvaluation],
    tags=["checks"],
)
async def list_check_evaluations(
    checks: CheckRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: Annotated[str | None, Query(max_length=255)] = None,
    flow_id: Annotated[str | None, Query(alias="flowId", max_length=128)] = None,
    execution_id: Annotated[UUID | None, Query(alias="executionId")] = None,
    outcome: CheckOutcome | None = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[CheckEvaluation]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="check",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await checks.list_evaluations(
        tenant_id=tenant_id,
        namespace=namespace,
        flow_id=flow_id,
        execution_id=execution_id,
        outcome=outcome,
        limit=limit,
    )


@app.get(
    "/api/v1/check-compliance",
    response_model=list[CheckComplianceSummary],
    tags=["checks"],
)
async def get_check_compliance(
    checks: CheckRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    group_by: Annotated[str, Query(alias="groupBy", max_length=256)] = "flow",
    from_time: Annotated[datetime | None, Query(alias="fromTime")] = None,
    to_time: Annotated[datetime | None, Query(alias="toTime")] = None,
    namespace: Annotated[str | None, Query(max_length=255)] = None,
    flow_id: Annotated[str | None, Query(alias="flowId", max_length=128)] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[CheckComplianceSummary]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="check",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await checks.summarize(
            tenant_id=tenant_id,
            group_by=group_by,
            from_time=from_time,
            to_time=to_time,
            namespace=namespace,
            flow_id=flow_id,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/triggers",
    response_model=list[TriggerRuntimeState],
    tags=["triggers"],
)
async def list_trigger_runtime_states(
    trigger_runtime: TriggerRuntimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: Annotated[str | None, Query(max_length=255)] = None,
    flow_id: Annotated[str | None, Query(alias="flowId", max_length=128)] = None,
    trigger_id: Annotated[str | None, Query(alias="triggerId", max_length=128)] = None,
    active: bool | None = True,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[TriggerRuntimeState]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="trigger",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await trigger_runtime.list_runtime_states(
        tenant_id=tenant_id,
        namespace=namespace,
        flow_id=flow_id,
        trigger_id=trigger_id,
        active=active,
        limit=limit,
    )


@app.get(
    "/api/v1/trigger-occurrences",
    response_model=list[TriggerOccurrence],
    tags=["triggers"],
)
async def list_trigger_occurrences(
    trigger_runtime: TriggerRuntimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: Annotated[str | None, Query(max_length=255)] = None,
    flow_id: Annotated[str | None, Query(alias="flowId", max_length=128)] = None,
    trigger_id: Annotated[str | None, Query(alias="triggerId", max_length=128)] = None,
    occurrence_state: Annotated[
        TriggerOccurrenceState | None,
        Query(alias="state"),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[TriggerOccurrence]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="trigger",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await trigger_runtime.list_occurrences(
        tenant_id=tenant_id,
        namespace=namespace,
        flow_id=flow_id,
        trigger_id=trigger_id,
        state=occurrence_state,
        limit=limit,
    )


@app.post(
    "/api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/pause",
    response_model=TriggerRuntimeState,
    tags=["triggers"],
)
async def pause_trigger_runtime(
    namespace: str,
    flow_id: str,
    trigger_id: str,
    request: TriggerActionRequest,
    trigger_runtime: TriggerRuntimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> TriggerRuntimeState:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="trigger",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await trigger_runtime.set_paused(
            tenant_id=tenant_id,
            namespace=namespace,
            flow_id=flow_id,
            trigger_id=trigger_id,
            paused=True,
            actor_id=str(actor.principal_id),
            reason=request.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/resume",
    response_model=TriggerRuntimeState,
    tags=["triggers"],
)
async def resume_trigger_runtime(
    namespace: str,
    flow_id: str,
    trigger_id: str,
    request: TriggerActionRequest,
    trigger_runtime: TriggerRuntimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> TriggerRuntimeState:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="trigger",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await trigger_runtime.set_paused(
            tenant_id=tenant_id,
            namespace=namespace,
            flow_id=flow_id,
            trigger_id=trigger_id,
            paused=False,
            actor_id=str(actor.principal_id),
            reason=request.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/trigger-occurrences/{occurrence_id}/replay",
    response_model=TriggerOccurrence,
    tags=["triggers"],
)
async def replay_trigger_occurrence(
    occurrence_id: UUID,
    request: TriggerActionRequest,
    trigger_runtime: TriggerRuntimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> TriggerOccurrence:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="trigger",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
    )
    try:
        return await trigger_runtime.replay_occurrence(
            occurrence_id,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            reason=request.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/executions",
    response_model=list[PersistedExecution],
    tags=["executions"],
)
async def list_executions(
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    query: Annotated[CollectionQuery, Depends(default_limited_collection_query)],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    executions = await repository.list_executions(tenant_id=tenant_id, limit=1000)
    public_executions: list[PersistedExecution] = []
    for execution in executions:
        flow = await repository.get_flow(
            execution.namespace,
            execution.flow_id,
            tenant_id=tenant_id,
            revision=execution.flow_revision,
        )
        public_executions.append(_public_execution(flow, execution))
    return collection_response(public_executions, query, default_limit=100)


@app.get(
    "/api/v1/executions/{execution_id}/admission",
    response_model=AdmissionDecision,
    tags=["executions"],
)
async def get_execution_admission(
    execution_id: UUID,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AdmissionDecision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    decision = await repository.get_admission(
        AdmissionResourceType.EXECUTION,
        execution_id,
        tenant_id=tenant_id,
    )
    if decision is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="admission not found")
    return decision


@app.get(
    "/api/v1/task-runs/{task_run_id}/admission",
    response_model=AdmissionDecision,
    tags=["executions"],
)
async def get_task_admission(
    task_run_id: UUID,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AdmissionDecision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    decision = await repository.get_admission(
        AdmissionResourceType.TASK,
        task_run_id,
        tenant_id=tenant_id,
    )
    if decision is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="admission not found")
    return decision


@app.get(
    "/api/v1/admissions/diagnostics",
    response_model=AdmissionDiagnostics,
    tags=["operations"],
)
async def get_admission_diagnostics(
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AdmissionDiagnostics:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    diagnostics = await repository.admission_diagnostics(tenant_id=tenant_id)
    total_demand = diagnostics.active_reservations + diagnostics.queued_requests
    ADMISSION_PRESSURE.set(diagnostics.queued_requests / max(1, total_demand))
    return diagnostics


@app.post("/api/v1/admissions/reconcile", tags=["operations"])
async def reconcile_admissions(
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: int = 100,
) -> dict[str, int]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="tenant",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        promoted = await repository.reconcile_admission(tenant_id=tenant_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return {"promoted": promoted}


@app.post(
    "/api/v1/reconciliations",
    response_model=ReconciliationRun,
    status_code=status.HTTP_201_CREATED,
    tags=["operations"],
)
async def run_reconciliation(
    request: ReconciliationRequest,
    service: ReconciliationServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ReconciliationRun:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="tenant",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await service.run(
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ReconciliationAlreadyRunningError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/reconciliations",
    response_model=list[ReconciliationRun],
    tags=["operations"],
)
async def list_reconciliations(
    service: ReconciliationServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[ReconciliationRun]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="tenant",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await service.list_runs(tenant_id=tenant_id, limit=limit)


@app.get(
    "/api/v1/reconciliations/{run_id}",
    response_model=ReconciliationRun,
    tags=["operations"],
)
async def get_reconciliation(
    run_id: UUID,
    service: ReconciliationServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ReconciliationRun:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="tenant",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await service.get(run_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get(
    "/api/v1/lifecycle/policies",
    response_model=tuple[LifecyclePolicy, ...],
    tags=["lifecycle"],
)
async def list_lifecycle_policies(
    repository: RetentionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> tuple[LifecyclePolicy, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await repository.list_policies(tenant_id)


@app.post(
    "/api/v1/lifecycle/policies",
    response_model=LifecyclePolicy,
    status_code=status.HTTP_201_CREATED,
    tags=["lifecycle"],
)
async def create_lifecycle_policy(
    request: LifecyclePolicyDraft,
    repository: RetentionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> LifecyclePolicy:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="instance" if request.scope is LifecycleScope.INSTANCE else "lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=None if request.scope is LifecycleScope.INSTANCE else tenant_id,
        namespace=request.namespace,
    )
    return await repository.save_policy(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@app.put(
    "/api/v1/lifecycle/policies/{policy_id}",
    response_model=LifecyclePolicy,
    tags=["lifecycle"],
)
async def update_lifecycle_policy(
    policy_id: UUID,
    request: LifecyclePolicyDraft,
    repository: RetentionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> LifecyclePolicy:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="instance" if request.scope is LifecycleScope.INSTANCE else "lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=None if request.scope is LifecycleScope.INSTANCE else tenant_id,
        namespace=request.namespace,
    )
    try:
        return await repository.save_policy(
            tenant_id,
            request,
            actor_id=str(actor.principal_id),
            policy_id=policy_id,
            expected_version=expected_version,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/lifecycle/legal-holds",
    response_model=tuple[LifecycleLegalHold, ...],
    tags=["lifecycle"],
)
async def list_lifecycle_legal_holds(
    repository: RetentionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> tuple[LifecycleLegalHold, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await repository.list_holds(tenant_id)


@app.post(
    "/api/v1/lifecycle/legal-holds",
    response_model=LifecycleLegalHold,
    status_code=status.HTTP_201_CREATED,
    tags=["lifecycle"],
)
async def create_lifecycle_legal_hold(
    request: LifecycleLegalHoldDraft,
    repository: RetentionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> LifecycleLegalHold:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=request.namespace,
    )
    return await repository.create_hold(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@app.post(
    "/api/v1/lifecycle/legal-holds/{hold_id}/release",
    response_model=LifecycleLegalHold,
    tags=["lifecycle"],
)
async def release_lifecycle_legal_hold(
    hold_id: UUID,
    repository: RetentionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> LifecycleLegalHold:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.release_hold(
            tenant_id,
            hold_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/lifecycle/previews",
    response_model=LifecycleJob,
    status_code=status.HTTP_201_CREATED,
    tags=["lifecycle"],
)
async def preview_lifecycle_purge(
    request: LifecyclePreviewRequest,
    repository: RetentionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> LifecycleJob:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.preview(
            tenant_id,
            request.policy_id,
            actor_id=str(actor.principal_id),
            reason=request.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get(
    "/api/v1/lifecycle/jobs",
    response_model=tuple[LifecycleJob, ...],
    tags=["lifecycle"],
)
async def list_lifecycle_jobs(
    repository: RetentionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> tuple[LifecycleJob, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await repository.list_jobs(tenant_id, limit=limit)


@app.get(
    "/api/v1/lifecycle/jobs/{job_id}",
    response_model=LifecycleJob,
    tags=["lifecycle"],
)
async def get_lifecycle_job(
    job_id: UUID,
    repository: RetentionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> LifecycleJob:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.get_job(tenant_id, job_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/lifecycle/jobs/{job_id}/execute",
    response_model=LifecycleJob,
    tags=["lifecycle"],
)
async def execute_lifecycle_job(
    job_id: UUID,
    request: LifecycleExecuteRequest,
    service: RetentionServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> LifecycleJob:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await service.confirm_and_process(tenant_id, job_id, request.confirmation)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post(
    "/api/v1/lifecycle/jobs/{job_id}/resume",
    response_model=LifecycleJob,
    tags=["lifecycle"],
)
async def resume_lifecycle_job(
    job_id: UUID,
    service: RetentionServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> LifecycleJob:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="lifecycle",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await service.process_once(tenant_id, job_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/upgrades/policy",
    response_model=UpgradePolicy,
    tags=["upgrades"],
)
async def get_upgrade_policy(
    service: UpgradeServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> UpgradePolicy:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="instance",
        action=PermissionAction.MANAGE,
    )
    return service.policy


@app.post(
    "/api/v1/upgrades/preflight",
    response_model=UpgradeReport,
    tags=["upgrades"],
)
async def run_upgrade_preflight(
    request: UpgradeReportRequest,
    service: UpgradeServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> UpgradeReport:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="instance",
        action=PermissionAction.MANAGE,
    )
    try:
        return await service.pre_upgrade(request.from_version, request.to_version)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/v1/upgrades/postflight",
    response_model=UpgradeReport,
    tags=["upgrades"],
)
async def run_upgrade_postflight(
    request: UpgradeReportRequest,
    service: UpgradeServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> UpgradeReport:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="instance",
        action=PermissionAction.MANAGE,
    )
    try:
        return await service.post_upgrade(request.from_version, request.to_version)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/upgrades/events/upcast",
    response_model=PersistedEventMigration,
    tags=["upgrades"],
)
async def preview_upgrade_event_upcast(
    repository: UpgradeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> PersistedEventMigration:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="instance",
        action=PermissionAction.MANAGE,
    )
    return await repository.preview_event_upcast()


@app.post(
    "/api/v1/upgrades/events/upcast",
    response_model=PersistedEventMigration,
    tags=["upgrades"],
)
async def run_upgrade_event_upcast(
    request: PersistedEventMigrationRequest,
    repository: UpgradeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> PersistedEventMigration:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="instance",
        action=PermissionAction.MANAGE,
    )
    try:
        return await repository.upcast_events(
            request.confirmation,
            actor_id=str(actor.principal_id),
            reason=request.reason,
            batch_size=request.batch_size,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post(
    "/api/v1/upgrades/configuration/migrate",
    response_model=ConfigurationMigration,
    tags=["upgrades"],
)
async def migrate_upgrade_configuration(
    request: ConfigurationMigrationRequest,
    service: UpgradeServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> ConfigurationMigration:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="instance",
        action=PermissionAction.MANAGE,
    )
    try:
        return service.migrate_configuration(
            request.kind,
            request.document,
            target_version=request.target_version,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/operations/topology",
    response_model=ServiceTopology,
    tags=["operations"],
)
async def get_service_topology(
    repository: ServiceRegistryRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> ServiceTopology:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="instance",
        action=PermissionAction.MANAGE,
    )
    return await repository.topology()


@app.post(
    "/api/v1/operations/services/{instance_id}/drain",
    response_model=ServiceInstance,
    tags=["operations"],
)
async def drain_service_instance(
    instance_id: UUID,
    request: ServiceDrainRequest,
    repository: ServiceRegistryRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> ServiceInstance:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="instance",
        action=PermissionAction.MANAGE,
    )
    try:
        return await repository.request_drain(
            instance_id,
            expected_version=request.expected_version,
            actor_id=str(actor.principal_id),
            reason=request.reason,
        )
    except ServiceFenceError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post(
    "/api/v1/backfills/preview",
    response_model=BackfillPreview,
    tags=["backfills"],
)
async def preview_backfill(
    request: BackfillSpec,
    service: BackfillServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> BackfillPreview:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=request.namespace,
    )
    try:
        return await service.preview(request, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/v1/backfills",
    response_model=BackfillRecord,
    status_code=status.HTTP_201_CREATED,
    tags=["backfills"],
)
async def create_backfill(
    request: BackfillSpec,
    service: BackfillServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> BackfillRecord:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=request.namespace,
    )
    try:
        return await service.create(
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (TenantQuotaExceeded, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/backfills",
    response_model=list[BackfillRecord],
    tags=["backfills"],
)
async def list_backfills(
    repository: BackfillRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    query: Annotated[CollectionQuery, Depends(default_limited_collection_query)],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    backfills = await repository.list_backfills(tenant_id=tenant_id, limit=1000)
    return collection_response(backfills, query, default_limit=100)


@app.get(
    "/api/v1/backfills/{backfill_id}",
    response_model=BackfillRecord,
    tags=["backfills"],
)
async def get_backfill(
    backfill_id: UUID,
    repository: BackfillRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> BackfillRecord:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return await repository.refresh_backfill(backfill_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


async def _transition_backfill(
    backfill_id: UUID,
    state: BackfillState,
    request: BackfillActionRequest,
    repository: PostgresBackfillRepository,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> BackfillRecord:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.transition_backfill(
            backfill_id,
            state,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            reason=request.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post(
    "/api/v1/backfills/{backfill_id}/pause",
    response_model=BackfillRecord,
    tags=["backfills"],
)
async def pause_backfill(
    backfill_id: UUID,
    request: BackfillActionRequest,
    repository: BackfillRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> BackfillRecord:
    return await _transition_backfill(
        backfill_id,
        BackfillState.PAUSED,
        request,
        repository,
        actor,
        authorization_service,
        tenant_id,
    )


@app.post(
    "/api/v1/backfills/{backfill_id}/resume",
    response_model=BackfillRecord,
    tags=["backfills"],
)
async def resume_backfill(
    backfill_id: UUID,
    request: BackfillActionRequest,
    repository: BackfillRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> BackfillRecord:
    return await _transition_backfill(
        backfill_id,
        BackfillState.RUNNING,
        request,
        repository,
        actor,
        authorization_service,
        tenant_id,
    )


@app.post(
    "/api/v1/backfills/{backfill_id}/cancel",
    response_model=BackfillRecord,
    tags=["backfills"],
)
async def cancel_backfill(
    backfill_id: UUID,
    request: BackfillActionRequest,
    repository: BackfillRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> BackfillRecord:
    return await _transition_backfill(
        backfill_id,
        BackfillState.CANCELLED,
        request,
        repository,
        actor,
        authorization_service,
        tenant_id,
    )


@app.get(
    "/api/v1/workers",
    response_model=list[WorkerInventory],
    tags=["workers"],
)
async def list_workers(
    workers: WorkerRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="worker",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    inventory = await workers.list_worker_inventory(tenant_id=tenant_id)
    return collection_response(inventory, query)


@app.get(
    "/api/v1/runners/capabilities",
    response_model=list[RunnerCapabilities],
    tags=["workers"],
)
async def list_runner_capabilities(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    settings: SettingsDependency,
) -> list[RunnerCapabilities]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="worker",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    capabilities = [KubernetesJobRunner.CAPABILITIES]
    if settings.docker_runner_enabled:
        capabilities.insert(0, DockerContainerRunner.CAPABILITIES)
    if settings.is_local_process_runner_enabled:
        capabilities.insert(0, LocalProcessRunner.CAPABILITIES)
    return capabilities


@app.post(
    "/api/v1/workers/{worker_id}/drain",
    response_model=WorkerInventory,
    tags=["workers"],
)
async def drain_worker(
    worker_id: UUID,
    workers: WorkerRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int, Query(alias="expectedVersion", ge=1)],
) -> WorkerInventory:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="worker",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await workers.drain_worker(
            worker_id,
            tenant_id=tenant_id,
            expected_version=expected_version,
            actor_id=str(actor.principal_id),
        )
    except WorkerFenceError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/executions/{execution_id}",
    response_model=ExecutionDetail,
    tags=["executions"],
)
async def get_execution(
    execution_id: UUID,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    task_offset: Annotated[int, Query(alias="taskOffset", ge=0)] = 0,
    task_limit: Annotated[int | None, Query(alias="taskLimit", ge=1, le=1000)] = None,
) -> ExecutionDetail:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=execution.namespace,
    )
    task_runs = await repository.list_task_runs(
        execution_id,
        tenant_id=tenant_id,
        include_iterations=False,
        limit=task_limit,
        offset=task_offset,
    )
    task_run_summary = await repository.summarize_task_runs(
        execution_id,
        tenant_id=tenant_id,
        include_iterations=False,
    )
    flow = await repository.get_flow(
        execution.namespace,
        execution.flow_id,
        tenant_id=tenant_id,
        revision=execution.flow_revision,
    )
    return _public_execution_detail(
        flow,
        execution,
        task_runs,
        task_run_summary=task_run_summary,
        task_run_offset=task_offset,
    )


@app.get(
    "/api/v1/executions/{execution_id}/agent-sessions",
    response_model=list[AgentSessionSummary],
    tags=["executions"],
)
async def list_execution_agent_sessions(
    execution_id: UUID,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[AgentSessionSummary]:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(getattr(execution, "trigger", None), dict) and execution.trigger.get(
        "ameshAgentSessionId"
    ):
        await _authorize_agent_session_access(
            execution,
            actor=actor,
            authorization_service=authorization_service,
            tenant_id=tenant_id,
        )
    else:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
        )
    return [
        _public_agent_session_detail(
            AgentSessionDetail(session=session, events=()),
            after_event_index=0,
            limit=100,
        ).session
        for session in await sessions.list_execution_sessions(tenant_id, execution_id)
    ]


@app.get(
    "/api/v1/executions/{execution_id}/agent-sessions/{task_run_id}",
    response_model=AgentSessionDetailResponse,
    tags=["executions"],
)
async def get_execution_agent_session(
    execution_id: UUID,
    task_run_id: UUID,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    attempt: Annotated[int, Query(ge=1)] = 1,
    after_event_index: Annotated[int, Query(alias="afterEventIndex", ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> AgentSessionDetailResponse:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        if isinstance(getattr(execution, "trigger", None), dict) and execution.trigger.get(
            "ameshAgentSessionId"
        ):
            await _authorize_agent_session_access(
                execution,
                actor=actor,
                authorization_service=authorization_service,
                tenant_id=tenant_id,
            )
        else:
            await authorize_request(
                authorization_service,
                actor,
                resource_type="execution",
                action=PermissionAction.VIEW,
                tenant_id=tenant_id,
            )
        detail = await sessions.get_session(tenant_id, task_run_id, attempt)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if detail.session.tenant_id != tenant_id or detail.session.execution_id != execution_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="agent session does not exist"
        )
    return _public_agent_session_detail(detail, after_event_index=after_event_index, limit=limit)


async def _launch_agent_session(
    request: AgentSessionCreateRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    resources: AgentResourceRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-ID")] = None,
) -> AgentSessionLaunchResponse:
    if request.namespace is None or request.agent is None or request.agent_revision is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="agentRef or namespace, agent, and agentRevision is required",
        )
    namespace = request.namespace
    if request.model_profile is not None or request.budgets is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="modelProfile and budgets are owned by the pinned agent definition",
        )
    if request.harness is not None and request.harness != settings.agent_session_harness:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="requested harness does not match the configured session harness",
        )
    if settings.agent_session_harness not in AGENT_SESSION_HARNESS_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="configured agent-session harness is not registered",
        )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    effective_idempotency_key = _resolve_idempotency_key(
        request.idempotency_key,
        idempotency_key,
    )
    service_session_id = _agent_session_service_session_id(
        tenant_id,
        namespace,
        str(actor.principal_id),
        effective_idempotency_key,
    )
    execution_idempotency_key = _agent_session_execution_idempotency_key(
        service_session_id,
        effective_idempotency_key,
    )
    try:
        preview = await resources.preview_agent(
            tenant_id,
            namespace,
            request.agent,
            agent_revision=request.agent_revision,
        )
        try:
            Draft202012Validator(preview.envelope.input_schema).validate(request.input)
        except JsonSchemaValidationError as exc:
            raise ValueError(
                f"input does not match the agent schema: {exc.message[:1024]}"
            ) from exc
        admission_limits, provider_ids = _agent_session_admission_limits(preview.envelope)
        task = TaskDefinition.model_validate(
            {
                "id": "agent",
                "type": "agent.session",
                "agent": request.agent,
                "agentRevision": request.agent_revision,
                "input": request.input,
                "invalidOutputPolicy": request.invalid_output_policy,
                "maxRepairAttempts": request.max_repair_attempts,
                "approvalTask": request.approval_task,
                "dataHandling": request.data_handling.value,
                "businessAssertions": request.business_assertions,
                "memoryReadKeys": request.memory_read_keys,
                "memoryWriteKey": request.memory_write_key,
                "timeoutSeconds": request.timeout_seconds,
                "retry": request.retry.model_dump(mode="json", by_alias=True),
                "concurrency": [
                    item.model_dump(mode="json", by_alias=True) for item in admission_limits[1:]
                ],
                "contract": {
                    "secretScopes": preview.envelope.permissions.secret_scopes,
                },
            }
        )
        flow = FlowDefinition(
            id=_agent_session_flow_id(namespace, request.agent, request.agent_revision),
            namespace=namespace,
            tasks=[task],
            concurrency=[admission_limits[0]],
        )
        detail = await _execute_flow(
            repository,
            task_cache,
            flow,
            CreateExecutionRequest(
                namespace=request.namespace,
                flowId=flow.id,
                inputs={},
                runner=request.runner,
                idempotencyKey=execution_idempotency_key,
            ),
            settings,
            operational_controls=operational_controls,
            shared_resources=shared_resources,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            actor=actor,
            authorization_service=authorization_service,
            background_tasks=background_tasks,
            launch_source=ExecutionLaunchSource.API,
            idempotency_key=execution_idempotency_key,
            respond_async=_prefers_async_response(prefer),
            trigger_context={
                "ameshAgentSessionId": str(service_session_id),
                "ameshAgentRef": f"{namespace}/{request.agent}@{request.agent_revision}",
                "ameshActorId": str(actor.principal_id),
                "ameshProviderId": ",".join(provider_ids),
                "ameshHarness": AGENT_SESSION_HARNESS_REGISTRY[settings.agent_session_harness],
                "ameshBudget": preview.envelope.hard_limits.model_dump(mode="json", by_alias=True),
            },
            correlation_id=correlation_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    task_run = next((item for item in detail.task_runs if item.task_id == "agent"), None)
    if task_run is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="agent session task was not created",
        )
    public_session: AgentSessionSummary | None = None
    try:
        session_detail = await get_service_agent_session_detail(
            service_session_id,
            sessions=sessions,
            tenant_id=tenant_id,
        )
        public_session = _public_agent_session_detail(
            session_detail,
            after_event_index=0,
            limit=100,
        ).session
        public_session = public_session.model_copy(
            update={
                "agentRef": f"{namespace}/{request.agent}@{request.agent_revision}",
                "modelProfile": request.model_profile,
            }
        )
    except LookupError:
        pass
    result = AgentSessionLaunchResponse(
        sessionId=service_session_id,
        executionId=detail.execution.execution_id,
        taskRunId=task_run.task_run_id,
        attempt=task_run.current_attempt or 1,
        executionState=detail.execution.state,
        session=public_session,
    )
    if _prefers_async_response(prefer) and detail.execution.state is ExecutionState.RUNNING:
        response.status_code = status.HTTP_202_ACCEPTED
        response.headers["Preference-Applied"] = "respond-async"
    response.headers["Location"] = f"/api/v1/agent-sessions/{service_session_id}"
    if correlation_id is not None:
        response.headers["X-Correlation-ID"] = correlation_id
    return result


@app.post(
    "/api/v1/agent-sessions",
    response_model=AgentSessionLaunchResponse,
    tags=["agent-sessions"],
)
async def create_agent_session(
    request: AgentSessionCreateRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    resources: AgentResourceRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-ID")] = None,
) -> AgentSessionLaunchResponse:
    return await _launch_agent_session(
        request,
        background_tasks,
        response,
        repository,
        task_cache,
        shared_resources,
        operational_controls,
        sessions,
        resources,
        settings,
        actor,
        authorization_service,
        tenant_id,
        prefer,
        idempotency_key,
        correlation_id,
    )


class _ApplicationSessionFacade:
    """Typed bridge from compatibility transports to the canonical launch path."""

    def __init__(
        self,
        *,
        background_tasks: BackgroundTasks,
        repository: RepositoryDependency,
        task_cache: TaskCacheRepositoryDependency,
        shared_resources: SharedResourceRepositoryDependency,
        operational_controls: OperationalControlRepositoryDependency,
        sessions: AgentSessionRepositoryDependency,
        resources: AgentResourceRepositoryDependency,
        settings: SettingsDependency,
        actor: ActorDependency,
        authorization_service: AuthorizationServiceDependency,
    ) -> None:
        self._background_tasks = background_tasks
        self._repository = repository
        self._task_cache = task_cache
        self._shared_resources = shared_resources
        self._operational_controls = operational_controls
        self._sessions = sessions
        self._resources = resources
        self._settings = settings
        self._actor = actor
        self._authorization_service = authorization_service

    async def complete(
        self,
        request: CanonicalSessionRequest,
        *,
        tenant_id: str,
        namespace: str,
        actor_id: str,
        idempotency_key: str | None,
    ) -> CanonicalSessionResult:
        del actor_id  # The authenticated actor is carried by the canonical dependency.
        try:
            create_request = AgentSessionCreateRequest.model_validate(
                {
                    "agentRef": request.profile,
                    "input": {"messages": list(request.messages)},
                    "idempotencyKey": idempotency_key,
                }
            )
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="model must be an authorized agent profile <namespace>/<key>@<revision>",
            ) from exc
        launch = await _launch_agent_session(
            create_request,
            self._background_tasks,
            Response(),
            self._repository,
            self._task_cache,
            self._shared_resources,
            self._operational_controls,
            self._sessions,
            self._resources,
            self._settings,
            self._actor,
            self._authorization_service,
            tenant_id,
            None,
            idempotency_key,
            None,
        )
        location = f"/api/v1/agent-sessions/{launch.session_id}"
        if launch.execution_state is not ExecutionState.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    f"agent session {launch.session_id} is "
                    f"{launch.execution_state.value}; retry this idempotent request or retrieve "
                    f"the accepted session at {location}"
                ),
                headers={"Location": location, "Retry-After": "1"},
            )
        try:
            detail = await get_service_agent_session_detail(
                launch.session_id,
                sessions=self._sessions,
                tenant_id=tenant_id,
            )
        except LookupError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    f"agent session {launch.session_id} result is not yet available; retry this "
                    f"idempotent request or retrieve the accepted session at {location}"
                ),
                headers={"Location": location, "Retry-After": "1"},
            ) from exc
        public = _public_agent_session_detail(detail, after_event_index=0, limit=100).session
        if public.state is AgentSessionState.FAILED:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=public.error or "agent session failed",
            )
        if public.state is not AgentSessionState.SUCCEEDED or public.final_result is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    f"agent session {launch.session_id} is {public.state.value}; retry this "
                    f"idempotent request or retrieve the accepted session at {location}"
                ),
                headers={"Location": location, "Retry-After": "1"},
            )
        harness = (
            HarnessProvenance(
                adapter=public.harness.adapter,
                adapterVersion=public.harness.adapter_version,
            )
            if public.harness is not None
            else None
        )
        return CanonicalSessionResult(
            sessionId=launch.session_id,
            profile=request.profile,
            content=public.final_result,
            usage=_durable_usage(detail.events),
            harness=harness,
        )


@app.post(
    "/v1/chat/completions",
    response_model=OpenAIChatCompletionResponse,
    tags=["agent-sessions"],
)
async def openai_chat_completions(
    request: OpenAIChatCompletionRequest,
    background_tasks: BackgroundTasks,
    repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    resources: AgentResourceRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> OpenAIChatCompletionResponse | StreamingResponse:
    unsupported = {
        "temperature": request.temperature,
        "top_p": request.top_p,
        "max_tokens": request.max_tokens,
        "max_completion_tokens": request.max_completion_tokens,
        "user": request.user,
        "response_format": request.response_format,
    }
    supplied = next((name for name, value in unsupported.items() if value is not None), None)
    if supplied is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{supplied} is pinned by the agent profile and cannot be overridden",
        )
    at = request.model.rfind("@")
    slash = request.model.rfind("/", 0, at)
    if at <= 0 or slash <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="model must be an authorized agent profile <namespace>/<key>@<revision>",
        )
    namespace = request.model[:slash]
    facade = _ApplicationSessionFacade(
        background_tasks=background_tasks,
        repository=repository,
        task_cache=task_cache,
        shared_resources=shared_resources,
        operational_controls=operational_controls,
        sessions=sessions,
        resources=resources,
        settings=settings,
        actor=actor,
        authorization_service=authorization_service,
    )
    adapter = OpenAICompatibleSessionAdapter(facade)
    result = await adapter.create_chat_completion(
        request,
        tenant_id=tenant_id,
        namespace=namespace,
        actor_id=str(actor.principal_id),
        idempotency_key=idempotency_key,
    )
    if request.stream:
        return StreamingResponse(openai_sse_events(result), media_type="text/event-stream")
    return result


@app.post(
    "/v1/responses",
    response_model=OpenAIResponse,
    tags=["agent-sessions"],
)
async def openai_responses(
    request: OpenAIResponseRequest,
    background_tasks: BackgroundTasks,
    repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    resources: AgentResourceRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> OpenAIResponse | StreamingResponse:
    unsupported = {
        "temperature": request.temperature,
        "top_p": request.top_p,
        "max_output_tokens": request.max_output_tokens,
        "user": request.user,
    }
    supplied = next((name for name, value in unsupported.items() if value is not None), None)
    if supplied is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{supplied} is pinned by the agent profile and cannot be overridden",
        )
    if request.text is not None and request.text.format.type != "text":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="structured response formats must be declared by the pinned agent schema",
        )
    at = request.model.rfind("@")
    slash = request.model.rfind("/", 0, at)
    if at <= 0 or slash <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="model must be an authorized agent profile <namespace>/<key>@<revision>",
        )
    facade = _ApplicationSessionFacade(
        background_tasks=background_tasks,
        repository=repository,
        task_cache=task_cache,
        shared_resources=shared_resources,
        operational_controls=operational_controls,
        sessions=sessions,
        resources=resources,
        settings=settings,
        actor=actor,
        authorization_service=authorization_service,
    )
    adapter = OpenAICompatibleSessionAdapter(facade)
    result = await adapter.create_response(
        request,
        tenant_id=tenant_id,
        namespace=request.model[:slash],
        actor_id=str(actor.principal_id),
        idempotency_key=idempotency_key,
    )
    if request.stream:
        return StreamingResponse(openai_response_sse_events(result), media_type="text/event-stream")
    return result


@app.get(
    "/api/v1/agent-sessions/harnesses",
    response_model=dict[str, AgentSessionHarnessCatalogEntry],
    tags=["agent-sessions"],
)
async def list_agent_session_harnesses(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> dict[str, AgentSessionHarnessCatalogEntry]:
    """Return registered harness provenance without exposing worker details."""

    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return {
        alias: AgentSessionHarnessCatalogEntry.model_validate(metadata)
        for alias, metadata in AGENT_SESSION_HARNESS_REGISTRY.items()
    }


@app.get(
    "/api/v1/agent-sessions",
    response_model=list[AgentSessionServiceItem],
    tags=["agent-sessions"],
)
async def list_agent_sessions(
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[AgentSessionServiceItem]:
    manage = await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            resource_type="execution",
            action=PermissionAction.MANAGE,
        )
    )
    owner_id = None if manage.allowed else str(actor.principal_id)
    items: list[AgentSessionServiceItem] = []
    for service_session_id, execution_id, agent_ref, record in await sessions.list_service_sessions(
        tenant_id,
        limit=limit,
        owner_id=owner_id,
    ):
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        try:
            await _authorize_agent_session_access(
                execution,
                actor=actor,
                authorization_service=authorization_service,
                tenant_id=tenant_id,
            )
        except HTTPException as exc:
            if exc.status_code in {status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND}:
                continue
            raise
        if record is None:
            items.append(
                AgentSessionServiceItem(
                    sessionId=service_session_id,
                    attemptSessionId=None,
                    session=_queued_agent_session_summary(
                        service_session_id,
                        execution,
                        agent_ref=agent_ref,
                    ),
                )
            )
            continue
        summary = _public_agent_session_detail(
            AgentSessionDetail(session=record, events=()),
            after_event_index=0,
            limit=100,
        ).session
        items.append(
            AgentSessionServiceItem(
                sessionId=service_session_id,
                attemptSessionId=record.session_id,
                session=_control_agent_session_summary(
                    service_session_id,
                    execution,
                    summary,
                    agent_ref=agent_ref,
                ),
            )
        )
    return items


@app.get(
    "/api/v1/agent-sessions/{service_session_id}/events",
    response_model=AgentSessionServiceDetailResponse,
    tags=["agent-sessions"],
)
async def get_agent_session_events(
    service_session_id: UUID,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    after_event_index: Annotated[int, Query(alias="afterEventIndex", ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> AgentSessionServiceDetailResponse:
    return await get_service_agent_session_response(
        service_session_id,
        repository=repository,
        sessions=sessions,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
        after_event_index=after_event_index,
        limit=limit,
    )


@app.get(
    "/api/v1/agent-sessions/{service_session_id}/messages",
    response_model=AgentSessionServiceDetailResponse,
    tags=["agent-sessions"],
)
async def get_agent_session_messages(
    service_session_id: UUID,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    after_event_index: Annotated[int, Query(alias="afterEventIndex", ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> AgentSessionServiceDetailResponse:
    return await get_service_agent_session_response(
        service_session_id,
        repository=repository,
        sessions=sessions,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
        after_event_index=after_event_index,
        limit=limit,
    )


@app.post(
    "/api/v1/agent-sessions/{service_session_id}/messages",
    status_code=status.HTTP_409_CONFLICT,
    response_model=None,
    tags=["agent-sessions"],
)
async def post_agent_session_message(
    service_session_id: UUID,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NoReturn:
    """Reject follow-up turns until the durable turn mapping is implemented."""

    execution = await _get_service_agent_session_execution(
        service_session_id,
        repository=repository,
        sessions=sessions,
        tenant_id=tenant_id,
    )
    await _authorize_agent_session_access(
        execution,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
    )
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="multi-turn messages are not supported for a completed agent session",
    )


@app.get(
    "/api/v1/agent-sessions/{service_session_id}/events/stream",
    response_class=StreamingResponse,
    tags=["agent-sessions"],
)
async def stream_agent_session_events(
    service_session_id: UUID,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    after_event_index: Annotated[int, Query(alias="afterEventIndex", ge=0)] = 0,
) -> StreamingResponse:
    """Stream durable redacted events with a bounded reconnectable poll window."""

    await get_service_agent_session_response(
        service_session_id,
        repository=repository,
        sessions=sessions,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
        after_event_index=after_event_index,
        limit=100,
    )

    async def events() -> AsyncIterator[str]:
        cursor = after_event_index
        for _ in range(30):
            try:
                projected = await get_service_agent_session_response(
                    service_session_id,
                    repository=repository,
                    sessions=sessions,
                    actor=actor,
                    authorization_service=authorization_service,
                    tenant_id=tenant_id,
                    after_event_index=cursor,
                    limit=100,
                )
            except LookupError:
                yield (
                    json.dumps(
                        {
                            "eventType": "heartbeat",
                            "sessionId": str(service_session_id),
                            "nextEventIndex": cursor,
                        },
                        separators=(",", ":"),
                    )
                    + "\n"
                )
                await asyncio.sleep(1)
                continue
            if projected.events:
                for event in projected.events:
                    yield json.dumps(jsonable_encoder(event), separators=(",", ":")) + "\n"
                cursor = projected.events[-1].event_index
            else:
                yield (
                    json.dumps(
                        {
                            "eventType": "heartbeat",
                            "sessionId": str(service_session_id),
                            "nextEventIndex": cursor,
                        },
                        separators=(",", ":"),
                    )
                    + "\n"
                )
            if projected.session.state in {"SUCCEEDED", "FAILED", "CANCELLED"}:
                break
            await asyncio.sleep(1)

    return StreamingResponse(events(), media_type="application/x-ndjson")


@app.get(
    "/api/v1/agent-sessions/{service_session_id}/result",
    response_model=AgentSessionResultResponse,
    tags=["agent-sessions"],
)
async def get_agent_session_result(
    service_session_id: UUID,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentSessionResultResponse:
    detail = await get_service_agent_session_response(
        service_session_id,
        repository=repository,
        sessions=sessions,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
        after_event_index=0,
        limit=100,
    )
    return AgentSessionResultResponse(
        sessionId=service_session_id,
        state=detail.session.state,
        result=detail.session.final_result,
        error=detail.session.error,
    )


@app.get(
    "/api/v1/agent-sessions/{service_session_id}",
    response_model=AgentSessionServiceDetailResponse,
    tags=["agent-sessions"],
)
async def get_agent_session(
    service_session_id: UUID,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    after_event_index: Annotated[int, Query(alias="afterEventIndex", ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> AgentSessionServiceDetailResponse:
    return await get_service_agent_session_response(
        service_session_id,
        repository=repository,
        sessions=sessions,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
        after_event_index=after_event_index,
        limit=limit,
    )


@app.post(
    "/api/v1/agent-sessions/{service_session_id}/{action}",
    response_model=AgentSessionLaunchResponse,
    tags=["agent-sessions"],
)
async def control_agent_session(
    service_session_id: UUID,
    action: Literal["cancel", "pause", "retry", "resume"],
    request: AgentSessionControlRequest,
    response: Response,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentSessionLaunchResponse:
    execution = await _get_service_agent_session_execution(
        service_session_id,
        repository=repository,
        sessions=sessions,
        tenant_id=tenant_id,
    )
    try:
        detail = await get_service_agent_session_detail(
            service_session_id,
            sessions=sessions,
            tenant_id=tenant_id,
        )
    except LookupError:
        detail = None
    action_map = {
        "cancel": ExecutionInterventionAction.REQUEST_CANCEL,
        "pause": ExecutionInterventionAction.PAUSE,
        "retry": ExecutionInterventionAction.RESTART,
        "resume": ExecutionInterventionAction.RESUME,
    }
    updated = await apply_execution_control(
        execution.execution_id,
        ExecutionInterventionRequest(
            action=action_map[action],
            expectedVersion=(
                request.expected_version
                if request.expected_version is not None
                else execution.version
            ),
            expectedEpoch=(
                request.expected_epoch if request.expected_epoch is not None else execution.epoch
            ),
            reason=request.reason,
            graceSeconds=request.grace_seconds,
        ),
        repository,
        actor,
        authorization_service,
        tenant_id,
    )
    latest = None
    try:
        latest_detail = await get_service_agent_session_detail(
            service_session_id,
            sessions=sessions,
            tenant_id=tenant_id,
        )
        latest = _public_agent_session_detail(
            latest_detail,
            after_event_index=0,
            limit=100,
        ).session
        task_run_id = latest.task_run_id
        attempt = latest.attempt
    except LookupError:
        if detail is not None:
            task_run_id = detail.session.task_run_id
            attempt = detail.session.attempt
        else:
            task_runs = await repository.list_task_runs(execution.execution_id, tenant_id=tenant_id)
            task_run = next((item for item in task_runs if item.task_id == "agent"), None)
            if task_run is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="agent task is not yet materialized",
                ) from None
            task_run_id = task_run.task_run_id
            attempt = task_run.current_attempt or 1
    response.headers["Location"] = f"/api/v1/agent-sessions/{service_session_id}"
    return AgentSessionLaunchResponse(
        sessionId=service_session_id,
        executionId=updated.execution.execution_id,
        taskRunId=task_run_id,
        attempt=attempt,
        executionState=updated.execution.state,
        session=latest,
    )


@app.get(
    "/api/v1/executions/{execution_id}/files",
    response_model=list[ExecutionArtifact],
    tags=["executions"],
)
async def list_execution_files(
    execution_id: UUID,
    repository: RepositoryDependency,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[ExecutionArtifact]:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=execution.namespace,
    )
    return await metadata.list_artifacts(execution_id, tenant_id=tenant_id)


@app.get(
    "/api/v1/executions/{execution_id}/files/{artifact_id}",
    response_class=StreamingResponse,
    tags=["executions"],
)
async def download_execution_file(
    execution_id: UUID,
    artifact_id: UUID,
    repository: RepositoryDependency,
    metadata: MetadataRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> StreamingResponse:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=execution.namespace,
    )
    artifacts = await metadata.list_artifacts(execution_id, tenant_id=tenant_id)
    selected = next((item for item in artifacts if item.artifact_id == artifact_id), None)
    if selected is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="execution file not found"
        )
    filename = Path(selected.logical_path or "execution-file").name
    return StreamingResponse(
        build_object_store(settings).get(tenant_id, selected.uri),
        media_type=selected.media_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get(
    "/api/v1/executions/{execution_id}/graph",
    response_model=FlowGraph,
    tags=["executions"],
)
async def get_execution_graph(
    execution_id: UUID,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowGraph:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
            namespace=execution.namespace,
        )
        flow = await repository.get_flow(
            execution.namespace,
            execution.flow_id,
            tenant_id=tenant_id,
            revision=execution.flow_revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    task_runs = await repository.list_task_runs(
        execution_id,
        tenant_id=tenant_id,
        include_iterations=False,
    )
    iteration_summaries = await repository.list_iteration_summaries(
        execution_id,
        tenant_id=tenant_id,
    )
    return _build_flow_graph(flow, task_runs, iteration_summaries)


async def _authorized_realtime_filter(
    filters: RealtimeFilter,
    *,
    repository: PostgresExecutionRepository,
    authorization_service: AuthorizationService,
    actor: ActorContext,
    tenant_id: str,
) -> RealtimeFilter:
    namespace = filters.namespace
    if filters.execution_id is not None:
        try:
            execution = await repository.get_execution(filters.execution_id, tenant_id=tenant_id)
        except LookupError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        if namespace is not None and namespace != execution.namespace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="execution unavailable"
            )
        if filters.flow_id is not None and filters.flow_id != execution.flow_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="execution unavailable"
            )
        namespace = execution.namespace
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    audit_decision = await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=namespace,
            resource_type="audit",
            action=PermissionAction.VIEW,
        )
    )
    return filters.model_copy(
        update={
            "namespace": namespace if filters.execution_id is not None else filters.namespace,
            "include_audit": filters.include_audit and audit_decision.allowed,
        }
    )


@app.get(
    "/api/v1/realtime/events",
    response_model=RealtimeEventPage,
    tags=["realtime"],
)
async def list_realtime_events(
    realtime: RealtimeRepositoryDependency,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    cursor: Annotated[str | None, Query(description="Opaque reconnect cursor")] = None,
    namespace: str | None = None,
    flow_id: Annotated[str | None, Query(alias="flowId")] = None,
    execution_id: Annotated[UUID | None, Query(alias="executionId")] = None,
    event_types: Annotated[list[str] | None, Query(alias="eventType")] = None,
    severities: Annotated[list[RealtimeSeverity] | None, Query(alias="severity")] = None,
    include_audit: Annotated[bool, Query(alias="includeAudit")] = True,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> RealtimeEventPage:
    filters = await _authorized_realtime_filter(
        RealtimeFilter(
            namespace=namespace,
            flowId=flow_id,
            executionId=execution_id,
            eventTypes=tuple(event_types or ()),
            severities=tuple(severities or ()),
            includeAudit=include_audit,
        ),
        repository=repository,
        authorization_service=authorization_service,
        actor=actor,
        tenant_id=tenant_id,
    )
    after_cursor = _decode_cursor(cursor)
    oldest, latest = await realtime.cursor_bounds(tenant_id=tenant_id)
    if latest is not None and after_cursor > latest:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cursor is ahead")
    events = await realtime.list_events(
        tenant_id=tenant_id,
        after_cursor=after_cursor,
        filters=filters,
        limit=limit,
    )
    public_events = await _public_realtime_events(
        repository,
        events,
        tenant_id=tenant_id,
    )
    return RealtimeEventPage(
        items=public_events,
        nextCursor=_encode_cursor(events[-1].cursor) if events else cursor,
        oldestCursor=_encode_cursor(oldest) if oldest is not None else None,
        latestCursor=_encode_cursor(latest) if latest is not None else None,
        gap=after_cursor > 0 and oldest is not None and after_cursor < oldest - 1,
    )


@app.get(
    "/api/v1/realtime/stream",
    response_class=StreamingResponse,
    responses={
        status.HTTP_200_OK: {
            "content": {"text/event-stream": {}},
            "description": "Cursor-resumable server-sent event stream",
        }
    },
    tags=["realtime"],
)
async def stream_realtime_events(
    request: Request,
    realtime: RealtimeRepositoryDependency,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    cursor: Annotated[str | None, Query(description="Opaque reconnect cursor")] = None,
    last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
    namespace: str | None = None,
    flow_id: Annotated[str | None, Query(alias="flowId")] = None,
    execution_id: Annotated[UUID | None, Query(alias="executionId")] = None,
    event_types: Annotated[list[str] | None, Query(alias="eventType")] = None,
    severities: Annotated[list[RealtimeSeverity] | None, Query(alias="severity")] = None,
    include_audit: Annotated[bool, Query(alias="includeAudit")] = True,
    buffer_events: Annotated[int, Query(alias="bufferEvents", ge=1, le=1000)] = 100,
    max_events: Annotated[int, Query(alias="maxEvents", ge=1, le=10000)] = 1000,
    heartbeat_seconds: Annotated[float, Query(alias="heartbeatSeconds", ge=0.1, le=30)] = 10,
    stream_seconds: Annotated[float, Query(alias="streamSeconds", ge=1, le=60)] = 15,
) -> StreamingResponse:
    if cursor is not None and last_event_id is not None and cursor != last_event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cursor and Last-Event-ID do not match",
        )
    filters = await _authorized_realtime_filter(
        RealtimeFilter(
            namespace=namespace,
            flowId=flow_id,
            executionId=execution_id,
            eventTypes=tuple(event_types or ()),
            severities=tuple(severities or ()),
            includeAudit=include_audit,
        ),
        repository=repository,
        authorization_service=authorization_service,
        actor=actor,
        tenant_id=tenant_id,
    )
    after_cursor = _decode_cursor(last_event_id or cursor)
    oldest, latest = await realtime.cursor_bounds(tenant_id=tenant_id)
    if latest is not None and after_cursor > latest:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cursor is ahead")

    async def events() -> AsyncIterator[str]:
        nonlocal after_cursor
        loop = asyncio.get_running_loop()
        deadline = loop.time() + stream_seconds
        next_heartbeat = loop.time() + heartbeat_seconds
        sent = 0
        if after_cursor > 0 and oldest is not None and after_cursor < oldest - 1:
            after_cursor = oldest - 1
            yield _sse_event(
                "gap",
                _encode_cursor(after_cursor),
                {
                    "requestedCursor": last_event_id or cursor,
                    "oldestAvailable": _encode_cursor(oldest),
                    "resumeCursor": _encode_cursor(after_cursor),
                },
            )
        while loop.time() < deadline and sent < max_events:
            if await request.is_disconnected():
                break
            batch = await realtime.list_events(
                tenant_id=tenant_id,
                after_cursor=after_cursor,
                filters=filters,
                limit=min(buffer_events, max_events - sent),
            )
            if batch:
                public_batch = await _public_realtime_events(
                    repository,
                    batch,
                    tenant_id=tenant_id,
                )
                for event in public_batch:
                    after_cursor = event.cursor
                    sent += 1
                    yield _sse_event(
                        event.event_type,
                        _encode_cursor(event.cursor),
                        event.model_dump(mode="json", by_alias=True),
                    )
                next_heartbeat = loop.time() + heartbeat_seconds
                continue
            if loop.time() >= next_heartbeat:
                yield f": heartbeat {datetime.now(UTC).isoformat()}\n\n"
                next_heartbeat = loop.time() + heartbeat_seconds
            await asyncio.sleep(min(0.25, heartbeat_seconds))

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "X-Amesh-Buffer-Limit": str(buffer_events),
        },
    )


@app.post(
    "/api/v1/webhook-subscriptions",
    response_model=ProvisionedWebhookSubscription,
    status_code=status.HTTP_201_CREATED,
    tags=["realtime"],
)
async def create_webhook_subscription(
    request: WebhookSubscriptionCreate,
    realtime: RealtimeRepositoryDependency,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
) -> ProvisionedWebhookSubscription:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=request.filters.namespace,
    )
    filters = await _authorized_realtime_filter(
        request.filters,
        repository=repository,
        authorization_service=authorization_service,
        actor=actor,
        tenant_id=tenant_id,
    )
    try:
        validate_http_destination(
            request.url,
            HttpTaskPolicy(
                allowed_hosts=settings.network_egress_allowed_hosts,
                allowed_private_hosts=frozenset(settings.core_http_allowed_private_hosts),
            ),
            resolve_dns=False,
        )
        subscription = await realtime.create_subscription(
            request.model_copy(update={"filters": filters}),
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return ProvisionedWebhookSubscription(
        subscription=subscription,
        signingSecret=derive_webhook_secret(
            settings.webhook_signing_key.get_secret_value(),
            tenant_id,
            subscription.subscription_id,
            subscription.signing_version,
        ),
    )


@app.get(
    "/api/v1/webhook-subscriptions",
    response_model=tuple[WebhookSubscription, ...],
    tags=["realtime"],
)
async def list_webhook_subscriptions(
    realtime: RealtimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> tuple[WebhookSubscription, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await realtime.list_subscriptions(tenant_id=tenant_id)


@app.post(
    "/api/v1/webhook-subscriptions/{subscription_id}/rotate-secret",
    response_model=ProvisionedWebhookSubscription,
    tags=["realtime"],
)
async def rotate_webhook_subscription_secret(
    subscription_id: UUID,
    realtime: RealtimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int, Query(alias="expectedVersion", ge=1)],
) -> ProvisionedWebhookSubscription:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    await realtime.get_subscription(subscription_id, tenant_id=tenant_id)
    try:
        subscription = await realtime.rotate_subscription(
            subscription_id,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return ProvisionedWebhookSubscription(
        subscription=subscription,
        signingSecret=derive_webhook_secret(
            settings.webhook_signing_key.get_secret_value(),
            tenant_id,
            subscription.subscription_id,
            subscription.signing_version,
        ),
    )


@app.post(
    "/api/v1/webhook-subscriptions/{subscription_id}/test",
    response_model=WebhookDelivery,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["realtime"],
)
async def test_webhook_subscription(
    subscription_id: UUID,
    realtime: RealtimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> WebhookDelivery:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await realtime.enqueue_test(
            subscription_id,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get(
    "/api/v1/webhook-subscriptions/{subscription_id}/deliveries",
    response_model=tuple[WebhookDeliveryHistory, ...],
    tags=["realtime"],
)
async def list_webhook_delivery_history(
    subscription_id: UUID,
    realtime: RealtimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> tuple[WebhookDeliveryHistory, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        await realtime.get_subscription(subscription_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return await realtime.list_delivery_history(
        subscription_id,
        tenant_id=tenant_id,
        limit=limit,
    )


@app.post(
    "/api/v1/webhook-deliveries/{delivery_id}/replay",
    response_model=WebhookDelivery,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["realtime"],
)
async def replay_webhook_delivery(
    delivery_id: UUID,
    realtime: RealtimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> WebhookDelivery:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await realtime.replay_delivery(
            delivery_id,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get(
    "/api/v1/executions/{execution_id}/evidence-bundle",
    response_model=EvidenceBundlePageResponse,
    tags=["executions"],
)
async def get_execution_evidence_bundle(
    execution_id: UUID,
    repository: RepositoryDependency,
    metadata: MetadataRepositoryDependency,
    evidence_repository: EvidenceBundleRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    section: Annotated[str, Query(description="Canonical evidence section")] = "trace",
    cursor: Annotated[str | None, Query(description="Opaque section cursor")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> EvidenceBundlePageResponse:
    """Return a verified, bounded, tenant-scoped canonical evidence projection."""

    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
            namespace=execution.namespace,
        )
        bundle = await evidence_repository.get(execution_id, tenant_id=tenant_id)
    except EvidenceNotFoundError:
        try:
            execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
            flow = await repository.get_flow(
                execution.namespace,
                execution.flow_id,
                tenant_id=tenant_id,
                revision=execution.flow_revision,
            )
            events: list[object] = []
            after_cursor = 0
            for _ in range(20):
                batch = await metadata.list_evidence_events(
                    execution_id,
                    tenant_id=tenant_id,
                    after_cursor=after_cursor,
                    limit=500,
                )
                if not batch:
                    break
                events.extend(_public_evidence(flow, execution, batch))
                after_cursor = batch[-1].cursor
                if len(batch) < 500:
                    break
            else:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="execution evidence exceeds the canonical export bound",
                )
            bundle = await evidence_repository.build_and_put(
                execution_id,
                tenant_id,
                events,
                created_at=execution.created_at,
                correlation_id=str(execution.execution_id),
                inputs=execution.inputs,
                outputs=execution.outputs,
            )
        except EvidenceConflictError:
            bundle = await evidence_repository.get(execution_id, tenant_id=tenant_id)
        except EvidenceUnavailableError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="canonical evidence repository unavailable",
            ) from exc
        except LookupError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EvidenceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="canonical evidence repository unavailable",
        ) from exc
    try:
        page = await evidence_repository.page(
            execution_id,
            tenant_id=tenant_id,
            section=section,
            cursor=cursor,
            limit=limit,
        )
    except EvidenceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="execution evidence absent"
        ) from exc
    except EvidenceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="canonical evidence repository unavailable",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return EvidenceBundlePageResponse(
        schemaVersion=bundle.schema_version,
        executionId=str(bundle.execution_id),
        bundleDigest=bundle.digest,
        section=section,
        items=page.items,
        nextCursor=page.next_cursor,
        limit=page.limit,
        total=page.total,
    )


@app.get(
    "/api/v1/executions/{execution_id}/evidence",
    response_model=ExecutionEvidencePage,
    tags=["executions"],
)
async def get_execution_evidence(
    execution_id: UUID,
    repository: RepositoryDependency,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    cursor: Annotated[str | None, Query(description="Opaque reconnect cursor")] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 500,
) -> ExecutionEvidencePage:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
            namespace=execution.namespace,
        )
        flow = await repository.get_flow(
            execution.namespace,
            execution.flow_id,
            tenant_id=tenant_id,
            revision=execution.flow_revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    events = await metadata.list_evidence_events(
        execution_id,
        tenant_id=tenant_id,
        after_cursor=_decode_cursor(cursor),
        limit=limit,
    )
    return ExecutionEvidencePage(
        items=_public_evidence(flow, execution, events),
        nextCursor=_encode_cursor(events[-1].cursor) if events else cursor,
    )


@app.get(
    "/api/v1/executions/{execution_id}/evidence/stream",
    response_class=StreamingResponse,
    responses={
        status.HTTP_200_OK: {
            "content": {"application/x-ndjson": {}},
            "description": "Evidence events streamed as newline-delimited JSON",
        }
    },
    tags=["executions"],
)
async def stream_execution_evidence(
    execution_id: UUID,
    repository: RepositoryDependency,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    cursor: Annotated[str | None, Query(description="Opaque reconnect cursor")] = None,
) -> StreamingResponse:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
            namespace=execution.namespace,
        )
        flow = await repository.get_flow(
            execution.namespace,
            execution.flow_id,
            tenant_id=tenant_id,
            revision=execution.flow_revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    after_cursor = _decode_cursor(cursor)

    async def lines() -> AsyncIterator[str]:
        nonlocal after_cursor, execution
        deadline = asyncio.get_running_loop().time() + 15
        while asyncio.get_running_loop().time() < deadline:
            events = await metadata.list_evidence_events(
                execution_id,
                tenant_id=tenant_id,
                after_cursor=after_cursor,
                limit=500,
            )
            for event in events:
                after_cursor = event.cursor
                public_event = _public_evidence(flow, execution, [event])[0]
                yield (
                    json.dumps(
                        {
                            **public_event.model_dump(mode="json"),
                            "nextCursor": _encode_cursor(after_cursor),
                        },
                        separators=(",", ":"),
                    )
                    + "\n"
                )
            if events:
                continue
            if execution.state in {
                ExecutionState.SUCCESS,
                ExecutionState.FAILED,
                ExecutionState.CANCELLED,
            }:
                break
            await asyncio.sleep(0.25)
            execution = await repository.get_execution(execution_id, tenant_id=tenant_id)

    return StreamingResponse(lines(), media_type="application/x-ndjson")


@app.post(
    "/api/v1/executions/{execution_id}/task-runs/{task_run_id}/resume",
    response_model=PersistedTaskRun,
    tags=["executions"],
)
async def resume_task_run(
    execution_id: UUID,
    task_run_id: UUID,
    request: ResumeTaskRequest,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PersistedTaskRun:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        flow = await repository.get_flow(
            execution.namespace,
            execution.flow_id,
            tenant_id=tenant_id,
            revision=execution.flow_revision,
        )
        task_runs = await repository.list_task_runs(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=execution.namespace,
    )
    task_run = next((item for item in task_runs if item.task_run_id == task_run_id), None)
    if task_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task run not found")
    task = next((item for item in flow.tasks if item.id == task_run.task_id), None)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="task contract unavailable"
        )
    try:
        output, evidence = normalize_task_completion(
            request.completion,
            task.contract.resource_limits,
        )
        return await repository.resume_deferred_task(
            task_run_id,
            request.resume_token,
            output,
            tenant_id=tenant_id,
            evidence=evidence,
        )
    except (TaskResourceLimitError, TaskStateConflictError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/executions/{execution_id}/subflows",
    response_model=list[PersistedSubflow],
    tags=["executions"],
)
async def list_execution_subflows(
    execution_id: UUID,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[PersistedSubflow]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        parent = await repository.get_execution(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=parent.namespace,
    )
    relationships = await repository.list_subflows(execution_id, tenant_id=tenant_id)
    for relationship in relationships:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
            namespace=relationship.child_namespace,
        )
    return relationships


@app.get(
    "/api/v1/executions/{execution_id}/parent-subflow",
    response_model=PersistedSubflow | None,
    tags=["executions"],
)
async def get_execution_parent_subflow(
    execution_id: UUID,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PersistedSubflow | None:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        child = await repository.get_execution(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=child.namespace,
    )
    relationship = await repository.get_parent_subflow(execution_id, tenant_id=tenant_id)
    if relationship is not None:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
            namespace=relationship.parent_namespace,
        )
    return relationship


@app.post(
    "/api/v1/executions/{execution_id}/interventions/preview",
    response_model=ExecutionInterventionPreview,
    tags=["executions"],
)
async def preview_execution_control(
    execution_id: UUID,
    request: ExecutionInterventionPreviewRequest,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ExecutionInterventionPreview:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        flow = await repository.get_flow(
            execution.namespace,
            execution.flow_id,
            tenant_id=tenant_id,
        )
        task_runs = await repository.list_task_runs(execution_id, tenant_id=tenant_id)
        return preview_execution_intervention(
            flow,
            execution,
            task_runs,
            request.action,
            checkpoint_task_id=request.checkpoint_task_id,
            now=await repository.database_time(),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post(
    "/api/v1/executions/{execution_id}/interventions",
    response_model=ExecutionDetail,
    tags=["executions"],
)
async def apply_execution_control(
    execution_id: UUID,
    request: ExecutionInterventionRequest,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ExecutionDetail:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        flow = await repository.get_flow(
            execution.namespace,
            execution.flow_id,
            tenant_id=tenant_id,
        )
        task_runs = await repository.list_task_runs(execution_id, tenant_id=tenant_id)
        preview = preview_execution_intervention(
            flow,
            execution,
            task_runs,
            request.action,
            checkpoint_task_id=request.checkpoint_task_id,
            now=await repository.database_time(),
        )
        updated = await repository.apply_execution_intervention(
            execution_id,
            request.action,
            tenant_id=tenant_id,
            expected_version=request.expected_version,
            expected_epoch=request.expected_epoch,
            actor_id=str(actor.principal_id),
            reason=request.reason,
            grace_period=timedelta(seconds=request.grace_seconds),
            reset_task_ids=preview.impacted_task_ids,
            checkpoint_task_id=request.checkpoint_task_id,
            restart_timeout=(
                timedelta(seconds=flow.timeout_seconds)
                if flow.timeout_seconds is not None
                else None
            ),
        )
        updated_tasks = await repository.list_task_runs(execution_id, tenant_id=tenant_id)
        return _public_execution_detail(flow, updated, updated_tasks)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ExecutionStateConflictError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/executions/{execution_id}/interventions",
    response_model=list[ExecutionInterventionRecord],
    tags=["executions"],
)
async def list_execution_control_history(
    execution_id: UUID,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[ExecutionInterventionRecord]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return await repository.list_execution_interventions(
            execution_id,
            tenant_id=tenant_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get(
    "/api/v1/executions/{execution_id}/logs",
    response_model=list[TaskLog],
    tags=["executions"],
)
async def get_execution_logs(
    execution_id: UUID,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[TaskLog]:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
            namespace=execution.namespace,
        )
        flow = await repository.get_flow(
            execution.namespace,
            execution.flow_id,
            tenant_id=tenant_id,
            revision=execution.flow_revision,
        )
        task_runs = await repository.list_task_runs(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [
        TaskLog(
            taskId=task_run.task_id,
            attempt=task_run.current_attempt,
            state=task_run.state.value,
            output=(
                dict(
                    redact_matching_values(
                        task_run.result,
                        sensitive_execution_values(flow, execution.inputs, execution.outputs),
                    )
                )
                if task_run.result is not None
                else None
            ),
        )
        for task_run in task_runs
    ]


@app.get(
    "/api/v1/executions/{execution_id}/logs/stream",
    response_class=StreamingResponse,
    responses={
        status.HTTP_200_OK: {
            "content": {"application/x-ndjson": {}},
            "description": "Task logs streamed as newline-delimited JSON",
        }
    },
    tags=["executions"],
)
async def stream_execution_logs(
    execution_id: UUID,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> StreamingResponse:
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
            namespace=execution.namespace,
        )
        flow = await repository.get_flow(
            execution.namespace,
            execution.flow_id,
            tenant_id=tenant_id,
            revision=execution.flow_revision,
        )
        task_runs = await repository.list_task_runs(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    async def lines() -> AsyncIterator[str]:
        for task_run in task_runs:
            yield (
                TaskLog(
                    taskId=task_run.task_id,
                    attempt=task_run.current_attempt,
                    state=task_run.state.value,
                    output=(
                        dict(
                            redact_matching_values(
                                task_run.result,
                                sensitive_execution_values(
                                    flow,
                                    execution.inputs,
                                    execution.outputs,
                                ),
                            )
                        )
                        if task_run.result is not None
                        else None
                    ),
                ).model_dump_json(by_alias=True)
                + "\n"
            )

    return StreamingResponse(lines(), media_type="application/x-ndjson")


@app.post(
    "/api/v1/webhooks/{namespace}/{flow_id}/{trigger_id}",
    response_model=ExecutionDetail,
    responses={
        status.HTTP_202_ACCEPTED: {
            "model": ExecutionDetail,
            "description": "Webhook execution persisted and accepted for asynchronous processing",
        }
    },
    tags=["triggers"],
)
async def trigger_webhook(
    namespace: str,
    flow_id: str,
    trigger_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    response: Response,
    repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    trigger_runtime: TriggerRuntimeRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    runner: RunnerMode = RunnerMode.LOCAL,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    source_event_id: Annotated[str | None, Header(alias="X-Event-Id")] = None,
) -> ExecutionDetail:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await repository.get_flow(namespace, flow_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    trigger = next(
        (
            item
            for item in flow.triggers
            if item.id == trigger_id and item.type == "core.webhook" and not item.disabled
        ),
        None,
    )
    if trigger is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"enabled webhook trigger {trigger_id!r} does not exist",
        )
    trigger_decision = await operational_controls.evaluate(
        OperationalBoundary.TRIGGERS,
        tenant_id=tenant_id,
        namespace=namespace,
        flow_id=flow_id,
        component_id="webserver:webhook",
        component_role=ServiceRole.WEBSERVER.value,
    )
    if trigger_decision.blocked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "message": "triggers blocked by operational control",
                "boundary": OperationalBoundary.TRIGGERS.value,
                "controlIds": [str(control.control_id) for control in trigger_decision.controls],
            },
        )
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="webhook body must be an object",
        )
    try:
        payload = validate_flow_inputs(flow, payload)
        payload = await stage_file_inputs(
            flow,
            payload,
            build_object_store(settings),
            tenant_id=tenant_id,
        )
        payload = validate_flow_inputs(flow, payload)
    except DataContractError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    source_key = idempotency_key or source_event_id
    if source_key is None:
        encoded_payload = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        source_key = f"sha256:{hashlib.sha256(encoded_payload).hexdigest()}"
    occurrence_key = f"webhook:{flow.namespace}:{flow.id}:{flow.revision}:{trigger.id}:{source_key}"
    public_payload = redact_sensitive_inputs(flow, payload)
    try:
        acceptance = await trigger_runtime.accept_occurrence(
            tenant_id=tenant_id,
            namespace=flow.namespace,
            flow_id=flow.id,
            flow_revision=flow.revision,
            trigger_id=trigger.id,
            occurrence_key=occurrence_key,
            payload=public_payload,
            recoverable_payload=payload if public_payload != payload else None,
            metadata={"source": "webhook", "observedAt": datetime.now(UTC).isoformat()},
            max_pending=trigger.max_pending,
            max_attempts=trigger.max_attempts,
            retry_delay=trigger.retry_delay,
        )
    except RuntimeError as exc:
        if str(exc) != "trigger payload encryption is unavailable":
            raise
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="trigger payload protection is unavailable",
        ) from exc
    if acceptance.duplicate and acceptance.occurrence.execution_id is not None:
        existing = await repository.get_execution(
            acceptance.occurrence.execution_id,
            tenant_id=tenant_id,
        )
        return _public_execution_detail(
            flow,
            existing,
            await repository.list_task_runs(
                existing.execution_id,
                tenant_id=tenant_id,
            ),
        )
    if acceptance.occurrence.state is not TriggerOccurrenceState.ACCEPTED:
        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
                if acceptance.occurrence.state
                in {TriggerOccurrenceState.DEFERRED, TriggerOccurrenceState.RETRY_WAIT}
                else status.HTTP_409_CONFLICT
            ),
            detail=acceptance.reason,
            headers={"Retry-After": str(max(int(trigger.retry_delay.total_seconds()), 1))},
        )
    occurrence_owner = new_runtime_id()
    try:
        claimed_occurrence = await trigger_runtime.claim_occurrence(
            acceptance.occurrence.occurrence_id,
            tenant_id=tenant_id,
            owner_id=occurrence_owner,
            lease_duration=timedelta(seconds=30),
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    try:
        execution_payload = await trigger_runtime.get_recoverable_payload(
            claimed_occurrence.occurrence_id,
            tenant_id=tenant_id,
        )
    except Exception as exc:
        await trigger_runtime.fail_occurrence(
            claimed_occurrence.occurrence_id,
            tenant_id=tenant_id,
            owner_id=occurrence_owner,
            fencing_token=claimed_occurrence.fencing_token,
            error="protected trigger payload is unavailable",
            retry_delay=trigger.retry_delay,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="trigger payload is unavailable for execution",
        ) from exc
    execution_request = CreateExecutionRequest(
        namespace=namespace,
        flowId=flow_id,
        inputs=execution_payload,
        runner=runner,
    )
    respond_async = _prefers_async_response(prefer)
    try:
        detail = await _execute_flow(
            repository,
            task_cache,
            flow,
            execution_request,
            settings,
            operational_controls=operational_controls,
            shared_resources=shared_resources,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            actor=actor,
            authorization_service=authorization_service,
            background_tasks=background_tasks,
            launch_source=ExecutionLaunchSource.EVENT,
            idempotency_key=(
                f"trigger:{claimed_occurrence.trigger_definition_id}:"
                f"{claimed_occurrence.occurrence_key}"
            ),
            respond_async=respond_async,
            trigger_context={
                "id": trigger.id,
                "type": trigger.type,
                "body": execution_payload,
                "occurrenceId": str(claimed_occurrence.occurrence_id),
                "occurrenceKey": claimed_occurrence.occurrence_key,
            },
        )
    except Exception as exc:
        await trigger_runtime.fail_occurrence(
            claimed_occurrence.occurrence_id,
            tenant_id=tenant_id,
            owner_id=occurrence_owner,
            fencing_token=claimed_occurrence.fencing_token,
            error=str(exc),
            retry_delay=trigger.retry_delay,
        )
        raise
    await trigger_runtime.complete_occurrence(
        claimed_occurrence.occurrence_id,
        tenant_id=tenant_id,
        owner_id=occurrence_owner,
        fencing_token=claimed_occurrence.fencing_token,
        execution_id=detail.execution.execution_id,
        evidence={
            "decision": "launched",
            "reason": "webhook occurrence created an execution",
        },
    )
    if respond_async and detail.execution.state is ExecutionState.RUNNING:
        response.status_code = status.HTTP_202_ACCEPTED
        response.headers["Preference-Applied"] = "respond-async"
        response.headers["Location"] = f"/api/v1/executions/{detail.execution.execution_id}"
    return detail


def _prefers_async_response(prefer: str | None) -> bool:
    if prefer is None:
        return False
    return any(item.strip().lower() == "respond-async" for item in prefer.split(","))


def _agent_session_flow_id(namespace: str, agent: str, revision: int) -> str:
    """Use one bounded generated flow definition per immutable agent revision."""

    digest = hashlib.sha256(f"{namespace}:{agent}:{revision}".encode()).hexdigest()[:32]
    return f"agent_session_{digest}"


def _agent_session_service_session_id(
    tenant_id: str,
    namespace: str,
    actor_id: str,
    public_idempotency_key: str | None,
) -> UUID:
    if public_idempotency_key is None:
        return new_runtime_id()
    return uuid5(
        NAMESPACE_URL,
        f"amesh:agent-session:{tenant_id}:{namespace}:{actor_id}:{public_idempotency_key}",
    )


def _agent_session_execution_idempotency_key(
    service_session_id: UUID,
    public_idempotency_key: str | None,
) -> str | None:
    """Keep execution uniqueness scoped to the public tenant/namespace session identity."""

    if public_idempotency_key is None:
        return None
    return f"agent-session:{service_session_id}"


async def _authorize_agent_session_access(
    execution: PersistedExecution,
    *,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> None:
    """Authorize owner reads by namespace and require MANAGE for other owners."""

    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=execution.namespace,
    )
    owner_id = execution.trigger.get("ameshActorId")
    if owner_id != str(actor.principal_id):
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.MANAGE,
            tenant_id=tenant_id,
            namespace=execution.namespace,
        )


def _agent_session_admission_limits(
    envelope: EffectiveCapabilityEnvelope,
) -> tuple[list[ConcurrencyLimit], tuple[str, ...]]:
    """Bind profile, actor, and provider buckets to the envelope hard ceiling."""

    hard_limit = envelope.hard_limits.max_concurrency
    provider_ids = tuple(
        sorted(
            {
                f"{route.provider.adapter}:{route.provider.revision or 'default'}"
                for route in envelope.model_routes
            }
        )
    )
    limits = [
        ConcurrencyLimit(
            id="agent-session-profile",
            scope=AdmissionScope.FLOW,
            limit=hard_limit,
            behavior=AdmissionBehavior.QUEUE,
        ),
        ConcurrencyLimit(
            id="agent-session-user",
            scope=AdmissionScope.KEY,
            key="{{ trigger.ameshActorId }}",
            limit=hard_limit,
            behavior=AdmissionBehavior.QUEUE,
        ),
    ]
    if provider_ids:
        limits.append(
            ConcurrencyLimit(
                id="agent-session-provider",
                scope=AdmissionScope.KEY,
                key="{{ trigger.ameshProviderId }}",
                limit=hard_limit,
                behavior=AdmissionBehavior.QUEUE,
            )
        )
    return limits, provider_ids


_AGENT_SESSION_EVENT_PAYLOAD_LIMIT = 64 * 1024
_PRIVATE_AGENT_PAYLOAD_KEYS = frozenset(
    {
        "chainofthought",
        "checkpoint",
        "continuation",
        "continuationfrominvocationid",
        "hiddenreasoning",
        "messages",
        "modelcontinuation",
        "modelrationale",
        "privatereasoning",
        "prompt",
        "reasoning",
        "scratchpad",
        "thoughts",
    }
)


async def get_service_agent_session_detail(
    service_session_id: UUID,
    *,
    sessions: AgentSessionRepositoryDependency,
    tenant_id: str,
) -> AgentSessionDetail:
    execution_id = await sessions.get_execution_by_service_session_id(
        tenant_id,
        service_session_id,
    )
    records = await sessions.list_execution_sessions(tenant_id, execution_id)
    if not records:
        raise LookupError("agent session is not started")
    record = max(records, key=lambda item: (item.attempt, item.updated_at, item.session_id))
    return await sessions.get_session(tenant_id, record.task_run_id, record.attempt)


async def _get_service_agent_session_execution(
    service_session_id: UUID,
    *,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    tenant_id: str,
) -> PersistedExecution:
    try:
        execution_id = await sessions.get_execution_by_service_session_id(
            tenant_id,
            service_session_id,
        )
        return await repository.get_execution(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="agent session does not exist",
        ) from exc


async def get_service_agent_session_response(
    service_session_id: UUID,
    *,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: str,
    after_event_index: int,
    limit: int,
) -> AgentSessionServiceDetailResponse:
    """Return a durable service projection even before an attempt row exists."""

    execution = await _get_service_agent_session_execution(
        service_session_id,
        repository=repository,
        sessions=sessions,
        tenant_id=tenant_id,
    )
    execution_id = execution.execution_id
    await _authorize_agent_session_access(
        execution,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
    )
    records = await sessions.list_execution_sessions(tenant_id, execution_id)
    agent_ref = execution.trigger.get("ameshAgentRef")
    if not isinstance(agent_ref, str):
        agent_ref = None
    if not records:
        summary = _queued_agent_session_summary(service_session_id, execution, agent_ref=agent_ref)
        return AgentSessionServiceDetailResponse(session=summary, events=(), nextEventIndex=None)
    record = max(records, key=lambda item: (item.attempt, item.updated_at, item.session_id))
    detail = await sessions.get_session(tenant_id, record.task_run_id, record.attempt)
    page = _public_agent_session_detail(detail, after_event_index=after_event_index, limit=limit)
    summary = _control_agent_session_summary(
        service_session_id,
        execution,
        page.session,
        agent_ref=agent_ref,
    )
    return AgentSessionServiceDetailResponse(
        session=summary,
        events=page.events,
        nextEventIndex=page.next_event_index,
    )


async def get_agent_session_detail(
    service_session_id: UUID,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: str,
    *,
    after_event_index: int,
    limit: int,
) -> AgentSessionDetailResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    detail = await get_service_agent_session_detail(
        service_session_id,
        sessions=sessions,
        tenant_id=tenant_id,
    )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=detail.session.namespace,
    )
    return _public_agent_session_detail(
        detail,
        after_event_index=after_event_index,
        limit=limit,
    )


def _public_agent_session_detail(
    detail: AgentSessionDetail,
    *,
    after_event_index: int,
    limit: int,
) -> AgentSessionDetailResponse:
    ordered_events = tuple(
        event for event in detail.events if event.event_index > after_event_index
    )
    page = ordered_events[:limit]
    next_event_index = page[-1].event_index if len(ordered_events) > limit else None
    public_events = tuple(
        event.model_copy(update={"payload": _public_agent_event_payload(event.payload)})
        for event in page
    )
    final_result = next(
        (
            _public_agent_event_payload(event.payload["result"])
            for event in reversed(detail.events)
            if event.event_type == "output.accepted"
            and isinstance(event.payload.get("result"), dict)
        ),
        None,
    )
    return AgentSessionDetailResponse(
        session=AgentSessionSummary(
            sessionId=detail.session.session_id,
            tenantId=detail.session.tenant_id,
            namespace=detail.session.namespace,
            executionId=detail.session.execution_id,
            taskRunId=detail.session.task_run_id,
            attempt=detail.session.attempt,
            capabilityPinId=detail.session.capability_pin_id,
            envelopeDigest=detail.session.envelope_digest,
            state=detail.session.state,
            phase=detail.session.phase,
            version=detail.session.version,
            counters=detail.session.counters,
            harness=detail.session.harness,
            contextReceipt=detail.session.checkpoint.last_context_receipt,
            finalResult=(final_result if isinstance(final_result, dict) else None),
            error=detail.session.error,
            createdAt=detail.session.created_at,
            updatedAt=detail.session.updated_at,
            completedAt=detail.session.completed_at,
        ),
        events=public_events,
        nextEventIndex=next_event_index,
    )


def _service_session_state(
    execution_state: ExecutionState,
    session_state: AgentSessionState | None = None,
) -> Literal[
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
]:
    """Project execution lifecycle first so cancelled/restarting runs cannot look active."""

    if execution_state is ExecutionState.SUCCESS:
        return "SUCCEEDED"
    if execution_state is ExecutionState.FAILED:
        return "FAILED"
    if execution_state is ExecutionState.RUNNING and session_state is not None:
        if session_state is AgentSessionState.SUCCEEDED:
            return "SUCCEEDED"
        if session_state is AgentSessionState.FAILED:
            return "FAILED"
        return "RUNNING"
    if execution_state is ExecutionState.CREATED:
        return "CREATED"
    if execution_state is ExecutionState.QUEUED:
        return "QUEUED"
    if execution_state is ExecutionState.PAUSED:
        return "PAUSED"
    if execution_state is ExecutionState.CANCELLING:
        return "CANCELLING"
    if execution_state is ExecutionState.CANCELLED:
        return "CANCELLED"
    if execution_state is ExecutionState.WARNING:
        return "WARNING"
    return "RESTARTING"


def _control_agent_session_summary(
    service_session_id: UUID,
    execution: PersistedExecution,
    summary: AgentSessionSummary,
    *,
    agent_ref: str | None,
) -> AgentSessionControlSummary:
    return AgentSessionControlSummary(
        sessionId=service_session_id,
        tenantId=summary.tenant_id,
        namespace=summary.namespace,
        executionId=summary.execution_id,
        taskRunId=summary.task_run_id,
        attempt=summary.attempt,
        capabilityPinId=summary.capability_pin_id,
        envelopeDigest=summary.envelope_digest,
        agentRef=agent_ref or summary.agent_ref,
        modelProfile=summary.model_profile,
        harness=summary.harness,
        version=execution.version,
        executionEpoch=execution.epoch,
        state=_service_session_state(execution.state, summary.state),
        phase=summary.phase.value,
        createdAt=summary.created_at,
        updatedAt=max(summary.updated_at, execution.updated_at),
        completedAt=summary.completed_at,
        counters=summary.counters,
        budgets=(
            execution.trigger.get("ameshBudget")
            if isinstance(execution.trigger.get("ameshBudget"), dict)
            else None
        ),
        finalResult=summary.final_result,
        result=summary.final_result,
        error=summary.error,
    )


def _queued_agent_session_summary(
    service_session_id: UUID,
    execution: PersistedExecution,
    *,
    agent_ref: str | None,
) -> AgentSessionControlSummary:
    harness = execution.trigger.get("ameshHarness")
    return AgentSessionControlSummary(
        sessionId=service_session_id,
        tenantId=execution.tenant_id,
        namespace=execution.namespace,
        executionId=execution.execution_id,
        agentRef=agent_ref,
        harness=(AgentHarnessPin.model_validate(harness) if isinstance(harness, dict) else None),
        budgets=(
            execution.trigger.get("ameshBudget")
            if isinstance(execution.trigger.get("ameshBudget"), dict)
            else None
        ),
        version=execution.version,
        state=_service_session_state(execution.state),
        createdAt=execution.created_at,
        updatedAt=execution.updated_at,
        executionEpoch=execution.epoch,
        error=None,
    )


def _public_agent_event_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized_value = _drop_private_agent_payload(redact_realtime_payload(payload))
    if not isinstance(sanitized_value, dict):
        raise TypeError("agent session event payload must remain an object")
    sanitized: dict[str, Any] = sanitized_value
    encoded = json.dumps(sanitized, separators=(",", ":"), sort_keys=True, default=str).encode(
        "utf-8"
    )
    if len(encoded) <= _AGENT_SESSION_EVENT_PAYLOAD_LIMIT:
        return sanitized
    return {
        "payloadDigest": "sha256:" + hashlib.sha256(encoded).hexdigest(),
        "payloadBytes": len(encoded),
        "truncated": True,
    }


def _durable_usage(events: tuple[Any, ...]) -> dict[str, int] | None:
    """Aggregate normalized provider usage from durable model-response events only."""

    totals = {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0}
    found = False
    for event in events:
        normalized = event.payload.get("usageNormalized")
        if not isinstance(normalized, dict):
            continue
        values = {key: normalized.get(key, 0) for key in totals}
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in values.values()
        ):
            continue
        found = True
        for key, value in values.items():
            totals[key] += value
    return totals if found else None


def _drop_private_agent_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _drop_private_agent_payload(item)
            for key, item in value.items()
            if str(key).casefold().replace("-", "").replace("_", "")
            not in _PRIVATE_AGENT_PAYLOAD_KEYS
        }
    if isinstance(value, list):
        return [_drop_private_agent_payload(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_drop_private_agent_payload(item) for item in value)
    return value


def _public_execution(flow: FlowDefinition, execution: PersistedExecution) -> PersistedExecution:
    sensitive_values = sensitive_execution_values(flow, execution.inputs, execution.outputs)
    public_trigger = dict(execution.trigger)
    trigger_body = public_trigger.get("body")
    if isinstance(trigger_body, Mapping):
        public_trigger["body"] = redact_sensitive_inputs(flow, trigger_body)
    return execution.model_copy(
        update={
            "inputs": redact_sensitive_inputs(flow, execution.inputs),
            "outputs": redact_sensitive_outputs(flow, execution.outputs),
            "trigger": dict(redact_matching_values(public_trigger, sensitive_values)),
            "lifecycle_evidence": dict(
                redact_matching_values(execution.lifecycle_evidence, sensitive_values)
            ),
        }
    )


def _public_execution_detail(
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_runs: list[PersistedTaskRun],
    *,
    task_run_summary: PersistedTaskRunSummary | None = None,
    task_run_offset: int = 0,
) -> ExecutionDetail:
    sensitive_values = sensitive_execution_values(flow, execution.inputs, execution.outputs)
    public_runs = [
        task_run.model_copy(
            update={
                "result": (
                    dict(redact_matching_values(task_run.result, sensitive_values))
                    if task_run.result is not None
                    else None
                ),
                "evidence": dict(redact_matching_values(task_run.evidence, sensitive_values)),
            }
        )
        for task_run in task_runs
    ]
    return ExecutionDetail(
        execution=_public_execution(flow, execution),
        taskRuns=public_runs,
        taskRunSummary=task_run_summary,
        taskRunOffset=task_run_offset,
    )


def _public_evidence(
    flow: FlowDefinition,
    execution: PersistedExecution,
    events: list[ExecutionEvidenceEvent],
) -> list[ExecutionEvidenceEvent]:
    sensitive_values = sensitive_execution_values(flow, execution.inputs, execution.outputs)
    return [
        event.model_copy(
            update={"payload": dict(redact_matching_values(event.payload, sensitive_values))}
        )
        for event in events
    ]


async def _public_realtime_events(
    repository: PostgresExecutionRepository,
    events: tuple[RealtimeEvent, ...],
    *,
    tenant_id: str,
) -> tuple[RealtimeEvent, ...]:
    sensitive_by_execution: dict[UUID, tuple[str, ...]] = {}
    public_events: list[RealtimeEvent] = []
    for event in events:
        sensitive_values: tuple[str, ...] = ()
        if event.execution_id is not None:
            if event.execution_id not in sensitive_by_execution:
                try:
                    execution = await repository.get_execution(
                        event.execution_id,
                        tenant_id=tenant_id,
                    )
                    flow = await repository.get_flow(
                        execution.namespace,
                        execution.flow_id,
                        tenant_id=tenant_id,
                        revision=execution.flow_revision,
                    )
                    sensitive_by_execution[event.execution_id] = tuple(
                        sensitive_execution_values(flow, execution.inputs, execution.outputs)
                    )
                except LookupError:
                    sensitive_by_execution[event.execution_id] = ()
            sensitive_values = sensitive_by_execution[event.execution_id]
        payload = redact_realtime_payload(event.payload, sensitive_values)
        public_events.append(
            event.model_copy(update={"payload": payload if isinstance(payload, dict) else {}})
        )
    return tuple(public_events)


def _sse_event(event_type: str, cursor: str, payload: dict[str, object]) -> str:
    safe_event_type = event_type.replace("\r", "").replace("\n", "")
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return f"id: {cursor}\nevent: {safe_event_type}\ndata: {data}\n\n"


def _simulation_signing_key(settings: Settings) -> bytes:
    source = settings.webhook_signing_key.get_secret_value().encode("utf-8")
    return hashlib.sha256(b"amesh-simulation-signing-v1\0" + source).digest()


def _simulation_plugin_policy(decision: PluginPolicyDecision) -> SimulationPolicyDecision:
    return SimulationPolicyDecision(
        category="PLUGIN",
        policyId=str(decision.decision_id),
        allowed=decision.allowed,
        reason=(
            "resolved plugin set is allowed by execution policy"
            if decision.allowed
            else "resolved plugin set is denied by execution policy"
        ),
        details={
            "stage": decision.stage.value,
            "subjects": [item.model_dump(mode="json", by_alias=True) for item in decision.subjects],
        },
    )


async def _preview_simulation_admission_policy(
    service: AdmissionPolicyService,
    flow: FlowDefinition,
    request: SimulationRequest,
    actor: ActorContext,
    tenant_id: str,
) -> PolicyDecision:
    runtime_actor = ActorContext(
        principal_id=actor.principal_id,
        principal_type=PrincipalType.SYSTEM,
        display=str(actor.principal_id),
    )
    return await service.evaluate(
        PolicyEvaluationRequest(
            stage=PolicyStage.LAUNCH,
            input=policy_input_from_flow(
                flow,
                tenant_id=tenant_id,
                actor=runtime_actor,
                inputs=dict(request.inputs),
            ),
        ),
        record=False,
    )


def _simulation_admission_policy_pins(
    decision: PolicyDecision,
) -> tuple[DeterminismPolicyPin, ...]:
    return tuple(
        DeterminismPolicyPin(
            category="ADMISSION",
            key=item.policy_key,
            revision=item.revision,
            digest=item.digest,
        )
        for item in decision.pinned_policies
    )


def _resolve_idempotency_key(body_value: str | None, header_value: str | None) -> str | None:
    if body_value is not None and header_value is not None and body_value != header_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header does not match idempotencyKey body field",
        )
    return header_value or body_value


async def _authorize_plugin_policy_change(
    scope: PluginPolicyScope,
    namespace: str | None,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> None:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
        tenant_id=None if scope is PluginPolicyScope.INSTANCE else tenant_id,
        namespace=namespace,
    )


async def _authorize_admission_policy_change(
    document: PolicyDocument,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> None:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="plugin",
        action=PermissionAction.MANAGE,
        tenant_id=None if document.scope is PolicyScope.INSTANCE else tenant_id,
        namespace=document.namespace,
    )


async def _execute_flow(
    repository: PostgresExecutionRepository,
    task_cache: PostgresTaskCacheRepository,
    flow: FlowDefinition,
    request: CreateExecutionRequest,
    settings: Settings,
    *,
    operational_controls: PostgresOperationalControlRepository,
    shared_resources: PostgresSharedResourceRepository,
    tenant_id: str,
    actor_id: str,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    background_tasks: BackgroundTasks,
    launch_source: ExecutionLaunchSource,
    idempotency_key: str | None = None,
    respond_async: bool = False,
    trigger_context: dict[str, object] | None = None,
    correlation_id: str | None = None,
) -> ExecutionDetail:
    if flow.disabled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"flow {flow.namespace}.{flow.id} is disabled",
        )
    planned_tasks = compile_execution_tasks(flow)
    resource_usage = {
        "secret": any(node.task.contract.secret_scopes for node in planned_tasks),
        "namespace_file": any(
            any(
                reference.startswith("nsfile:///")
                for reference in (
                    *node.task.contract.files.values(),
                    *node.task.input_files.values(),
                )
            )
            for node in planned_tasks
        ),
        "key_value": "kv("
        in json.dumps(flow.model_dump(mode="json", by_alias=True), separators=(",", ":")),
    }
    for resource_type, used in resource_usage.items():
        if used:
            await authorize_request(
                authorization_service,
                actor,
                resource_type=resource_type,
                action=PermissionAction.USE,
                tenant_id=tenant_id,
                namespace=flow.namespace,
            )
    object_store = build_object_store(settings)
    workspace_manager = WorkingDirectoryManager(object_store)
    context_provider = SharedResourceContextProvider(
        shared_resources,
        object_store=object_store,
    )
    try:
        validated_inputs = validate_flow_inputs(flow, request.inputs)
        validated_inputs = await stage_file_inputs(
            flow,
            validated_inputs,
            object_store,
            tenant_id=tenant_id,
        )
        validated_inputs = validate_flow_inputs(flow, validated_inputs)
    except DataContractError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    runner_policy = RunnerPolicySet(settings.runner_policies)
    fallback_runner = RunnerId(request.runner.value)
    available_runners = {RunnerId.KUBERNETES}
    if settings.is_local_process_runner_enabled:
        available_runners.add(RunnerId.LOCAL)
    if settings.docker_runner_enabled:
        available_runners.add(RunnerId.DOCKER)
    try:
        selected_runners = required_runner_ids(
            (node.task for node in planned_tasks),
            runner_policy,
            namespace=flow.namespace,
            fallback=fallback_runner,
            available=frozenset(available_runners),
        )
    except RunnerPolicyViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    decision = await operational_controls.evaluate(
        OperationalBoundary.NEW_EXECUTIONS,
        tenant_id=tenant_id,
        namespace=flow.namespace,
        flow_id=flow.id,
        plugin_ids=tuple(node.task.type for node in planned_tasks),
        runner_ids=tuple(runner.value for runner in selected_runners),
        component_id="webserver:execution-admission",
        component_role=ServiceRole.WEBSERVER.value,
    )
    if decision.blocked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "message": "new executions blocked by operational control",
                "boundary": OperationalBoundary.NEW_EXECUTIONS.value,
                "controlIds": [str(control.control_id) for control in decision.controls],
            },
        )
    runner_handlers: dict[RunnerId, TaskHandler] = {}
    docker_runner: DockerContainerRunner | None = None
    if RunnerId.LOCAL in selected_runners:
        runner_handlers[RunnerId.LOCAL] = local_process_handler(
            LocalProcessRunner(),
            workspace_manager,
            namespace=flow.namespace,
        )
    if RunnerId.DOCKER in selected_runners:
        docker_runner = DockerContainerRunner(
            endpoint=settings.docker_runner_endpoint,
            image_policy=settings.docker_image_policy,
            signature_command=settings.docker_signature_verification_command,
            vulnerability_command=settings.docker_vulnerability_verification_command,
        )
        runner_handlers[RunnerId.DOCKER] = docker_container_handler(
            docker_runner,
            workspace_manager,
            namespace=flow.namespace,
        )
    kubernetes_runner: ProfiledKubernetesJobRunner | None = None
    if RunnerId.KUBERNETES in selected_runners:
        kubernetes_runner = ProfiledKubernetesJobRunner(
            settings.effective_kubernetes_runner_profiles
        )
        runner_handlers[RunnerId.KUBERNETES] = kubernetes_job_handler(
            kubernetes_runner,
            workspace_manager,
            namespace=flow.namespace,
        )
    shell_handler = selecting_runner_handler(
        runner_handlers,
        runner_policy,
        namespace=flow.namespace,
        fallback=fallback_runner,
    )

    http_policy = HttpTaskPolicy(
        allowed_hosts=settings.network_egress_allowed_hosts,
        allowed_private_hosts=frozenset(settings.core_http_allowed_private_hosts),
        maximum_response_bytes=settings.core_http_max_response_bytes,
        maximum_pages=settings.core_http_max_pages,
        maximum_redirects=settings.core_http_max_redirects,
        http_proxy_url=(
            settings.network_http_proxy_url.get_secret_value()
            if settings.network_http_proxy_url is not None
            else None
        ),
        https_proxy_url=(
            settings.network_https_proxy_url.get_secret_value()
            if settings.network_https_proxy_url is not None
            else None
        ),
        no_proxy=settings.network_no_proxy,
        ca_file=settings.network_outbound_ca_file,
        client_certificate_file=settings.network_outbound_client_certificate_file,
        client_key_file=settings.network_outbound_client_key_file,
    )
    agent_repository = PostgresAgentPrimitiveRepository(database_engine())
    agent_resources = PostgresAgentResourceRepository(database_engine())
    agent_sessions = PostgresAgentSessionRepository(database_engine())
    agent_memory = PostgresAgentMemoryRepository(database_engine())
    model_handler = agent_llm_handler(
        http_policy=http_policy,
        repository=agent_repository,
        continuation_protector=configured_model_continuation_protector(
            primary_key_id=settings.model_continuation_key_id,
            primary_key=settings.model_continuation_encryption_key,
            previous_key_id=settings.model_continuation_previous_key_id,
            previous_key=settings.model_continuation_previous_encryption_key,
        ),
    )
    mcp_handler = agent_mcp_handler(
        repository=agent_repository,
        http_policy=http_policy,
    )
    handlers = {
        "core.shell": shell_handler,
        **{
            task_type: model_handler
            for task_type in (
                "agent.llm",
                "agent.chat",
                "agent.embedding",
                "agent.structured",
                "agent.toolCall",
            )
        },
        "agent.mcp": mcp_handler,
        **agent_mesh_handlers(agent_resources),
        "agent.session": agent_session_handler(
            resources=agent_resources,
            sessions=agent_sessions,
            model_handler=model_handler,
            mcp_handler=mcp_handler,
            harness=create_agent_session_harness(
                settings.agent_session_harness,
                settings.agent_session_pi_worker_command,
                max_frame_bytes=settings.agent_session_max_frame_bytes,
            ),
            memory=agent_memory,
        ),
        "core.approval": approval_task_handler(
            get_human_task_repository(),
            repository,
            token_pepper=settings.amesh_token_pepper.get_secret_value(),
        ),
        **core_utility_handlers(workspace_manager, http_policy=http_policy),
        **script_task_handlers(shell_handler, settings.script_task_policy),
    }
    if settings.trusted_plugin_approvals or settings.isolated_plugin_services:
        revisions = await repository.list_flow_revisions(
            flow.namespace,
            flow.id,
            tenant_id=tenant_id,
        )
        revision = next((item for item in revisions if item.revision == flow.revision), None)
        if revision is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"flow revision {flow.revision} plugin resolution is unavailable",
            )
        plugin_handlers: dict[str, TaskHandler] = {}
        if settings.trusted_plugin_approvals:
            trusted_runtime = get_trusted_plugin_runtime()
            await trusted_runtime.ensure_started()
            plugin_handlers.update(trusted_runtime.task_handlers(revision.plugin_resolution))
        if settings.isolated_plugin_services:
            isolated_runtime = get_isolated_plugin_runtime()
            await isolated_runtime.ensure_configured()
            for task_type, handler in isolated_runtime.task_handlers(
                revision.plugin_resolution
            ).items():
                if task_type in plugin_handlers:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"plugin task identity {task_type!r} has multiple runtime owners",
                    )
                plugin_handlers[task_type] = handler
        for task_type, handler in plugin_handlers.items():
            if task_type in handlers:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"plugin task identity {task_type!r} conflicts with a core task",
                )
            handlers[task_type] = handler

    async def authorize_subflow(child_flow: FlowDefinition) -> None:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="execution",
            action=PermissionAction.EXECUTE,
            tenant_id=tenant_id,
            namespace=child_flow.namespace,
        )
        if child_flow.system:
            await authorize_request(
                authorization_service,
                actor,
                resource_type="tenant",
                action=PermissionAction.MANAGE,
                tenant_id=tenant_id,
            )

    for task in flow.tasks:
        if task.type != "core.subflow":
            continue
        extra = task.model_extra or {}
        child_flow_id = extra.get("flowId")
        child_namespace = extra.get("namespace", flow.namespace)
        child_revision = extra.get("revision")
        if not isinstance(child_flow_id, str) or "{{" in child_flow_id:
            continue
        if not isinstance(child_namespace, str) or "{{" in child_namespace:
            continue
        try:
            child_flow = await repository.get_flow(
                child_namespace,
                child_flow_id,
                tenant_id=tenant_id,
                revision=child_revision if isinstance(child_revision, int) else None,
            )
        except LookupError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        await authorize_subflow(child_flow)

    async def enforce_dispatch_policy(
        dispatch_flow: FlowDefinition,
        dispatch_execution: PersistedExecution,
        task_run: PersistedTaskRun,
        task: TaskDefinition,
    ) -> PolicyDecision:
        return await repository.enforce_admission_policy(
            dispatch_flow,
            tenant_id=dispatch_execution.tenant_id,
            stage=PolicyStage.DISPATCH,
            actor_id=dispatch_execution.created_by,
            inputs=dict(dispatch_execution.inputs),
            task=task,
            execution_id=dispatch_execution.execution_id,
            task_run_id=task_run.task_run_id,
        )

    def executor_factory() -> InProcessExecutor:
        return InProcessExecutor(
            repository,
            handlers=handlers,
            recover_running_types=frozenset({"core.subflow", "agent.session"}),
            context_provider=context_provider,
            object_store=object_store,
            task_cache=task_cache,
            workspace_manager=workspace_manager,
            dispatch_policy_enforcer=(
                enforce_dispatch_policy if repository.has_admission_policy_enforcer else None
            ),
        )

    handlers["core.subflow"] = subflow_task_handler(
        repository,
        executor_factory,
        authorize_subflow,
    )
    executor = executor_factory()
    background_scheduled = False

    async def run_pending_subflows() -> None:
        try:
            await SubflowCoordinator(repository, executor_factory).run_pending(
                execution.execution_id,
                tenant_id=tenant_id,
            )
        finally:
            if docker_runner is not None:
                await asyncio.to_thread(docker_runner.close)
            if kubernetes_runner is not None:
                await kubernetes_runner.close()

    async def run_async_execution(execution_id: UUID) -> None:
        try:
            async with repository.execution_guard(tenant_id, execution_id) as acquired:
                if not acquired:
                    return
                await executor.run_to_completion(
                    flow,
                    execution_id,
                    tenant_id=tenant_id,
                )
            completed = await repository.get_execution(execution_id, tenant_id=tenant_id)
            if completed.state is ExecutionState.SUCCESS:
                await SubflowCoordinator(repository, executor_factory).run_pending(
                    execution_id,
                    tenant_id=tenant_id,
                )
        except Exception:
            LOGGER.exception(
                "asynchronous execution failed",
                extra={"execution_id": str(execution_id), "tenant_id": tenant_id},
            )
        finally:
            if docker_runner is not None:
                await asyncio.to_thread(docker_runner.close)
            if kubernetes_runner is not None:
                await kubernetes_runner.close()

    try:
        try:
            execution_trigger = dict(trigger_context or {})
            if request.cache_mode.value != "USE":
                execution_trigger["_ameshCacheMode"] = request.cache_mode.value
            launch_trigger = dict(trigger_context or {})
            if correlation_id is not None:
                launch_trigger.setdefault("correlationId", correlation_id)
            execution = await repository.create_execution(
                flow,
                tenant_id=tenant_id,
                inputs=validated_inputs,
                trigger={**execution_trigger, **launch_trigger} or None,
                launch_source=launch_source,
                idempotency_key=idempotency_key,
                actor_id=actor_id,
            )
        except (TenantQuotaExceeded, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        if execution.state is ExecutionState.RUNNING and respond_async:
            background_tasks.add_task(run_async_execution, execution.execution_id)
            background_scheduled = True
        elif execution.state is ExecutionState.RUNNING:
            async with repository.execution_guard(tenant_id, execution.execution_id) as acquired:
                if acquired:
                    await executor.run_to_completion(
                        flow,
                        execution.execution_id,
                        tenant_id=tenant_id,
                    )
        detail = _public_execution_detail(
            flow,
            await repository.get_execution(
                execution.execution_id,
                tenant_id=tenant_id,
            ),
            await repository.list_task_runs(
                execution.execution_id,
                tenant_id=tenant_id,
            ),
        )
        if detail.execution.state is ExecutionState.SUCCESS:
            background_tasks.add_task(run_pending_subflows)
            background_scheduled = True
        return detail
    finally:
        if docker_runner is not None and not background_scheduled:
            await asyncio.to_thread(docker_runner.close)
        if kubernetes_runner is not None and not background_scheduled:
            await kubernetes_runner.close()


def _build_flow_graph(
    flow: FlowDefinition,
    task_runs: list[PersistedTaskRun] | None = None,
    iteration_summaries: list[PersistedIterationSummary] | None = None,
) -> FlowGraph:
    plan = compile_execution_tasks(flow)
    plan_by_id = {node.task.id: node for node in plan}
    runs_by_id = {task_run.task_id: task_run for task_run in task_runs or []}

    def depth(task_id: str) -> int:
        value = 0
        parent_id = plan_by_id[task_id].parent_id
        while parent_id is not None:
            value += 1
            parent_id = plan_by_id[parent_id].parent_id
        return value

    summaries = {
        (summary.loop_id, summary.task_id): summary for summary in iteration_summaries or []
    }
    nodes: list[FlowGraphNode] = []
    edges: list[FlowGraphEdge] = []
    for node in plan:
        dynamic_children = (
            tuple(f"{node.task.id}--template--{child.id}" for child in node.task.tasks)
            if node.dynamic
            else node.children
        )
        nodes.append(
            FlowGraphNode(
                taskId=node.task.id,
                label=node.task.id,
                taskType=node.task.type,
                order=len(nodes),
                depth=depth(node.task.id),
                parentId=node.parent_id,
                branchId=node.branch_id,
                dependencies=node.dependencies,
                children=dynamic_children,
                mode=node.mode,
                failurePolicy=node.failure_policy.value,
                maxConcurrency=node.max_concurrency,
                state=(
                    runs_by_id[node.task.id].state.value if node.task.id in runs_by_id else None
                ),
                result=(runs_by_id[node.task.id].result if node.task.id in runs_by_id else None),
                iterationCount=(
                    int((runs_by_id[node.task.id].result or {}).get("iterationCount", 0))
                    if node.dynamic and node.task.id in runs_by_id
                    else None
                ),
                lifecyclePhase=node.lifecycle_phase.value,
                handlerOwnerId=node.handler_owner_id,
            )
        )
        if node.parent_id is not None:
            edges.append(FlowGraphEdge(source=node.parent_id, target=node.task.id, kind="contains"))
        elif node.handler_owner_id not in {None, "flow"}:
            edges.append(
                FlowGraphEdge(
                    source=str(node.handler_owner_id),
                    target=node.task.id,
                    kind="handles",
                )
            )
        edges.extend(
            FlowGraphEdge(source=dependency, target=node.task.id, kind="dependsOn")
            for dependency in node.dependencies
        )
        if not node.dynamic:
            continue
        for child in node.task.tasks:
            child_node_id = f"{node.task.id}--template--{child.id}"
            summary = summaries.get((node.task.id, child.id))
            nodes.append(
                FlowGraphNode(
                    taskId=child_node_id,
                    label=child.id,
                    taskType=child.type,
                    order=len(nodes),
                    depth=depth(node.task.id) + 1,
                    parentId=node.task.id,
                    branchId=node.branch_id,
                    dependencies=tuple(
                        f"{node.task.id}--template--{dependency}" for dependency in child.depends_on
                    ),
                    failurePolicy=node.failure_policy.value,
                    state=_iteration_summary_state(summary),
                    iterationCount=summary.iteration_count if summary is not None else 0,
                    lifecyclePhase=node.lifecycle_phase.value,
                    handlerOwnerId=node.handler_owner_id,
                )
            )
            edges.append(FlowGraphEdge(source=node.task.id, target=child_node_id, kind="contains"))
            edges.extend(
                FlowGraphEdge(
                    source=f"{node.task.id}--template--{dependency}",
                    target=child_node_id,
                    kind="dependsOn",
                )
                for dependency in child.depends_on
            )
    return FlowGraph(
        namespace=flow.namespace,
        flowId=flow.id,
        revision=flow.revision,
        nodes=tuple(nodes),
        edges=tuple(edges),
    )


def _iteration_summary_state(summary: PersistedIterationSummary | None) -> str | None:
    if summary is None or summary.iteration_count == 0:
        return None
    if summary.failed or summary.cancelled:
        return "FAILED"
    if summary.running:
        return "RUNNING"
    if summary.waiting:
        return "WAITING"
    return "SUCCESS"


async def _authorize_tenant_administration(
    service: AuthorizationService,
    actor: ActorContext,
) -> None:
    await authorize_request(
        service,
        actor,
        resource_type="tenant",
        action=PermissionAction.MANAGE,
    )


@app.post(
    "/api/v1/admin/tenants",
    response_model=TenantDefinition,
    status_code=status.HTTP_201_CREATED,
    tags=["tenants"],
)
async def create_tenant(
    request: CreateTenantRequest,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.create(
            slug=request.slug,
            display_name=request.display_name,
            policy=request.policy,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/admin/tenants",
    response_model=list[TenantDefinition],
    tags=["tenants"],
)
async def list_tenants(
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await _authorize_tenant_administration(authorization_service, actor)
    return collection_response(await tenants.list(), query)


@app.get(
    "/api/v1/admin/tenants/{tenant_slug}",
    response_model=TenantDefinition,
    tags=["tenants"],
)
async def get_tenant(
    tenant_slug: str,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.get(tenant_slug)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.put(
    "/api/v1/admin/tenants/{tenant_slug}/policy",
    response_model=TenantDefinition,
    tags=["tenants"],
)
async def update_tenant_policy(
    tenant_slug: str,
    policy: TenantPolicy,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.update_policy(
            tenant_slug,
            policy,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/admin/tenants/{tenant_slug}/suspend",
    response_model=TenantDefinition,
    tags=["tenants"],
)
async def suspend_tenant(
    tenant_slug: str,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.suspend(tenant_slug, actor_id=str(actor.principal_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete(
    "/api/v1/admin/tenants/{tenant_slug}",
    response_model=TenantDefinition,
    tags=["tenants"],
)
async def delete_tenant(
    tenant_slug: str,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.delete(tenant_slug, actor_id=str(actor.principal_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/admin/tenants/{tenant_slug}/restore",
    response_model=TenantDefinition,
    tags=["tenants"],
)
async def restore_tenant(
    tenant_slug: str,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.restore(tenant_slug, actor_id=str(actor.principal_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/admin/tenants/{tenant_slug}/exports",
    response_model=TenantExport,
    status_code=status.HTTP_201_CREATED,
    tags=["tenants"],
)
async def export_tenant(
    tenant_slug: str,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantExport:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.export(tenant_slug, actor_id=str(actor.principal_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/admin/principals",
    response_model=PrincipalDefinition,
    status_code=status.HTTP_201_CREATED,
    tags=["authorization"],
)
async def create_principal(
    principal: PrincipalDefinition,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> PrincipalDefinition:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="principal",
        action=PermissionAction.MANAGE,
    )
    try:
        return await repository.create_principal(
            principal,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/admin/principals",
    response_model=list[PrincipalDefinition],
    tags=["authorization"],
)
async def list_principals(
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="principal",
        action=PermissionAction.VIEW,
    )
    return collection_response(await repository.list_principals(), query)


@app.put(
    "/api/v1/admin/groups/{group_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["authorization"],
)
async def add_group_member(
    group_id: UUID,
    member_id: UUID,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="group",
        action=PermissionAction.MANAGE,
    )
    try:
        await repository.add_group_member(
            group_id,
            member_id,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete(
    "/api/v1/admin/groups/{group_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["authorization"],
)
async def remove_group_member(
    group_id: UUID,
    member_id: UUID,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="group",
        action=PermissionAction.MANAGE,
    )
    try:
        await repository.remove_group_member(
            group_id,
            member_id,
            actor_id=str(actor.principal_id),
        )
    except LastAdministratorError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put(
    "/api/v1/admin/roles/{role_name}",
    response_model=RoleDefinition,
    tags=["authorization"],
)
async def upsert_role(
    role_name: str,
    role: RoleDefinition,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> RoleDefinition:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="role",
        action=PermissionAction.MANAGE,
    )
    if role.name != role_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="role path and body names must match",
        )
    try:
        return await repository.upsert_role(role, actor_id=str(actor.principal_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/admin/roles",
    response_model=list[RoleDefinition],
    tags=["authorization"],
)
async def list_roles(
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="role",
        action=PermissionAction.VIEW,
    )
    return collection_response(await repository.list_roles(), query)


@app.post(
    "/api/v1/admin/bindings",
    response_model=RoleBinding,
    status_code=status.HTTP_201_CREATED,
    tags=["authorization"],
)
async def create_role_binding(
    binding: RoleBinding,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> RoleBinding:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.MANAGE,
        tenant_id=binding.tenant_id,
        namespace=binding.namespace,
    )
    try:
        return await repository.create_binding(binding, actor_id=str(actor.principal_id))
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/admin/bindings",
    response_model=list[RoleBinding],
    tags=["authorization"],
)
async def list_role_bindings(
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.VIEW,
    )
    return collection_response(await repository.list_bindings(), query)


@app.delete(
    "/api/v1/admin/bindings/{binding_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["authorization"],
)
async def delete_role_binding(
    binding_id: UUID,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: Annotated[str | None, Header(alias="X-Amesh-Tenant")] = None,
    namespace: Annotated[str | None, Header(alias="X-Amesh-Namespace")] = None,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    binding = next(
        (item for item in await repository.list_bindings() if item.id == binding_id),
        None,
    )
    if binding is None or binding.tenant_id != tenant_id or binding.namespace != namespace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="binding not found")
    try:
        await repository.delete_binding(binding_id, actor_id=str(actor.principal_id))
    except LastAdministratorError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put(
    "/api/v1/admin/tenants/{tenant_id}/namespaces/{namespace}/authorization-boundary",
    response_model=NamespaceAuthorizationBoundary,
    tags=["authorization"],
)
async def set_namespace_authorization_boundary(
    tenant_id: str,
    namespace: str,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> NamespaceAuthorizationBoundary:
    boundary = NamespaceAuthorizationBoundary(tenant_id=tenant_id, namespace=namespace)
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.set_namespace_boundary(
            boundary,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def _issued_credential_response(issued: IssuedCredential) -> IssuedCredentialResponse:
    return IssuedCredentialResponse(
        metadata=issued.metadata,
        token=issued.token.get_secret_value(),
    )


@app.post(
    "/api/v1/admin/principals/{principal_id}/credentials",
    response_model=IssuedCredentialResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["credentials"],
)
async def issue_credential(
    principal_id: UUID,
    request: IssueCredentialRequest,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> IssuedCredentialResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.MANAGE,
    )
    try:
        issued = await credentials.issue(
            principal_id,
            name=request.name,
            scopes=request.scopes,
            audience=request.audience,
            expires_at=request.expires_at,
            rate_limit_per_minute=request.rate_limit_per_minute,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (CredentialOperationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _issued_credential_response(issued)


@app.get(
    "/api/v1/admin/principals/{principal_id}/credentials",
    response_model=list[CredentialMetadata],
    tags=["credentials"],
)
async def list_credentials(
    principal_id: UUID,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.VIEW,
    )
    return collection_response(await credentials.list(principal_id), query)


@app.post(
    "/api/v1/admin/credentials/{credential_id}/rotate",
    response_model=IssuedCredentialResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["credentials"],
)
async def rotate_credential(
    credential_id: UUID,
    request: RotateCredentialRequest,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> IssuedCredentialResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.MANAGE,
    )
    try:
        issued = await credentials.rotate(
            credential_id,
            overlap_seconds=request.overlap_seconds,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (CredentialOperationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _issued_credential_response(issued)


@app.delete(
    "/api/v1/admin/credentials/{credential_id}",
    response_model=RevokedCredentialsResponse,
    tags=["credentials"],
)
async def revoke_credential(
    credential_id: UUID,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> RevokedCredentialsResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.MANAGE,
    )
    try:
        revoked = await credentials.revoke(credential_id, actor_id=str(actor.principal_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RevokedCredentialsResponse(revokedCount=revoked)


@app.delete(
    "/api/v1/admin/principals/{principal_id}/credentials",
    response_model=RevokedCredentialsResponse,
    tags=["credentials"],
)
async def revoke_all_credentials(
    principal_id: UUID,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> RevokedCredentialsResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.MANAGE,
    )
    try:
        revoked = await credentials.revoke_all(
            principal_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RevokedCredentialsResponse(revokedCount=revoked)


@app.post(
    "/api/v1/credentials/exchange",
    response_model=IssuedCredentialResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["credentials"],
)
async def exchange_workload_credential(
    request: ExchangeCredentialRequest,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> IssuedCredentialResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.USE,
    )
    if actor.credential_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="workload exchange requires an API credential",
        )
    try:
        issued = await credentials.exchange(
            actor.credential_id,
            principal_id=actor.principal_id,
            scopes=request.scopes,
            audience=request.audience,
            expires_in_seconds=request.expires_in_seconds,
            rate_limit_per_minute=request.rate_limit_per_minute,
        )
    except (CredentialOperationError, LookupError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _issued_credential_response(issued)


@app.post(
    "/api/v1/authorization/explain",
    response_model=AuthorizationDecision,
    tags=["authorization"],
)
async def explain_authorization(
    request: AuthorizationExplanationRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> AuthorizationDecision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.MANAGE,
    )
    return await authorization_service.decide(
        AuthorizationRequest(
            actor=ActorContext(
                principal_id=request.principal_id,
                principal_type=request.principal_type,
                display="authorization-subject",
            ),
            tenant_id=request.tenant_id,
            namespace=request.namespace,
            resource_type=request.resource_type,
            action=request.action,
        )
    )


@app.post(
    "/api/v1/executions/reduce",
    response_model=ReduceExecutionResponse,
    tags=["executions"],
)
async def reduce_execution_events(
    request: ReduceExecutionRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    tenants: TenantServiceDependency,
) -> ReduceExecutionResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        await tenants.require_active(tenant_id)
    except TenantUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tenant unavailable",
        ) from None
    if request.snapshot.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="execution snapshot does not exist",
        )
    snapshot = request.snapshot
    duplicates = 0
    for event in request.events:
        before = snapshot
        try:
            snapshot = reduce_execution(snapshot, event)
        except InvalidTransition as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        if snapshot is before:
            duplicates += 1
    return ReduceExecutionResponse(
        snapshot=snapshot,
        duplicate_events_ignored=duplicates,
    )


@app.get(
    "/api/v1/audit-events",
    response_model=AuditEventPage,
    tags=["audit"],
)
async def list_audit_events(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    cursor: Annotated[int | None, Query(ge=1)] = None,
    limit: Annotated[int, Query(ge=1, le=1_000)] = 100,
    action: Annotated[str | None, Query(max_length=255)] = None,
    resource_type: Annotated[str | None, Query(alias="resourceType", max_length=128)] = None,
    outcome: Annotated[str | None, Query(max_length=64)] = None,
    occurred_from: Annotated[datetime | None, Query(alias="occurredFrom")] = None,
    occurred_to: Annotated[datetime | None, Query(alias="occurredTo")] = None,
) -> AuditEventPage:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_events(
        tenant_id,
        actor_id=str(actor.principal_id),
        cursor=cursor,
        limit=limit,
        action=action,
        resource_type=resource_type,
        outcome=outcome,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
    )


@app.get(
    "/api/v1/audit-events/integrity",
    response_model=AuditIntegrityReport,
    tags=["audit"],
)
async def verify_audit_integrity(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditIntegrityReport:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.verify_integrity(tenant_id, actor_id=str(actor.principal_id))


@app.get(
    "/api/v1/audit-policy",
    response_model=AuditRetentionPolicy,
    tags=["audit"],
)
async def get_audit_policy(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditRetentionPolicy:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.get_retention_policy(tenant_id)


@app.put(
    "/api/v1/audit-policy",
    response_model=AuditRetentionPolicy,
    tags=["audit"],
)
async def update_audit_policy(
    request: AuditRetentionPolicyUpdate,
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditRetentionPolicy:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await repository.set_retention_policy(
        tenant_id,
        AuditRetentionPolicy(retentionDays=request.retention_days),
        actor_id=str(actor.principal_id),
    )


@app.get(
    "/api/v1/audit-legal-holds",
    response_model=tuple[AuditLegalHold, ...],
    tags=["audit"],
)
async def list_audit_legal_holds(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> tuple[AuditLegalHold, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_legal_holds(tenant_id, actor_id=str(actor.principal_id))


@app.post(
    "/api/v1/audit-legal-holds",
    response_model=AuditLegalHold,
    status_code=status.HTTP_201_CREATED,
    tags=["audit"],
)
async def create_audit_legal_hold(
    request: AuditLegalHoldCreate,
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditLegalHold:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await repository.create_legal_hold(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@app.delete(
    "/api/v1/audit-legal-holds/{hold_id}",
    response_model=AuditLegalHold,
    tags=["audit"],
)
async def release_audit_legal_hold(
    hold_id: UUID,
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditLegalHold:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.release_legal_hold(
            tenant_id,
            hold_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post(
    "/api/v1/audit-retention/purge",
    response_model=AuditRetentionResult,
    tags=["audit"],
)
async def purge_audit_retention(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditRetentionResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await repository.purge_retained(tenant_id, actor_id=str(actor.principal_id))


@app.get(
    "/api/v1/audit-events/export",
    response_model=None,
    tags=["audit"],
)
async def download_audit_export(
    service: AuditArtifactServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    format: AuditExportFormat = AuditExportFormat.NDJSON,
    limit: Annotated[int, Query(ge=1, le=10_000)] = 10_000,
    action: Annotated[str | None, Query(max_length=255)] = None,
    resource_type: Annotated[str | None, Query(alias="resourceType", max_length=128)] = None,
    outcome: Annotated[str | None, Query(max_length=64)] = None,
    occurred_from: Annotated[datetime | None, Query(alias="occurredFrom")] = None,
    occurred_to: Annotated[datetime | None, Query(alias="occurredTo")] = None,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
    )
    artifact = await service.export_audit(
        tenant_id,
        actor_id=str(actor.principal_id),
        destination=AuditExportDestination.FILE,
        format=format,
        limit=limit,
        action=action,
        resource_type=resource_type,
        outcome=outcome,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
    )
    return _audit_artifact_response(artifact)


@app.post(
    "/api/v1/audit-exports",
    response_model=AuditExportReceipt,
    status_code=status.HTTP_201_CREATED,
    tags=["audit"],
)
async def create_object_audit_export(
    request: AuditExportRequest,
    service: AuditArtifactServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditExportReceipt:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
    )
    artifact = await service.export_audit(
        tenant_id,
        actor_id=str(actor.principal_id),
        destination=AuditExportDestination.OBJECT_STORAGE,
        format=request.format,
        limit=request.limit,
        action=request.action,
        resource_type=request.resource_type,
        outcome=request.outcome,
        occurred_from=request.occurred_from,
        occurred_to=request.occurred_to,
    )
    return artifact.receipt


@app.post(
    "/api/v1/compliance-evidence",
    response_model=ComplianceEvidenceRecord,
    status_code=status.HTTP_201_CREATED,
    tags=["audit"],
)
async def create_compliance_evidence(
    request: ComplianceEvidenceCreate,
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ComplianceEvidenceRecord:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="compliance",
        action=PermissionAction.CREATE,
        tenant_id=tenant_id,
    )
    return await repository.create_compliance_evidence(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@app.get(
    "/api/v1/compliance-evidence",
    response_model=tuple[ComplianceEvidenceRecord, ...],
    tags=["audit"],
)
async def list_compliance_evidence(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> tuple[ComplianceEvidenceRecord, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="compliance",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_compliance_evidence(
        tenant_id,
        actor_id=str(actor.principal_id),
    )


@app.get(
    "/api/v1/compliance-packages/export",
    response_model=None,
    tags=["audit"],
)
async def download_compliance_package(
    service: AuditArtifactServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    occurred_from: Annotated[datetime | None, Query(alias="occurredFrom")] = None,
    occurred_to: Annotated[datetime | None, Query(alias="occurredTo")] = None,
    max_audit_events: Annotated[int, Query(alias="maxAuditEvents", ge=1, le=10_000)] = 10_000,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="compliance",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
    )
    artifact = await service.export_compliance_package(
        tenant_id,
        actor_id=str(actor.principal_id),
        destination=AuditExportDestination.FILE,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
        max_audit_events=max_audit_events,
    )
    return _audit_artifact_response(artifact)


@app.post(
    "/api/v1/compliance-packages",
    response_model=AuditExportReceipt,
    status_code=status.HTTP_201_CREATED,
    tags=["audit"],
)
async def create_object_compliance_package(
    request: CompliancePackageRequest,
    service: AuditArtifactServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditExportReceipt:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="compliance",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
    )
    artifact = await service.export_compliance_package(
        tenant_id,
        actor_id=str(actor.principal_id),
        destination=AuditExportDestination.OBJECT_STORAGE,
        occurred_from=request.occurred_from,
        occurred_to=request.occurred_to,
        max_audit_events=request.max_audit_events,
    )
    return artifact.receipt


def _audit_artifact_response(artifact: AuditArtifact) -> Response:
    return Response(
        content=artifact.content,
        media_type=artifact.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{artifact.filename}"',
            "X-Checksum-Sha256": artifact.receipt.checksum_sha256,
            "X-Amesh-Signature": artifact.receipt.signature,
        },
    )


@app.post(
    "/api/v1/executions/{namespace}/{flow_id}",
    response_model=ExecutionDetail,
    responses={
        status.HTTP_202_ACCEPTED: {
            "model": ExecutionDetail,
            "description": "Execution persisted and accepted for asynchronous processing",
        }
    },
    tags=["compatibility"],
)
async def create_kestra_execution(
    namespace: str,
    flow_id: str,
    request: KestraExecutionRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-ID")] = None,
) -> ExecutionDetail:
    return await create_execution(
        CreateExecutionRequest(
            namespace=namespace,
            flowId=flow_id,
            inputs=request.inputs,
            runner=request.runner,
            idempotencyKey=request.idempotency_key,
        ),
        background_tasks,
        response,
        repository,
        task_cache,
        shared_resources,
        operational_controls,
        settings,
        actor,
        authorization_service,
        tenant_id,
        prefer,
        idempotency_key,
        correlation_id,
    )


_mcp_settings = get_settings()
_mcp_base_url = _mcp_settings.network_external_base_url or "http://localhost:8000"
_mcp_server = create_amesh_mcp_server(
    get_credential_service(),
    get_repository(),
    get_agent_resource_repository(),
    get_authorization_service(),
    base_url=_mcp_base_url,
)
_AMESH_MCP_APPLICATION = create_amesh_mcp_application(
    _mcp_server,
    base_url=_mcp_base_url,
)
app.router.routes.extend(_AMESH_MCP_APPLICATION.routes)

_FRONTEND_DIST = find_frontend_dist()
if _FRONTEND_DIST is not None:
    app.mount("/", SpaStaticFiles(directory=_FRONTEND_DIST, html=True), name="web")
