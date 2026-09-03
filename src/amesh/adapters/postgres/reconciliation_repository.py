from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import (
    ReconciliationDisposition,
    ReconciliationFinding,
    ReconciliationInvariant,
    ReconciliationMode,
    ReconciliationRequest,
    ReconciliationRun,
    new_runtime_id,
)
from amesh.ports import ReconciliationAlreadyRunningError, ReconciliationRepository
from amesh.ports.errors import NotFoundError
from amesh.ports.repository_support import AuditWrite

from .repository_support import PostgresRepositoryBase

_RUNBOOK = "docs/operations/reconciliation.md"

_GET_EXISTING_RUN = text(
    """
    SELECT reconciliation_runs.*, tenants.slug AS tenant_slug
    FROM reconciliation_runs
    JOIN tenants ON tenants.id = reconciliation_runs.tenant_id
    WHERE reconciliation_runs.tenant_id = :tenant_id
      AND reconciliation_runs.idempotency_key = :idempotency_key
    """
)

_INSERT_RUN = text(
    """
    INSERT INTO reconciliation_runs (
        id, tenant_id, mode, target_type, target_id, since, until,
        stale_after_seconds, max_findings, max_repairs, actor_id, reason,
        idempotency_key
    ) VALUES (
        :run_id, :tenant_id, :mode, :target_type, :target_id, :since, :until,
        :stale_after_seconds, :max_findings, :max_repairs, :actor_id, :reason,
        :idempotency_key
    )
    RETURNING *
    """
)

_COMPLETE_RUN = text(
    """
    UPDATE reconciliation_runs
    SET state = 'COMPLETED',
        repairs_applied = :repairs_applied,
        finding_count = :finding_count,
        unresolved_count = :unresolved_count,
        completed_at = clock_timestamp()
    WHERE id = :run_id AND tenant_id = :tenant_id AND state = 'RUNNING'
    RETURNING *
    """
)

_LIST_RUNS = text(
    """
    SELECT reconciliation_runs.*, tenants.slug AS tenant_slug
    FROM reconciliation_runs
    JOIN tenants ON tenants.id = reconciliation_runs.tenant_id
    WHERE reconciliation_runs.tenant_id = :tenant_id
    ORDER BY reconciliation_runs.created_at DESC, reconciliation_runs.id DESC
    LIMIT :limit
    """
)

_GET_RUN = text(
    """
    SELECT reconciliation_runs.*, tenants.slug AS tenant_slug
    FROM reconciliation_runs
    JOIN tenants ON tenants.id = reconciliation_runs.tenant_id
    WHERE reconciliation_runs.tenant_id = :tenant_id
      AND reconciliation_runs.id = :run_id
    """
)

_LIST_FINDINGS = text(
    """
    SELECT *
    FROM reconciliation_findings
    WHERE tenant_id = :tenant_id AND run_id = :run_id
    ORDER BY observed_at, id
    """
)

_SCAN_EXPIRED_LEASES = text(
    """
    SELECT
        'EXPIRED_LEASE' AS invariant_type,
        'queue_claim' AS resource_type,
        queue.id::text AS resource_id,
        queue.fencing_token AS expected_version,
        queue.updated_at AS observed_at,
        jsonb_build_object(
            'lane', queue.lane,
            'claimedBy', queue.claimed_by,
            'leaseExpiredAt', queue.lease_expires_at,
            'deliveryAttempt', queue.delivery_attempt,
            'maxAttempts', queue.max_attempts,
            'repairable', queue.delivery_attempt < queue.max_attempts
        ) AS detail
    FROM durable_work_queue AS queue
    LEFT JOIN task_attempts AS attempts ON attempts.queue_id = queue.id
    LEFT JOIN task_runs AS runs ON runs.id = attempts.task_run_id
    WHERE queue.tenant_id = :tenant_id
      AND queue.state = 'CLAIMED'
      AND queue.lease_expires_at <= clock_timestamp()
      AND CAST(:trigger_definition_id AS uuid) IS NULL
      AND (CAST(:execution_id AS uuid) IS NULL OR runs.execution_id = :execution_id)
      AND (
          CAST(:worker_id AS uuid) IS NULL
          OR queue.claimed_by = CAST(:worker_id AS text)
          OR attempts.worker_id = :worker_id
      )
      AND (CAST(:since AS timestamptz) IS NULL OR queue.updated_at >= :since)
      AND (CAST(:until AS timestamptz) IS NULL OR queue.updated_at < :until)
    ORDER BY queue.lease_expires_at, queue.id
    LIMIT :limit
    """
)

