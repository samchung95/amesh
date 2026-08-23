from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresAuditRepository, PostgresAuthorizationRepository
from amesh.app import (
    app,
    authenticate_actor,
    get_audit_artifact_service,
    get_audit_repository,
    get_authorization_service,
)
from amesh.audit import AuditArtifactService
from amesh.authorization import AuthorizationService
from amesh.domain import ActorContext, PrincipalDefinition, PrincipalType
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_audit_and_compliance_api_lifecycle() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, migration_directory())
            repository = PostgresAuditRepository(engine)
            authorization_repository = PostgresAuthorizationRepository(engine)
            artifact_service = AuditArtifactService(repository, signing_key="api-test-key")
            actor = ActorContext(
                principal_id=uuid4(),
                principal_type=PrincipalType.SYSTEM,
                display="audit-api-admin",
                bootstrap_admin=True,
            )
            app.dependency_overrides[authenticate_actor] = lambda: actor
            app.dependency_overrides[get_audit_repository] = lambda: repository
            app.dependency_overrides[get_audit_artifact_service] = lambda: artifact_service
            app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
                authorization_repository
            )
            transport = httpx.ASGITransport(app=app)
            headers = {"X-Amesh-Tenant": "default"}
            now = datetime.now(UTC)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                policy = await client.put(
                    "/api/v1/audit-policy",
                    headers=headers,
                    json={"retentionDays": 30},
                )
                assert policy.status_code == 200, policy.text
                assert policy.json()["retentionDays"] == 30

                hold = await client.post(
                    "/api/v1/audit-legal-holds",
                    headers=headers,
                    json={
                        "name": "api-test",
                        "reason": "verify legal hold API",
                        "startsAt": (now - timedelta(minutes=1)).isoformat(),
                        "endsAt": (now + timedelta(minutes=1)).isoformat(),
                    },
                )
                assert hold.status_code == 201, hold.text
                holds = await client.get("/api/v1/audit-legal-holds", headers=headers)
                assert holds.status_code == 200, holds.text
                assert holds.json()[0]["id"] == hold.json()["id"]

                evidence = await client.post(
                    "/api/v1/compliance-evidence",
                    headers=headers,
                    json={
                        "category": "VULNERABILITY",
                        "title": "Dependency scan",
                        "source": "local-test",
                        "occurredAt": now.isoformat(),
                        "payload": {"result": "passed", "token": "api-canary-token"},
                    },
                )
                assert evidence.status_code == 201, evidence.text
                assert evidence.json()["payload"]["token"] == "[REDACTED]"

                events = await client.get("/api/v1/audit-events", headers=headers)
                assert events.status_code == 200, events.text
                assert events.json()["items"]
                audited_read = await client.get(
                    "/api/v1/audit-events",
                    headers=headers,
                    params={"action": "audit.read"},
                )
                assert audited_read.status_code == 200, audited_read.text
                assert audited_read.json()["items"]
                integrity = await client.get(
                    "/api/v1/audit-events/integrity",
                    headers=headers,
                )
                assert integrity.status_code == 200, integrity.text
                assert integrity.json()["valid"]

                audit_export = await client.get(
                    "/api/v1/audit-events/export",
                    headers=headers,
                    params={"format": "JSON"},
                )
                assert audit_export.status_code == 200, audit_export.text
                assert audit_export.headers["x-amesh-signature"].startswith("v1=")
                assert b"api-canary-token" not in audit_export.content

                package = await client.get(
                    "/api/v1/compliance-packages/export",
                    headers=headers,
                )
                assert package.status_code == 200, package.text
                assert package.headers["content-type"] == "application/zip"
                assert package.headers["x-amesh-signature"].startswith("v1=")

                unauthorized_principal = await authorization_repository.create_principal(
                    PrincipalDefinition(
                        principal_type=PrincipalType.USER,
                        handle="unauthorized-audit-reader",
                        display_name="Unauthorized audit reader",
                    ),
                    actor_id="test:audit-api",
                )
                unauthorized_actor = ActorContext(
                    principal_id=unauthorized_principal.id,
                    principal_type=unauthorized_principal.principal_type,
                    display=unauthorized_principal.handle,
                )
                app.dependency_overrides[authenticate_actor] = lambda: unauthorized_actor
                denied = await client.get("/api/v1/audit-events", headers=headers)
                assert denied.status_code == 404, denied.text
                assert denied.json()["detail"] == "tenant unavailable"
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
