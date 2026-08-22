from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import secrets
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from http import HTTPStatus
from pathlib import Path
from time import perf_counter
from typing import Annotated
from uuid import UUID

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
from fastapi.exceptions import RequestValidationError
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse, StreamingResponse

from amesh import __version__
from amesh.adapters.kubernetes import KubernetesJobRunner
from amesh.adapters.local import LocalProcessRunner
from amesh.adapters.postgres import (
    PostgresAuthenticationRepository,
    PostgresAuthorizationRepository,
    PostgresBackfillRepository,
    PostgresCheckRepository,
    PostgresCredentialRepository,
    PostgresExecutionRepository,
    PostgresFeatureFlagRepository,
    PostgresMetadataRepository,
    PostgresReconciliationRepository,
    PostgresServiceRegistryRepository,
    PostgresSharedResourceRepository,
    PostgresTaskCacheRepository,
    PostgresTenantRepository,
    PostgresTriggerRuntimeRepository,
    PostgresWorkerRepository,
)
from amesh.api.contracts import (
    CollectionQuery,
    _decode_cursor,
    _encode_cursor,
    collection_response,
    default_limited_collection_query,
)
from amesh.api.models import (
    AuthorizationExplanationRequest,
    BackfillActionRequest,
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
    FeatureFlagUpsertRequest,
    FlowDataContract,
    FlowGraph,
    FlowGraphEdge,
    FlowGraphNode,
    FlowMetadataResponse,
    FlowRevisionLifecycleRequest,
    FlowRevisionRestoreRequest,
    HealthResponse,
    IssueCredentialRequest,
    IssuedCredentialResponse,
    LoginRequest,
    LoginResponse,
    NamespaceFileMoveRequest,
    NamespaceResourceImportResult,
    ProblemDetail,
    ReadinessResponse,
    ReduceExecutionRequest,
    ReduceExecutionResponse,
    ResumeTaskRequest,
    RevokedCredentialsResponse,
    RevokedSessionsResponse,
    RotateCredentialRequest,
    RunnerMode,
    SetLocalPasswordRequest,
    TaskCachePurgeRequest,
    TaskLog,
    TriggerActionRequest,
    UiSessionResponse,
)
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
from amesh.config import (
    ConfigurationLoadError,
    ConfigurationManager,
    ConfigurationSnapshot,
    NonReloadableConfigurationChanged,
    Settings,
    get_configuration_manager,
    get_settings,
)
from amesh.credentials import CredentialOperationError, CredentialService, InvalidCredential
from amesh.database import create_database_engine
from amesh.domain import (
    ActorContext,
    AdmissionDecision,
    AdmissionDiagnostics,
    AdmissionResourceType,
    AuthenticationProviderDescriptor,
    AuthorizationDecision,
    AuthorizationRequest,
    BackfillPreview,
    BackfillRecord,
    BackfillSpec,
    BackfillState,
    CredentialMetadata,
    ExecutionState,
    FeatureFlag,
    FeatureFlagDecision,
    FeatureFlagScope,
    FlowRevisionDiff,
    FlowRevisionRecord,
    FlowRevisionSource,
    InvalidTransition,
    IssuedCredential,
    KeyValueChange,
    KeyValueEntry,
    KeyValueWrite,
    NamespaceAuthorizationBoundary,
    NamespaceFile,
    NamespaceFileVersion,
    NamespaceResourceBundle,
    PermissionAction,
    PrincipalDefinition,
    PrincipalType,
    ReconciliationRequest,
    ReconciliationRun,
    ResourceVersionConflict,
    RoleBinding,
    RoleDefinition,
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
    new_runtime_id,
    reduce_execution,
)
from amesh.domain import (
    AuthenticationRequest as ProviderAuthenticationRequest,
)
from amesh.domain.runner import RunnerId, RunnerPolicySet, RunnerPolicyViolation
from amesh.dsl import (
    FlowDefinition,
    FlowDocumentError,
    FlowValidationResult,
    compile_execution_tasks,
    validate_flow_document,
)
from amesh.executor import (
    InProcessExecutor,
    SubflowCoordinator,
    TaskHandler,
    TaskResourceLimitError,
    kubernetes_job_handler,
    local_process_handler,
    normalize_task_completion,
    preview_execution_intervention,
    required_runner_ids,
    selecting_runner_handler,
    subflow_task_handler,
)
from amesh.frontend import SpaStaticFiles, find_frontend_dist
from amesh.migrations import migration_directory
from amesh.observability import (
    HTTP_REQUEST_DURATION,
    HTTP_REQUESTS,
    configure_structured_logging,
    database_readiness,
    instrument_database,
)
from amesh.ports import (
    CheckComplianceSummary,
    CheckEvaluation,
    CheckOutcome,
    CredentialRateLimitExceeded,
    ExecutionArtifact,
    ExecutionEvidenceEvent,
    ExecutionInterventionPreview,
    ExecutionInterventionRecord,
    ExecutionLaunchSource,
    ExecutionStateConflictError,
    FeatureFlagVersionConflict,
    LastAdministratorError,
    NamespaceCheckPolicy,
    PersistedExecution,
    PersistedFlow,
    PersistedIterationSummary,
    PersistedSubflow,
    PersistedTaskRun,
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
from amesh.reconciliation import ReconciliationService
from amesh.scheduler import CronScheduler, SchedulePreview
from amesh.storage.factory import build_object_store
from amesh.tasks import agent_llm_handler, agent_mcp_handler, core_http_handler
from amesh.tenancy import TenantService
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

app = FastAPI(
    title="AMESH",
    version=__version__,
    description=(
        "Clean-room durable workflow MVP with validated flow management, "
        "execution control, webhook triggers and execution logs."
    ),
)


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
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers,
        media_type="application/problem+json",
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, (str, list)) else str(exc.detail)
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
    return _problem_response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Request validation failed",
        code="REQUEST_VALIDATION_FAILED",
        errors=exc.errors(),
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
    response = await call_next(request)
    route = request.scope.get("route")
    route_path = getattr(route, "path", "unmatched")
    status_code = str(response.status_code)
    HTTP_REQUESTS.labels(request.method, route_path, status_code).inc()
    HTTP_REQUEST_DURATION.labels(request.method, route_path).inc(perf_counter() - started)
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
def get_repository() -> PostgresExecutionRepository:
    return PostgresExecutionRepository(database_engine())


