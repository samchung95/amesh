"""Triggers HTTP routes."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)

from amesh.api.dependencies import (
    ActorDependency,
    AuthorizationServiceDependency,
    OperationalControlRepositoryDependency,
    RepositoryDependency,
    SettingsDependency,
    SharedResourceRepositoryDependency,
    TaskCacheRepositoryDependency,
    TenantDependency,
    TriggerRuntimeRepositoryDependency,
    authorize_request,
    require_namespace_permission,
)
from amesh.api.models import (
    CreateExecutionRequest,
    ExecutionDetail,
    RunnerMode,
    TriggerActionRequest,
)
from amesh.api.route_support import (
    _execute_flow,
    _prefers_async_response,
    _public_execution_detail,
)
from amesh.domain import (
    ActorContext,
    ExecutionState,
    OperationalBoundary,
    PermissionAction,
    ServiceRole,
    new_runtime_id,
)
from amesh.ports import (
    ExecutionLaunchSource,
    TriggerOccurrence,
    TriggerOccurrenceState,
    TriggerRuntimeState,
)
from amesh.scheduler import CronScheduler, SchedulePreview
from amesh.storage.factory import build_object_store
from amesh.workflow.data_contracts import (
    DataContractError,
    normalized_input_type,
    redact_sensitive_inputs,
    stage_file_inputs,
    validate_flow_inputs,
)
from amesh.workflow.shared_resources import (
    NamespaceResourceService,
)

router_1 = APIRouter()
router_2 = APIRouter()
router_3 = APIRouter()


@router_1.get(
    "/api/v1/flows/{namespace}/{flow_id}/schedules/{trigger_id}/preview",
    response_model=SchedulePreview,
    tags=["triggers"],
)
async def preview_schedule(
    namespace: str,
    flow_id: str,
    trigger_id: str,
    repository: RepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow", PermissionAction.VIEW))
    ],
    tenant_id: TenantDependency,
    after: datetime | None = None,
    count: int = 5,
) -> SchedulePreview:
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


@router_2.get(
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


@router_2.get(
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


@router_2.post(
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("trigger", PermissionAction.MANAGE))
    ],
    tenant_id: TenantDependency,
) -> TriggerRuntimeState:
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


@router_2.post(
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("trigger", PermissionAction.MANAGE))
    ],
    tenant_id: TenantDependency,
) -> TriggerRuntimeState:
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


@router_2.post(
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


@router_3.post(
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("execution", PermissionAction.EXECUTE))
    ],
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    runner: RunnerMode = RunnerMode.LOCAL,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    source_event_id: Annotated[str | None, Header(alias="X-Event-Id")] = None,
) -> ExecutionDetail:
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
        image_values = [
            payload[definition.id]
            for definition in flow.inputs
            if normalized_input_type(definition.type) == "image" and definition.id in payload
        ]
        if image_values:
            await authorize_request(
                authorization_service,
                actor,
                resource_type="namespace_file",
                action=PermissionAction.USE,
                tenant_id=tenant_id,
                namespace=flow.namespace,
            )
        if any(isinstance(value, Mapping) and "contentBase64" in value for value in image_values):
            await authorize_request(
                authorization_service,
                actor,
                resource_type="namespace_file",
                action=PermissionAction.WRITE,
                tenant_id=tenant_id,
                namespace=flow.namespace,
            )
        object_store = build_object_store(settings)
        payload = await stage_file_inputs(
            flow,
            payload,
            object_store,
            tenant_id=tenant_id,
            image_artifact_service=NamespaceResourceService(
                shared_resources,
                object_store,
            ),
            actor_id=str(actor.principal_id),
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
