"""Cohesive operations API definitions extracted from the composition root."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from amesh.adapters.docker import DockerContainerRunner
from amesh.adapters.kubernetes import KubernetesJobRunner
from amesh.adapters.local import LocalProcessRunner
from amesh.adapters.postgres.operational_control_repository import (
    OperationalControlVersionConflict,
)
from amesh.api.contracts import (
    CollectionQuery,
    collection_response,
    default_limited_collection_query,
)
from amesh.api.dependencies import (
    ActorDependency,
    AuthorizationServiceDependency,
    BackfillRepositoryDependency,
    BackfillServiceDependency,
    OperationalControlRepositoryDependency,
    ReconciliationServiceDependency,
    RepositoryDependency,
    RetentionRepositoryDependency,
    RetentionServiceDependency,
    ServiceRegistryRepositoryDependency,
    SettingsDependency,
    TenantDependency,
    UpgradeRepositoryDependency,
    UpgradeServiceDependency,
    WorkerRepositoryDependency,
    authorize_request,
)
from amesh.api.models import (
    BackfillActionRequest,
)
from amesh.authorization import AuthorizationService
from amesh.domain import (
    ActorContext,
    AdmissionDiagnostics,
    Announcement,
    AnnouncementAudience,
    AnnouncementCreateRequest,
    BackfillPreview,
    BackfillRecord,
    BackfillSpec,
    BackfillState,
    ConfigurationMigration,
    ConfigurationMigrationRequest,
    OperationalControl,
    OperationalControlActionRequest,
    OperationalControlCreateRequest,
    OperationalControlEvent,
    OperationalControlScope,
    PermissionAction,
    PersistedEventMigration,
    PersistedEventMigrationRequest,
    ReconciliationRequest,
    ReconciliationRun,
    ServiceDrainRequest,
    ServiceInstance,
    ServiceTopology,
    UpgradePolicy,
    UpgradeReport,
    UpgradeReportRequest,
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
from amesh.networking import (
    NetworkDiagnosticBundle,
    build_network_diagnostics,
)
from amesh.observability import (
    ADMISSION_PRESSURE,
)
from amesh.ports import (
    BackfillRepository,
    LifecycleVersionConflict,
    ReconciliationAlreadyRunningError,
    RunnerCapabilities,
    ServiceFenceError,
    TenantQuotaExceeded,
    WorkerFenceError,
    WorkerInventory,
)

router_1 = APIRouter()


router_2 = APIRouter()


router_3 = APIRouter()


@router_1.get(
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


@router_2.get(
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


@router_2.post(
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


@router_2.delete(
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


@router_2.get(
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


@router_2.post(
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


@router_2.post(
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


@router_2.get(
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


@router_3.get(
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


@router_3.post("/api/v1/admissions/reconcile", tags=["operations"])
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


@router_3.post(
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


@router_3.get(
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


@router_3.get(
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


@router_3.get(
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


@router_3.post(
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


@router_3.put(
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
    except (LifecycleVersionConflict, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_3.get(
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


@router_3.post(
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


@router_3.post(
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


@router_3.post(
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


@router_3.get(
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


@router_3.get(
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


@router_3.post(
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


@router_3.post(
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


@router_3.get(
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


@router_3.post(
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


@router_3.post(
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


@router_3.get(
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


@router_3.post(
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


@router_3.post(
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


@router_3.get(
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


@router_3.post(
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


@router_3.post(
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


@router_3.post(
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


@router_3.get(
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


@router_3.get(
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
    repository: BackfillRepository,
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


@router_3.post(
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


@router_3.post(
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


@router_3.post(
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


@router_3.get(
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


@router_3.get(
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


@router_3.post(
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
