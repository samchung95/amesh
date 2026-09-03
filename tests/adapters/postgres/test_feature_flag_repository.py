from __future__ import annotations

import asyncio
import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresFeatureFlagRepository,
    PostgresTenantRepository,
)
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.domain import FeatureFlag, FeatureFlagScope, TenantDefinition
from amesh.ports import FeatureFlagVersionConflict

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_scoped_feature_flags_are_versioned_audited_and_tenant_isolated(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            tenants = PostgresTenantRepository(engine)
            flags = PostgresFeatureFlagRepository(engine)
            for slug in ("flag-alpha", "flag-beta"):
                await tenants.create(
                    TenantDefinition(slug=slug, display_name=slug),
                    actor_id="flag-test-admin",
                )

            instance = await flags.upsert(
                FeatureFlag(
                    key="new-engine",
                    scope=FeatureFlagScope.INSTANCE,
                    enabled=False,
                    updated_by="flag-test-admin",
                ),
                actor_id="flag-test-admin",
            )
            tenant = await flags.upsert(
                FeatureFlag(
                    key="new-engine",
                    scope=FeatureFlagScope.TENANT,
                    tenant_id="flag-alpha",
                    enabled=True,
                    updated_by="flag-test-admin",
                ),
                actor_id="flag-test-admin",
            )
            namespace = await flags.upsert(
                FeatureFlag(
                    key="new-engine",
                    scope=FeatureFlagScope.NAMESPACE,
                    tenant_id="flag-alpha",
                    namespace="finance.payments",
                    enabled=False,
                    updated_by="flag-test-admin",
                ),
                actor_id="flag-test-admin",
            )
            await flags.upsert(
                FeatureFlag(
                    key="beta-only",
                    scope=FeatureFlagScope.TENANT,
                    tenant_id="flag-beta",
                    enabled=True,
                    updated_by="flag-test-admin",
                ),
                actor_id="flag-test-admin",
            )

            decision = await flags.evaluate(
                "new-engine",
                "flag-alpha",
                namespace="finance.payments",
                default=True,
            )
            assert (decision.enabled, decision.reason) == (False, "NAMESPACE_MATCH")
            visible = await flags.list_for_context("flag-alpha", namespace="finance.payments")
            assert {flag.id for flag in visible} == {instance.id, tenant.id, namespace.id}
            assert "beta-only" not in {flag.key for flag in visible}

            updated = await flags.upsert(
                tenant.model_copy(update={"enabled": False}),
                actor_id="flag-test-admin",
                expected_version=tenant.version,
            )
            assert updated.version == 2
            with pytest.raises(FeatureFlagVersionConflict):
                await flags.upsert(
                    updated.model_copy(update={"enabled": True}),
                    actor_id="flag-test-admin",
                    expected_version=tenant.version,
                )

            async with tenant_transaction(engine, "flag-alpha") as (connection, _tenant_uuid):
                runtime_keys = set(
                    (
                        await connection.execute(
                            text("SELECT flag_key FROM feature_flags ORDER BY flag_key")
                        )
                    ).scalars()
                )
            assert runtime_keys == {"new-engine"}

            await flags.audit_configuration_reload(
                actor_id="flag-test-admin",
                outcome="SUCCESS",
                changed_fields=("log_level",),
                reason="reload accepted",
            )
            async with engine.connect() as connection:
                audit_actions = set(
                    (
                        await connection.execute(
                            text(
                                "SELECT action FROM audit_events WHERE actor_id = 'flag-test-admin'"
                            )
                        )
                    ).scalars()
                )
            assert {"feature-flag.upsert", "configuration.reload"} <= audit_actions
        finally:
            await engine.dispose()

    asyncio.run(scenario())
