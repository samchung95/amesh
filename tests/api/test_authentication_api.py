from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthenticationRepository,
    PostgresAuthorizationRepository,
    PostgresCredentialRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    get_authentication_repository,
    get_authentication_service,
    get_authorization_repository,
    get_authorization_service,
    get_credential_repository,
    get_credential_service,
    get_settings,
    get_tenant_repository,
    get_tenant_service,
)
from amesh.authentication import AuthenticationService, LocalAuthenticationDisabled
from amesh.authorization import AuthorizationService
from amesh.config import Settings
from amesh.credentials import CredentialService
from amesh.domain import (
    ActorContext,
    AuthenticationProviderDescriptor,
    AuthenticationProviderKind,
    AuthenticationRequest,
    PrincipalType,
    ProviderIdentity,
)
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_local_multi_user_browser_sessions_are_cookie_csrf_and_policy_bound(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        try:
            engine = create_async_engine(migrated_test_database_url)
            authentication_repository = PostgresAuthenticationRepository(engine)
            authorization_repository = PostgresAuthorizationRepository(engine)
            credential_repository = PostgresCredentialRepository(engine)
            tenant_repository = PostgresTenantRepository(engine)
            settings = Settings(
                _env_file=None,
                database_url=migrated_test_database_url,
                app_env="production",
                auth_mode="credentials",
                auth_policy="local",
                amesh_token_pepper="interactive-auth-test-pepper",
                object_storage_workload_identity=True,
                webhook_signing_key="external-webhook-signing-key-at-least-32-bytes",
                auth_login_max_failures=2,
                auth_login_lock_seconds=60,
                auth_session_idle_seconds=300,
                auth_session_absolute_seconds=3_600,
                auth_session_rotation_seconds=30,
            )
            authentication_service = _authentication_service(
                authentication_repository,
                settings,
            )
            authorization_service = AuthorizationService(authorization_repository)
            credential_service = CredentialService(
                credential_repository,
                token_pepper=settings.amesh_token_pepper,
            )
            tenant_service = TenantService(tenant_repository)

            administrator = await authentication_service.bootstrap_local_admin(
                handle="root-admin",
                display_name="Root administrator",
                password=SecretStr("correct horse battery staple"),
            )
            with pytest.raises(ValueError, match="already been completed"):
                await authentication_service.bootstrap_local_admin(
                    handle="second-bootstrap",
                    display_name="Second bootstrap",
                    password=SecretStr("another correct battery staple"),
                )

            app.dependency_overrides[get_settings] = lambda: settings
            app.dependency_overrides[get_authentication_repository] = lambda: (
                authentication_repository
            )
            app.dependency_overrides[get_authentication_service] = lambda: authentication_service
            app.dependency_overrides[get_authorization_repository] = lambda: (
                authorization_repository
            )
            app.dependency_overrides[get_authorization_service] = lambda: authorization_service
            app.dependency_overrides[get_credential_repository] = lambda: credential_repository
            app.dependency_overrides[get_credential_service] = lambda: credential_service
            app.dependency_overrides[get_tenant_repository] = lambda: tenant_repository
            app.dependency_overrides[get_tenant_service] = lambda: tenant_service

            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="https://amesh.test",
            ) as client:
                providers = await client.get("/api/v1/auth/providers")
                assert providers.status_code == 200
                assert providers.json() == [
                    {
                        "id": "local",
                        "kind": "local",
                        "display_name": "Local account",
                        "interactive": True,
                        "login_mode": "password",
                        "domains": [],
                        "tenants": [],
                    }
                ]

                login = await client.post(
                    "/api/v1/auth/login",
                    json={
                        "provider": "local",
                        "identifier": "root-admin",
                        "password": "correct horse battery staple",
                    },
                )
                assert login.status_code == 200
                assert login.json()["principalId"] == str(administrator.id)
                cookies = login.headers.get_list("set-cookie")
                assert any(
                    "__Host-amesh_session=" in value
                    and "HttpOnly" in value
                    and "Secure" in value
                    and "SameSite=lax" in value
                    for value in cookies
                )
                assert any(
                    "__Host-amesh_csrf=" in value and "Secure" in value and "HttpOnly" not in value
                    for value in cookies
                )
                csrf = client.cookies.get("__Host-amesh_csrf")
                session_token = client.cookies.get("__Host-amesh_session")
                assert csrf and session_token

                ui_session = await client.get(
                    "/api/v1/ui/session",
                    headers={"X-Amesh-Tenant": "default"},
                )
                assert ui_session.status_code == 200
                assert ui_session.json()["display"] == "Root administrator"

                missing_csrf = await client.post(
                    "/api/v1/admin/principals",
                    json={
                        "principal_type": "USER",
                        "handle": f"viewer-{uuid4().hex[:8]}",
                        "display_name": "Tenant viewer",
                    },
                )
                assert missing_csrf.status_code == 403

                headers = {"X-Amesh-CSRF": csrf, "X-Amesh-Tenant": "default"}
                created = await client.post(
                    "/api/v1/admin/principals",
                    headers=headers,
                    json={
                        "principal_type": "USER",
                        "handle": "tenant-viewer",
                        "display_name": "Tenant viewer",
                    },
                )
                assert created.status_code == 201
                viewer_id = UUID(created.json()["id"])
                binding = await client.post(
                    "/api/v1/admin/bindings",
                    headers=headers,
                    json={
                        "principal_id": str(viewer_id),
                        "principal_type": "USER",
                        "role_name": "viewer",
                        "scope_type": "TENANT",
                        "tenant_id": "default",
                    },
                )
                assert binding.status_code == 201
                password = await client.put(
                    f"/api/v1/admin/principals/{viewer_id}/local-password",
                    headers=headers,
                    json={"newPassword": "viewer correct battery staple"},
                )
                assert password.status_code == 200

                logout = await client.post("/api/v1/auth/logout", headers=headers)
                assert logout.status_code == 204
                assert client.cookies.get("__Host-amesh_session") is None

                viewer_login = await client.post(
                    "/api/v1/auth/login",
                    json={
                        "provider": "local",
                        "identifier": "tenant-viewer",
                        "password": "viewer correct battery staple",
                    },
                )
                assert viewer_login.status_code == 200
                viewer_csrf = client.cookies.get("__Host-amesh_csrf")
                viewer_session_token = client.cookies.get("__Host-amesh_session")
                assert viewer_csrf and viewer_session_token
                viewer_ui = await client.get(
                    "/api/v1/ui/session",
                    headers={"X-Amesh-Tenant": "default"},
                )
                assert viewer_ui.status_code == 200
                assert viewer_ui.json()["display"] == "Tenant viewer"
                assert viewer_ui.json()["capabilities"]["flows.view"] is True
                assert viewer_ui.json()["capabilities"]["administration.manage"] is False

                async with engine.begin() as connection:
                    await connection.execute(
                        text(
                            """
                            UPDATE auth_browser_sessions
                            SET rotated_at = :rotated_at
                            WHERE principal_id = :principal_id AND status = 'ACTIVE'
                            """
                        ),
                        {
                            "rotated_at": datetime.now(UTC) - timedelta(seconds=60),
                            "principal_id": viewer_id,
                        },
                    )
                rotated = await client.get(
                    "/api/v1/ui/session",
                    headers={"X-Amesh-Tenant": "default"},
                )
                assert rotated.status_code == 200
                rotated_token = client.cookies.get("__Host-amesh_session")
                assert rotated_token and rotated_token != viewer_session_token

                revoke_all = await client.post(
                    "/api/v1/auth/logout-all",
                    headers={
                        "X-Amesh-CSRF": viewer_csrf,
                        "X-Amesh-Tenant": "default",
                    },
                )
                assert revoke_all.status_code == 200
                assert revoke_all.json()["revokedCount"] == 1
                assert (
                    await client.get(
                        "/api/v1/ui/session",
                        headers={"X-Amesh-Tenant": "default"},
                    )
                ).status_code == 401

                relogin = await client.post(
                    "/api/v1/auth/login",
                    json={
                        "provider": "local",
                        "identifier": "tenant-viewer",
                        "password": "viewer correct battery staple",
                    },
                )
                assert relogin.status_code == 200
                rotation_csrf = client.cookies.get("__Host-amesh_csrf")
                assert rotation_csrf
                changed = await client.post(
                    "/api/v1/auth/password",
                    headers={
                        "X-Amesh-CSRF": rotation_csrf,
                        "X-Amesh-Tenant": "default",
                    },
                    json={
                        "identifier": "tenant-viewer",
                        "currentPassword": "viewer correct battery staple",
                        "newPassword": "rotated viewer battery staple",
                    },
                )
                assert changed.status_code == 200
                assert changed.json()["revokedCount"] == 1
                assert (
                    await client.get(
                        "/api/v1/ui/session",
                        headers={"X-Amesh-Tenant": "default"},
                    )
                ).status_code == 401
                assert (
                    await client.post(
                        "/api/v1/auth/login",
                        json={
                            "provider": "local",
                            "identifier": "tenant-viewer",
                            "password": "viewer correct battery staple",
                        },
                    )
                ).status_code == 401
                renewed = await client.post(
                    "/api/v1/auth/login",
                    json={
                        "provider": "local",
                        "identifier": "tenant-viewer",
                        "password": "rotated viewer battery staple",
                    },
                )
                assert renewed.status_code == 200
                async with engine.begin() as connection:
                    await connection.execute(
                        text(
                            """
                            UPDATE auth_browser_sessions
                            SET idle_expires_at = :expired_at
                            WHERE principal_id = :principal_id AND status = 'ACTIVE'
                            """
                        ),
                        {
                            "expired_at": datetime.now(UTC) - timedelta(seconds=1),
                            "principal_id": viewer_id,
                        },
                    )
                assert (
                    await client.get(
                        "/api/v1/ui/session",
                        headers={"X-Amesh-Tenant": "default"},
                    )
                ).status_code == 401

                for _ in range(2):
                    rejected = await client.post(
                        "/api/v1/auth/login",
                        json={
                            "provider": "local",
                            "identifier": "tenant-viewer",
                            "password": "wrong password material",
                        },
                    )
                    assert rejected.status_code == 401
                    assert rejected.json()["detail"] == "authentication failed"
                locked = await client.post(
                    "/api/v1/auth/login",
                    json={
                        "provider": "local",
                        "identifier": "tenant-viewer",
                        "password": "rotated viewer battery staple",
                    },
                )
                assert locked.status_code == 401
                assert locked.json()["detail"] == "authentication failed"

                rate_limited_settings = settings.model_copy(
                    update={"auth_login_rate_limit_per_minute": 2}
                )
                rate_limited_service = _authentication_service(
                    authentication_repository,
                    rate_limited_settings,
                )
                app.dependency_overrides[get_authentication_service] = lambda: rate_limited_service
                rate_transport = httpx.ASGITransport(
                    app=app,
                    client=(f"rate-limit-{uuid4()}", 123),
                )
                async with httpx.AsyncClient(
                    transport=rate_transport,
                    base_url="https://amesh.test",
                ) as rate_client:
                    for _ in range(2):
                        assert (
                            await rate_client.post(
                                "/api/v1/auth/login",
                                json={
                                    "provider": "local",
                                    "identifier": "missing-user",
                                    "password": "irrelevant password material",
                                },
                            )
                        ).status_code == 401
                    limited = await rate_client.post(
                        "/api/v1/auth/login",
                        json={
                            "provider": "local",
                            "identifier": "missing-user",
                            "password": "irrelevant password material",
                        },
                    )
                    assert limited.status_code == 429
                    assert limited.headers["Retry-After"] == "60"

            async with engine.connect() as connection:
                evidence = [
                    json.dumps(dict(row), default=str)
                    for row in (
                        (
                            await connection.execute(
                                text(
                                    """
                                    SELECT actor_id, action, resource_id, source, evidence
                                    FROM audit_events
                                    WHERE resource_type = 'authentication'
                                    ORDER BY occurred_at
                                    """
                                )
                            )
                        )
                        .mappings()
                        .all()
                    )
                ]
            combined = "\n".join(evidence)
            assert "correct horse battery staple" not in combined
            assert "viewer correct battery staple" not in combined
            assert "rotated viewer battery staple" not in combined
            assert session_token not in combined
            assert csrf not in combined
            await engine.dispose()
        finally:
            app.dependency_overrides.clear()

    asyncio.run(scenario())


