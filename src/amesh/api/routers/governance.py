"""Cohesive governance API definitions extracted from the composition root."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    Response,
    status,
)

from amesh.api.contracts import (
    CollectionQuery,
    collection_response,
)
from amesh.api.dependencies import (
    ActorDependency,
    AuditArtifactServiceDependency,
    AuditRepositoryDependency,
    AuthorizationRepositoryDependency,
    AuthorizationServiceDependency,
    CredentialServiceDependency,
    TenantDependency,
    TenantServiceDependency,
    authorize_request,
)
from amesh.api.models import (
    AuthorizationExplanationRequest,
    CreateTenantRequest,
    ExchangeCredentialRequest,
    IssueCredentialRequest,
    IssuedCredentialResponse,
    RevokedCredentialsResponse,
    RotateCredentialRequest,
)
from amesh.audit import AuditArtifact
from amesh.authorization import AuthorizationService
from amesh.domain import (
    ActorContext,
    AuditEventPage,
    AuditExportDestination,
    AuditExportFormat,
    AuditExportReceipt,
    AuditExportRequest,
    AuditIntegrityReport,
    AuditLegalHold,
    AuditLegalHoldCreate,
    AuditRetentionPolicy,
    AuditRetentionPolicyUpdate,
    AuditRetentionResult,
    AuthorizationDecision,
    AuthorizationRequest,
    ComplianceEvidenceCreate,
    ComplianceEvidenceRecord,
    CompliancePackageRequest,
    CredentialMetadata,
    IssuedCredential,
    NamespaceAuthorizationBoundary,
    PermissionAction,
    PrincipalDefinition,
    RoleBinding,
    RoleDefinition,
    TenantDefinition,
    TenantExport,
    TenantPolicy,
)
from amesh.identity import CredentialOperationError
from amesh.ports import (
    LastAdministratorError,
)

router_1 = APIRouter()


router_2 = APIRouter()


async def _authorize_tenant_administration(
    service: AuthorizationService,
    actor: ActorContext,
) -> None:
    await authorize_request(
        service,
        actor,
        resource_type="tenant",
        action=PermissionAction.MANAGE,
    )


@router_1.post(
    "/api/v1/admin/tenants",
    response_model=TenantDefinition,
    status_code=status.HTTP_201_CREATED,
    tags=["tenants"],
)
async def create_tenant(
    request: CreateTenantRequest,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.create(
            slug=request.slug,
            display_name=request.display_name,
            policy=request.policy,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_1.get(
    "/api/v1/admin/tenants",
    response_model=list[TenantDefinition],
    tags=["tenants"],
)
async def list_tenants(
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await _authorize_tenant_administration(authorization_service, actor)
    return collection_response(await tenants.list(), query)


@router_1.get(
    "/api/v1/admin/tenants/{tenant_slug}",
    response_model=TenantDefinition,
    tags=["tenants"],
)
async def get_tenant(
    tenant_slug: str,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.get(tenant_slug)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.put(
    "/api/v1/admin/tenants/{tenant_slug}/policy",
    response_model=TenantDefinition,
    tags=["tenants"],
)
async def update_tenant_policy(
    tenant_slug: str,
    policy: TenantPolicy,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.update_policy(
            tenant_slug,
            policy,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.post(
    "/api/v1/admin/tenants/{tenant_slug}/suspend",
    response_model=TenantDefinition,
    tags=["tenants"],
)
async def suspend_tenant(
    tenant_slug: str,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.suspend(tenant_slug, actor_id=str(actor.principal_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.delete(
    "/api/v1/admin/tenants/{tenant_slug}",
    response_model=TenantDefinition,
    tags=["tenants"],
)
async def delete_tenant(
    tenant_slug: str,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.delete(tenant_slug, actor_id=str(actor.principal_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.post(
    "/api/v1/admin/tenants/{tenant_slug}/restore",
    response_model=TenantDefinition,
    tags=["tenants"],
)
async def restore_tenant(
    tenant_slug: str,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantDefinition:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.restore(tenant_slug, actor_id=str(actor.principal_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.post(
    "/api/v1/admin/tenants/{tenant_slug}/exports",
    response_model=TenantExport,
    status_code=status.HTTP_201_CREATED,
    tags=["tenants"],
)
async def export_tenant(
    tenant_slug: str,
    tenants: TenantServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> TenantExport:
    await _authorize_tenant_administration(authorization_service, actor)
    try:
        return await tenants.export(tenant_slug, actor_id=str(actor.principal_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.post(
    "/api/v1/admin/principals",
    response_model=PrincipalDefinition,
    status_code=status.HTTP_201_CREATED,
    tags=["authorization"],
)
async def create_principal(
    principal: PrincipalDefinition,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> PrincipalDefinition:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="principal",
        action=PermissionAction.MANAGE,
    )
    try:
        return await repository.create_principal(
            principal,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_1.get(
    "/api/v1/admin/principals",
    response_model=list[PrincipalDefinition],
    tags=["authorization"],
)
async def list_principals(
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="principal",
        action=PermissionAction.VIEW,
    )
    return collection_response(await repository.list_principals(), query)


@router_1.put(
    "/api/v1/admin/groups/{group_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["authorization"],
)
async def add_group_member(
    group_id: UUID,
    member_id: UUID,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="group",
        action=PermissionAction.MANAGE,
    )
    try:
        await repository.add_group_member(
            group_id,
            member_id,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router_1.delete(
    "/api/v1/admin/groups/{group_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["authorization"],
)
async def remove_group_member(
    group_id: UUID,
    member_id: UUID,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="group",
        action=PermissionAction.MANAGE,
    )
    try:
        await repository.remove_group_member(
            group_id,
            member_id,
            actor_id=str(actor.principal_id),
        )
    except LastAdministratorError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router_1.put(
    "/api/v1/admin/roles/{role_name}",
    response_model=RoleDefinition,
    tags=["authorization"],
)
async def upsert_role(
    role_name: str,
    role: RoleDefinition,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> RoleDefinition:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="role",
        action=PermissionAction.MANAGE,
    )
    if role.name != role_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="role path and body names must match",
        )
    try:
        return await repository.upsert_role(role, actor_id=str(actor.principal_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_1.get(
    "/api/v1/admin/roles",
    response_model=list[RoleDefinition],
    tags=["authorization"],
)
async def list_roles(
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="role",
        action=PermissionAction.VIEW,
    )
    return collection_response(await repository.list_roles(), query)


@router_1.post(
    "/api/v1/admin/bindings",
    response_model=RoleBinding,
    status_code=status.HTTP_201_CREATED,
    tags=["authorization"],
)
async def create_role_binding(
    binding: RoleBinding,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> RoleBinding:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.MANAGE,
        tenant_id=binding.tenant_id,
        namespace=binding.namespace,
    )
    try:
        return await repository.create_binding(binding, actor_id=str(actor.principal_id))
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_1.get(
    "/api/v1/admin/bindings",
    response_model=list[RoleBinding],
    tags=["authorization"],
)
async def list_role_bindings(
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.VIEW,
    )
    return collection_response(await repository.list_bindings(), query)


@router_1.delete(
    "/api/v1/admin/bindings/{binding_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["authorization"],
)
async def delete_role_binding(
    binding_id: UUID,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: Annotated[str | None, Header(alias="X-Amesh-Tenant")] = None,
    namespace: Annotated[str | None, Header(alias="X-Amesh-Namespace")] = None,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    binding = next(
        (item for item in await repository.list_bindings() if item.id == binding_id),
        None,
    )
    if binding is None or binding.tenant_id != tenant_id or binding.namespace != namespace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="binding not found")
    try:
        await repository.delete_binding(binding_id, actor_id=str(actor.principal_id))
    except LastAdministratorError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router_1.put(
    "/api/v1/admin/tenants/{tenant_id}/namespaces/{namespace}/authorization-boundary",
    response_model=NamespaceAuthorizationBoundary,
    tags=["authorization"],
)
async def set_namespace_authorization_boundary(
    tenant_id: str,
    namespace: str,
    repository: AuthorizationRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> NamespaceAuthorizationBoundary:
    boundary = NamespaceAuthorizationBoundary(tenant_id=tenant_id, namespace=namespace)
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.set_namespace_boundary(
            boundary,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def _issued_credential_response(issued: IssuedCredential) -> IssuedCredentialResponse:
    return IssuedCredentialResponse(
        metadata=issued.metadata,
        token=issued.token.get_secret_value(),
    )


@router_1.post(
    "/api/v1/admin/principals/{principal_id}/credentials",
    response_model=IssuedCredentialResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["credentials"],
)
async def issue_credential(
    principal_id: UUID,
    request: IssueCredentialRequest,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> IssuedCredentialResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.MANAGE,
    )
    try:
        issued = await credentials.issue(
            principal_id,
            name=request.name,
            scopes=request.scopes,
            audience=request.audience,
            expires_at=request.expires_at,
            rate_limit_per_minute=request.rate_limit_per_minute,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (CredentialOperationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _issued_credential_response(issued)


@router_1.get(
    "/api/v1/admin/principals/{principal_id}/credentials",
    response_model=list[CredentialMetadata],
    tags=["credentials"],
)
async def list_credentials(
    principal_id: UUID,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.VIEW,
    )
    return collection_response(await credentials.list(principal_id), query)


@router_1.post(
    "/api/v1/admin/credentials/{credential_id}/rotate",
    response_model=IssuedCredentialResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["credentials"],
)
async def rotate_credential(
    credential_id: UUID,
    request: RotateCredentialRequest,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> IssuedCredentialResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.MANAGE,
    )
    try:
        issued = await credentials.rotate(
            credential_id,
            overlap_seconds=request.overlap_seconds,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (CredentialOperationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _issued_credential_response(issued)


@router_1.delete(
    "/api/v1/admin/credentials/{credential_id}",
    response_model=RevokedCredentialsResponse,
    tags=["credentials"],
)
async def revoke_credential(
    credential_id: UUID,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> RevokedCredentialsResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.MANAGE,
    )
    try:
        revoked = await credentials.revoke(credential_id, actor_id=str(actor.principal_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RevokedCredentialsResponse(revokedCount=revoked)


@router_1.delete(
    "/api/v1/admin/principals/{principal_id}/credentials",
    response_model=RevokedCredentialsResponse,
    tags=["credentials"],
)
async def revoke_all_credentials(
    principal_id: UUID,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> RevokedCredentialsResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.MANAGE,
    )
    try:
        revoked = await credentials.revoke_all(
            principal_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RevokedCredentialsResponse(revokedCount=revoked)


@router_1.post(
    "/api/v1/credentials/exchange",
    response_model=IssuedCredentialResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["credentials"],
)
async def exchange_workload_credential(
    request: ExchangeCredentialRequest,
    credentials: CredentialServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> IssuedCredentialResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="credential",
        action=PermissionAction.USE,
    )
    if actor.credential_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="workload exchange requires an API credential",
        )
    try:
        issued = await credentials.exchange(
            actor.credential_id,
            principal_id=actor.principal_id,
            scopes=request.scopes,
            audience=request.audience,
            expires_in_seconds=request.expires_in_seconds,
            rate_limit_per_minute=request.rate_limit_per_minute,
        )
    except (CredentialOperationError, LookupError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _issued_credential_response(issued)


@router_1.post(
    "/api/v1/authorization/explain",
    response_model=AuthorizationDecision,
    tags=["authorization"],
)
async def explain_authorization(
    request: AuthorizationExplanationRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
) -> AuthorizationDecision:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="authorization",
        action=PermissionAction.MANAGE,
    )
    return await authorization_service.decide(
        AuthorizationRequest(
            actor=ActorContext(
                principal_id=request.principal_id,
                principal_type=request.principal_type,
                display="authorization-subject",
            ),
            tenant_id=request.tenant_id,
            namespace=request.namespace,
            resource_type=request.resource_type,
            action=request.action,
        )
    )


@router_2.get(
    "/api/v1/audit-events",
    response_model=AuditEventPage,
    tags=["audit"],
)
async def list_audit_events(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    cursor: Annotated[int | None, Query(ge=1)] = None,
    limit: Annotated[int, Query(ge=1, le=1_000)] = 100,
    action: Annotated[str | None, Query(max_length=255)] = None,
    resource_type: Annotated[str | None, Query(alias="resourceType", max_length=128)] = None,
    outcome: Annotated[str | None, Query(max_length=64)] = None,
    occurred_from: Annotated[datetime | None, Query(alias="occurredFrom")] = None,
    occurred_to: Annotated[datetime | None, Query(alias="occurredTo")] = None,
) -> AuditEventPage:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_events(
        tenant_id,
        actor_id=str(actor.principal_id),
        cursor=cursor,
        limit=limit,
        action=action,
        resource_type=resource_type,
        outcome=outcome,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
    )


@router_2.get(
    "/api/v1/audit-events/integrity",
    response_model=AuditIntegrityReport,
    tags=["audit"],
)
async def verify_audit_integrity(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditIntegrityReport:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.verify_integrity(tenant_id, actor_id=str(actor.principal_id))


@router_2.get(
    "/api/v1/audit-policy",
    response_model=AuditRetentionPolicy,
    tags=["audit"],
)
async def get_audit_policy(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditRetentionPolicy:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.get_retention_policy(tenant_id)


@router_2.put(
    "/api/v1/audit-policy",
    response_model=AuditRetentionPolicy,
    tags=["audit"],
)
async def update_audit_policy(
    request: AuditRetentionPolicyUpdate,
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditRetentionPolicy:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await repository.set_retention_policy(
        tenant_id,
        AuditRetentionPolicy(retentionDays=request.retention_days),
        actor_id=str(actor.principal_id),
    )


@router_2.get(
    "/api/v1/audit-legal-holds",
    response_model=tuple[AuditLegalHold, ...],
    tags=["audit"],
)
async def list_audit_legal_holds(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> tuple[AuditLegalHold, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_legal_holds(tenant_id, actor_id=str(actor.principal_id))


@router_2.post(
    "/api/v1/audit-legal-holds",
    response_model=AuditLegalHold,
    status_code=status.HTTP_201_CREATED,
    tags=["audit"],
)
async def create_audit_legal_hold(
    request: AuditLegalHoldCreate,
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditLegalHold:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await repository.create_legal_hold(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@router_2.delete(
    "/api/v1/audit-legal-holds/{hold_id}",
    response_model=AuditLegalHold,
    tags=["audit"],
)
async def release_audit_legal_hold(
    hold_id: UUID,
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditLegalHold:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await repository.release_legal_hold(
            tenant_id,
            hold_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_2.post(
    "/api/v1/audit-retention/purge",
    response_model=AuditRetentionResult,
    tags=["audit"],
)
async def purge_audit_retention(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditRetentionResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await repository.purge_retained(tenant_id, actor_id=str(actor.principal_id))


@router_2.get(
    "/api/v1/audit-events/export",
    response_model=None,
    tags=["audit"],
)
async def download_audit_export(
    service: AuditArtifactServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    format: AuditExportFormat = AuditExportFormat.NDJSON,
    limit: Annotated[int, Query(ge=1, le=10_000)] = 10_000,
    action: Annotated[str | None, Query(max_length=255)] = None,
    resource_type: Annotated[str | None, Query(alias="resourceType", max_length=128)] = None,
    outcome: Annotated[str | None, Query(max_length=64)] = None,
    occurred_from: Annotated[datetime | None, Query(alias="occurredFrom")] = None,
    occurred_to: Annotated[datetime | None, Query(alias="occurredTo")] = None,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
    )
    artifact = await service.export_audit(
        tenant_id,
        actor_id=str(actor.principal_id),
        destination=AuditExportDestination.FILE,
        format=format,
        limit=limit,
        action=action,
        resource_type=resource_type,
        outcome=outcome,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
    )
    return _audit_artifact_response(artifact)


@router_2.post(
    "/api/v1/audit-exports",
    response_model=AuditExportReceipt,
    status_code=status.HTTP_201_CREATED,
    tags=["audit"],
)
async def create_object_audit_export(
    request: AuditExportRequest,
    service: AuditArtifactServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditExportReceipt:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="audit",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
    )
    artifact = await service.export_audit(
        tenant_id,
        actor_id=str(actor.principal_id),
        destination=AuditExportDestination.OBJECT_STORAGE,
        format=request.format,
        limit=request.limit,
        action=request.action,
        resource_type=request.resource_type,
        outcome=request.outcome,
        occurred_from=request.occurred_from,
        occurred_to=request.occurred_to,
    )
    return artifact.receipt


@router_2.post(
    "/api/v1/compliance-evidence",
    response_model=ComplianceEvidenceRecord,
    status_code=status.HTTP_201_CREATED,
    tags=["audit"],
)
async def create_compliance_evidence(
    request: ComplianceEvidenceCreate,
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ComplianceEvidenceRecord:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="compliance",
        action=PermissionAction.CREATE,
        tenant_id=tenant_id,
    )
    return await repository.create_compliance_evidence(
        tenant_id,
        request,
        actor_id=str(actor.principal_id),
    )


@router_2.get(
    "/api/v1/compliance-evidence",
    response_model=tuple[ComplianceEvidenceRecord, ...],
    tags=["audit"],
)
async def list_compliance_evidence(
    repository: AuditRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> tuple[ComplianceEvidenceRecord, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="compliance",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return await repository.list_compliance_evidence(
        tenant_id,
        actor_id=str(actor.principal_id),
    )


@router_2.get(
    "/api/v1/compliance-packages/export",
    response_model=None,
    tags=["audit"],
)
async def download_compliance_package(
    service: AuditArtifactServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    occurred_from: Annotated[datetime | None, Query(alias="occurredFrom")] = None,
    occurred_to: Annotated[datetime | None, Query(alias="occurredTo")] = None,
    max_audit_events: Annotated[int, Query(alias="maxAuditEvents", ge=1, le=10_000)] = 10_000,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="compliance",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
    )
    artifact = await service.export_compliance_package(
        tenant_id,
        actor_id=str(actor.principal_id),
        destination=AuditExportDestination.FILE,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
        max_audit_events=max_audit_events,
    )
    return _audit_artifact_response(artifact)


@router_2.post(
    "/api/v1/compliance-packages",
    response_model=AuditExportReceipt,
    status_code=status.HTTP_201_CREATED,
    tags=["audit"],
)
async def create_object_compliance_package(
    request: CompliancePackageRequest,
    service: AuditArtifactServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> AuditExportReceipt:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="compliance",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
    )
    artifact = await service.export_compliance_package(
        tenant_id,
        actor_id=str(actor.principal_id),
        destination=AuditExportDestination.OBJECT_STORAGE,
        occurred_from=request.occurred_from,
        occurred_to=request.occurred_to,
        max_audit_events=request.max_audit_events,
    )
    return artifact.receipt


def _audit_artifact_response(artifact: AuditArtifact) -> Response:
    return Response(
        content=artifact.content,
        media_type=artifact.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{artifact.filename}"',
            "X-Checksum-Sha256": artifact.receipt.checksum_sha256,
            "X-Amesh-Signature": artifact.receipt.signature,
        },
    )
