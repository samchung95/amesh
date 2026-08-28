from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.domain import new_runtime_id
from amesh.domain.agent_sessions import (
    AgentSessionCheckpoint,
    AgentSessionCounters,
    AgentSessionDetail,
    AgentSessionEvent,
    AgentSessionPhase,
    AgentSessionRecord,
    AgentSessionStart,
    AgentSessionState,
    AgentSessionTransition,
)

from .tenant_context import tenant_transaction


class PostgresAgentSessionRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    @asynccontextmanager
    async def session_guard(
        self,
        tenant_id: str,
        task_run_id: UUID,
        attempt: int,
    ) -> AsyncIterator[None]:
        lock_key = f"agent-session:{tenant_id}:{task_run_id}:{attempt}"
        async with self._engine.connect() as connection:
            acquired = await connection.scalar(
                text("SELECT pg_try_advisory_lock(hashtextextended(:lock_key, 0))"),
                {"lock_key": lock_key},
            )
            if acquired is not True:
                raise RuntimeError("agent session is already running on another worker")
            try:
                yield
            finally:
                await connection.execute(
                    text("SELECT pg_advisory_unlock(hashtextextended(:lock_key, 0))"),
                    {"lock_key": lock_key},
                )

    async def start_session(self, start: AgentSessionStart) -> AgentSessionRecord:
        checkpoint = AgentSessionCheckpoint()
        counters = AgentSessionCounters()
        async with tenant_transaction(self._engine, start.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            inserted = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO agent_sessions (
                                session_id, tenant_id, namespace_name, execution_id,
                                task_run_id, attempt, capability_pin_id, envelope_digest,
                                state, phase, checkpoint, counters
                            ) VALUES (
                                :session_id, :tenant_id, :namespace, :execution_id,
                                :task_run_id, :attempt, :capability_pin_id, :envelope_digest,
                                'RUNNING', 'READY', CAST(:checkpoint AS jsonb),
                                CAST(:counters AS jsonb)
                            )
                            ON CONFLICT (tenant_id, task_run_id, attempt) DO NOTHING
                            RETURNING *
                            """
                        ),
                        {
                            "session_id": start.session_id,
                            "tenant_id": tenant_uuid,
                            "namespace": start.namespace,
                            "execution_id": start.execution_id,
                            "task_run_id": start.task_run_id,
                            "attempt": start.attempt,
                            "capability_pin_id": start.capability_pin_id,
                            "envelope_digest": start.envelope_digest,
                            "checkpoint": checkpoint.model_dump_json(by_alias=True),
                            "counters": counters.model_dump_json(by_alias=True),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            row = inserted
            if row is None:
                row = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT * FROM agent_sessions
                                WHERE tenant_id = :tenant_id
                                  AND task_run_id = :task_run_id
                                  AND attempt = :attempt
                                """
                            ),
                            {
                                "tenant_id": tenant_uuid,
                                "task_run_id": start.task_run_id,
                                "attempt": start.attempt,
                            },
                        )
                    )
                    .mappings()
                    .one()
                )
                if (
                    UUID(str(row["capability_pin_id"])) != start.capability_pin_id
                    or row["envelope_digest"] != start.envelope_digest
                    or UUID(str(row["execution_id"])) != start.execution_id
                ):
                    raise ValueError("agent session identity is already bound to another envelope")
        return _session_record(row, start.tenant_id)

    async def transition(
        self,
        session_id: UUID,
        *,
        tenant_id: str,
        transition: AgentSessionTransition,
    ) -> AgentSessionRecord:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM agent_sessions
                            WHERE tenant_id = :tenant_id AND session_id = :session_id
                            FOR UPDATE
                            """
                        ),
                        {"tenant_id": tenant_uuid, "session_id": session_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError(f"agent session {session_id} does not exist")
            existing_event = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT event_type, payload FROM agent_session_events
                            WHERE tenant_id = :tenant_id
                              AND session_id = :session_id
                              AND event_key = :event_key
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "session_id": session_id,
                            "event_key": transition.event_key,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if existing_event is not None:
                if (
                    existing_event["event_type"] != transition.event_type
                    or existing_event["payload"] != transition.payload
                ):
                    raise ValueError("agent session event key was reused with different evidence")
                return _session_record(row, tenant_id)
            if AgentSessionState(row["state"]) is not AgentSessionState.RUNNING:
                raise RuntimeError(f"agent session {session_id} is already {row['state']}")

            next_version = int(row["version"]) + 1
            event_id = new_runtime_id()
            await connection.execute(
                text(
                    """
                    INSERT INTO agent_session_events (
                        event_id, tenant_id, execution_id, task_run_id, session_id,
                        event_index, event_key, event_type, payload
                    ) VALUES (
                        :event_id, :tenant_id, :execution_id, :task_run_id, :session_id,
                        :event_index, :event_key, :event_type, CAST(:payload AS jsonb)
                    )
                    """
                ),
                {
                    "event_id": event_id,
                    "tenant_id": tenant_uuid,
                    "execution_id": row["execution_id"],
                    "task_run_id": row["task_run_id"],
                    "session_id": session_id,
                    "event_index": next_version,
                    "event_key": transition.event_key,
                    "event_type": transition.event_type,
                    "payload": json.dumps(transition.payload),
                },
            )
            updated = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE agent_sessions
                            SET state = :state,
                                phase = :phase,
                                version = :version,
                                checkpoint = CAST(:checkpoint AS jsonb),
                                counters = CAST(:counters AS jsonb),
                                final_result = CAST(:final_result AS jsonb),
                                error = :error,
                                updated_at = clock_timestamp(),
                                completed_at = CASE
                                    WHEN :state = 'RUNNING' THEN NULL
                                    ELSE clock_timestamp()
                                END
                            WHERE tenant_id = :tenant_id AND session_id = :session_id
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "session_id": session_id,
                            "state": transition.state.value,
                            "phase": transition.phase.value,
                            "version": next_version,
                            "checkpoint": transition.checkpoint.model_dump_json(by_alias=True),
                            "counters": transition.counters.model_dump_json(by_alias=True),
                            "final_result": (
                                json.dumps(transition.final_result)
                                if transition.final_result is not None
                                else None
                            ),
                            "error": transition.error,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return _session_record(updated, tenant_id)

    async def get_session(
        self,
        tenant_id: str,
        task_run_id: UUID,
        attempt: int,
    ) -> AgentSessionDetail:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM agent_sessions
                            WHERE tenant_id = :tenant_id
                              AND task_run_id = :task_run_id
                              AND attempt = :attempt
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "task_run_id": task_run_id,
                            "attempt": attempt,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError("agent session does not exist")
            event_rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM agent_session_events
                            WHERE tenant_id = :tenant_id AND session_id = :session_id
                            ORDER BY event_index
                            """
                        ),
                        {"tenant_id": tenant_uuid, "session_id": row["session_id"]},
                    )
                )
                .mappings()
                .all()
            )
        return AgentSessionDetail(
            session=_session_record(row, tenant_id),
            events=tuple(_session_event(item) for item in event_rows),
        )

    async def list_execution_sessions(
        self,
        tenant_id: str,
        execution_id: UUID,
    ) -> tuple[AgentSessionRecord, ...]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM agent_sessions
                            WHERE tenant_id = :tenant_id AND execution_id = :execution_id
                            ORDER BY created_at, session_id
                            """
                        ),
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_session_record(row, tenant_id) for row in rows)


def _session_record(row: RowMapping, tenant_id: str) -> AgentSessionRecord:
    return AgentSessionRecord(
        sessionId=row["session_id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        executionId=row["execution_id"],
        taskRunId=row["task_run_id"],
        attempt=row["attempt"],
        capabilityPinId=row["capability_pin_id"],
        envelopeDigest=row["envelope_digest"],
        state=AgentSessionState(row["state"]),
        phase=AgentSessionPhase(row["phase"]),
        version=row["version"],
        checkpoint=AgentSessionCheckpoint.model_validate(row["checkpoint"]),
        counters=AgentSessionCounters.model_validate(row["counters"]),
        finalResult=row["final_result"],
        error=row["error"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
        completedAt=row["completed_at"],
    )


def _session_event(row: RowMapping) -> AgentSessionEvent:
    return AgentSessionEvent(
        eventId=row["event_id"],
        sessionId=row["session_id"],
        eventIndex=row["event_index"],
        eventKey=row["event_key"],
        eventType=row["event_type"],
        payload=row["payload"],
        occurredAt=row["occurred_at"],
    )
