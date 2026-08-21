from __future__ import annotations

import logging
import secrets
from collections.abc import Awaitable, Callable
from functools import lru_cache
from time import perf_counter
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh import __version__
from amesh.adapters.kubernetes import KubernetesJobRunner
from amesh.adapters.local import LocalProcessRunner
from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresCredentialRepository,
    PostgresExecutionRepository,
)
from amesh.api.models import (
    AuthorizationExplanationRequest,
    CreateExecutionRequest,
    ExchangeCredentialRequest,
    ExecutionDetail,
    HealthResponse,
    IssueCredentialRequest,
    IssuedCredentialResponse,
    ReduceExecutionRequest,
    ReduceExecutionResponse,
    RevokedCredentialsResponse,
    RotateCredentialRequest,
    RunnerMode,
    TaskLog,
)
from amesh.authorization import AuthorizationDenied, AuthorizationService
from amesh.config import Settings, get_settings
from amesh.credentials import CredentialOperationError, CredentialService, InvalidCredential
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    CredentialMetadata,
    InvalidTransition,
    IssuedCredential,
    NamespaceAuthorizationBoundary,
    PermissionAction,
    PrincipalDefinition,
    PrincipalType,
    ResourceVersionConflict,
    RoleBinding,
    RoleDefinition,
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
    kubernetes_job_handler,
    local_process_handler,
)
from amesh.observability import HTTP_REQUEST_DURATION, HTTP_REQUESTS
from amesh.ports import (
    CredentialRateLimitExceeded,
    LastAdministratorError,
    PersistedExecution,
    PersistedFlow,
)
from amesh.tasks import agent_llm_handler, agent_mcp_handler, core_http_handler

LOGGER = logging.getLogger("amesh.api")

app = FastAPI(
    title="AMESH",
    version=__version__,
    description=(
        "Clean-room durable workflow MVP with validated flow management, "
        "execution control, webhook triggers and execution logs."
    ),
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
    return create_async_engine(get_settings().database_url)


@lru_cache
def get_repository() -> PostgresExecutionRepository:
    return PostgresExecutionRepository(database_engine())


RepositoryDependency = Annotated[
    PostgresExecutionRepository,
    Depends(get_repository),
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


_BOOTSTRAP_PRINCIPAL_ID = UUID("00000000-0000-7000-8000-000000000001")


async def authenticate_actor(
    settings: SettingsDependency,
    credential_service: CredentialServiceDependency,
    authorization: Annotated[str | None, Header()] = None,
) -> ActorContext:
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized",
        ) from exc


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@app.get("/ready", response_model=HealthResponse, tags=["system"])
async def ready() -> HealthResponse:
    return HealthResponse(status="ready", version=__version__)


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
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
    tenant_id: Annotated[str, Header(alias="X-Amesh-Tenant")] = "default",
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
            detail=[issue.model_dump(mode="json") for issue in result.issues],
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
    tenant_id: Annotated[str, Header(alias="X-Amesh-Tenant")] = "default",
) -> list[PersistedFlow]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_flows(tenant_id=tenant_id)


@app.post(
    "/api/v1/executions",
    response_model=ExecutionDetail,
    tags=["executions"],
)
async def create_execution(
    request: CreateExecutionRequest,
    repository: RepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: Annotated[str, Header(alias="X-Amesh-Tenant")] = "default",
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
    limit: int = 100,
    tenant_id: Annotated[str, Header(alias="X-Amesh-Tenant")] = "default",
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
    "/api/v1/executions/{execution_id}",
    response_model=ExecutionDetail,
    tags=["executions"],
)
async def get_execution(
    execution_id: UUID,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: Annotated[str, Header(alias="X-Amesh-Tenant")] = "default",
) -> ExecutionDetail:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        execution = await repository.get_execution(execution_id)
        if execution.tenant_id != tenant_id:
            raise LookupError(f"execution {execution_id} does not exist")
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    task_runs = await repository.list_task_runs(execution_id)
    return ExecutionDetail(execution=execution, taskRuns=task_runs)


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
    tenant_id: Annotated[str, Header(alias="X-Amesh-Tenant")] = "default",
) -> list[TaskLog]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        execution = await repository.get_execution(execution_id)
        if execution.tenant_id != tenant_id:
            raise LookupError(f"execution {execution_id} does not exist")
        task_runs = await repository.list_task_runs(execution_id)
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
    repository: RepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    runner: RunnerMode = RunnerMode.LOCAL,
    tenant_id: Annotated[str, Header(alias="X-Amesh-Tenant")] = "default",
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
    )


async def _execute_flow(
    repository: PostgresExecutionRepository,
    flow: FlowDefinition,
    request: CreateExecutionRequest,
    settings: Settings,
    *,
    tenant_id: str,
    actor_id: str,
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

    executor = InProcessExecutor(
        repository,
        handlers={
            "core.shell": shell_handler,
            "core.http": core_http_handler(),
            "agent.llm": agent_llm_handler(),
            "agent.mcp": agent_mcp_handler(),
        },
    )
    try:
        execution = await repository.create_execution(
            flow,
            tenant_id=tenant_id,
            inputs=request.inputs,
            idempotency_key=request.idempotency_key,
            actor_id=actor_id,
        )
        await executor.run_to_completion(flow, execution.execution_id)
        return ExecutionDetail(
            execution=await repository.get_execution(execution.execution_id),
            taskRuns=await repository.list_task_runs(execution.execution_id),
        )
    finally:
        if kubernetes_runner is not None:
            await kubernetes_runner.close()


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
    tenant_id: Annotated[str, Header(alias="X-Amesh-Tenant")] = "default",
) -> ReduceExecutionResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
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
