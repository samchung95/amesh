"""Cohesive identity API definitions extracted from the composition root."""

from __future__ import annotations

from contextlib import suppress
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from starlette.responses import PlainTextResponse, RedirectResponse

from amesh.api.dependencies import (
    ActorDependency,
    AuthenticationServiceDependency,
    AuthorizationServiceDependency,
    FederationRepositoryDependency,
    FederationServiceDependency,
    ScimProviderDependency,
    SettingsDependency,
    _clear_session_cookies,
    _saml_request_data,
    _scim_filter_value,
    _scim_group_patch,
    _scim_group_resource,
    _scim_principal_handle,
    _scim_user_patch,
    _scim_user_resource,
    _set_authentication_cookies,
    _set_issued_session_cookies,
    _urlencoded_form,
    authorize_request,
)
from amesh.api.models import (
    ChangeLocalPasswordRequest,
    LoginRequest,
    LoginResponse,
    RevokedSessionsResponse,
    ScimGroupRequest,
    ScimGroupResource,
    ScimListResponse,
    ScimPatchRequest,
    ScimUserRequest,
    ScimUserResource,
    SetLocalPasswordRequest,
)
from amesh.authentication import (
    AuthenticationRateLimited,
    InvalidAuthentication,
    LocalAuthenticationDisabled,
    PasswordPolicyError,
)
from amesh.domain import (
    AuthenticationProviderDescriptor,
    PermissionAction,
    PrincipalType,
)
from amesh.domain import (
    AuthenticationRequest as ProviderAuthenticationRequest,
)
from amesh.federation import (
    FederationProviderUnavailable,
    FederationRejected,
)
from amesh.ports.federation_repository import (
    AmbiguousFederatedIdentity,
    FederationReplayRejected,
    FederationStateRejected,
)

router_1 = APIRouter()


@router_1.get(
    "/api/v1/auth/providers",
    response_model=tuple[AuthenticationProviderDescriptor, ...],
    tags=["authentication"],
)
async def list_authentication_providers(
    authentication_service: AuthenticationServiceDependency,
    federation_service: FederationServiceDependency,
    identifier: Annotated[str | None, Query(max_length=255)] = None,
    tenant: Annotated[str | None, Query(max_length=128)] = None,
) -> tuple[AuthenticationProviderDescriptor, ...]:
    routed = federation_service.descriptors(identifier=identifier, tenant=tenant)
    by_id = {provider.id: provider for provider in authentication_service.providers()}
    by_id.update({provider.id: provider for provider in routed})
    return tuple(by_id.values())


