from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.ports.scheduler_repository import (
    SchedulerFenceError,
    SchedulerRepository,
    ScheduleState,
)

from .tenant_context import tenant_transaction

_ENSURE_SCHEDULE = text(
    """
    INSERT INTO scheduler_states (
        trigger_definition_id, tenant_id, namespace_name, flow_key,
        flow_revision, trigger_key, next_fire_at
    )
    SELECT
        trigger_definitions.id,
        trigger_definitions.tenant_id,
        namespaces.name,
        flows.flow_key,
        flow_revisions.revision,
        trigger_definitions.trigger_key,
        CAST(:initial_next_fire_at AS timestamptz)
    FROM trigger_definitions
    JOIN flow_revisions ON flow_revisions.id = trigger_definitions.flow_revision_id
    JOIN flows ON flows.id = flow_revisions.flow_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    WHERE trigger_definitions.tenant_id = :tenant_id
      AND namespaces.name = :namespace
      AND flows.flow_key = :flow_key
      AND flow_revisions.revision = :flow_revision
      AND trigger_definitions.trigger_key = :trigger_key
    ON CONFLICT (trigger_definition_id) DO UPDATE SET
        next_fire_at = COALESCE(scheduler_states.next_fire_at, EXCLUDED.next_fire_at),
        last_decision = CASE
            WHEN scheduler_states.next_fire_at IS NULL
                THEN 'scheduler initialized rebuilt projection'
            ELSE scheduler_states.last_decision
        END,
        updated_at = CASE
            WHEN scheduler_states.next_fire_at IS NULL
                THEN clock_timestamp()
            ELSE scheduler_states.updated_at
        END
    """
)

_CLAIM_SCHEDULE = text(
    """
    UPDATE scheduler_states
    SET owner_id = :owner_id,
        fencing_token = fencing_token + 1,
        lease_expires_at = clock_timestamp() + make_interval(secs => :lease_seconds),
        updated_at = clock_timestamp()
    WHERE tenant_id = :tenant_id
      AND namespace_name = :namespace
      AND flow_key = :flow_key
      AND flow_revision = :flow_revision
      AND trigger_key = :trigger_key
      AND next_fire_at IS NOT NULL
      AND next_fire_at <= :due_before
      AND (
          owner_id = :owner_id
          OR lease_expires_at IS NULL
          OR lease_expires_at <= clock_timestamp()
      )
    RETURNING *
    """
)

_GET_SCHEDULE = text(
    """
    SELECT *
    FROM scheduler_states
    WHERE tenant_id = :tenant_id
      AND namespace_name = :namespace
      AND flow_key = :flow_key
      AND flow_revision = :flow_revision
      AND trigger_key = :trigger_key
    """
)

_COMPLETE_SCHEDULE = text(
    """
    UPDATE scheduler_states
    SET next_fire_at = CAST(:next_fire_at AS timestamptz),
        last_evaluated_at = :evaluated_at,
        last_occurrence_at = COALESCE(
            CAST(:last_occurrence_at AS timestamptz),
            last_occurrence_at
        ),
        owner_id = NULL,
        lease_expires_at = NULL,
        last_decision = :decision,
        missed_count = :missed_count,
        updated_at = clock_timestamp()
    WHERE trigger_definition_id = :trigger_definition_id
      AND tenant_id = :tenant_id
      AND owner_id = :owner_id
      AND fencing_token = :fencing_token
      AND lease_expires_at > clock_timestamp()
    RETURNING *
    """
)

_GET_BY_ID = text(
    """
    SELECT *
    FROM scheduler_states
    WHERE trigger_definition_id = :trigger_definition_id
      AND tenant_id = :tenant_id
    """
)


