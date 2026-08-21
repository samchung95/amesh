from __future__ import annotations

import asyncio
import os
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresExecutionRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.domain import (
    ActorContext,
    AuthorizationScopeType,
    PrincipalDefinition,
    PrincipalType,
    RoleBinding,
)
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


async def cleanup_execution_tree(engine: AsyncEngine, root_id: UUID) -> None:
    async with engine.connect() as connection:
        child_ids = list(
            (
                await connection.execute(
                    text(
                        "SELECT child_execution_id FROM execution_subflows "
                        "WHERE parent_execution_id = :root_id ORDER BY created_at"
                    ),
                    {"root_id": root_id},
                )
            ).scalars()
        )
    execution_ids = [*child_ids, root_id]
    async with engine.begin() as connection:
        await connection.execute(
            text(
                "DELETE FROM execution_subflows WHERE parent_execution_id = ANY(:ids) "
                "OR child_execution_id = ANY(:ids)"
            ),
            {"ids": execution_ids},
        )
        for execution_id in execution_ids:
            await connection.execute(
                text("DELETE FROM messages_outbox WHERE partition_key = :partition_key"),
                {"partition_key": f"execution:{execution_id}"},
            )
            await connection.execute(
                text(
                    "DELETE FROM transition_rejections WHERE "
                    "(aggregate_type = 'execution' AND aggregate_id = :execution_id) OR "
                    "(aggregate_type = 'task_run' AND aggregate_id IN "
                    "(SELECT id FROM task_runs WHERE execution_id = :execution_id))"
                ),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM task_run_events WHERE execution_id = :execution_id"),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text(
                    "DELETE FROM task_attempts WHERE task_run_id IN "
                    "(SELECT id FROM task_runs WHERE execution_id = :execution_id)"
                ),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM task_runs WHERE execution_id = :execution_id"),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM execution_events WHERE execution_id = :execution_id"),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM executions WHERE id = :execution_id"),
                {"execution_id": execution_id},
            )


async def cleanup_flows(engine: AsyncEngine, namespaces: tuple[str, ...]) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                "DELETE FROM trigger_definitions WHERE flow_revision_id IN ("
                "SELECT revisions.id FROM flow_revisions revisions "
                "JOIN flows ON flows.id = revisions.flow_id "
                "JOIN namespaces ON namespaces.id = flows.namespace_id "
                "WHERE namespaces.name = ANY(:namespaces))"
            ),
            {"namespaces": list(namespaces)},
        )
        await connection.execute(
            text(
                "UPDATE flows SET active_revision = NULL WHERE namespace_id IN ("
                "SELECT id FROM namespaces WHERE name = ANY(:namespaces))"
            ),
            {"namespaces": list(namespaces)},
        )
        await connection.execute(
            text(
                "DELETE FROM flow_revisions WHERE flow_id IN ("
                "SELECT flows.id FROM flows JOIN namespaces "
                "ON namespaces.id = flows.namespace_id "
                "WHERE namespaces.name = ANY(:namespaces))"
            ),
            {"namespaces": list(namespaces)},
        )
        await connection.execute(
            text(
                "DELETE FROM flows WHERE namespace_id IN ("
                "SELECT id FROM namespaces WHERE name = ANY(:namespaces))"
            ),
            {"namespaces": list(namespaces)},
        )
        await connection.execute(
            text("DELETE FROM namespaces WHERE name = ANY(:namespaces)"),
            {"namespaces": list(namespaces)},
        )


