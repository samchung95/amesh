"""Cohesive executions API definitions extracted from the composition root."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Query,
    Response,
    status,
)
from starlette.responses import StreamingResponse

from amesh.api.contracts import (
    CollectionQuery,
    _decode_cursor,
    _encode_cursor,
    collection_response,
    default_limited_collection_query,
)
from amesh.api.dependencies import (
    ActorDependency,
    AgentSessionRepositoryDependency,
    AuthorizationServiceDependency,
    CheckRepositoryDependency,
    EvidenceBundleRepositoryDependency,
    MetadataRepositoryDependency,
    OperationalControlRepositoryDependency,
    ReadRepositoryDependency,
    RepositoryDependency,
    SettingsDependency,
    SharedResourceRepositoryDependency,
    TaskCacheRepositoryDependency,
    TenantDependency,
    TenantServiceDependency,
    authorize_request,
    require_namespace_permission,
)
from amesh.api.evidence_models import EvidenceBundlePageResponse
from amesh.api.models import (
    AgentSessionDetailResponse,
    AgentSessionSummary,
    BulkExecutionItemResult,
    BulkExecutionRequest,
    CheckPolicyUpsertRequest,
    CreateExecutionRequest,
    ExecutionDetail,
    ExecutionEvidencePage,
    ExecutionInterventionPreviewRequest,
    ExecutionInterventionRequest,
    FlowGraph,
    ProblemDetail,
    ReduceExecutionRequest,
    ReduceExecutionResponse,
    ResumeTaskRequest,
    TaskCachePurgeRequest,
    TaskLog,
)
from amesh.api.route_support import (
    _apply_execution_control_authorized,
    _authorize_agent_session_access,
    _build_flow_graph,
    _execute_flow,
    _prefers_async_response,
    _public_agent_session_detail,
    _public_execution,
    _public_execution_detail,
    _resolve_idempotency_key,
)
from amesh.domain import (
    ActorContext,
    AdmissionDecision,
    AdmissionResourceType,
    AgentSessionDetail,
    ExecutionState,
    InvalidTransition,
    PermissionAction,
    reduce_execution,
)
from amesh.dsl import (
    FlowDefinition,
)
from amesh.evidence_bundle import (
    EvidenceConflictError,
    EvidenceNotFoundError,
    EvidenceUnavailableError,
)
from amesh.executor import (
    TaskResourceLimitError,
    normalize_task_completion,
    preview_execution_intervention,
)
from amesh.ports import (
    CheckComplianceSummary,
    CheckEvaluation,
    CheckOutcome,
    ExecutionArtifact,
    ExecutionEvidenceEvent,
    ExecutionInterventionPreview,
    ExecutionInterventionRecord,
    ExecutionLaunchSource,
    NamespaceCheckPolicy,
    PersistedExecution,
    PersistedSubflow,
    PersistedTaskRun,
    TaskCacheEntry,
    TaskCachePurgeResult,
    TaskStateConflictError,
    TenantUnavailableError,
)
from amesh.storage.factory import build_object_store
from amesh.workflow.data_contracts import (
    redact_matching_values,
    sensitive_execution_values,
)

router_1 = APIRouter()
router_2 = APIRouter()
router_3 = APIRouter()
router_4 = APIRouter()
router_5 = APIRouter()
router_6 = APIRouter()


@router_1.post(
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


@router_1.post(
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


@router_1.get(
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


@router_1.post(
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


@router_1.get(
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


@router_1.put(
    "/api/v1/check-policies/{namespace}/{policy_key}",
    response_model=NamespaceCheckPolicy,
    tags=["checks"],
)
async def upsert_check_policy(
    namespace: str,
    policy_key: str,
    request: CheckPolicyUpsertRequest,
    checks: CheckRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("check", PermissionAction.MANAGE))
    ],
    tenant_id: TenantDependency,
) -> NamespaceCheckPolicy:
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


@router_1.get(
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


@router_1.get(
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


@router_2.get(
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


@router_2.get(
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


@router_2.get(
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


@router_3.get(
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


@router_3.get(
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
    execution_trigger = getattr(execution, "trigger", None)
    return [
        _public_agent_session_detail(
            AgentSessionDetail(session=session, events=()),
            after_event_index=0,
            limit=100,
            policy_provenance=(
                execution_trigger.get("ameshAgentSessionPolicy")
                if isinstance(execution_trigger, dict)
                and isinstance(execution_trigger.get("ameshAgentSessionPolicy"), dict)
                else None
            ),
        ).session
        for session in await sessions.list_execution_sessions(tenant_id, execution_id)
    ]


@router_3.get(
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
    execution_trigger = getattr(execution, "trigger", None)
    return _public_agent_session_detail(
        detail,
        after_event_index=after_event_index,
        limit=limit,
        policy_provenance=(
            execution_trigger.get("ameshAgentSessionPolicy")
            if isinstance(execution_trigger, dict)
            and isinstance(execution_trigger.get("ameshAgentSessionPolicy"), dict)
            else None
        ),
    )


@router_4.get(
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


@router_4.get(
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


@router_4.get(
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


@router_5.get(
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


@router_5.get(
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


@router_5.get(
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


@router_5.post(
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


@router_5.get(
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


@router_5.get(
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


@router_5.post(
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


@router_5.post(
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
    return await _apply_execution_control_authorized(
        execution_id,
        request,
        repository,
        actor,
        tenant_id,
    )


@router_5.get(
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


@router_5.get(
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


@router_5.get(
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


@router_6.post(
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
