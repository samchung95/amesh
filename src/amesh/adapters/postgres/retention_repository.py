from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.domain.retention import (
    LifecycleBatch,
    LifecycleJob,
    LifecycleJobState,
    LifecycleLegalHold,
    LifecycleLegalHoldDraft,
    LifecycleObjectDecision,
    LifecyclePolicy,
    LifecyclePolicyDraft,
    LifecycleResourceType,
    LifecycleScope,
)
from amesh.ports.errors import LifecycleVersionConflict, NotFoundError
from amesh.ports.retention_repository import RetentionRepository

from .repository_support import PostgresRepositoryBase

_TERMINAL_STATES = "('CANCELLED', 'SUCCESS', 'FAILED', 'WARNING')"


class PostgresRetentionRepository(PostgresRepositoryBase, RetentionRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def list_policies(self, tenant_id: str) -> tuple[LifecyclePolicy, ...]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT policies.*, tenants.slug AS tenant_slug
                            FROM lifecycle_policies AS policies
                            LEFT JOIN tenants ON tenants.id = policies.tenant_id
                            WHERE policies.tenant_id IS NULL OR policies.tenant_id = :tenant_id
                            ORDER BY
                                CASE policies.scope
                                    WHEN 'LABEL' THEN 1 WHEN 'NAMESPACE' THEN 2
                                    WHEN 'TENANT' THEN 3 ELSE 4
                                END,
                                policies.resource_type,
                                policies.updated_at DESC
                            """
                        ),
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_policy(row) for row in rows)

    async def save_policy(
        self,
        tenant_id: str,
        draft: LifecyclePolicyDraft,
        *,
        actor_id: str,
        policy_id: UUID | None = None,
        expected_version: int | None = None,
    ) -> LifecyclePolicy:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            stored_tenant = None if draft.scope is LifecycleScope.INSTANCE else tenant_uuid
            now = await _database_now(connection)
            next_run_at = (
                now + timedelta(minutes=draft.schedule_interval_minutes)
                if draft.schedule_interval_minutes is not None
                else None
            )
            parameters = {
                "id": policy_id or new_runtime_id(),
                "tenant_id": stored_tenant,
                "resource_type": draft.resource_type.value,
                "scope": draft.scope.value,
                "namespace": draft.namespace,
                "labels": self._services.codec.dumps(draft.label_selector),
                "retention_days": draft.retention_days,
                "batch_size": draft.batch_size,
                "schedule_interval_minutes": draft.schedule_interval_minutes,
                "next_run_at": next_run_at,
                "enabled": draft.enabled,
                "reason": draft.reason,
                "actor_id": actor_id,
                "expected_version": expected_version,
            }
            row: RowMapping | None
            if policy_id is None:
                row = (
                    (
                        await connection.execute(
                            text(
                                """
                                INSERT INTO lifecycle_policies (
                                    id, tenant_id, resource_type, scope, namespace_name,
                                    label_selector, retention_days, batch_size,
                                    schedule_interval_minutes, next_run_at, enabled, reason,
                                    created_by, updated_by
                                ) VALUES (
                                    :id, :tenant_id, :resource_type, :scope, :namespace,
                                    CAST(:labels AS jsonb), :retention_days, :batch_size,
                                    :schedule_interval_minutes, :next_run_at, :enabled, :reason,
                                    :actor_id, :actor_id
                                )
                                RETURNING *
                                """
                            ),
                            parameters,
                        )
                    )
                    .mappings()
                    .one()
                )
            else:
                row = (
                    (
                        await connection.execute(
                            text(
                                """
                                UPDATE lifecycle_policies
                                SET tenant_id = :tenant_id,
                                    resource_type = :resource_type,
                                    scope = :scope,
                                    namespace_name = :namespace,
                                    label_selector = CAST(:labels AS jsonb),
                                    retention_days = :retention_days,
                                    batch_size = :batch_size,
                                    schedule_interval_minutes = :schedule_interval_minutes,
                                    next_run_at = :next_run_at,
                                    enabled = :enabled,
                                    reason = :reason,
                                    updated_by = :actor_id,
                                    updated_at = clock_timestamp(),
                                    version = version + 1
                                WHERE id = :id
                                  AND (tenant_id IS NULL OR tenant_id = amesh_current_tenant_id())
                                  AND scope = :scope
                                  AND tenant_id IS NOT DISTINCT FROM :tenant_id
                                  AND (CAST(:expected_version AS integer) IS NULL
                                       OR version = CAST(:expected_version AS integer))
                                RETURNING *
                                """
                            ),
                            parameters,
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if row is None:
                    raise LifecycleVersionConflict(
                        "lifecycle policy version changed or is unavailable"
                    )
            assert row is not None
            await _write_event(
                connection,
                tenant_uuid,
                policy_id=row["id"],
                event_type="LifecyclePolicySaved",
                actor_id=actor_id,
                reason=draft.reason,
                payload={"resourceType": draft.resource_type.value, "scope": draft.scope.value},
            )
            result = dict(row)
            result["tenant_slug"] = None if stored_tenant is None else tenant_id
        return _policy(result)

    async def create_hold(
        self,
        tenant_id: str,
        draft: LifecycleLegalHoldDraft,
        *,
        actor_id: str,
    ) -> LifecycleLegalHold:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO lifecycle_legal_holds (
                                id, tenant_id, name, reason, resource_type, resource_id,
                                namespace_name, label_selector, data_from, data_to, created_by
                            ) VALUES (
                                :id, :tenant_id, :name, :reason, :resource_type, :resource_id,
                                :namespace, CAST(:labels AS jsonb), :data_from, :data_to, :actor_id
                            )
                            RETURNING *
                            """
                        ),
                        {
                            "id": new_runtime_id(),
                            "tenant_id": tenant_uuid,
                            "name": draft.name,
                            "reason": draft.reason,
                            "resource_type": (
                                draft.resource_type.value
                                if draft.resource_type is not None
                                else "ALL"
                            ),
                            "resource_id": draft.resource_id,
                            "namespace": draft.namespace,
                            "labels": self._services.codec.dumps(draft.label_selector),
                            "data_from": draft.data_from,
                            "data_to": draft.data_to,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await _write_event(
                connection,
                tenant_uuid,
                event_type="LifecycleLegalHoldCreated",
                actor_id=actor_id,
                reason=draft.reason,
                payload={"holdId": str(row["id"]), "resourceType": row["resource_type"]},
            )
        return _hold(row, tenant_id)

    async def list_holds(self, tenant_id: str) -> tuple[LifecycleLegalHold, ...]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM lifecycle_legal_holds
                            WHERE tenant_id = :tenant_id
                            ORDER BY active DESC, created_at DESC, id
                            """
                        ),
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_hold(row, tenant_id) for row in rows)

    async def release_hold(
        self,
        tenant_id: str,
        hold_id: UUID,
        *,
        actor_id: str,
    ) -> LifecycleLegalHold:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE lifecycle_legal_holds
                            SET active = false, released_by = :actor_id,
                                released_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND id = :hold_id AND active
                            RETURNING *
                            """
                        ),
                        {"tenant_id": tenant_uuid, "hold_id": hold_id, "actor_id": actor_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise NotFoundError(
                    "active lifecycle legal hold",
                    hold_id,
                    message="active lifecycle legal hold unavailable",
                )
            await _write_event(
                connection,
                tenant_uuid,
                event_type="LifecycleLegalHoldReleased",
                actor_id=actor_id,
                reason=f"released legal hold {hold_id}",
                payload={"holdId": str(hold_id)},
            )
        return _hold(row, tenant_id)

    async def preview(
        self,
        tenant_id: str,
        policy_id: UUID,
        *,
        actor_id: str,
        reason: str,
    ) -> LifecycleJob:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            policy = await _fetch_policy(connection, tenant_uuid, policy_id)
            now = await _database_now(connection)
            cutoff = now - timedelta(days=int(policy["retention_days"]))
            estimates = await _estimate(connection, tenant_uuid, policy, cutoff)
            job_id = new_runtime_id()
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO lifecycle_jobs (
                                id, tenant_id, policy_id, trigger_kind, state, cutoff,
                                policy_snapshot, estimated_records, estimated_bytes,
                                protected_records, active_records, batch_size, reason, actor_id,
                                preview_expires_at
                            ) VALUES (
                                :id, :tenant_id, :policy_id, 'MANUAL', 'PREVIEWED', :cutoff,
                                CAST(:snapshot AS jsonb), :records, :bytes, :protected, :active,
                                :batch_size, :reason, :actor_id, :preview_expires_at
                            )
                            RETURNING *
                            """
                        ),
                        {
                            "id": job_id,
                            "tenant_id": tenant_uuid,
                            "policy_id": policy_id,
                            "cutoff": cutoff,
                            "snapshot": self._services.codec.dumps(
                                _policy_snapshot(policy, tenant_id)
                            ),
                            "records": estimates["records"],
                            "bytes": estimates["bytes"],
                            "protected": estimates["protected"],
                            "active": estimates["active"],
                            "batch_size": policy["batch_size"],
                            "reason": reason,
                            "actor_id": actor_id,
                            "preview_expires_at": now + timedelta(minutes=5),
                        },
                    )
                )
                .mappings()
                .one()
            )
            await _write_event(
                connection,
                tenant_uuid,
                policy_id=policy_id,
                job_id=job_id,
                event_type="LifecyclePurgePreviewed",
                actor_id=actor_id,
                reason=reason,
                payload=estimates,
            )
        return _job(row, tenant_id)

    async def confirm(self, tenant_id: str, job_id: UUID, confirmation: str) -> LifecycleJob:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            current = await _fetch_job(connection, tenant_uuid, job_id, for_update=True)
            expected = _confirmation(int(current["estimated_records"]))
            if current["state"] != LifecycleJobState.PREVIEWED.value:
                raise ValueError("only a previewed lifecycle job can be confirmed")
            now = await _database_now(connection)
            if current["preview_expires_at"] <= now:
                raise ValueError("lifecycle preview expired; generate a new impact preview")
            if confirmation != expected:
                raise ValueError(f"confirmation must exactly match {expected!r}")
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE lifecycle_jobs
                            SET state = 'READY', updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND id = :job_id
                            RETURNING *
                            """
                        ),
                        {"tenant_id": tenant_uuid, "job_id": job_id},
                    )
                )
                .mappings()
                .one()
            )
            await _write_event(
                connection,
                tenant_uuid,
                policy_id=row["policy_id"],
                job_id=job_id,
                event_type="LifecyclePurgeConfirmed",
                actor_id=row["actor_id"],
                reason=row["reason"],
                payload={"confirmation": confirmation},
            )
        return _job(row, tenant_id)

    async def process_batch(self, tenant_id: str, job_id: UUID) -> LifecycleBatch:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            job = await _fetch_job(connection, tenant_uuid, job_id, for_update=True)
            if job["state"] in {
                LifecycleJobState.WAITING_EXTERNAL.value,
                LifecycleJobState.FAILED.value,
            }:
                objects = await _pending_objects(connection, tenant_uuid, job_id, tenant_id)
                return LifecycleBatch(job=_job(job, tenant_id), objects=objects)
            if job["state"] not in {
                LifecycleJobState.READY.value,
                LifecycleJobState.RUNNING.value,
            }:
                raise ValueError("lifecycle job is not ready for batch processing")
            policy = dict(job["policy_snapshot"])
            resource_type = LifecycleResourceType(policy["resourceType"])
            started_at = job["started_at"] or await _database_now(connection)
            await connection.execute(
                text(
                    """
                    UPDATE lifecycle_jobs SET state = 'RUNNING', started_at = :started_at,
                        updated_at = clock_timestamp(), last_error = NULL
                    WHERE id = :job_id AND tenant_id = :tenant_id
                    """
                ),
                {"job_id": job_id, "tenant_id": tenant_uuid, "started_at": started_at},
            )
            candidates = await _select_candidates(
                connection,
                tenant_uuid,
                policy,
                job["cutoff"],
                int(job["batch_size"]),
            )
            processed, processed_bytes = await _purge_candidates(
                connection,
                tenant_uuid,
                job_id,
                resource_type,
                candidates,
            )
            remaining = await _has_candidates(connection, tenant_uuid, policy, job["cutoff"])
            pending = await _pending_objects(connection, tenant_uuid, job_id, tenant_id)
            if pending:
                state = LifecycleJobState.WAITING_EXTERNAL.value
            elif remaining:
                state = LifecycleJobState.READY.value
            else:
                state = LifecycleJobState.SUCCEEDED.value
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE lifecycle_jobs
                            SET state = :state,
                                processed_records = processed_records + :processed,
                                processed_bytes = processed_bytes + :processed_bytes,
                                cursor = :cursor,
                                completed_at = CASE WHEN :state = 'SUCCEEDED'
                                    THEN clock_timestamp() ELSE NULL END,
                                evidence = evidence || CAST(:evidence AS jsonb),
                                updated_at = clock_timestamp()
                            WHERE id = :job_id AND tenant_id = :tenant_id
                            RETURNING *
                            """
                        ),
                        {
                            "state": state,
                            "processed": processed,
                            "processed_bytes": processed_bytes,
                            "cursor": str(candidates[-1]["record_id"])
                            if candidates
                            else job["cursor"],
                            "evidence": self._services.codec.dumps(
                                {
                                    "lastBatchRecords": processed,
                                    "lastBatchBytes": processed_bytes,
                                    "authoritativeDecisionCommitted": True,
                                    "searchProjectionRemovedAfterDecision": True,
                                }
                            ),
                            "job_id": job_id,
                            "tenant_id": tenant_uuid,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await _write_event(
                connection,
                tenant_uuid,
                policy_id=row["policy_id"],
                job_id=job_id,
                event_type=(
                    "LifecyclePurgeCompleted"
                    if state == "SUCCEEDED"
                    else "LifecyclePurgeBatchCommitted"
                ),
                actor_id=row["actor_id"],
                reason=row["reason"],
                payload={"records": processed, "bytes": processed_bytes, "state": state},
            )
        return LifecycleBatch(job=_job(row, tenant_id), objects=pending)

    async def record_object_result(
        self,
        tenant_id: str,
        job_id: UUID,
        ordinal: int,
        *,
        error: str | None,
    ) -> None:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                text(
                    """
                    UPDATE lifecycle_job_items
                    SET state = CASE WHEN CAST(:error AS text) IS NULL
                            THEN 'DELETED' ELSE 'FAILED' END,
                        attempts = attempts + 1,
                        last_error = CAST(:error AS text),
                        completed_at = CASE WHEN CAST(:error AS text) IS NULL
                            THEN clock_timestamp() ELSE NULL END
                    WHERE tenant_id = :tenant_id AND job_id = :job_id AND ordinal = :ordinal
                      AND state IN ('PENDING_EXTERNAL', 'FAILED')
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "job_id": job_id,
                    "ordinal": ordinal,
                    "error": error,
                },
            )
            if result.rowcount != 1:
                raise NotFoundError(
                    "pending lifecycle object decision",
                    f"{job_id}:{ordinal}",
                    message="pending lifecycle object decision unavailable",
                )

    async def finish_external(self, tenant_id: str, job_id: UUID) -> LifecycleJob:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            job = await _fetch_job(connection, tenant_uuid, job_id, for_update=True)
            failures = int(
                await connection.scalar(
                    text(
                        """
                        SELECT count(*) FROM lifecycle_job_items
                        WHERE tenant_id = :tenant_id AND job_id = :job_id AND state = 'FAILED'
                        """
                    ),
                    {"tenant_id": tenant_uuid, "job_id": job_id},
                )
                or 0
            )
            policy = dict(job["policy_snapshot"])
            remaining = await _has_candidates(connection, tenant_uuid, policy, job["cutoff"])
            state = "FAILED" if failures else ("READY" if remaining else "SUCCEEDED")
            last_error = f"{failures} object deletion(s) require retry" if failures else None
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE lifecycle_jobs
                            SET state = :state,
                                retry_count = retry_count + CASE WHEN :failures > 0 THEN 1 ELSE 0 END,
                                last_error = :last_error,
                                completed_at = CASE WHEN :state = 'SUCCEEDED'
                                    THEN clock_timestamp() ELSE NULL END,
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND id = :job_id
                            RETURNING *
                            """
                        ),
                        {
                            "state": state,
                            "failures": failures,
                            "last_error": last_error,
                            "tenant_id": tenant_uuid,
                            "job_id": job_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await _write_event(
                connection,
                tenant_uuid,
                policy_id=row["policy_id"],
                job_id=job_id,
                event_type=(
                    "LifecyclePurgeObjectRetryRequired"
                    if failures
                    else "LifecyclePurgeExternalDeletesCompleted"
                ),
                actor_id=row["actor_id"],
                reason=row["reason"],
                payload={"failures": failures, "state": state},
            )
        return _job(row, tenant_id)

    async def get_job(self, tenant_id: str, job_id: UUID) -> LifecycleJob:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = await _fetch_job(connection, tenant_uuid, job_id)
        return _job(row, tenant_id)

    async def list_jobs(self, tenant_id: str, *, limit: int = 50) -> tuple[LifecycleJob, ...]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM lifecycle_jobs
                            WHERE tenant_id = :tenant_id
                            ORDER BY created_at DESC, id
                            LIMIT :limit
                            """
                        ),
                        {"tenant_id": tenant_uuid, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_job(row, tenant_id) for row in rows)

    async def create_due_jobs(self, tenant_id: str) -> tuple[LifecycleJob, ...]:
        created: list[LifecycleJob] = []
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            due = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT policies.*
                            FROM lifecycle_policies AS policies
                            WHERE policies.enabled
                              AND policies.schedule_interval_minutes IS NOT NULL
                              AND policies.next_run_at <= clock_timestamp()
                              AND (policies.tenant_id IS NULL OR policies.tenant_id = :tenant_id)
                              AND NOT EXISTS (
                                  SELECT 1 FROM lifecycle_jobs AS jobs
                                  WHERE jobs.tenant_id = :tenant_id
                                    AND jobs.policy_id = policies.id
                                    AND jobs.state IN ('READY', 'RUNNING', 'WAITING_EXTERNAL')
                              )
                            ORDER BY policies.next_run_at, policies.id
                            FOR UPDATE OF policies SKIP LOCKED
                            """
                        ),
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
            now = await _database_now(connection)
            for policy in due:
                cutoff = now - timedelta(days=int(policy["retention_days"]))
                estimates = await _estimate(connection, tenant_uuid, policy, cutoff)
                job_id = new_runtime_id()
                row = (
                    (
                        await connection.execute(
                            text(
                                """
                                INSERT INTO lifecycle_jobs (
                                    id, tenant_id, policy_id, trigger_kind, state, cutoff,
                                    policy_snapshot, estimated_records, estimated_bytes,
                                    protected_records, active_records, batch_size, reason, actor_id,
                                    preview_expires_at
                                ) VALUES (
                                    :id, :tenant_id, :policy_id, 'SCHEDULED', 'READY', :cutoff,
                                    CAST(:snapshot AS jsonb), :records, :bytes, :protected, :active,
                                    :batch_size, :reason, 'system:maintenance', :now
                                )
                                RETURNING *
                                """
                            ),
                            {
                                "id": job_id,
                                "tenant_id": tenant_uuid,
                                "policy_id": policy["id"],
                                "cutoff": cutoff,
                                "snapshot": self._services.codec.dumps(
                                    _policy_snapshot(policy, tenant_id)
                                ),
                                "records": estimates["records"],
                                "bytes": estimates["bytes"],
                                "protected": estimates["protected"],
                                "active": estimates["active"],
                                "batch_size": policy["batch_size"],
                                "reason": f"scheduled lifecycle policy {policy['id']}",
                                "now": now,
                            },
                        )
                    )
                    .mappings()
                    .one()
                )
                await connection.execute(
                    text(
                        """
                        UPDATE lifecycle_policies
                        SET next_run_at = :next_run_at, updated_at = clock_timestamp()
                        WHERE id = :policy_id
                        """
                    ),
                    {
                        "policy_id": policy["id"],
                        "next_run_at": now
                        + timedelta(minutes=int(policy["schedule_interval_minutes"])),
                    },
                )
                await _write_event(
                    connection,
                    tenant_uuid,
                    policy_id=policy["id"],
                    job_id=job_id,
                    event_type="LifecyclePurgeScheduled",
                    actor_id="system:maintenance",
                    reason=row["reason"],
                    payload=estimates,
                )
                created.append(_job(row, tenant_id))
        return tuple(created)


async def _fetch_policy(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    policy_id: UUID,
) -> RowMapping:
    row = (
        (
            await connection.execute(
                text(
                    """
                    SELECT * FROM lifecycle_policies
                    WHERE id = :policy_id AND enabled
                      AND (tenant_id IS NULL OR tenant_id = :tenant_id)
                    """
                ),
                {"policy_id": policy_id, "tenant_id": tenant_uuid},
            )
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise NotFoundError(
            "enabled lifecycle policy",
            policy_id,
            message="enabled lifecycle policy unavailable",
        )
    return row


async def _fetch_job(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    job_id: UUID,
    *,
    for_update: bool = False,
) -> RowMapping:
    row = (
        (
            await connection.execute(
                text(
                    "SELECT * FROM lifecycle_jobs WHERE tenant_id = :tenant_id AND id = :job_id"
                    + (" FOR UPDATE" if for_update else "")
                ),
                {"tenant_id": tenant_uuid, "job_id": job_id},
            )
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise NotFoundError(
            "lifecycle job",
            job_id,
            message="lifecycle job unavailable",
        )
    return row


def _scope_sql(
    policy: RowMapping | dict[str, Any], execution_alias: str, namespace_sql: str
) -> str:
    scope = str(policy["scope"])
    if scope in {LifecycleScope.INSTANCE.value, LifecycleScope.TENANT.value}:
        return "TRUE"
    if scope == LifecycleScope.NAMESPACE.value:
        return f"{namespace_sql} = :namespace"
    return f"{execution_alias}.labels @> CAST(:label_selector AS jsonb)"


def _retention_eligibility_sql(timestamp_sql: str, execution_alias: str) -> str:
    """Apply session-policy retention from terminal time within lifecycle selection."""

    context = f"COALESCE({execution_alias}.trigger_context, '{{}}'::jsonb)"
    session_policy = (
        f"({context} ? 'ameshAgentSessionId' "
        f"AND jsonb_array_length(COALESCE({context}->'ameshAgentSessionPolicy'->'policies', "
        "'[]'::jsonb)) > 0)"
    )
    session_expiry = (
        f"COALESCE({execution_alias}.terminal_at, {execution_alias}.created_at) "
        f"+ make_interval(secs => (({context}->'ameshAgentSessionPolicy'->>'retentionSeconds')::double precision))"
    )
    return f"(({session_policy} AND clock_timestamp() >= {session_expiry}) OR (NOT {session_policy} AND {timestamp_sql} < :cutoff))"


def _hold_sql(
    resource_type: LifecycleResourceType,
    *,
    resource_id_sql: str,
    occurred_at_sql: str,
    execution_alias: str,
    namespace_sql: str,
) -> str:
    return f"""
        EXISTS (
            SELECT 1 FROM lifecycle_legal_holds AS holds
            WHERE holds.tenant_id = :tenant_id AND holds.active
              AND holds.resource_type IN ('ALL', '{resource_type.value}')
              AND (holds.resource_id IS NULL OR holds.resource_id IN (
                    {resource_id_sql}, {execution_alias}.id::text
              ))
              AND (holds.namespace_name IS NULL OR holds.namespace_name = {namespace_sql})
              AND (holds.label_selector = '{{}}'::jsonb
                   OR {execution_alias}.labels @> holds.label_selector)
              AND (holds.data_from IS NULL OR {occurred_at_sql} >= holds.data_from)
              AND (holds.data_to IS NULL OR {occurred_at_sql} < holds.data_to)
        )
    """


def _precedence_sql(
    policy: RowMapping | dict[str, Any],
    *,
    execution_alias: str,
    namespace_sql: str,
) -> str:
    current_rank = {
        LifecycleScope.INSTANCE.value: 1,
        LifecycleScope.TENANT.value: 2,
        LifecycleScope.NAMESPACE.value: 3,
        LifecycleScope.LABEL.value: 4,
    }[str(policy["scope"])]
    return f"""
        NOT EXISTS (
            SELECT 1 FROM lifecycle_policies AS overrides
            WHERE overrides.enabled
              AND overrides.id <> CAST(:policy_id AS uuid)
              AND overrides.resource_type = :resource_type
              AND (overrides.tenant_id IS NULL OR overrides.tenant_id = :tenant_id)
              AND (
                    overrides.scope = 'INSTANCE'
                    OR (overrides.scope = 'TENANT' AND overrides.tenant_id = :tenant_id)
                    OR (overrides.scope = 'NAMESPACE'
                        AND overrides.tenant_id = :tenant_id
                        AND overrides.namespace_name = {namespace_sql})
                    OR (overrides.scope = 'LABEL'
                        AND overrides.tenant_id = :tenant_id
                        AND {execution_alias}.labels @> overrides.label_selector)
              )
              AND (
                    CASE overrides.scope
                        WHEN 'LABEL' THEN 4 WHEN 'NAMESPACE' THEN 3
                        WHEN 'TENANT' THEN 2 ELSE 1
                    END > {current_rank}
                    OR (
                        CASE overrides.scope
                            WHEN 'LABEL' THEN 4 WHEN 'NAMESPACE' THEN 3
                            WHEN 'TENANT' THEN 2 ELSE 1
                        END = {current_rank}
                        AND overrides.retention_days > :retention_days
                    )
              )
        )
    """


def _candidate_source(policy: RowMapping | dict[str, Any]) -> tuple[str, dict[str, Any]]:
    resource_type = LifecycleResourceType(
        str(policy["resource_type"] if "resource_type" in policy else policy["resourceType"])
    )
    parameters = {
        "policy_id": str(policy["id"]),
        "resource_type": resource_type.value,
        "retention_days": int(
            policy["retention_days"] if "retention_days" in policy else policy["retentionDays"]
        ),
        "namespace": policy.get("namespace_name", policy.get("namespace")),
        "label_selector": json.dumps(policy.get("label_selector", policy.get("labelSelector", {}))),
    }
    if resource_type is LifecycleResourceType.EXECUTION:
        scope = _scope_sql(policy, "executions", "executions.namespace_name")
        held = _hold_sql(
            resource_type,
            resource_id_sql="executions.id::text",
            occurred_at_sql="executions.created_at",
            execution_alias="executions",
            namespace_sql="executions.namespace_name",
        )
        precedence = _precedence_sql(
            policy,
            execution_alias="executions",
            namespace_sql="executions.namespace_name",
        )
        source = f"""
            SELECT executions.id AS record_id,
                   pg_column_size(executions)::bigint AS size_bytes,
                   executions.terminal_at IS NULL OR executions.state NOT IN {_TERMINAL_STATES} AS active,
                   {held} AS held
            FROM executions
            WHERE executions.tenant_id = :tenant_id
              AND {_retention_eligibility_sql("executions.created_at", "executions")}
              AND executions.lifecycle <> 'TOMBSTONED'
              AND {scope}
              AND {precedence}
        """
        return source, parameters

    table, id_column, occurred_column, size_sql = {
        LifecycleResourceType.LOG: (
            "execution_logs",
            "id",
            "occurred_at",
            "pg_column_size(records)::bigint",
        ),
        LifecycleResourceType.METRIC: (
            "execution_metrics",
            "id",
            "occurred_at",
            "pg_column_size(records)::bigint",
        ),
        LifecycleResourceType.ARTIFACT: (
            "execution_artifacts",
            "id",
            "occurred_at",
            "(pg_column_size(records) + records.size_bytes)::bigint",
        ),
        LifecycleResourceType.CACHE: (
            "task_cache_entries",
            "entry_id",
            "updated_at",
            "pg_column_size(records)::bigint",
        ),
    }[resource_type]
    if resource_type is LifecycleResourceType.CACHE:
        execution_join = "LEFT JOIN executions ON executions.id = records.source_execution_id AND executions.tenant_id = records.tenant_id"
        namespace_sql = "records.namespace_name"
        active_sql = "records.state = 'POPULATING' OR (executions.id IS NOT NULL AND executions.terminal_at IS NULL)"
        execution_id_sql = "COALESCE(executions.id::text, records.entry_id::text)"
    else:
        execution_join = "JOIN executions ON executions.id = records.execution_id AND executions.tenant_id = records.tenant_id"
        namespace_sql = "executions.namespace_name"
        active_sql = f"executions.terminal_at IS NULL OR executions.state NOT IN {_TERMINAL_STATES}"
        execution_id_sql = f"records.{id_column}::text"
    scope = _scope_sql(policy, "executions", namespace_sql)
    held = _hold_sql(
        resource_type,
        resource_id_sql=f"records.{id_column}::text",
        occurred_at_sql=f"records.{occurred_column}",
        execution_alias="executions",
        namespace_sql=namespace_sql,
    )
    precedence = _precedence_sql(
        policy,
        execution_alias="executions",
        namespace_sql=namespace_sql,
    )
    source = f"""
        SELECT records.{id_column} AS record_id,
               {size_sql} AS size_bytes,
               {active_sql} AS active,
               {held} AS held
        FROM {table} AS records
        {execution_join}
        WHERE records.tenant_id = :tenant_id
          AND {_retention_eligibility_sql(f"records.{occurred_column}", "executions")}
          AND {scope}
          AND {precedence}
    """
    del execution_id_sql
    return source, parameters


async def _estimate(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    policy: RowMapping | dict[str, Any],
    cutoff: datetime,
) -> dict[str, int]:
    source, parameters = _candidate_source(policy)
    resource_value = str(
        policy["resource_type"] if "resource_type" in policy else policy["resourceType"]
    )
    if resource_value == LifecycleResourceType.EXECUTION.value:
        row = (
            (
                await connection.execute(
                    text(
                        f"""
                        WITH candidates AS ({source}),
                        eligible AS (
                            SELECT record_id FROM candidates WHERE NOT active AND NOT held
                        ),
                        affected AS (
                            SELECT pg_column_size(executions)::bigint AS size_bytes
                            FROM executions JOIN eligible ON eligible.record_id = executions.id
                            UNION ALL
                            SELECT pg_column_size(task_runs)::bigint FROM task_runs
                            JOIN eligible ON eligible.record_id = task_runs.execution_id
                            UNION ALL
                            SELECT pg_column_size(task_attempts)::bigint FROM task_attempts
                            JOIN task_runs ON task_runs.id = task_attempts.task_run_id
                            JOIN eligible ON eligible.record_id = task_runs.execution_id
                            UNION ALL
                            SELECT pg_column_size(execution_events)::bigint FROM execution_events
                            JOIN eligible ON eligible.record_id = execution_events.execution_id
                            UNION ALL
                            SELECT pg_column_size(task_run_events)::bigint FROM task_run_events
                            JOIN eligible ON eligible.record_id = task_run_events.execution_id
                            UNION ALL
                            SELECT pg_column_size(execution_logs)::bigint FROM execution_logs
                            JOIN eligible ON eligible.record_id = execution_logs.execution_id
                            UNION ALL
                            SELECT pg_column_size(execution_metrics)::bigint FROM execution_metrics
                            JOIN eligible ON eligible.record_id = execution_metrics.execution_id
                            UNION ALL
                            SELECT (pg_column_size(execution_artifacts) + size_bytes)::bigint
                            FROM execution_artifacts
                            JOIN eligible ON eligible.record_id = execution_artifacts.execution_id
                            UNION ALL
                            SELECT (pg_column_size(execution_outputs) + size_bytes)::bigint
                            FROM execution_outputs
                            JOIN eligible ON eligible.record_id = execution_outputs.execution_id
                            UNION ALL
                            SELECT pg_column_size(execution_evidence_events)::bigint
                            FROM execution_evidence_events
                            JOIN eligible ON eligible.record_id = execution_evidence_events.execution_id
                            UNION ALL
                            SELECT pg_column_size(task_cache_entries)::bigint FROM task_cache_entries
                            JOIN eligible ON eligible.record_id = task_cache_entries.source_execution_id
                            WHERE task_cache_entries.state <> 'POPULATING'
                            UNION ALL
                            SELECT pg_column_size(search_documents)::bigint FROM search_documents
                            JOIN eligible ON search_documents.document_id = eligible.record_id::text
                            WHERE search_documents.document_type = 'EXECUTION'
                            UNION ALL
                            SELECT pg_column_size(search_documents_v2)::bigint FROM search_documents_v2
                            JOIN eligible ON search_documents_v2.document_id = eligible.record_id::text
                            WHERE search_documents_v2.document_type = 'EXECUTION'
                        )
                        SELECT (SELECT count(*) FROM affected) AS records,
                               COALESCE((SELECT sum(size_bytes) FROM affected), 0) AS bytes,
                               count(*) FILTER (WHERE held) AS protected,
                               count(*) FILTER (WHERE active) AS active
                        FROM candidates
                        """
                    ),
                    {"tenant_id": tenant_uuid, "cutoff": cutoff, **parameters},
                )
            )
            .mappings()
            .one()
        )
        return {name: int(row[name] or 0) for name in ("records", "bytes", "protected", "active")}
    row = (
        (
            await connection.execute(
                text(
                    f"""
                    WITH candidates AS ({source})
                    SELECT count(*) FILTER (WHERE NOT active AND NOT held) AS records,
                           COALESCE(sum(size_bytes) FILTER (WHERE NOT active AND NOT held), 0) AS bytes,
                           count(*) FILTER (WHERE held) AS protected,
                           count(*) FILTER (WHERE active) AS active
                    FROM candidates
                    """
                ),
                {"tenant_id": tenant_uuid, "cutoff": cutoff, **parameters},
            )
        )
        .mappings()
        .one()
    )
    return {name: int(row[name] or 0) for name in ("records", "bytes", "protected", "active")}


async def _select_candidates(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    policy: dict[str, Any],
    cutoff: datetime,
    limit: int,
) -> list[RowMapping]:
    source, parameters = _candidate_source(policy)
    return list(
        (
            await connection.execute(
                text(
                    f"""
                    WITH candidates AS ({source})
                    SELECT record_id, size_bytes
                    FROM candidates
                    WHERE NOT active AND NOT held
                    ORDER BY record_id
                    LIMIT :limit
                    """
                ),
                {"tenant_id": tenant_uuid, "cutoff": cutoff, "limit": limit, **parameters},
            )
        )
        .mappings()
        .all()
    )


async def _has_candidates(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    policy: dict[str, Any],
    cutoff: datetime,
) -> bool:
    source, parameters = _candidate_source(policy)
    return bool(
        await connection.scalar(
            text(
                f"""
                WITH candidates AS ({source})
                SELECT EXISTS(SELECT 1 FROM candidates WHERE NOT active AND NOT held)
                """
            ),
            {"tenant_id": tenant_uuid, "cutoff": cutoff, **parameters},
        )
    )


async def _purge_candidates(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    job_id: UUID,
    resource_type: LifecycleResourceType,
    candidates: list[RowMapping],
) -> tuple[int, int]:
    if not candidates:
        return 0, 0
    ids = [row["record_id"] for row in candidates]
    selected_bytes = sum(int(row["size_bytes"]) for row in candidates)
    if resource_type is LifecycleResourceType.EXECUTION:
        return await _purge_executions(connection, tenant_uuid, job_id, ids, selected_bytes)
    if resource_type is LifecycleResourceType.ARTIFACT:
        await _queue_artifact_objects(connection, tenant_uuid, job_id, ids)
        for table in ("asset_lineage_edges", "asset_observations"):
            await connection.execute(
                text(
                    f"DELETE FROM {table} WHERE tenant_id = :tenant_id "
                    "AND artifact_id = ANY(CAST(:ids AS uuid[]))"
                ),
                {"tenant_id": tenant_uuid, "ids": ids},
            )
    table, id_column, search_type, evidence_kind = {
        LifecycleResourceType.LOG: ("execution_logs", "id", "LOG", "LOG"),
        LifecycleResourceType.METRIC: ("execution_metrics", "id", None, "METRIC"),
        LifecycleResourceType.ARTIFACT: ("execution_artifacts", "id", None, "ARTIFACT"),
        LifecycleResourceType.CACHE: ("task_cache_entries", "entry_id", None, None),
    }[resource_type]
    if evidence_kind is not None:
        await connection.execute(
            text(
                """
                DELETE FROM execution_evidence_events
                WHERE tenant_id = :tenant_id AND kind = :kind
                  AND event_id = ANY(CAST(:ids AS uuid[]))
                """
            ),
            {"tenant_id": tenant_uuid, "kind": evidence_kind, "ids": ids},
        )
    if resource_type is LifecycleResourceType.CACHE:
        await connection.execute(
            text(
                """
                DELETE FROM task_cache_events
                WHERE tenant_id = :tenant_id AND entry_id = ANY(CAST(:ids AS uuid[]))
                """
            ),
            {"tenant_id": tenant_uuid, "ids": ids},
        )
    deleted = await _delete_count(
        connection,
        f"DELETE FROM {table} WHERE tenant_id = :tenant_id AND {id_column} = ANY(CAST(:ids AS uuid[])) RETURNING {id_column}",
        {"tenant_id": tenant_uuid, "ids": ids},
    )
    if search_type is not None:
        deleted += await _delete_search_documents(
            connection, tenant_uuid, search_type, [str(item) for item in ids]
        )
    for resource_id in ids:
        await _insert_item(
            connection,
            tenant_uuid,
            job_id,
            resource_type.value,
            str(resource_id),
            state="PURGED",
        )
    return deleted, selected_bytes


async def _purge_executions(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    job_id: UUID,
    execution_ids: list[UUID],
    selected_bytes: int,
) -> tuple[int, int]:
    artifacts = (
        (
            await connection.execute(
                text(
                    """
                    SELECT id, execution_id, uri, size_bytes
                    FROM execution_artifacts
                    WHERE tenant_id = :tenant_id
                      AND execution_id = ANY(CAST(:ids AS uuid[]))
                    ORDER BY id
                    """
                ),
                {"tenant_id": tenant_uuid, "ids": execution_ids},
            )
        )
        .mappings()
        .all()
    )
    for artifact in artifacts:
        await _insert_item(
            connection,
            tenant_uuid,
            job_id,
            "OBJECT",
            str(artifact["id"]),
            execution_id=artifact["execution_id"],
            object_uri=str(artifact["uri"]),
            size_bytes=int(artifact["size_bytes"]),
            state="PENDING_EXTERNAL",
        )
    affected = 0
    parameters = {"tenant_id": tenant_uuid, "ids": execution_ids}
    for table in (
        "execution_logs",
        "execution_metrics",
        "asset_lineage_edges",
        "asset_observations",
        "execution_artifacts",
        "execution_outputs",
        "execution_evidence_events",
        "task_run_events",
        "execution_events",
        "task_attempts",
    ):
        column = "execution_id" if table != "task_attempts" else "task_run_id"
        if table == "task_attempts":
            statement = """
                DELETE FROM task_attempts
                WHERE tenant_id = :tenant_id AND task_run_id IN (
                    SELECT id FROM task_runs
                    WHERE tenant_id = :tenant_id AND execution_id = ANY(CAST(:ids AS uuid[]))
                ) RETURNING id
            """
        else:
            statement = (
                f"DELETE FROM {table} WHERE tenant_id = :tenant_id "
                f"AND {column} = ANY(CAST(:ids AS uuid[])) RETURNING 1"
            )
        affected += await _delete_count(connection, statement, parameters)
    cache_ids = (
        (
            await connection.execute(
                text(
                    """
                SELECT entry_id FROM task_cache_entries
                WHERE tenant_id = :tenant_id
                  AND source_execution_id = ANY(CAST(:ids AS uuid[]))
                  AND state <> 'POPULATING'
                """
                ),
                parameters,
            )
        )
        .scalars()
        .all()
    )
    if cache_ids:
        await connection.execute(
            text(
                """
                DELETE FROM task_cache_events
                WHERE tenant_id = :tenant_id AND entry_id = ANY(CAST(:cache_ids AS uuid[]))
                """
            ),
            {"tenant_id": tenant_uuid, "cache_ids": list(cache_ids)},
        )
    affected += await _delete_count(
        connection,
        """
        DELETE FROM task_cache_entries
        WHERE tenant_id = :tenant_id AND source_execution_id = ANY(CAST(:ids AS uuid[]))
          AND state <> 'POPULATING'
        RETURNING entry_id
        """,
        parameters,
    )
    task_runs = await connection.execute(
        text(
            """
            UPDATE task_runs
            SET terminal_result = '{}'::jsonb, control_evidence = '{}'::jsonb,
                labels = '{}'::jsonb, updated_at = clock_timestamp(), version = version + 1
            WHERE tenant_id = :tenant_id AND execution_id = ANY(CAST(:ids AS uuid[]))
            """
        ),
        parameters,
    )
    affected += int(task_runs.rowcount or 0)
    executions = await connection.execute(
        text(
            """
            UPDATE executions
            SET lifecycle = 'TOMBSTONED', deleted_at = clock_timestamp(),
                inputs = '{}'::jsonb, outputs = '{}'::jsonb, labels = '{}'::jsonb,
                annotations = '{}'::jsonb, lifecycle_evidence = '{}'::jsonb,
                updated_by = 'system:lifecycle', updated_at = clock_timestamp(),
                version = version + 1
            WHERE tenant_id = :tenant_id AND id = ANY(CAST(:ids AS uuid[]))
              AND terminal_at IS NOT NULL AND lifecycle <> 'TOMBSTONED'
            """
        ),
        parameters,
    )
    affected += int(executions.rowcount or 0)
    affected += await _delete_search_documents(
        connection,
        tenant_uuid,
        "EXECUTION",
        [str(item) for item in execution_ids],
    )
    for execution_id in execution_ids:
        await _insert_item(
            connection,
            tenant_uuid,
            job_id,
            LifecycleResourceType.EXECUTION.value,
            str(execution_id),
            execution_id=execution_id,
            state="PURGED",
        )
    return affected, selected_bytes + sum(int(item["size_bytes"]) for item in artifacts)


async def _queue_artifact_objects(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    job_id: UUID,
    artifact_ids: list[UUID],
) -> None:
    rows = (
        (
            await connection.execute(
                text(
                    """
                    SELECT id, execution_id, uri, size_bytes FROM execution_artifacts
                    WHERE tenant_id = :tenant_id AND id = ANY(CAST(:ids AS uuid[]))
                    ORDER BY id
                    """
                ),
                {"tenant_id": tenant_uuid, "ids": artifact_ids},
            )
        )
        .mappings()
        .all()
    )
    for row in rows:
        await _insert_item(
            connection,
            tenant_uuid,
            job_id,
            "OBJECT",
            str(row["id"]),
            execution_id=row["execution_id"],
            object_uri=str(row["uri"]),
            size_bytes=int(row["size_bytes"]),
            state="PENDING_EXTERNAL",
        )


async def _delete_search_documents(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    document_type: str,
    document_ids: list[str],
) -> int:
    parameters = {
        "tenant_id": tenant_uuid,
        "document_type": document_type,
        "document_ids": document_ids,
    }
    legacy = await connection.execute(
        text(
            """
            DELETE FROM search_documents
            WHERE tenant_id = :tenant_id AND document_type = :document_type
              AND document_id = ANY(CAST(:document_ids AS text[]))
            """
        ),
        parameters,
    )
    current = await connection.execute(
        text(
            """
            DELETE FROM search_documents_v2
            WHERE tenant_id = :tenant_id AND document_type = :document_type
              AND document_id = ANY(CAST(:document_ids AS text[]))
            """
        ),
        parameters,
    )
    return int(legacy.rowcount or 0) + int(current.rowcount or 0)


async def _delete_count(
    connection: AsyncConnection,
    statement: str,
    parameters: dict[str, Any],
) -> int:
    rows = (await connection.execute(text(statement), parameters)).all()
    return len(rows)


async def _insert_item(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    job_id: UUID,
    resource_type: str,
    resource_id: str,
    *,
    execution_id: UUID | None = None,
    object_uri: str | None = None,
    size_bytes: int = 0,
    state: str,
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO lifecycle_job_items (
                job_id, tenant_id, resource_type, resource_id, execution_id,
                object_uri, size_bytes, state, completed_at
            ) VALUES (
                :job_id, :tenant_id, :resource_type, :resource_id, :execution_id,
                :object_uri, :size_bytes, :state,
                CASE WHEN :state = 'PURGED' THEN clock_timestamp() ELSE NULL END
            )
            ON CONFLICT (job_id, resource_type, resource_id) DO NOTHING
            """
        ),
        {
            "job_id": job_id,
            "tenant_id": tenant_uuid,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "execution_id": execution_id,
            "object_uri": object_uri,
            "size_bytes": size_bytes,
            "state": state,
        },
    )


