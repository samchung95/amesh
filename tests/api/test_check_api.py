from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresCheckRepository,
    PostgresExecutionRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_check_repository,
    get_settings,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings
from amesh.dsl import FlowDefinition
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_check_policy_evaluation_and_compliance_api(migrated_test_database_url: str) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        checks = PostgresCheckRepository(engine)
        executions = PostgresExecutionRepository(engine)
        namespace = f"tests.check-api.{uuid4().hex}"
        try:
            app.dependency_overrides[get_check_repository] = lambda: checks
            app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
                PostgresAuthorizationRepository(engine)
            )
            app.dependency_overrides[get_tenant_service] = lambda: TenantService(
                PostgresTenantRepository(engine)
            )
            app.dependency_overrides[get_settings] = lambda: Settings(
                _env_file=None,
                database_url=migrated_test_database_url,
                amesh_admin_token="test-token",
            )
            transport = httpx.ASGITransport(app=app)
            headers = {"authorization": "Bearer test-token"}
            async with httpx.AsyncClient(
                transport=transport, base_url="http://amesh.test"
            ) as client:
                created = await client.put(
                    f"/api/v1/check-policies/{namespace}/baseline",
                    headers=headers,
                    json={
                        "source": "NAMESPACE",
                        "definition": {
                            "id": "policy-start",
                            "type": "START_DELAY",
                            "threshold": "PT1H",
                        },
                    },
                )
                assert created.status_code == 200
                listed = await client.get(
                    f"/api/v1/check-policies?namespace={namespace}", headers=headers
                )
                assert listed.status_code == 200
                assert listed.json()[0]["policy_key"] == "baseline"

                flow = FlowDefinition.model_validate(
                    {
                        "id": "checked",
                        "namespace": namespace,
                        "checkPolicies": ["baseline"],
                        "tasks": [{"id": "result", "type": "test.echo"}],
                    }
                )
                execution = await executions.create_execution(flow, tenant_id="default", inputs={})
                evaluations = await client.get(
                    f"/api/v1/check-evaluations?executionId={execution.execution_id}",
                    headers=headers,
                )
                assert evaluations.status_code == 200
                assert evaluations.json()[0]["outcome"] == "PASS"
                compliance = await client.get(
                    "/api/v1/check-compliance?groupBy=flow", headers=headers
                )
                assert compliance.status_code == 200
                assert compliance.json()[0]["total"] == 1
                assert compliance.json()[0]["compliance_rate"] == 1.0
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    asyncio.run(scenario())
