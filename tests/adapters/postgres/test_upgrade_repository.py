from __future__ import annotations

import asyncio
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresServiceRegistryRepository,
    PostgresUpgradeRepository,
)
from amesh.adapters.postgres.tenant_context import TenantAdminGrantsUnavailableError
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database
from amesh.plugin_sdk import PluginCatalogManager
from amesh.release_policy import load_upgrade_policy
from amesh.storage import StorageValidationReport
from amesh.upgrade import UpgradeService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"
SOURCE_BOUNDARY = "0032_configuration_feature_flags.sql"
PRE_ADMIN_BOUNDARY = "0074_agent_session_policy_ceiling_mode.sql"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class EmptyObjectStore:
    async def validate_inventory(
        self,
        tenant_id: str,
        *,
        verify_content: bool = True,
    ) -> StorageValidationReport:
        del tenant_id, verify_content
        return StorageValidationReport(
            backend="test",
            objects=0,
            bytes=0,
            verified=0,
        )


def test_current_binary_requires_admin_grants_before_upgrade_repository_work() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            applied = await apply_migrations(
                database.database_url,
                MIGRATIONS,
                target_version=SOURCE_BOUNDARY,
            )
            assert applied[-1] == SOURCE_BOUNDARY

            tenant_id: object
            event_id = uuid4()
            async with engine.begin() as connection:
                tenant_id = await connection.scalar(
                    text("SELECT id FROM tenants WHERE slug = 'default'")
                )
                namespace_id = uuid4()
                flow_id = uuid4()
                duplicate_flow_id = uuid4()
                revision_id = uuid4()
                duplicate_revision_id = uuid4()
                execution_id = uuid4()
                await connection.execute(
                    text(
                        """
                        INSERT INTO namespaces (id, tenant_id, name)
                        VALUES (:namespace_id, :tenant_id, 'tests.upgrade')
                        """
                    ),
                    {"namespace_id": namespace_id, "tenant_id": tenant_id},
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO flows (
                            id, tenant_id, namespace_id, flow_key, active_revision, status
                        ) VALUES (
                            :flow_id, :tenant_id, :namespace_id, 'representative', NULL, 'ACTIVE'
                        )
                        """
                    ),
                    {
                        "flow_id": flow_id,
                        "tenant_id": tenant_id,
                        "namespace_id": namespace_id,
                    },
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO flows (
                            id, tenant_id, namespace_id, flow_key, active_revision, status
                        ) VALUES (
                            :flow_id, :tenant_id, :namespace_id,
                            'representative-copy', NULL, 'ACTIVE'
                        )
                        """
                    ),
                    {
                        "flow_id": duplicate_flow_id,
                        "tenant_id": tenant_id,
                        "namespace_id": namespace_id,
                    },
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO flow_revisions (
                            id, tenant_id, flow_id, revision, semantic_hash,
                            canonical_definition, created_by
                        ) VALUES (
                            :revision_id, :tenant_id, :flow_id, 1, 'upgrade-fixture',
                            CAST(:definition AS jsonb), 'test:upgrade'
                        )
                        """
                    ),
                    {
                        "revision_id": duplicate_revision_id,
                        "tenant_id": tenant_id,
                        "flow_id": duplicate_flow_id,
                        "definition": (
                            '{"id":"representative","namespace":"tests.upgrade",'
                            '"inputs":[{"id":"x","type":"STRING","default":null}],'
                            '"triggers":[{"id":"scheduled","type":"core.cron",'
                            '"cron":"* * * * *","start":null,"interval":null,'
                            '"maxAttempts":3}],'
                            '"tasks":[{"id":"log","type":"core.log","message":"hi",'
                            '"level":null},{"id":"sleep","type":"core.sleep","seconds":1,'
                            '"until":null}]}'
                        ),
                    },
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO flow_revisions (
                            id, tenant_id, flow_id, revision, semantic_hash,
                            canonical_definition, created_by
                        ) VALUES (
                            :revision_id, :tenant_id, :flow_id, 1, 'upgrade-fixture',
                            CAST(:definition AS jsonb), 'test:upgrade'
                        )
                        """
                    ),
                    {
                        "revision_id": revision_id,
                        "tenant_id": tenant_id,
                        "flow_id": flow_id,
                        "definition": (
                            '{"id":"representative","namespace":"tests.upgrade",'
                            '"inputs":[{"id":"x","type":"STRING","default":null}],'
                            '"triggers":[{"id":"scheduled","type":"core.cron",'
                            '"cron":"* * * * *","start":null,"interval":null,'
                            '"maxAttempts":3}],'
                            '"tasks":[{"id":"log","type":"core.log","message":"hi",'
                            '"level":null},{"id":"sleep","type":"core.sleep","seconds":1,'
                            '"until":null}]}'
                        ),
                    },
                )
                await connection.execute(
                    text("UPDATE flows SET active_revision = 1 WHERE id = :flow_id"),
                    {"flow_id": flow_id},
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO executions (
                            id, tenant_id, flow_id, flow_revision_id, namespace_name,
                            flow_key, state, version, created_at, updated_at
                        ) VALUES (
                            :execution_id, :tenant_id, :flow_id, :revision_id,
                            'tests.upgrade', 'representative', 'SUCCESS', 1,
                            clock_timestamp(), clock_timestamp()
                        )
                        """
                    ),
                    {
                        "execution_id": execution_id,
                        "tenant_id": tenant_id,
                        "flow_id": flow_id,
                        "revision_id": revision_id,
                    },
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO execution_events (
                            tenant_id, execution_id, sequence, event_id, event_type,
                            schema_version, idempotency_key, correlation_id, actor_id,
                            reason, occurred_at, payload
                        ) VALUES (
                            :tenant_id, :execution_id, 1, :event_id, 'ExecutionSucceeded',
                            1, :idempotency_key, :correlation_id, 'test:upgrade', NULL,
                            clock_timestamp(), '{"reason":"historical success"}'::jsonb
                        )
                        """
                    ),
                    {
                        "tenant_id": tenant_id,
                        "execution_id": execution_id,
                        "event_id": event_id,
                        "idempotency_key": str(event_id),
                        "correlation_id": uuid4(),
                    },
                )

            pre_admin = await apply_migrations(
                database.database_url,
                MIGRATIONS,
                target_version=PRE_ADMIN_BOUNDARY,
            )
            assert pre_admin[0] == "0033_flow_revisions.sql"
            assert pre_admin[-1] == PRE_ADMIN_BOUNDARY

            repository = PostgresUpgradeRepository(engine)
            service = UpgradeService(
                repository,
                PostgresServiceRegistryRepository(engine),
                PluginCatalogManager(),
                EmptyObjectStore(),  # type: ignore[arg-type]
            )
            with pytest.raises(
                TenantAdminGrantsUnavailableError,
                match="0075_restricted_repository_roles",
            ):
                await repository.inventory()
            with pytest.raises(
                TenantAdminGrantsUnavailableError,
                match="0075_restricted_repository_roles",
            ):
                await service.pre_upgrade("0.1.0", "0.2.0")

            remaining = await apply_migrations(database.database_url, MIGRATIONS)
            assert remaining[0] == "0075_restricted_repository_roles.sql"

            source_inventory = await repository.inventory()
            assert source_inventory.applied_migrations[-1] == remaining[-1]
            assert source_inventory.legacy_execution_events == 1
            assert len(await repository.flow_documents()) == 1
            preflight = await service.pre_upgrade("0.1.0", "0.2.0")
            assert not preflight.safe_to_proceed
            assert preflight.rolling_compatible
            assert len(preflight.rolling_plan) == 6
            preflight_schema = next(
                check for check in preflight.checks if check.name == "schema-and-checksums"
            )
            assert preflight_schema.status.value == "BLOCKED"
            assert preflight_schema.evidence["latestMigration"] == remaining[-1]
            preflight_flow = next(
                check for check in preflight.checks if check.name == "flow-syntax"
            )
            assert preflight_flow.status.value == "PASS"
            assert preflight_flow.detail.startswith("1 unique stored flow definition")

            postflight = await service.post_upgrade("0.1.0", "0.2.0")
            assert not postflight.safe_to_proceed
            postflight_schema = next(
                check for check in postflight.checks if check.name == "schema-and-checksums"
            )
            assert postflight_schema.status.value == "BLOCKED"
            assert postflight_schema.evidence["latestMigration"] == remaining[-1]
            assert any("historical event" in warning for warning in postflight.warnings)

            preview = await repository.preview_event_upcast()
            assert preview.confirmation_phrase == "UPCAST 1"
            with pytest.raises(ValueError, match="exactly match"):
                await repository.upcast_events(
                    "UPCAST",
                    actor_id="test:operator",
                    reason="invalid confirmation",
                )
            migrated = await repository.upcast_events(
                preview.confirmation_phrase,
                actor_id="test:operator",
                reason="complete supported LTS event migration",
                batch_size=1,
            )
            assert migrated.migrated_events == 1
            assert migrated.remaining_events == 0
            async with engine.connect() as connection:
                row = (
                    (
                        await connection.execute(
                            text(
                                "SELECT schema_version, reason FROM execution_events "
                                "WHERE event_id = :event_id"
                            ),
                            {"event_id": event_id},
                        )
                    )
                    .mappings()
                    .one()
                )
                assert row["schema_version"] == 2
                assert row["reason"] == "historical success"
                assert (
                    int(
                        await connection.scalar(
                            text("SELECT count(*) FROM audit_events WHERE event_id = :event_id"),
                            {"event_id": migrated.evidence_event_id},
                        )
                        or 0
                    )
                    == 1
                )
            verified = await service.post_upgrade("0.1.0", "0.2.0")
            assert not verified.safe_to_proceed
            assert not any("historical event" in warning for warning in verified.warnings)
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


def test_current_head_upgrade_preflight_can_report_safe(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            repository = PostgresUpgradeRepository(engine)
            current_head = (await repository.inventory()).applied_migrations[-1]
            policy = load_upgrade_policy()
            current_head_policy = policy.model_copy(
                update={
                    "releases": tuple(
                        release.model_copy(update={"schema_migration": current_head})
                        if release.version == policy.current_version
                        else release
                        for release in policy.releases
                    )
                }
            )
            service = UpgradeService(
                repository,
                PostgresServiceRegistryRepository(engine),
                PluginCatalogManager(),
                EmptyObjectStore(),  # type: ignore[arg-type]
                policy=current_head_policy,
            )

            preflight = await service.pre_upgrade("0.1.0", "0.2.0")

            assert preflight.safe_to_proceed
            assert all(check.status.value != "BLOCKED" for check in preflight.checks)
        finally:
            await engine.dispose()

    asyncio.run(scenario())
