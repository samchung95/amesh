"""Cohesive system API definitions extracted from the composition root."""

from __future__ import annotations

import asyncio

from fastapi import (
    APIRouter,
    HTTPException,
    Response,
    status,
)
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from amesh import __version__
from amesh.api.dependencies import (
    ActorDependency,
    AuthorizationServiceDependency,
    ServiceRegistryRepositoryDependency,
    SettingsDependency,
    TenantDependency,
    _charge_authorized_tenant_request,
    database_engine,
)
from amesh.api.models import (
    HealthResponse,
    ReadinessResponse,
    UiSessionResponse,
)
from amesh.domain import (
    AuthorizationRequest,
    PermissionAction,
    ServiceLiveness,
    ServiceRole,
    ServiceState,
)
from amesh.entrypoints.preflight import DependencyCondition, run_preflight
from amesh.external_orchestration import (
    ExternalOrchestrationProfile,
    external_orchestration_profile,
)

router_1 = APIRouter()


router_2 = APIRouter()


router_3 = APIRouter()


@router_1.get(
    "/api/v1/orchestration/profile",
    response_model=ExternalOrchestrationProfile,
    tags=["external-orchestration"],
)
async def get_external_orchestration_profile() -> ExternalOrchestrationProfile:
    """Publish the client-neutral contract without exposing tenant data."""

    return external_orchestration_profile()


@router_2.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@router_2.get("/ready", response_model=ReadinessResponse, tags=["system"])
async def ready(
    response: Response,
    settings: SettingsDependency,
    service_registry: ServiceRegistryRepositoryDependency,
) -> ReadinessResponse:
    readiness = await run_preflight(
        settings,
        engine=database_engine(),
        check_storage=settings.readiness_check_storage,
    )
    dependencies = readiness.dependency_states
    registered_ready = True
    role_states = {role.value: "DISABLED" for role in ServiceRole}
    enabled_roles = {ServiceRole(value) for value in settings.service_enabled_roles}
    for role in enabled_roles:
        role_states[role.value] = DependencyCondition.UNAVAILABLE.value
    unready_roles: list[str] = []
    if readiness.ready:
        topology = await service_registry.topology()
        for role in enabled_roles:
            live = tuple(
                instance
                for instance in topology.instances
                if instance.role is role and instance.liveness is ServiceLiveness.LIVE
            )
            if any(instance.state is ServiceState.READY for instance in live):
                role_states[role.value] = ServiceState.READY.value
            elif any(instance.state is ServiceState.DEGRADED for instance in live):
                role_states[role.value] = ServiceState.DEGRADED.value
            elif any(instance.state is ServiceState.DRAINING for instance in live):
                role_states[role.value] = ServiceState.DRAINING.value
            elif live:
                role_states[role.value] = ServiceState.STARTING.value
            else:
                role_states[role.value] = DependencyCondition.UNAVAILABLE.value
            if role_states[role.value] != ServiceState.READY.value:
                unready_roles.append(role.value)
            dependencies[f"role:{role.value}"] = (
                DependencyCondition.READY.value
                if role_states[role.value] == ServiceState.READY.value
                else DependencyCondition.UNAVAILABLE.value
            )
        if settings.service_instance_name is not None:
            registered_ready = any(
                instance.role is ServiceRole.WEBSERVER
                and instance.instance_name == settings.service_instance_name
                and instance.liveness is ServiceLiveness.LIVE
                and instance.state is ServiceState.READY
                for instance in topology.instances
            )
        registered_ready = registered_ready and not unready_roles
        dependencies["service-registry"] = (
            DependencyCondition.READY.value
            if registered_ready
            else DependencyCondition.UNAVAILABLE.value
        )
    if not readiness.ready or not registered_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(
        status=("not-ready" if not readiness.ready or not registered_ready else readiness.status),
        version=__version__,
        database=(
            "ready"
            if dependencies.get("database") == DependencyCondition.READY.value
            else "unavailable"
        ),
        migrations_applied=readiness.migrations_applied,
        migrations_expected=readiness.migrations_expected,
        latest_migration=readiness.latest_migration,
        dependencies=dependencies,
        roles=role_states,
        degraded_dependencies=readiness.degraded_dependencies,
        error=(
            f"enabled service roles not ready: {', '.join(sorted(unready_roles))}"
            if unready_roles
            else "service instance is not ready"
            if not registered_ready
            else readiness.error
        ),
    )


