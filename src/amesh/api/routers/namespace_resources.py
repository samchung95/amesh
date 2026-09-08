"""Namespace resources HTTP routes."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from starlette.responses import StreamingResponse

from amesh.api.dependencies import (
    ActorDependency,
    AuthorizationServiceDependency,
    NamespaceResourceServiceDependency,
    SharedResourceRepositoryDependency,
    TenantDependency,
    authorize_request,
    require_namespace_permission,
)
from amesh.api.models import (
    NamespaceFileMoveRequest,
    NamespaceResourceImportResult,
)
from amesh.domain import (
    ActorContext,
    ArtifactRef,
    ImageArtifactRef,
    KeyValueChange,
    KeyValueEntry,
    KeyValueWrite,
    NamespaceFile,
    NamespaceFileVersion,
    NamespaceResourceBundle,
    PermissionAction,
    ResourceVersionConflict,
    SecretBinding,
    SecretBindingWrite,
)

router_1 = APIRouter()


@router_1.get(
    "/api/v1/namespaces/{namespace}/files",
    response_model=list[NamespaceFile],
    tags=["namespace-resources"],
)
async def list_namespace_files(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("namespace_file", PermissionAction.LIST))
    ],
    tenant_id: TenantDependency,
    inherited: bool = True,
) -> list[NamespaceFile]:
    return await repository.list_files(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        inherited=inherited,
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/artifacts",
    response_model=list[ArtifactRef],
    tags=["namespace-resources"],
)
async def list_namespace_artifacts(
    namespace: str,
    service: NamespaceResourceServiceDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("namespace_file", PermissionAction.LIST))
    ],
    tenant_id: TenantDependency,
    inherited: bool = True,
) -> list[ArtifactRef]:
    return await service.list_artifacts(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        inherited=inherited,
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/artifacts/{path:path}",
    response_model=ArtifactRef,
    tags=["namespace-resources"],
)
async def get_namespace_artifact(
    namespace: str,
    path: str,
    service: NamespaceResourceServiceDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("namespace_file", PermissionAction.READ))
    ],
    tenant_id: TenantDependency,
    version: Annotated[int | None, Query(ge=1)] = None,
) -> ArtifactRef:
    try:
        return await service.get_artifact(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            version=version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router_1.put(
    "/api/v1/namespaces/{namespace}/images/{path:path}",
    response_model=ImageArtifactRef,
    tags=["namespace-resources"],
)
async def upload_namespace_image(
    namespace: str,
    path: str,
    request: Request,
    service: NamespaceResourceServiceDependency,
    actor: Annotated[
        ActorContext,
        Depends(require_namespace_permission("namespace_file", PermissionAction.WRITE)),
    ],
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=0)] = None,
    alt_text: Annotated[
        str | None,
        Query(alias="altText", min_length=1, max_length=1024),
    ] = None,
) -> ImageArtifactRef:
    try:
        return await service.upload_image(
            namespace,
            path,
            await request.body(),
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            content_type=request.headers.get("content-type"),
            expected_version=expected_version,
            alt_text=alt_text,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/images/{path:path}",
    response_model=ImageArtifactRef,
    tags=["namespace-resources"],
)
async def get_namespace_image(
    namespace: str,
    path: str,
    service: NamespaceResourceServiceDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("namespace_file", PermissionAction.READ))
    ],
    tenant_id: TenantDependency,
    version: Annotated[int | None, Query(ge=1)] = None,
    alt_text: Annotated[
        str | None,
        Query(alias="altText", min_length=1, max_length=1024),
    ] = None,
) -> ImageArtifactRef:
    try:
        return await service.get_image_artifact(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            version=version,
            alt_text=alt_text,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router_1.put(
    "/api/v1/namespaces/{namespace}/files/{path:path}",
    response_model=NamespaceFile,
    tags=["namespace-resources"],
)
async def upload_namespace_file(
    namespace: str,
    path: str,
    request: Request,
    service: NamespaceResourceServiceDependency,
    actor: Annotated[
        ActorContext,
        Depends(require_namespace_permission("namespace_file", PermissionAction.WRITE)),
    ],
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=0)] = None,
) -> NamespaceFile:
    try:
        return await service.upload_file(
            namespace,
            path,
            await request.body(),
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            content_type=request.headers.get("content-type"),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/files/{path:path}/versions",
    response_model=list[NamespaceFileVersion],
    tags=["namespace-resources"],
)
async def list_namespace_file_versions(
    namespace: str,
    path: str,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("namespace_file", PermissionAction.LIST))
    ],
    tenant_id: TenantDependency,
) -> list[NamespaceFileVersion]:
    return await repository.list_file_versions(
        namespace,
        path,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
    )


@router_1.post(
    "/api/v1/namespaces/{namespace}/files/{path:path}/move",
    response_model=NamespaceFile,
    tags=["namespace-resources"],
)
async def move_namespace_file(
    namespace: str,
    path: str,
    request: NamespaceFileMoveRequest,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext,
        Depends(require_namespace_permission("namespace_file", PermissionAction.WRITE)),
    ],
    tenant_id: TenantDependency,
) -> NamespaceFile:
    try:
        return await repository.move_file(
            namespace,
            path,
            request.destination_path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=request.expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/files/{path:path}",
    response_class=StreamingResponse,
    tags=["namespace-resources"],
)
async def download_namespace_file(
    namespace: str,
    path: str,
    service: NamespaceResourceServiceDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("namespace_file", PermissionAction.READ))
    ],
    tenant_id: TenantDependency,
    version: Annotated[int | None, Query(ge=1)] = None,
) -> StreamingResponse:
    try:
        selected, content = await service.download_file(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            version=version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    async def chunks() -> AsyncIterator[bytes]:
        yield content

    return StreamingResponse(
        chunks(),
        media_type=selected.content_type or "application/octet-stream",
        headers={
            "ETag": f'"sha256:{selected.checksum_sha256}"',
            "X-Amesh-File-Version": str(selected.version),
            "X-Content-Type-Options": "nosniff",
        },
    )


@router_1.delete(
    "/api/v1/namespaces/{namespace}/files/{path:path}",
    tags=["namespace-resources"],
)
async def delete_namespace_file(
    namespace: str,
    path: str,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext,
        Depends(require_namespace_permission("namespace_file", PermissionAction.DELETE)),
    ],
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=0)] = None,
) -> dict[str, int]:
    try:
        version = await repository.delete_file(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    return {"resourceVersion": version}


@router_1.get(
    "/api/v1/namespaces/{namespace}/key-values",
    response_model=list[KeyValueEntry],
    tags=["namespace-resources"],
)
async def list_namespace_key_values(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("key_value", PermissionAction.LIST))
    ],
    tenant_id: TenantDependency,
) -> list[KeyValueEntry]:
    return await repository.list_key_values(
        namespace, tenant_id=tenant_id, actor_id=str(actor.principal_id)
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/key-values/changes",
    response_model=list[KeyValueChange],
    tags=["namespace-resources"],
)
async def list_namespace_key_value_changes(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("key_value", PermissionAction.LIST))
    ],
    tenant_id: TenantDependency,
    after: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[KeyValueChange]:
    return await repository.list_key_value_changes(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        after=after,
        limit=limit,
    )


@router_1.put(
    "/api/v1/namespaces/{namespace}/key-values/{key}",
    response_model=KeyValueEntry,
    tags=["namespace-resources"],
)
async def put_namespace_key_value(
    namespace: str,
    key: str,
    write: KeyValueWrite,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("key_value", PermissionAction.WRITE))
    ],
    tenant_id: TenantDependency,
) -> KeyValueEntry:
    try:
        return await repository.put_key_value(
            namespace,
            key,
            write,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/key-values/{key}",
    response_model=KeyValueEntry,
    tags=["namespace-resources"],
)
async def get_namespace_key_value(
    namespace: str,
    key: str,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("key_value", PermissionAction.READ))
    ],
    tenant_id: TenantDependency,
) -> KeyValueEntry:
    try:
        return await repository.get_key_value(
            namespace, key, tenant_id=tenant_id, actor_id=str(actor.principal_id)
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.delete(
    "/api/v1/namespaces/{namespace}/key-values/{key}",
    tags=["namespace-resources"],
)
async def delete_namespace_key_value(
    namespace: str,
    key: str,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("key_value", PermissionAction.DELETE))
    ],
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> dict[str, bool]:
    try:
        deleted = await repository.delete_key_value(
            namespace,
            key,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    return {"deleted": deleted}


@router_1.get(
    "/api/v1/namespaces/{namespace}/secret-bindings",
    response_model=list[SecretBinding],
    tags=["namespace-resources"],
)
async def list_namespace_secret_bindings(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("secret", PermissionAction.LIST))
    ],
    tenant_id: TenantDependency,
    inherited: bool = True,
) -> list[SecretBinding]:
    return await repository.list_secret_bindings(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        inherited=inherited,
    )


@router_1.put(
    "/api/v1/namespaces/{namespace}/secret-bindings/{key}",
    response_model=SecretBinding,
    tags=["namespace-resources"],
)
async def put_namespace_secret_binding(
    namespace: str,
    key: str,
    write: SecretBindingWrite,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("secret", PermissionAction.WRITE))
    ],
    tenant_id: TenantDependency,
) -> SecretBinding:
    try:
        return await repository.put_secret_binding(
            namespace,
            key,
            write,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc


@router_1.delete(
    "/api/v1/namespaces/{namespace}/secret-bindings/{key}",
    tags=["namespace-resources"],
)
async def delete_namespace_secret_binding(
    namespace: str,
    key: str,
    repository: SharedResourceRepositoryDependency,
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("secret", PermissionAction.WRITE))
    ],
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> dict[str, bool]:
    try:
        deleted = await repository.delete_secret_binding(
            namespace,
            key,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    return {"deleted": deleted}


@router_1.get(
    "/api/v1/namespaces/{namespace}/resource-bundle",
    response_model=NamespaceResourceBundle,
    tags=["namespace-resources"],
)
async def export_namespace_resource_bundle(
    namespace: str,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceResourceBundle:
    for resource_type, action in (
        ("namespace_file", PermissionAction.READ),
        ("key_value", PermissionAction.READ),
        ("secret", PermissionAction.LIST),
    ):
        await authorize_request(
            authorization_service,
            actor,
            resource_type=resource_type,
            action=action,
            tenant_id=tenant_id,
            namespace=namespace,
        )
    return await service.export_bundle(
        namespace, tenant_id=tenant_id, actor_id=str(actor.principal_id)
    )


@router_1.post(
    "/api/v1/namespaces/{namespace}/resource-bundle",
    response_model=NamespaceResourceImportResult,
    tags=["namespace-resources"],
)
async def import_namespace_resource_bundle(
    namespace: str,
    bundle: NamespaceResourceBundle,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceResourceImportResult:
    for resource_type in ("namespace_file", "key_value", "secret"):
        await authorize_request(
            authorization_service,
            actor,
            resource_type=resource_type,
            action=PermissionAction.WRITE,
            tenant_id=tenant_id,
            namespace=namespace,
        )
    try:
        result = await service.import_bundle(
            namespace,
            bundle,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return NamespaceResourceImportResult.model_validate(result)
