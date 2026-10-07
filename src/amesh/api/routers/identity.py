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
from starlette.responses import RedirectResponse

from amesh.api.dependencies import (
    ActorDependency,
    AuthenticationServiceDependency,
    AuthorizationServiceDependency,
    FederationServiceDependency,
    SettingsDependency,
    _clear_session_cookies,
    _set_authentication_cookies,
    _set_issued_session_cookies,
    authorize_request,
)
from amesh.api.models import (
    ChangeLocalPasswordRequest,
    LoginRequest,
    LoginResponse,
    RevokedSessionsResponse,
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
    federation_service: FederationServiceDependency,
    tenant: Annotated[str | None, Query(max_length=128)] = None,
    return_to: Annotated[str, Query(alias="returnTo", max_length=2048)] = "/",
) -> RedirectResponse:
    try:
        location = await federation_service.begin_oidc(
            provider_id,
            tenant=tenant,
            return_to=return_to,
        )
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
