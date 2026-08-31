from __future__ import annotations

import asyncio
import os
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresAuthorizationRepository
from amesh.authorization import AuthorizationService
from amesh.domain import (
    ActorContext,
    AuthorizationRequest,
    AuthorizationScopeType,
    Permission,
    PermissionAction,
    PrincipalDefinition,
    PrincipalType,
    RoleBinding,
    RoleDefinition,
)
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)
from amesh.ports import LastAdministratorError

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_session_administration_roles_and_fleet_indexes_migrate_cleanly() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, migration_directory())
            roles = {
                role.name: role
                for role in await PostgresAuthorizationRepository(engine).list_roles()
            }
            assert {
                "session-client",
                "session-operator",
                "session-admin",
            } <= roles.keys()
            assert Permission(
                resource_type="agent_session_migration",
                action=PermissionAction.MANAGE,
            ) in roles["session-admin"].permissions

            async with engine.connect() as connection:
                indexes = set(
                    (
                        await connection.execute(
                            text(
                                "SELECT indexname FROM pg_indexes "
                                "WHERE schemaname = 'public' AND indexname IN "
                                "('executions_agent_session_fleet_keyset_idx', "
                                "'agent_sessions_latest_attempt_idx')"
                            )
                        )
                    ).scalars()
                )
            assert indexes == {
                "executions_agent_session_fleet_keyset_idx",
                "agent_sessions_latest_attempt_idx",
            }
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


async def _cleanup(
    engine: AsyncEngine,
    *,
    principal_ids: list[UUID],
    role_name: str,
    actor_id: str,
) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM auth_principals WHERE id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": principal_ids},
        )
        await connection.execute(
            text("DELETE FROM auth_roles WHERE name = :name"),
            {"name": role_name},
        )
        await connection.execute(
            text("DELETE FROM audit_events WHERE actor_id = :actor_id"),
            {"actor_id": actor_id},
        )


def test_postgres_policy_persistence_cache_revocation_and_last_admin_guard() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresAuthorizationRepository(engine)
        suffix = uuid4().hex[:12]
        actor_id = f"test:authorization:{suffix}"
        role_name = f"test-reader-{suffix}"
        user = PrincipalDefinition(
            principal_type=PrincipalType.USER,
            handle=f"user-{suffix}",
            display_name="Policy user",
        )
        group = PrincipalDefinition(
            principal_type=PrincipalType.GROUP,
            handle=f"group-{suffix}",
            display_name="Policy group",
        )
        second_admin = PrincipalDefinition(
            principal_type=PrincipalType.USER,
            handle=f"admin-{suffix}",
            display_name="Second administrator",
        )
        principal_ids = [user.id, group.id, second_admin.id]
        try:
            persisted_user = await repository.create_principal(user, actor_id=actor_id)
            await repository.create_principal(group, actor_id=actor_id)
            await repository.create_principal(second_admin, actor_id=actor_id)
            assert persisted_user.id.version == 7

            await repository.add_group_member(group.id, user.id, actor_id=actor_id)
            role = RoleDefinition(
                name=role_name,
                display_name="Test reader",
                permissions=(Permission(resource_type="flow", action=PermissionAction.VIEW),),
            )
            await repository.upsert_role(role, actor_id=actor_id)
            with pytest.raises(ValueError, match="principal type"):
                await repository.create_binding(
                    RoleBinding(
                        principal_id=user.id,
                        principal_type=PrincipalType.GROUP,
                        role_name=role_name,
                        scope_type=AuthorizationScopeType.TENANT,
                        tenant_id="default",
                    ),
                    actor_id=actor_id,
                )
            binding = RoleBinding(
                principal_id=group.id,
                principal_type=PrincipalType.GROUP,
                role_name=role_name,
                scope_type=AuthorizationScopeType.TENANT,
                tenant_id="default",
            )
            await repository.create_binding(binding, actor_id=actor_id)
            assert binding.id.version == 7

            actor = ActorContext(
                principal_id=user.id,
                principal_type=PrincipalType.USER,
                display=user.handle,
            )
            request = AuthorizationRequest(
                actor=actor,
                tenant_id="default",
                resource_type="flow",
                action=PermissionAction.VIEW,
            )
            service = AuthorizationService(repository)
            assert (await service.decide(request)).allowed

            version_before_membership_revoke = await repository.policy_version()
            await repository.remove_group_member(group.id, user.id, actor_id=actor_id)
            assert await repository.policy_version() > version_before_membership_revoke
            assert not (await service.decide(request)).allowed

            await repository.add_group_member(group.id, user.id, actor_id=actor_id)
            assert (await service.decide(request)).allowed

            version_before_revoke = await repository.policy_version()
            await repository.delete_binding(binding.id, actor_id=actor_id)
            assert await repository.policy_version() > version_before_revoke
            assert not (await service.decide(request)).allowed

            first_admin_binding = RoleBinding(
                principal_id=user.id,
                principal_type=PrincipalType.USER,
                role_name="instance-admin",
                scope_type=AuthorizationScopeType.INSTANCE,
            )
            await repository.create_binding(first_admin_binding, actor_id=actor_id)
            with pytest.raises(LastAdministratorError):
                await repository.delete_binding(first_admin_binding.id, actor_id=actor_id)

            second_admin_binding = RoleBinding(
                principal_id=second_admin.id,
                principal_type=PrincipalType.USER,
                role_name="instance-admin",
                scope_type=AuthorizationScopeType.INSTANCE,
            )
            await repository.create_binding(second_admin_binding, actor_id=actor_id)
            await repository.delete_binding(first_admin_binding.id, actor_id=actor_id)

            group_admin_binding = RoleBinding(
                principal_id=group.id,
                principal_type=PrincipalType.GROUP,
                role_name="instance-admin",
                scope_type=AuthorizationScopeType.INSTANCE,
            )
            await repository.create_binding(group_admin_binding, actor_id=actor_id)
            await repository.delete_binding(second_admin_binding.id, actor_id=actor_id)
            with pytest.raises(LastAdministratorError):
                await repository.remove_group_member(group.id, user.id, actor_id=actor_id)

            assert role_name in {item.name for item in await repository.list_roles()}
            assert {item.id for item in await repository.list_principals()} >= set(principal_ids)
            assert group_admin_binding.id in {item.id for item in await repository.list_bindings()}
        finally:
            await _cleanup(
                engine,
                principal_ids=principal_ids,
                role_name=role_name,
                actor_id=actor_id,
            )
            await engine.dispose()

    asyncio.run(scenario())
