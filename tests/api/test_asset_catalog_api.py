from __future__ import annotations

import asyncio
import os
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from tests.fixtures.api_stubs import DefaultTenantQuotaStub as _TenantQuota

from amesh.adapters.postgres import PostgresMetadataRepository
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_metadata_repository,
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
from amesh.ports import AssetLineageDeclaration, AssetMetadata

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def _payload(*, key: str, namespace: str = "catalog.api") -> dict[str, object]:
    return {
        "assetId": str(uuid4()),
        "namespace": namespace,
        "provider": "postgresql",
        "account": "analytics",
        "location": "warehouse.internal:5432",
        "externalKey": key,
        "assetType": "table",
        "displayName": key.replace(".", " / "),
        "description": "API catalog fixture",
        "owner": "data-platform",
        "contacts": ["data@example.test"],
        "domainGroup": "analytics",
        "tags": ["qualified"],
        "customMetadata": {"classification": "internal"},
        "labels": {"environment": "test"},
    }


def test_asset_catalog_api_registers_traverses_filters_and_exports() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        metadata = PostgresMetadataRepository(engine)
        actor = ActorContext(
            principal_id=uuid4(),
            principal_type=PrincipalType.USER,
            display="asset-steward",
            bootstrap_admin=False,
        )
        headers = {"X-Amesh-Tenant": "default"}
        source_payload = _payload(key="raw.orders")
        target_payload = _payload(key="curated.orders")
        try:
            await apply_migrations(database.database_url, migration_directory())
            app.dependency_overrides[authenticate_actor] = lambda: actor
            app.dependency_overrides[get_authorization_service] = _CatalogAuthorization
            app.dependency_overrides[get_tenant_service] = _TenantQuota
            app.dependency_overrides[get_metadata_repository] = lambda: metadata
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                source_response = await client.post(
                    "/api/v1/assets",
                    headers=headers,
                    json=source_payload,
                )
                target_response = await client.post(
                    "/api/v1/assets",
                    headers=headers,
                    json=target_payload,
                )
                assert source_response.status_code == 201, source_response.text
                assert target_response.status_code == 201, target_response.text
                source_id = source_response.json()["assetId"]
                target_id = target_response.json()["assetId"]

                observation = await client.post(
                    "/api/v1/assets/observations",
                    headers=headers,
                    json={
                        "asset": target_payload,
                        "accessMode": "WRITE",
                        "evidenceKind": "OBSERVED",
                        "confidence": 0.9,
                        "flowId": "catalog-api-flow",
                    },
                )
                assert observation.status_code == 201, observation.text
                assert observation.json()["accessMode"] == "WRITE"

                lineage = await client.post(
                    "/api/v1/assets/lineage",
                    headers=headers,
                    json={
                        "upstreamAssetId": source_id,
                        "downstreamAssetId": target_id,
                        "evidenceKind": "DECLARED",
                        "confidence": 1,
                        "flowId": "catalog-api-flow",
                    },
                )
                assert lineage.status_code == 201, lineage.text

                hidden = await metadata.upsert_asset(
                    AssetMetadata.model_validate(
                        _payload(key="private.orders", namespace="private")
                    ),
                    tenant_id="default",
                    actor_id="catalog-test",
                )
                await metadata.declare_asset_lineage(
                    AssetLineageDeclaration(
                        upstreamAssetId=hidden.asset_id,
                        downstreamAssetId=UUID(target_id),
                    ),
                    tenant_id="default",
                    namespace="catalog.api",
                    actor_id="catalog-test",
                )

                listed = await client.get("/api/v1/assets", headers=headers)
                assert listed.status_code == 200, listed.text
                assert {item["assetId"] for item in listed.json()} == {source_id, target_id}

                detail = await client.get(f"/api/v1/assets/{target_id}", headers=headers)
                assert detail.status_code == 200, detail.text
                assert [item["assetId"] for item in detail.json()["upstream"]] == [source_id]
                assert all(
                    edge["upstreamAssetId"] != str(hidden.asset_id)
                    for edge in detail.json()["edges"]
                )

                exported = await client.get(
                    "/api/v1/assets/export/openlineage",
                    headers=headers,
                    params={"namespace": "catalog.api"},
                )
                assert exported.status_code == 200, exported.text
                assert exported.json()["format"] == "openlineage"
                assert exported.json()["events"]
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


class _CatalogAuthorization:
    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        allowed = request.namespace != "private"
        return AuthorizationDecision(
            allowed=allowed,
            reason_code="test_allow" if allowed else "test_deny",
            summary="catalog API authorization fixture",
            policy_version=1,
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        decision = await self.decide(request)
        if not decision.allowed:
            raise AssertionError("the test should not require a denied namespace")
        return decision
