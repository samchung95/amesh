from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresExecutionRepository,
    PostgresMetadataRepository,
    PostgresTenantRepository,
)
from amesh.domain import TenantDefinition
from amesh.dsl import FlowDefinition
from amesh.ports import (
    AssetAccessMode,
    AssetHealth,
    AssetLineageDeclaration,
    AssetMetadata,
    AssetObservationCreate,
    LineageEvidenceKind,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def _asset(*, key: str, account: str = "analytics") -> AssetMetadata:
    return AssetMetadata(
        assetId=uuid4(),
        namespace="catalog.tests",
        provider="postgresql",
        account=account,
        location="warehouse.internal:5432",
        externalKey=key,
        assetType="table",
        displayName=key.replace(".", " / "),
        description=f"Catalog fixture for {key}",
        owner="data-platform",
        contacts=("data@example.test",),
        domainGroup="analytics",
        tags=("qualified", "warehouse"),
        customMetadata={"classification": "internal"},
        labels={"environment": "test"},
    )


def test_asset_catalog_is_durable_tenant_scoped_and_openlineage_exportable(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        metadata = PostgresMetadataRepository(engine)
        executions = PostgresExecutionRepository(engine)
        tenants = PostgresTenantRepository(engine)
        flow = FlowDefinition.model_validate(
            {
                "id": "catalog_flow",
                "namespace": "catalog.tests",
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        try:
            execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                actor_id="catalog-test",
            )
            source = await metadata.upsert_asset(
                _asset(key="raw.orders"),
                tenant_id="default",
                actor_id="catalog-test",
            )
            target = await metadata.upsert_asset(
                _asset(key="curated.orders"),
                tenant_id="default",
                actor_id="catalog-test",
            )
            same_key_other_account = await metadata.upsert_asset(
                _asset(key="raw.orders", account="finance"),
                tenant_id="default",
                actor_id="catalog-test",
            )
            assert same_key_other_account.asset_id != source.asset_id

            await metadata.record_asset_observation(
                AssetObservationCreate(
                    asset=source,
                    accessMode=AssetAccessMode.READ,
                    confidence=0.9,
                    flowId=flow.id,
                    executionId=execution.execution_id,
                ),
                tenant_id="default",
                actor_id="catalog-test",
            )
            await metadata.record_asset_observation(
                AssetObservationCreate(
                    asset=target,
                    accessMode=AssetAccessMode.WRITE,
                    confidence=0.8,
                    flowId=flow.id,
                    executionId=execution.execution_id,
                ),
                tenant_id="default",
                actor_id="catalog-test",
            )

            declaration = AssetLineageDeclaration(
                upstreamAssetId=source.asset_id,
                downstreamAssetId=target.asset_id,
                confidence=0.4,
                flowId=flow.id,
                executionId=execution.execution_id,
                metadata={"contract": "orders-v1"},
            )
            first = await metadata.declare_asset_lineage(
                declaration,
                tenant_id="default",
                namespace=target.namespace,
                actor_id="catalog-test",
            )
            updated = await metadata.declare_asset_lineage(
                declaration.model_copy(update={"confidence": 0.95}),
                tenant_id="default",
                namespace=target.namespace,
                actor_id="catalog-test",
            )
            assert updated.edge_id == first.edge_id
            assert updated.confidence == 0.95

            reloaded = PostgresMetadataRepository(engine)
            entry = await reloaded.get_asset_catalog_entry(
                target.asset_id,
                tenant_id="default",
            )
            assert entry.asset.health is AssetHealth.HEALTHY
            assert entry.asset.last_materialization_at is not None
            assert tuple(item.asset_id for item in entry.upstream) == (source.asset_id,)
            assert {edge.evidence_kind for edge in entry.edges} == {
                LineageEvidenceKind.DECLARED,
                LineageEvidenceKind.INFERRED,
            }
            inferred = next(
                edge for edge in entry.edges if edge.evidence_kind is LineageEvidenceKind.INFERRED
            )
            assert inferred.confidence == pytest.approx(0.64)

            exported = await reloaded.export_asset_catalog(
                tenant_id="default",
                namespace="catalog.tests",
            )
            assert len(exported.events) == 4
            assert all(
                event["schemaURL"].startswith("https://openlineage.io/")
                for event in exported.events
            )
            edge_event = next(
                event for event in exported.events if event["inputs"] and event["outputs"]
            )
            assert edge_event["inputs"][0] == {
                "namespace": "postgresql://analytics/warehouse.internal:5432",
                "name": "raw.orders",
            }
            assert edge_event["outputs"][0]["name"] == "curated.orders"

            other_tenant = TenantDefinition(
                id=uuid4(),
                slug="catalog-other",
                display_name="Catalog other",
            )
            await tenants.create(other_tenant, actor_id="catalog-test")
            await metadata.upsert_asset(
                _asset(key="private.orders"),
                tenant_id=other_tenant.slug,
                actor_id="catalog-test",
            )
            default_ids = {
                item.asset_id for item in await metadata.list_assets(tenant_id="default")
            }
            other_ids = {
                item.asset_id for item in await metadata.list_assets(tenant_id=other_tenant.slug)
            }
            assert default_ids.isdisjoint(other_ids)
            with pytest.raises(LookupError, match="asset unavailable"):
                await metadata.get_asset(source.asset_id, tenant_id=other_tenant.slug)
        finally:
            await engine.dispose()

    asyncio.run(scenario())
