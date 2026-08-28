from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    OperationalControlVersionConflict,
    PostgresOperationalControlRepository,
    PostgresTenantRepository,
)
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.domain import (
    AnnouncementAudience,
    AnnouncementCreateRequest,
    AnnouncementSeverity,
    OperationalBoundary,
    OperationalControlActionKind,
    OperationalControlActionRequest,
    OperationalControlCreateRequest,
    OperationalControlKind,
    OperationalControlScope,
    OperationalControlState,
    RunningWorkPolicy,
    TenantDefinition,
)
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_operational_controls_are_scoped_acknowledged_audited_and_expired() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, MIGRATIONS)
            tenants = PostgresTenantRepository(engine)
            await tenants.create(
                TenantDefinition(slug="other", display_name="Other tenant"),
                actor_id="test:operator",
            )
            repository = PostgresOperationalControlRepository(engine)
            now = datetime.now(UTC)

            await repository.create_announcement(
                AnnouncementCreateRequest(
                    title="Immediate maintenance",
                    message="Execution starts are paused.",
                    severity=AnnouncementSeverity.WARNING,
                    audience=AnnouncementAudience.TENANT,
                    startsAt=now,
                    expiresAt=now + timedelta(hours=1),
                ),
                tenant_id="default",
                actor_id="test:operator",
            )
            await repository.create_announcement(
                AnnouncementCreateRequest(
                    title="Other tenant",
                    message="Must remain isolated.",
                    severity=AnnouncementSeverity.INFO,
                    audience=AnnouncementAudience.TENANT,
                    startsAt=now,
                    expiresAt=now + timedelta(hours=1),
                ),
                tenant_id="other",
                actor_id="test:other",
            )
            visible = await repository.list_announcements("default")
            assert [item.title for item in visible] == ["Immediate maintenance"]

            async with tenant_transaction(engine, "default") as (connection, _tenant_uuid):
                leaked = await connection.scalar(
                    text(
                        """
                        SELECT count(*)
                        FROM announcements
                        WHERE title = 'Other tenant'
                        """
                    )
                )
            assert leaked == 0

            control = await repository.create_control(
                OperationalControlCreateRequest(
                    kind=OperationalControlKind.KILL_SWITCH,
                    name="Stop expense flow",
                    scope=OperationalControlScope.FLOW,
                    namespace="tests.controls",
                    flowId="expense",
                    boundaries=(
                        OperationalBoundary.NEW_EXECUTIONS,
                        OperationalBoundary.WORKER_DISPATCH,
                    ),
                    runningWorkPolicy=RunningWorkPolicy.CANCEL,
                    reason="incident containment",
                    expiresAt=now + timedelta(hours=1),
                ),
                tenant_id="default",
                actor_id="test:operator",
            )
            assert not (
                await repository.evaluate(
                    OperationalBoundary.NEW_EXECUTIONS,
                    tenant_id="default",
                    namespace="tests.controls",
                    flow_id="other",
                )
            ).blocked
            blocked = await repository.evaluate(
                OperationalBoundary.NEW_EXECUTIONS,
                tenant_id="default",
                namespace="tests.controls",
                flow_id="expense",
                component_id="executor-a",
                component_role="EXECUTOR",
            )
            assert blocked.blocked
            assert blocked.running_work_policy is RunningWorkPolicy.CANCEL
            assert blocked.controls[0].control_id == control.control_id
            listed = await repository.list_controls("default")
            persisted = next(item for item in listed if item.control_id == control.control_id)
            assert persisted.acknowledgements[0].component_id == "executor-a"
            assert persisted.acknowledgements[0].control_version == control.version

            bypassed = await repository.apply_action(
                control.control_id,
                OperationalControlActionRequest(
                    action=OperationalControlActionKind.BYPASS,
                    reason="approved incident validation",
                    expectedVersion=control.version,
                    bypassUntil=now + timedelta(minutes=15),
                ),
                tenant_id="default",
                actor_id="test:operator",
            )
            assert bypassed.state is OperationalControlState.BYPASSED
            assert not (
                await repository.evaluate(
                    OperationalBoundary.NEW_EXECUTIONS,
                    tenant_id="default",
                    namespace="tests.controls",
                    flow_id="expense",
                )
            ).blocked
            with pytest.raises(OperationalControlVersionConflict):
                await repository.apply_action(
                    control.control_id,
                    OperationalControlActionRequest(
                        action=OperationalControlActionKind.DEACTIVATE,
                        reason="stale action",
                        expectedVersion=control.version,
                    ),
                    tenant_id="default",
                    actor_id="test:operator",
                )
            deactivated = await repository.apply_action(
                control.control_id,
                OperationalControlActionRequest(
                    action=OperationalControlActionKind.DEACTIVATE,
                    reason="incident resolved",
                    expectedVersion=bypassed.version,
                ),
                tenant_id="default",
                actor_id="test:operator",
            )
            assert deactivated.state is OperationalControlState.DEACTIVATED

            expiring = await repository.create_control(
                OperationalControlCreateRequest(
                    kind=OperationalControlKind.MAINTENANCE,
                    name="Short maintenance",
                    scope=OperationalControlScope.TENANT,
                    boundaries=(OperationalBoundary.AUTHORING,),
                    runningWorkPolicy=RunningWorkPolicy.DRAIN,
                    reason="verify automatic expiry",
                    expiresAt=datetime.now(UTC) + timedelta(milliseconds=100),
                ),
                tenant_id="default",
                actor_id="test:operator",
            )
            await asyncio.sleep(0.15)
            controls = await repository.list_controls("default")
            expired = next(item for item in controls if item.control_id == expiring.control_id)
            assert expired.state is OperationalControlState.EXPIRED
            actions = [event.action for event in await repository.list_events("default")]
            assert {"ACTIVATE", "BYPASS", "DEACTIVATE", "EXPIRE"} <= set(actions)
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