def test_federated_only_policy_disables_local_provider_and_password_login() -> None:
    class RepositoryStub:
        async def allow_login_source(self, *_args: object, **_kwargs: object) -> bool:
            return True

    settings = Settings(
        _env_file=None,
        auth_policy="federated-only",
    )
    service = _authentication_service(RepositoryStub(), settings)

    assert service.providers() == ()
    with pytest.raises(LocalAuthenticationDisabled):
        asyncio.run(
            service.login(
                AuthenticationRequest(
                    provider="local",
                    identifier="operator",
                    secret=SecretStr("correct horse battery staple"),
                ),
                source="test",
            )
        )


def test_provider_neutral_registry_delegates_federated_authentication() -> None:
    principal_id = uuid4()

    class RepositoryStub:
        async def allow_login_source(self, *_args: object, **_kwargs: object) -> bool:
            return True

        async def create_browser_session(self, *_args: object, **_kwargs: object) -> ActorContext:
            return ActorContext(
                principal_id=principal_id,
                principal_type=PrincipalType.USER,
                display="Federated operator",
            )

    class FederatedProvider:
        id = "corporate-oidc"
        descriptor = AuthenticationProviderDescriptor(
            id=id,
            kind=AuthenticationProviderKind.OIDC,
            display_name="Corporate OIDC",
        )

        async def authenticate(
            self,
            request: AuthenticationRequest,
            *,
            now: datetime,
        ) -> ProviderIdentity | None:
            del now
            assert request.provider == self.id
            return ProviderIdentity(
                provider=self.id,
                principal_id=principal_id,
                display="Federated operator",
                credential_version=1,
            )

    settings = Settings(_env_file=None, auth_policy="federated-only")
    service = _authentication_service(
        RepositoryStub(),
        settings,
        providers=(FederatedProvider(),),
    )

    assert [provider.kind for provider in service.providers()] == [AuthenticationProviderKind.OIDC]
    issued = asyncio.run(
        service.login(
            AuthenticationRequest(
                provider="corporate-oidc",
                identifier="operator@example.test",
                secret=SecretStr("provider-assertion"),
            ),
            source="test",
        )
    )
    assert issued.actor.principal_id == principal_id


def _authentication_service(
    repository: object,
    settings: Settings,
    *,
    providers: tuple[object, ...] = (),
) -> AuthenticationService:
    return AuthenticationService(
        repository,  # type: ignore[arg-type]
        token_pepper=settings.amesh_token_pepper,
        policy=settings.auth_policy,
        session_idle_seconds=settings.auth_session_idle_seconds,
        session_absolute_seconds=settings.auth_session_absolute_seconds,
        session_rotation_seconds=settings.auth_session_rotation_seconds,
        session_overlap_seconds=settings.auth_session_overlap_seconds,
        login_rate_limit_per_minute=settings.auth_login_rate_limit_per_minute,
        login_max_failures=settings.auth_login_max_failures,
        login_lock_seconds=settings.auth_login_lock_seconds,
        providers=providers,  # type: ignore[arg-type]
    )