@router_2.get("/api/v1/ui/session", response_model=UiSessionResponse, tags=["ui"])
async def get_ui_session(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
) -> UiSessionResponse:
    requested_capabilities = {
        "assets.view": ("asset", PermissionAction.VIEW),
        "assets.manage": ("asset", PermissionAction.UPDATE),
        "agents.view": ("agent", PermissionAction.VIEW),
        "agents.manage": ("agent", PermissionAction.MANAGE),
        "agents.execute": ("agent", PermissionAction.EXECUTE),
        "flows.view": ("flow", PermissionAction.VIEW),
        "flows.create": ("flow", PermissionAction.CREATE),
        "flows.update": ("flow", PermissionAction.UPDATE),
        "flowTests.view": ("flow_test", PermissionAction.VIEW),
        "flowTests.manage": ("flow_test", PermissionAction.UPDATE),
        "flowTests.execute": ("flow_test", PermissionAction.EXECUTE),
        "executions.view": ("execution", PermissionAction.VIEW),
        "executions.execute": ("execution", PermissionAction.EXECUTE),
        "executions.manage": ("execution", PermissionAction.MANAGE),
        "agentSessions.view": ("agent_session", PermissionAction.VIEW),
        "agentSessions.create": ("agent_session", PermissionAction.CREATE),
        "agentSessions.list": ("agent_session", PermissionAction.LIST),
        "agentSessions.manage": ("agent_session", PermissionAction.MANAGE),
        "agentSessionAdministration.view": (
            "agent_session_administration",
            PermissionAction.VIEW,
        ),
        "agentSessionAdministration.instanceView": (
            "agent_session_administration",
            PermissionAction.VIEW,
        ),
        "agentSessionPolicies.view": ("agent_session_policy", PermissionAction.VIEW),
        "agentSessionPolicies.manage": ("agent_session_policy", PermissionAction.MANAGE),
        "agentSessionMigration.view": (
            "agent_session_migration",
            PermissionAction.VIEW,
        ),
        "agentSessionMigration.manage": (
            "agent_session_migration",
            PermissionAction.MANAGE,
        ),
        "apps.view": ("app", PermissionAction.VIEW),
        "apps.manage": ("app", PermissionAction.UPDATE),
        "apps.execute": ("app", PermissionAction.EXECUTE),
        "humanTasks.view": ("human_task", PermissionAction.VIEW),
        "humanTasks.update": ("human_task", PermissionAction.UPDATE),
        "announcements.view": ("announcement", PermissionAction.VIEW),
        "operationalControls.manage": ("operational_control", PermissionAction.MANAGE),
        "dashboards.view": ("dashboard", PermissionAction.VIEW),
        "dashboards.manage": ("dashboard", PermissionAction.UPDATE),
        "search.view": ("search", PermissionAction.VIEW),
        "search.manage": ("search", PermissionAction.MANAGE),
        "triggers.view": ("trigger", PermissionAction.VIEW),
        "triggers.manage": ("trigger", PermissionAction.MANAGE),
        "checks.view": ("check", PermissionAction.VIEW),
        "checks.manage": ("check", PermissionAction.MANAGE),
        "namespaces.view": ("namespace", PermissionAction.VIEW),
        "namespaceResources.read": ("namespace_file", PermissionAction.LIST),
        "namespaceResources.write": ("namespace_file", PermissionAction.WRITE),
        "secretBindings.write": ("secret", PermissionAction.WRITE),
        "plugins.view": ("plugin", PermissionAction.VIEW),
        "releases.view": ("release", PermissionAction.VIEW),
        "releases.manage": ("release", PermissionAction.MANAGE),
        "administration.manage": ("tenant", PermissionAction.MANAGE),
    }
    decisions = await asyncio.gather(
        *(
            authorization_service.decide(
                AuthorizationRequest(
                    actor=actor,
                    tenant_id=(
                        None
                        if capability == "agentSessionAdministration.instanceView"
                        else tenant_id
                    ),
                    namespace=(
                        None
                        if capability == "agentSessionAdministration.instanceView"
                        else namespace
                    ),
                    resource_type=resource_type,
                    action=action,
                )
            )
            for capability, (resource_type, action) in requested_capabilities.items()
        )
    )
    capabilities = {
        capability: decision.allowed
        for capability, decision in zip(requested_capabilities, decisions, strict=True)
    }
    capabilities["agentSessionAdministration.view"] = (
        capabilities["agentSessionAdministration.view"] and capabilities["agentSessions.list"]
    )
    if not any(capabilities.values()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tenant unavailable",
        )
    await _charge_authorized_tenant_request(tenant_id)
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


@router_3.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
