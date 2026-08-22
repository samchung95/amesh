from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.ports import (
    TaskCacheDecision,
    TaskCacheEntry,
    TaskCacheKey,
    TaskCacheLookup,
    TaskCacheMode,
    TaskCachePurgeResult,
    TaskCacheRepository,
)

from .tenant_context import tenant_transaction


class PostgresTaskCacheRepository(TaskCacheRepository):
    """Tenant-fenced durable task-result cache with an immutable decision ledger."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def lookup_or_reserve(
        self,
        key: TaskCacheKey,
        *,
        tenant_id: str,
        execution_id: UUID,
        task_run_id: UUID,
        attempt: int,
        mode: TaskCacheMode = TaskCacheMode.USE,
    ) -> TaskCacheLookup:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await _lock_key(connection, tenant_uuid, key.key_hash)
            now = await connection.scalar(text("SELECT clock_timestamp()"))
            if not isinstance(now, datetime):
                raise TypeError("PostgreSQL returned an invalid database timestamp")
            row = await _get_entry(connection, tenant_uuid, key.key_hash)
            if (
                row is not None
                and row["state"] == "READY"
                and row["expires_at"] > now
                and mode is TaskCacheMode.USE
            ):
                updated = (
                    (
                        await connection.execute(
                            text(
                                """
                                UPDATE task_cache_entries
                                SET hit_count = hit_count + 1,
                                    last_hit_at = clock_timestamp(),
                                    updated_at = clock_timestamp()
                                WHERE tenant_id = :tenant_id AND entry_id = :entry_id
                                RETURNING *
                                """
                            ),
                            {"tenant_id": tenant_uuid, "entry_id": row["entry_id"]},
                        )
                    )
                    .mappings()
                    .one()
                )
                reason = (
                    "reused a tenant- and security-context-matched result from "
                    f"execution {updated['source_execution_id']}"
                )
                await _insert_event(
                    connection,
                    tenant_uuid,
                    entry_id=updated["entry_id"],
                    key_hash=key.key_hash,
                    event_type=TaskCacheDecision.HIT.value,
                    reason=reason,
                    execution_id=execution_id,
                    task_run_id=task_run_id,
                    attempt=attempt,
                    actor_id="system:executor",
                    payload={
                        "sourceExecutionId": str(updated["source_execution_id"]),
                        "sourceTaskRunId": str(updated["source_task_run_id"]),
                        "sourceAttempt": updated["source_attempt"],
                    },
                )
                return TaskCacheLookup(
                    decision=TaskCacheDecision.HIT,
                    reason=reason,
                    key_hash=key.key_hash,
                    output=dict(updated["output"] or {}),
                    evidence=dict(updated["evidence"] or {}),
                    source_execution_id=updated["source_execution_id"],
                    source_task_run_id=updated["source_task_run_id"],
                    source_attempt=updated["source_attempt"],
                    expires_at=updated["expires_at"],
                )

            active_population = (
                row is not None
                and row["state"] == "POPULATING"
                and row["lease_expires_at"] is not None
                and row["lease_expires_at"] > now
            )
            if active_population:
                assert row is not None
                decision = TaskCacheDecision.MISS_CONCURRENT
                reason = "another execution is populating this key; computing a safe duplicate"
                await _insert_event(
                    connection,
                    tenant_uuid,
                    entry_id=row["entry_id"],
                    key_hash=key.key_hash,
                    event_type=decision.value,
                    reason=reason,
                    execution_id=execution_id,
                    task_run_id=task_run_id,
                    attempt=attempt,
                    actor_id="system:executor",
                    payload={},
                )
                return TaskCacheLookup(
                    decision=decision,
                    reason=reason,
                    key_hash=key.key_hash,
                )

            if mode is TaskCacheMode.REFRESH:
                decision = TaskCacheDecision.REFRESH
                reason = "execution requested a fresh result and replaced any reusable entry"
            elif row is None:
                decision = TaskCacheDecision.MISS
                reason = "no cache entry exists for the derived key"
            elif row["state"] == "INVALIDATED":
                decision = TaskCacheDecision.MISS_INVALIDATED
                reason = str(row["invalidation_reason"] or "cache entry was invalidated")
            elif row["expires_at"] <= now:
                decision = TaskCacheDecision.MISS_EXPIRED
                reason = f"cache entry expired at {row['expires_at'].isoformat()}"
            else:
                decision = TaskCacheDecision.MISS
                reason = "cache entry is not reusable"

            owner_token = new_runtime_id()
            expires_at = now + key.ttl
            lease_expires_at = now + key.population_lease
            if row is None:
                entry_id = new_runtime_id()
                await connection.execute(
                    text(
                        """
                        INSERT INTO task_cache_entries (
                            entry_id, tenant_id, key_hash, key_prefix, cache_namespace,
                            scope, namespace_name, flow_id, flow_revision, task_id,
                            task_type, security_context_hash, invalidation_policy,
                            state, owner_token, lease_expires_at, expires_at
                        ) VALUES (
                            :entry_id, :tenant_id, :key_hash, :key_prefix, :cache_namespace,
                            :scope, :namespace, :flow_id, :flow_revision, :task_id,
                            :task_type, :security_context_hash, :invalidation_policy,
                            'POPULATING', :owner_token, :lease_expires_at, :expires_at
                        )
                        """
                    ),
                    {
                        "entry_id": entry_id,
                        "tenant_id": tenant_uuid,
                        "key_hash": key.key_hash,
                        "key_prefix": key.key_prefix,
                        "cache_namespace": key.cache_namespace,
                        "scope": key.scope,
                        "namespace": key.namespace,
                        "flow_id": key.flow_id,
                        "flow_revision": key.flow_revision,
                        "task_id": key.task_id,
                        "task_type": key.task_type,
                        "security_context_hash": key.security_context_hash,
                        "invalidation_policy": key.invalidation_policy,
                        "owner_token": owner_token,
                        "lease_expires_at": lease_expires_at,
                        "expires_at": expires_at,
                    },
                )
            else:
                entry_id = row["entry_id"]
                await connection.execute(
                    text(
                        """
                        UPDATE task_cache_entries
                        SET key_prefix = :key_prefix,
                            cache_namespace = :cache_namespace,
                            scope = :scope,
                            namespace_name = :namespace,
                            flow_id = :flow_id,
                            flow_revision = :flow_revision,
                            task_id = :task_id,
                            task_type = :task_type,
                            security_context_hash = :security_context_hash,
                            invalidation_policy = :invalidation_policy,
                            state = 'POPULATING', owner_token = :owner_token,
                            lease_expires_at = :lease_expires_at, expires_at = :expires_at,
                            output = NULL, evidence = NULL,
                            source_execution_id = NULL, source_task_run_id = NULL,
                            source_attempt = NULL, invalidation_reason = NULL,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND entry_id = :entry_id
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "entry_id": entry_id,
                        "key_prefix": key.key_prefix,
                        "cache_namespace": key.cache_namespace,
                        "scope": key.scope,
                        "namespace": key.namespace,
                        "flow_id": key.flow_id,
                        "flow_revision": key.flow_revision,
                        "task_id": key.task_id,
                        "task_type": key.task_type,
                        "security_context_hash": key.security_context_hash,
                        "invalidation_policy": key.invalidation_policy,
                        "owner_token": owner_token,
                        "lease_expires_at": lease_expires_at,
                        "expires_at": expires_at,
                    },
                )
            await _insert_event(
                connection,
                tenant_uuid,
                entry_id=entry_id,
                key_hash=key.key_hash,
                event_type=decision.value,
                reason=reason,
                execution_id=execution_id,
                task_run_id=task_run_id,
                attempt=attempt,
                actor_id="system:executor",
                payload={"ownerToken": str(owner_token), "expiresAt": expires_at.isoformat()},
            )
            return TaskCacheLookup(
                decision=decision,
                reason=reason,
                key_hash=key.key_hash,
                owner_token=owner_token,
                expires_at=expires_at,
            )

    async def publish(
        self,
        key_hash: str,
        owner_token: UUID,
        output: dict[str, object],
        evidence: dict[str, object],
        *,
        tenant_id: str,
        execution_id: UUID,
        task_run_id: UUID,
        attempt: int,
    ) -> bool:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await _lock_key(connection, tenant_uuid, key_hash)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE task_cache_entries
                            SET state = 'READY', owner_token = NULL, lease_expires_at = NULL,
                                output = CAST(:output AS jsonb), evidence = CAST(:evidence AS jsonb),
                                source_execution_id = :execution_id,
                                source_task_run_id = :task_run_id,
                                source_attempt = :attempt,
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND key_hash = :key_hash
                              AND state = 'POPULATING' AND owner_token = :owner_token
                            RETURNING entry_id
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "key_hash": key_hash,
                            "owner_token": owner_token,
                            "output": json.dumps(output),
                            "evidence": json.dumps(evidence),
                            "execution_id": execution_id,
                            "task_run_id": task_run_id,
                            "attempt": attempt,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                return False
            await _insert_event(
                connection,
                tenant_uuid,
                entry_id=row["entry_id"],
                key_hash=key_hash,
                event_type="FILLED",
                reason="task result committed as the reusable cache entry",
                execution_id=execution_id,
                task_run_id=task_run_id,
                attempt=attempt,
                actor_id="system:executor",
                payload={},
            )
            return True

    async def record_bypass(
        self,
        key: TaskCacheKey,
        *,
        tenant_id: str,
        execution_id: UUID,
        task_run_id: UUID,
        attempt: int,
        reason: str,
    ) -> None:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await _insert_event(
                connection,
                tenant_uuid,
                entry_id=None,
                key_hash=key.key_hash,
                event_type=TaskCacheDecision.BYPASS.value,
                reason=reason,
                execution_id=execution_id,
                task_run_id=task_run_id,
                attempt=attempt,
                actor_id="system:executor",
                payload={"keyPrefix": key.key_prefix},
            )

    async def abandon(
        self,
        key_hash: str,
        owner_token: UUID,
        *,
        tenant_id: str,
        execution_id: UUID,
        task_run_id: UUID,
        attempt: int,
        reason: str,
    ) -> bool:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await _lock_key(connection, tenant_uuid, key_hash)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE task_cache_entries
                            SET state = 'INVALIDATED', owner_token = NULL,
                                lease_expires_at = NULL, invalidation_reason = :reason,
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND key_hash = :key_hash
                              AND state = 'POPULATING' AND owner_token = :owner_token
                            RETURNING entry_id
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "key_hash": key_hash,
                            "owner_token": owner_token,
                            "reason": reason,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                return False
            await _insert_event(
                connection,
                tenant_uuid,
                entry_id=row["entry_id"],
                key_hash=key_hash,
                event_type="ABANDONED",
                reason=reason,
                execution_id=execution_id,
                task_run_id=task_run_id,
                attempt=attempt,
                actor_id="system:executor",
                payload={},
            )
            return True

    async def list_entries(
        self,
        *,
        tenant_id: str,
        key_prefix: str | None = None,
        namespace: str | None = None,
        flow_id: str | None = None,
        task_id: str | None = None,
        limit: int = 100,
    ) -> list[TaskCacheEntry]:
        if not 1 <= limit <= 1000:
            raise ValueError("cache entry limit must be between 1 and 1000")
        clauses = ["tenant_id = :tenant_id"]
        parameters: dict[str, object] = {"limit": limit}
        if key_prefix is not None:
            clauses.append("starts_with(key_prefix, :key_prefix)")
            parameters["key_prefix"] = key_prefix
        if namespace is not None:
            clauses.append("namespace_name = :namespace")
            parameters["namespace"] = namespace
        if flow_id is not None:
            clauses.append("flow_id = :flow_id")
            parameters["flow_id"] = flow_id
        if task_id is not None:
            clauses.append("task_id = :task_id")
            parameters["task_id"] = task_id
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            parameters["tenant_id"] = tenant_uuid
            rows = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM task_cache_entries WHERE "
                            + " AND ".join(clauses)
                            + " ORDER BY updated_at DESC, entry_id LIMIT :limit"
                        ),
                        parameters,
                    )
                )
                .mappings()
                .all()
            )
        return [_to_entry(row) for row in rows]

    async def purge(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str,
        key_prefix: str | None = None,
        namespace: str | None = None,
        flow_id: str | None = None,
        task_id: str | None = None,
    ) -> TaskCachePurgeResult:
        if not any((key_prefix, namespace, flow_id, task_id)):
            raise ValueError("cache purge requires a key prefix or resource scope")
        clauses = ["tenant_id = :tenant_id", "state <> 'INVALIDATED'"]
        parameters: dict[str, object] = {"reason": reason}
        scope: dict[str, object] = {
            "keyPrefix": key_prefix,
            "namespace": namespace,
            "flowId": flow_id,
            "taskId": task_id,
        }
        if key_prefix is not None:
            clauses.append("starts_with(key_prefix, :key_prefix)")
            parameters["key_prefix"] = key_prefix
        if namespace is not None:
            clauses.append("namespace_name = :namespace")
            parameters["namespace"] = namespace
        if flow_id is not None:
            clauses.append("flow_id = :flow_id")
            parameters["flow_id"] = flow_id
        if task_id is not None:
            clauses.append("task_id = :task_id")
            parameters["task_id"] = task_id
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            parameters["tenant_id"] = tenant_uuid
            rows = (
                (
                    await connection.execute(
                        text(
                            "UPDATE task_cache_entries SET state = 'INVALIDATED', "
                            "owner_token = NULL, lease_expires_at = NULL, "
                            "invalidation_reason = :reason, updated_at = clock_timestamp() WHERE "
                            + " AND ".join(clauses)
                            + " RETURNING entry_id, key_hash"
                        ),
                        parameters,
                    )
                )
                .mappings()
                .all()
            )
            for row in rows:
                await _insert_event(
                    connection,
                    tenant_uuid,
                    entry_id=row["entry_id"],
                    key_hash=row["key_hash"],
                    event_type="PURGED",
                    reason=reason,
                    execution_id=None,
                    task_run_id=None,
                    attempt=None,
                    actor_id=actor_id,
                    payload=scope,
                )
            await connection.execute(
                text(
                    """
                    INSERT INTO audit_events (
                        event_id, tenant_id, actor_id, action, resource_type,
                        resource_id, outcome, source, evidence, occurred_at
                    ) VALUES (
                        :event_id, :tenant_id, :actor_id, 'cache.purge', 'task_cache',
                        :resource_id, 'SUCCESS', CAST(:source AS jsonb),
                        CAST(:evidence AS jsonb), clock_timestamp()
                    )
                    """
                ),
                {
                    "event_id": new_runtime_id(),
                    "tenant_id": tenant_uuid,
                    "actor_id": actor_id,
                    "resource_id": key_prefix or task_id or flow_id or namespace,
                    "source": json.dumps({"component": "task-cache-api"}),
                    "evidence": json.dumps(
                        {**scope, "invalidatedCount": len(rows), "reason": reason}
                    ),
                },
            )
        return TaskCachePurgeResult(invalidated_count=len(rows), reason=reason)