@router_1.get(
    "/api/v1/auth/federated/{provider_id}/start",
    response_class=RedirectResponse,
    tags=["authentication"],
)
async def begin_federated_login(
    provider_id: str,
    request: Request,
    federation_service: FederationServiceDependency,
    tenant: Annotated[str | None, Query(max_length=128)] = None,
    return_to: Annotated[str, Query(alias="returnTo", max_length=2048)] = "/",
) -> RedirectResponse:
    try:
        provider = federation_service.provider(provider_id)
        if provider.kind == "oidc":
            location = await federation_service.begin_oidc(
                provider_id,
                tenant=tenant,
                return_to=return_to,
            )
        elif provider.kind == "saml":
            location = await federation_service.begin_saml(
                provider_id,
                _saml_request_data(request),
                tenant=tenant,
                return_to=return_to,
            )
        else:
            raise FederationRejected("LDAP providers use password login")
    except FederationProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except FederationRejected as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RedirectResponse(location, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router_1.get(
    "/api/v1/auth/federated/{provider_id}/callback",
    response_class=RedirectResponse,
    tags=["authentication"],
)
async def complete_oidc_login(
    provider_id: str,
    response: Response,
    federation_service: FederationServiceDependency,
    settings: SettingsDependency,
    state_token: Annotated[str, Query(alias="state", min_length=1, max_length=2048)],
    code: Annotated[str | None, Query(max_length=4096)] = None,
    error: Annotated[str | None, Query(max_length=255)] = None,
) -> RedirectResponse:
    if error is not None or code is None:
        with suppress(FederationRejected, FederationStateRejected):
            await federation_service.reject_oidc(
                provider_id,
                state_token=state_token,
                reason=error or "authorization-code-missing",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="identity provider denied authentication",
        )
    try:
        issued, return_to = await federation_service.complete_oidc(
            provider_id,
            state_token=state_token,
            code=code,
        )
    except FederationProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except (
        AmbiguousFederatedIdentity,
        FederationRejected,
        FederationReplayRejected,
        FederationStateRejected,
        PermissionError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="federated authentication failed",
        ) from exc
    redirect = RedirectResponse(return_to, status_code=status.HTTP_303_SEE_OTHER)
    _set_issued_session_cookies(redirect, settings, issued)
    response.headers.update(redirect.headers)
    return redirect


@router_1.post(
    "/api/v1/auth/federated/{provider_id}/callback",
    response_class=RedirectResponse,
    tags=["authentication"],
)
async def complete_saml_login(
    provider_id: str,
    request: Request,
    response: Response,
    federation_service: FederationServiceDependency,
    settings: SettingsDependency,
) -> RedirectResponse:
    post_data = _urlencoded_form(await request.body())
    state_token = post_data.get("RelayState", "")
    if not state_token or "SAMLResponse" not in post_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid SAML callback")
    try:
        issued, return_to = await federation_service.complete_saml(
            provider_id,
            _saml_request_data(request, post_data=post_data),
            state_token=state_token,
        )
    except FederationProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except (
        AmbiguousFederatedIdentity,
        FederationRejected,
        FederationReplayRejected,
        FederationStateRejected,
        PermissionError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="federated authentication failed",
        ) from exc
    redirect = RedirectResponse(return_to, status_code=status.HTTP_303_SEE_OTHER)
    _set_issued_session_cookies(redirect, settings, issued)
    response.headers.update(redirect.headers)
    return redirect


@router_1.get(
    "/api/v1/auth/federated/{provider_id}/saml/metadata",
    response_class=PlainTextResponse,
    tags=["authentication"],
)
async def saml_service_provider_metadata(
    provider_id: str,
    federation_service: FederationServiceDependency,
) -> PlainTextResponse:
    try:
        metadata = federation_service.saml_metadata(provider_id)
    except (FederationProviderUnavailable, FederationRejected) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PlainTextResponse(metadata, media_type="application/samlmetadata+xml")


@router_1.get("/scim/v2/ServiceProviderConfig", tags=["scim"])
async def scim_service_provider_config(
    provider: ScimProviderDependency,
) -> dict[str, object]:
    del provider
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "patch": {"supported": True},
        "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
        "filter": {"supported": True, "maxResults": 200},
        "changePassword": {"supported": False},
        "sort": {"supported": False},
        "etag": {"supported": True},
        "authenticationSchemes": [
            {
                "type": "oauthbearertoken",
                "name": "Bearer token",
                "description": "Tenant-bound token loaded from a rotatable file",
                "specUri": "https://www.rfc-editor.org/rfc/rfc6750",
                "primary": True,
            }
        ],
    }


@router_1.get(
    "/scim/v2/Users",
    response_model=ScimListResponse,
    response_model_by_alias=True,
    tags=["scim"],
)
async def list_scim_users(
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
    filter_value: Annotated[str | None, Query(alias="filter", max_length=1024)] = None,
    start_index: Annotated[int, Query(alias="startIndex", ge=1)] = 1,
    count: Annotated[int, Query(ge=0, le=200)] = 100,
) -> ScimListResponse:
    handle = _scim_filter_value(filter_value, "userName")
    records = await repository.list_scim(provider.id, "User", handle=handle)
    selected = records[start_index - 1 : start_index - 1 + count]
    resources = tuple(_scim_user_resource(record) for record in selected)
    return ScimListResponse(
        totalResults=len(records),
        startIndex=start_index,
        itemsPerPage=len(resources),
        Resources=resources,
    )


