from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.ports.trigger_runtime import (
    TriggerOccurrence,
    TriggerOccurrenceAcceptance,
    TriggerOccurrenceState,
    TriggerRuntimeRepository,
    TriggerRuntimeState,
)

from .tenant_context import tenant_transaction


async def synchronize_flow_trigger_runtime(
    connection: AsyncConnection,
    tenant_id: UUID,
    flow_id: UUID,
    *,
    active_revision: int,
    flow_disabled: bool,
) -> None:
    """Activate only the current immutable trigger revision in the flow transaction."""

    await connection.execute(
        text(
            """
            UPDATE trigger_runtime_states AS runtime
            SET active = false,
                last_decision = 'superseded by flow revision activation',
                updated_at = clock_timestamp()
            FROM trigger_definitions AS triggers
            JOIN flow_revisions AS revisions ON revisions.id = triggers.flow_revision_id
            WHERE runtime.trigger_definition_id = triggers.id
              AND runtime.tenant_id = :tenant_id
              AND revisions.flow_id = :flow_id
              AND runtime.active
            """
        ),
        {"tenant_id": tenant_id, "flow_id": flow_id},
    )
    await connection.execute(
        text(
            """
            INSERT INTO trigger_runtime_states (
                trigger_definition_id, tenant_id, namespace_name, flow_key,
                flow_revision, trigger_key, trigger_type, active, paused,
                last_decision
            )
            SELECT
                triggers.id,
                triggers.tenant_id,
                namespaces.name,
                flows.flow_key,
                revisions.revision,
                triggers.trigger_key,
                triggers.trigger_type,
                triggers.enabled AND NOT :flow_disabled,
                COALESCE((triggers.definition ->> 'paused')::boolean, false),
                CASE
                    WHEN triggers.enabled AND NOT :flow_disabled
                        THEN 'trigger revision activated'
                    ELSE 'trigger revision disabled by definition or flow'
                END
            FROM trigger_definitions AS triggers
            JOIN flow_revisions AS revisions ON revisions.id = triggers.flow_revision_id
            JOIN flows ON flows.id = revisions.flow_id
            JOIN namespaces ON namespaces.id = flows.namespace_id
            WHERE triggers.tenant_id = :tenant_id
              AND revisions.flow_id = :flow_id
              AND revisions.revision = :active_revision
            ON CONFLICT (trigger_definition_id) DO UPDATE SET
                active = EXCLUDED.active,
                paused = EXCLUDED.paused,
                last_decision = EXCLUDED.last_decision,
                updated_at = clock_timestamp()
            """
        ),
        {
            "tenant_id": tenant_id,
            "flow_id": flow_id,
            "active_revision": active_revision,
            "flow_disabled": flow_disabled,
        },
    )


