"""Session administration HTTP routes."""

from __future__ import annotations

from http import HTTPStatus
from typing import Annotated, Literal, NoReturn
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from amesh.api.dependencies import (
    ActorDependency,
    AgentSessionFleetRepositoryDependency,
    AgentSessionPolicyRepositoryDependency,
    AgentSessionRepositoryDependency,
    AuthorizationServiceDependency,
    ProfileTransferServiceDependency,
    RepositoryDependency,
    TenantDependency,
    TransferRepositoryDependency,
    authorize_agent_session_request,
    authorize_request,
    require_namespace_permission,
)
from amesh.api.models import (
    AgentSessionBulkActionItemResult,
    AgentSessionBulkActionRequest,
    AgentSessionBulkActionResponse,
    AgentSessionControlRequest,
    AgentSessionLaunchResponse,
    AgentSessionPolicyUpsertRequest,
    AgentSessionTransferProfileImportRequest,
    AgentSessionTransferProfilePlanRequest,
    AgentSessionTransferSessionExportRequest,
    AgentSessionTransferSessionImportRequest,
    AgentSessionTransferSessionPlanRequest,
    ExecutionInterventionRequest,
    ProblemDetail,
)
from amesh.api.route_support import (
    _apply_execution_control_authorized,
    _get_service_agent_session_execution,
    _public_agent_session_detail,
    get_service_agent_session_detail,
)
from amesh.domain import (
    ActorContext,
    AgentSessionFleetPage,
    AgentSessionFleetQuery,
    AgentSessionInstanceAggregate,
    AgentSessionPolicyRevision,
    PermissionAction,
)
from amesh.ports import (
    AgentSessionFleetCursorError,
    AgentSessionPolicyVersionConflict,
    ExecutionInterventionAction,
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

router_1 = APIRouter()
router_2 = APIRouter()
router_3 = APIRouter()


def _validate_agent_session_policy_identity(
    namespace: str | None,
    application_id: str | None,
) -> None:
    if application_id is not None and namespace is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="applicationId requires namespace",
        )


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
    actor: Annotated[
        ActorContext,
        Depends(require_namespace_permission("agent_session_migration", PermissionAction.VIEW)),
    ],
    tenant_id: TenantDependency,
) -> ProfileBundle:
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


@router_3.post(
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


@router_3.post(
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
