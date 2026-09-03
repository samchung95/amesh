"""Cohesive agents API definitions extracted from the composition root."""

from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from amesh.api.dependencies import (
    ActorDependency,
    AgentMemoryRepositoryDependency,
    AgentPrimitiveRepositoryDependency,
    AgentResourceRepositoryDependency,
    AuditRepositoryDependency,
    AuthorizationServiceDependency,
    SelfHostedPluginRegistryDependency,
    SettingsDependency,
    SharedResourceRepositoryDependency,
    TenantDependency,
    _charge_authorized_tenant_request,
    authorize_request,
)
from amesh.api.http import (
    LOGGER,
)
from amesh.api.models import (
    McpConnectionDiscoveryRequest,
    McpConnectionTestPin,
    McpConnectionTestRequest,
    McpConnectionTestResponse,
    McpConnectionTestStatus,
)
from amesh.application import (
    build_http_task_policy,
)
from amesh.authorization import AuthorizationService
from amesh.capability_catalog import (
    CapabilityCatalog,
    CapabilityKind,
    CapabilitySource,
    CapabilitySourceAccess,
    CapabilitySourceAccessStatus,
    CapabilityStatus,
    build_capability_catalog,
    filter_capability_catalog,
)
from amesh.config import (
    Settings,
)
from amesh.domain import (
    ActorContext,
    AgentCapabilityPin,
    AgentEnvelopePreview,
    AgentEvaluationPreview,
    AgentEvaluationSpec,
    AgentMemoryMetadata,
    AgentResolutionRequest,
    AgentResourceKind,
    AgentResourceRevision,
    AgentResourceSpec,
    AgentRevisionComparison,
    AgentRouteDecision,
    AgentRouteRequest,
    AuthorizationRequest,
    McpConnectionRevision,
    McpConnectionSpec,
    McpDiscoveryResult,
    ModelPolicySpec,
    PermissionAction,
    ProviderMigrationDiagnostic,
    compare_agent_revisions,
    evaluate_deterministic_output,
    provider_migration_diagnostic,
    route_agent,
)
from amesh.plugin_sdk import (
    PluginRegistryPackage,
)
from amesh.ports import (
    AgentResourceRepository,
    SharedResourceRepository,
)
from amesh.tasks import (
    HttpTaskPolicy,
    discover_mcp_server,
)

router_1 = APIRouter()


def _agent_outbound_policy(settings: Settings) -> HttpTaskPolicy:
    return build_http_task_policy(settings)


async def _agent_secret_value(
    namespace: str,
    credential_ref: str,
    *,
    repository: SharedResourceRepository,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> str:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="secret_binding",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        binding = await repository.get_secret_binding(
            namespace,
            credential_ref,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="credential binding unavailable",
        ) from exc
    credential = os.environ.get(binding.provider_reference)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="credential provider reference unavailable",
        )
    return credential