async def emit_flow_completion_occurrences(
    connection: AsyncConnection,
    tenant_id: UUID,
    *,
    source_execution_id: UUID,
    source_namespace: str,
    source_flow_id: str,
    source_flow_revision: int,
    terminal_state: str,
    source_trigger: dict[str, Any],
) -> int:
    """Transactionally route one terminal execution to active core.flow triggers."""

    source_depth = int(source_trigger.get("depth", 0))
    rows = (
        (
            await connection.execute(
                text(
                    """
                    WITH candidates AS (
                        SELECT
                            runtime.*,
                            triggers.definition,
                            COALESCE(pending.count, 0) AS pending_count,
                            COALESCE((triggers.definition ->> 'maxPending')::integer, 1000)
                                AS max_pending,
                            COALESCE((triggers.definition ->> 'maxAttempts')::integer, 3)
                                AS max_attempts,
                            COALESCE((triggers.definition ->> 'maxDepth')::integer, 16)
                                AS max_depth,
                            COALESCE(
                                (triggers.definition ->> 'retryDelay')::interval,
                                interval '30 seconds'
                            ) AS retry_delay
                        FROM trigger_runtime_states AS runtime
                        JOIN trigger_definitions AS triggers
                          ON triggers.id = runtime.trigger_definition_id
                        LEFT JOIN LATERAL (
                            SELECT count(*)
                            FROM trigger_occurrences AS occurrences
                            WHERE occurrences.tenant_id = runtime.tenant_id
                              AND occurrences.trigger_definition_id = runtime.trigger_definition_id
                              AND occurrences.state IN (
                                  'ACCEPTED', 'DEFERRED', 'PROCESSING', 'RETRY_WAIT'
                              )
                        ) AS pending ON true
                        WHERE runtime.tenant_id = :tenant_id
                          AND runtime.active
                          AND runtime.trigger_type = 'core.flow'
                          AND COALESCE(
                              NULLIF(triggers.definition ->> 'namespace', ''),
                              runtime.namespace_name
                          ) = :source_namespace
                          AND triggers.definition ->> 'flowId' = :source_flow_id
                          AND EXISTS (
                              SELECT 1
                              FROM jsonb_array_elements_text(
                                  COALESCE(triggers.definition -> 'states', '["SUCCESS"]'::jsonb)
                              ) AS accepted_state
                              WHERE accepted_state = :terminal_state
                          )
                    ), inserted AS (
                        INSERT INTO trigger_occurrences (
                            occurrence_id, tenant_id, trigger_definition_id,
                            namespace_name, flow_key, flow_revision, trigger_key,
                            trigger_type, occurrence_key, state, max_attempts,
                            available_at, payload, metadata, evidence, completed_at
                        )
                        SELECT
                            gen_random_uuid(),
                            candidates.tenant_id,
                            candidates.trigger_definition_id,
                            candidates.namespace_name,
                            candidates.flow_key,
                            candidates.flow_revision,
                            candidates.trigger_key,
                            candidates.trigger_type,
                            'flow-completion:' || :source_execution_id || ':' || :terminal_state,
                            CASE
                                WHEN :source_depth + 1 > candidates.max_depth
                                    THEN 'DEAD_LETTERED'
                                WHEN candidates.paused
                                  OR candidates.pending_count >= candidates.max_pending
                                    THEN 'DEFERRED'
                                ELSE 'ACCEPTED'
                            END,
                            candidates.max_attempts,
                            CASE
                                WHEN candidates.paused
                                  OR candidates.pending_count >= candidates.max_pending
                                    THEN clock_timestamp() + candidates.retry_delay
                                ELSE clock_timestamp()
                            END,
                            jsonb_build_object(
                                'sourceExecutionId', :source_execution_id,
                                'sourceNamespace', :source_namespace,
                                'sourceFlowId', :source_flow_id,
                                'sourceFlowRevision', CAST(:source_flow_revision AS integer),
                                'state', :terminal_state
                            ),
                            jsonb_build_object(
                                'source', 'flow-completion',
                                'observedAt', clock_timestamp(),
                                'depth', :source_depth + 1
                            ),
                            CASE
                                WHEN :source_depth + 1 > candidates.max_depth
                                    THEN jsonb_build_object(
                                        'decision', 'dead-lettered',
                                        'reason', 'flow trigger depth exceeded',
                                        'maxDepth', candidates.max_depth
                                    )
                                WHEN candidates.paused
                                    THEN jsonb_build_object(
                                        'decision', 'deferred',
                                        'reason', 'trigger is paused'
                                    )
                                WHEN candidates.pending_count >= candidates.max_pending
                                    THEN jsonb_build_object(
                                        'decision', 'deferred',
                                        'reason', 'trigger backpressure limit reached',
                                        'pendingCount', candidates.pending_count,
                                        'maxPending', candidates.max_pending
                                    )
                                ELSE jsonb_build_object(
                                    'decision', 'accepted',
                                    'reason', 'flow completion matched active trigger'
                                )
                            END,
                            CASE
                                WHEN :source_depth + 1 > candidates.max_depth
                                    THEN clock_timestamp()
                                ELSE NULL
                            END
                        FROM candidates
                        ON CONFLICT (tenant_id, trigger_definition_id, occurrence_key) DO NOTHING
                        RETURNING *
                    ), events AS (
                        INSERT INTO trigger_occurrence_events (
                            tenant_id, event_id, occurrence_id, event_type,
                            reason, actor_id, payload
                        )
                        SELECT
                            inserted.tenant_id,
                            gen_random_uuid(),
                            inserted.occurrence_id,
                            CASE
                                WHEN inserted.state = 'DEAD_LETTERED' THEN 'DEAD_LETTERED'
                                WHEN inserted.state = 'DEFERRED' THEN 'DEFERRED'
                                ELSE 'ACCEPTED'
                            END,
                            inserted.evidence ->> 'reason',
                            'system:trigger-router',
                            inserted.evidence
                        FROM inserted
                        RETURNING occurrence_id
                    )
                    SELECT occurrence_id FROM events
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "source_execution_id": str(source_execution_id),
                    "source_namespace": source_namespace,
                    "source_flow_id": source_flow_id,
                    "source_flow_revision": source_flow_revision,
                    "terminal_state": terminal_state,
                    "source_depth": source_depth,
                },
            )
        )
        .mappings()
        .all()
    )
    return len(rows)


class PostgresTriggerRuntimeRepository(TriggerRuntimeRepository):
    """PostgreSQL occurrence state machine, retry queue and trigger health projection."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def accept_occurrence(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        flow_revision: int,
        trigger_id: str,
        occurrence_key: str,
        payload: dict[str, Any],
        metadata: dict[str, Any],
        max_pending: int,
        max_attempts: int,
        retry_delay: timedelta,
    ) -> TriggerOccurrenceAcceptance:
        if not occurrence_key or len(occurrence_key) > 1024:
            raise ValueError("trigger occurrence key must contain 1 to 1024 characters")
        if max_pending < 1 or max_attempts < 1:
            raise ValueError("trigger occurrence limits must be positive")
        retry_seconds = retry_delay.total_seconds()
        if retry_seconds <= 0:
            raise ValueError("trigger retry delay must be positive")
        occurrence_id = new_runtime_id()
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            runtime = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT runtime.*
                            FROM trigger_runtime_states AS runtime
                            WHERE runtime.tenant_id = :tenant_id
                              AND runtime.namespace_name = :namespace
                              AND runtime.flow_key = :flow_key
                              AND runtime.flow_revision = :flow_revision
                              AND runtime.trigger_key = :trigger_key
                            FOR UPDATE
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "flow_key": flow_id,
                            "flow_revision": flow_revision,
                            "trigger_key": trigger_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if runtime is None or not runtime["active"]:
                raise LookupError(
                    f"active trigger {namespace}.{flow_id}@{flow_revision}/{trigger_id} does not exist"
                )
            pending_count = int(
                await connection.scalar(
                    text(
                        """
                        SELECT count(*)
                        FROM trigger_occurrences
                        WHERE tenant_id = :tenant_id
                          AND trigger_definition_id = :trigger_definition_id
                          AND state IN ('ACCEPTED', 'DEFERRED', 'PROCESSING', 'RETRY_WAIT')
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "trigger_definition_id": runtime["trigger_definition_id"],
                    },
                )
                or 0
            )
            if runtime["paused"]:
                initial_state = TriggerOccurrenceState.DEFERRED
                reason = "trigger is paused"
            elif pending_count >= max_pending:
                initial_state = TriggerOccurrenceState.DEFERRED
                reason = "trigger backpressure limit reached"
            else:
                initial_state = TriggerOccurrenceState.ACCEPTED
                reason = "occurrence accepted"
            evidence = {
                "decision": initial_state.value.lower(),
                "reason": reason,
                "pendingCount": pending_count,
                "maxPending": max_pending,
            }
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO trigger_occurrences (
                                occurrence_id, tenant_id, trigger_definition_id,
                                namespace_name, flow_key, flow_revision, trigger_key,
                                trigger_type, occurrence_key, state, max_attempts,
                                available_at, payload, metadata, evidence
                            ) VALUES (
                                :occurrence_id, :tenant_id, :trigger_definition_id,
                                :namespace, :flow_key, :flow_revision, :trigger_key,
                                :trigger_type, :occurrence_key, :state, :max_attempts,
                                CASE
                                    WHEN :state = 'DEFERRED'
                                        THEN clock_timestamp() + make_interval(secs => :retry_seconds)
                                    ELSE clock_timestamp()
                                END,
                                CAST(:payload AS jsonb), CAST(:metadata AS jsonb),
                                CAST(:evidence AS jsonb)
                            )
                            ON CONFLICT (tenant_id, trigger_definition_id, occurrence_key)
                                DO NOTHING
                            RETURNING *
                            """
                        ),
                        {
                            "occurrence_id": occurrence_id,
                            "tenant_id": tenant_uuid,
                            "trigger_definition_id": runtime["trigger_definition_id"],
                            "namespace": namespace,
                            "flow_key": flow_id,
                            "flow_revision": flow_revision,
                            "trigger_key": trigger_id,
                            "trigger_type": runtime["trigger_type"],
                            "occurrence_key": occurrence_key,
                            "state": initial_state.value,
                            "max_attempts": max_attempts,
                            "retry_seconds": retry_seconds,
                            "payload": json.dumps(payload),
                            "metadata": json.dumps(metadata),
                            "evidence": json.dumps(evidence),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            duplicate = row is None
            if row is None:
                row = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT * FROM trigger_occurrences
                                WHERE tenant_id = :tenant_id
                                  AND trigger_definition_id = :trigger_definition_id
                                  AND occurrence_key = :occurrence_key
                                """
                            ),
                            {
                                "tenant_id": tenant_uuid,
                                "trigger_definition_id": runtime["trigger_definition_id"],
                                "occurrence_key": occurrence_key,
                            },
                        )
                    )
                    .mappings()
                    .one()
                )
                reason = f"duplicate occurrence already {str(row['state']).lower()}"
            else:
                await _insert_occurrence_event(
                    connection,
                    tenant_uuid,
                    row["occurrence_id"],
                    "DEFERRED" if initial_state is TriggerOccurrenceState.DEFERRED else "ACCEPTED",
                    reason,
                    actor_id="system:trigger-runtime",
                    payload=evidence,
                )
                await connection.execute(
                    text(
                        """
                        UPDATE trigger_runtime_states
                        SET last_occurrence_at = clock_timestamp(),
                            last_decision = :decision,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id
                          AND trigger_definition_id = :trigger_definition_id
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "trigger_definition_id": runtime["trigger_definition_id"],
                        "decision": reason,
                    },
                )
        occurrence = _to_occurrence(row, tenant_id=tenant_id)
        return TriggerOccurrenceAcceptance(
            occurrence=occurrence,
            duplicate=duplicate,
            accepted=occurrence.state is TriggerOccurrenceState.ACCEPTED,
            reason=reason,
        )

    async def claim_occurrence(
        self,
        occurrence_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        lease_duration: timedelta,
    ) -> TriggerOccurrence:
        rows = await self._claim(
            tenant_id=tenant_id,
            owner_id=owner_id,
            lease_duration=lease_duration,
            limit=1,
            occurrence_id=occurrence_id,
        )
        if not rows:
            raise RuntimeError(f"trigger occurrence {occurrence_id} is not claimable")
        return rows[0]

    async def claim_due_occurrences(
        self,
        *,
        tenant_id: str,
        owner_id: UUID,
        lease_duration: timedelta,
        limit: int = 100,
    ) -> list[TriggerOccurrence]:
        if limit < 1 or limit > 1000:
            raise ValueError("trigger claim limit must be between 1 and 1000")
        return await self._claim(
            tenant_id=tenant_id,
            owner_id=owner_id,
            lease_duration=lease_duration,
            limit=limit,
        )

    async def _claim(
        self,
        *,
        tenant_id: str,
        owner_id: UUID,
        lease_duration: timedelta,
        limit: int,
        occurrence_id: UUID | None = None,
    ) -> list[TriggerOccurrence]:
        lease_seconds = lease_duration.total_seconds()
        if lease_seconds <= 0:
            raise ValueError("trigger occurrence lease must be positive")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await connection.execute(
                text(
                    """
                    UPDATE trigger_occurrences
                    SET state = CASE
                            WHEN attempt >= max_attempts THEN 'DEAD_LETTERED'
                            ELSE 'RETRY_WAIT'
                        END,
                        owner_id = NULL,
                        lease_expires_at = NULL,
                        available_at = clock_timestamp(),
                        completed_at = CASE
                            WHEN attempt >= max_attempts THEN clock_timestamp()
                            ELSE NULL
                        END,
                        evidence = evidence || jsonb_build_object(
                            'decision', CASE
                                WHEN attempt >= max_attempts THEN 'dead-lettered'
                                ELSE 'retry'
                            END,
                            'reason', 'processing lease expired'
                        ),
                        updated_at = clock_timestamp()
                    WHERE tenant_id = :tenant_id
                      AND state = 'PROCESSING'
                      AND lease_expires_at <= clock_timestamp()
                    """
                ),
                {"tenant_id": tenant_uuid},
            )
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            WITH candidates AS (
                                SELECT occurrences.occurrence_id
                                FROM trigger_occurrences AS occurrences
                                JOIN trigger_runtime_states AS runtime
                                  ON runtime.trigger_definition_id = occurrences.trigger_definition_id
                                 AND runtime.tenant_id = occurrences.tenant_id
                                WHERE occurrences.tenant_id = :tenant_id
                                  AND runtime.active
                                  AND NOT runtime.paused
                                  AND occurrences.state IN ('ACCEPTED', 'DEFERRED', 'RETRY_WAIT')
                                  AND occurrences.available_at <= clock_timestamp()
                                  AND (
                                      CAST(:occurrence_id AS uuid) IS NULL
                                      OR occurrences.occurrence_id = :occurrence_id
                                  )
                                ORDER BY occurrences.available_at, occurrences.created_at,
                                         occurrences.occurrence_id
                                FOR UPDATE OF occurrences SKIP LOCKED
                                LIMIT :limit
                            )
                            UPDATE trigger_occurrences AS occurrences
                            SET state = 'PROCESSING',
                                attempt = attempt + 1,
                                owner_id = :owner_id,
                                fencing_token = fencing_token + 1,
                                lease_expires_at = clock_timestamp()
                                    + make_interval(secs => :lease_seconds),
                                evidence = evidence || jsonb_build_object(
                                    'decision', 'processing',
                                    'reason', 'occurrence claimed by trigger worker'
                                ),
                                updated_at = clock_timestamp()
                            FROM candidates
                            WHERE occurrences.tenant_id = :tenant_id
                              AND occurrences.occurrence_id = candidates.occurrence_id
                            RETURNING occurrences.*
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "occurrence_id": occurrence_id,
                            "limit": limit,
                            "owner_id": owner_id,
                            "lease_seconds": lease_seconds,
                        },
                    )
                )
                .mappings()
                .all()
            )
            for row in rows:
                await _insert_occurrence_event(
                    connection,
                    tenant_uuid,
                    row["occurrence_id"],
                    "CLAIMED",
                    "occurrence claimed by trigger worker",
                    actor_id=f"system:trigger-worker:{owner_id}",
                    payload={"attempt": row["attempt"], "fencingToken": row["fencing_token"]},
                )
        return [_to_occurrence(row, tenant_id=tenant_id) for row in rows]

    async def complete_occurrence(
        self,
        occurrence_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        fencing_token: int,
        execution_id: UUID,
        evidence: dict[str, Any],
    ) -> TriggerOccurrence:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE trigger_occurrences
                            SET state = 'SUCCEEDED',
                                execution_id = :execution_id,
                                evidence = evidence || CAST(:evidence AS jsonb),
                                owner_id = NULL,
                                lease_expires_at = NULL,
                                completed_at = clock_timestamp(),
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id
                              AND occurrence_id = :occurrence_id
                              AND state = 'PROCESSING'
                              AND owner_id = :owner_id
                              AND fencing_token = :fencing_token
                              AND lease_expires_at > clock_timestamp()
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "occurrence_id": occurrence_id,
                            "owner_id": owner_id,
                            "fencing_token": fencing_token,
                            "execution_id": execution_id,
                            "evidence": json.dumps(evidence),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise RuntimeError(f"trigger occurrence {occurrence_id} ownership is stale")
            await connection.execute(
                text(
                    """
                    UPDATE trigger_runtime_states
                    SET last_success_at = clock_timestamp(),
                        consecutive_failures = 0,
                        last_error = NULL,
                        last_decision = 'occurrence launched execution',
                        updated_at = clock_timestamp()
                    WHERE tenant_id = :tenant_id
                      AND trigger_definition_id = :trigger_definition_id
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "trigger_definition_id": row["trigger_definition_id"],
                },
            )
            await _insert_occurrence_event(
                connection,
                tenant_uuid,
                occurrence_id,
                "SUCCEEDED",
                "occurrence launched execution",
                actor_id=f"system:trigger-worker:{owner_id}",
                payload={"executionId": str(execution_id), **evidence},
            )
        return _to_occurrence(row, tenant_id=tenant_id)

    async def fail_occurrence(
        self,
        occurrence_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        fencing_token: int,
        error: str,
        retry_delay: timedelta,
    ) -> TriggerOccurrence:
        retry_seconds = retry_delay.total_seconds()
        if retry_seconds <= 0:
            raise ValueError("trigger retry delay must be positive")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE trigger_occurrences
                            SET state = CASE
                                    WHEN attempt >= max_attempts
                                        THEN 'DEAD_LETTERED'
                                    ELSE 'RETRY_WAIT'
                                END,
                                available_at = clock_timestamp()
                                    + make_interval(secs => :retry_seconds),
                                evidence = evidence || jsonb_build_object(
                                    'decision', CASE
                                        WHEN attempt >= max_attempts
                                            THEN 'dead-lettered'
                                        ELSE 'retry'
                                    END,
                                    'reason', CAST(:error AS text)
                                ),
                                owner_id = NULL,
                                lease_expires_at = NULL,
                                completed_at = CASE
                                    WHEN attempt >= max_attempts THEN clock_timestamp()
                                    ELSE NULL
                                END,
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id
                              AND occurrence_id = :occurrence_id
                              AND state = 'PROCESSING'
                              AND owner_id = :owner_id
                              AND fencing_token = :fencing_token
                              AND lease_expires_at > clock_timestamp()
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "occurrence_id": occurrence_id,
                            "owner_id": owner_id,
                            "fencing_token": fencing_token,
                            "retry_seconds": retry_seconds,
                            "error": error[:4096],
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise RuntimeError(f"trigger occurrence {occurrence_id} ownership is stale")
            event_type = (
                "DEAD_LETTERED"
                if row["state"] == TriggerOccurrenceState.DEAD_LETTERED.value
                else "RETRY_SCHEDULED"
            )
            await connection.execute(
                text(
                    """
                    UPDATE trigger_runtime_states
                    SET consecutive_failures = consecutive_failures + 1,
                        last_error = :error,
                        last_decision = :decision,
                        updated_at = clock_timestamp()
                    WHERE tenant_id = :tenant_id
                      AND trigger_definition_id = :trigger_definition_id
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "trigger_definition_id": row["trigger_definition_id"],
                    "error": error[:4096],
                    "decision": event_type.lower().replace("_", " "),
                },
            )
            await _insert_occurrence_event(
                connection,
                tenant_uuid,
                occurrence_id,
                event_type,
                error[:4096],
                actor_id=f"system:trigger-worker:{owner_id}",
                payload={"attempt": row["attempt"], "maxAttempts": row["max_attempts"]},
            )
        return _to_occurrence(row, tenant_id=tenant_id)

    async def get_occurrence(
        self,
        occurrence_id: UUID,
        *,
        tenant_id: str,
    ) -> TriggerOccurrence:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM trigger_occurrences "
                            "WHERE tenant_id = :tenant_id AND occurrence_id = :occurrence_id"
                        ),
                        {"tenant_id": tenant_uuid, "occurrence_id": occurrence_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError(f"trigger occurrence {occurrence_id} does not exist")
        return _to_occurrence(row, tenant_id=tenant_id)

    async def list_occurrences(
        self,
        *,
        tenant_id: str,
        namespace: str | None = None,
        flow_id: str | None = None,
        trigger_id: str | None = None,
        state: TriggerOccurrenceState | None = None,
        limit: int = 100,
    ) -> list[TriggerOccurrence]:
        if limit < 1 or limit > 1000:
            raise ValueError("trigger occurrence list limit must be between 1 and 1000")
        clauses = ["tenant_id = :tenant_id"]
        parameters: dict[str, object] = {"limit": limit}
        for column, key, value in (
            ("namespace_name", "namespace", namespace),
            ("flow_key", "flow_id", flow_id),
            ("trigger_key", "trigger_id", trigger_id),
        ):
            if value is not None:
                clauses.append(f"{column} = :{key}")
                parameters[key] = value
        if state is not None:
            clauses.append("state = :state")
            parameters["state"] = state.value
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            parameters["tenant_id"] = tenant_uuid
            rows = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM trigger_occurrences WHERE "
                            + " AND ".join(clauses)
                            + " ORDER BY created_at DESC, occurrence_id DESC LIMIT :limit"
                        ),
                        parameters,
                    )
                )
                .mappings()
                .all()
            )
        return [_to_occurrence(row, tenant_id=tenant_id) for row in rows]

    async def replay_occurrence(
        self,
        occurrence_id: UUID,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str,
    ) -> TriggerOccurrence:
        replay_id = new_runtime_id()
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO trigger_occurrences (
                                occurrence_id, tenant_id, trigger_definition_id,
                                namespace_name, flow_key, flow_revision, trigger_key,
                                trigger_type, occurrence_key, state, max_attempts,
                                available_at, payload, metadata, evidence, replay_of
                            )
                            SELECT
                                CAST(:replay_id AS uuid), source.tenant_id,
                                source.trigger_definition_id,
                                source.namespace_name, source.flow_key, source.flow_revision,
                                source.trigger_key, source.trigger_type,
                                'replay:' || source.occurrence_id || ':'
                                    || CAST(CAST(:replay_id AS uuid) AS text),
                                CASE WHEN runtime.active AND NOT runtime.paused
                                    THEN 'ACCEPTED' ELSE 'DEFERRED' END,
                                source.max_attempts, clock_timestamp(), source.payload,
                                source.metadata || jsonb_build_object(
                                    'replayOf', source.occurrence_id,
                                    'replayReason', CAST(:reason AS text)
                                ),
                                jsonb_build_object(
                                    'decision', 'replayed',
                                    'reason', CAST(:reason AS text),
                                    'actorId', CAST(:actor_id AS text)
                                ),
                                source.occurrence_id
                            FROM trigger_occurrences AS source
                            JOIN trigger_runtime_states AS runtime
                              ON runtime.trigger_definition_id = source.trigger_definition_id
                             AND runtime.tenant_id = source.tenant_id
                            WHERE source.tenant_id = :tenant_id
                              AND source.occurrence_id = :occurrence_id
                              AND source.state IN ('SUCCEEDED', 'DEAD_LETTERED')
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "occurrence_id": occurrence_id,
                            "replay_id": replay_id,
                            "actor_id": actor_id,
                            "reason": reason,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise ValueError("only succeeded or dead-lettered occurrences can be replayed")
            await _insert_occurrence_event(
                connection,
                tenant_uuid,
                replay_id,
                "REPLAYED",
                reason,
                actor_id=actor_id,
                payload={"replayOf": str(occurrence_id)},
            )
            await _insert_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="trigger.occurrence.replay",
                resource_id=str(replay_id),
                reason=reason,
                evidence={"replayOf": str(occurrence_id)},
            )
        return _to_occurrence(row, tenant_id=tenant_id)

    async def list_runtime_states(
        self,
        *,
        tenant_id: str,
        namespace: str | None = None,
        flow_id: str | None = None,
        trigger_id: str | None = None,
        active: bool | None = None,
        limit: int = 100,
    ) -> list[TriggerRuntimeState]:
        if limit < 1 or limit > 1000:
            raise ValueError("trigger state list limit must be between 1 and 1000")
        clauses = ["runtime.tenant_id = :tenant_id"]
        parameters: dict[str, object] = {"limit": limit}
        for column, key, value in (
            ("runtime.namespace_name", "namespace", namespace),
            ("runtime.flow_key", "flow_id", flow_id),
            ("runtime.trigger_key", "trigger_id", trigger_id),
        ):
            if value is not None:
                clauses.append(f"{column} = :{key}")
                parameters[key] = value
        if active is not None:
            clauses.append("runtime.active = :active")
            parameters["active"] = active
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            parameters["tenant_id"] = tenant_uuid
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT runtime.*,
                                count(occurrences.occurrence_id) FILTER (
                                    WHERE occurrences.state IN (
                                        'ACCEPTED', 'DEFERRED', 'PROCESSING', 'RETRY_WAIT'
                                    )
                                ) AS pending_count,
                                count(occurrences.occurrence_id) FILTER (
                                    WHERE occurrences.state = 'DEAD_LETTERED'
                                ) AS dead_letter_count
                            FROM trigger_runtime_states AS runtime
                            LEFT JOIN trigger_occurrences AS occurrences
                              ON occurrences.tenant_id = runtime.tenant_id
                             AND occurrences.trigger_definition_id = runtime.trigger_definition_id
                            WHERE """
                            + " AND ".join(clauses)
                            + """
                            GROUP BY runtime.trigger_definition_id
                            ORDER BY runtime.active DESC, runtime.namespace_name,
                                     runtime.flow_key, runtime.trigger_key, runtime.flow_revision DESC
                            LIMIT :limit
                            """
                        ),
                        parameters,
                    )
                )
                .mappings()
                .all()
            )
        return [_to_runtime_state(row, tenant_id=tenant_id) for row in rows]

    async def set_paused(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        trigger_id: str,
        paused: bool,
        actor_id: str,
        reason: str,
    ) -> TriggerRuntimeState:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE trigger_runtime_states
                            SET paused = :paused,
                                last_decision = :reason,
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND flow_key = :flow_key
                              AND trigger_key = :trigger_key
                              AND active
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "flow_key": flow_id,
                            "trigger_key": trigger_id,
                            "paused": paused,
                            "reason": reason,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError(
                    f"active trigger {namespace}.{flow_id}/{trigger_id} does not exist"
                )
            if not paused:
                await connection.execute(
                    text(
                        """
                        UPDATE trigger_occurrences
                        SET state = 'ACCEPTED',
                            available_at = clock_timestamp(),
                            evidence = evidence || jsonb_build_object(
                                'decision', 'accepted',
                                'reason', 'trigger resumed'
                            ),
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id
                          AND trigger_definition_id = :trigger_definition_id
                          AND state = 'DEFERRED'
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "trigger_definition_id": row["trigger_definition_id"],
                    },
                )
            await _insert_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="trigger.pause" if paused else "trigger.resume",
                resource_id=f"{namespace}.{flow_id}/{trigger_id}",
                reason=reason,
                evidence={"paused": paused},
            )
        return _to_runtime_state(
            {**dict(row), "pending_count": 0, "dead_letter_count": 0},
            tenant_id=tenant_id,
        )

    async def update_checkpoint(
        self,
        *,
        tenant_id: str,
        trigger_definition_id: UUID,
        checkpoint: dict[str, Any],
        cursor: str | None,
        evaluated_at: datetime,
        next_evaluation_at: datetime | None,
        decision: str,
    ) -> TriggerRuntimeState:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE trigger_runtime_states
                            SET checkpoint = CAST(:checkpoint AS jsonb),
                                cursor = :cursor,
                                last_evaluated_at = :evaluated_at,
                                next_evaluation_at = :next_evaluation_at,
                                lag_seconds = greatest(
                                    extract(epoch FROM (clock_timestamp() - :evaluated_at)), 0
                                ),
                                last_decision = :decision,
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id
                              AND trigger_definition_id = :trigger_definition_id
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "trigger_definition_id": trigger_definition_id,
                            "checkpoint": json.dumps(checkpoint),
                            "cursor": cursor,
                            "evaluated_at": evaluated_at,
                            "next_evaluation_at": next_evaluation_at,
                            "decision": decision,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError(f"trigger runtime {trigger_definition_id} does not exist")
        return _to_runtime_state(
            {**dict(row), "pending_count": 0, "dead_letter_count": 0},
            tenant_id=tenant_id,
        )