_SCAN_ORPHAN_TASK_RUNS = text(
    """
    SELECT
        'ORPHAN_TASK_RUN' AS invariant_type,
        'task_run' AS resource_type,
        runs.id::text AS resource_id,
        runs.version AS expected_version,
        runs.updated_at AS observed_at,
        jsonb_build_object(
            'executionId', runs.execution_id,
            'taskPath', runs.task_path,
            'currentAttempt', runs.current_attempt
        ) AS detail
    FROM task_runs AS runs
    WHERE runs.tenant_id = :tenant_id
      AND runs.state = 'RUNNING'
      AND NOT EXISTS (
          SELECT 1
          FROM task_attempts AS attempts
          WHERE attempts.tenant_id = runs.tenant_id
            AND attempts.task_run_id = runs.id
            AND attempts.attempt = runs.current_attempt
      )
      AND CAST(:trigger_definition_id AS uuid) IS NULL
      AND CAST(:worker_id AS uuid) IS NULL
      AND (CAST(:execution_id AS uuid) IS NULL OR runs.execution_id = :execution_id)
      AND (CAST(:since AS timestamptz) IS NULL OR runs.updated_at >= :since)
      AND (CAST(:until AS timestamptz) IS NULL OR runs.updated_at < :until)
    ORDER BY runs.updated_at, runs.id
    LIMIT :limit
    """
)

_SCAN_STUCK_EXECUTIONS = text(
    """
    SELECT
        'STUCK_EXECUTION' AS invariant_type,
        'execution' AS resource_type,
        executions.id::text AS resource_id,
        executions.version AS expected_version,
        executions.updated_at AS observed_at,
        jsonb_build_object(
            'state', executions.state,
            'epoch', executions.epoch,
            'updatedAt', executions.updated_at
        ) AS detail
    FROM executions
    WHERE executions.tenant_id = :tenant_id
      AND executions.state IN ('CREATED', 'QUEUED', 'RUNNING', 'RESTARTING', 'CANCELLING')
      AND executions.updated_at <= clock_timestamp() - make_interval(secs => :stale_after_seconds)
      AND NOT EXISTS (
          SELECT 1
          FROM task_runs
          JOIN task_attempts ON task_attempts.task_run_id = task_runs.id
          WHERE task_runs.tenant_id = executions.tenant_id
            AND task_runs.execution_id = executions.id
            AND task_attempts.state = 'RUNNING'
            AND (
                task_attempts.lease_expires_at IS NULL
                OR task_attempts.lease_expires_at > clock_timestamp()
            )
      )
      AND CAST(:trigger_definition_id AS uuid) IS NULL
      AND (
          CAST(:worker_id AS uuid) IS NULL
          OR EXISTS (
              SELECT 1
              FROM task_runs
              JOIN task_attempts ON task_attempts.task_run_id = task_runs.id
              WHERE task_runs.execution_id = executions.id
                AND task_attempts.worker_id = :worker_id
          )
      )
      AND (CAST(:execution_id AS uuid) IS NULL OR executions.id = :execution_id)
      AND (CAST(:since AS timestamptz) IS NULL OR executions.updated_at >= :since)
      AND (CAST(:until AS timestamptz) IS NULL OR executions.updated_at < :until)
    ORDER BY executions.updated_at, executions.id
    LIMIT :limit
    """
)

