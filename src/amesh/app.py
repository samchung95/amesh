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
from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.api.models import (
    CreateExecutionRequest,
    ExecutionDetail,
    HealthResponse,
    ReduceExecutionRequest,
    ReduceExecutionResponse,
    RunnerMode,
    TaskLog,
)
from amesh.config import Settings, get_settings
from amesh.domain import InvalidTransition, reduce_execution
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
from amesh.ports import PersistedExecution, PersistedFlow
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


async def require_admin(
    settings: SettingsDependency,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    expected = f"Bearer {settings.amesh_admin_token.get_secret_value()}"
    if authorization is None or not secrets.compare_digest(authorization, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="valid admin bearer token required",
        )


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
    dependencies=[Depends(require_admin)],
)
async def apply_flow(
    request: Request,
    repository: RepositoryDependency,
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
    try:
        return await repository.apply_flow(flow, tenant_id="default")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/api/v1/flows",
    response_model=list[PersistedFlow],
    tags=["flows"],
    dependencies=[Depends(require_admin)],
)
async def list_flows(
    repository: RepositoryDependency,
) -> list[PersistedFlow]:
    return await repository.list_flows(tenant_id="default")


@app.post(
    "/api/v1/executions",
    response_model=ExecutionDetail,
    tags=["executions"],
    dependencies=[Depends(require_admin)],
)
async def create_execution(
    request: CreateExecutionRequest,
    repository: RepositoryDependency,
    settings: SettingsDependency,
) -> ExecutionDetail:
    try:
        flow = await repository.get_flow(
            request.namespace,
            request.flow_id,
            tenant_id="default",
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return await _execute_flow(repository, flow, request, settings)


@app.get(
    "/api/v1/executions",
    response_model=list[PersistedExecution],
    tags=["executions"],
    dependencies=[Depends(require_admin)],
)
async def list_executions(
    repository: RepositoryDependency,
    limit: int = 100,
) -> list[PersistedExecution]:
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="limit must be between 1 and 1000",
        )
    return await repository.list_executions(tenant_id="default", limit=limit)


@app.get(
    "/api/v1/executions/{execution_id}",
    response_model=ExecutionDetail,
    tags=["executions"],
    dependencies=[Depends(require_admin)],
)
async def get_execution(
    execution_id: UUID,
    repository: RepositoryDependency,
) -> ExecutionDetail:
    try:
        execution = await repository.get_execution(execution_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    task_runs = await repository.list_task_runs(execution_id)
    return ExecutionDetail(execution=execution, taskRuns=task_runs)


@app.get(
    "/api/v1/executions/{execution_id}/logs",
    response_model=list[TaskLog],
    tags=["executions"],
    dependencies=[Depends(require_admin)],
)
async def get_execution_logs(
    execution_id: UUID,
    repository: RepositoryDependency,
) -> list[TaskLog]:
    try:
        task_runs = await repository.list_task_runs(execution_id)
        await repository.get_execution(execution_id)
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
    dependencies=[Depends(require_admin)],
)
async def trigger_webhook(
    namespace: str,
    flow_id: str,
    trigger_id: str,
    request: Request,
    repository: RepositoryDependency,
    settings: SettingsDependency,
    runner: RunnerMode = RunnerMode.LOCAL,
) -> ExecutionDetail:
    try:
        flow = await repository.get_flow(namespace, flow_id, tenant_id="default")
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
    return await _execute_flow(repository, flow, execution_request, settings)


async def _execute_flow(
    repository: PostgresExecutionRepository,
    flow: FlowDefinition,
    request: CreateExecutionRequest,
    settings: Settings,
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
            tenant_id="default",
            inputs=request.inputs,
            idempotency_key=request.idempotency_key,
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
    "/api/v1/executions/reduce",
    response_model=ReduceExecutionResponse,
    tags=["executions"],
)
async def reduce_execution_events(
    request: ReduceExecutionRequest,
) -> ReduceExecutionResponse:
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