async def _insert_occurrence_event(
    connection: AsyncConnection,
    tenant_id: UUID,
    occurrence_id: UUID,
    event_type: str,
    reason: str,
    *,
    actor_id: str,
    payload: dict[str, Any],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO trigger_occurrence_events (
                tenant_id, event_id, occurrence_id, event_type,
                reason, actor_id, payload
            ) VALUES (
                :tenant_id, :event_id, :occurrence_id, :event_type,
                :reason, :actor_id, CAST(:payload AS jsonb)
            )
            """
        ),
        {
            "tenant_id": tenant_id,
            "event_id": new_runtime_id(),
            "occurrence_id": occurrence_id,
            "event_type": event_type,
            "reason": reason,
            "actor_id": actor_id,
            "payload": json.dumps(payload),
        },
    )


async def _insert_audit(
    connection: AsyncConnection,
    tenant_id: UUID,
    *,
    actor_id: str,
    action: str,
    resource_id: str,
    reason: str,
    evidence: dict[str, Any],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                event_id, tenant_id, actor_id, action, resource_type,
                resource_id, outcome, reason, source, evidence, occurred_at
            ) VALUES (
                :event_id, :tenant_id, :actor_id, :action, 'trigger_occurrence',
                :resource_id, 'SUCCESS', :reason,
                '{"component":"trigger-runtime-api"}'::jsonb,
                CAST(:evidence AS jsonb), clock_timestamp()
            )
            """
        ),
        {
            "event_id": new_runtime_id(),
            "tenant_id": tenant_id,
            "actor_id": actor_id,
            "action": action,
            "resource_id": resource_id,
            "reason": reason,
            "evidence": json.dumps(evidence),
        },
    )


