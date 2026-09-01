from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.domain import new_runtime_id
from amesh.domain.agent_progress import (
    AgentProgressEvent,
    AgentProgressFrame,
    AgentProgressLimitExceeded,
    AgentProgressLimits,
    AgentProgressSequenceState,
    AgentProgressStatus,
    AgentSessionEventCursor,
    accept_progress_frame,
    close_progress_segment,
    make_truncated_progress_frame,
    project_agent_session_lifecycle_frame,
)
from amesh.domain.agent_sessions import (
    AgentHarnessPin,
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
from amesh.ports.agent_progress import (
    AgentProgressContext,
    AgentProgressReceipt,
)

from .tenant_context import tenant_transaction


class PostgresAgentSessionRepository:
    def __init__(
        self,
        engine: AsyncEngine,
        *,
        progress_limits: AgentProgressLimits | None = None,
    ) -> None:
        self._engine = engine
        self._progress_limits = progress_limits or AgentProgressLimits()

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
                                harness_adapter, harness_version, harness_protocol,
                                state, phase, checkpoint, counters
                            ) VALUES (
                                :session_id, :tenant_id, :namespace, :execution_id,
                                :task_run_id, :attempt, :capability_pin_id, :envelope_digest,
                                :harness_adapter, :harness_version, :harness_protocol,
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
                            "harness_adapter": (
                                start.harness.adapter if start.harness is not None else None
                            ),
                            "harness_version": (
                                start.harness.adapter_version if start.harness is not None else None
                            ),
                            "harness_protocol": (
                                start.harness.protocol if start.harness is not None else None
                            ),
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
                                harness_adapter = COALESCE(:harness_adapter, harness_adapter),
                                harness_version = COALESCE(:harness_version, harness_version),
                                harness_protocol = COALESCE(:harness_protocol, harness_protocol),
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
                            "harness_adapter": (
                                transition.harness.adapter
                                if transition.harness is not None
                                else None
                            ),
                            "harness_version": (
                                transition.harness.adapter_version
                                if transition.harness is not None
                                else None
                            ),
                            "harness_protocol": (
                                transition.harness.protocol
                                if transition.harness is not None
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

    async def append_progress(
        self,
        context: AgentProgressContext,
        frame: AgentProgressFrame,
        *,
        limits: AgentProgressLimits | None = None,
    ) -> AgentProgressReceipt:
        """Append one safe progress frame to the canonical session journal.

        Progress frames share ``agent_session_events`` with lifecycle events.  The
        locked session row supplies the canonical event index, so a progress write
        and a lifecycle transition cannot allocate the same index.
        """

        if frame.attempt_session_id != context.attempt_session_id:
            raise ValueError("progress frame belongs to a different attempt session")
        if frame.attempt != context.attempt:
            raise ValueError("progress frame belongs to a different attempt")
        effective_limits = limits or self._progress_limits
        event_key = frame.event_key
        event_type = "progress.frame"
        async with tenant_transaction(self._engine, context.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            session = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT sessions.*, executions.trigger_context
                            FROM agent_sessions AS sessions
                            JOIN executions ON executions.id = sessions.execution_id
                            WHERE sessions.tenant_id = :tenant_id
                              AND executions.tenant_id = :tenant_id
                              AND sessions.session_id = :session_id
                              AND sessions.task_run_id = :task_run_id
                              AND sessions.attempt = :attempt
                            FOR UPDATE OF sessions
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "session_id": context.attempt_session_id,
                            "task_run_id": context.task_run_id,
                            "attempt": context.attempt,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if session is None:
                raise LookupError("agent session does not exist")
            if UUID(str(session["execution_id"])) != context.execution_id:
                raise ValueError("progress context is bound to a different execution")
            if _logical_service_session_id(session) != context.service_session_id:
                raise ValueError("progress context is bound to a different service session")

            existing = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT event_id, event_index, event_type, payload
                            FROM agent_session_events
                            WHERE tenant_id = :tenant_id
                              AND session_id = :session_id
                              AND event_key = :event_key
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "session_id": context.attempt_session_id,
                            "event_key": event_key,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if existing is not None:
                _require_same_progress_frame(existing, frame, event_type)
                cursor = AgentSessionEventCursor(
                    serviceSessionId=context.service_session_id,
                    attemptSessionId=context.attempt_session_id,
                    attempt=context.attempt,
                    eventIndex=int(existing["event_index"]),
                ).encode()
                return AgentProgressReceipt(
                    eventId=existing["event_id"],
                    eventIndex=existing["event_index"],
                    cursor=cursor,
                    duplicate=True,
                    truncated=(
                        _progress_frame_from_payload(existing["payload"]).status
                        is AgentProgressStatus.TRUNCATED
                    ),
                )
            if session["state"] != AgentSessionState.RUNNING.value:
                raise RuntimeError(
                    f"agent session {context.attempt_session_id} is already {session['state']}"
                )

            progress_rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT event_id, event_index, event_type, payload
                            FROM agent_session_events
                            WHERE tenant_id = :tenant_id
                              AND session_id = :session_id
                            ORDER BY event_index
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "session_id": context.attempt_session_id,
                        },
                    )
                )
                .mappings()
                .all()
            )
            state = AgentProgressSequenceState()
            truncated_event: RowMapping | None = None
            for progress_row in progress_rows:
                if progress_row["event_type"] == event_type:
                    persisted_frame = _progress_frame_from_payload(progress_row["payload"])
                    state = accept_progress_frame(
                        state,
                        persisted_frame,
                        limits=effective_limits,
                    ).state
                    if persisted_frame.status is AgentProgressStatus.TRUNCATED:
                        truncated_event = progress_row
                else:
                    state = close_progress_segment(state)
            if truncated_event is not None:
                cursor = AgentSessionEventCursor(
                    serviceSessionId=context.service_session_id,
                    attemptSessionId=context.attempt_session_id,
                    attempt=context.attempt,
                    eventIndex=int(truncated_event["event_index"]),
                ).encode()
                return AgentProgressReceipt(
                    eventId=truncated_event["event_id"],
                    eventIndex=truncated_event["event_index"],
                    cursor=cursor,
                    truncated=True,
                )
            try:
                accept_progress_frame(state, frame, limits=effective_limits)
            except AgentProgressLimitExceeded:
                # Commit one deterministic, non-sensitive terminal marker.  The
                # marker is deliberately allowed to exceed the producer quota so
                # observers can distinguish truncation from an ordinary failure.
                frame = make_truncated_progress_frame(frame, state)
                event_key = frame.event_key
                existing = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT event_id, event_index, event_type, payload
                                FROM agent_session_events
                                WHERE tenant_id = :tenant_id
                                  AND session_id = :session_id
                                  AND event_key = :event_key
                                """
                            ),
                            {
                                "tenant_id": tenant_uuid,
                                "session_id": context.attempt_session_id,
                                "event_key": event_key,
                            },
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if existing is not None:
                    _require_same_progress_frame(existing, frame, event_type)
                    cursor = AgentSessionEventCursor(
                        serviceSessionId=context.service_session_id,
                        attemptSessionId=context.attempt_session_id,
                        attempt=context.attempt,
                        eventIndex=int(existing["event_index"]),
                    ).encode()
                    return AgentProgressReceipt(
                        eventId=existing["event_id"],
                        eventIndex=existing["event_index"],
                        cursor=cursor,
                        duplicate=True,
                        truncated=True,
                    )

            event_id = new_runtime_id()
            event_index = int(session["version"]) + 1
            payload = _progress_payload(frame)
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
                    "execution_id": session["execution_id"],
                    "task_run_id": session["task_run_id"],
                    "session_id": context.attempt_session_id,
                    "event_index": event_index,
                    "event_key": event_key,
                    "event_type": event_type,
                    "payload": json.dumps(payload, separators=(",", ":")),
                },
            )
            await connection.execute(
                text(
                    """
                    UPDATE agent_sessions
                    SET version = :version, updated_at = clock_timestamp()
                    WHERE tenant_id = :tenant_id AND session_id = :session_id
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "session_id": context.attempt_session_id,
                    "version": event_index,
                },
            )
        cursor = AgentSessionEventCursor(
            serviceSessionId=context.service_session_id,
            attemptSessionId=context.attempt_session_id,
            attempt=context.attempt,
            eventIndex=event_index,
        ).encode()
        return AgentProgressReceipt(
            eventId=event_id,
            eventIndex=event_index,
            cursor=cursor,
            truncated=frame.status is AgentProgressStatus.TRUNCATED,
        )

    async def list_progress_events(
        self,
        tenant_id: str,
        service_session_id: UUID,
        *,
        after: AgentSessionEventCursor | None = None,
        limit: int = 100,
    ) -> tuple[AgentProgressEvent, ...]:
        """Read the canonical journal as safe progress events across attempts."""

        if after is not None:
            after.require_service_session(service_session_id)
        bounded_limit = max(1, min(limit, 1000))
        after_attempt = after.attempt if after is not None else 0
        after_index = after.event_index if after is not None else 0
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            if after is not None and after.attempt > 0:
                cursor_exists = await connection.scalar(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1
                            FROM agent_session_events AS events
                            JOIN agent_sessions AS sessions
                              ON sessions.tenant_id = events.tenant_id
                             AND sessions.session_id = events.session_id
                            JOIN executions
                              ON executions.id = events.execution_id
                             AND executions.tenant_id = events.tenant_id
                            WHERE events.tenant_id = :tenant_id
                              AND COALESCE(
                                  NULLIF(
                                      executions.trigger_context
                                          ->>'ameshAgentSessionId',
                                      ''
                                  ),
                                  events.session_id::text
                              ) = :service_session_id
                              AND events.session_id = :after_session_id
                              AND sessions.attempt = :after_attempt
                              AND events.event_index = :after_index
                        )
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "service_session_id": str(service_session_id),
                        "after_session_id": after.attempt_session_id,
                        "after_attempt": after_attempt,
                        "after_index": after_index,
                    },
                )
                if cursor_exists is not True:
                    raise ValueError("agent-session cursor does not identify a canonical event")
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT events.*, sessions.attempt
                            FROM agent_session_events AS events
                            JOIN agent_sessions AS sessions
                              ON sessions.tenant_id = events.tenant_id
                             AND sessions.session_id = events.session_id
                            JOIN executions ON executions.id = events.execution_id
                            WHERE events.tenant_id = :tenant_id
                              AND executions.tenant_id = :tenant_id
                              AND COALESCE(
                                  NULLIF(
                                      executions.trigger_context
                                          ->>'ameshAgentSessionId',
                                      ''
                                  ),
                                  events.session_id::text
                              ) = :service_session_id
                              AND (
                                  sessions.attempt > :after_attempt
                                  OR (
                                      sessions.attempt = :after_attempt
                                      AND events.event_index > :after_index
                                  )
                              )
                            ORDER BY sessions.attempt, events.event_index
                            LIMIT :limit
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "service_session_id": str(service_session_id),
                            "after_attempt": after_attempt,
                            "after_index": after_index,
                            "limit": bounded_limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
        result: list[AgentProgressEvent] = []
        for row in rows:
            attempt = int(row["attempt"])
            if row["event_type"] == "progress.frame":
                frame = _progress_frame_from_payload(row["payload"])
                if frame.attempt_session_id != row["session_id"] or frame.attempt != attempt:
                    raise ValueError("persisted progress frame has a mismatched attempt identity")
            else:
                payload = row["payload"] if isinstance(row["payload"], dict) else {}
                frame = project_agent_session_lifecycle_frame(
                    attempt_session_id=row["session_id"],
                    attempt=attempt,
                    event_id=row["event_id"],
                    event_index=row["event_index"],
                    event_type=row["event_type"],
                    payload=payload,
                    occurred_at=row["occurred_at"],
                )
            event_cursor = AgentSessionEventCursor(
                serviceSessionId=service_session_id,
                attemptSessionId=row["session_id"],
                attempt=attempt,
                eventIndex=row["event_index"],
            ).encode()
            result.append(
                AgentProgressEvent(
                    serviceSessionId=service_session_id,
                    eventId=row["event_id"],
                    eventIndex=row["event_index"],
                    cursor=event_cursor,
                    acceptedAt=row["occurred_at"],
                    frame=frame,
                )
            )
        return tuple(result)

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

    async def get_execution_by_service_session_id(
        self,
        tenant_id: str,
        service_session_id: UUID,
    ) -> UUID:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            execution_id = await connection.scalar(
                text(
                    """
                    SELECT id
                    FROM executions
                    WHERE tenant_id = :tenant_id
                      AND trigger_context->>'ameshAgentSessionId' = :service_session_id
                    ORDER BY
                      CASE
                        WHEN trigger_context->>'ameshAgentSessionTurn' ~ '^[1-9][0-9]*$'
                        THEN (trigger_context->>'ameshAgentSessionTurn')::integer
                        ELSE 1
                      END DESC,
                      created_at DESC,
                      id DESC
                    LIMIT 1
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "service_session_id": str(service_session_id),
                },
            )
        if execution_id is None:
            raise LookupError("agent service session does not exist")
        return UUID(str(execution_id))

    async def list_service_sessions(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
        owner_id: str | None = None,
    ) -> tuple[tuple[UUID, UUID, str | None, AgentSessionRecord | None], ...]:
        bounded_limit = max(1, min(limit, 100))
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            WITH latest_executions AS (
                                SELECT DISTINCT ON (
                                           executions.trigger_context
                                               ->>'ameshAgentSessionId'
                                       )
                                       executions.*
                                FROM executions
                                WHERE executions.tenant_id = :tenant_id
                                  AND executions.trigger_context ? 'ameshAgentSessionId'
                                  AND (
                                      CAST(:owner_id AS text) IS NULL
                                      OR executions.trigger_context->>'ameshActorId'
                                          = CAST(:owner_id AS text)
                                  )
                                ORDER BY
                                  executions.trigger_context->>'ameshAgentSessionId',
                                  CASE
                                    WHEN executions.trigger_context
                                             ->>'ameshAgentSessionTurn'
                                             ~ '^[1-9][0-9]*$'
                                    THEN (
                                        executions.trigger_context
                                            ->>'ameshAgentSessionTurn'
                                    )::integer
                                    ELSE 1
                                  END DESC,
                                  executions.created_at DESC,
                                  executions.id DESC
                            )
                            SELECT latest_executions.id AS service_execution_id,
                                   latest_executions.trigger_context->>'ameshAgentSessionId'
                                       AS service_session_id,
                                   latest_executions.trigger_context->>'ameshAgentRef'
                                       AS agent_ref,
                                   latest_session.*
                            FROM latest_executions
                            LEFT JOIN LATERAL (
                                SELECT agent_sessions.*
                                FROM agent_sessions
                                WHERE agent_sessions.tenant_id = latest_executions.tenant_id
                                  AND agent_sessions.execution_id = latest_executions.id
                                ORDER BY agent_sessions.attempt DESC,
                                         agent_sessions.updated_at DESC,
                                         agent_sessions.session_id DESC
                                LIMIT 1
                            ) AS latest_session ON TRUE
                            ORDER BY latest_executions.created_at DESC,
                                     latest_executions.id DESC
                            LIMIT :limit
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "owner_id": owner_id,
                            "limit": bounded_limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return tuple(
            (
                UUID(str(row["service_session_id"])),
                UUID(str(row["service_execution_id"])),
                row.get("agent_ref"),
                _session_record(row, tenant_id) if row.get("session_id") is not None else None,
            )
            for row in rows
        )


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
        harness=(
            AgentHarnessPin(
                adapter=row["harness_adapter"],
                adapterVersion=row["harness_version"],
                protocol=row["harness_protocol"],
            )
            if row.get("harness_adapter") is not None
            else None
        ),
        finalResult=row["final_result"],
        error=row["error"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
        completedAt=row["completed_at"],
    )


class PostgresAgentProgressSink:
    """PostgreSQL implementation of the provider-neutral progress port."""

    def __init__(
        self,
        repository: PostgresAgentSessionRepository,
        *,
        limits: AgentProgressLimits | None = None,
    ) -> None:
        self._repository = repository
        self._limits = limits

    async def append(
        self,
        context: AgentProgressContext,
        frame: AgentProgressFrame,
    ) -> AgentProgressReceipt:
        return await self._repository.append_progress(
            context,
            frame,
            limits=self._limits,
        )

    async def close_active_segment(
        self,
        context: AgentProgressContext,
        *,
        occurred_at: datetime,
    ) -> None:
        del context, occurred_at


def _progress_payload(frame: AgentProgressFrame) -> dict[str, object]:
    return {
        "schemaVersion": "amesh.agent-progress/v1",
        "frame": frame.model_dump(mode="json", by_alias=True),
    }


def _logical_service_session_id(session: RowMapping) -> UUID:
    trigger = session.get("trigger_context")
    raw = trigger.get("ameshAgentSessionId") if isinstance(trigger, dict) else None
    if isinstance(raw, str):
        try:
            return UUID(raw)
        except ValueError:
            pass
    return UUID(str(session["session_id"]))


def _progress_frame_from_payload(payload: object) -> AgentProgressFrame:
    if not isinstance(payload, dict) or set(payload) != {"schemaVersion", "frame"}:
        raise ValueError("persisted progress payload is not a governed progress frame")
    if payload["schemaVersion"] != "amesh.agent-progress/v1":
        raise ValueError("unsupported persisted progress schema")
    frame = payload["frame"]
    if not isinstance(frame, dict):
        raise ValueError("persisted progress frame is not an object")
    return AgentProgressFrame.model_validate(frame)


def _require_same_progress_frame(
    existing: RowMapping,
    frame: AgentProgressFrame,
    event_type: str,
) -> None:
    if existing["event_type"] != event_type:
        raise ValueError("agent session event key was reused with different evidence")
    persisted = _progress_frame_from_payload(existing["payload"])
    if persisted.fingerprint != frame.fingerprint:
        raise ValueError("progress source sequence was reused with different content")


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
