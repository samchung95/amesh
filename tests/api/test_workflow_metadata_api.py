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


def test_namespace_defaults_labels_provenance_filtering_and_policy_api() -> None:
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
        suffix = uuid4().hex
        parent = f"tests.metadata.{suffix}"
        child = f"{parent}.team"
        namespace = f"{child}.jobs"
        headers = {"authorization": "Bearer test-token"}
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                parent_response = await client.put(
                    f"/api/v1/namespaces/{parent}/workflow-metadata",
                    json={
                        "pluginDefaults": [
                            {
                                "type": "core.return",
                                "values": {"workerGroup": "secure"},
                                "forced": True,
                            }
                        ],
                        "policy": {
                            "requiredLabels": {"team": "platform"},
                            "normalizeLabels": {"environment": "LOWERCASE"},
                            "requiredDefaults": {"core.return": ["region"]},
                            "normalizeDefaults": {"core.return": {"region": "TRIM"}},
                        },
                    },
                    headers=headers,
                )
                assert parent_response.status_code == 200, parent_response.text
                child_response = await client.put(
                    f"/api/v1/namespaces/{child}/workflow-metadata",
                    json={
                        "pluginDefaults": [
                            {"type": "core.return", "values": {"region": " APAC "}}
                        ]
                    },
                    headers=headers,
                )
                assert child_response.status_code == 200, child_response.text

                lineage = await client.get(
                    f"/api/v1/namespaces/{namespace}/workflow-metadata",
                    headers=headers,
                )
                assert lineage.status_code == 200
                assert [item["namespace"] for item in lineage.json()["lineage"]] == [
                    parent,
                    child,
                ]

                definition = f"""
id: governed
namespace: {namespace}
labels:
  team: platform
  environment: PROD
pluginDefaults:
  - type: core.return
    values:
      timeoutSeconds: 30
tasks:
  - id: done
    type: core.return
    timeoutSeconds: 5
    runLabels:
      stage: acceptance
    value: ok
"""
                applied = await client.put(
                    "/api/v1/flows",
                    content=definition,
                    headers={**headers, "content-type": "application/yaml"},
                )
                assert applied.status_code == 200, applied.text

                metadata = await client.get(
                    f"/api/v1/flows/{namespace}/governed/metadata",
                    headers=headers,
                )
                assert metadata.status_code == 200, metadata.text
                payload = metadata.json()
                assert payload["labels"]["environment"] == "prod"
                assert payload["labels"]["amesh.flow.id"] == "governed"
                task_defaults = payload["pluginResolution"]["defaults"]["tasks"][
                    "tasks.done"
                ]
                assert task_defaults["origins"]["timeoutSeconds"]["source"] == "task"
                assert task_defaults["origins"]["workerGroup"]["namespace"] == parent
                assert task_defaults["effective"]["region"] == "APAC"

                filtered = await client.get(
                    "/api/v1/flows",
                    params={"filter": "metadata.labels.team=platform"},
                    headers=headers,
                )
                assert filtered.status_code == 200
                assert any(item["flow_id"] == "governed" for item in filtered.json())

                started = await client.post(
                    "/api/v1/executions",
                    json={"namespace": namespace, "flowId": "governed"},
                    headers=headers,
                )
                assert started.status_code == 200, started.text
                detail = started.json()
                execution = detail["execution"]
                task_run = detail["taskRuns"][0]
                assert execution["labels"]["amesh.execution.source"] == "api"
                assert task_run["labels"]["stage"] == "acceptance"
                assert task_run["labels"]["amesh.task.id"] == "done"

                denied = await client.put(
                    "/api/v1/flows",
                    content=definition.replace("  team: platform\n", ""),
                    headers={**headers, "content-type": "application/yaml"},
                )
                assert denied.status_code == 409

                spoofed = await client.put(
                    "/api/v1/flows",
                    content=definition.replace("  team: platform", "  amesh.flow.id: spoofed"),
                    headers={**headers, "content-type": "application/yaml"},
                )
                assert spoofed.status_code == 422

                stale = await client.put(
                    f"/api/v1/namespaces/{parent}/workflow-metadata",
                    json={"expectedVersion": 999},
                    headers=headers,
                )
                assert stale.status_code == 412

            async with engine.connect() as connection:
                indexes = set(
                    await connection.scalars(
                        text(
                            "SELECT indexname FROM pg_indexes WHERE indexname IN "
                            "('flows_labels_gin_idx', 'executions_labels_gin_idx', "
                            "'task_runs_labels_gin_idx', 'assets_labels_gin_idx', "
                            "'backfills_labels_gin_idx')"
                        )
                    )
                )
                assert len(indexes) == 5
                policy_exists = await connection.scalar(
                    text(
                        "SELECT count(*) FROM pg_policies "
                        "WHERE tablename = 'namespace_workflow_metadata' "
                        "AND policyname = 'tenant_runtime_isolation'"
                    )
                )
                assert policy_exists == 1
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
