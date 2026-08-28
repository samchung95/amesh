from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresCredentialRepository,
)
from amesh.authorization import AuthorizationService
from amesh.credentials import CredentialService, InvalidCredential
from amesh.domain import (
    AuthorizationRequest,
    AuthorizationScopeType,
    PermissionAction,
    PrincipalDefinition,
    PrincipalType,
    RoleBinding,
)
from amesh.ports import CredentialRateLimitExceeded

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


async def _cleanup(
    engine: AsyncEngine,
    *,
    principal_ids: list[UUID],
    actor_id: str,
) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM auth_principals WHERE id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": principal_ids},
        )
        await connection.execute(
            text(
                """
                DELETE FROM audit_events
                WHERE resource_type = 'credential'
                  AND (
                    actor_id = :actor_id
                    OR actor_id = ANY(CAST(:principal_ids AS text[]))
                  )
                """
            ),
            {
                "actor_id": actor_id,
                "principal_ids": [str(value) for value in principal_ids],
            },
        )


def test_postgres_service_tokens_rotation_exchange_quota_and_revocation() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        authorization_repository = PostgresAuthorizationRepository(engine)
        repository = PostgresCredentialRepository(engine)
        service = CredentialService(repository, token_pepper=SecretStr("integration-pepper"))
        suffix = uuid4().hex[:12]
        actor_id = f"test:credentials:{suffix}"
        service_account = PrincipalDefinition(
            principal_type=PrincipalType.SERVICE_ACCOUNT,
            handle=f"automation-{suffix}",
            display_name="Automation service account",
        )
        group = PrincipalDefinition(
            principal_type=PrincipalType.GROUP,
            handle=f"automation-group-{suffix}",
            display_name="Automation group",
        )
        worker = PrincipalDefinition(
            principal_type=PrincipalType.WORKER,
            handle=f"worker-{suffix}",
            display_name="Workload worker",
        )
        principal_ids = [service_account.id, group.id, worker.id]
        issued_tokens: list[str] = []
        try:
            for principal in (service_account, group, worker):
                await authorization_repository.create_principal(principal, actor_id=actor_id)
            await authorization_repository.add_group_member(
                group.id,
                service_account.id,
                actor_id=actor_id,
            )
            await authorization_repository.create_binding(
                RoleBinding(
                    principal_id=group.id,
                    principal_type=PrincipalType.GROUP,
                    role_name="viewer",
                    scope_type=AuthorizationScopeType.NAMESPACE,
                    tenant_id="default",
                    namespace="team.automation",
                ),
                actor_id=actor_id,
            )
            tenant_binding = RoleBinding(
                principal_id=service_account.id,
                principal_type=PrincipalType.SERVICE_ACCOUNT,
                role_name="viewer",
                scope_type=AuthorizationScopeType.TENANT,
                tenant_id="default",
            )
            await authorization_repository.create_binding(tenant_binding, actor_id=actor_id)
            assert tenant_binding.id in {
                item.id for item in await authorization_repository.list_bindings()
            }

            issued = await service.issue(
                service_account.id,
                name="automation-api",
                scopes=("flow:view",),
                audience="amesh-api",
                expires_at=datetime.now(UTC) + timedelta(hours=1),
                rate_limit_per_minute=20,
                actor_id=actor_id,
            )
            token = issued.token.get_secret_value()
            issued_tokens.append(token)
            authenticated = await service.authenticate_bearer(f"Bearer {token}")
            assert authenticated.principal_id == service_account.id
            assert authenticated.principal_type is PrincipalType.SERVICE_ACCOUNT
            decision = await AuthorizationService(authorization_repository).decide(
                AuthorizationRequest(
                    actor=authenticated,
                    tenant_id="default",
                    namespace="team.automation",
                    resource_type="flow",
                    action=PermissionAction.VIEW,
                )
            )
            assert decision.allowed
            update_denied = await AuthorizationService(authorization_repository).decide(
                AuthorizationRequest(
                    actor=authenticated,
                    tenant_id="default",
                    namespace="team.automation",
                    resource_type="flow",
                    action=PermissionAction.UPDATE,
                )
            )
            assert update_denied.reason_code == "CREDENTIAL_SCOPE_DENY"
            with pytest.raises(InvalidCredential):
                await service.authenticate_bearer(
                    f"Bearer {token}",
                    audience="amesh-worker",
                )

            rotating_pepper_service = CredentialService(
                repository,
                token_pepper=SecretStr("replacement-integration-pepper"),
                previous_token_pepper=SecretStr("integration-pepper"),
            )
            assert (
                await rotating_pepper_service.authenticate_bearer(f"Bearer {token}")
            ).principal_id == service_account.id
            new_pepper_credential = await rotating_pepper_service.issue(
                service_account.id,
                name="new-pepper",
                scopes=("flow:view",),
                audience="amesh-api",
                expires_at=datetime.now(UTC) + timedelta(hours=1),
                rate_limit_per_minute=20,
                actor_id=actor_id,
            )
            new_pepper_token = new_pepper_credential.token.get_secret_value()
            issued_tokens.append(new_pepper_token)
            assert (
                await rotating_pepper_service.authenticate_bearer(f"Bearer {new_pepper_token}")
            ).credential_id == new_pepper_credential.metadata.id
            with pytest.raises(InvalidCredential):
                await service.authenticate_bearer(f"Bearer {new_pepper_token}")

            quota = await service.issue(
                service_account.id,
                name="one-request",
                scopes=("flow:view",),
                audience="amesh-api",
                expires_at=datetime.now(UTC) + timedelta(hours=1),
                rate_limit_per_minute=1,
                actor_id=actor_id,
            )
            quota_token = quota.token.get_secret_value()
            issued_tokens.append(quota_token)
            await service.authenticate_bearer(f"Bearer {quota_token}")
            with pytest.raises(CredentialRateLimitExceeded):
                await service.authenticate_bearer(f"Bearer {quota_token}")

            replacement = await service.rotate(
                issued.metadata.id,
                overlap_seconds=300,
                actor_id=actor_id,
            )
            replacement_token = replacement.token.get_secret_value()
            issued_tokens.append(replacement_token)
            assert (
                await service.authenticate_bearer(f"Bearer {token}")
            ).credential_id == issued.metadata.id
            assert (
                await service.authenticate_bearer(f"Bearer {replacement_token}")
            ).credential_id == replacement.metadata.id

            parent = await service.issue(
                worker.id,
                name="worker-api",
                scopes=("credential:use", "worker:*"),
                audience="amesh-api",
                expires_at=datetime.now(UTC) + timedelta(hours=1),
                rate_limit_per_minute=20,
                actor_id=actor_id,
            )
            parent_token = parent.token.get_secret_value()
            issued_tokens.append(parent_token)
            parent_actor = await service.authenticate_bearer(f"Bearer {parent_token}")
            derived = await service.exchange(
                parent.metadata.id,
                principal_id=parent_actor.principal_id,
                scopes=("worker:view",),
                audience="amesh-worker",
                expires_in_seconds=300,
                rate_limit_per_minute=3,
            )
            derived_token = derived.token.get_secret_value()
            issued_tokens.append(derived_token)
            derived_actor = await service.authenticate_bearer(
                f"Bearer {derived_token}",
                audience="amesh-worker",
            )
            assert derived_actor.credential_scopes == ("worker:view",)
            assert derived.metadata.expires_at <= datetime.now(UTC) + timedelta(hours=1)

            assert await service.revoke(parent.metadata.id, actor_id=actor_id) == 2
            with pytest.raises(InvalidCredential):
                await service.authenticate_bearer(
                    f"Bearer {derived_token}",
                    audience="amesh-worker",
                )
            assert await service.revoke_all(service_account.id, actor_id=actor_id) >= 2
            with pytest.raises(InvalidCredential):
                await service.authenticate_bearer(f"Bearer {replacement_token}")

            async with engine.connect() as connection:
                column_names = set(
                    await connection.scalars(
                        text(
                            """
                            SELECT column_name
                            FROM information_schema.columns
                            WHERE table_name = 'auth_credentials'
                            """
                        )
                    )
                )
                assert "token_hash" in column_names
                assert "token" not in column_names
                audit_blob = str(
                    await connection.scalar(
                        text(
                            """
                            SELECT COALESCE(string_agg(evidence::text, ''), '')
                            FROM audit_events
                            WHERE resource_type = 'credential'
                              AND (
                                actor_id = :actor_id
                                OR actor_id = ANY(CAST(:principal_ids AS text[]))
                              )
                            """
                        ),
                        {
                            "actor_id": actor_id,
                            "principal_ids": [str(value) for value in principal_ids],
                        },
                    )
                )
                assert all(value not in audit_blob for value in issued_tokens)
                assert (
                    int(
                        await connection.scalar(
                            text(
                                """
                            SELECT count(*)
                            FROM audit_events
                            WHERE resource_type = 'credential'
                              AND outcome = 'FAILURE'
                              AND actor_id = :principal_id
                            """
                            ),
                            {"principal_id": str(service_account.id)},
                        )
                        or 0
                    )
                    >= 2
                )
                assert await connection.scalar(
                    text("SELECT last_used_at IS NOT NULL FROM auth_credentials WHERE id = :id"),
                    {"id": issued.metadata.id},
                )
        finally:
            await _cleanup(engine, principal_ids=principal_ids, actor_id=actor_id)
            await engine.dispose()

    asyncio.run(scenario())