_SCAN_EXECUTION_EVENTS = text(
    """
    SELECT
        'UNPROJECTED_EVENT' AS invariant_type,
        'execution_event' AS resource_type,
        events.event_id::text AS resource_id,
        events.sequence AS expected_version,
        events.occurred_at AS observed_at,
        jsonb_build_object(
            'executionId', events.execution_id,
            'eventType', events.event_type,
            'sequence', events.sequence
        ) AS detail
    FROM execution_events AS events
    LEFT JOIN messages_outbox AS outbox
      ON outbox.tenant_id = events.tenant_id AND outbox.message_id = events.event_id
    WHERE events.tenant_id = :tenant_id
      AND outbox.sequence IS NULL
      AND CAST(:trigger_definition_id AS uuid) IS NULL
      AND CAST(:worker_id AS uuid) IS NULL
      AND (CAST(:execution_id AS uuid) IS NULL OR events.execution_id = :execution_id)
      AND events.occurred_at >= COALESCE(
          CAST(:since AS timestamptz),
          clock_timestamp() - interval '1 day'
      )
      AND (CAST(:until AS timestamptz) IS NULL OR events.occurred_at < :until)
    ORDER BY events.occurred_at, events.event_id
    LIMIT :limit
    """
)

_SCAN_TASK_EVENTS = text(
    """
    SELECT
        CASE
            WHEN events.event_type = 'TaskRunStarted' THEN 'MISSING_DISPATCH'
            ELSE 'UNPROJECTED_EVENT'
        END AS invariant_type,
        'task_run_event' AS resource_type,
        events.event_id::text AS resource_id,
        events.sequence AS expected_version,
        events.occurred_at AS observed_at,
        jsonb_build_object(
            'executionId', events.execution_id,
            'taskRunId', events.task_run_id,
            'eventType', events.event_type,
            'sequence', events.sequence
        ) AS detail
    FROM task_run_events AS events
    JOIN task_runs AS runs ON runs.id = events.task_run_id
    LEFT JOIN task_attempts AS attempts
      ON attempts.task_run_id = runs.id AND attempts.attempt = runs.current_attempt
    LEFT JOIN messages_outbox AS outbox
      ON outbox.tenant_id = events.tenant_id AND outbox.message_id = events.event_id
    WHERE events.tenant_id = :tenant_id
      AND outbox.sequence IS NULL
      AND CAST(:trigger_definition_id AS uuid) IS NULL
      AND (CAST(:execution_id AS uuid) IS NULL OR events.execution_id = :execution_id)
      AND (CAST(:worker_id AS uuid) IS NULL OR attempts.worker_id = :worker_id)
      AND events.occurred_at >= COALESCE(
          CAST(:since AS timestamptz),
          clock_timestamp() - interval '1 day'
      )
      AND (CAST(:until AS timestamptz) IS NULL OR events.occurred_at < :until)
    ORDER BY events.occurred_at, events.event_id
    LIMIT :limit
    """
)

_SCAN_SCHEDULE_PROJECTIONS = text(
    """
    SELECT
        'MISSING_SCHEDULE_PROJECTION' AS invariant_type,
        'trigger_definition' AS resource_type,
        triggers.id::text AS resource_id,
        revisions.revision AS expected_version,
        triggers.created_at AS observed_at,
        jsonb_build_object(
            'namespace', namespaces.name,
            'flowId', flows.flow_key,
            'flowRevision', revisions.revision,
            'triggerKey', triggers.trigger_key,
            'triggerType', triggers.trigger_type
        ) AS detail
    FROM trigger_definitions AS triggers
    JOIN flow_revisions AS revisions ON revisions.id = triggers.flow_revision_id
    JOIN flows ON flows.id = revisions.flow_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    LEFT JOIN scheduler_states AS states ON states.trigger_definition_id = triggers.id
    WHERE triggers.tenant_id = :tenant_id
      AND triggers.enabled
      AND triggers.trigger_type IN ('core.cron', 'core.interval')
      AND states.trigger_definition_id IS NULL
      AND CAST(:execution_id AS uuid) IS NULL
      AND CAST(:worker_id AS uuid) IS NULL
      AND (
          CAST(:trigger_definition_id AS uuid) IS NULL
          OR triggers.id = :trigger_definition_id
      )
      AND triggers.created_at >= COALESCE(
          CAST(:since AS timestamptz),
          clock_timestamp() - interval '1 day'
      )
      AND (CAST(:until AS timestamptz) IS NULL OR triggers.created_at < :until)
    ORDER BY triggers.created_at, triggers.id
    LIMIT :limit
    """
)

