"""Cohesive agent sessions API definitions extracted from the composition root."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator, Mapping
from http import HTTPStatus
from typing import Annotated, Any, Literal, NoReturn
from uuid import NAMESPACE_URL, UUID, uuid5

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
from fastapi.encoders import jsonable_encoder
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import ValidationError
from starlette.responses import StreamingResponse

from amesh.adapters.agent_session_registry import (
    AGENT_SESSION_HARNESS_REGISTRY,
)
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
from amesh.api.dependencies import (
    ActorDependency,
    AgentResourceRepositoryDependency,
    AgentSessionFleetRepositoryDependency,
    AgentSessionPolicyRepositoryDependency,
    AgentSessionRepositoryDependency,
    AuthorizationServiceDependency,
    NamespaceResourceServiceDependency,
    OperationalControlRepositoryDependency,
    ProfileTransferServiceDependency,
    RepositoryDependency,
    SettingsDependency,
    SharedResourceRepositoryDependency,
    TaskCacheRepositoryDependency,
    TenantDependency,
    TransferRepositoryDependency,
    _agent_session_fleet_access_allowed,
    authorize_agent_session_request,
    authorize_request,
    get_agent_session_policy_repository,
)
from amesh.api.models import (
    AgentProgressPage,
    AgentSessionBulkActionItemResult,
    AgentSessionBulkActionRequest,
    AgentSessionBulkActionResponse,
    AgentSessionControlRequest,
    AgentSessionCreateRequest,
    AgentSessionHarnessCatalogEntry,
    AgentSessionLaunchResponse,
    AgentSessionMessageRequest,
    AgentSessionPolicyUpsertRequest,
    AgentSessionResultResponse,
    AgentSessionServiceDetailResponse,
    AgentSessionServiceItem,
    AgentSessionSummary,
    AgentSessionTransferProfileImportRequest,
    AgentSessionTransferProfilePlanRequest,
    AgentSessionTransferSessionExportRequest,
    AgentSessionTransferSessionImportRequest,
    AgentSessionTransferSessionPlanRequest,
    CreateExecutionRequest,
    ExecutionDetail,
    ExecutionInterventionRequest,
    ProblemDetail,
    RunnerMode,
)
from amesh.api.route_support import (
    _apply_execution_control_authorized,
    _authorize_agent_session_access,
    _control_agent_session_summary,
    _execute_flow,
    _get_service_agent_session_execution,
    _prefers_async_response,
    _public_agent_session_detail,
    _public_execution_detail,
    _queued_agent_session_summary,
    _resolve_idempotency_key,
    get_service_agent_session_detail,
    get_service_agent_session_response,
)
from amesh.domain import (
    ActorContext,
    AdmissionBehavior,
    AdmissionScope,
    AgentProgressActivity,
    AgentProgressEvent,
    AgentProgressLimits,
    AgentSessionDetail,
    AgentSessionEventCursor,
    AgentSessionFleetPage,
    AgentSessionFleetQuery,
    AgentSessionInstanceAggregate,
    AgentSessionPolicyRevision,
    AgentSessionState,
    ConcurrencyLimit,
    EffectiveCapabilityEnvelope,
    ExecutionState,
    ImageArtifactRef,
    PermissionAction,
    ResourceVersionConflict,
    evaluate_agent_session_policies,
    new_runtime_id,
)
from amesh.dsl import (
    FlowDefinition,
    TaskDefinition,
)
from amesh.ports import (
    AgentSessionFleetCursorError,
    AgentSessionPolicyVersionConflict,
    AgentSessionRepository,
    ExecutionInterventionAction,
    ExecutionLaunchSource,
    PersistedExecution,
)
from amesh.profile_transfer import (
    ProfileBundle,
    ProfileCompatibilityError,
    ProfileCompatibilityReport,
    ProfileImportResult,
)
from amesh.session_transfer import (
    SessionTransferBundle,
    SessionTransferCompatibilityReport,
    SessionTransferImportResult,
    SessionTransferService,
)
from amesh.storage.factory import build_object_store
from amesh.workflow.shared_resources import (
    NamespaceResourceService,
)

router_1 = APIRouter()


router_2 = APIRouter()


def _validate_agent_session_policy_identity(
    namespace: str | None,
    application_id: str | None,
) -> None:
    if application_id is not None and namespace is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="applicationId requires namespace",
        )


def _resolve_agent_session_application_id(
    actor: ActorContext,
    requested_application_id: str | None,
) -> str:
    """Bind application policy selection to the authenticated principal identity."""

    authoritative_application_id = actor.display
    if (
        requested_application_id is not None
        and requested_application_id != authoritative_application_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="applicationId is not authorized for the authenticated principal",
        )
    return authoritative_application_id


@router_1.get(
    "/api/v1/admin/agent-session-policies",
    response_model=tuple[AgentSessionPolicyRevision, ...],
    tags=["agent-session-administration"],
)
async def list_agent_session_policies(
    repository: AgentSessionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: Annotated[str | None, Query(min_length=1, max_length=255)] = None,
    application_id: Annotated[
        str | None, Query(alias="applicationId", min_length=1, max_length=255)
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> tuple[AgentSessionPolicyRevision, ...]:
    _validate_agent_session_policy_identity(namespace, application_id)
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_policy",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_revisions(
        tenant_id,
        namespace=namespace,
        application_id=application_id,
        limit=limit,
    )


@router_1.get(
    "/api/v1/admin/agent-session-policies/effective",
    response_model=tuple[AgentSessionPolicyRevision, ...],
    tags=["agent-session-administration"],
)
async def get_effective_agent_session_policies(
    repository: AgentSessionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: Annotated[str, Query(min_length=1, max_length=255)],
    application_id: Annotated[
        str | None, Query(alias="applicationId", min_length=1, max_length=255)
    ] = None,
) -> tuple[AgentSessionPolicyRevision, ...]:
    _validate_agent_session_policy_identity(namespace, application_id)
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_policy",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.effective_revisions(
        tenant_id,
        namespace=namespace,
        application_id=application_id,
    )


@router_1.get(
    "/api/v1/admin/agent-session-policies/{policy_id}",
    response_model=AgentSessionPolicyRevision,
    tags=["agent-session-administration"],
)
async def get_agent_session_policy_revision(
    policy_id: UUID,
    repository: AgentSessionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> AgentSessionPolicyRevision:
    try:
        result = await repository.get_revision(tenant_id, policy_id=policy_id, revision=revision)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_policy",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=result.namespace,
    )
    return result


@router_1.put(
    "/api/v1/admin/agent-session-policies",
    response_model=AgentSessionPolicyRevision,
    status_code=status.HTTP_200_OK,
    tags=["agent-session-administration"],
)
async def put_agent_session_policy(
    request: AgentSessionPolicyUpsertRequest,
    repository: AgentSessionPolicyRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentSessionPolicyRevision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_policy",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=request.namespace,
    )
    try:
        return await repository.save_revision(
            tenant_id,
            request,
            actor_id=str(actor.principal_id),
            namespace=request.namespace,
            application_id=request.application_id,
            expected_revision=request.expected_revision,
        )
    except AgentSessionPolicyVersionConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


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
    await authorize_agent_session_request(
        authorization_service,
        actor,
        action=PermissionAction.CREATE,
        legacy_actions=(PermissionAction.EXECUTE,),
        tenant_id=tenant_id,
        namespace=namespace,
    )
    effective_application_id = _resolve_agent_session_application_id(actor, request.application_id)
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
        policy_evaluation = evaluate_agent_session_policies(
            await get_agent_session_policy_repository().effective_revisions(
                tenant_id,
                namespace=namespace,
                application_id=effective_application_id,
            ),
            envelope_ceiling_mode=preview.envelope.hard_limits.ceiling_mode,
            envelope_max_total_tokens=preview.envelope.hard_limits.max_total_tokens,
            envelope_max_cost_usd=preview.envelope.hard_limits.max_cost_usd,
            envelope_max_duration_seconds=preview.envelope.hard_limits.max_duration_seconds,
            envelope_max_concurrency=preview.envelope.hard_limits.max_concurrency,
            requested_timeout_seconds=request.timeout_seconds,
            provider_ids=provider_ids,
            harness_id=settings.agent_session_harness,
            tool_ids=_agent_session_tool_dependency_ids(preview.envelope),
        )
        admission_limits[0] = admission_limits[0].model_copy(
            update={"limit": policy_evaluation.max_concurrency}
        )
        task = TaskDefinition.model_validate(
            {
                "id": "agent",
                "type": "agent.session",
                "agent": request.agent,
                "agentRevision": request.agent_revision,
                "input": request.input,
                "invalidOutputPolicy": request.invalid_output_policy,
                "maxRepairAttempts": request.max_repair_attempts,
                "requiredToolPlan": (
                    request.required_tool_plan.model_dump(
                        mode="json",
                        by_alias=True,
                        exclude_none=True,
                    )
                    if request.required_tool_plan is not None
                    else None
                ),
                "approvalTask": request.approval_task,
                "dataHandling": request.data_handling.value,
                "businessAssertions": request.business_assertions,
                "memoryReadKeys": request.memory_read_keys,
                "memoryWriteKey": request.memory_write_key,
                "contextPolicy": request.context_policy.model_dump(
                    mode="json",
                    by_alias=True,
                ),
                **(
                    {"timeoutMode": request.timeout_mode.value}
                    if request.timeout_mode.value == "DISABLED"
                    else {"timeoutSeconds": request.timeout_seconds}
                ),
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
                "ameshAgentSessionTurn": 1,
                "ameshAgentSessionAttemptBase": 0,
                "ameshAgentRef": f"{namespace}/{request.agent}@{request.agent_revision}",
                "ameshApplicationId": effective_application_id,
                "ameshActorId": str(actor.principal_id),
                "ameshProviderId": ",".join(provider_ids),
                "ameshHarness": AGENT_SESSION_HARNESS_REGISTRY[settings.agent_session_harness],
                "ameshBudget": preview.envelope.hard_limits.model_dump(mode="json", by_alias=True),
                "ameshAgentSessionPolicy": policy_evaluation.provenance,
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
                "applicationId": effective_application_id,
                "modelProfile": request.model_profile,
                "policyProvenance": detail.execution.trigger.get("ameshAgentSessionPolicy"),
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


@router_2.post(
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
        if request.inline_images:
            await authorize_agent_session_request(
                self._authorization_service,
                self._actor,
                action=PermissionAction.CREATE,
                legacy_actions=(PermissionAction.EXECUTE,),
                tenant_id=tenant_id,
                namespace=namespace,
            )
            for action in (PermissionAction.READ, PermissionAction.WRITE):
                await authorize_request(
                    self._authorization_service,
                    self._actor,
                    resource_type="namespace_file",
                    action=action,
                    tenant_id=tenant_id,
                    namespace=namespace,
                )
            try:
                request = await _stage_openai_session_images(
                    request,
                    NamespaceResourceService(
                        self._shared_resources,
                        build_object_store(self._settings),
                    ),
                    tenant_id=tenant_id,
                    namespace=namespace,
                    actor_id=actor_id,
                )
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(exc),
                ) from exc
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


async def _stage_openai_session_images(
    request: CanonicalSessionRequest,
    service: NamespaceResourceService,
    *,
    tenant_id: str,
    namespace: str,
    actor_id: str,
) -> CanonicalSessionRequest:
    """Replace transient OpenAI image uploads with governed immutable references."""

    if not request.inline_images:
        return request
    uploads = {upload.upload_id: upload for upload in request.inline_images}
    if len(uploads) != len(request.inline_images):
        raise ValueError("inline image upload identifiers must be unique")

    staged: dict[str, ImageArtifactRef] = {}
    for upload_id, upload in uploads.items():
        checksum = hashlib.sha256(upload.content).hexdigest()
        path = f"openai-inputs/{checksum}"
        try:
            image = await service.get_image_artifact(
                namespace,
                path,
                tenant_id=tenant_id,
                actor_id=actor_id,
            )
        except LookupError:
            try:
                image = await service.upload_image(
                    namespace,
                    path,
                    upload.content,
                    tenant_id=tenant_id,
                    actor_id=actor_id,
                    content_type=upload.media_type,
                    expected_version=0,
                )
            except ResourceVersionConflict:
                image = await service.get_image_artifact(
                    namespace,
                    path,
                    tenant_id=tenant_id,
                    actor_id=actor_id,
                )
        if (
            image.artifact.checksum_sha256 != checksum
            or image.artifact.media_type != upload.media_type
        ):
            raise ValueError("staged image does not match its inline upload")
        staged[upload_id] = image

    used: set[str] = set()
    messages: list[dict[str, Any]] = []
    for message in request.messages:
        content = message.get("content")
        if not isinstance(content, list):
            messages.append(dict(message))
            continue
        parts: list[dict[str, Any]] = []
        for part in content:
            if not isinstance(part, Mapping) or part.get("type") != "inline_image_upload":
                parts.append(dict(part))
                continue
            if set(part) != {"type", "uploadId"}:
                raise ValueError("inline image placeholder is malformed")
            placeholder_id = part.get("uploadId")
            if not isinstance(placeholder_id, str) or placeholder_id not in staged:
                raise ValueError("inline image placeholder has no matching upload")
            used.add(placeholder_id)
            parts.append(
                {
                    "type": "image_ref",
                    "image": staged[placeholder_id].model_dump(mode="json", by_alias=True),
                }
            )
        messages.append({**message, "content": parts})
    if used != set(uploads):
        raise ValueError("inline image upload has no matching message placeholder")
    return request.model_copy(
        update={
            "messages": tuple(messages),
            "inline_images": (),
        }
    )


@router_2.post(
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


@router_2.post(
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


@router_2.get(
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

    await authorize_agent_session_request(
        authorization_service,
        actor,
        action=PermissionAction.VIEW,
        legacy_actions=(PermissionAction.VIEW,),
        tenant_id=tenant_id,
    )
    return {
        alias: AgentSessionHarnessCatalogEntry.model_validate(metadata)
        for alias, metadata in AGENT_SESSION_HARNESS_REGISTRY.items()
    }


@router_2.get(
    "/api/v1/admin/agent-sessions",
    response_model=AgentSessionFleetPage,
    tags=["agent-session-administration"],
)
async def list_agent_session_fleet(
    sessions: AgentSessionFleetRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    query: Annotated[AgentSessionFleetQuery, Depends()],
) -> AgentSessionFleetPage:
    """Return a bounded, tenant-isolated administrative session fleet projection."""

    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_administration",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
    )
    try:
        return await sessions.list_fleet(tenant_id, query)
    except AgentSessionFleetCursorError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router_2.get(
    "/api/v1/admin/agent-sessions/aggregate",
    response_model=AgentSessionInstanceAggregate,
    tags=["agent-session-administration"],
)
async def get_agent_session_instance_aggregate(
    sessions: AgentSessionFleetRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> AgentSessionInstanceAggregate:
    """Return instance-wide metadata-only totals without exposing tenant session rows."""

    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_administration",
        action=PermissionAction.VIEW,
    )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session",
        action=PermissionAction.LIST,
    )
    return await sessions.instance_aggregate()


def _raise_transfer_http_error(exc: Exception, *, conflict: bool = False) -> NoReturn:
    if isinstance(exc, LookupError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TRANSFER_NOT_FOUND: {exc}",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT if conflict else status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=(f"TRANSFER_CONFLICT: {exc}" if conflict else f"TRANSFER_INVALID: {exc}"),
    ) from exc


@router_2.get(
    "/api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export",
    response_model=ProfileBundle,
    tags=["agent-session-transfers"],
)
@router_2.post(
    "/api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export",
    response_model=ProfileBundle,
    tags=["agent-session-transfers"],
)
async def export_agent_profile_transfer(
    namespace: str,
    agent_key: str,
    profiles: ProfileTransferServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ProfileBundle:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_migration",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await profiles.export(
            tenant_id,
            namespace,
            agent_key,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        _raise_transfer_http_error(exc)
    except ValueError as exc:
        _raise_transfer_http_error(exc)


@router_2.post(
    "/api/v1/admin/agent-session-transfers/profiles/plan",
    response_model=ProfileCompatibilityReport,
    tags=["agent-session-transfers"],
)
async def plan_agent_profile_transfer(
    request: AgentSessionTransferProfilePlanRequest,
    profiles: ProfileTransferServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ProfileCompatibilityReport:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_migration",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=request.bundle.namespace,
    )
    try:
        return await profiles.compatibility(
            request.bundle,
            target_tenant_id=tenant_id,
            target_namespace=request.target_namespace,
        )
    except ValueError as exc:
        _raise_transfer_http_error(exc)


@router_2.post(
    "/api/v1/admin/agent-session-transfers/profiles/import",
    response_model=ProfileImportResult,
    tags=["agent-session-transfers"],
)
async def import_agent_profile_transfer(
    request: AgentSessionTransferProfileImportRequest,
    profiles: ProfileTransferServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ProfileImportResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_migration",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=request.bundle.namespace,
    )
    try:
        return await profiles.import_bundle(
            request.bundle,
            target_tenant_id=tenant_id,
            target_namespace=request.target_namespace,
            actor_id=str(actor.principal_id),
        )
    except ProfileCompatibilityError as exc:
        _raise_transfer_http_error(exc, conflict=True)
    except LookupError as exc:
        _raise_transfer_http_error(exc, conflict=True)
    except ValueError as exc:
        _raise_transfer_http_error(exc, conflict=True)


@router_2.post(
    "/api/v1/admin/agent-session-transfers/sessions/{session_id}/export",
    response_model=SessionTransferBundle,
    tags=["agent-session-transfers"],
)
async def export_agent_session_transfer(
    session_id: UUID,
    request: AgentSessionTransferSessionExportRequest,
    transfers: TransferRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SessionTransferBundle:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_migration",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return await transfers.export_session_bundle(
            tenant_id,
            session_id,
            mode=request.mode,
            artifact_destination_refs=request.artifact_destination_refs,
        )
    except LookupError as exc:
        _raise_transfer_http_error(exc)
    except ValueError as exc:
        _raise_transfer_http_error(exc, conflict=True)


@router_2.post(
    "/api/v1/admin/agent-session-transfers/sessions/plan",
    response_model=SessionTransferCompatibilityReport,
    tags=["agent-session-transfers"],
)
async def plan_agent_session_transfer(
    request: AgentSessionTransferSessionPlanRequest,
    transfers: TransferRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SessionTransferCompatibilityReport:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_migration",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    service = SessionTransferService(transfers)
    try:
        return await service.plan_import(
            request.bundle,
            target_tenant_id=tenant_id,
            credential_rebindings=request.credential_rebindings,
        )
    except LookupError as exc:
        _raise_transfer_http_error(exc)
    except ValueError as exc:
        _raise_transfer_http_error(exc)


@router_2.post(
    "/api/v1/admin/agent-session-transfers/sessions/import",
    response_model=SessionTransferImportResult,
    tags=["agent-session-transfers"],
)
async def import_agent_session_transfer(
    request: AgentSessionTransferSessionImportRequest,
    transfers: TransferRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SessionTransferImportResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_migration",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    service = SessionTransferService(transfers)
    try:
        return await service.import_bundle(
            request.bundle,
            target_tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            credential_rebindings=request.credential_rebindings,
        )
    except LookupError as exc:
        _raise_transfer_http_error(exc, conflict=True)
    except ValueError as exc:
        _raise_transfer_http_error(exc, conflict=True)


@router_2.get(
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
    fleet_access = await _agent_session_fleet_access_allowed(
        authorization_service,
        actor,
        tenant_id=tenant_id,
    )
    owner_id = None if fleet_access else str(actor.principal_id)
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


@router_2.get(
    "/api/v1/agent-sessions/{service_session_id}/progress",
    response_model=AgentProgressPage,
    tags=["agent-sessions"],
)
async def get_agent_session_progress(
    service_session_id: UUID,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    after: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> AgentProgressPage:
    """Return one authorized page from the canonical cross-attempt timeline."""

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
    cursor = _agent_progress_cursor(service_session_id, after)
    bounded_limit = min(limit, _AGENT_PROGRESS_MAX_BUFFERED_FRAMES)
    try:
        events = await _bounded_agent_progress_page(
            sessions,
            tenant_id,
            service_session_id,
            after=cursor,
            limit=bounded_limit,
        )
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="agent progress observer timed out",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AgentProgressPage(
        sessionId=service_session_id,
        events=events,
        nextCursor=events[-1].cursor if events else cursor.encode(),
    )


@router_2.get(
    "/api/v1/agent-sessions/{service_session_id}/progress/stream",
    response_class=StreamingResponse,
    tags=["agent-sessions"],
)
async def stream_agent_session_progress(
    service_session_id: UUID,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    after: Annotated[str | None, Query(min_length=1, max_length=512)] = None,
    last_event_id: Annotated[
        str | None,
        Header(alias="Last-Event-ID", min_length=1, max_length=512),
    ] = None,
) -> StreamingResponse:
    """Poll the durable journal without coupling observer speed to execution."""

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
    cursor = _agent_progress_cursor(
        service_session_id,
        after if after is not None else last_event_id,
    )
    try:
        initial_events = await _bounded_agent_progress_page(
            sessions,
            tenant_id,
            service_session_id,
            after=cursor,
            limit=_AGENT_PROGRESS_STREAM_PAGE_SIZE,
        )
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="agent progress observer timed out",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    async def lines() -> AsyncIterator[str]:
        current = cursor
        events = initial_events
        loop = asyncio.get_running_loop()
        next_heartbeat = loop.time()
        terminal_cursor = not events and await _agent_progress_cursor_references_terminal_attempt(
            sessions,
            tenant_id,
            execution.execution_id,
            execution.state,
            cursor,
        )
        for poll in range(_AGENT_PROGRESS_STREAM_MAX_POLLS):
            if events:
                for event in events:
                    yield json.dumps(jsonable_encoder(event), separators=(",", ":")) + "\n"
                    current = AgentSessionEventCursor.decode(event.cursor)
                next_heartbeat = loop.time() + _AGENT_PROGRESS_STREAM_HEARTBEAT_SECONDS
                if events[-1].frame.activity is AgentProgressActivity.TERMINAL:
                    try:
                        events = await _bounded_agent_progress_page(
                            sessions,
                            tenant_id,
                            service_session_id,
                            after=current,
                            limit=_AGENT_PROGRESS_STREAM_PAGE_SIZE,
                        )
                    except TimeoutError:
                        return
                    if not events:
                        return
                    continue
            elif loop.time() >= next_heartbeat:
                if terminal_cursor:
                    return
                yield (
                    json.dumps(
                        {
                            "type": "heartbeat",
                            "sessionId": str(service_session_id),
                            "cursor": current.encode(),
                        },
                        separators=(",", ":"),
                    )
                    + "\n"
                )
                next_heartbeat = loop.time() + _AGENT_PROGRESS_STREAM_HEARTBEAT_SECONDS
            if poll + 1 >= _AGENT_PROGRESS_STREAM_MAX_POLLS:
                return
            if not events or len(events) < _AGENT_PROGRESS_STREAM_PAGE_SIZE:
                await asyncio.sleep(_AGENT_PROGRESS_STREAM_POLL_SECONDS)
            try:
                events = await _bounded_agent_progress_page(
                    sessions,
                    tenant_id,
                    service_session_id,
                    after=current,
                    limit=_AGENT_PROGRESS_STREAM_PAGE_SIZE,
                )
            except TimeoutError:
                return

    return StreamingResponse(lines(), media_type="application/x-ndjson")


@router_2.get(
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


@router_2.get(
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


@router_2.post(
    "/api/v1/agent-sessions/{service_session_id}/messages",
    response_model=AgentSessionLaunchResponse,
    tags=["agent-sessions"],
)
async def post_agent_session_message(
    service_session_id: UUID,
    request: AgentSessionMessageRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    resources: AgentResourceRepositoryDependency,
    namespace_resources: NamespaceResourceServiceDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-ID")] = None,
) -> AgentSessionLaunchResponse:
    """Append one idempotent input through a new canonical execution turn."""

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
    if execution.trigger.get("ameshActorId") != str(actor.principal_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized")
    await authorize_agent_session_request(
        authorization_service,
        actor,
        action=PermissionAction.CREATE,
        legacy_actions=(PermissionAction.EXECUTE,),
        tenant_id=tenant_id,
        namespace=execution.namespace,
    )
    effective_idempotency_key = _resolve_idempotency_key(
        request.idempotency_key,
        idempotency_key,
    )
    if effective_idempotency_key is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Idempotency-Key is required for an agent-session message",
        )
    message_key_digest = hashlib.sha256(effective_idempotency_key.encode()).hexdigest()
    source_flow = await _agent_session_execution_flow(repository, execution, tenant_id=tenant_id)
    if execution.trigger.get("ameshAgentSessionMessageKeyDigest") == message_key_digest:
        detail = _public_execution_detail(
            source_flow,
            execution,
            await repository.list_task_runs(execution.execution_id, tenant_id=tenant_id),
        )
        return await _agent_session_message_launch_response(
            service_session_id,
            detail,
            response=response,
            sessions=sessions,
            tenant_id=tenant_id,
            prefer=prefer,
            correlation_id=correlation_id,
        )
    if execution.state is not ExecutionState.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="the current agent-session turn must succeed before another message",
        )
    try:
        source_detail = await get_service_agent_session_detail(
            service_session_id,
            sessions=sessions,
            tenant_id=tenant_id,
        )
        source_session = source_detail.session
        if source_session.state is not AgentSessionState.SUCCEEDED:
            raise ValueError("the current agent-session checkpoint is not successful")
        next_flow, agent_key, agent_revision = _agent_session_follow_up_flow(
            source_flow,
            request.input,
        )
        preview = await resources.preview_agent(
            tenant_id,
            execution.namespace,
            agent_key,
            agent_revision=agent_revision,
        )
        Draft202012Validator(preview.envelope.input_schema).validate(request.input)
        images = _agent_session_input_images(request.input)
        if images:
            unsupported_routes = tuple(
                route.route_id
                for route in preview.envelope.model_routes
                if not _agent_session_route_accepts_images(route.required_features)
            )
            if unsupported_routes:
                raise ValueError(
                    "agent session image_input is unsupported by model route(s): "
                    + ", ".join(unsupported_routes)
                )
            for namespace in sorted({image.artifact.namespace for image in images}):
                await authorize_request(
                    authorization_service,
                    actor,
                    resource_type="namespace_file",
                    action=PermissionAction.READ,
                    tenant_id=tenant_id,
                    namespace=namespace,
                )
            for image in images:
                await namespace_resources.resolve_image(
                    image,
                    tenant_id=tenant_id,
                    actor_id=str(actor.principal_id),
                )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except JsonSchemaValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"input does not match the agent schema: {exc.message[:1024]}",
        ) from exc
    except (ValidationError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    source_turn = _agent_session_turn(execution.trigger)
    execution_idempotency_key = f"agent-session:{service_session_id}:message:{message_key_digest}"
    trigger_context = {
        key: execution.trigger[key]
        for key in (
            "ameshAgentRef",
            "ameshApplicationId",
            "ameshActorId",
            "ameshProviderId",
            "ameshHarness",
            "ameshBudget",
            "ameshAgentSessionPolicy",
        )
        if key in execution.trigger
    }
    trigger_context.update(
        {
            "ameshAgentSessionId": str(service_session_id),
            "ameshAgentSessionTurn": source_turn + 1,
            "ameshAgentSessionAttemptBase": source_session.attempt,
            "ameshAgentSessionMessageKeyDigest": message_key_digest,
            "ameshAgentSessionResumeFrom": {
                "sessionId": str(source_session.session_id),
                "taskRunId": str(source_session.task_run_id),
                "attempt": source_session.attempt,
                "capabilityPinId": str(source_session.capability_pin_id),
                "envelopeDigest": source_session.envelope_digest,
            },
        }
    )
    detail = await _execute_flow(
        repository,
        task_cache,
        next_flow,
        CreateExecutionRequest(
            namespace=next_flow.namespace,
            flowId=next_flow.id,
            inputs={},
            runner=RunnerMode.LOCAL,
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
        trigger_context=trigger_context,
        correlation_id=correlation_id,
    )
    return await _agent_session_message_launch_response(
        service_session_id,
        detail,
        response=response,
        sessions=sessions,
        tenant_id=tenant_id,
        prefer=prefer,
        correlation_id=correlation_id,
    )


@router_2.get(
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


@router_2.get(
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


@router_2.get(
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


@router_2.post(
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
    await authorize_agent_session_request(
        authorization_service,
        actor,
        action=PermissionAction.MANAGE,
        legacy_actions=(PermissionAction.MANAGE,),
        tenant_id=tenant_id,
        namespace=execution.namespace,
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
    updated = await _apply_execution_control_authorized(
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


@router_2.post(
    "/api/v1/admin/agent-sessions/actions",
    response_model=AgentSessionBulkActionResponse,
    status_code=status.HTTP_207_MULTI_STATUS,
    tags=["agent-session-administration"],
)
async def bulk_control_agent_sessions(
    request: AgentSessionBulkActionRequest,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentSessionBulkActionResponse:
    """Apply bounded, independently fenced lifecycle controls to agent sessions."""

    # These are deliberately tenant-scoped resource checks.  In particular, do
    # not use authorize_agent_session_request here: its execution-RBAC fallback
    # is retained only for the compatibility period of the individual routes.
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session_administration",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_session",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )

    action_map = {
        "cancel": ExecutionInterventionAction.REQUEST_CANCEL,
        "pause": ExecutionInterventionAction.PAUSE,
        "retry": ExecutionInterventionAction.RESTART,
        "resume": ExecutionInterventionAction.RESUME,
    }
    results: list[AgentSessionBulkActionItemResult] = []
    for index, item in enumerate(request.items):
        try:
            execution = await _get_service_agent_session_execution(
                item.session_id,
                repository=repository,
                sessions=sessions,
                tenant_id=tenant_id,
            )
            detail = await _apply_execution_control_authorized(
                execution.execution_id,
                ExecutionInterventionRequest(
                    action=action_map[request.action],
                    expectedVersion=item.expected_version,
                    expectedEpoch=item.expected_epoch,
                    reason=request.reason,
                ),
                repository,
                actor,
                tenant_id,
            )
        except (HTTPException, LookupError) as exc:
            item_status = exc.status_code if isinstance(exc, HTTPException) else 404
            item_detail = exc.detail if isinstance(exc, HTTPException) else str(exc)
            problem_code = f"HTTP_{item_status}"
            results.append(
                AgentSessionBulkActionItemResult(
                    sessionId=item.session_id,
                    status="rejected",
                    error=ProblemDetail(
                        type=f"urn:amesh:problem:{problem_code.lower()}",
                        title=HTTPStatus(item_status).phrase,
                        status=item_status,
                        detail=item_detail if isinstance(item_detail, str) else str(item_detail),
                        code=problem_code,
                        instance=f"/api/v1/admin/agent-sessions/actions#item-{index}",
                    ),
                )
            )
            continue
        results.append(
            AgentSessionBulkActionItemResult(
                sessionId=item.session_id,
                status="applied",
                execution=detail,
            )
        )

    applied = sum(result.status == "applied" for result in results)
    return AgentSessionBulkActionResponse(
        action=request.action,
        total=len(results),
        applied=applied,
        rejected=len(results) - applied,
        results=results,
    )


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


async def _agent_session_execution_flow(
    repository: RepositoryDependency,
    execution: PersistedExecution,
    *,
    tenant_id: str,
) -> FlowDefinition:
    try:
        return await repository.get_flow(
            execution.namespace,
            execution.flow_id,
            tenant_id=tenant_id,
            revision=execution.flow_revision,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="the agent-session execution flow revision is unavailable",
        ) from exc


def _agent_session_follow_up_flow(
    source_flow: FlowDefinition,
    session_input: dict[str, Any],
) -> tuple[FlowDefinition, str, int]:
    source_task = next(
        (task for task in source_flow.tasks if task.id == "agent" and task.type == "agent.session"),
        None,
    )
    if source_task is None:
        raise ValueError("the agent-session execution has no canonical agent task")
    extra = source_task.configuration
    agent_key = extra.get("agent")
    agent_revision = extra.get("agentRevision")
    if (
        not isinstance(agent_key, str)
        or not agent_key
        or not isinstance(agent_revision, int)
        or isinstance(agent_revision, bool)
        or agent_revision < 1
    ):
        raise ValueError("the agent-session execution has no exact agent revision pin")
    task_payload = source_task.model_dump(mode="python", by_alias=True, exclude_none=True)
    task_payload["input"] = session_input
    follow_up_task = TaskDefinition.model_validate(task_payload)
    return (
        source_flow.model_copy(update={"tasks": [follow_up_task]}),
        agent_key,
        agent_revision,
    )


def _agent_session_input_images(value: object) -> tuple[ImageArtifactRef, ...]:
    if isinstance(value, ImageArtifactRef):
        return (value,)
    if isinstance(value, Mapping):
        if value.get("schemaVersion", value.get("schema_version")) == "amesh.image-ref/v1":
            return (ImageArtifactRef.model_validate(value),)
        return tuple(
            image for item in value.values() for image in _agent_session_input_images(item)
        )
    if isinstance(value, list | tuple):
        return tuple(image for item in value for image in _agent_session_input_images(item))
    return ()


def _agent_session_route_accepts_images(required_features: tuple[str, ...]) -> bool:
    return bool(
        {"image", "image-input", "image_input"}.intersection(
            feature.lower() for feature in required_features
        )
    )


def _agent_session_turn(trigger: Mapping[str, object]) -> int:
    raw_turn = trigger.get("ameshAgentSessionTurn", 1)
    if not isinstance(raw_turn, int) or isinstance(raw_turn, bool) or raw_turn < 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="the agent-session turn mapping is invalid",
        )
    return raw_turn


async def _agent_session_message_launch_response(
    service_session_id: UUID,
    detail: ExecutionDetail,
    *,
    response: Response,
    sessions: AgentSessionRepositoryDependency,
    tenant_id: str,
    prefer: str | None,
    correlation_id: str | None,
) -> AgentSessionLaunchResponse:
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


def _agent_session_tool_dependency_ids(
    envelope: EffectiveCapabilityEnvelope,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                f"{tool.provider_kind.value}:{tool.provider_key}@"
                f"{tool.provider_revision}:{tool.tool_name}"
                for tool in envelope.tools
            }
        )
    )


_AGENT_PROGRESS_MAX_BUFFERED_FRAMES = AgentProgressLimits().max_buffered_frames


_AGENT_PROGRESS_STREAM_PAGE_SIZE = min(100, _AGENT_PROGRESS_MAX_BUFFERED_FRAMES)


_AGENT_PROGRESS_STREAM_POLL_TIMEOUT_SECONDS = 5.0


_AGENT_PROGRESS_STREAM_MAX_POLLS = 30


_AGENT_PROGRESS_STREAM_POLL_SECONDS = 1.0


_AGENT_PROGRESS_STREAM_HEARTBEAT_SECONDS = 5.0


def _agent_progress_cursor(
    service_session_id: UUID,
    token: str | None,
) -> AgentSessionEventCursor:
    if token is None:
        return AgentSessionEventCursor(
            serviceSessionId=service_session_id,
            attemptSessionId=None,
            attempt=0,
            eventIndex=0,
        )
    try:
        cursor = AgentSessionEventCursor.decode(token)
        cursor.require_service_session(service_session_id)
        return cursor
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


async def _bounded_agent_progress_page(
    sessions: AgentSessionRepository,
    tenant_id: str,
    service_session_id: UUID,
    *,
    after: AgentSessionEventCursor,
    limit: int,
) -> tuple[AgentProgressEvent, ...]:
    """Read one bounded observer page without retaining an unbounded queue."""

    return await asyncio.wait_for(
        sessions.list_progress_events(
            tenant_id,
            service_session_id,
            after=after,
            limit=min(limit, _AGENT_PROGRESS_MAX_BUFFERED_FRAMES),
        ),
        timeout=_AGENT_PROGRESS_STREAM_POLL_TIMEOUT_SECONDS,
    )


async def _agent_progress_cursor_references_terminal_attempt(
    sessions: AgentSessionRepository,
    tenant_id: str,
    execution_id: UUID,
    execution_state: ExecutionState,
    cursor: AgentSessionEventCursor,
) -> bool:
    """Classify an empty reconnect cursor without changing the journal read contract."""

    if cursor.attempt == 0 or cursor.attempt_session_id is None:
        return False
    list_sessions = getattr(sessions, "list_execution_sessions", None)
    if not callable(list_sessions):
        return execution_state in {
            ExecutionState.SUCCESS,
            ExecutionState.FAILED,
            ExecutionState.CANCELLED,
        }
    records = await list_sessions(tenant_id, execution_id)
    cursor_record = next(
        (
            record
            for record in records
            if (record.session_id == cursor.attempt_session_id and record.attempt == cursor.attempt)
        ),
        None,
    )
    if cursor_record is None or cursor_record.state is AgentSessionState.RUNNING:
        return False
    return not any(
        record.attempt > cursor.attempt and record.state is AgentSessionState.RUNNING
        for record in records
    )


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
