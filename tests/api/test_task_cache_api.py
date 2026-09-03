from __future__ import annotations

import asyncio
import os
from datetime import timedelta
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresTaskCacheRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_settings,
    get_task_cache_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings
from amesh.ports import TaskCacheKey
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_authorized_user_can_list_and_purge_cache_by_resource_scope(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            cache = PostgresTaskCacheRepository(engine)
            key = TaskCacheKey(
                key_hash="a" * 64,
                key_prefix="acceptance/tests.cache/cached/result",
                cache_namespace="acceptance",
                scope="TASK",
                namespace="tests.cache",
                flow_id="cached",
                flow_revision=1,
                task_id="result",
                task_type="core.return",
                security_context_hash="b" * 64,
                invalidation_policy="TTL_AND_REVISION",
                ttl=timedelta(hours=1),
            )
            execution_id = uuid4()
            task_run_id = uuid4()
            reserved = await cache.lookup_or_reserve(
                key,
                tenant_id="default",
                execution_id=execution_id,
                task_run_id=task_run_id,
                attempt=1,
            )
            assert reserved.owner_token is not None
            assert await cache.publish(
                key.key_hash,
                reserved.owner_token,
                {"value": "cached"},
                {"metrics": [], "artifacts": []},
                tenant_id="default",
                execution_id=execution_id,
                task_run_id=task_run_id,
                attempt=1,
            )

            app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
                PostgresAuthorizationRepository(engine)
            )
            app.dependency_overrides[get_tenant_service] = lambda: TenantService(
                PostgresTenantRepository(engine)
            )
            app.dependency_overrides[get_task_cache_repository] = lambda: cache
            app.dependency_overrides[get_settings] = lambda: Settings(
                _env_file=None,
                database_url=migrated_test_database_url,
                amesh_admin_token="test-token",
            )
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                unauthorized = await client.get("/api/v1/task-cache")
                assert unauthorized.status_code == 401

                headers = {"authorization": "Bearer test-token"}
                listed = await client.get(
                    "/api/v1/task-cache?namespace=tests.cache",
                    headers=headers,
                )
                assert listed.status_code == 200
                assert listed.json()[0]["state"] == "READY"

                purged = await client.post(
                    "/api/v1/task-cache/purge",
                    headers=headers,
                    json={
                        "namespace": "tests.cache",
                        "flowId": "cached",
                        "reason": "API acceptance purge",
                    },
                )
                assert purged.status_code == 200
                assert purged.json() == {
                    "invalidated_count": 1,
                    "reason": "API acceptance purge",
                }
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    asyncio.run(scenario())