_REQUEUE_EXPIRED = text(
    """
    WITH candidate AS (
        SELECT id
        FROM durable_work_queue
        WHERE tenant_id = :tenant_id
          AND id = CAST(:resource_id AS bigint)
          AND state = 'CLAIMED'
          AND fencing_token = :expected_version
          AND lease_expires_at <= clock_timestamp()
          AND delivery_attempt < max_attempts
        FOR UPDATE
    ), released_attempt AS (
        UPDATE task_attempts
        SET worker_id = NULL,
            queue_id = NULL,
            lease_expires_at = NULL,
            last_heartbeat_at = NULL
        WHERE tenant_id = :tenant_id
          AND queue_id IN (SELECT id FROM candidate)
          AND state = 'RUNNING'
        RETURNING id
    )
    UPDATE durable_work_queue
    SET state = 'READY',
        claimed_by = NULL,
        lease_expires_at = NULL,
        available_at = clock_timestamp(),
        last_error = 'reconciled expired lease',
        updated_at = clock_timestamp()
    WHERE id IN (SELECT id FROM candidate)
    RETURNING id
    """
)

_REBUILD_EXECUTION_OUTBOX = text(
    """
    INSERT INTO messages_outbox (
        tenant_id, message_id, subject, partition_key, envelope, available_at
    )
    SELECT
        events.tenant_id,
        events.event_id,
        'execution-events',
        'execution:' || events.execution_id::text,
        jsonb_build_object(
            'message_id', events.event_id,
            'message_type', events.event_type,
            'schema_version', events.schema_version,
            'tenant_id', tenants.slug,
            'partition_key', 'execution:' || events.execution_id::text,
            'correlation_id', events.correlation_id,
            'causation_id', events.causation_id,
            'produced_at', events.occurred_at,
            'trace_context', '{}'::jsonb,
            'payload', jsonb_build_object(
                'execution_id', events.execution_id,
                'sequence', events.sequence,
                'actor_id', events.actor_id,
                'reason', events.reason,
                'event', events.payload
            )
        ),
        events.occurred_at
    FROM execution_events AS events
    JOIN tenants ON tenants.id = events.tenant_id
    WHERE events.tenant_id = :tenant_id
      AND events.event_id = CAST(:resource_id AS uuid)
      AND events.sequence = :expected_version
    ON CONFLICT (tenant_id, message_id) DO NOTHING
    RETURNING sequence
    """
)

_REBUILD_TASK_OUTBOX = text(
    """
    INSERT INTO messages_outbox (
        tenant_id, message_id, subject, partition_key, envelope, available_at
    )
    SELECT
        events.tenant_id,
        events.event_id,
        CASE
            WHEN events.event_type = 'TaskRunStarted'
                 AND COALESCE((events.payload ->> 'dispatch')::boolean, true)
                THEN 'task-dispatch'
            ELSE 'task-run-events'
        END,
        'execution:' || events.execution_id::text,
        jsonb_build_object(
            'message_id', events.event_id,
            'message_type', CASE
                WHEN events.event_type = 'TaskRunStarted'
                     AND COALESCE((events.payload ->> 'dispatch')::boolean, true)
                    THEN 'DispatchTaskRun'
                ELSE events.event_type
            END,
            'schema_version', events.schema_version,
            'tenant_id', tenants.slug,
            'partition_key', 'execution:' || events.execution_id::text,
            'correlation_id', events.correlation_id,
            'causation_id', events.causation_id,
            'produced_at', events.occurred_at,
            'trace_context', '{}'::jsonb,
            'payload', jsonb_build_object(
                'execution_id', events.execution_id,
                'task_run_id', events.task_run_id,
                'sequence', events.sequence,
                'actor_id', events.actor_id,
                'reason', events.reason,
                'event_type', events.event_type,
                'event', events.payload
            )
        ),
        events.occurred_at
    FROM task_run_events AS events
    JOIN tenants ON tenants.id = events.tenant_id
    WHERE events.tenant_id = :tenant_id
      AND events.event_id = CAST(:resource_id AS uuid)
      AND events.sequence = :expected_version
    ON CONFLICT (tenant_id, message_id) DO NOTHING
    RETURNING sequence
    """
)

