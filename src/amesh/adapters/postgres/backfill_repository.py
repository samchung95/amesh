from __future__ import annotations

import json
from uuid import UUID, uuid5

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import (
    BackfillItem,
    BackfillItemState,
    BackfillRecord,
    BackfillSelectionKind,
    BackfillSpec,
    BackfillState,
    new_runtime_id,
)
from amesh.ports import BackfillItemDefinition, BackfillRepository

from .tenant_context import tenant_transaction

_BACKFILL_SELECT = """
    SELECT
        backfills.*,
        tenants.slug AS tenant_slug,
        count(DISTINCT backfill_items.item_id) FILTER (
            WHERE backfill_items.state = 'PENDING'
        )::integer AS pending,
        count(DISTINCT backfill_items.item_id) FILTER (
            WHERE executions.state IN ('CREATED', 'QUEUED', 'RUNNING', 'PAUSED',
                                       'CANCELLING', 'RESTARTING')
        )::integer AS running,
        count(DISTINCT backfill_items.item_id) FILTER (
            WHERE executions.state IN ('SUCCESS', 'WARNING')
        )::integer AS succeeded,
        count(DISTINCT backfill_items.item_id) FILTER (
            WHERE executions.state = 'FAILED'
        )::integer AS failed,
        count(DISTINCT backfill_items.item_id) FILTER (
            WHERE backfill_items.state = 'CANCELLED' OR executions.state = 'CANCELLED'
        )::integer AS cancelled,
        (
            SELECT count(*)::integer
            FROM task_runs AS cost_task_runs
            JOIN backfill_items AS cost_items
              ON cost_items.tenant_id = cost_task_runs.tenant_id
             AND cost_items.execution_id = cost_task_runs.execution_id
            WHERE cost_items.tenant_id = backfills.tenant_id
              AND cost_items.backfill_id = backfills.id
        ) AS actual_cost_units,
        (
            SELECT COALESCE(sum(EXTRACT(epoch FROM (
                COALESCE(duration_executions.terminal_at, clock_timestamp())
                - duration_executions.created_at
            ))), 0)::double precision
            FROM executions AS duration_executions
            JOIN backfill_items AS duration_items
              ON duration_items.tenant_id = duration_executions.tenant_id
             AND duration_items.execution_id = duration_executions.id
            WHERE duration_items.tenant_id = backfills.tenant_id
              AND duration_items.backfill_id = backfills.id
        ) AS duration_seconds
    FROM backfills
    JOIN tenants ON tenants.id = backfills.tenant_id
    LEFT JOIN backfill_items
      ON backfill_items.tenant_id = backfills.tenant_id
     AND backfill_items.backfill_id = backfills.id
    LEFT JOIN executions
      ON executions.tenant_id = backfill_items.tenant_id
     AND executions.id = backfill_items.execution_id
"""


