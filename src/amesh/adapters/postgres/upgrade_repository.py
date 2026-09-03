from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.adapters.postgres.tenant_context import resolve_active_tenant_id
from amesh.domain import PersistedEventMigration, UpgradeDatabaseInventory, new_runtime_id
from amesh.ports.repository_support import AuditWrite
from amesh.ports.upgrade_repository import UpgradeRepository

from .repository_support import PostgresRepositoryBase


class PostgresUpgradeRepository(PostgresRepositoryBase, UpgradeRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def inventory(self) -> UpgradeDatabaseInventory:
        async with self._services.transactions.admin() as connection:
            migrations = (
                (
                    await connection.execute(
                        text(
                            "SELECT version, checksum FROM amesh_schema_migrations ORDER BY version"
                        )
                    )
                )
                .mappings()
                .all()
            )
            values = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT
                                pg_database_size(current_database()) AS database_bytes,
                                (SELECT count(*) FROM durable_work_queue
                                 WHERE state IN ('READY', 'CLAIMED')) AS queued_work,
                                (SELECT count(*) FROM executions
                                 WHERE state NOT IN (
                                     'SUCCESS', 'FAILED', 'CANCELLED', 'KILLED'
                                 )) AS active_executions,
                                (SELECT count(*) FROM execution_events WHERE schema_version < 2)
                                    AS legacy_execution_events,
                                (SELECT count(*) FROM execution_events WHERE schema_version > 2)
                                    AS unsupported_execution_events
                            """
                        )
                    )
                )
                .mappings()
                .one()
            )
        return UpgradeDatabaseInventory(
            appliedMigrations=tuple(str(row["version"]) for row in migrations),
            migrationChecksums={str(row["version"]): str(row["checksum"]) for row in migrations},
            **dict(values),
        )

    async def flow_documents(self) -> tuple[Mapping[str, Any], ...]:
        async with self._services.transactions.admin() as connection:
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT DISTINCT ON (semantic_hash) canonical_definition
                            FROM flow_revisions
                            ORDER BY semantic_hash, tenant_id, flow_id, revision
                            """
                        )
                    )
                )
                .mappings()
                .all()
            )
        return tuple(row["canonical_definition"] for row in rows)

    async def tenant_slugs(self) -> tuple[str, ...]:
        async with self._services.transactions.admin() as connection:
            values = await connection.scalars(
                text("SELECT slug FROM tenants WHERE lifecycle <> 'TOMBSTONED' ORDER BY slug")
            )
        return tuple(str(value) for value in values)

    async def preview_event_upcast(self) -> PersistedEventMigration:
        async with self._services.transactions.admin() as connection:
            eligible = int(
                await connection.scalar(
                    text("SELECT count(*) FROM execution_events WHERE schema_version < 2")
                )
                or 0
            )
        return PersistedEventMigration(
            eligibleEvents=eligible,
            migratedEvents=0,
            remainingEvents=eligible,
            confirmationPhrase=f"UPCAST {eligible}",
            applied=False,
        )

    async def upcast_events(
        self,
        confirmation: str,
        *,
        actor_id: str,
        reason: str,
        batch_size: int = 1_000,
    ) -> PersistedEventMigration:
        if batch_size < 1 or batch_size > 10_000:
            raise ValueError("event upcast batch size must be between 1 and 10000")
        evidence_id = new_runtime_id()
        async with self._services.transactions.admin() as connection:
            eligible = int(
                await connection.scalar(
                    text("SELECT count(*) FROM execution_events WHERE schema_version < 2")
                )
                or 0
            )
            required = f"UPCAST {eligible}"
            if confirmation != required:
                raise ValueError(f"confirmation must exactly match {required!r}")
            result = await connection.execute(
                text(
                    """
                    WITH candidates AS (
                        SELECT tenant_id, execution_id, sequence
                        FROM execution_events
                        WHERE schema_version < 2
                        ORDER BY tenant_id, execution_id, sequence
                        LIMIT :batch_size
                        FOR UPDATE SKIP LOCKED
                    )
                    UPDATE execution_events AS events
                    SET schema_version = 2,
                        idempotency_key = COALESCE(
                            events.idempotency_key, events.event_id::text
                        ),
                        reason = COALESCE(events.reason, events.payload ->> 'reason')
                    FROM candidates
                    WHERE events.tenant_id = candidates.tenant_id
                      AND events.execution_id = candidates.execution_id
                      AND events.sequence = candidates.sequence
                    """
                ),
                {"batch_size": batch_size},
            )
            migrated = max(result.rowcount or 0, 0)
            remaining = int(
                await connection.scalar(
                    text("SELECT count(*) FROM execution_events WHERE schema_version < 2")
                )
                or 0
            )
            default_tenant_id = await resolve_active_tenant_id(connection, "default")
            await self._services.audit.write(
                connection,
                AuditWrite(
                    tenant_id=default_tenant_id,
                    actor_id=actor_id,
                    action="upgrade.events.upcast",
                    resource_type="instance",
                    resource_id=None,
                    reason=reason,
                    source={"component": "upgrade-service"},
                    evidence={
                        "eligibleEvents": eligible,
                        "migratedEvents": migrated,
                        "remainingEvents": remaining,
                    },
                    event_id=evidence_id,
                    use_database_clock=True,
                    generate_correlation_id=False,
                ),
            )
        return PersistedEventMigration(
            eligibleEvents=eligible,
            migratedEvents=migrated,
            remainingEvents=remaining,
            confirmationPhrase=required,
            applied=True,
            evidenceEventId=evidence_id,
        )