_REBUILD_SCHEDULE_PROJECTION = text(
    """
    INSERT INTO scheduler_states (
        trigger_definition_id, tenant_id, namespace_name, flow_key,
        flow_revision, trigger_key, next_fire_at, last_decision
    )
    SELECT
        triggers.id,
        triggers.tenant_id,
        namespaces.name,
        flows.flow_key,
        revisions.revision,
        triggers.trigger_key,
        NULL,
        'projection rebuilt; scheduler initialization pending'
    FROM trigger_definitions AS triggers
    JOIN flow_revisions AS revisions ON revisions.id = triggers.flow_revision_id
    JOIN flows ON flows.id = revisions.flow_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    WHERE triggers.tenant_id = :tenant_id
      AND triggers.id = CAST(:resource_id AS uuid)
      AND revisions.revision = :expected_version
      AND triggers.enabled
      AND triggers.trigger_type IN ('core.cron', 'core.interval')
    ON CONFLICT (trigger_definition_id) DO NOTHING
    RETURNING trigger_definition_id
    """
)

_INSERT_FINDING = text(
    """
    INSERT INTO reconciliation_findings (
        id, tenant_id, run_id, invariant_type, resource_type, resource_id,
        expected_version, disposition, repair_action, detail, runbook,
        observed_at, resolved_at
    ) VALUES (
        :finding_id, :tenant_id, :run_id, :invariant_type, :resource_type,
        :resource_id, :expected_version, :disposition, :repair_action,
        CAST(:detail AS jsonb), :runbook, :observed_at, :resolved_at
    )
    RETURNING *
    """
)

_SCANS = (
    _SCAN_EXPIRED_LEASES,
    _SCAN_ORPHAN_TASK_RUNS,
    _SCAN_STUCK_EXECUTIONS,
    _SCAN_EXECUTION_EVENTS,
    _SCAN_TASK_EVENTS,
    _SCAN_SCHEDULE_PROJECTIONS,
)


@dataclass(frozen=True)
class _Candidate:
    invariant: ReconciliationInvariant
    resource_type: str
    resource_id: str
    expected_version: int | None
    observed_at: datetime
    detail: dict[str, Any]


