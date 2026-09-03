from __future__ import annotations

import asyncio
import os
import sys
from datetime import UTC, datetime, timedelta
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
    PostgresSharedResourceRepository,
    PostgresTaskCacheRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_metadata_repository,
    get_namespace_resource_service,
    get_repository,
    get_shared_resource_repository,
    get_task_cache_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database
from amesh.storage.factory import build_object_store
from amesh.tenancy import TenantService
from amesh.workflow.shared_resources import NamespaceResourceService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_namespace_files_key_values_secrets_and_promotion(tmp_path: Path) -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        settings = Settings(
            _env_file=None,
            database_url=database.database_url,
            amesh_admin_token="test-token",
            object_storage_backend="local",
            object_storage_local_root=str(tmp_path / "object-store"),
        )
        repository = PostgresExecutionRepository(engine)
        shared_resources = PostgresSharedResourceRepository(engine)
        resource_service = NamespaceResourceService(
            shared_resources,
            build_object_store(settings),
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_task_cache_repository] = lambda: PostgresTaskCacheRepository(
            engine
        )
        app.dependency_overrides[get_shared_resource_repository] = lambda: shared_resources
        app.dependency_overrides[get_namespace_resource_service] = lambda: resource_service
        app.dependency_overrides[get_metadata_repository] = lambda: PostgresMetadataRepository(
            engine
        )
        app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
            PostgresAuthorizationRepository(engine)
        )
        app.dependency_overrides[get_tenant_service] = lambda: TenantService(
            PostgresTenantRepository(engine)
        )
        app.dependency_overrides[get_settings] = lambda: settings
        suffix = uuid4().hex
        parent = f"tests.resources.{suffix}"
        child = f"{parent}.jobs"
        promoted = f"tests.promoted.{suffix}"
        headers = {"authorization": "Bearer test-token"}
        secret_value = f"secret-{suffix}"
        environment_name = f"AMESH_TEST_SECRET_{suffix.upper()}"
        os.environ[environment_name] = secret_value
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                uploaded = await client.put(
                    f"/api/v1/namespaces/{parent}/files/config/rules.txt",
                    content=b"parent rules",
                    headers={**headers, "content-type": "text/plain"},
                )
                assert uploaded.status_code == 200, uploaded.text
                assert uploaded.json()["version"] == 1

                inherited = await client.get(
                    f"/api/v1/namespaces/{child}/files",
                    headers=headers,
                )
                assert inherited.status_code == 200, inherited.text
                assert inherited.json()[0]["originNamespace"] == parent
                assert inherited.json()[0]["inherited"] is True
                parent_download = await client.get(
                    f"/api/v1/namespaces/{child}/files/config/rules.txt",
                    headers=headers,
                )
                assert parent_download.content == b"parent rules"

                child_upload = await client.put(
                    f"/api/v1/namespaces/{child}/files/config/rules.txt",
                    params={"expectedVersion": 0},
                    content=b"child rules v1",
                    headers={**headers, "content-type": "text/plain"},
                )
                assert child_upload.status_code == 200, child_upload.text
                updated = await client.put(
                    f"/api/v1/namespaces/{child}/files/config/rules.txt",
                    params={"expectedVersion": 1},
                    content=b"child rules v2",
                    headers={**headers, "content-type": "text/plain"},
                )
                assert updated.status_code == 200, updated.text
                assert updated.json()["version"] == 2
                versions = await client.get(
                    f"/api/v1/namespaces/{child}/files/config/rules.txt/versions",
                    headers=headers,
                )
                assert [item["version"] for item in versions.json()] == [2, 1]
                assert all("objectUri" not in item for item in versions.json())

                moved = await client.post(
                    f"/api/v1/namespaces/{child}/files/config/rules.txt/move",
                    json={"destinationPath": "runtime/rules.txt", "expectedVersion": 2},
                    headers=headers,
                )
                assert moved.status_code == 200, moved.text
                assert moved.json()["path"] == "runtime/rules.txt"
                moved_download = await client.get(
                    f"/api/v1/namespaces/{child}/files/runtime/rules.txt",
                    headers=headers,
                )
                assert moved_download.content == b"child rules v2"
                hidden_parent = await client.get(
                    f"/api/v1/namespaces/{child}/files/config/rules.txt",
                    headers=headers,
                )
                assert hidden_parent.status_code == 404

                created_kv = await client.put(
                    f"/api/v1/namespaces/{child}/key-values/release.channel",
                    json={"type": "STRING", "value": "stable", "expectedVersion": 0},
                    headers=headers,
                )
                assert created_kv.status_code == 200, created_kv.text
                stale_kv = await client.put(
                    f"/api/v1/namespaces/{child}/key-values/release.channel",
                    json={"type": "STRING", "value": "canary", "expectedVersion": 0},
                    headers=headers,
                )
                assert stale_kv.status_code == 412
                expired = await client.put(
                    f"/api/v1/namespaces/{child}/key-values/expired",
                    json={
                        "type": "NUMBER",
                        "value": 7,
                        "expiresAt": (datetime.now(UTC) - timedelta(seconds=1)).isoformat(),
                    },
                    headers=headers,
                )
                assert expired.status_code == 200, expired.text
                listed_kv = await client.get(
                    f"/api/v1/namespaces/{child}/key-values",
                    headers=headers,
                )
                assert [item["key"] for item in listed_kv.json()] == ["release.channel"]
                changes = await client.get(
                    f"/api/v1/namespaces/{child}/key-values/changes",
                    headers=headers,
                )
                assert len(changes.json()) == 2
                assert all("value" not in item for item in changes.json())

                bound = await client.put(
                    f"/api/v1/namespaces/{parent}/secret-bindings/API_KEY",
                    json={
                        "provider": "env",
                        "providerReference": environment_name,
                        "expectedVersion": 0,
                    },
                    headers=headers,
                )
                assert bound.status_code == 200, bound.text
                inherited_secret = await client.get(
                    f"/api/v1/namespaces/{child}/secret-bindings",
                    headers=headers,
                )
                assert inherited_secret.json()[0]["originNamespace"] == parent
                assert secret_value not in inherited_secret.text

                definition = f"""
id: resource-context
namespace: {child}
tasks:
  - id: done
    type: core.return
    contract:
      secretScopes: [API_KEY]
      files:
        rules: nsfile:///runtime/rules.txt
    value:
      secret: "{{{{ secret('API_KEY') }}}}"
      channel: "{{{{ kv('release.channel') }}}}"
"""
                applied = await client.put(
                    "/api/v1/flows",
                    content=definition,
                    headers={**headers, "content-type": "application/yaml"},
                )
                assert applied.status_code == 200, applied.text
                executed = await client.post(
                    "/api/v1/executions",
                    json={"namespace": child, "flowId": "resource-context"},
                    headers=headers,
                )
                assert executed.status_code == 200, executed.text
                assert executed.json()["execution"]["state"] == "SUCCESS"
                result = executed.json()["taskRuns"][0]["result"]["value"]
                assert result == {"secret": "[REDACTED]", "channel": "stable"}
                assert secret_value not in executed.text

                workspace_definition = f"""
id: workspace-context
namespace: {child}
tasks:
  - id: workspace
    type: core.workingDirectory
    inputFiles:
      rules.txt: nsfile:///runtime/rules.txt
    outputFiles: [result.txt]
    maxConcurrency: 1
    tasks:
      - id: transform
        type: core.shell
        command:
          - {sys.executable!r}
          - -c
          - "from pathlib import Path; Path('result.txt').write_text(Path('rules.txt').read_text().upper())"
"""
                workspace_applied = await client.put(
                    "/api/v1/flows",
                    content=workspace_definition,
                    headers={**headers, "content-type": "application/yaml"},
                )
                assert workspace_applied.status_code == 200, workspace_applied.text
                workspace_execution = await client.post(
                    "/api/v1/executions",
                    json={"namespace": child, "flowId": "workspace-context"},
                    headers=headers,
                )
                assert workspace_execution.status_code == 200, workspace_execution.text
                workspace_execution_id = workspace_execution.json()["execution"]["execution_id"]
                files = await client.get(
                    f"/api/v1/executions/{workspace_execution_id}/files",
                    headers=headers,
                )
                assert files.status_code == 200, files.text
                assert files.json()[0]["logical_path"] == "result.txt"
                assert "workspace-path:result.txt" in files.json()[0]["lineage"]
                downloaded = await client.get(
                    (
                        f"/api/v1/executions/{workspace_execution_id}/files/"
                        f"{files.json()[0]['artifact_id']}"
                    ),
                    headers=headers,
                )
                assert downloaded.status_code == 200, downloaded.text
                assert downloaded.content == b"CHILD RULES V2"

                exported = await client.get(
                    f"/api/v1/namespaces/{child}/resource-bundle",
                    headers=headers,
                )
                assert exported.status_code == 200, exported.text
                assert secret_value not in exported.text
                imported = await client.post(
                    f"/api/v1/namespaces/{promoted}/resource-bundle",
                    json=exported.json(),
                    headers=headers,
                )
                assert imported.status_code == 200, imported.text
                assert imported.json() == {
                    "files": 1,
                    "keyValues": 1,
                    "secretBindings": 0,
                }
                promoted_file = await client.get(
                    f"/api/v1/namespaces/{promoted}/files/runtime/rules.txt",
                    headers=headers,
                )
                assert promoted_file.content == b"child rules v2"

            async with engine.connect() as connection:
                stored_secret = await connection.scalar(
                    text("SELECT string_agg(evidence::text, '') FROM audit_events")
                )
                revisions = await connection.scalar(
                    text("SELECT string_agg(canonical_definition::text, '') FROM flow_revisions")
                )
                assert secret_value not in (stored_secret or "")
                assert secret_value not in (revisions or "")
        finally:
            os.environ.pop(environment_name, None)
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