def _to_occurrence(row: RowMapping, *, tenant_id: str) -> TriggerOccurrence:
    return TriggerOccurrence(
        occurrence_id=row["occurrence_id"],
        tenant_id=tenant_id,
        trigger_definition_id=row["trigger_definition_id"],
        namespace=row["namespace_name"],
        flow_id=row["flow_key"],
        flow_revision=row["flow_revision"],
        trigger_id=row["trigger_key"],
        trigger_type=row["trigger_type"],
        occurrence_key=row["occurrence_key"],
        state=row["state"],
        attempt=row["attempt"],
        max_attempts=row["max_attempts"],
        available_at=row["available_at"],
        payload=row["payload"],
        metadata=row["metadata"],
        evidence=row["evidence"],
        execution_id=row["execution_id"],
        replay_of=row["replay_of"],
        owner_id=row["owner_id"],
        fencing_token=row["fencing_token"],
        lease_expires_at=row["lease_expires_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        completed_at=row["completed_at"],
    )


def _to_runtime_state(row: RowMapping | dict[str, Any], *, tenant_id: str) -> TriggerRuntimeState:
    return TriggerRuntimeState(
        trigger_definition_id=row["trigger_definition_id"],
        tenant_id=tenant_id,
        namespace=row["namespace_name"],
        flow_id=row["flow_key"],
        flow_revision=row["flow_revision"],
        trigger_id=row["trigger_key"],
        trigger_type=row["trigger_type"],
        active=row["active"],
        paused=row["paused"],
        checkpoint=row["checkpoint"],
        cursor=row["cursor"],
        last_evaluated_at=row["last_evaluated_at"],
        next_evaluation_at=row["next_evaluation_at"],
        last_occurrence_at=row["last_occurrence_at"],
        last_success_at=row["last_success_at"],
        lag_seconds=row["lag_seconds"],
        pending_count=row["pending_count"],
        dead_letter_count=row["dead_letter_count"],
        consecutive_failures=row["consecutive_failures"],
        last_error=row["last_error"],
        last_decision=row["last_decision"],
        updated_at=row["updated_at"],
    )
