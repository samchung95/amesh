from __future__ import annotations

import asyncio
from collections.abc import Sequence
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository, PostgresTenantRepository
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.domain import TenantDefinition, TenantPolicy, TenantStatus, new_runtime_id
from amesh.dsl import FlowDefinition
from amesh.dsl.models import TaskDefinition
from amesh.ports import TenantQuotaExceeded, TenantUnavailableError
from amesh.tenancy import TenantService


async def _cleanup(engine: AsyncEngine, tenant_ids: Sequence[object], actor_id: str) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM namespaces WHERE tenant_id = ANY(CAST(:tenant_ids AS uuid[]))"),
            {"tenant_ids": tenant_ids},
        )
        await connection.execute(
            text("DELETE FROM audit_events WHERE actor_id = :actor_id"),
            {"actor_id": actor_id},
        )
        await connection.execute(
            text("DELETE FROM tenants WHERE id = ANY(CAST(:tenant_ids AS uuid[]))"),
            {"tenant_ids": tenant_ids},
        )


def test_tenant_lifecycle_policy_export_workers_and_rls_isolation(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresTenantRepository(engine)
        service = TenantService(repository)
        suffix = uuid4().hex[:10]
        actor_id = f"test:tenant:{suffix}"
        first = TenantDefinition(
            slug=f"tenant-a-{suffix}",
            display_name="Tenant A",
            policy=TenantPolicy(
                retention_days=7,
                max_concurrent_executions=2,
                encryption_key_ref="kms://tenant-a",
                identity_provider_refs=("oidc-a",),
                plugin_allowlist=("core.http",),
                feature_flags={"executions": True},
                worker_groups=("regulated",),
            ),
        )
        second = TenantDefinition(
            slug=f"tenant-b-{suffix}",
            display_name="Tenant B",
            policy=TenantPolicy(worker_groups=("general",)),
        )
        tenant_ids = [first.id, second.id]
        restricted_role = f"amesh_test_{suffix}"
        restricted_password = uuid4().hex
        restricted_engine: AsyncEngine | None = None
        restricted_role_created = False
        try:
            persisted_first = await repository.create(first, actor_id=actor_id)
            await repository.create(second, actor_id=actor_id)
            assert persisted_first.id.version == 7
            assert persisted_first.policy.encryption_key_ref == "kms://tenant-a"
            assert first.slug in await repository.list_active_for_worker_group("regulated")
            assert first.slug not in await repository.list_active_for_worker_group("general")
            assert {item.slug for item in await repository.list()} >= {first.slug, second.slug}

            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        """
                        INSERT INTO namespaces (id, tenant_id, name)
                        VALUES (:first_id, :first_tenant, 'shared'),
                               (:second_id, :second_tenant, 'shared')
                        """
                    ),
                    {
                        "first_id": new_runtime_id(),
                        "first_tenant": first.id,
                        "second_id": new_runtime_id(),
                        "second_tenant": second.id,
                    },
                )

            async with tenant_transaction(engine, first.slug) as (connection, tenant_id):
                assert tenant_id == first.id
                assert await connection.scalar(text("SELECT current_user")) == "amesh_runtime"
                visible = set(await connection.scalars(text("SELECT tenant_id FROM namespaces")))
                assert visible == {first.id}
            with pytest.raises(DBAPIError):
                async with tenant_transaction(engine, first.slug) as (connection, _tenant_id):
                    await connection.execute(
                        text(
                            """
                            INSERT INTO namespaces (id, tenant_id, name)
                            VALUES (:id, :tenant_id, 'cross-tenant-write')
                            """
                        ),
                        {"id": new_runtime_id(), "tenant_id": second.id},
                    )

            async with engine.begin() as connection:
                await connection.exec_driver_sql(
                    f'CREATE ROLE "{restricted_role}" LOGIN PASSWORD '
                    f"'{restricted_password}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT "
                    "NOBYPASSRLS"
                )
                await connection.exec_driver_sql(f'GRANT amesh_runtime TO "{restricted_role}"')
                await connection.exec_driver_sql(f'GRANT amesh_tenant_admin TO "{restricted_role}"')
            restricted_role_created = True
            restricted_url = make_url(migrated_test_database_url).set(
                username=restricted_role,
                password=restricted_password,
            )
            restricted_engine = create_async_engine(restricted_url)
            restricted_repository = PostgresTenantRepository(restricted_engine)
            with pytest.raises(DBAPIError):
                async with restricted_engine.connect() as connection:
                    await connection.execute(text("SELECT id FROM tenants"))
            assert (await restricted_repository.get(first.slug)).id == first.id
            assert first.slug in await restricted_repository.list_active_for_worker_group(
                "regulated"
            )
            async with tenant_transaction(
                restricted_engine,
                first.slug,
            ) as (connection, restricted_tenant_id):
                assert restricted_tenant_id == first.id
                assert await connection.scalar(text("SELECT current_user")) == "amesh_runtime"
                visible = set(await connection.scalars(text("SELECT tenant_id FROM namespaces")))
                assert visible == {first.id}

            exported = await service.export(first.slug, actor_id=actor_id)
            assert exported.tenant.slug == first.slug
            assert exported.resource_counts["namespaces"] == 1
            suspended = await service.suspend(first.slug, actor_id=actor_id)
            assert suspended.status is TenantStatus.SUSPENDED
            with pytest.raises(TenantUnavailableError):
                await repository.require_active(first.slug)
            assert first.slug not in await repository.list_active_for_worker_group("regulated")
            restored = await service.restore(first.slug, actor_id=actor_id)
            assert restored.status is TenantStatus.ACTIVE
            tombstoned = await service.delete(first.slug, actor_id=actor_id)
            assert tombstoned.status is TenantStatus.TOMBSTONED
            assert (
                await service.restore(first.slug, actor_id=actor_id)
            ).status is TenantStatus.ACTIVE

            async with engine.connect() as connection:
                audit_rows = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT tenant_id, evidence
                                FROM audit_events
                                WHERE actor_id = :actor_id
                                """
                            ),
                            {"actor_id": actor_id},
                        )
                    )
                    .mappings()
                    .all()
                )
                assert audit_rows
                assert all(row["tenant_id"] is not None for row in audit_rows)
                assert all(row["evidence"]["superAdmin"] is True for row in audit_rows)
        finally:
            if restricted_engine is not None:
                await restricted_engine.dispose()
            if restricted_role_created:
                async with engine.begin() as connection:
                    await connection.exec_driver_sql(
                        f'REVOKE amesh_tenant_admin FROM "{restricted_role}"'
                    )
                    await connection.exec_driver_sql(
                        f'REVOKE amesh_runtime FROM "{restricted_role}"'
                    )
                    await connection.exec_driver_sql(f'DROP ROLE "{restricted_role}"')
            await _cleanup(engine, tenant_ids, actor_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_tenant_plugin_feature_and_concurrency_policy_are_enforced(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        tenant_repository = PostgresTenantRepository(engine)
        execution_repository = PostgresExecutionRepository(engine)
        suffix = uuid4().hex[:10]
        actor_id = f"test:tenant-policy:{suffix}"
        tenant = TenantDefinition(
            slug=f"tenant-policy-{suffix}",
            display_name="Tenant policy enforcement",
            policy=TenantPolicy(
                max_concurrent_executions=1,
                plugin_allowlist=("core.return",),
                feature_flags={"executions": False},
                worker_groups=("policy-workers",),
            ),
        )
        flow = FlowDefinition(
            id="allowed",
            namespace=f"tests.tenant.policy.{suffix}",
            tasks=[TaskDefinition(id="done", type="core.return")],
        )
        try:
            await tenant_repository.create(tenant, actor_id=actor_id)
            await execution_repository.apply_flow(
                flow,
                tenant_id=tenant.slug,
                actor_id=actor_id,
            )
            with pytest.raises(TenantQuotaExceeded, match="feature is disabled"):
                await execution_repository.create_execution(
                    flow,
                    tenant_id=tenant.slug,
                    inputs={},
                    actor_id=actor_id,
                )

            await tenant_repository.set_policy(
                tenant.slug,
                tenant.policy.model_copy(update={"feature_flags": {"executions": True}}),
                actor_id=actor_id,
            )
            await execution_repository.create_execution(
                flow,
                tenant_id=tenant.slug,
                inputs={},
                actor_id=actor_id,
            )
            with pytest.raises(TenantQuotaExceeded, match="concurrent execution quota"):
                await execution_repository.create_execution(
                    flow,
                    tenant_id=tenant.slug,
                    inputs={},
                    actor_id=actor_id,
                )

            disallowed = flow.model_copy(
                update={
                    "id": "disallowed",
                    "tasks": [TaskDefinition(id="log", type="core.log")],
                }
            )
            with pytest.raises(ValueError, match="plugin policy does not allow"):
                await execution_repository.apply_flow(
                    disallowed,
                    tenant_id=tenant.slug,
                    actor_id=actor_id,
                )
            assert tenant.slug in await tenant_repository.list_active_for_worker_group(
                "policy-workers"
            )
        finally:
            async with engine.begin() as connection:
                parameters = {"tenant_id": tenant.id}
                for table in (
                    "messages_outbox",
                    "transition_rejections",
                    "task_run_events",
                    "task_attempts",
                    "task_runs",
                    "execution_events",
                    "executions",
                ):
                    await connection.execute(
                        text(f"DELETE FROM {table} WHERE tenant_id = :tenant_id"),
                        parameters,
                    )
                await connection.execute(
                    text("UPDATE flows SET active_revision = NULL WHERE tenant_id = :tenant_id"),
                    parameters,
                )
                for table in ("flow_revisions", "flows", "namespaces"):
                    await connection.execute(
                        text(f"DELETE FROM {table} WHERE tenant_id = :tenant_id"),
                        parameters,
                    )
                await connection.execute(
                    text("DELETE FROM audit_events WHERE actor_id = :actor_id"),
                    {"actor_id": actor_id},
                )
                await connection.execute(
                    text("DELETE FROM tenants WHERE id = :tenant_id"),
                    parameters,
                )
            await engine.dispose()

    asyncio.run(scenario())
