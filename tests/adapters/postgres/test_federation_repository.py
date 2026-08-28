from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresFederationRepository,
)
from amesh.config import IdentityGroupMapping
from amesh.domain import (
    FederatedClaims,
    FederationProtocol,
    FederationState,
    PrincipalDefinition,
    PrincipalType,
)
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)
from amesh.ports.federation_repository import (
    AmbiguousFederatedIdentity,
    FederationReplayRejected,
    FederationStateRejected,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_federated_identity_state_mapping_replay_and_scim_lifecycle() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        try:
            await apply_migrations(database.database_url, migration_directory())
            engine = create_async_engine(database.database_url)
            repository = PostgresFederationRepository(
                engine,
                token_pepper=SecretStr("federation-test-pepper"),
            )
            authorization = PostgresAuthorizationRepository(engine)
            group = await authorization.create_principal(
                PrincipalDefinition(
                    principal_type=PrincipalType.GROUP,
                    handle="federated-engineers",
                    display_name="Federated engineers",
                ),
                actor_id="test:federation",
            )
            now = datetime.now(UTC)
            state = FederationState(
                provider_id="corporate-oidc",
                protocol=FederationProtocol.OIDC,
                nonce="nonce",
                code_verifier="verifier",
                tenant_slug="default",
                return_to="/flows",
                expires_at=now + timedelta(minutes=5),
            )
            await repository.create_state("opaque-state", state)
            consumed = await repository.consume_state(
                "opaque-state",
                provider_id="corporate-oidc",
                now=now,
            )
            assert consumed.nonce == "nonce"
            with pytest.raises(FederationStateRejected):
                await repository.consume_state(
                    "opaque-state",
                    provider_id="corporate-oidc",
                    now=now,
                )

            identity = await repository.resolve_identity(
                FederatedClaims(
                    provider_id="corporate-oidc",
                    subject="idp-subject-123",
                    email="ada@example.com",
                    display="Ada Lovelace",
                    groups=("Engineering",),
                ),
                group_mappings=(
                    IdentityGroupMapping(
                        external="Engineering",
                        platformGroup="federated-engineers",
                    ),
                ),
                default_tenant="default",
                default_role="viewer",
            )
            repeated = await repository.resolve_identity(
                FederatedClaims(
                    provider_id="corporate-oidc",
                    subject="idp-subject-123",
                    email="ada@example.com",
                    display="Ada L.",
                    groups=(),
                ),
                group_mappings=(
                    IdentityGroupMapping(
                        external="Engineering",
                        platformGroup="federated-engineers",
                    ),
                ),
                default_tenant="default",
                default_role="viewer",
            )
            assert repeated.principal_id == identity.principal_id
            with pytest.raises(AmbiguousFederatedIdentity):
                await repository.resolve_identity(
                    FederatedClaims(
                        provider_id="other-oidc",
                        subject="attacker-subject",
                        email="ada@example.com",
                        display="Not Ada",
                    ),
                    group_mappings=(),
                    default_tenant=None,
                    default_role=None,
                )

            await repository.record_assertion(
                "corporate-saml",
                "assertion-1",
                expires_at=now + timedelta(minutes=5),
            )
            with pytest.raises(FederationReplayRejected):
                await repository.record_assertion(
                    "corporate-saml",
                    "assertion-1",
                    expires_at=now + timedelta(minutes=5),
                )

            scim_user = await repository.create_scim(
                "entra",
                "User",
                handle="scim-grace-example-com",
                resource_name="grace@example.com",
                display_name="Grace Hopper",
                enabled=True,
                external_id="entra-user-1",
                tenant="default",
                role="viewer",
            )
            scim_group = await repository.create_scim(
                "entra",
                "Group",
                handle="scim-platform-team",
                resource_name="Platform team",
                display_name="Platform team",
                enabled=True,
                external_id="entra-group-1",
                tenant="default",
                role="viewer",
                member_ids=(scim_user.principal_id,),
            )
            assert scim_group.member_ids == (scim_user.principal_id,)
            filtered = await repository.list_scim(
                "entra",
                "User",
                handle="grace@example.com",
            )
            assert [item.principal_id for item in filtered] == [scim_user.principal_id]
            disabled = await repository.update_scim(
                "entra",
                "User",
                scim_user.principal_id,
                enabled=False,
            )
            assert not disabled.enabled
            emptied = await repository.update_scim(
                "entra",
                "Group",
                scim_group.principal_id,
                member_ids=(),
            )
            assert emptied.member_ids == ()
            await repository.delete_scim("entra", "User", scim_user.principal_id)
            with pytest.raises(LookupError):
                await repository.get_scim("entra", "User", scim_user.principal_id)

            async with engine.connect() as connection:
                membership_count = int(
                    await connection.scalar(
                        text(
                            """
                            SELECT count(*) FROM auth_group_memberships
                            WHERE group_id = :group_id AND member_id = :member_id
                            """
                        ),
                        {"group_id": group.id, "member_id": identity.principal_id},
                    )
                    or 0
                )
                tenant_binding_count = int(
                    await connection.scalar(
                        text(
                            """
                            SELECT count(*) FROM auth_role_bindings
                            WHERE principal_id = :principal_id AND role_name = 'viewer'
                              AND scope_type = 'TENANT'
                            """
                        ),
                        {"principal_id": identity.principal_id},
                    )
                    or 0
                )
                audit_actions = set(
                    (
                        await connection.scalars(
                            text(
                                """
                                SELECT action FROM audit_events
                                WHERE actor_id LIKE 'identity-provider:%'
                                """
                            )
                        )
                    ).all()
                )
            assert membership_count == 0
            assert tenant_binding_count == 1
            assert "federation.identity.provision" in audit_actions
            assert "scim.user.delete" in audit_actions
            await engine.dispose()
        finally:
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
