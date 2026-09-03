from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from tests.fixtures.api_stubs import DefaultTenantQuotaStub as _TenantQuota

from amesh.adapters.postgres import (
    PostgresExecutionRepository,
    PostgresFlowTestRepository,
    PostgresOperationalControlRepository,
)
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_flow_test_repository,
    get_operational_control_repository,
    get_repository,
    get_tenant_service,
)
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    PrincipalType,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class _AllowFlowTests:
    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        del request
        return AuthorizationDecision(
            allowed=True,
            reason_code="test_allow",
            summary="flow-test API fixture",
            policy_version=1,
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        return await self.decide(request)


def test_flow_tests_are_durable_isolated_and_gate_active_promotion(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        executions = PostgresExecutionRepository(engine)
        flow_tests = PostgresFlowTestRepository(engine)
        controls = PostgresOperationalControlRepository(engine)
        actor = ActorContext(
            principal_id=uuid4(),
            principal_type=PrincipalType.USER,
            display="flow-author",
            bootstrap_admin=True,
        )
        try:
            app.dependency_overrides[get_repository] = lambda: executions
            app.dependency_overrides[get_flow_test_repository] = lambda: flow_tests
            app.dependency_overrides[get_operational_control_repository] = lambda: controls
            app.dependency_overrides[authenticate_actor] = lambda: actor
            app.dependency_overrides[get_authorization_service] = _AllowFlowTests
            app.dependency_overrides[get_tenant_service] = _TenantQuota
            namespace = f"tests.flowtests.{uuid4().hex}"
            headers = {
                "Authorization": "Bearer test",
                "X-Amesh-Tenant": "default",
            }
            flow = f"""
id: approval
namespace: {namespace}
revision: 1
inputs:
  - id: route
    type: STRING
    required: true
tasks:
  - id: choose
    type: core.if
    condition: "{{{{ inputs.route == 'primary' }}}}"
    then:
      - id: primary
        type: core.return
        value: ok
    else:
      - id: fallback
        type: core.return
        value: fallback
outputs:
  result: "{{{{ outputs.primary.value }}}}"
"""
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://test",
                headers=headers,
            ) as client:
                applied = await client.put(
                    "/api/v1/flows",
                    content=flow,
                    headers={**headers, "Content-Type": "application/yaml"},
                )
                assert applied.status_code == 200, applied.text

                saved = await client.put(
                    f"/api/v1/flows/{namespace}/approval/tests",
                    json={
                        "testId": "primary-route",
                        "name": "Primary route",
                        "revision": 1,
                        "inputs": {"route": "primary"},
                        "variables": {},
                        "fixtures": {},
                        "expected": {
                            "state": "SUCCESS",
                            "outputs": {"result": "ok"},
                            "taskStates": {
                                "primary": "SUCCESS",
                                "fallback": "SKIPPED",
                            },
                        },
                        "tags": ["ci"],
                    },
                )
                assert saved.status_code == 200, saved.text
                assert saved.json()["revision"] == 1
                assert saved.json()["version"] == 1
                assert saved.json()["flowSemanticHash"]
                assert saved.json()["pluginSetHash"]

                listed = await client.get(
                    f"/api/v1/flows/{namespace}/approval/tests",
                    params={"revision": 1},
                )
                assert [item["testId"] for item in listed.json()] == ["primary-route"]

                gate = await client.put(
                    f"/api/v1/namespaces/{namespace}/flow-test-gate",
                    json={
                        "enabled": True,
                        "minimumCoverage": 50,
                        "requiredTestIds": ["primary-route"],
                    },
                )
                assert gate.status_code == 200, gate.text

                draft = await client.put(
                    f"/api/v1/flows/{namespace}/approval/revisions/1/lifecycle",
                    json={"lifecycle": "DRAFT"},
                )
                assert draft.status_code == 200, draft.text
                blocked = await client.put(
                    f"/api/v1/flows/{namespace}/approval/revisions/1/lifecycle",
                    json={"lifecycle": "ACTIVE"},
                )
                assert blocked.status_code == 409
                assert "FLOW_TEST_GATE_FAILED" in blocked.json()["detail"]

                run = await client.post(
                    f"/api/v1/flows/{namespace}/approval/tests/runs",
                    params={"revision": 1},
                    json={"testIds": ["primary-route"]},
                )
                assert run.status_code == 200, run.text
                result = run.json()
                assert result["outcome"] == "PASSED"
                assert result["coverage"]["percentage"] >= 50
                assert result["isolated"] is True
                assert result["productionExecutionsCreated"] == 0
                assert result["artifactsCreated"] == 0
                assert result["secretLookups"] == 0

                promoted = await client.put(
                    f"/api/v1/flows/{namespace}/approval/revisions/1/lifecycle",
                    json={"lifecycle": "ACTIVE"},
                )
                assert promoted.status_code == 200, promoted.text
                assert promoted.json()["lifecycle"] == "ACTIVE"

                next_revision = await client.put(
                    "/api/v1/flows",
                    content=flow.replace("id: approval", "id: approval\ndescription: revision two"),
                    headers={**headers, "Content-Type": "application/yaml"},
                )
                assert next_revision.status_code == 200, next_revision.text
                assert next_revision.json()["revision"] == 2
                assert next_revision.json()["lifecycle"] == "DRAFT"
                blocked_next = await client.put(
                    f"/api/v1/flows/{namespace}/approval/revisions/2/lifecycle",
                    json={"lifecycle": "ACTIVE"},
                )
                assert blocked_next.status_code == 409

                stale = await client.put(
                    f"/api/v1/flows/{namespace}/approval/tests",
                    json={
                        "testId": "primary-route",
                        "name": "Stale update",
                        "revision": 1,
                        "expectedVersion": 9,
                    },
                )
                assert stale.status_code == 412

                rejected_secret = await client.put(
                    f"/api/v1/flows/{namespace}/approval/tests",
                    json={
                        "testId": "unsafe-data",
                        "name": "Unsafe data",
                        "revision": 1,
                        "inputs": {"apiToken": "must-not-persist"},
                    },
                )
                assert rejected_secret.status_code == 422
                assert "secret-like" in rejected_secret.json()["detail"]

            async with engine.connect() as connection:
                assert (
                    int(await connection.scalar(text("SELECT count(*) FROM executions")) or 0) == 0
                )
                assert (
                    int(
                        await connection.scalar(text("SELECT count(*) FROM execution_artifacts"))
                        or 0
                    )
                    == 0
                )
                assert (
                    int(await connection.scalar(text("SELECT count(*) FROM flow_test_runs")) or 0)
                    == 1
                )
                assert (
                    int(
                        await connection.scalar(
                            text(
                                "SELECT count(*) FROM audit_events "
                                "WHERE resource_type = 'flow_test'"
                            )
                        )
                        or 0
                    )
                    >= 3
                )
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    asyncio.run(scenario())