class PostgresReconciliationRepository(PostgresRepositoryBase, ReconciliationRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def run(
        self,
        request: ReconciliationRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> ReconciliationRun:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            existing = (
                (
                    await connection.execute(
                        _GET_EXISTING_RUN,
                        {"tenant_id": tenant_uuid, "idempotency_key": request.idempotency_key},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if existing is not None:
                return await self._hydrate_run(connection, existing, tenant_uuid)
            locked = bool(
                await connection.scalar(
                    text(
                        "SELECT pg_try_advisory_xact_lock("
                        "hashtextextended('amesh-reconciliation:' || :tenant_id, 0))"
                    ),
                    {"tenant_id": str(tenant_uuid)},
                )
            )
            if not locked:
                raise ReconciliationAlreadyRunningError(
                    f"tenant {tenant_id!r} already has an active reconciliation transaction"
                )
            run_id = new_runtime_id()
            await connection.execute(
                _INSERT_RUN,
                {
                    "run_id": run_id,
                    "tenant_id": tenant_uuid,
                    "mode": request.mode.value,
                    "target_type": request.target_type.value,
                    "target_id": request.target_id,
                    "since": request.since,
                    "until": request.until,
                    "stale_after_seconds": request.stale_after_seconds,
                    "max_findings": request.max_findings,
                    "max_repairs": request.max_repairs,
                    "actor_id": actor_id,
                    "reason": request.reason,
                    "idempotency_key": request.idempotency_key,
                },
            )
            candidates = await self._scan(connection, tenant_uuid, request)
            findings: list[ReconciliationFinding] = []
            repairs_applied = 0
            for candidate in candidates:
                disposition = ReconciliationDisposition.DETECTED
                repair_action = _repair_action(candidate)
                resolved_at: datetime | None = None
                if request.mode is ReconciliationMode.APPLY:
                    repaired = False
                    if repair_action is not None and repairs_applied < request.max_repairs:
                        repaired = await self._repair(connection, tenant_uuid, candidate)
                    if repaired:
                        disposition = ReconciliationDisposition.REPAIRED
                        repairs_applied += 1
                    elif repair_action is not None and repairs_applied >= request.max_repairs:
                        disposition = ReconciliationDisposition.DETECTED
                    else:
                        disposition = ReconciliationDisposition.QUARANTINED
                    if disposition is not ReconciliationDisposition.DETECTED:
                        resolved_at = await connection.scalar(text("SELECT clock_timestamp()"))
                    await self._audit(
                        connection,
                        tenant_uuid,
                        run_id,
                        candidate,
                        disposition,
                        actor_id=actor_id,
                        reason=request.reason,
                        repair_action=repair_action,
                    )
                finding_row = (
                    (
                        await connection.execute(
                            _INSERT_FINDING,
                            {
                                "finding_id": new_runtime_id(),
                                "tenant_id": tenant_uuid,
                                "run_id": run_id,
                                "invariant_type": candidate.invariant.value,
                                "resource_type": candidate.resource_type,
                                "resource_id": candidate.resource_id,
                                "expected_version": candidate.expected_version,
                                "disposition": disposition.value,
                                "repair_action": repair_action,
                                "detail": json.dumps(candidate.detail, default=str),
                                "runbook": _RUNBOOK,
                                "observed_at": candidate.observed_at,
                                "resolved_at": resolved_at,
                            },
                        )
                    )
                    .mappings()
                    .one()
                )
                findings.append(_to_finding(finding_row))
            unresolved_count = sum(
                finding.disposition is not ReconciliationDisposition.REPAIRED
                for finding in findings
            )
            completed = (
                (
                    await connection.execute(
                        _COMPLETE_RUN,
                        {
                            "run_id": run_id,
                            "tenant_id": tenant_uuid,
                            "repairs_applied": repairs_applied,
                            "finding_count": len(findings),
                            "unresolved_count": unresolved_count,
                        },
                    )
                )
                .mappings()
                .one()
            )
            return _to_run(completed, tenant_id=tenant_id, findings=tuple(findings))

    async def get(self, run_id: UUID, *, tenant_id: str) -> ReconciliationRun:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _GET_RUN,
                        {"tenant_id": tenant_uuid, "run_id": run_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise NotFoundError(
                    "reconciliation run",
                    run_id,
                    message=f"reconciliation run {run_id} does not exist",
                )
            return await self._hydrate_run(connection, row, tenant_uuid)

    async def list_runs(
        self,
        *,
        tenant_id: str,
        limit: int = 50,
    ) -> list[ReconciliationRun]:
        if limit < 1 or limit > 200:
            raise ValueError("reconciliation list limit must be between 1 and 200")
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _LIST_RUNS,
                        {"tenant_id": tenant_uuid, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
            return [await self._hydrate_run(connection, row, tenant_uuid) for row in rows]

    async def _scan(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        request: ReconciliationRequest,
    ) -> list[_Candidate]:
        parameters = {
            "tenant_id": tenant_id,
            "execution_id": request.execution_id,
            "trigger_definition_id": request.trigger_definition_id,
            "worker_id": request.worker_id,
            "since": request.since,
            "until": request.until,
            "stale_after_seconds": request.stale_after_seconds,
            "limit": request.max_findings,
        }
        candidates: list[_Candidate] = []
        for statement in _SCANS:
            rows = (await connection.execute(statement, parameters)).mappings().all()
            candidates.extend(_to_candidate(row) for row in rows)
        candidates.sort(
            key=lambda item: (
                item.observed_at,
                item.invariant.value,
                item.resource_type,
                item.resource_id,
            )
        )
        return candidates[: request.max_findings]

    async def _repair(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        candidate: _Candidate,
    ) -> bool:
        statement = {
            ReconciliationInvariant.EXPIRED_LEASE: _REQUEUE_EXPIRED,
            ReconciliationInvariant.UNPROJECTED_EVENT: (
                _REBUILD_EXECUTION_OUTBOX
                if candidate.resource_type == "execution_event"
                else _REBUILD_TASK_OUTBOX
            ),
            ReconciliationInvariant.MISSING_DISPATCH: _REBUILD_TASK_OUTBOX,
            ReconciliationInvariant.MISSING_SCHEDULE_PROJECTION: _REBUILD_SCHEDULE_PROJECTION,
        }.get(candidate.invariant)
        if statement is None or candidate.expected_version is None:
            return False
        repaired = await connection.scalar(
            statement,
            {
                "tenant_id": tenant_id,
                "resource_id": (
                    int(candidate.resource_id)
                    if candidate.invariant is ReconciliationInvariant.EXPIRED_LEASE
                    else candidate.resource_id
                ),
                "expected_version": candidate.expected_version,
            },
        )
        return repaired is not None

    async def _audit(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        run_id: UUID,
        candidate: _Candidate,
        disposition: ReconciliationDisposition,
        *,
        actor_id: str,
        reason: str,
        repair_action: str | None,
    ) -> None:
        evidence = json.loads(
            json.dumps(
                {
                    "invariant": candidate.invariant.value,
                    "expectedVersion": candidate.expected_version,
                    "repairAction": repair_action,
                    "detail": candidate.detail,
                },
                default=str,
            )
        )
        await self._services.audit.write(
            connection,
            AuditWrite(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action=(
                    "reconciliation.repair"
                    if disposition is ReconciliationDisposition.REPAIRED
                    else (
                        "reconciliation.defer"
                        if disposition is ReconciliationDisposition.DETECTED
                        else "reconciliation.quarantine"
                    )
                ),
                resource_type=candidate.resource_type,
                resource_id=candidate.resource_id,
                outcome=disposition.value,
                reason=reason,
                correlation_id=run_id,
                source={"component": "reconciler", "runbook": _RUNBOOK},
                evidence=evidence,
                event_id=new_runtime_id(),
                use_database_clock=True,
            ),
        )

    async def _hydrate_run(
        self,
        connection: AsyncConnection,
        row: RowMapping,
        tenant_id: UUID,
    ) -> ReconciliationRun:
        findings = (
            (
                await connection.execute(
                    _LIST_FINDINGS,
                    {"tenant_id": tenant_id, "run_id": row["id"]},
                )
            )
            .mappings()
            .all()
        )
        return _to_run(
            row,
            tenant_id=str(row["tenant_slug"]),
            findings=tuple(_to_finding(item) for item in findings),
        )


def _repair_action(candidate: _Candidate) -> str | None:
    if candidate.invariant is ReconciliationInvariant.EXPIRED_LEASE:
        return "REQUEUE_EXPIRED_LEASE" if candidate.detail.get("repairable") else None
    if candidate.invariant in {
        ReconciliationInvariant.MISSING_DISPATCH,
        ReconciliationInvariant.UNPROJECTED_EVENT,
    }:
        return "REBUILD_OUTBOX_PROJECTION"
    if candidate.invariant is ReconciliationInvariant.MISSING_SCHEDULE_PROJECTION:
        return "REBUILD_SCHEDULE_PROJECTION"
    return None


def _to_candidate(row: RowMapping) -> _Candidate:
    return _Candidate(
        invariant=ReconciliationInvariant(row["invariant_type"]),
        resource_type=str(row["resource_type"]),
        resource_id=str(row["resource_id"]),
        expected_version=(
            int(row["expected_version"]) if row["expected_version"] is not None else None
        ),
        observed_at=row["observed_at"],
        detail=dict(row["detail"] or {}),
    )


def _to_finding(row: RowMapping) -> ReconciliationFinding:
    return ReconciliationFinding(
        id=row["id"],
        invariant=row["invariant_type"],
        resourceType=row["resource_type"],
        resourceId=row["resource_id"],
        expectedVersion=row["expected_version"],
        disposition=row["disposition"],
        repairAction=row["repair_action"],
        detail=row["detail"] or {},
        runbook=row["runbook"],
        observedAt=row["observed_at"],
        resolvedAt=row["resolved_at"],
    )


def _to_run(
    row: RowMapping,
    *,
    tenant_id: str,
    findings: tuple[ReconciliationFinding, ...],
) -> ReconciliationRun:
    return ReconciliationRun(
        id=row["id"],
        tenantId=tenant_id,
        mode=row["mode"],
        targetType=row["target_type"],
        targetId=row["target_id"],
        since=row["since"],
        until=row["until"],
        state=row["state"],
        maxRepairs=row["max_repairs"],
        repairsApplied=row["repairs_applied"],
        findingCount=row["finding_count"],
        unresolvedCount=row["unresolved_count"],
        actorId=row["actor_id"],
        reason=row["reason"],
        idempotencyKey=row["idempotency_key"],
        createdAt=row["created_at"],
        completedAt=row["completed_at"],
        findings=findings,
    )