@router_1.post(
    "/scim/v2/Users",
    response_model=ScimUserResource,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    tags=["scim"],
)
async def create_scim_user(
    payload: ScimUserRequest,
    response: Response,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimUserResource:
    try:
        record = await repository.create_scim(
            provider.id,
            "User",
            handle=_scim_principal_handle(payload.user_name),
            resource_name=payload.user_name,
            display_name=payload.display_name or payload.user_name,
            enabled=payload.active,
            external_id=payload.external_id,
            tenant=provider.tenant,
            role=provider.role,
        )
    except (ValueError, LookupError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    result = _scim_user_resource(record)
    response.headers["Location"] = result.meta.location
    response.headers["ETag"] = result.meta.version
    return result


@router_1.get(
    "/scim/v2/Users/{user_id}",
    response_model=ScimUserResource,
    response_model_by_alias=True,
    tags=["scim"],
)
async def get_scim_user(
    user_id: UUID,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimUserResource:
    try:
        return _scim_user_resource(await repository.get_scim(provider.id, "User", user_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.patch(
    "/scim/v2/Users/{user_id}",
    response_model=ScimUserResource,
    response_model_by_alias=True,
    tags=["scim"],
)
async def patch_scim_user(
    user_id: UUID,
    payload: ScimPatchRequest,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimUserResource:
    try:
        display_name, active = _scim_user_patch(payload)
        record = await repository.update_scim(
            provider.id,
            "User",
            user_id,
            display_name=display_name,
            enabled=active,
        )
        return _scim_user_resource(record)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router_1.delete(
    "/scim/v2/Users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["scim"],
)
async def delete_scim_user(
    user_id: UUID,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> None:
    try:
        await repository.delete_scim(provider.id, "User", user_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.get(
    "/scim/v2/Groups",
    response_model=ScimListResponse,
    response_model_by_alias=True,
    tags=["scim"],
)
async def list_scim_groups(
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
    filter_value: Annotated[str | None, Query(alias="filter", max_length=1024)] = None,
    start_index: Annotated[int, Query(alias="startIndex", ge=1)] = 1,
    count: Annotated[int, Query(ge=0, le=200)] = 100,
) -> ScimListResponse:
    handle = _scim_filter_value(filter_value, "displayName")
    records = await repository.list_scim(provider.id, "Group", handle=handle)
    selected = records[start_index - 1 : start_index - 1 + count]
    resources = tuple(_scim_group_resource(record) for record in selected)
    return ScimListResponse(
        totalResults=len(records),
        startIndex=start_index,
        itemsPerPage=len(resources),
        Resources=resources,
    )


@router_1.post(
    "/scim/v2/Groups",
    response_model=ScimGroupResource,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    tags=["scim"],
)
async def create_scim_group(
    payload: ScimGroupRequest,
    response: Response,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimGroupResource:
    try:
        record = await repository.create_scim(
            provider.id,
            "Group",
            handle=_scim_principal_handle(payload.display_name),
            resource_name=payload.display_name,
            display_name=payload.display_name,
            enabled=True,
            external_id=payload.external_id,
            tenant=provider.tenant,
            role=provider.role,
            member_ids=tuple(item.value for item in payload.members),
        )
    except (ValueError, LookupError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    result = _scim_group_resource(record)
    response.headers["Location"] = result.meta.location
    response.headers["ETag"] = result.meta.version
    return result


@router_1.get(
    "/scim/v2/Groups/{group_id}",
    response_model=ScimGroupResource,
    response_model_by_alias=True,
    tags=["scim"],
)
async def get_scim_group(
    group_id: UUID,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimGroupResource:
    try:
        return _scim_group_resource(await repository.get_scim(provider.id, "Group", group_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.patch(
    "/scim/v2/Groups/{group_id}",
    response_model=ScimGroupResource,
    response_model_by_alias=True,
    tags=["scim"],
)
async def patch_scim_group(
    group_id: UUID,
    payload: ScimPatchRequest,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> ScimGroupResource:
    try:
        current = await repository.get_scim(provider.id, "Group", group_id)
        display_name, member_ids = _scim_group_patch(payload, current.member_ids)
        record = await repository.update_scim(
            provider.id,
            "Group",
            group_id,
            display_name=display_name,
            member_ids=member_ids,
        )
        return _scim_group_resource(record)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router_1.delete(
    "/scim/v2/Groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["scim"],
)
async def delete_scim_group(
    group_id: UUID,
    provider: ScimProviderDependency,
    repository: FederationRepositoryDependency,
) -> None:
    try:
        await repository.delete_scim(provider.id, "Group", group_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def _authentication_source(request: Request) -> str:
    """Return the stable peer identifier used by the login throttle."""

    return request.client.host if request.client is not None else "unknown"


@router_1.post(
    "/api/v1/auth/login",
    response_model=LoginResponse,
    tags=["authentication"],
)
async def login(
    login_request: LoginRequest,
    request: Request,
    response: Response,
    authentication_service: AuthenticationServiceDependency,
    settings: SettingsDependency,
) -> LoginResponse:
    # Keep the login throttle key tied to the network peer only.  User-Agent is
    # attacker-controlled and would let a caller evade the source limit by
    # rotating an otherwise irrelevant header.
    source = _authentication_source(request)
    try:
        issued = await authentication_service.login(
            ProviderAuthenticationRequest(
                provider=login_request.provider,
                identifier=login_request.identifier,
                secret=login_request.password,
            ),
            source=source,
        )
    except AuthenticationRateLimited as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="authentication rate limit exceeded",
            headers={"Retry-After": "60"},
        ) from exc
    except LocalAuthenticationDisabled as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="local authentication is disabled by policy",
        ) from exc
    except FederationProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="identity provider is unavailable",
        ) from exc
    except InvalidAuthentication as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication failed",
        ) from exc
    max_age = max(
        0,
        int((issued.absolute_expires_at - datetime.now(UTC)).total_seconds()),
    )
    _set_authentication_cookies(
        response,
        settings,
        session_token=issued.session_token.get_secret_value(),
        csrf_token=issued.csrf_token.get_secret_value(),
        max_age=max_age,
    )
    return LoginResponse(
        principalId=issued.actor.principal_id,
        display=issued.actor.display,
        idleExpiresAt=issued.idle_expires_at,
        absoluteExpiresAt=issued.absolute_expires_at,
    )


@router_1.post(
    "/api/v1/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["authentication"],
)
async def logout(
    request: Request,
    response: Response,
    actor: ActorDependency,
    authentication_service: AuthenticationServiceDependency,
    settings: SettingsDependency,
) -> None:
    session_id = getattr(request.state, "browser_session_id", None)
    if session_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="logout requires a browser session",
        )
    await authentication_service.logout(session_id, actor_id=str(actor.principal_id))
    _clear_session_cookies(response, settings)


@router_1.post(
    "/api/v1/auth/logout-all",
    response_model=RevokedSessionsResponse,
    tags=["authentication"],
)
async def logout_all(
    response: Response,
    actor: ActorDependency,
    authentication_service: AuthenticationServiceDependency,
    settings: SettingsDependency,
) -> RevokedSessionsResponse:
    count = await authentication_service.revoke_all(
        actor.principal_id,
        actor_id=str(actor.principal_id),
    )
    _clear_session_cookies(response, settings)
    return RevokedSessionsResponse(revokedCount=count)


@router_1.post(
    "/api/v1/auth/password",
    response_model=RevokedSessionsResponse,
    tags=["authentication"],
)
async def change_local_password(
    password_request: ChangeLocalPasswordRequest,
    response: Response,
    actor: ActorDependency,
    authentication_service: AuthenticationServiceDependency,
    settings: SettingsDependency,
) -> RevokedSessionsResponse:
    if actor.principal_type is not PrincipalType.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="local password rotation requires a user session",
        )
    try:
        count = await authentication_service.change_local_password(
            actor.principal_id,
            identifier=password_request.identifier,
            current_password=password_request.current_password,
            new_password=password_request.new_password,
        )
    except InvalidAuthentication as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication failed",
        ) from exc
    except (LocalAuthenticationDisabled, PasswordPolicyError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    _clear_session_cookies(response, settings)
    return RevokedSessionsResponse(revokedCount=count)


@router_1.put(
    "/api/v1/admin/principals/{principal_id}/local-password",
    response_model=RevokedSessionsResponse,
    tags=["authentication"],
)
async def set_local_password(
    principal_id: UUID,
    password_request: SetLocalPasswordRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    authentication_service: AuthenticationServiceDependency,
) -> RevokedSessionsResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="principal",
        action=PermissionAction.MANAGE,
    )
    try:
        count = await authentication_service.set_local_password(
            principal_id,
            password_request.new_password,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ValueError, LocalAuthenticationDisabled, PasswordPolicyError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return RevokedSessionsResponse(revokedCount=count)


@router_1.delete(
    "/api/v1/admin/principals/{principal_id}/sessions",
    response_model=RevokedSessionsResponse,
    tags=["authentication"],
)
async def revoke_principal_sessions(
    principal_id: UUID,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    authentication_service: AuthenticationServiceDependency,
) -> RevokedSessionsResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="principal",
        action=PermissionAction.MANAGE,
    )
    count = await authentication_service.revoke_all(
        principal_id,
        actor_id=str(actor.principal_id),
    )
    return RevokedSessionsResponse(revokedCount=count)