async def _discover_agent_mcp(
    request: McpConnectionDiscoveryRequest,
    namespace: str,
    *,
    shared_resources: SharedResourceRepository,
    settings: Settings,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> McpDiscoveryResult:
    credential = await _agent_secret_value(
        namespace,
        request.credential_ref,
        repository=shared_resources,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
    )
    try:
        return await discover_mcp_server(
            request.endpoint,
            credential,
            timeout_seconds=request.timeout_seconds,
            http_policy=_agent_outbound_policy(settings),
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        LOGGER.warning(
            "MCP discovery failed",
            extra={"namespace": namespace, "endpoint": request.endpoint},
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="MCP discovery failed",
        ) from exc


@router_1.post(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections/discover",
    response_model=McpDiscoveryResult,
    tags=["agents"],
)
async def discover_agent_mcp_connection(
    namespace: str,
    request: McpConnectionDiscoveryRequest,
    shared_resources: SharedResourceRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> McpDiscoveryResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.CREATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await _discover_agent_mcp(
        request,
        namespace,
        shared_resources=shared_resources,
        settings=settings,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
    )


@router_1.post(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections",
    response_model=McpConnectionRevision,
    status_code=status.HTTP_201_CREATED,
    tags=["agents"],
)
async def create_agent_mcp_connection_revision(
    namespace: str,
    spec: McpConnectionSpec,
    repository: AgentPrimitiveRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> McpConnectionRevision:
    if spec.namespace != namespace:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="connection namespace must match the route namespace",
        )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    discovery = await _discover_agent_mcp(
        McpConnectionDiscoveryRequest(
            endpoint=spec.endpoint,
            credentialRef=spec.credential_ref,
        ),
        namespace,
        shared_resources=shared_resources,
        settings=settings,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
    )
    live_tools = {tool.name: tool.schema_digest for tool in discovery.tools}
    pinned_tools = {tool.name: tool.schema_digest for tool in spec.tools}
    if any(live_tools.get(name) != digest for name, digest in pinned_tools.items()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="MCP tool schemas changed after discovery",
        )
    return await repository.save_mcp_connection(
        tenant_id,
        spec,
        actor_id=str(actor.principal_id),
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections",
    response_model=list[McpConnectionRevision],
    tags=["agents"],
)
async def list_agent_mcp_connections(
    namespace: str,
    repository: AgentPrimitiveRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[McpConnectionRevision]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(await repository.list_mcp_connections(tenant_id, namespace))


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections/{key}",
    response_model=McpConnectionRevision,
    tags=["agents"],
)
async def get_agent_mcp_connection(
    namespace: str,
    key: str,
    repository: AgentPrimitiveRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> McpConnectionRevision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.get_mcp_connection(
            tenant_id,
            namespace,
            key,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP connection unavailable",
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/tools",
    response_model=list[dict[str, object]],
    tags=["agents"],
)
async def list_agent_mcp_connection_tools(
    namespace: str,
    key: str,
    repository: AgentPrimitiveRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> list[dict[str, object]]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        connection = await repository.get_mcp_connection(
            tenant_id,
            namespace,
            key,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP connection unavailable",
        ) from exc
    return [
        {
            "connectionKey": connection.spec.key,
            "connectionRevision": connection.revision,
            "connectionDigest": connection.digest,
            "credentialRef": connection.spec.credential_ref,
            "endpoint": connection.spec.endpoint,
            "toolName": tool.name,
            "description": tool.description,
            "schemaDigest": tool.schema_digest,
            "impact": tool.impact.value,
        }
        for tool in connection.spec.tools
    ]


@router_1.post(
    "/api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/test",
    response_model=McpConnectionTestResponse,
    tags=["agents"],
)
async def test_agent_mcp_connection(
    namespace: str,
    key: str,
    request: McpConnectionTestRequest,
    repository: AgentPrimitiveRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    settings: SettingsDependency,
    audit_repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> McpConnectionTestResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent_connection",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        connection = await repository.get_mcp_connection(
            tenant_id,
            namespace,
            key,
            revision=request.revision,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP connection unavailable",
        ) from exc

    observed_digest: str | None
    diagnostic: str | None
    try:
        discovery = await _discover_agent_mcp(
            McpConnectionDiscoveryRequest(
                endpoint=connection.spec.endpoint,
                credentialRef=connection.spec.credential_ref,
                timeoutSeconds=request.timeout_seconds,
            ),
            namespace,
            shared_resources=shared_resources,
            settings=settings,
            actor=actor,
            authorization_service=authorization_service,
            tenant_id=tenant_id,
        )
    except HTTPException as exc:
        if exc.status_code in {
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        }:
            raise
        result_status = McpConnectionTestStatus.UNAVAILABLE
        observed_digest = None
        checked_tool_count = 0
        diagnostic = (
            "The MCP server could not be discovered under the configured network, "
            "credential, and timeout policy."
        )
    else:
        live_tools = {tool.name: tool.schema_digest for tool in discovery.tools}
        schema_drift = any(
            live_tools.get(tool.name) != tool.schema_digest for tool in connection.spec.tools
        )
        result_status = (
            McpConnectionTestStatus.SCHEMA_DRIFT if schema_drift else McpConnectionTestStatus.PASSED
        )
        observed_digest = discovery.digest
        checked_tool_count = len(connection.spec.tools)
        diagnostic = (
            "One or more pinned MCP tool schemas changed or disappeared; rediscover "
            "the server and save a new immutable connection revision."
            if schema_drift
            else None
        )

    evidence_id = await audit_repository.record_connection_test(
        tenant_id,
        actor_id=str(actor.principal_id),
        connection_key=connection.spec.key,
        connection_revision=connection.revision,
        connection_digest=connection.digest,
        status=result_status.value,
        observed_digest=observed_digest,
        checked_tool_count=checked_tool_count,
        diagnostic=diagnostic,
    )
    return McpConnectionTestResponse(
        status=result_status,
        evidenceId=evidence_id,
        connectionPin=McpConnectionTestPin(
            key=connection.spec.key,
            revision=connection.revision,
            digest=connection.digest,
        ),
        observedDigest=observed_digest,
        checkedToolCount=checked_tool_count,
        diagnostic=diagnostic,
    )


async def _capability_source_access(
    authorization_service: AuthorizationService,
    actor: ActorContext,
    *,
    source: CapabilitySource,
    resource_type: str,
    tenant_id: str,
    namespace: str | None,
) -> tuple[bool, CapabilitySourceAccess]:
    try:
        decision = await authorization_service.decide(
            AuthorizationRequest(
                actor=actor,
                tenant_id=tenant_id,
                namespace=namespace,
                resource_type=resource_type,
                action=PermissionAction.VIEW,
            )
        )
    except Exception:
        LOGGER.exception("Capability catalog authorization source unavailable")
        return False, CapabilitySourceAccess(
            source=source,
            status=CapabilitySourceAccessStatus.UNAVAILABLE,
            diagnostics=("Authorization policy could not evaluate this source.",),
        )
    if not decision.allowed:
        return False, CapabilitySourceAccess(
            source=source,
            status=CapabilitySourceAccessStatus.DENIED,
            diagnostics=("This source is not authorized for the current principal.",),
        )
    return True, CapabilitySourceAccess(
        source=source,
        status=CapabilitySourceAccessStatus.ALLOWED,
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/capabilities/catalog",
    response_model=CapabilityCatalog,
    tags=["agents"],
)
async def get_agent_capability_catalog(
    namespace: str,
    resource_repository: AgentResourceRepositoryDependency,
    primitive_repository: AgentPrimitiveRepositoryDependency,
    registry: SelfHostedPluginRegistryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    query: Annotated[str | None, Query(alias="q", min_length=1, max_length=255)] = None,
    kinds: Annotated[list[CapabilityKind] | None, Query(alias="kind")] = None,
    statuses: Annotated[list[CapabilityStatus] | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
) -> CapabilityCatalog:
    source_specs = (
        (CapabilitySource.AGENTS, "agent", namespace),
        (CapabilitySource.CONNECTIONS, "agent_connection", namespace),
        (CapabilitySource.PLUGINS, "plugin", None),
    )
    access: dict[CapabilitySource, CapabilitySourceAccess] = {}
    allowed: dict[CapabilitySource, bool] = {}
    for source, resource_type, source_namespace in source_specs:
        allowed[source], access[source] = await _capability_source_access(
            authorization_service,
            actor,
            source=source,
            resource_type=resource_type,
            tenant_id=tenant_id,
            namespace=source_namespace,
        )
    if any(allowed.values()):
        await _charge_authorized_tenant_request(tenant_id)

    agent_resources: tuple[AgentResourceRevision, ...] = ()
    connections: tuple[McpConnectionRevision, ...] = ()
    plugin_packages: tuple[PluginRegistryPackage, ...] = ()
    try:
        if allowed[CapabilitySource.AGENTS]:
            agent_resources = await resource_repository.list_resources(
                tenant_id,
                namespace,
            )
    except Exception:
        LOGGER.exception("Capability catalog agent resource source unavailable")
        access[CapabilitySource.AGENTS] = CapabilitySourceAccess(
            source=CapabilitySource.AGENTS,
            status=CapabilitySourceAccessStatus.UNAVAILABLE,
            diagnostics=("Agent resources are temporarily unavailable.",),
        )
    try:
        if allowed[CapabilitySource.CONNECTIONS]:
            connections = await primitive_repository.list_mcp_connections(
                tenant_id,
                namespace,
            )
    except Exception:
        LOGGER.exception("Capability catalog connection source unavailable")
        access[CapabilitySource.CONNECTIONS] = CapabilitySourceAccess(
            source=CapabilitySource.CONNECTIONS,
            status=CapabilitySourceAccessStatus.UNAVAILABLE,
            diagnostics=("MCP connections are temporarily unavailable.",),
        )
    try:
        if allowed[CapabilitySource.PLUGINS]:
            plugin_packages = registry.snapshot().packages
    except Exception:
        LOGGER.exception("Capability catalog plugin source unavailable")
        access[CapabilitySource.PLUGINS] = CapabilitySourceAccess(
            source=CapabilitySource.PLUGINS,
            status=CapabilitySourceAccessStatus.UNAVAILABLE,
            diagnostics=("Plugin packages are temporarily unavailable.",),
        )

    catalog = build_capability_catalog(
        agent_resources,
        connections,
        plugin_packages,
        namespace=namespace,
        source_access=(access[source] for source in CapabilitySource),
    )
    return filter_capability_catalog(
        catalog,
        query=query,
        kinds=kinds or (),
        statuses=statuses or (),
        limit=limit,
    )


@router_1.post(
    "/api/v1/namespaces/{namespace}/agent/resources",
    response_model=AgentResourceRevision,
    status_code=status.HTTP_201_CREATED,
    tags=["agents"],
)
async def create_agent_resource_revision(
    namespace: str,
    spec: AgentResourceSpec,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentResourceRevision:
    if spec.namespace != namespace:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resource namespace must match the route namespace",
        )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.save_resource(
        tenant_id,
        spec,
        actor_id=str(actor.principal_id),
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/resources",
    response_model=list[AgentResourceRevision],
    tags=["agents"],
)
async def list_agent_resources(
    namespace: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    kind: AgentResourceKind | None = None,
) -> list[AgentResourceRevision]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(await repository.list_resources(tenant_id, namespace, kind=kind))


async def _agent_resource_or_404(
    repository: AgentResourceRepository,
    tenant_id: str,
    namespace: str,
    kind: AgentResourceKind,
    key: str,
    revision: int | None,
) -> AgentResourceRevision:
    try:
        return await repository.get_resource(
            tenant_id,
            namespace,
            kind,
            key,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="agent resource unavailable",
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/resources/{kind}/{key}",
    response_model=AgentResourceRevision,
    tags=["agents"],
)
async def get_agent_resource(
    namespace: str,
    kind: AgentResourceKind,
    key: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> AgentResourceRevision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        kind,
        key,
        revision,
    )


@router_1.post(
    "/api/v1/namespaces/{namespace}/agent/definitions/{key}/resolve",
    response_model=AgentCapabilityPin,
    tags=["agents"],
)
async def resolve_agent_definition(
    namespace: str,
    key: str,
    request: AgentResolutionRequest,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentCapabilityPin:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.resolve_agent(
            tenant_id,
            namespace,
            key,
            request,
            actor_id=str(actor.principal_id),
        )
    except (LookupError, PermissionError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/definitions/{key}/preview",
    response_model=AgentEnvelopePreview,
    tags=["agents"],
)
async def preview_agent_definition(
    namespace: str,
    key: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    agent_revision: Annotated[int, Query(alias="agentRevision", ge=1)],
) -> AgentEnvelopePreview:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.preview_agent(
            tenant_id,
            namespace,
            key,
            agent_revision=agent_revision,
        )
    except (LookupError, PermissionError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router_1.post(
    "/api/v1/namespaces/{namespace}/agent/mesh/routes/preview",
    response_model=AgentRouteDecision,
    tags=["agents"],
)
async def preview_agent_mesh_route(
    namespace: str,
    request: AgentRouteRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentRouteDecision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return route_agent(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/evaluations/{key}/fixtures/{fixture_key}/preview",
    response_model=AgentEvaluationPreview,
    tags=["agents"],
)
async def preview_agent_evaluation_fixture(
    namespace: str,
    key: str,
    fixture_key: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int, Query(ge=1)],
) -> AgentEvaluationPreview:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    resource = await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        AgentResourceKind.EVALUATION,
        key,
        revision,
    )
    if not isinstance(resource.spec, AgentEvaluationSpec):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="resource is not an evaluation",
        )
    fixture = next(
        (item for item in resource.spec.fixtures if item.key == fixture_key),
        None,
    )
    if fixture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="evaluation fixture unavailable",
        )
    return AgentEvaluationPreview(
        evaluationKey=resource.key,
        evaluationRevision=resource.revision,
        fixtureKey=fixture.key,
        input=fixture.input,
        recordedOutput=fixture.recorded_output,
        deterministic=evaluate_deterministic_output(
            resource.spec,
            fixture.recorded_output,
        ),
        judgeRequired=resource.spec.judge is not None,
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/memory",
    response_model=list[AgentMemoryMetadata],
    tags=["agents"],
)
async def list_agent_memory_metadata(
    namespace: str,
    repository: AgentMemoryRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    agent_key: Annotated[str | None, Query(alias="agentKey")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[AgentMemoryMetadata]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(
        await repository.list_metadata(
            tenant_id,
            namespace,
            agent_key=agent_key,
            limit=limit,
        )
    )


@router_1.delete(
    "/api/v1/namespaces/{namespace}/agent/memory/{entry_id}",
    response_model=AgentMemoryMetadata,
    tags=["agents"],
)
async def delete_agent_memory_entry(
    namespace: str,
    entry_id: UUID,
    repository: AgentMemoryRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AgentMemoryMetadata:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        metadata = await repository.delete(
            tenant_id,
            namespace,
            entry_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="agent memory entry unavailable",
        ) from exc
    return metadata


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/definitions/{key}/compare",
    response_model=AgentRevisionComparison,
    tags=["agents"],
)
async def compare_agent_definition_revisions(
    namespace: str,
    key: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    from_revision: Annotated[int, Query(alias="fromRevision", ge=1)],
    to_revision: Annotated[int, Query(alias="toRevision", ge=1)],
) -> AgentRevisionComparison:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    previous = await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        AgentResourceKind.AGENT,
        key,
        from_revision,
    )
    current = await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        AgentResourceKind.AGENT,
        key,
        to_revision,
    )
    return compare_agent_revisions(previous, current)


@router_1.get(
    "/api/v1/namespaces/{namespace}/agent/model-policies/{key}/migration",
    response_model=ProviderMigrationDiagnostic,
    tags=["agents"],
)
async def diagnose_model_policy_migration(
    namespace: str,
    key: str,
    repository: AgentResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    from_revision: Annotated[int, Query(alias="fromRevision", ge=1)],
    to_revision: Annotated[int, Query(alias="toRevision", ge=1)],
) -> ProviderMigrationDiagnostic:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="agent",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    previous = await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        AgentResourceKind.MODEL_POLICY,
        key,
        from_revision,
    )
    current = await _agent_resource_or_404(
        repository,
        tenant_id,
        namespace,
        AgentResourceKind.MODEL_POLICY,
        key,
        to_revision,
    )
    if not isinstance(previous.spec, ModelPolicySpec) or not isinstance(
        current.spec,
        ModelPolicySpec,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="model-policy revisions have incompatible resource kinds",
        )
    return provider_migration_diagnostic(previous.spec, current.spec)
