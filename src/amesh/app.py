from __future__ import annotations

import asyncio
import logging
import secrets
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from functools import lru_cache
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
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from starlette.responses import JSONResponse

from amesh import __version__
from amesh.adapters.kubernetes import KubernetesJobRunner
from amesh.adapters.local import LocalProcessRunner
from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresBackfillRepository,
    PostgresCredentialRepository,
    PostgresExecutionRepository,
    PostgresTenantRepository,
    PostgresWorkerRepository,
)
from amesh.api.models import (
    AuthorizationExplanationRequest,
    BackfillActionRequest,
    CreateExecutionRequest,
    CreateTenantRequest,
    ExchangeCredentialRequest,
    ExecutionDetail,
    ExecutionInterventionPreviewRequest,
    ExecutionInterventionRequest,
    HealthResponse,
    IssueCredentialRequest,
    IssuedCredentialResponse,
    ReadinessResponse,
    ReduceExecutionRequest,
    ReduceExecutionResponse,
    ResumeTaskRequest,
    RevokedCredentialsResponse,
    RotateCredentialRequest,
    RunnerMode,
    TaskLog,
    UiSessionResponse,
)
from amesh.authorization import AuthorizationDenied, AuthorizationService
from amesh.backfills import BackfillService
from amesh.config import Settings, get_settings
from amesh.credentials import CredentialOperationError, CredentialService, InvalidCredential
from amesh.domain import (
    ActorContext,
    AdmissionDecision,
    AdmissionDiagnostics,
    AdmissionResourceType,
    AuthorizationDecision,
    AuthorizationRequest,
    BackfillPreview,
    BackfillRecord,
    BackfillSpec,
    BackfillState,
    CredentialMetadata,
    ExecutionState,
    InvalidTransition,
    IssuedCredential,
    NamespaceAuthorizationBoundary,
    PermissionAction,
    PrincipalDefinition,
    PrincipalType,
    ResourceVersionConflict,
    RoleBinding,
    RoleDefinition,
    TenantDefinition,
    TenantExport,
    TenantPolicy,
    TenantSlug,
    reduce_execution,
)
from amesh.dsl import (
    FlowDefinition,
    FlowDocumentError,
    FlowValidationResult,
    validate_flow_document,
)
from amesh.executor import (
    InProcessExecutor,
    SubflowCoordinator,
    TaskResourceLimitError,
    kubernetes_job_handler,
    local_process_handler,
    normalize_task_completion,
    preview_execution_intervention,
    subflow_task_handler,
)
from amesh.frontend import SpaStaticFiles, find_frontend_dist
from amesh.migrations import migration_directory
from amesh.observability import (
    HTTP_REQUEST_DURATION,
    HTTP_REQUESTS,
    database_readiness,
    instrument_database,
)
from amesh.ports import (
    CredentialRateLimitExceeded,
    ExecutionInterventionPreview,
    ExecutionInterventionRecord,
    ExecutionLaunchSource,
    ExecutionStateConflictError,
    LastAdministratorError,
    PersistedExecution,
    PersistedFlow,
    PersistedSubflow,
    PersistedTaskRun,
    TaskStateConflictError,
    TenantQuotaExceeded,
    TenantUnavailableError,
    WorkerFenceError,
    WorkerInventory,
)
from amesh.scheduler import CronScheduler, SchedulePreview
from amesh.tasks import agent_llm_handler, agent_mcp_handler, core_http_handler
from amesh.tenancy import TenantService

LOGGER = logging.getLogger("amesh.api")

app = FastAPI(
    title="AMESH",
    version=__version__,
    description=(
        "Clean-room durable workflow MVP with validated flow management, "
        "execution control, webhook triggers and execution logs."
    ),
)


@app.exception_handler(TenantUnavailableError)
async def tenant_unavailable_handler(
    request: Request,
    exc: TenantUnavailableError,
) -> JSONResponse:
    del request, exc
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "tenant unavailable"},
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
        create_async_engine(settings.database_url),
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
def get_tenant_repository() -> PostgresTenantRepository:
    return PostgresTenantRepository(database_engine())


@lru_cache
def get_tenant_service() -> TenantService:
    return TenantService(get_tenant_repository())


TenantServiceDependency = Annotated[TenantService, Depends(get_tenant_service)]


@lru_cache
def get_worker_repository() -> PostgresWorkerRepository:
    return PostgresWorkerRepository(database_engine())


WorkerRepositoryDependency = Annotated[
    PostgresWorkerRepository,
    Depends(get_worker_repository),
]
_TENANT_SLUG_ADAPTER = TypeAdapter(TenantSlug)


_BOOTSTRAP_PRINCIPAL_ID = UUID("00000000-0000-7000-8000-000000000001")


