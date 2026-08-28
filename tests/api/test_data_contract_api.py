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


def test_api_schema_validation_terminal_outputs_and_public_redaction() -> None:
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
        namespace = f"tests.contracts.{uuid4().hex}"
        flow_id = "typed_api"
        headers = {"authorization": "Bearer test-token"}
        definition = f"""
id: {flow_id}
namespace: {namespace}
inputs:
  - id: message
    type: STRING
    required: true
    sensitive: true
    displayName: Message
    placeholder: Enter a message
    validation:
      minLength: 2
  - id: credential
    type: SECRET
    required: true
tasks:
  - id: done
    type: core.return
    value: "{{{{ inputs.message }}}}"
outputs:
  echo:
    type: string
    value: "{{{{ outputs.done.value }}}}"
  protected:
    type: string
    value: "{{{{ inputs.message }}}}"
    sensitive: true
"""
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                applied = await client.put(
                    "/api/v1/flows",
                    content=definition,
                    headers={**headers, "content-type": "application/yaml"},
                )
                assert applied.status_code == 200, applied.text

                contract = await client.get(
                    f"/api/v1/flows/{namespace}/{flow_id}/data-contract",
                    headers=headers,
                )
                assert contract.status_code == 200
                contract_payload = contract.json()
                assert contract_payload["inputSchema"]["required"] == [
                    "message",
                    "credential",
                ]
                assert contract_payload["inputSchema"]["properties"]["message"][
                    "minLength"
                ] == 2
                assert contract_payload["inputSchema"]["properties"]["credential"][
                    "writeOnly"
                ] is True

                rejected = await client.post(
                    "/api/v1/executions",
                    json={
                        "namespace": namespace,
                        "flowId": flow_id,
                        "inputs": {
                            "message": "hello",
                            "credential": "plaintext-secret-canary",
                        },
                    },
                    headers=headers,
                )
                assert rejected.status_code == 422

                started = await client.post(
                    "/api/v1/executions",
                    json={
                        "namespace": namespace,
                        "flowId": flow_id,
                        "inputs": {
                            "message": "hello",
                            "credential": "secret://tests/credential",
                        },
                    },
                    headers=headers,
                )
                assert started.status_code == 200, started.text
                detail = started.json()
                assert detail["execution"]["state"] == "SUCCESS"
                assert detail["execution"]["inputs"] == {
                    "message": "[REDACTED]",
                    "credential": "[REDACTED]",
                }
                assert detail["execution"]["outputs"] == {
                    "echo": "hello",
                    "protected": "[REDACTED]",
                }
                assert "hello" not in str(detail["taskRuns"])

                execution_id = detail["execution"]["execution_id"]
                fetched = await client.get(
                    f"/api/v1/executions/{execution_id}",
                    headers=headers,
                )
                assert fetched.status_code == 200
                assert fetched.json()["execution"]["inputs"]["message"] == "[REDACTED]"

            async with engine.connect() as connection:
                canary_count = int(
                    await connection.scalar(
                        text(
                            """
                            SELECT
                                (SELECT count(*) FROM executions
                                 WHERE inputs::text LIKE '%plaintext-secret-canary%')
                              + (SELECT count(*) FROM execution_events
                                 WHERE payload::text LIKE '%plaintext-secret-canary%')
                              + (SELECT count(*) FROM messages_outbox
                                 WHERE envelope::text LIKE '%plaintext-secret-canary%')
                            """
                        )
                    )
                    or 0
                )
                assert canary_count == 0
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