async def _pending_objects(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    job_id: UUID,
    tenant_id: str,
) -> tuple[LifecycleObjectDecision, ...]:
    rows = (
        (
            await connection.execute(
                text(
                    """
                    SELECT job_id, ordinal, object_uri, size_bytes
                    FROM lifecycle_job_items
                    WHERE tenant_id = :tenant_id AND job_id = :job_id
                      AND state IN ('PENDING_EXTERNAL', 'FAILED')
                    ORDER BY ordinal
                    """
                ),
                {"tenant_id": tenant_uuid, "job_id": job_id},
            )
        )
        .mappings()
        .all()
    )
    return tuple(
        LifecycleObjectDecision(
            job_id=row["job_id"],
            ordinal=row["ordinal"],
            tenant_id=tenant_id,
            uri=row["object_uri"],
            size_bytes=row["size_bytes"],
        )
        for row in rows
    )


async def _write_event(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    *,
    event_type: str,
    actor_id: str,
    reason: str,
    payload: dict[str, Any],
    policy_id: UUID | None = None,
    job_id: UUID | None = None,
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO lifecycle_events (
                event_id, tenant_id, policy_id, job_id, event_type, actor_id, reason, payload
            ) VALUES (
                :event_id, :tenant_id, :policy_id, :job_id, :event_type,
                :actor_id, :reason, CAST(:payload AS jsonb)
            )
            """
        ),
        {
            "event_id": new_runtime_id(),
            "tenant_id": tenant_uuid,
            "policy_id": policy_id,
            "job_id": job_id,
            "event_type": event_type,
            "actor_id": actor_id,
            "reason": reason,
            "payload": json.dumps(payload),
        },
    )


async def _database_now(connection: AsyncConnection) -> datetime:
    value = await connection.scalar(text("SELECT clock_timestamp()"))
    if not isinstance(value, datetime):
        raise TypeError("PostgreSQL returned an invalid database timestamp")
    return value


def _policy(row: RowMapping | dict[str, Any]) -> LifecyclePolicy:
    return LifecyclePolicy(
        id=row["id"],
        tenantId=row.get("tenant_slug"),
        resourceType=row["resource_type"],
        scope=row["scope"],
        namespace=row["namespace_name"],
        labelSelector=dict(row["label_selector"]),
        retentionDays=row["retention_days"],
        batchSize=row["batch_size"],
        scheduleIntervalMinutes=row["schedule_interval_minutes"],
        nextRunAt=row["next_run_at"],
        enabled=row["enabled"],
        reason=row["reason"],
        createdBy=row["created_by"],
        createdAt=row["created_at"],
        updatedBy=row["updated_by"],
        updatedAt=row["updated_at"],
        version=row["version"],
    )


def _hold(row: RowMapping | dict[str, Any], tenant_id: str) -> LifecycleLegalHold:
    return LifecycleLegalHold(
        id=row["id"],
        tenantId=tenant_id,
        name=row["name"],
        reason=row["reason"],
        resourceType=None if row["resource_type"] == "ALL" else row["resource_type"],
        resourceId=row["resource_id"],
        namespace=row["namespace_name"],
        labelSelector=dict(row["label_selector"]),
        dataFrom=row["data_from"],
        dataTo=row["data_to"],
        active=row["active"],
        createdBy=row["created_by"],
        createdAt=row["created_at"],
        releasedBy=row["released_by"],
        releasedAt=row["released_at"],
    )


def _job(row: RowMapping | dict[str, Any], tenant_id: str) -> LifecycleJob:
    records = int(row["estimated_records"])
    return LifecycleJob(
        id=row["id"],
        tenantId=tenant_id,
        policyId=row["policy_id"],
        trigger=row["trigger_kind"],
        state=row["state"],
        cutoff=row["cutoff"],
        policySnapshot=dict(row["policy_snapshot"]),
        estimatedRecords=records,
        estimatedBytes=row["estimated_bytes"],
        protectedRecords=row["protected_records"],
        activeRecords=row["active_records"],
        processedRecords=row["processed_records"],
        processedBytes=row["processed_bytes"],
        batchSize=row["batch_size"],
        cursor=row["cursor"],
        retryCount=row["retry_count"],
        lastError=row["last_error"],
        evidence=dict(row["evidence"]),
        reason=row["reason"],
        actorId=row["actor_id"],
        previewExpiresAt=row["preview_expires_at"],
        startedAt=row["started_at"],
        completedAt=row["completed_at"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
        confirmationPhrase=_confirmation(records),
    )


def _policy_snapshot(policy: RowMapping, tenant_id: str) -> dict[str, Any]:
    return {
        "id": str(policy["id"]),
        "tenantId": None if policy["tenant_id"] is None else tenant_id,
        "resourceType": policy["resource_type"],
        "scope": policy["scope"],
        "namespace": policy["namespace_name"],
        "labelSelector": dict(policy["label_selector"]),
        "retentionDays": policy["retention_days"],
        "batchSize": policy["batch_size"],
        "reason": policy["reason"],
        "version": policy["version"],
    }


def _confirmation(records: int) -> str:
    return f"PURGE {records}"


__all__ = ["LifecycleVersionConflict", "PostgresRetentionRepository"]
