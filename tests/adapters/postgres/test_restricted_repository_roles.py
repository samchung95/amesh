from __future__ import annotations

import ast
import asyncio
import importlib
import inspect
import os
from uuid import uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresAuditRepository,
    PostgresAuthenticationRepository,
    PostgresAuthorizationRepository,
    PostgresCredentialRepository,
    PostgresFederationRepository,
    PostgresOperationsRepository,
    PostgresServiceRegistryRepository,
    PostgresUpgradeRepository,
)
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.domain import (
    AuthorizationScopeType,
    NamespaceAuthorizationBoundary,
    PrincipalDefinition,
    PrincipalType,
    RoleBinding,
    new_runtime_id,
)
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

RESTRICTED_REPOSITORY_MODULES = (
    "amesh.adapters.postgres.audit_repository",
    "amesh.adapters.postgres.authorization_repository",
    "amesh.adapters.postgres.authentication_repository",
    "amesh.adapters.postgres.credential_repository",
    "amesh.adapters.postgres.federation_repository",
    "amesh.adapters.postgres.operations_repository",
    "amesh.adapters.postgres.service_registry",
    "amesh.adapters.postgres.upgrade_repository",
)


def _raw_engine_context_lines(source: str) -> tuple[int, ...]:
    tree = ast.parse(source)
    violations: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncWith):
            continue
        for item in node.items:
            expression = item.context_expr
            if not isinstance(expression, ast.Call):
                continue
            method = expression.func
            if (
                isinstance(method, ast.Attribute)
                and method.attr in {"begin", "connect"}
                and isinstance(method.value, ast.Attribute)
                and method.value.attr == "_engine"
                and isinstance(method.value.value, ast.Name)
                and method.value.value.id == "self"
            ):
                violations.append(expression.lineno)
    return tuple(violations)


@pytest.mark.parametrize("module_name", RESTRICTED_REPOSITORY_MODULES)
def test_restricted_repository_modules_do_not_open_raw_engine_contexts(
    module_name: str,
) -> None:
    module = importlib.import_module(module_name)
    violations = _raw_engine_context_lines(inspect.getsource(module))

    assert not violations, f"{module_name} opens raw engine contexts at lines {violations}"


@pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
def test_restricted_login_uses_tenant_and_admin_repository_boundaries() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")

        database = await create_ephemeral_database(TEST_DATABASE_URL)
        admin_engine = create_async_engine(database.database_url)
        restricted_engine: AsyncEngine | None = None
        restricted_role_created = False
        suffix = uuid4().hex[:12]
        restricted_role = f"amesh_test_{suffix}"
        restricted_password = uuid4().hex
        tenant_a_id = new_runtime_id()
        tenant_b_id = new_runtime_id()
        tenant_a_slug = f"restricted-a-{suffix}"
        tenant_b_slug = f"restricted-b-{suffix}"
        actor_id = f"test:restricted-repositories:{suffix}"
        projection_name = f"amesh_search_restricted_{suffix}"

        try:
            applied = await apply_migrations(database.database_url, migration_directory())
            assert "0075_restricted_repository_roles.sql" in applied
            assert "0076_authorization_binding_lock_grant.sql" in applied
            assert "0077_restricted_operations_role.sql" in applied
            assert "0078_projection_rebuild_execution_scope.sql" in applied

            async with admin_engine.begin() as connection:
                await connection.execute(
                    text(
                        """
                        INSERT INTO tenants (
                            id, slug, display_name, storage_prefix, created_by, updated_by
                        ) VALUES (
                            :tenant_a_id, :tenant_a_slug, 'Restricted tenant A',
                            :tenant_a_prefix, :actor_id, :actor_id
                        ), (
                            :tenant_b_id, :tenant_b_slug, 'Restricted tenant B',
                            :tenant_b_prefix, :actor_id, :actor_id
                        )
                        """
                    ),
                    {
                        "tenant_a_id": tenant_a_id,
                        "tenant_a_slug": tenant_a_slug,
                        "tenant_a_prefix": f"tenants/{tenant_a_slug}/",
                        "tenant_b_id": tenant_b_id,
                        "tenant_b_slug": tenant_b_slug,
                        "tenant_b_prefix": f"tenants/{tenant_b_slug}/",
                        "actor_id": actor_id,
                    },
                )
                await connection.exec_driver_sql(
                    f'CREATE ROLE "{restricted_role}" LOGIN PASSWORD '
                    f"'{restricted_password}' NOSUPERUSER NOCREATEDB NOCREATEROLE "
                    "NOINHERIT NOBYPASSRLS"
                )
                await connection.exec_driver_sql(f'GRANT amesh_runtime TO "{restricted_role}"')
                await connection.exec_driver_sql(f'GRANT amesh_tenant_admin TO "{restricted_role}"')
                await connection.exec_driver_sql(
                    f'CREATE MATERIALIZED VIEW "{projection_name}" AS SELECT 1 AS value'
                )
            restricted_role_created = True

            async with admin_engine.connect() as connection:
                attributes = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT rolcanlogin, rolinherit, rolsuper, rolcreatedb,
                                       rolcreaterole, rolbypassrls
                                FROM pg_roles
                                WHERE rolname = :role_name
                                """
                            ),
                            {"role_name": restricted_role},
                        )
                    )
                    .mappings()
                    .one()
                )
                memberships = set(
                    await connection.scalars(
                        text(
                            """
                            SELECT granted.rolname
                            FROM pg_auth_members AS memberships
                            JOIN pg_roles AS granted ON granted.oid = memberships.roleid
                            JOIN pg_roles AS member ON member.oid = memberships.member
                            WHERE member.rolname = :role_name
                            """
                        ),
                        {"role_name": restricted_role},
                    )
                )
            assert dict(attributes) == {
                "rolcanlogin": True,
                "rolinherit": False,
                "rolsuper": False,
                "rolcreatedb": False,
                "rolcreaterole": False,
                "rolbypassrls": False,
            }
            assert memberships == {"amesh_runtime", "amesh_tenant_admin"}

            restricted_url = make_url(database.database_url).set(
                username=restricted_role,
                password=restricted_password,
            )
            restricted_engine = create_async_engine(restricted_url)

            with pytest.raises(DBAPIError):
                async with restricted_engine.connect() as connection:
                    assert await connection.scalar(text("SELECT current_user")) == restricted_role
                    await connection.execute(text("SELECT id FROM tenants"))

            with pytest.raises(DBAPIError):
                async with restricted_engine.connect() as connection:
                    await connection.execute(
                        text("SELECT * FROM amesh_rebuild_disposable_projections()")
                    )

            audit = PostgresAuditRepository(restricted_engine)
            authorization = PostgresAuthorizationRepository(restricted_engine)
            authentication = PostgresAuthenticationRepository(restricted_engine)
            credentials = PostgresCredentialRepository(restricted_engine)
            federation = PostgresFederationRepository(
                restricted_engine,
                token_pepper=SecretStr(uuid4().hex),
            )
            operations = PostgresOperationsRepository(restricted_engine)
            service_registry = PostgresServiceRegistryRepository(restricted_engine)
            upgrade = PostgresUpgradeRepository(restricted_engine)

            audit_a = await audit.record_model_engine_account_action(
                tenant_a_slug,
                actor_id=actor_id,
                namespace="team.alpha",
                adapter="restricted-test",
                engine_ref="tenant-a",
                action="status",
                outcome="SUCCESS",
            )
            audit_b = await audit.record_model_engine_account_action(
                tenant_b_slug,
                actor_id=actor_id,
                namespace="team.beta",
                adapter="restricted-test",
                engine_ref="tenant-b",
                action="status",
                outcome="SUCCESS",
            )
            page_a = await audit.list_events(
                tenant_a_slug,
                actor_id=actor_id,
                action="model_engine.account.status",
                record_access=False,
            )
            page_b = await audit.list_events(
                tenant_b_slug,
                actor_id=actor_id,
                action="model_engine.account.status",
                record_access=False,
            )
            assert {event.event_id for event in page_a.items} == {audit_a}
            assert {event.event_id for event in page_b.items} == {audit_b}

            principal = PrincipalDefinition(
                principal_type=PrincipalType.USER,
                handle=f"restricted-user-{suffix}",
                display_name="Restricted repository user",
            )
            await authorization.create_principal(principal, actor_id=actor_id)
            boundary_a = NamespaceAuthorizationBoundary(
                tenant_id=tenant_a_slug,
                namespace="team.alpha",
            )
            boundary_b = NamespaceAuthorizationBoundary(
                tenant_id=tenant_b_slug,
                namespace="team.beta",
            )
            binding_a = RoleBinding(
                principal_id=principal.id,
                principal_type=PrincipalType.USER,
                role_name="viewer",
                scope_type=AuthorizationScopeType.NAMESPACE,
                tenant_id=tenant_a_slug,
                namespace=boundary_a.namespace,
            )
            binding_b = RoleBinding(
                principal_id=principal.id,
                principal_type=PrincipalType.USER,
                role_name="viewer",
                scope_type=AuthorizationScopeType.NAMESPACE,
                tenant_id=tenant_b_slug,
                namespace=boundary_b.namespace,
            )
            await authorization.set_namespace_boundary(boundary_a, actor_id=actor_id)
            await authorization.set_namespace_boundary(boundary_b, actor_id=actor_id)
            await authorization.create_binding(binding_a, actor_id=actor_id)
            await authorization.create_binding(binding_b, actor_id=actor_id)

            for tenant_slug, tenant_id, boundary, binding in (
                (tenant_a_slug, tenant_a_id, boundary_a, binding_a),
                (tenant_b_slug, tenant_b_id, boundary_b, binding_b),
            ):
                async with tenant_transaction(restricted_engine, tenant_slug) as (
                    connection,
                    resolved_tenant_id,
                ):
                    assert resolved_tenant_id == tenant_id
                    assert await connection.scalar(text("SELECT current_user")) == "amesh_runtime"
                    visible_boundaries = set(
                        (
                            await connection.execute(
                                text(
                                    "SELECT tenant_id, namespace_name "
                                    "FROM auth_namespace_boundaries"
                                )
                            )
                        ).all()
                    )
                    visible_bindings = set(
                        (
                            await connection.execute(
                                text(
                                    "SELECT id, tenant_id FROM auth_role_bindings "
                                    "WHERE tenant_id IS NOT NULL"
                                )
                            )
                        ).all()
                    )
                assert visible_boundaries == {(tenant_id, boundary.namespace)}
                assert visible_bindings == {(binding.id, tenant_id)}

            with pytest.raises(DBAPIError):
                async with tenant_transaction(restricted_engine, tenant_a_slug) as (
                    connection,
                    _tenant_id,
                ):
                    await connection.execute(
                        text("SELECT * FROM amesh_rebuild_disposable_projections()")
                    )

            assert principal.id in {item.id for item in await authorization.list_principals()}
            assert {binding_a.id, binding_b.id} <= {
                item.id for item in await authorization.list_bindings()
            }
            await authorization.delete_binding(binding_a.id, actor_id=actor_id)
            assert binding_a.id not in {item.id for item in await authorization.list_bindings()}
            assert await authentication.load_local_identity(principal.handle) is None
            assert await credentials.list_credentials(principal.id) == []
            assert await federation.list_scim(f"missing-{suffix}", "User") == ()

            checkpoint = await operations.record_backup_checkpoint(
                f"s3://restricted-tests/{suffix}/manifest.json",
                "a" * 64,
                created_by=actor_id,
            )
            assert await operations.latest_backup_checkpoint() == checkpoint
            assert set(await operations.prepare_restored_state()) == {
                "serviceInstancesStopped",
                "workersStopped",
                "queueClaimsExpired",
                "taskAttemptLeasesExpired",
                "genericLeasesExpired",
                "schedulerOwnersCleared",
            }
            assert projection_name in await operations.rebuild_disposable_projections()
            assert (await service_registry.topology()).instances == ()
            inventory = await upgrade.inventory()
            assert "0078_projection_rebuild_execution_scope.sql" in inventory.applied_migrations
            assert {tenant_a_slug, tenant_b_slug} <= set(await upgrade.tenant_slugs())
        finally:
            try:
                if restricted_engine is not None:
                    await restricted_engine.dispose()
                if restricted_role_created:
                    async with admin_engine.begin() as connection:
                        await connection.exec_driver_sql(
                            f'REVOKE amesh_tenant_admin FROM "{restricted_role}"'
                        )
                        await connection.exec_driver_sql(
                            f'REVOKE amesh_runtime FROM "{restricted_role}"'
                        )
                        await connection.exec_driver_sql(f'DROP ROLE "{restricted_role}"')
            finally:
                await admin_engine.dispose()
                await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
