"""Cohesive catalog API definitions extracted from the composition root."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID

import yaml
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Response,
    status,
)
from fastapi import Path as PathParameter

from amesh.api.dependencies import (
    ActorDependency,
    AuthorizationServiceDependency,
    DashboardRepositoryDependency,
    MetadataRepositoryDependency,
    SearchRepositoryDependency,
    TenantDependency,
    _charge_authorized_tenant_request,
    authorize_request,
)
from amesh.authorization import AuthorizationService
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    DashboardDataSource,
    DashboardDefinition,
    DashboardFilters,
    DashboardQuery,
    DashboardQueryResult,
    DashboardRender,
    DashboardSpec,
    DashboardWidgetResult,
    PermissionAction,
    SearchDocumentType,
    SearchProjectionControlRequest,
    SearchProjectionStatus,
    SearchProjectionVerification,
    SearchRebuildRequest,
    SearchRequest,
    SearchResponse,
)
from amesh.platform import (
    apply_dashboard_filters,
    builtin_dashboard,
    builtin_dashboards,
    can_edit_dashboard,
    can_view_dashboard,
)
from amesh.ports import (
    AssetCatalogEntry,
    AssetCatalogExport,
    AssetLineageDeclaration,
    AssetLineageEdge,
    AssetMetadata,
    AssetObservation,
    AssetObservationCreate,
    MetadataVersionConflict,
    PersistedAsset,
)
from amesh.ports.dashboard_repository import (
    DashboardQueryTimeout,
    DashboardRepository,
    DashboardVersionConflict,
)
from amesh.ports.search_repository import SearchCursorError, SearchUnavailableError

router_1 = APIRouter()


async def _asset_visible(
    asset: PersistedAsset,
    *,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> bool:
    decision = await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=asset.namespace,
            resource_type="asset",
            action=PermissionAction.VIEW,
        )
    )
    return decision.allowed


@router_1.get(
    "/api/v1/assets/export/openlineage",
    response_model=AssetCatalogExport,
    response_model_by_alias=True,
    tags=["assets"],
)
async def export_asset_catalog(
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: Annotated[str | None, Query(max_length=255)] = None,
) -> AssetCatalogExport:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="asset",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await metadata.export_asset_catalog(tenant_id=tenant_id, namespace=namespace)


@router_1.get(
    "/api/v1/assets",
    response_model=tuple[PersistedAsset, ...],
    response_model_by_alias=True,
    tags=["assets"],
)
async def list_assets(
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: Annotated[str | None, Query(max_length=255)] = None,
) -> tuple[PersistedAsset, ...]:
    if namespace is not None:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="asset",
            action=PermissionAction.VIEW,
            tenant_id=tenant_id,
            namespace=namespace,
        )
    assets = tuple(
        asset
        for asset in await metadata.list_assets(tenant_id=tenant_id)
        if namespace is None or asset.namespace == namespace
    )
    visible = await asyncio.gather(
        *(
            _asset_visible(
                asset,
                actor=actor,
                authorization_service=authorization_service,
                tenant_id=tenant_id,
            )
            for asset in assets
        )
    )
    if namespace is None:
        if not assets:
            await authorize_request(
                authorization_service,
                actor,
                resource_type="asset",
                action=PermissionAction.VIEW,
                tenant_id=tenant_id,
            )
        elif any(visible):
            await _charge_authorized_tenant_request(tenant_id)
    return tuple(asset for asset, allowed in zip(assets, visible, strict=True) if allowed)


@router_1.post(
    "/api/v1/assets",
    response_model=PersistedAsset,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    tags=["assets"],
)
async def register_asset(
    payload: AssetMetadata,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> PersistedAsset:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="asset",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=payload.namespace,
    )
    try:
        return await metadata.upsert_asset(
            payload,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except MetadataVersionConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_1.post(
    "/api/v1/assets/observations",
    response_model=AssetObservation,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    tags=["assets"],
)
async def record_asset_observation(
    payload: AssetObservationCreate,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AssetObservation:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="asset",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=payload.asset.namespace,
    )
    return await metadata.record_asset_observation(
        payload,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
    )


@router_1.post(
    "/api/v1/assets/lineage",
    response_model=AssetLineageEdge,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    tags=["assets"],
)
async def declare_asset_lineage(
    payload: AssetLineageDeclaration,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AssetLineageEdge:
    try:
        upstream = await metadata.get_asset(payload.upstream_asset_id, tenant_id=tenant_id)
        downstream = await metadata.get_asset(payload.downstream_asset_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="asset unavailable"
        ) from exc
    for asset in (upstream, downstream):
        await authorize_request(
            authorization_service,
            actor,
            resource_type="asset",
            action=PermissionAction.UPDATE,
            tenant_id=tenant_id,
            namespace=asset.namespace,
        )
    return await metadata.declare_asset_lineage(
        payload,
        tenant_id=tenant_id,
        namespace=downstream.namespace,
        actor_id=str(actor.principal_id),
    )


@router_1.get(
    "/api/v1/assets/{asset_id}",
    response_model=AssetCatalogEntry,
    response_model_by_alias=True,
    tags=["assets"],
)
async def get_asset_catalog_entry(
    asset_id: UUID,
    metadata: MetadataRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AssetCatalogEntry:
    try:
        entry = await metadata.get_asset_catalog_entry(asset_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="asset unavailable"
        ) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="asset",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=entry.asset.namespace,
    )
    neighbors = entry.upstream + entry.downstream
    visibility = await asyncio.gather(
        *(
            _asset_visible(
                asset,
                actor=actor,
                authorization_service=authorization_service,
                tenant_id=tenant_id,
            )
            for asset in neighbors
        )
    )
    visible_ids = {
        asset.asset_id for asset, allowed in zip(neighbors, visibility, strict=True) if allowed
    }
    visible_ids.add(entry.asset.asset_id)
    return entry.model_copy(
        update={
            "upstream": tuple(item for item in entry.upstream if item.asset_id in visible_ids),
            "downstream": tuple(item for item in entry.downstream if item.asset_id in visible_ids),
            "edges": tuple(
                edge
                for edge in entry.edges
                if edge.upstream_asset_id in visible_ids and edge.downstream_asset_id in visible_ids
            ),
        }
    )


_DASHBOARD_DATA_RESOURCES = {
    DashboardDataSource.EXECUTIONS: "execution",
    DashboardDataSource.LOGS: "execution",
    DashboardDataSource.METRICS: "execution",
    DashboardDataSource.SLA: "check",
    DashboardDataSource.WORKERS: "worker",
    DashboardDataSource.ASSETS: "asset",
}


_DASHBOARD_ADMIN_ROLES = {"instance-admin", "tenant-admin", "namespace-admin"}


def _dashboard_admin(decision: AuthorizationDecision, actor: ActorContext) -> bool:
    return actor.bootstrap_admin or bool(
        _DASHBOARD_ADMIN_ROLES.intersection(decision.matched_role_names)
    )


async def _load_dashboard(
    dashboard_id: str,
    *,
    repository: DashboardRepository,
    tenant_id: str,
) -> DashboardDefinition:
    if dashboard_id.startswith("builtin."):
        try:
            return builtin_dashboard(dashboard_id, tenant_id)
        except LookupError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="dashboard unavailable"
            ) from exc
    try:
        return await repository.get_definition(dashboard_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="dashboard unavailable"
        ) from exc


async def _authorize_dashboard_source(
    query: DashboardQuery,
    *,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    tenant_id: str,
) -> AuthorizationDecision:
    return await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=query.filters.namespace,
            resource_type=_DASHBOARD_DATA_RESOURCES[query.source],
            action=PermissionAction.VIEW,
        )
    )


@router_1.get(
    "/api/v1/dashboards",
    response_model=list[DashboardDefinition],
    tags=["dashboards"],
)
async def list_dashboards(
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[DashboardDefinition]:
    decision = await authorize_request(
        authorization_service,
        actor,
        resource_type="dashboard",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    custom = await repository.list_definitions(tenant_id=tenant_id)
    principal_id = str(actor.principal_id)
    visible = [
        definition
        for definition in custom
        if _dashboard_admin(decision, actor) or can_view_dashboard(definition, principal_id)
    ]
    return [*builtin_dashboards(tenant_id), *visible]


@router_1.post(
    "/api/v1/dashboard-queries",
    response_model=DashboardQueryResult,
    tags=["dashboards"],
)
async def execute_dashboard_query(
    query: DashboardQuery,
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> DashboardQueryResult:
    decision = await _authorize_dashboard_source(
        query,
        actor=actor,
        authorization_service=authorization_service,
        tenant_id=tenant_id,
    )
    if not decision.allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="dashboard data unavailable"
        )
    await _charge_authorized_tenant_request(tenant_id)
    try:
        return await repository.execute_query(query, tenant_id=tenant_id)
    except DashboardQueryTimeout as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc


@router_1.get(
    "/api/v1/dashboards/{dashboard_id}",
    response_model=DashboardDefinition,
    tags=["dashboards"],
)
async def get_dashboard(
    dashboard_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> DashboardDefinition:
    decision = await authorize_request(
        authorization_service,
        actor,
        resource_type="dashboard",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    definition = await _load_dashboard(dashboard_id, repository=repository, tenant_id=tenant_id)
    if not _dashboard_admin(decision, actor) and not can_view_dashboard(
        definition, str(actor.principal_id)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dashboard unavailable")
    return definition


@router_1.post(
    "/api/v1/dashboards/{dashboard_id}/render",
    response_model=DashboardRender,
    tags=["dashboards"],
)
async def render_dashboard(
    dashboard_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    filters: DashboardFilters,
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> DashboardRender:
    definition = await get_dashboard(
        dashboard_id,
        repository,
        actor,
        authorization_service,
        tenant_id,
    )
    widget_results: list[DashboardWidgetResult] = []
    for widget in definition.widgets:
        query = apply_dashboard_filters(widget.query, filters)
        decision = await _authorize_dashboard_source(
            query,
            actor=actor,
            authorization_service=authorization_service,
            tenant_id=tenant_id,
        )
        if not decision.allowed:
            result = DashboardQueryResult(
                columns=(),
                rows=(),
                freshAt=datetime.now(UTC),
                partial=False,
                sampled=query.sample_rate < 1,
                redacted=True,
                scannedRows=0,
                limit=query.limit,
            )
        else:
            try:
                result = await repository.execute_query(query, tenant_id=tenant_id)
            except DashboardQueryTimeout as exc:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"widget {widget.widget_id}: {exc}",
                ) from exc
        widget_results.append(DashboardWidgetResult(widgetId=widget.widget_id, result=result))
    return DashboardRender(dashboard=definition, widgets=tuple(widget_results))


@router_1.put(
    "/api/v1/dashboards/{dashboard_id}",
    response_model=DashboardDefinition,
    tags=["dashboards"],
)
async def put_dashboard(
    dashboard_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    spec: DashboardSpec,
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> DashboardDefinition:
    decision = await authorize_request(
        authorization_service,
        actor,
        resource_type="dashboard",
        action=PermissionAction.CREATE if expected_version is None else PermissionAction.UPDATE,
        tenant_id=tenant_id,
    )
    if dashboard_id.startswith("builtin.") or spec.source.value == "BUILTIN":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="built-in dashboards are immutable",
        )
    if expected_version is not None:
        existing = await _load_dashboard(dashboard_id, repository=repository, tenant_id=tenant_id)
        if not _dashboard_admin(decision, actor) and not can_edit_dashboard(
            existing, str(actor.principal_id)
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="dashboard unavailable"
            )
    try:
        return await repository.upsert_definition(
            dashboard_id,
            spec,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except DashboardVersionConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_1.delete(
    "/api/v1/dashboards/{dashboard_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["dashboards"],
)
async def delete_dashboard(
    dashboard_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int, Query(alias="expectedVersion", ge=1)],
) -> Response:
    decision = await authorize_request(
        authorization_service,
        actor,
        resource_type="dashboard",
        action=PermissionAction.DELETE,
        tenant_id=tenant_id,
    )
    definition = await _load_dashboard(dashboard_id, repository=repository, tenant_id=tenant_id)
    if not _dashboard_admin(decision, actor) and not can_edit_dashboard(
        definition, str(actor.principal_id)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dashboard unavailable")
    try:
        await repository.delete_definition(
            dashboard_id,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except DashboardVersionConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router_1.get("/api/v1/dashboards/{dashboard_id}/export", tags=["dashboards"])
async def export_dashboard(
    dashboard_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    repository: DashboardRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    format: Literal["yaml", "json"] = "yaml",
) -> Response:
    definition = await get_dashboard(
        dashboard_id,
        repository,
        actor,
        authorization_service,
        tenant_id,
    )
    payload = definition.model_dump(mode="json", by_alias=True)
    if format == "json":
        content = json.dumps(payload, indent=2, sort_keys=True)
        media_type = "application/json"
        suffix = "json"
    else:
        content = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
        media_type = "application/yaml"
        suffix = "yaml"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{dashboard_id}.{suffix}"'},
    )


_SEARCH_DATA_RESOURCES = {
    SearchDocumentType.FLOW: "flow",
    SearchDocumentType.EXECUTION: "execution",
    SearchDocumentType.TASK_RUN: "execution",
    SearchDocumentType.LOG: "execution",
    SearchDocumentType.METRIC: "execution",
    SearchDocumentType.ASSET: "asset",
    SearchDocumentType.AUDIT: "audit",
}


@router_1.post("/api/v1/search", response_model=SearchResponse, tags=["search"])
async def search_resources(
    request: SearchRequest,
    repository: SearchRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SearchResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="search",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=request.namespace,
    )
    requested_types = request.types or tuple(SearchDocumentType)
    decisions = await asyncio.gather(
        *(
            authorization_service.decide(
                AuthorizationRequest(
                    actor=actor,
                    tenant_id=tenant_id,
                    namespace=request.namespace,
                    resource_type=_SEARCH_DATA_RESOURCES[document_type],
                    action=PermissionAction.VIEW,
                )
            )
            for document_type in requested_types
        )
    )
    authorized = tuple(
        document_type
        for document_type, decision in zip(requested_types, decisions, strict=True)
        if decision.allowed
    )
    denied = tuple(
        document_type
        for document_type, decision in zip(requested_types, decisions, strict=True)
        if not decision.allowed
    )
    try:
        return await repository.search(
            request,
            tenant_id=tenant_id,
            authorized_types=authorized,
            denied_types=denied,
        )
    except SearchCursorError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SearchUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router_1.get(
    "/api/v1/search/status",
    response_model=SearchProjectionStatus,
    tags=["search"],
)
async def get_search_status(
    repository: SearchRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SearchProjectionStatus:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="search",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return await repository.status(tenant_id=tenant_id)
    except SearchUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router_1.post(
    "/api/v1/search/rebuild",
    response_model=SearchProjectionStatus,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["search"],
)
async def rebuild_search_projection(
    request: SearchRebuildRequest,
    repository: SearchRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SearchProjectionStatus:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="search",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.request_rebuild(
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            reason=request.reason,
            document_types=request.types,
            from_time=request.from_time,
            to_time=request.to_time,
        )
    except SearchUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router_1.get(
    "/api/v1/search/verify",
    response_model=SearchProjectionVerification,
    tags=["search"],
)
async def verify_search_projection(
    repository: SearchRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SearchProjectionVerification:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="search",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.verify(tenant_id=tenant_id)
    except SearchUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router_1.post(
    "/api/v1/search/control",
    response_model=SearchProjectionStatus,
    tags=["search"],
)
async def control_search_projection(
    request: SearchProjectionControlRequest,
    repository: SearchRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SearchProjectionStatus:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="search",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.set_enabled(
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            enabled=request.enabled,
            reason=request.reason,
        )
    except SearchUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