def test_subflow_execution_and_lineage_api() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        authorization_repository = PostgresAuthorizationRepository(engine)
        authorization_service = AuthorizationService(authorization_repository)
        tenant_service = TenantService(PostgresTenantRepository(engine))
        settings = Settings(
            database_url=TEST_DATABASE_URL,
            amesh_admin_token="test-token",
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_authorization_service] = lambda: authorization_service
        app.dependency_overrides[get_tenant_service] = lambda: tenant_service
        app.dependency_overrides[get_settings] = lambda: settings
        suffix = uuid4().hex
        parent_namespace = f"tests.api.subflow.parent.{suffix}"
        child_namespace = f"tests.api.subflow.child.{suffix}"
        system_namespace = f"tests.api.subflow.system.{suffix}"
        headers = {
            "authorization": "Bearer test-token",
            "content-type": "application/yaml",
        }
        audit_actor = f"tests:subflow-api:{suffix}"
        principal = PrincipalDefinition(
            principal_type=PrincipalType.USER,
            handle=f"subflow-author-{suffix}",
            display_name="Subflow author",
        )
        restricted_actor = ActorContext(
            principal_id=principal.id,
            principal_type=principal.principal_type,
            display=principal.handle,
        )
        await authorization_repository.create_principal(principal, actor_id=audit_actor)
        await authorization_repository.create_binding(
            RoleBinding(
                principal_id=principal.id,
                principal_type=principal.principal_type,
                role_name="flow-author",
                scope_type=AuthorizationScopeType.NAMESPACE,
                tenant_id="default",
                namespace=parent_namespace,
            ),
            actor_id=audit_actor,
        )
        parent_execution_id: UUID | None = None
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                child = await client.put(
                    "/api/v1/flows",
                    headers=headers,
                    content=f"""
id: greeting
namespace: {child_namespace}
inputs:
  - id: name
    type: string
    required: true
tasks:
  - id: result
    type: core.return
    value: "hello {{{{ inputs.name }}}}"
""",
                )
                system_child = await client.put(
                    "/api/v1/flows",
                    headers=headers,
                    content=f"""
id: notify
namespace: {system_namespace}
system: true
tasks:
  - id: result
    type: core.return
    value: notified
""",
                )
                parent = await client.put(
                    "/api/v1/flows",
                    headers=headers,
                    content=f"""
id: parent
namespace: {parent_namespace}
inputs:
  - id: person
    type: string
    required: true
tasks:
  - id: greeting
    type: core.subflow
    namespace: {child_namespace}
    flowId: greeting
    revision: 1
    inputs:
      name: "{{{{ inputs.person }}}}"
    outputMapping:
      message: "{{{{ outputs.result.value }}}}"
    outputSchema:
      type: object
      properties:
        message:
          type: string
      required: [message]
  - id: notify
    type: core.subflow
    namespace: {system_namespace}
    flowId: notify
    mode: ASYNC
    dependsOn: [greeting]
""",
                )
                assert child.status_code == 200
                assert system_child.status_code == 200
                assert parent.status_code == 200

                created = await client.post(
                    "/api/v1/executions",
                    headers={"authorization": "Bearer test-token"},
                    json={
                        "namespace": parent_namespace,
                        "flowId": "parent",
                        "inputs": {"person": "Ada"},
                    },
                )
                assert created.status_code == 200
                payload = created.json()
                parent_execution_id = UUID(payload["execution"]["execution_id"])
                assert payload["execution"]["state"] == "SUCCESS"
                assert payload["taskRuns"][0]["result"]["outputs"] == {"message": "hello Ada"}

                links = await client.get(
                    f"/api/v1/executions/{parent_execution_id}/subflows",
                    headers={"authorization": "Bearer test-token"},
                )
                assert links.status_code == 200
                relationships = links.json()
                assert {item["child_namespace"] for item in relationships} == {
                    child_namespace,
                    system_namespace,
                }
                assert all(
                    item["created_by"] == payload["execution"]["created_by"]
                    for item in relationships
                )
                system_link = next(
                    item for item in relationships if item["child_flow_id"] == "notify"
                )
                assert system_link["mode"] == "ASYNC"
                assert system_link["child_state"] == "SUCCESS"

                greeting_link = next(
                    item for item in relationships if item["child_flow_id"] == "greeting"
                )
                parent_link = await client.get(
                    f"/api/v1/executions/{greeting_link['child_execution_id']}/parent-subflow",
                    headers={"authorization": "Bearer test-token"},
                )
                assert parent_link.status_code == 200
                assert parent_link.json()["parent_execution_id"] == str(parent_execution_id)
                assert parent_link.json()["parent_namespace"] == parent_namespace

                app.dependency_overrides[authenticate_actor] = lambda: restricted_actor
                restricted_links = await client.get(
                    f"/api/v1/executions/{parent_execution_id}/subflows"
                )
                assert restricted_links.status_code == 404
                cross_namespace_denied = await client.post(
                    "/api/v1/executions",
                    json={
                        "namespace": parent_namespace,
                        "flowId": "parent",
                        "inputs": {"person": "Ada"},
                    },
                )
                assert cross_namespace_denied.status_code == 404

                await authorization_repository.create_binding(
                    RoleBinding(
                        principal_id=principal.id,
                        principal_type=principal.principal_type,
                        role_name="flow-author",
                        scope_type=AuthorizationScopeType.TENANT,
                        tenant_id="default",
                    ),
                    actor_id=audit_actor,
                )
                authorized_links = await client.get(
                    f"/api/v1/executions/{parent_execution_id}/subflows"
                )
                assert authorized_links.status_code == 200
                system_flow_denied = await client.post(
                    "/api/v1/executions",
                    json={
                        "namespace": parent_namespace,
                        "flowId": "parent",
                        "inputs": {"person": "Ada"},
                    },
                )
                assert system_flow_denied.status_code == 403
        finally:
            app.dependency_overrides.clear()
            if parent_execution_id is not None:
                await cleanup_execution_tree(engine, parent_execution_id)
            await cleanup_flows(
                engine,
                (parent_namespace, child_namespace, system_namespace),
            )
            async with engine.begin() as connection:
                await connection.execute(
                    text("DELETE FROM auth_principals WHERE id = :principal_id"),
                    {"principal_id": principal.id},
                )
                await connection.execute(
                    text("DELETE FROM audit_events WHERE actor_id = :actor_id"),
                    {"actor_id": audit_actor},
                )
            await engine.dispose()

    asyncio.run(scenario())