async def _lock_key(connection: AsyncConnection, tenant_id: UUID, key_hash: str) -> None:
    await connection.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:lock_key, 0))"),
        {"lock_key": f"{tenant_id}:task-cache:{key_hash}"},
    )


async def _get_entry(
    connection: AsyncConnection,
    tenant_id: UUID,
    key_hash: str,
) -> RowMapping | None:
    return (
        (
            await connection.execute(
                text(
                    "SELECT * FROM task_cache_entries "
                    "WHERE tenant_id = :tenant_id AND key_hash = :key_hash"
                ),
                {"tenant_id": tenant_id, "key_hash": key_hash},
            )
        )
        .mappings()
        .one_or_none()
    )


async def _insert_event(
    connection: AsyncConnection,
    tenant_id: UUID,
    *,
    entry_id: UUID | None,
    key_hash: str | None,
    event_type: str,
    reason: str,
    execution_id: UUID | None,
    task_run_id: UUID | None,
    attempt: int | None,
    actor_id: str,
    payload: dict[str, object],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO task_cache_events (
                tenant_id, event_id, entry_id, key_hash, event_type, reason,
                execution_id, task_run_id, attempt, actor_id, payload
            ) VALUES (
                :tenant_id, :event_id, :entry_id, :key_hash, :event_type, :reason,
                :execution_id, :task_run_id, :attempt, :actor_id, CAST(:payload AS jsonb)
            )
            """
        ),
        {
            "tenant_id": tenant_id,
            "event_id": new_runtime_id(),
            "entry_id": entry_id,
            "key_hash": key_hash,
            "event_type": event_type,
            "reason": reason,
            "execution_id": execution_id,
            "task_run_id": task_run_id,
            "attempt": attempt,
            "actor_id": actor_id,
            "payload": json.dumps(payload),
        },
    )


def _to_entry(row: RowMapping) -> TaskCacheEntry:
    return TaskCacheEntry(
        entry_id=row["entry_id"],
        key_hash=str(row["key_hash"]),
        key_prefix=str(row["key_prefix"]),
        cache_namespace=str(row["cache_namespace"]),
        scope=str(row["scope"]),
        namespace=str(row["namespace_name"]),
        flow_id=str(row["flow_id"]),
        flow_revision=int(row["flow_revision"]),
        task_id=str(row["task_id"]),
        task_type=str(row["task_type"]),
        state=str(row["state"]),
        source_execution_id=row["source_execution_id"],
        source_task_run_id=row["source_task_run_id"],
        source_attempt=row["source_attempt"],
        expires_at=row["expires_at"],
        hit_count=int(row["hit_count"]),
        last_hit_at=row["last_hit_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        invalidation_reason=row["invalidation_reason"],
    )
