from __future__ import annotations

import asyncio
import os
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresExecutionRepository,
    PostgresMetadataRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_metadata_repository,
    get_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_flow_revision_history_diff_lifecycle_restore_and_reference_protection() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        repository = PostgresExecutionRepository(engine)
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_metadata_repository] = lambda: PostgresMetadataRepository(
            engine
        )
        app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
            PostgresAuthorizationRepository(engine)
        )
        app.dependency_overrides[get_tenant_service] = lambda: TenantService(
            PostgresTenantRepository(engine)
        )
        app.dependency_overrides[get_settings] = lambda: Settings(
            database_url=database.database_url,
            amesh_admin_token="test-token",
        )
        namespace = f"tests.revisions.{uuid4().hex}"
        flow_id = "revisioned_flow"
        auth = {"authorization": "Bearer test-token"}
        document_headers = {
            **auth,
            "content-type": "application/yaml",
            "X-AMESH-Source": "git",
            "X-AMESH-Commit": "abc123",
            "X-AMESH-Environment": "staging",
            "X-AMESH-Deployment": "deploy-42",
        }

        def flow_document(description: str, revision: int = 1) -> str:
            return f"""
id: {flow_id}
namespace: {namespace}
revision: {revision}
description: {description}
tasks:
  - id: done
    type: core.return
    value: ok
"""

        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                first = await client.put(
                    "/api/v1/flows",
                    content=flow_document("first"),
                    headers=document_headers,
                )
                assert first.status_code == 200
                assert first.json()["revision"] == 1
                assert first.json()["lifecycle"] == "ACTIVE"

                semantic_noop = await client.put(
                    "/api/v1/flows",
                    content=flow_document("first"),
                    headers=document_headers,
                )
                assert semantic_noop.status_code == 200
                assert semantic_noop.json()["revision"] == 1

                second = await client.put(
                    "/api/v1/flows",
                    content=flow_document("second"),
                    headers=document_headers,
                )
                assert second.status_code == 200
                assert second.json()["revision"] == 2

                unauthorized = await client.get(f"/api/v1/flows/{namespace}/{flow_id}/revisions")
                assert unauthorized.status_code == 401
                history = await client.get(
                    f"/api/v1/flows/{namespace}/{flow_id}/revisions",
                    headers=auth,
                )
                assert history.status_code == 200
                records = history.json()
                assert [item["revision"] for item in records] == [1, 2]
                assert records[0]["source"] == "git"
                assert records[0]["source_commit"] == "abc123"
                assert records[0]["environment"] == "staging"
                assert records[0]["deployment"] == {"reference": "deploy-42"}
                assert records[0]["plugin_resolution"] == {
                    "catalogVersion": "amesh.resource-catalog/v1",
                    "resources": [{"kind": "task", "type": "core.return"}],
                }

                diff = await client.get(
                    f"/api/v1/flows/{namespace}/{flow_id}/revisions/diff",
                    headers=auth,
                    params={"from": 1, "to": 2},
                )
                assert diff.status_code == 200
                assert "revision-1" in diff.json()["human"]
                assert {item["path"] for item in diff.json()["operations"]} >= {
                    "/description",
                    "/revision",
                }

                for lifecycle in ("DRAFT", "DISABLED", "ARCHIVED"):
                    promoted = await client.put(
                        f"/api/v1/flows/{namespace}/{flow_id}/revisions/2/lifecycle",
                        headers={**auth, "content-type": "application/json"},
                        json={"lifecycle": lifecycle, "reason": "acceptance"},
                    )
                    assert promoted.status_code == 200
                    assert promoted.json()["lifecycle"] == lifecycle

                archived_flow = await repository.get_flow(
                    namespace,
                    flow_id,
                    tenant_id="default",
                )
                with pytest.raises(ValueError, match="ARCHIVED does not permit execution"):
                    await repository.create_execution(
                        archived_flow,
                        tenant_id="default",
                        inputs={},
                    )

                restored = await client.post(
                    f"/api/v1/flows/{namespace}/{flow_id}/revisions/1/restore",
                    headers={**auth, "content-type": "application/json"},
                    json={"reason": "rollback"},
                )
                assert restored.status_code == 200
                assert restored.json()["revision"] == 1
                assert restored.json()["lifecycle"] == "ACTIVE"
                restored_history = await client.get(
                    f"/api/v1/flows/{namespace}/{flow_id}/revisions",
                    headers=auth,
                )
                assert [item["semantic_hash"] for item in restored_history.json()] == [
                    item["semantic_hash"] for item in records
                ]

                restored_flow = await repository.get_flow(
                    namespace,
                    flow_id,
                    tenant_id="default",
                )
                execution = await repository.create_execution(
                    restored_flow,
                    tenant_id="default",
                    inputs={},
                )
                active_second = await client.put(
                    f"/api/v1/flows/{namespace}/{flow_id}/revisions/2/lifecycle",
                    headers={**auth, "content-type": "application/json"},
                    json={"lifecycle": "ACTIVE"},
                )
                assert active_second.status_code == 200

                third = await client.put(
                    "/api/v1/flows",
                    content=flow_document("third"),
                    headers=document_headers,
                )
                assert third.status_code == 200
                assert third.json()["revision"] == 3
                active_second = await client.put(
                    f"/api/v1/flows/{namespace}/{flow_id}/revisions/2/lifecycle",
                    headers={**auth, "content-type": "application/json"},
                    json={"lifecycle": "ACTIVE"},
                )
                assert active_second.status_code == 200

                third_history = await client.get(
                    f"/api/v1/flows/{namespace}/{flow_id}/revisions",
                    headers=auth,
                )
                revision_three_id = next(
                    item["resource_id"] for item in third_history.json() if item["revision"] == 3
                )
                async with engine.begin() as connection:
                    await connection.execute(
                        text(
                            "INSERT INTO audit_events ("
                            "event_id, tenant_id, actor_id, action, resource_type, "
                            "resource_id, outcome, occurred_at) "
                            "SELECT :event_id, id, 'test:audit', 'flow_revision_reviewed', "
                            "'flow_revision', :resource_id, 'SUCCESS', clock_timestamp() "
                            "FROM tenants WHERE slug = 'default'"
                        ),
                        {"event_id": uuid4(), "resource_id": revision_three_id},
                    )
                audit_delete = await client.delete(
                    f"/api/v1/flows/{namespace}/{flow_id}/revisions/3",
                    headers=auth,
                )
                assert audit_delete.status_code == 409
                assert "audit" in audit_delete.json()["detail"]

                referenced_delete = await client.delete(
                    f"/api/v1/flows/{namespace}/{flow_id}/revisions/1",
                    headers=auth,
                )
                assert referenced_delete.status_code == 409
                assert "execution" in referenced_delete.json()["detail"]

                async with engine.connect() as connection:
                    pinned = (
                        (
                            await connection.execute(
                                text(
                                    "SELECT revisions.revision, revisions.plugin_resolution "
                                    "FROM executions "
                                    "JOIN flow_revisions revisions "
                                    "ON revisions.id = executions.flow_revision_id "
                                    "WHERE executions.id = :execution_id"
                                ),
                                {"execution_id": execution.execution_id},
                            )
                        )
                        .mappings()
                        .one()
                    )
                    assert pinned["revision"] == 1
                    assert pinned["plugin_resolution"]["catalogVersion"] == (
                        "amesh.resource-catalog/v1"
                    )
                    event_count = int(
                        await connection.scalar(
                            text(
                                "SELECT count(*) FROM flow_revision_events "
                                "WHERE flow_id = CAST(:flow_id AS uuid)"
                            ),
                            {"flow_id": first.json()["resource_id"]},
                        )
                        or 0
                    )
                    assert event_count >= 7
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