class PostgresBackfillRepository(BackfillRepository):
    """Tenant-isolated durable storage for backfill plans and occurrence lineage."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def create_backfill(
        self,
        spec: BackfillSpec,
        items: tuple[BackfillItemDefinition, ...],
        *,
        tenant_id: str,
        actor_id: str,
        task_count: int,
    ) -> BackfillRecord:
        if not items:
            raise ValueError("a backfill must contain at least one item")
        backfill_id = new_runtime_id()
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await connection.execute(
                text(
                    """
                    INSERT INTO backfills (
                        id, tenant_id, namespace_name, flow_key, flow_revision,
                        state, selection_kind, selection, inputs, labels,
                        max_concurrency, rate_per_minute, priority, task_count,
                        total_items, created_by
                    ) VALUES (
                        :id, :tenant_id, :namespace, :flow_id, :flow_revision,
                        'RUNNING', :selection_kind, CAST(:selection AS jsonb),
                        CAST(:inputs AS jsonb), CAST(:labels AS jsonb),
                        :max_concurrency, :rate_per_minute, :priority, :task_count,
                        :total_items, :created_by
                    )
                    """
                ),
                {
                    "id": backfill_id,
                    "tenant_id": tenant_uuid,
                    "namespace": spec.namespace,
                    "flow_id": spec.flow_id,
                    "flow_revision": spec.flow_revision,
                    "selection_kind": spec.selection.kind.value,
                    "selection": spec.selection.model_dump_json(by_alias=True),
                    "inputs": json.dumps(spec.inputs),
                    "labels": json.dumps(
                        {
                            **spec.labels,
                            "amesh.namespace": spec.namespace,
                            "amesh.flow.id": spec.flow_id,
                            "amesh.flow.revision": str(spec.flow_revision),
                            "amesh.backfill.id": str(backfill_id),
                        }
                    ),
                    "max_concurrency": spec.max_concurrency,
                    "rate_per_minute": spec.rate_per_minute,
                    "priority": spec.priority,
                    "task_count": task_count,
                    "total_items": len(items),
                    "created_by": actor_id,
                },
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO backfill_items (
                        item_id, tenant_id, backfill_id, occurrence_key,
                        scheduled_for, partition_key, source_execution_id
                    ) VALUES (
                        :item_id, :tenant_id, :backfill_id, :occurrence_key,
                        :scheduled_for, :partition_key, :source_execution_id
                    )
                    """
                ),
                [
                    {
                        "item_id": uuid5(backfill_id, item.occurrence_key),
                        "tenant_id": tenant_uuid,
                        "backfill_id": backfill_id,
                        "occurrence_key": item.occurrence_key,
                        "scheduled_for": item.scheduled_for,
                        "partition_key": item.partition_key,
                        "source_execution_id": item.source_execution_id,
                    }
                    for item in items
                ],
            )
            await self._append_event(
                connection,
                tenant_uuid,
                backfill_id,
                event_type="BackfillCreated",
                actor_id=actor_id,
                reason="backfill submitted",
                payload={"total": len(items), "selectionKind": spec.selection.kind.value},
            )
            row = await self._get_row(connection, tenant_uuid, backfill_id)
        if row is None:
            raise RuntimeError("created backfill could not be loaded")
        return _to_backfill(row)

    async def get_backfill(self, backfill_id: UUID, *, tenant_id: str) -> BackfillRecord:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = await self._get_row(connection, tenant_uuid, backfill_id)
        if row is None:
            raise LookupError(f"backfill {backfill_id} does not exist")
        return _to_backfill(row)

    async def list_backfills(self, *, tenant_id: str, limit: int = 100) -> list[BackfillRecord]:
        if limit < 1 or limit > 1000:
            raise ValueError("backfill list limit must be between 1 and 1000")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            _BACKFILL_SELECT
                            + """
                            WHERE backfills.tenant_id = :tenant_id
                            GROUP BY backfills.id, tenants.slug
                            ORDER BY backfills.created_at DESC, backfills.id DESC
                            LIMIT :limit
                            """
                        ),
                        {"tenant_id": tenant_uuid, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_backfill(row) for row in rows]

    async def list_pending_items(
        self, backfill_id: UUID, *, tenant_id: str, limit: int
    ) -> list[BackfillItem]:
        if limit < 1:
            return []
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT backfill_items.*
                            FROM backfill_items
                            JOIN backfills
                              ON backfills.tenant_id = backfill_items.tenant_id
                             AND backfills.id = backfill_items.backfill_id
                            WHERE backfill_items.tenant_id = :tenant_id
                              AND backfill_items.backfill_id = :backfill_id
                              AND backfill_items.state = 'PENDING'
                              AND backfills.state = 'RUNNING'
                            ORDER BY backfill_items.created_at, backfill_items.item_id
                            LIMIT :limit
                            """
                        ),
                        {"tenant_id": tenant_uuid, "backfill_id": backfill_id, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_item(row) for row in rows]

    async def link_execution(
        self,
        backfill_id: UUID,
        item_id: UUID,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> None:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await self._lock_backfill(connection, tenant_uuid, backfill_id)
            result = await connection.execute(
                text(
                    """
                    UPDATE backfill_items
                    SET state = 'CREATED',
                        execution_id = :execution_id,
                        launched_at = COALESCE(launched_at, clock_timestamp())
                    WHERE tenant_id = :tenant_id
                      AND backfill_id = :backfill_id
                      AND item_id = :item_id
                      AND (state = 'PENDING' OR execution_id = :execution_id)
                    RETURNING occurrence_key
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "backfill_id": backfill_id,
                    "item_id": item_id,
                    "execution_id": execution_id,
                },
            )
            occurrence_key = result.scalar_one_or_none()
            if occurrence_key is None:
                raise LookupError(f"pending backfill item {item_id} does not exist")
            await connection.execute(
                text(
                    "UPDATE backfills SET updated_at = clock_timestamp() "
                    "WHERE tenant_id = :tenant_id AND id = :backfill_id"
                ),
                {"tenant_id": tenant_uuid, "backfill_id": backfill_id},
            )
            await self._append_event(
                connection,
                tenant_uuid,
                backfill_id,
                event_type="BackfillExecutionCreated",
                actor_id="system:backfill-worker",
                reason="backfill item launched",
                payload={
                    "itemId": str(item_id),
                    "executionId": str(execution_id),
                    "occurrenceKey": occurrence_key,
                },
            )

    async def transition_backfill(
        self,
        backfill_id: UUID,
        state: BackfillState,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str,
    ) -> BackfillRecord:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            current = await self._lock_backfill(connection, tenant_uuid, backfill_id)
            current_state = BackfillState(current["state"])
            allowed = {
                BackfillState.RUNNING: {BackfillState.PAUSED, BackfillState.CANCELLED},
                BackfillState.PAUSED: {BackfillState.RUNNING, BackfillState.CANCELLED},
                BackfillState.CANCELLED: set(),
                BackfillState.COMPLETED: set(),
            }
            if state is current_state:
                row = await self._get_row(connection, tenant_uuid, backfill_id)
                if row is None:
                    raise LookupError(f"backfill {backfill_id} does not exist")
                return _to_backfill(row)
            if state not in allowed[current_state]:
                raise ValueError(
                    f"backfill cannot transition from {current_state.value} to {state.value}"
                )
            await connection.execute(
                text(
                    """
                    UPDATE backfills
                    SET state = :state,
                        updated_at = clock_timestamp(),
                        finished_at = CASE WHEN :state = 'CANCELLED'
                                           THEN clock_timestamp() ELSE NULL END
                    WHERE tenant_id = :tenant_id AND id = :backfill_id
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "backfill_id": backfill_id,
                    "state": state.value,
                },
            )
            if state is BackfillState.CANCELLED:
                await connection.execute(
                    text(
                        """
                        UPDATE backfill_items SET state = 'CANCELLED'
                        WHERE tenant_id = :tenant_id
                          AND backfill_id = :backfill_id
                          AND state = 'PENDING'
                        """
                    ),
                    {"tenant_id": tenant_uuid, "backfill_id": backfill_id},
                )
            await self._append_event(
                connection,
                tenant_uuid,
                backfill_id,
                event_type=f"Backfill{state.value.title()}",
                actor_id=actor_id,
                reason=reason,
                payload={"previousState": current_state.value, "state": state.value},
            )
            row = await self._get_row(connection, tenant_uuid, backfill_id)
        if row is None:
            raise LookupError(f"backfill {backfill_id} does not exist")
        return _to_backfill(row)

    async def launch_capacity(self, backfill_id: UUID, *, tenant_id: str) -> int:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT
                                backfills.state,
                                backfills.max_concurrency,
                                backfills.rate_per_minute,
                                count(backfill_items.item_id) FILTER (
                                    WHERE executions.state IN (
                                        'CREATED', 'QUEUED', 'RUNNING', 'PAUSED',
                                        'CANCELLING', 'RESTARTING'
                                    )
                                )::integer AS active,
                                count(backfill_items.item_id) FILTER (
                                    WHERE backfill_items.launched_at >=
                                          clock_timestamp() - interval '1 minute'
                                )::integer AS recent
                            FROM backfills
                            LEFT JOIN backfill_items
                              ON backfill_items.tenant_id = backfills.tenant_id
                             AND backfill_items.backfill_id = backfills.id
                            LEFT JOIN executions
                              ON executions.tenant_id = backfill_items.tenant_id
                             AND executions.id = backfill_items.execution_id
                            WHERE backfills.tenant_id = :tenant_id
                              AND backfills.id = :backfill_id
                            GROUP BY backfills.id
                            """
                        ),
                        {"tenant_id": tenant_uuid, "backfill_id": backfill_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError(f"backfill {backfill_id} does not exist")
        if BackfillState(row["state"]) is not BackfillState.RUNNING:
            return 0
        return max(
            min(
                int(row["max_concurrency"]) - int(row["active"]),
                int(row["rate_per_minute"]) - int(row["recent"]),
            ),
            0,
        )

    async def refresh_backfill(self, backfill_id: UUID, *, tenant_id: str) -> BackfillRecord:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            current = await self._lock_backfill(connection, tenant_uuid, backfill_id)
            row = await self._get_row(connection, tenant_uuid, backfill_id)
            if row is None:
                raise LookupError(f"backfill {backfill_id} does not exist")
            if (
                BackfillState(current["state"]) is BackfillState.RUNNING
                and int(row["pending"]) == 0
                and int(row["running"]) == 0
            ):
                await connection.execute(
                    text(
                        """
                        UPDATE backfills
                        SET state = 'COMPLETED', updated_at = clock_timestamp(),
                            finished_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND id = :backfill_id
                        """
                    ),
                    {"tenant_id": tenant_uuid, "backfill_id": backfill_id},
                )
                await self._append_event(
                    connection,
                    tenant_uuid,
                    backfill_id,
                    event_type="BackfillCompleted",
                    actor_id="system:backfill-worker",
                    reason="all generated executions reached terminal state",
                    payload={
                        "succeeded": int(row["succeeded"]),
                        "failed": int(row["failed"]),
                        "cancelled": int(row["cancelled"]),
                    },
                )
                row = await self._get_row(connection, tenant_uuid, backfill_id)
        if row is None:
            raise LookupError(f"backfill {backfill_id} does not exist")
        return _to_backfill(row)

    async def _get_row(
        self, connection: AsyncConnection, tenant_uuid: UUID, backfill_id: UUID
    ) -> RowMapping | None:
        return (
            (
                await connection.execute(
                    text(
                        _BACKFILL_SELECT
                        + """
                        WHERE backfills.tenant_id = :tenant_id
                          AND backfills.id = :backfill_id
                        GROUP BY backfills.id, tenants.slug
                        """
                    ),
                    {"tenant_id": tenant_uuid, "backfill_id": backfill_id},
                )
            )
            .mappings()
            .one_or_none()
        )

    @staticmethod
    async def _lock_backfill(
        connection: AsyncConnection, tenant_uuid: UUID, backfill_id: UUID
    ) -> RowMapping:
        row = (
            (
                await connection.execute(
                    text(
                        """
                        SELECT * FROM backfills
                        WHERE tenant_id = :tenant_id AND id = :backfill_id
                        FOR UPDATE
                        """
                    ),
                    {"tenant_id": tenant_uuid, "backfill_id": backfill_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise LookupError(f"backfill {backfill_id} does not exist")
        return row

    @staticmethod
    async def _append_event(
        connection: AsyncConnection,
        tenant_uuid: UUID,
        backfill_id: UUID,
        *,
        event_type: str,
        actor_id: str,
        reason: str,
        payload: dict[str, object],
    ) -> None:
        await connection.execute(
            text(
                """
                INSERT INTO backfill_events (
                    event_id, tenant_id, backfill_id, sequence,
                    event_type, actor_id, reason, payload
                )
                SELECT
                    :event_id, :tenant_id, :backfill_id,
                    COALESCE(max(sequence), 0) + 1,
                    :event_type, :actor_id, :reason, CAST(:payload AS jsonb)
                FROM backfill_events
                WHERE tenant_id = :tenant_id AND backfill_id = :backfill_id
                """
            ),
            {
                "event_id": new_runtime_id(),
                "tenant_id": tenant_uuid,
                "backfill_id": backfill_id,
                "event_type": event_type,
                "actor_id": actor_id,
                "reason": reason,
                "payload": json.dumps(payload),
            },
        )


def _to_item(row: RowMapping) -> BackfillItem:
    return BackfillItem(
        itemId=row["item_id"],
        backfillId=row["backfill_id"],
        occurrenceKey=row["occurrence_key"],
        state=BackfillItemState(row["state"]),
        scheduledFor=row["scheduled_for"],
        partitionKey=row["partition_key"],
        sourceExecutionId=row["source_execution_id"],
        executionId=row["execution_id"],
    )


def _to_backfill(row: RowMapping) -> BackfillRecord:
    return BackfillRecord(
        backfillId=row["id"],
        tenantId=row["tenant_slug"],
        namespace=row["namespace_name"],
        flowId=row["flow_key"],
        flowRevision=row["flow_revision"],
        state=BackfillState(row["state"]),
        selectionKind=BackfillSelectionKind(row["selection_kind"]),
        inputs=dict(row["inputs"]),
        labels=dict(row["labels"]),
        maxConcurrency=row["max_concurrency"],
        ratePerMinute=row["rate_per_minute"],
        priority=row["priority"],
        total=row["total_items"],
        pending=row["pending"],
        running=row["running"],
        succeeded=row["succeeded"],
        failed=row["failed"],
        cancelled=row["cancelled"],
        durationSeconds=row["duration_seconds"],
        estimatedCostUnits=row["total_items"] * row["task_count"],
        actualCostUnits=row["actual_cost_units"],
        createdBy=row["created_by"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
        finishedAt=row["finished_at"],
    )
