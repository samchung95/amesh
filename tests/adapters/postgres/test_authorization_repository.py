from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresAuthorizationRepository, PostgresTenantRepository
from amesh.authorization import AuthorizationService
from amesh.domain import (
    ActorContext,
    AuthorizationRequest,
    AuthorizationScopeType,
    NamespaceAuthorizationBoundary,
    Permission,
    PermissionAction,
    PrincipalDefinition,
    PrincipalType,
    RoleBinding,
    RoleDefinition,
    TenantDefinition,
)
from amesh.ports import LastAdministratorError


def test_session_administration_roles_and_fleet_indexes_migrate_cleanly(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            roles = {
                role.name: role
                for role in await PostgresAuthorizationRepository(engine).list_roles()
            }
            assert {
                "session-client",
                "session-operator",
                "session-admin",
            } <= roles.keys()
            assert (
                Permission(
                    resource_type="agent_session_migration",
                    action=PermissionAction.MANAGE,
                )
                in roles["session-admin"].permissions
            )

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


def test_postgres_policy_persistence_cache_revocation_and_last_admin_guard(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
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


def test_policy_snapshot_only_lists_boundaries_for_reachable_tenants(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresAuthorizationRepository(engine)
        tenant_repository = PostgresTenantRepository(engine)
        suffix = uuid4().hex[:12]
        actor_id = f"test:authorization-boundaries:{suffix}"
        user = PrincipalDefinition(
            principal_type=PrincipalType.USER,
            handle=f"boundary-user-{suffix}",
            display_name="Boundary policy user",
        )
        group = PrincipalDefinition(
            principal_type=PrincipalType.GROUP,
            handle=f"boundary-group-{suffix}",
            display_name="Boundary policy group",
        )
        other_tenant = TenantDefinition(
            slug=f"boundary-other-{suffix}",
            display_name="Unreachable boundary tenant",
        )
        reachable_boundary = NamespaceAuthorizationBoundary(
            tenant_id="default",
            namespace=f"tests.reachable.{suffix}",
        )
        unreachable_boundary = NamespaceAuthorizationBoundary(
            tenant_id=other_tenant.slug,
            namespace=f"tests.unreachable.{suffix}",
        )
        tenant_binding = RoleBinding(
            principal_id=group.id,
            principal_type=PrincipalType.GROUP,
            role_name="viewer",
            scope_type=AuthorizationScopeType.TENANT,
            tenant_id="default",
        )
        instance_binding = RoleBinding(
            principal_id=user.id,
            principal_type=PrincipalType.USER,
            role_name="viewer",
            scope_type=AuthorizationScopeType.INSTANCE,
        )
        try:
            await tenant_repository.create(other_tenant, actor_id=actor_id)
            await repository.create_principal(user, actor_id=actor_id)
            await repository.create_principal(group, actor_id=actor_id)
            await repository.add_group_member(group.id, user.id, actor_id=actor_id)
            await repository.create_binding(tenant_binding, actor_id=actor_id)
            await repository.create_binding(instance_binding, actor_id=actor_id)
            await repository.set_namespace_boundary(reachable_boundary, actor_id=actor_id)
            await repository.set_namespace_boundary(unreachable_boundary, actor_id=actor_id)

            snapshot = await repository.load_policy_snapshot(
                user.id,
                expected_version=await repository.policy_version(),
            )

            assert {binding.id for binding in snapshot.bindings} >= {
                tenant_binding.id,
                instance_binding.id,
            }
            assert reachable_boundary in snapshot.boundaries
            assert unreachable_boundary not in snapshot.boundaries
            assert {boundary.tenant_id for boundary in snapshot.boundaries} == {"default"}
        finally:
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "DELETE FROM auth_namespace_boundaries "
                        "WHERE tenant_id = (SELECT id FROM tenants WHERE slug = 'default') "
                        "AND namespace_name = :namespace"
                    ),
                    {"namespace": reachable_boundary.namespace},
                )
                await connection.execute(
                    text("DELETE FROM auth_principals WHERE id = ANY(CAST(:ids AS uuid[]))"),
                    {"ids": [user.id, group.id]},
                )
                await connection.execute(
                    text("DELETE FROM audit_events WHERE actor_id = :actor_id"),
                    {"actor_id": actor_id},
                )
                await connection.execute(
                    text("DELETE FROM tenants WHERE id = :tenant_id"),
                    {"tenant_id": other_tenant.id},
                )
            await engine.dispose()

    asyncio.run(scenario())