class PostgresSchedulerRepository(SchedulerRepository):
    """PostgreSQL schedule cursor and fenced ownership adapter."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def database_time(self) -> datetime:
        async with self._engine.connect() as connection:
            value = await connection.scalar(text("SELECT clock_timestamp()"))
        if not isinstance(value, datetime):
            raise TypeError("PostgreSQL returned a non-datetime clock value")
        return value

    async def claim_schedule(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        flow_revision: int,
        trigger_id: str,
        initial_next_fire_at: datetime | None,
        due_before: datetime,
        owner_id: UUID,
        lease_duration: timedelta,
    ) -> ScheduleState:
        lease_seconds = lease_duration.total_seconds()
        if lease_seconds <= 0:
            raise ValueError("scheduler lease duration must be positive")
        parameters = {
            "namespace": namespace,
            "flow_key": flow_id,
            "flow_revision": flow_revision,
            "trigger_key": trigger_id,
        }
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await connection.execute(
                _ENSURE_SCHEDULE,
                {
                    **parameters,
                    "tenant_id": tenant_uuid,
                    "initial_next_fire_at": initial_next_fire_at,
                },
            )
            row = (
                (
                    await connection.execute(
                        _CLAIM_SCHEDULE,
                        {
                            **parameters,
                            "tenant_id": tenant_uuid,
                            "owner_id": owner_id,
                            "due_before": due_before,
                            "lease_seconds": lease_seconds,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            claimed = row is not None
            if row is None:
                row = (
                    (
                        await connection.execute(
                            _GET_SCHEDULE,
                            {**parameters, "tenant_id": tenant_uuid},
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
        if row is None:
            raise LookupError(
                f"schedule {namespace}.{flow_id}@{flow_revision}/{trigger_id} does not exist"
            )
        return _to_schedule_state(row, tenant_id=tenant_id, claimed=claimed)

    async def complete_schedule(
        self,
        *,
        tenant_id: str,
        trigger_definition_id: UUID,
        owner_id: UUID,
        fencing_token: int,
        evaluated_at: datetime,
        next_fire_at: datetime | None,
        last_occurrence_at: datetime | None,
        decision: str,
        missed_count: int,
    ) -> ScheduleState:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _COMPLETE_SCHEDULE,
                        {
                            "tenant_id": tenant_uuid,
                            "trigger_definition_id": trigger_definition_id,
                            "owner_id": owner_id,
                            "fencing_token": fencing_token,
                            "evaluated_at": evaluated_at,
                            "next_fire_at": next_fire_at,
                            "last_occurrence_at": last_occurrence_at,
                            "decision": decision,
                            "missed_count": missed_count,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise SchedulerFenceError(
                f"schedule {trigger_definition_id} ownership is expired or superseded"
            )
        return _to_schedule_state(row, tenant_id=tenant_id)

    async def get_schedule_state(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        flow_revision: int,
        trigger_id: str,
    ) -> ScheduleState:
        parameters = {
            "namespace": namespace,
            "flow_key": flow_id,
            "flow_revision": flow_revision,
            "trigger_key": trigger_id,
        }
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _GET_SCHEDULE,
                        {**parameters, "tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError(
                f"schedule {namespace}.{flow_id}@{flow_revision}/{trigger_id} does not exist"
            )
        return _to_schedule_state(row, tenant_id=tenant_id)


def _to_schedule_state(
    row: RowMapping,
    *,
    tenant_id: str,
    claimed: bool = False,
) -> ScheduleState:
    return ScheduleState(
        trigger_definition_id=row["trigger_definition_id"],
        tenant_id=tenant_id,
        namespace=row["namespace_name"],
        flow_id=row["flow_key"],
        flow_revision=row["flow_revision"],
        trigger_id=row["trigger_key"],
        next_fire_at=row["next_fire_at"],
        last_evaluated_at=row["last_evaluated_at"],
        last_occurrence_at=row["last_occurrence_at"],
        owner_id=row["owner_id"],
        fencing_token=row["fencing_token"],
        lease_expires_at=row["lease_expires_at"],
        last_decision=row["last_decision"],
        missed_count=row["missed_count"],
        claimed=claimed,
    )
