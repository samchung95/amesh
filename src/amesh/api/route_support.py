"""Cohesive route support API definitions extracted from the composition root."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import timedelta
from typing import Any, Literal, cast
from uuid import UUID

from fastapi import (
    BackgroundTasks,
    HTTPException,
    status,
)

from amesh.adapters.agent_session_registry import (
    create_agent_session_harness,
)
from amesh.adapters.postgres import (
    PostgresAgentMemoryRepository,
    PostgresAgentPrimitiveRepository,
    PostgresAgentProgressSink,
    PostgresAgentResourceRepository,
    PostgresAgentSessionRepository,
)
from amesh.api.dependencies import (
    ActorDependency,
    AgentSessionRepositoryDependency,
    AuthorizationServiceDependency,
    RepositoryDependency,
    authorize_agent_session_request,
    authorize_request,
    database_engine,
    get_human_task_repository,
    get_isolated_plugin_runtime,
    get_trusted_plugin_runtime,
)
from amesh.api.models import (
    AgentSessionControlSummary,
    AgentSessionDetailResponse,
    AgentSessionServiceDetailResponse,
    AgentSessionSummary,
    CreateExecutionRequest,
    ExecutionDetail,
    ExecutionInterventionRequest,
    FlowGraph,
    FlowGraphEdge,
    FlowGraphNode,
)
from amesh.application import (
    LAUNCH_RECOVER_RUNNING_TYPES,
    ExecutionLaunchConflict,
    ExecutionLaunchRepository,
    ExecutionLaunchService,
    HandlerComposition,
    RuntimeCompositionError,
    build_execution_runtime,
    select_runner_ids,
)
from amesh.authorization import AuthorizationService
from amesh.config import (
    Settings,
)
from amesh.domain import (
    ActorContext,
    AgentHarnessPin,
    AgentSessionDetail,
    AgentSessionState,
    ExecutionState,
    OperationalBoundary,
    PermissionAction,
    PolicyDecision,
    PolicyStage,
    ServiceRole,
)
from amesh.domain.runner import RunnerId, RunnerPolicyViolation
from amesh.dsl import (
    FlowDefinition,
    TaskDefinition,
    compile_execution_tasks,
)
from amesh.executor import (
    TaskHandler,
    preview_execution_intervention,
)
from amesh.model_continuations import (
    configured_model_continuation_protector,
)
from amesh.model_engine_runtime import (
    configured_model_capability_resolver,
    configured_model_engine_registry,
    configured_openai_compatible,
)
from amesh.plugins import (
    IsolatedPluginRuntime,
    TrustedPluginRuntime,
)
from amesh.ports import (
    ExecutionLaunchSource,
    ExecutionRepository,
    ExecutionStateConflictError,
    OperationalControlRepository,
    PersistedExecution,
    PersistedIterationSummary,
    PersistedTaskRun,
    PersistedTaskRunSummary,
    SharedResourceRepository,
    TaskCacheRepository,
)
from amesh.realtime import (
    redact_realtime_payload,
)
from amesh.storage.factory import build_object_store
from amesh.tasks import (
    HttpTaskPolicy,
)
from amesh.workflow.data_contracts import (
    DataContractError,
    normalized_input_type,
    redact_matching_values,
    redact_sensitive_inputs,
    redact_sensitive_outputs,
    sensitive_execution_values,
    stage_file_inputs,
    validate_flow_inputs,
)
from amesh.workflow.shared_resources import (
    NamespaceImageArtifactResolver,
    NamespaceResourceService,
    SharedResourceContextProvider,
)
from amesh.workflow.working_directory import WorkingDirectoryManager


async def _apply_execution_control_authorized(
    execution_id: UUID,
    request: ExecutionInterventionRequest,
    repository: RepositoryDependency,
    actor: ActorContext,
    tenant_id: str,
) -> ExecutionDetail:
    """Apply a fenced intervention after the caller has authorized its own boundary."""

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


def _prefers_async_response(prefer: str | None) -> bool:
    if prefer is None:
        return False
    return any(item.strip().lower() == "respond-async" for item in prefer.split(","))


async def _authorize_agent_session_access(
    execution: PersistedExecution,
    *,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> None:
    """Authorize owner reads separately from fleet visibility."""

    owner_id = execution.trigger.get("ameshActorId")
    if owner_id == str(actor.principal_id):
        await authorize_agent_session_request(
            authorization_service,
            actor,
            action=PermissionAction.VIEW,
            legacy_actions=(PermissionAction.VIEW,),
            tenant_id=tenant_id,
            namespace=execution.namespace,
        )
        return
    await authorize_agent_session_request(
        authorization_service,
        actor,
        action=PermissionAction.LIST,
        legacy_actions=(PermissionAction.VIEW, PermissionAction.MANAGE),
        tenant_id=tenant_id,
        namespace=execution.namespace,
    )


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
    page = _public_agent_session_detail(
        detail,
        after_event_index=after_event_index,
        limit=limit,
        policy_provenance=(
            execution.trigger.get("ameshAgentSessionPolicy")
            if isinstance(execution.trigger.get("ameshAgentSessionPolicy"), dict)
            else None
        ),
    )
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
    policy_provenance: dict[str, Any] | None = None,
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
            policyProvenance=policy_provenance,
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
        applicationId=(
            execution.trigger.get("ameshApplicationId")
            if isinstance(execution.trigger.get("ameshApplicationId"), str)
            else None
        ),
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
        policyProvenance=(
            execution.trigger.get("ameshAgentSessionPolicy")
            if isinstance(execution.trigger.get("ameshAgentSessionPolicy"), dict)
            else None
        ),
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
        applicationId=(
            execution.trigger.get("ameshApplicationId")
            if isinstance(execution.trigger.get("ameshApplicationId"), str)
            else None
        ),
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
        policyProvenance=(
            execution.trigger.get("ameshAgentSessionPolicy")
            if isinstance(execution.trigger.get("ameshAgentSessionPolicy"), dict)
            else None
        ),
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


def _resolve_idempotency_key(body_value: str | None, header_value: str | None) -> str | None:
    if body_value is not None and header_value is not None and body_value != header_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header does not match idempotencyKey body field",
        )
    return header_value or body_value


async def _execute_flow(
    repository: ExecutionRepository,
    task_cache: TaskCacheRepository,
    flow: FlowDefinition,
    request: CreateExecutionRequest,
    settings: Settings,
    *,
    operational_controls: OperationalControlRepository,
    shared_resources: SharedResourceRepository,
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
        )
        or any(
            normalized_input_type(definition.type) == "image" and definition.id in request.inputs
            for definition in flow.inputs
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
    resource_service = NamespaceResourceService(shared_resources, object_store)
    workspace_manager = WorkingDirectoryManager(object_store)
    context_provider = SharedResourceContextProvider(
        shared_resources,
        object_store=object_store,
    )
    try:
        validated_inputs = validate_flow_inputs(flow, request.inputs)
        if any(
            normalized_input_type(definition.type) == "image"
            and isinstance(validated_inputs.get(definition.id), Mapping)
            and "contentBase64" in validated_inputs[definition.id]
            for definition in flow.inputs
        ):
            await authorize_request(
                authorization_service,
                actor,
                resource_type="namespace_file",
                action=PermissionAction.WRITE,
                tenant_id=tenant_id,
                namespace=flow.namespace,
            )
        validated_inputs = await stage_file_inputs(
            flow,
            validated_inputs,
            object_store,
            tenant_id=tenant_id,
            image_artifact_service=resource_service,
            actor_id=actor_id,
        )
        validated_inputs = validate_flow_inputs(flow, validated_inputs)
    except DataContractError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    fallback_runner = RunnerId(request.runner.value)
    try:
        runner_selection = select_runner_ids(
            settings,
            (node.task for node in planned_tasks),
            namespace=flow.namespace,
            fallback=fallback_runner,
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
        runner_ids=tuple(runner.value for runner in runner_selection.selected),
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
    agent_repository = PostgresAgentPrimitiveRepository(database_engine())
    agent_resources = PostgresAgentResourceRepository(database_engine())
    agent_sessions = PostgresAgentSessionRepository(database_engine())
    agent_progress_sink = PostgresAgentProgressSink(agent_sessions)
    agent_memory = PostgresAgentMemoryRepository(database_engine())
    image_resolver = NamespaceImageArtifactResolver(
        resource_service,
        actor_id=actor_id,
    )
    model_engine_registry = configured_model_engine_registry(
        settings,
        image_resolver=image_resolver,
    )
    trusted_runtime: TrustedPluginRuntime | None = None
    isolated_runtime: IsolatedPluginRuntime | None = None
    plugin_resolution: Mapping[str, object] | None = None
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
        plugin_resolution = revision.plugin_resolution
        if settings.trusted_plugin_approvals:
            trusted_runtime = get_trusted_plugin_runtime()
            await trusted_runtime.ensure_started()
        if settings.isolated_plugin_services:
            isolated_runtime = get_isolated_plugin_runtime()
            await isolated_runtime.ensure_configured()

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
        extra = task.configuration
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

    def compose_handlers(
        shell_handler: TaskHandler,
        http_policy: HttpTaskPolicy,
    ) -> HandlerComposition:
        return HandlerComposition(
            workspace_manager=workspace_manager,
            shell_handler=shell_handler,
            execution_repository=repository,
            http_policy=http_policy,
            model_configuration=configured_openai_compatible(settings),
            agent_repository=agent_repository,
            agent_resources=agent_resources,
            agent_sessions=agent_sessions,
            agent_memory=agent_memory,
            agent_progress_sink=agent_progress_sink,
            image_resolver=image_resolver,
            model_engine_registry=model_engine_registry,
            model_capability_resolver=configured_model_capability_resolver(model_engine_registry),
            continuation_protector=configured_model_continuation_protector(
                primary_key_id=settings.model_continuation_key_id,
                primary_key=settings.model_continuation_encryption_key,
                previous_key_id=settings.model_continuation_previous_key_id,
                previous_key=settings.model_continuation_previous_encryption_key,
            ),
            agent_session_harness=create_agent_session_harness(
                settings.agent_session_harness,
                settings.agent_session_pi_worker_command,
                max_frame_bytes=settings.agent_session_max_frame_bytes,
                operation_timeout_seconds=settings.model_engine_timeout_seconds,
                cancel_grace_seconds=settings.model_engine_cancel_grace_seconds,
                environment=settings.model_engine_environment,
            ),
            human_task_repository=get_human_task_repository(),
            token_pepper=settings.amesh_token_pepper.get_secret_value(),
            script_policy=settings.script_task_policy,
            trusted_plugin_runtime=trusted_runtime,
            isolated_plugin_runtime=isolated_runtime,
            plugin_resolution=plugin_resolution,
        )

    try:
        runtime = await build_execution_runtime(
            settings,
            (node.task for node in planned_tasks),
            workspace_manager,
            repository,
            compose_handlers,
            authorize_subflow,
            namespace=flow.namespace,
            runner_selection=runner_selection,
            context_provider=context_provider,
            object_store=object_store,
            task_cache=task_cache,
            dispatch_policy_enforcer=(
                enforce_dispatch_policy if repository.has_admission_policy_enforcer else None
            ),
            recover_running_types=LAUNCH_RECOVER_RUNNING_TYPES,
        )
    except RuntimeCompositionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    execution_trigger = dict(trigger_context or {})
    if request.cache_mode.value != "USE":
        execution_trigger["_ameshCacheMode"] = request.cache_mode.value
    launch_trigger = dict(trigger_context or {})
    if correlation_id is not None:
        launch_trigger.setdefault("correlationId", correlation_id)
    launch_service = ExecutionLaunchService(
        cast(ExecutionLaunchRepository, repository),
        runtime.executor_factory,
        schedule_background=background_tasks.add_task,
        close_runtime=runtime.close,
    )
    try:
        result = await launch_service.launch(
            flow,
            tenant_id=tenant_id,
            actor_id=actor_id,
            inputs=validated_inputs,
            trigger={**execution_trigger, **launch_trigger} or None,
            launch_source=launch_source,
            idempotency_key=idempotency_key,
            respond_async=respond_async,
        )
    except ExecutionLaunchConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _public_execution_detail(flow, result.execution, list(result.task_runs))


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
