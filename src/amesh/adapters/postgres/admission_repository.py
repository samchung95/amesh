"""SQL authority for the admission_repository execution port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection

from amesh.domain import (
    AdmissionBehavior,
    AdmissionDecision,
    AdmissionDiagnostics,
    AdmissionOutcome,
    AdmissionResourceType,
    ExecutionEventType,
    ExecutionState,
    PolicyDecision,
    PolicyStage,
    ResolvedAdmissionPolicy,
    TaskRunEventType,
    TaskRunState,
    new_runtime_id,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.ports.execution_repository import AdmissionRepository

from .check_repository import (
    record_execution_check_start,
)
from .execution_port_base import PostgresExecutionPort
from .execution_rows import (
    admission_decision_from_row as _to_admission_decision,
)
from .execution_shared import _DATABASE_TIME, _INSERT_EXECUTION_EVENT

_REQUEST_ADMISSION_TX_SELECT_ADMISSION_RESERVATIONS = text(
    """
                    SELECT resource_id
                    FROM admission_reservations
                    WHERE tenant_id = :tenant_id
                      AND resource_type = :resource_type
                      AND bucket = :bucket
                      AND released_at IS NULL
                      AND lease_expires_at > clock_timestamp()
                    ORDER BY created_at, reservation_id
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                    """
)

_GET_ADMISSION_REQUEST = text(
    """
    WITH ranked AS (
        SELECT request_id,
               row_number() OVER (
                   ORDER BY
                       priority
                           + floor(extract(epoch FROM (clock_timestamp() - created_at)) / 60)
                           DESC,
                       created_at,
                       request_id
               ) AS queue_position
        FROM admission_requests
        WHERE tenant_id = :tenant_id AND outcome = 'QUEUED'
    )
    SELECT requests.*,
           ranked.queue_position,
           greatest(extract(epoch FROM (clock_timestamp() - requests.created_at)), 0)
               AS queue_age_seconds
    FROM admission_requests AS requests
    LEFT JOIN ranked ON ranked.request_id = requests.request_id
    WHERE requests.tenant_id = :tenant_id
      AND requests.resource_type = :resource_type
      AND requests.resource_id = :resource_id
    ORDER BY requests.created_at DESC, requests.request_id DESC
    LIMIT 1
    """
)

_INSERT_ADMISSION_REQUEST = text(
    """
    INSERT INTO admission_requests (
        request_id, tenant_id, resource_type, resource_id, policies, priority,
        outcome, reason, limiting_policy_id, limiting_scope, limiting_bucket,
        active_count, limit_value, replaced_resource_id, admitted_at, finished_at
    ) VALUES (
        :request_id, :tenant_id, :resource_type, :resource_id, CAST(:policies AS jsonb),
        :priority, :outcome, :reason, :limiting_policy_id, :limiting_scope,
        :limiting_bucket, :active_count, :limit_value, :replaced_resource_id,
        CASE WHEN :outcome IN ('ADMITTED', 'REPLACED') THEN clock_timestamp() ELSE NULL END,
        CASE WHEN :outcome IN ('CANCELLED', 'FAILED', 'SKIPPED')
             THEN clock_timestamp() ELSE NULL END
    )
    RETURNING *
    """
)

_INSERT_ADMISSION_RESERVATION = text(
    """
    INSERT INTO admission_reservations (
        reservation_id, tenant_id, request_id, resource_type, resource_id,
        policy_id, scope, bucket, lease_expires_at
    ) VALUES (
        :reservation_id, :tenant_id, :request_id, :resource_type, :resource_id,
        :policy_id, :scope, :bucket,
        clock_timestamp() + make_interval(secs => :lease_seconds)
    )
    ON CONFLICT (tenant_id, request_id, policy_id) DO NOTHING
    """
)

_RELEASE_ADMISSION = text(
    """
    WITH released AS (
        UPDATE admission_reservations
        SET released_at = COALESCE(released_at, clock_timestamp()),
            release_reason = COALESCE(release_reason, :reason)
        WHERE tenant_id = :tenant_id
          AND resource_type = :resource_type
          AND resource_id = :resource_id
          AND released_at IS NULL
        RETURNING request_id
    )
    UPDATE admission_requests
    SET outcome = CASE WHEN outcome IN ('ADMITTED', 'REPLACED') THEN 'RELEASED' ELSE outcome END,
        reason = CASE WHEN outcome IN ('ADMITTED', 'REPLACED') THEN :reason ELSE reason END,
        finished_at = CASE
            WHEN outcome IN ('ADMITTED', 'REPLACED') THEN clock_timestamp()
            ELSE finished_at
        END
    WHERE tenant_id = :tenant_id
      AND resource_type = :resource_type
      AND resource_id = :resource_id
      AND (
          EXISTS (SELECT 1 FROM released)
          OR outcome IN ('ADMITTED', 'REPLACED')
      )
    RETURNING request_id
    """
)

_EXPIRE_ADMISSION_RESERVATIONS = text(
    """
    WITH expired AS (
        UPDATE admission_reservations
        SET released_at = clock_timestamp(), release_reason = 'lease expired'
        WHERE tenant_id = :tenant_id
          AND released_at IS NULL
          AND lease_expires_at <= clock_timestamp()
        RETURNING request_id
    )
    UPDATE admission_requests
    SET outcome = 'EXPIRED', reason = 'admission lease expired', finished_at = clock_timestamp()
    WHERE tenant_id = :tenant_id
      AND request_id IN (SELECT request_id FROM expired)
      AND NOT EXISTS (
          SELECT 1 FROM admission_reservations
          WHERE admission_reservations.request_id = admission_requests.request_id
            AND admission_reservations.released_at IS NULL
            AND admission_reservations.lease_expires_at > clock_timestamp()
      )
    RETURNING request_id
    """
)

_LIST_QUEUED_ADMISSIONS = text(
    """
    SELECT *
    FROM admission_requests
    WHERE tenant_id = :tenant_id AND outcome = 'QUEUED'
    ORDER BY
        priority + floor(extract(epoch FROM (clock_timestamp() - created_at)) / 60) DESC,
        created_at,
        request_id
    FOR UPDATE SKIP LOCKED
    LIMIT :limit
    """
)

_ADMISSION_DIAGNOSTICS = text(
    """
    SELECT
        (SELECT count(*) FROM admission_reservations
         WHERE tenant_id = :tenant_id AND released_at IS NULL
           AND lease_expires_at > clock_timestamp()) AS active_reservations,
        (SELECT count(*) FROM admission_requests
         WHERE tenant_id = :tenant_id AND outcome = 'QUEUED') AS queued_requests,
        COALESCE((SELECT greatest(extract(epoch FROM (
            clock_timestamp() - min(created_at)
        )), 0) FROM admission_requests
         WHERE tenant_id = :tenant_id AND outcome = 'QUEUED'), 0) AS oldest_queue_age_seconds,
        COALESCE((SELECT jsonb_object_agg(limiting_policy_id, pressure)
                  FROM (SELECT limiting_policy_id, count(*) AS pressure
                        FROM admission_requests
                        WHERE tenant_id = :tenant_id AND outcome = 'QUEUED'
                          AND limiting_policy_id IS NOT NULL
                        GROUP BY limiting_policy_id) AS grouped), '{}'::jsonb)
            AS pressure_by_policy
    """
)


class PostgresAdmissionRepository(PostgresExecutionPort, AdmissionRepository):
    @property
    def has_admission_policy_enforcer(self) -> bool:
        return self._admission_policy_enforcer is not None

    async def enforce_admission_policy(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        stage: PolicyStage,
        actor_id: str,
        inputs: dict[str, object] | None = None,
        task: TaskDefinition | None = None,
        execution_id: UUID | None = None,
        task_run_id: UUID | None = None,
    ) -> PolicyDecision:
        if self._admission_policy_enforcer is None:
            raise RuntimeError("admission policy enforcer is not configured")
        return await self._admission_policy_enforcer(
            flow,
            tenant_id,
            stage,
            actor_id,
            inputs,
            task,
            execution_id,
            task_run_id,
        )

    async def request_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        policies: tuple[ResolvedAdmissionPolicy, ...],
        *,
        tenant_id: str,
        priority: int = 0,
    ) -> AdmissionDecision:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            decision = await self._request_admission_tx(
                connection,
                tenant_uuid,
                resource_type,
                resource_id,
                policies,
                priority,
            )
            if resource_type is AdmissionResourceType.TASK and decision.outcome in {
                AdmissionOutcome.CANCELLED,
                AdmissionOutcome.FAILED,
                AdmissionOutcome.SKIPPED,
            }:
                await self._terminate_denied_task(
                    connection,
                    tenant_uuid,
                    resource_id,
                    decision,
                )
            return decision

    async def get_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        *,
        tenant_id: str,
    ) -> AdmissionDecision | None:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = await self._get_admission_row(
                connection,
                tenant_uuid,
                resource_type,
                resource_id,
            )
        return _to_admission_decision(row) if row is not None else None

    async def release_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        *,
        tenant_id: str,
        reason: str = "resource completed",
    ) -> bool:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            released = await self._release_admission_tx(
                connection,
                tenant_uuid,
                resource_type,
                resource_id,
                reason,
            )
            await self._reconcile_admission_tx(connection, tenant_uuid, limit=100)
        return released

    async def reconcile_admission(self, *, tenant_id: str, limit: int = 100) -> int:
        if limit < 1 or limit > 10_000:
            raise ValueError("admission reconciliation limit must be between 1 and 10000")
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            return await self._reconcile_admission_tx(connection, tenant_uuid, limit=limit)

    async def admission_diagnostics(self, *, tenant_id: str) -> AdmissionDiagnostics:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            await connection.execute(
                _EXPIRE_ADMISSION_RESERVATIONS,
                {"tenant_id": tenant_uuid},
            )
            row = (
                (
                    await connection.execute(
                        _ADMISSION_DIAGNOSTICS,
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one()
            )
        return AdmissionDiagnostics(
            active_reservations=int(row["active_reservations"]),
            queued_requests=int(row["queued_requests"]),
            oldest_queue_age_seconds=float(row["oldest_queue_age_seconds"]),
            pressure_by_policy={
                str(key): int(value) for key, value in row["pressure_by_policy"].items()
            },
        )

    async def _request_admission_tx(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        policies: tuple[ResolvedAdmissionPolicy, ...],
        priority: int,
    ) -> AdmissionDecision:
        await connection.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:resource_key, 0))"),
            {"resource_key": f"{tenant_id}:{resource_type.value}:{resource_id}"},
        )
        existing = await self._get_admission_row(
            connection,
            tenant_id,
            resource_type,
            resource_id,
        )
        if existing is not None and AdmissionOutcome(existing["outcome"]) not in {
            AdmissionOutcome.RELEASED,
            AdmissionOutcome.EXPIRED,
        }:
            return _to_admission_decision(existing)
        (
            limiting,
            active_count,
            replaced_resource_id,
            outcome,
            reason,
        ) = await self._resolve_admission_outcome(
            connection, tenant_id, resource_type, resource_id, policies
        )
        request_id = new_runtime_id()
        inserted = (
            (
                await connection.execute(
                    _INSERT_ADMISSION_REQUEST,
                    {
                        "request_id": request_id,
                        "tenant_id": tenant_id,
                        "resource_type": resource_type.value,
                        "resource_id": resource_id,
                        "policies": self._services.codec.dumps(
                            [policy.model_dump(mode="json") for policy in policies]
                        ),
                        "priority": priority,
                        "outcome": outcome.value,
                        "reason": reason,
                        "limiting_policy_id": limiting.policy_id if limiting else None,
                        "limiting_scope": limiting.scope.value if limiting else None,
                        "limiting_bucket": limiting.bucket if limiting else None,
                        "active_count": active_count,
                        "limit_value": limiting.limit if limiting else None,
                        "replaced_resource_id": replaced_resource_id,
                    },
                )
            )
            .mappings()
            .one_or_none()
        )
        if inserted is None:
            raise RuntimeError("admission request identity conflict")
        if outcome in {AdmissionOutcome.ADMITTED, AdmissionOutcome.REPLACED}:
            await self._insert_admission_reservations(
                connection,
                tenant_id,
                request_id,
                resource_type,
                resource_id,
                policies,
            )
        row = await self._get_admission_row(
            connection,
            tenant_id,
            resource_type,
            resource_id,
        )
        if row is None:
            raise RuntimeError("admission decision was not persisted")
        return _to_admission_decision(row)

    async def _resolve_admission_outcome(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        policies: tuple[ResolvedAdmissionPolicy, ...],
    ) -> tuple[ResolvedAdmissionPolicy | None, int, UUID | None, AdmissionOutcome, str]:
        await connection.execute(
            _EXPIRE_ADMISSION_RESERVATIONS,
            {"tenant_id": tenant_id},
        )
        for bucket in sorted({policy.bucket for policy in policies}):
            await connection.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:bucket, 0))"),
                {"bucket": bucket},
            )

        limiting: ResolvedAdmissionPolicy | None = None
        active_count = 0
        for policy in policies:
            count = int(
                await connection.scalar(
                    text("SELECT amesh_admission_active_count(:resource_type, :bucket)"),
                    {"resource_type": resource_type.value, "bucket": policy.bucket},
                )
                or 0
            )
            if count >= policy.limit:
                limiting = policy
                active_count = count
                break

        replaced_resource_id: UUID | None = None
        outcome = AdmissionOutcome.ADMITTED
        reason = "all admission policies have available capacity"
        if limiting is not None and limiting.behavior is AdmissionBehavior.REPLACE:
            victim = await connection.scalar(
                _REQUEST_ADMISSION_TX_SELECT_ADMISSION_RESERVATIONS,
                {
                    "tenant_id": tenant_id,
                    "resource_type": resource_type.value,
                    "bucket": limiting.bucket,
                },
            )
            if victim is not None:
                replaced_resource_id = UUID(str(victim))
                await self._release_admission_tx(
                    connection,
                    tenant_id,
                    resource_type,
                    replaced_resource_id,
                    f"replaced by {resource_id}",
                    replacement=True,
                )
                await self._terminate_replaced_resource(
                    connection,
                    tenant_id,
                    resource_type,
                    replaced_resource_id,
                    resource_id,
                )
                limiting = None
                outcome = AdmissionOutcome.REPLACED
                reason = f"admitted after replacing {replaced_resource_id}"

        if limiting is not None:
            outcome = {
                AdmissionBehavior.QUEUE: AdmissionOutcome.QUEUED,
                AdmissionBehavior.CANCEL: AdmissionOutcome.CANCELLED,
                AdmissionBehavior.FAIL: AdmissionOutcome.FAILED,
                AdmissionBehavior.REPLACE: AdmissionOutcome.REPLACED,
                AdmissionBehavior.SKIP: AdmissionOutcome.SKIPPED,
            }[limiting.behavior]
            reason = (
                f"policy {limiting.policy_id} reached {active_count}/{limiting.limit}; "
                f"behavior={limiting.behavior.value}"
            )
        return limiting, active_count, replaced_resource_id, outcome, reason

    async def _get_admission_row(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
    ) -> RowMapping | None:
        return (
            (
                await connection.execute(
                    _GET_ADMISSION_REQUEST,
                    {
                        "tenant_id": tenant_id,
                        "resource_type": resource_type.value,
                        "resource_id": resource_id,
                    },
                )
            )
            .mappings()
            .one_or_none()
        )

    async def _insert_admission_reservations(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        request_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        policies: tuple[ResolvedAdmissionPolicy, ...],
    ) -> None:
        if not policies:
            return
        await connection.execute(
            _INSERT_ADMISSION_RESERVATION,
            [
                {
                    "reservation_id": new_runtime_id(),
                    "tenant_id": tenant_id,
                    "request_id": request_id,
                    "resource_type": resource_type.value,
                    "resource_id": resource_id,
                    "policy_id": policy.policy_id,
                    "scope": policy.scope.value,
                    "bucket": policy.bucket,
                    "lease_seconds": policy.lease_seconds,
                }
                for policy in policies
            ],
        )

    async def _release_admission_tx(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        reason: str,
        *,
        replacement: bool = False,
    ) -> bool:
        result = await connection.execute(
            _RELEASE_ADMISSION,
            {
                "tenant_id": tenant_id,
                "resource_type": resource_type.value,
                "resource_id": resource_id,
                "reason": reason,
            },
        )
        released = result.scalar_one_or_none() is not None
        if replacement:
            await connection.execute(
                text(
                    """
                    UPDATE admission_requests
                    SET outcome = 'REPLACED', reason = :reason,
                        finished_at = COALESCE(finished_at, clock_timestamp())
                    WHERE tenant_id = :tenant_id
                      AND resource_type = :resource_type
                      AND resource_id = :resource_id
                      AND outcome IN ('ADMITTED', 'RELEASED')
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "resource_type": resource_type.value,
                    "resource_id": resource_id,
                    "reason": reason,
                },
            )
        return released

    async def _reconcile_admission_tx(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        *,
        limit: int,
    ) -> int:
        await connection.execute(
            _EXPIRE_ADMISSION_RESERVATIONS,
            {"tenant_id": tenant_id},
        )
        queued = (
            (
                await connection.execute(
                    _LIST_QUEUED_ADMISSIONS,
                    {"tenant_id": tenant_id, "limit": limit},
                )
            )
            .mappings()
            .all()
        )
        promoted = 0
        for row in queued:
            policies = tuple(
                ResolvedAdmissionPolicy.model_validate(item) for item in row["policies"]
            )
            for bucket in sorted({policy.bucket for policy in policies}):
                await connection.execute(
                    text("SELECT pg_advisory_xact_lock(hashtextextended(:bucket, 0))"),
                    {"bucket": bucket},
                )
            capacity_reached = False
            for policy in policies:
                active = int(
                    await connection.scalar(
                        text("SELECT amesh_admission_active_count(:resource_type, :bucket)"),
                        {
                            "resource_type": row["resource_type"],
                            "bucket": policy.bucket,
                        },
                    )
                    or 0
                )
                if active >= policy.limit:
                    capacity_reached = True
                    break
            if capacity_reached:
                continue
            updated = await connection.scalar(
                text(
                    """
                    UPDATE admission_requests
                    SET outcome = 'ADMITTED', reason = 'capacity became available',
                        limiting_policy_id = NULL, limiting_scope = NULL,
                        limiting_bucket = NULL, active_count = 0, limit_value = NULL,
                        admitted_at = clock_timestamp()
                    WHERE tenant_id = :tenant_id AND request_id = :request_id
                      AND outcome = 'QUEUED'
                    RETURNING request_id
                    """
                ),
                {"tenant_id": tenant_id, "request_id": row["request_id"]},
            )
            if updated is None:
                continue
            resource_type = AdmissionResourceType(row["resource_type"])
            resource_id = UUID(str(row["resource_id"]))
            await self._insert_admission_reservations(
                connection,
                tenant_id,
                UUID(str(row["request_id"])),
                resource_type,
                resource_id,
                policies,
            )
            if resource_type is AdmissionResourceType.EXECUTION:
                await self._start_promoted_execution(connection, tenant_id, resource_id)
            promoted += 1
        return promoted

    async def _start_promoted_execution(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
    ) -> None:
        row = (
            (
                await connection.execute(
                    text(
                        """
                        UPDATE executions
                        SET state = 'RUNNING', version = version + 1,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND id = :execution_id
                          AND state = 'QUEUED'
                        RETURNING version, flow_revision_id, namespace_name, flow_key,
                                  inputs, labels, trigger_context, created_at, updated_at
                        """
                    ),
                    {"tenant_id": tenant_id, "execution_id": execution_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return
        event_id = new_runtime_id()
        await connection.execute(
            _INSERT_EXECUTION_EVENT,
            {
                "tenant_id": tenant_id,
                "execution_id": execution_id,
                "sequence": int(row["version"]),
                "event_id": event_id,
                "event_type": ExecutionEventType.STARTED.value,
                "idempotency_key": str(event_id),
                "correlation_id": new_runtime_id(),
                "actor_id": "system:admission-reconciler",
                "reason": "capacity became available",
                "occurred_at": await connection.scalar(_DATABASE_TIME),
                "trace_context": self._services.codec.dumps({}),
            },
        )
        flow_revision = await connection.scalar(
            text("SELECT revision FROM flow_revisions WHERE id = :id"),
            {"id": row["flow_revision_id"]},
        )
        await record_execution_check_start(
            connection,
            tenant_id,
            flow_revision_id=UUID(str(row["flow_revision_id"])),
            execution_id=execution_id,
            execution_state=ExecutionState.RUNNING.value,
            namespace=str(row["namespace_name"]),
            flow_id=str(row["flow_key"]),
            flow_revision=int(flow_revision),
            created_at=row["created_at"],
            started_at=row["updated_at"],
            trigger=dict(row["trigger_context"]),
            labels=dict(row["labels"]),
        )

    async def _terminate_replaced_resource(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        replacement_id: UUID,
    ) -> None:
        reason = f"replaced by {replacement_id}"
        if resource_type is AdmissionResourceType.EXECUTION:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE executions
                            SET state = 'CANCELLED', version = version + 2,
                                terminal_at = clock_timestamp(), updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND id = :resource_id
                              AND state IN ('RUNNING', 'QUEUED', 'PAUSED')
                            RETURNING version
                            """
                        ),
                        {"tenant_id": tenant_id, "resource_id": resource_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is not None:
                occurred_at = await connection.scalar(_DATABASE_TIME)
                correlation_id = new_runtime_id()
                version = int(row["version"])
                parameters = []
                for sequence, event_type in (
                    (version - 1, ExecutionEventType.CANCEL_REQUESTED),
                    (version, ExecutionEventType.CANCELLED),
                ):
                    event_id = new_runtime_id()
                    parameters.append(
                        {
                            "tenant_id": tenant_id,
                            "execution_id": resource_id,
                            "sequence": sequence,
                            "event_id": event_id,
                            "event_type": event_type.value,
                            "idempotency_key": str(event_id),
                            "correlation_id": correlation_id,
                            "actor_id": "system:admission-controller",
                            "reason": reason,
                            "occurred_at": occurred_at,
                            "trace_context": self._services.codec.dumps({}),
                        }
                    )
                await connection.execute(_INSERT_EXECUTION_EVENT, parameters)
            return
        row = (
            (
                await connection.execute(
                    text(
                        """
                        UPDATE task_runs
                        SET state = 'CANCELLED', version = version + 1,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND id = :resource_id
                          AND state IN ('WAITING', 'RUNNING', 'RETRY_DELAY')
                        RETURNING id, execution_id, task_path, state,
                                  current_attempt, version, retry_at
                        """
                    ),
                    {"tenant_id": tenant_id, "resource_id": resource_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is not None:
            await self._repository._insert_task_event(
                connection,
                tenant_id,
                row,
                new_runtime_id(),
                TaskRunEventType.CANCELLED,
                new_runtime_id(),
                reason=reason,
                payload={"replacementId": str(replacement_id)},
                actor_id="system:admission-controller",
            )

    async def _terminate_denied_task(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        task_run_id: UUID,
        decision: AdmissionDecision,
    ) -> None:
        terminal_state = {
            AdmissionOutcome.CANCELLED: TaskRunState.CANCELLED,
            AdmissionOutcome.FAILED: TaskRunState.FAILED,
            AdmissionOutcome.SKIPPED: TaskRunState.SUCCESS,
        }[decision.outcome]
        event_types = (
            (TaskRunEventType.CANCELLED,)
            if terminal_state is TaskRunState.CANCELLED
            else (
                TaskRunEventType.STARTED,
                TaskRunEventType.FAILED
                if terminal_state is TaskRunState.FAILED
                else TaskRunEventType.SUCCEEDED,
            )
        )
        row = (
            (
                await connection.execute(
                    text(
                        """
                        UPDATE task_runs
                        SET state = :state, version = version + :version_delta,
                            current_attempt = CASE
                                WHEN :version_delta = 2 THEN current_attempt + 1
                                ELSE current_attempt
                            END,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND id = :task_run_id
                          AND state = 'WAITING'
                        RETURNING id, execution_id, task_path, state,
                                  current_attempt, version, retry_at
                        """
                    ),
                    {
                        "tenant_id": tenant_id,
                        "task_run_id": task_run_id,
                        "state": terminal_state.value,
                        "version_delta": len(event_types),
                    },
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return
        correlation_id = new_runtime_id()
        first_sequence = int(row["version"]) - len(event_types) + 1
        for offset, event_type in enumerate(event_types):
            event_row = dict(row)
            event_row["version"] = first_sequence + offset
            await self._repository._insert_task_event(
                connection,
                tenant_id,
                event_row,
                new_runtime_id(),
                event_type,
                correlation_id,
                reason=decision.reason,
                payload={
                    "admissionRequestId": str(decision.request_id),
                    "admissionOutcome": decision.outcome.value,
                    "dispatch": event_type is not TaskRunEventType.STARTED,
                },
                actor_id="system:admission-controller",
            )