RepositoryDependency = Annotated[
    PostgresExecutionRepository,
    Depends(get_repository),
]


@lru_cache
def get_task_cache_repository() -> PostgresTaskCacheRepository:
    return PostgresTaskCacheRepository(database_engine())


TaskCacheRepositoryDependency = Annotated[
    PostgresTaskCacheRepository,
    Depends(get_task_cache_repository),
]


@lru_cache
def get_trigger_runtime_repository() -> PostgresTriggerRuntimeRepository:
    return PostgresTriggerRuntimeRepository(database_engine())


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
def get_shared_resource_repository() -> PostgresSharedResourceRepository:
    return PostgresSharedResourceRepository(database_engine())


SharedResourceRepositoryDependency = Annotated[
    PostgresSharedResourceRepository,
    Depends(get_shared_resource_repository),
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
    return BackfillService(get_repository(), get_backfill_repository())


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
def get_authorization_service() -> AuthorizationService:
    return AuthorizationService(get_authorization_repository())


AuthorizationServiceDependency = Annotated[
    AuthorizationService,
    Depends(get_authorization_service),
]
AuthorizationRepositoryDependency = Annotated[
    PostgresAuthorizationRepository,
    Depends(get_authorization_repository),
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
def get_authentication_service() -> AuthenticationService:
    settings = get_settings()
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
    )


AuthenticationServiceDependency = Annotated[
    AuthenticationService,
    Depends(get_authentication_service),
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


ActorDependency = Annotated[ActorContext, Depends(authenticate_actor)]


async def require_tenant_context(
    settings: SettingsDependency,
    tenant_service: TenantServiceDependency,
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
    try:
        await tenant_service.consume_api_request(tenant_slug)
    except TenantQuotaExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="tenant API request quota exceeded",
            headers={"Retry-After": "60"},
        ) from exc
    return tenant_slug


TenantDependency = Annotated[str, Depends(require_tenant_context)]


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
        return await service.require(
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


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@app.get("/ready", response_model=ReadinessResponse, tags=["system"])
async def ready(
    response: Response,
    settings: SettingsDependency,
    service_registry: ServiceRegistryRepositoryDependency,
) -> ReadinessResponse:
    readiness = await database_readiness(database_engine(), migration_directory())
    if readiness.ready and settings.service_instance_name is not None:
        topology = await service_registry.topology()
        registered_ready = any(
            instance.role is ServiceRole.WEBSERVER
            and instance.instance_name == settings.service_instance_name
            and instance.liveness is ServiceLiveness.LIVE
            and instance.state is ServiceState.READY
            for instance in topology.instances
        )
        if not registered_ready:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return ReadinessResponse(
                status="not-ready",
                version=__version__,
                database="ready",
                migrations_applied=readiness.applied,
                migrations_expected=readiness.expected,
                latest_migration=readiness.latest_migration,
                error="service instance is not ready",
            )
    if not readiness.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(
        status="ready" if readiness.ready else "not-ready",
        version=__version__,
        database="ready" if readiness.ready else "unavailable",
        migrations_applied=readiness.applied,
        migrations_expected=readiness.expected,
        latest_migration=readiness.latest_migration,
        error=readiness.error,
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
        "flows.view": ("flow", PermissionAction.VIEW),
        "flows.create": ("flow", PermissionAction.CREATE),
        "executions.view": ("execution", PermissionAction.VIEW),
        "executions.execute": ("execution", PermissionAction.EXECUTE),
        "triggers.view": ("trigger", PermissionAction.VIEW),
        "triggers.manage": ("trigger", PermissionAction.MANAGE),
        "checks.view": ("check", PermissionAction.VIEW),
        "checks.manage": ("check", PermissionAction.MANAGE),
        "namespaces.view": ("namespace", PermissionAction.VIEW),
        "namespaceResources.read": ("namespace_file", PermissionAction.LIST),
        "namespaceResources.write": ("namespace_file", PermissionAction.WRITE),
        "secretBindings.write": ("secret", PermissionAction.WRITE),
        "plugins.view": ("plugin", PermissionAction.VIEW),
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
    configure_structured_logging(configuration.settings.log_level)
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
    return ConfigurationDiagnosticBundle(
        generatedAt=datetime.now(UTC),
        tenantId=tenant_id,
        namespace=namespace,
        configuration=configuration.snapshot(),
        featureFlags=await feature_flags.list_for_context(tenant_id, namespace=namespace),
    )


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
    "/api/v1/auth/providers",
    response_model=tuple[AuthenticationProviderDescriptor, ...],
    tags=["authentication"],
)
async def list_authentication_providers(
    authentication_service: AuthenticationServiceDependency,
) -> tuple[AuthenticationProviderDescriptor, ...]:
    return authentication_service.providers()


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
    source = "|".join(
        (
            request.client.host if request.client is not None else "unknown",
            request.headers.get("user-agent", "unknown")[:512],
        )
    )
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


@app.post(
    "/api/v1/flows/validate",
    response_model=FlowValidationResult,
    tags=["flows"],
)
async def validate_flow(request: Request) -> FlowValidationResult:
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="flow document exceeds the 2 MiB foundation limit",
        )
    try:
        return validate_flow_document(body)
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.put(
    "/api/v1/flows",
    response_model=PersistedFlow,
    tags=["flows"],
)
async def apply_flow(
    request: Request,
    response: Response,
    repository: RepositoryDependency,
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
        result = validate_flow_document(await request.body())
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
        action=PermissionAction.UPDATE,
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
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
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
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
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
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
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
        shared_resources=shared_resources,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        actor=actor,
        authorization_service=authorization_service,
        background_tasks=background_tasks,
        launch_source=ExecutionLaunchSource.API,
        idempotency_key=effective_idempotency_key,
        respond_async=respond_async,
    )
    if respond_async and detail.execution.state is ExecutionState.RUNNING:
        response.status_code = status.HTTP_202_ACCEPTED
        response.headers["Preference-Applied"] = "respond-async"
        response.headers["Location"] = f"/api/v1/executions/{detail.execution.execution_id}"
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
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
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
                shared_resources=shared_resources,
                tenant_id=tenant_id,
                actor_id=str(actor.principal_id),
                actor=actor,
                authorization_service=authorization_service,
                background_tasks=background_tasks,
                launch_source=ExecutionLaunchSource.API,
                idempotency_key=item.idempotency_key,
                respond_async=respond_async,
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
    return await repository.admission_diagnostics(tenant_id=tenant_id)


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
) -> list[RunnerCapabilities]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="worker",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return [
        LocalProcessRunner.CAPABILITIES,
        KubernetesJobRunner.CAPABILITIES,
    ]


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
) -> ExecutionDetail:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    task_runs = await repository.list_task_runs(
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
    return _public_execution_detail(flow, execution, task_runs)


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
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        await repository.get_execution(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
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
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        await repository.get_execution(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
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
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
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
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
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
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        execution = await repository.get_execution(execution_id, tenant_id=tenant_id)
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
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
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
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
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
    acceptance = await trigger_runtime.accept_occurrence(
        tenant_id=tenant_id,
        namespace=flow.namespace,
        flow_id=flow.id,
        flow_revision=flow.revision,
        trigger_id=trigger.id,
        occurrence_key=occurrence_key,
        payload=redact_sensitive_inputs(flow, payload),
        metadata={"source": "webhook", "observedAt": datetime.now(UTC).isoformat()},
        max_pending=trigger.max_pending,
        max_attempts=trigger.max_attempts,
        retry_delay=trigger.retry_delay,
    )
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
    execution_request = CreateExecutionRequest(
        namespace=namespace,
        flowId=flow_id,
        inputs=payload,
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
                "body": payload,
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


def _public_execution(flow: FlowDefinition, execution: PersistedExecution) -> PersistedExecution:
    sensitive_values = sensitive_execution_values(flow, execution.inputs, execution.outputs)
    return execution.model_copy(
        update={
            "inputs": redact_sensitive_inputs(flow, execution.inputs),
            "outputs": redact_sensitive_outputs(flow, execution.outputs),
            "trigger": dict(redact_matching_values(execution.trigger, sensitive_values)),
            "lifecycle_evidence": dict(
                redact_matching_values(execution.lifecycle_evidence, sensitive_values)
            ),
        }
    )


def _public_execution_detail(
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_runs: list[PersistedTaskRun],
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
    return ExecutionDetail(execution=_public_execution(flow, execution), taskRuns=public_runs)


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


def _resolve_idempotency_key(body_value: str | None, header_value: str | None) -> str | None:
    if body_value is not None and header_value is not None and body_value != header_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header does not match idempotencyKey body field",
        )
    return header_value or body_value


async def _execute_flow(
    repository: PostgresExecutionRepository,
    task_cache: PostgresTaskCacheRepository,
    flow: FlowDefinition,
    request: CreateExecutionRequest,
    settings: Settings,
    *,
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
    try:
        selected_runners = required_runner_ids(
            (node.task for node in planned_tasks),
            runner_policy,
            namespace=flow.namespace,
            fallback=fallback_runner,
        )
    except RunnerPolicyViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    runner_handlers: dict[RunnerId, TaskHandler] = {}
    if RunnerId.LOCAL in selected_runners:
        runner_handlers[RunnerId.LOCAL] = local_process_handler(
            LocalProcessRunner(),
            workspace_manager,
            namespace=flow.namespace,
        )
    kubernetes_runner: KubernetesJobRunner | None = None
    if RunnerId.KUBERNETES in selected_runners:
        if settings.kubernetes_context is None:
            kubernetes_runner = KubernetesJobRunner.from_in_cluster(
                namespace=settings.kubernetes_task_namespace
            )
        else:
            kubernetes_runner = await KubernetesJobRunner.from_kube_config(
                namespace=settings.kubernetes_task_namespace,
                context=settings.kubernetes_context,
            )
        runner_handlers[RunnerId.KUBERNETES] = kubernetes_job_handler(
            kubernetes_runner,
            namespace=flow.namespace,
        )
    shell_handler = selecting_runner_handler(
        runner_handlers,
        runner_policy,
        namespace=flow.namespace,
        fallback=fallback_runner,
    )

    handlers = {
        "core.shell": shell_handler,
        "core.http": core_http_handler(),
        "agent.llm": agent_llm_handler(),
        "agent.mcp": agent_mcp_handler(),
    }

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

    def executor_factory() -> InProcessExecutor:
        return InProcessExecutor(
            repository,
            handlers=handlers,
            recover_running_types=frozenset({"core.subflow"}),
            context_provider=context_provider,
            object_store=object_store,
            task_cache=task_cache,
            workspace_manager=workspace_manager,
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
            if kubernetes_runner is not None:
                await kubernetes_runner.close()

    async def run_async_execution(execution_id: UUID) -> None:
        try:
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
            if kubernetes_runner is not None:
                await kubernetes_runner.close()

    try:
        try:
            execution_trigger = dict(trigger_context or {})
            if request.cache_mode.value != "USE":
                execution_trigger["_ameshCacheMode"] = request.cache_mode.value
            execution = await repository.create_execution(
                flow,
                tenant_id=tenant_id,
                inputs=validated_inputs,
                trigger=execution_trigger or None,
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


_FRONTEND_DIST = find_frontend_dist()
if _FRONTEND_DIST is not None:
    app.mount("/", SpaStaticFiles(directory=_FRONTEND_DIST, html=True), name="web")
