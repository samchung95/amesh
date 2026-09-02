from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from tests.fixtures.api_stubs import DefaultTenantQuotaStub as _TenantQuota

from amesh.adapters.postgres import PostgresOperationalControlRepository
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_operational_control_repository,
    get_tenant_service,
)
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    PrincipalType,
)
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


class _AllowOperations:
    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        del request
        return AuthorizationDecision(
            allowed=True,
            reason_code="test_allow",
            summary="operations API fixture",
            policy_version=1,
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        return await self.decide(request)


def test_operations_api_publishes_announcements_and_enforces_bypassable_controls() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        repository = PostgresOperationalControlRepository(engine)
        actor = ActorContext(
            principal_id=uuid4(),
            principal_type=PrincipalType.USER,
            display="incident-commander",
            bootstrap_admin=True,
        )
        try:
            await apply_migrations(database.database_url, migration_directory())
            app.dependency_overrides[get_operational_control_repository] = lambda: repository
            app.dependency_overrides[authenticate_actor] = lambda: actor
            app.dependency_overrides[get_authorization_service] = _AllowOperations
            app.dependency_overrides[get_tenant_service] = _TenantQuota
            now = datetime.now(UTC)
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://test",
                headers={
                    "Authorization": "Bearer test",
                    "X-Amesh-Tenant": "default",
                },
            ) as client:
                published = await client.post(
                    "/api/v1/announcements",
                    json={
                        "title": "Maintenance begins",
                        "message": "New writes pause while accepted work drains.",
                        "severity": "CRITICAL",
                        "audience": "TENANT",
                        "startsAt": now.isoformat(),
                        "expiresAt": (now + timedelta(hours=2)).isoformat(),
                    },
                )
                assert published.status_code == 201, published.text
                active = await client.get("/api/v1/announcements")
                assert active.status_code == 200
                assert active.json()[0]["severity"] == "CRITICAL"

                activated = await client.post(
                    "/api/v1/operational-controls",
                    json={
                        "kind": "MAINTENANCE",
                        "name": "API write maintenance",
                        "scope": "TENANT",
                        "boundaries": ["API_WRITES"],
                        "runningWorkPolicy": "DRAIN",
                        "reason": "database maintenance",
                        "expiresAt": (now + timedelta(hours=1)).isoformat(),
                    },
                )
                assert activated.status_code == 201, activated.text
                control = activated.json()

                blocked = await client.post(
                    "/api/v1/admin/controls/preview",
                    json={
                        "key": "MAINTENANCE",
                        "enabled": True,
                        "value": None,
                        "reason": "verify API write control",
                    },
                )
                assert blocked.status_code == 423
                assert "operational control" in blocked.text

                listed = await client.get("/api/v1/operational-controls")
                assert listed.status_code == 200
                acknowledgements = listed.json()[0]["acknowledgements"]
                assert any(item["componentId"] == "webserver:api" for item in acknowledgements)

                bypassed = await client.post(
                    f"/api/v1/operational-controls/{control['id']}/actions",
                    json={
                        "action": "BYPASS",
                        "reason": "approved smoke validation",
                        "expectedVersion": control["version"],
                        "bypassUntil": (now + timedelta(minutes=15)).isoformat(),
                    },
                )
                assert bypassed.status_code == 200, bypassed.text
                assert bypassed.json()["state"] == "BYPASSED"

                allowed = await client.post(
                    "/api/v1/admin/controls/preview",
                    json={
                        "key": "MAINTENANCE",
                        "enabled": True,
                        "value": None,
                        "reason": "verify bypass",
                    },
                )
                assert allowed.status_code != 423

                events = await client.get("/api/v1/operational-control-events")
                assert events.status_code == 200
                assert {"ACTIVATE", "BYPASS"} <= {item["action"] for item in events.json()}

                deactivated = await client.post(
                    f"/api/v1/operational-controls/{control['id']}/actions",
                    json={
                        "action": "DEACTIVATE",
                        "reason": "maintenance complete",
                        "expectedVersion": bypassed.json()["version"],
                    },
                )
                assert deactivated.status_code == 200
                assert deactivated.json()["state"] == "DEACTIVATED"
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