async def authenticate_actor(
    settings: SettingsDependency,
    credential_service: CredentialServiceDependency,
    authorization: Annotated[str | None, Header()] = None,
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
async def ready(response: Response) -> ReadinessResponse:
    readiness = await database_readiness(database_engine(), migration_directory())
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
        "namespaces.view": ("namespace", PermissionAction.VIEW),
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
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[PersistedFlow]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_flows(tenant_id=tenant_id)


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
    tags=["executions"],
)
async def create_execution(
    request: CreateExecutionRequest,
    background_tasks: BackgroundTasks,
    repository: RepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
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
    return await _execute_flow(
        repository,
        flow,
        request,
        settings,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        actor=actor,
        authorization_service=authorization_service,
        background_tasks=background_tasks,
        launch_source=ExecutionLaunchSource.API,
    )


@app.get(
    "/api/v1/executions",
    response_model=list[PersistedExecution],
    tags=["executions"],
)
async def list_executions(
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: int = 100,
) -> list[PersistedExecution]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="limit must be between 1 and 1000",
        )
    return await repository.list_executions(tenant_id=tenant_id, limit=limit)


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
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[BackfillRecord]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_backfills(tenant_id=tenant_id, limit=limit)


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
) -> list[WorkerInventory]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="worker",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await workers.list_worker_inventory(tenant_id=tenant_id)


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
    task_runs = await repository.list_task_runs(execution_id, tenant_id=tenant_id)
    return ExecutionDetail(execution=execution, taskRuns=task_runs)


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
        return ExecutionDetail(execution=updated, taskRuns=updated_tasks)
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
        await repository.get_execution(execution_id, tenant_id=tenant_id)
        task_runs = await repository.list_task_runs(execution_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [
        TaskLog(
            taskId=task_run.task_id,
            attempt=task_run.current_attempt,
            state=task_run.state.value,
            output=task_run.result,
        )
        for task_run in task_runs
    ]


@app.post(
    "/api/v1/webhooks/{namespace}/{flow_id}/{trigger_id}",
    response_model=ExecutionDetail,
    tags=["triggers"],
)
async def trigger_webhook(
    namespace: str,
    flow_id: str,
    trigger_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    repository: RepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    runner: RunnerMode = RunnerMode.LOCAL,
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
    execution_request = CreateExecutionRequest(
        namespace=namespace,
        flowId=flow_id,
        inputs=payload,
        runner=runner,
    )
    return await _execute_flow(
        repository,
        flow,
        execution_request,
        settings,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        actor=actor,
        authorization_service=authorization_service,
        background_tasks=background_tasks,
        launch_source=ExecutionLaunchSource.EVENT,
        trigger_context={
            "id": trigger.id,
            "type": trigger.type,
            "body": payload,
        },
    )


async def _execute_flow(
    repository: PostgresExecutionRepository,
    flow: FlowDefinition,
    request: CreateExecutionRequest,
    settings: Settings,
    *,
    tenant_id: str,
    actor_id: str,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    background_tasks: BackgroundTasks,
    launch_source: ExecutionLaunchSource,
    trigger_context: dict[str, object] | None = None,
) -> ExecutionDetail:
    if flow.disabled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"flow {flow.namespace}.{flow.id} is disabled",
        )
    kubernetes_runner: KubernetesJobRunner | None = None
    if request.runner is RunnerMode.KUBERNETES:
        if settings.kubernetes_context is None:
            kubernetes_runner = KubernetesJobRunner.from_in_cluster(
                namespace=settings.kubernetes_task_namespace
            )
        else:
            kubernetes_runner = await KubernetesJobRunner.from_kube_config(
                namespace=settings.kubernetes_task_namespace,
                context=settings.kubernetes_context,
            )
        shell_handler = kubernetes_job_handler(kubernetes_runner)
    else:
        shell_handler = local_process_handler(LocalProcessRunner())

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

    try:
        try:
            execution = await repository.create_execution(
                flow,
                tenant_id=tenant_id,
                inputs=request.inputs,
                trigger=trigger_context,
                launch_source=launch_source,
                idempotency_key=request.idempotency_key,
                actor_id=actor_id,
            )
        except (TenantQuotaExceeded, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        if execution.state is ExecutionState.RUNNING:
            await executor.run_to_completion(
                flow,
                execution.execution_id,
                tenant_id=tenant_id,
            )
        detail = ExecutionDetail(
            execution=await repository.get_execution(
                execution.execution_id,
                tenant_id=tenant_id,
            ),
            taskRuns=await repository.list_task_runs(
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
) -> list[TenantDefinition]:
    await _authorize_tenant_administration(authorization_service, actor)
    return await tenants.list()


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
) -> list[PrincipalDefinition]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="principal",
        action=PermissionAction.VIEW,
    )
    return await repository.list_principals()


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
) -> list[RoleDefinition]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="role",
        action=PermissionAction.VIEW,
    )
    return await repository.list_roles()


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
) -> list[RoleBinding]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.VIEW,
    )
    return await repository.list_bindings()


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
) -> list[CredentialMetadata]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.VIEW,
    )
    return await credentials.list(principal_id)


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
