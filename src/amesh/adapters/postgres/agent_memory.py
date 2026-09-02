from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.domain.agent_memory import (
    AgentMemoryContext,
    AgentMemoryEntry,
    AgentMemoryMetadata,
    AgentMemoryWrite,
)
from amesh.domain.agent_resources import AgentMemoryScope
from amesh.domain.resources import canonical_hash
from amesh.ports.agent_memory import AgentMemoryRepository

from .tenant_context import tenant_transaction


class PostgresAgentMemoryRepository(AgentMemoryRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def read(
        self,
        tenant_id: str,
        context: AgentMemoryContext,
        keys: tuple[str, ...],
    ) -> tuple[AgentMemoryEntry, ...]:
        if not keys:
            return ()
        scope_key = _scope_key(context)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM agent_memory_entries
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND scope = :scope
                              AND scope_key = :scope_key
                              AND memory_key = ANY(CAST(:keys AS text[]))
                              AND deleted_at IS NULL
                              AND expires_at > clock_timestamp()
                            ORDER BY memory_key
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": context.namespace,
                            "scope": context.scope.value,
                            "scope_key": scope_key,
                            "keys": list(keys),
                        },
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_entry(row, tenant_id) for row in rows)

    async def write(
        self,
        tenant_id: str,
        context: AgentMemoryContext,
        write: AgentMemoryWrite,
    ) -> AgentMemoryEntry:
        scope_key = _scope_key(context)
        encoded = json.dumps(
            write.value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        byte_size = len(encoded)
        if byte_size > context.max_bytes:
            raise ValueError("agent memory entry exceeds maxBytes")
        digest = "sha256:" + canonical_hash(write.value)
        expires_at = datetime.now(UTC) + timedelta(seconds=context.retention_seconds)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await connection.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:lock_key, 0))"),
                {
                    "lock_key": (
                        f"{tenant_uuid}:{context.namespace}:{context.scope.value}:{scope_key}"
                    )
                },
            )
            existing = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM agent_memory_entries
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND scope = :scope
                              AND scope_key = :scope_key
                              AND memory_key = :memory_key
                            FOR UPDATE
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": context.namespace,
                            "scope": context.scope.value,
                            "scope_key": scope_key,
                            "memory_key": write.key,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if (
                existing is not None
                and existing["deleted_at"] is None
                and existing["expires_at"] > datetime.now(UTC)
                and existing["content_digest"] == digest
                and existing["provenance"].get("operationKey")
                == write.provenance.get("operationKey")
            ):
                return _entry(existing, tenant_id)
            retained_bytes = int(
                await connection.scalar(
                    text(
                        """
                        SELECT COALESCE(sum(byte_size), 0)
                        FROM agent_memory_entries
                        WHERE tenant_id = :tenant_id
                          AND namespace_name = :namespace
                          AND scope = :scope
                          AND scope_key = :scope_key
                          AND memory_key <> :memory_key
                          AND deleted_at IS NULL
                          AND expires_at > clock_timestamp()
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "namespace": context.namespace,
                        "scope": context.scope.value,
                        "scope_key": scope_key,
                        "memory_key": write.key,
                    },
                )
                or 0
            )
            if retained_bytes + byte_size > context.max_bytes:
                raise ValueError("agent memory scope exceeds maxBytes")
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO agent_memory_entries (
                                entry_id, tenant_id, namespace_name, scope, scope_key,
                                source_execution_id, producer_agent_key,
                                producer_agent_revision, memory_key, content,
                                content_digest, byte_size, provenance, redacted, expires_at
                            ) VALUES (
                                :entry_id, :tenant_id, :namespace, :scope, :scope_key,
                                :execution_id, :agent_key, :agent_revision, :memory_key,
                                CAST(:content AS jsonb), :content_digest, :byte_size,
                                CAST(:provenance AS jsonb), :redacted, :expires_at
                            )
                            ON CONFLICT (
                                tenant_id, namespace_name, scope, scope_key, memory_key
                            ) DO UPDATE SET
                                source_execution_id = EXCLUDED.source_execution_id,
                                producer_agent_key = EXCLUDED.producer_agent_key,
                                producer_agent_revision = EXCLUDED.producer_agent_revision,
                                content = EXCLUDED.content,
                                content_digest = EXCLUDED.content_digest,
                                byte_size = EXCLUDED.byte_size,
                                provenance = EXCLUDED.provenance,
                                redacted = EXCLUDED.redacted,
                                version = agent_memory_entries.version + 1,
                                updated_at = clock_timestamp(),
                                expires_at = EXCLUDED.expires_at,
                                deleted_at = NULL
                            RETURNING *
                            """
                        ),
                        {
                            "entry_id": new_runtime_id(),
                            "tenant_id": tenant_uuid,
                            "namespace": context.namespace,
                            "scope": context.scope.value,
                            "scope_key": scope_key,
                            "execution_id": context.execution_id,
                            "agent_key": context.agent_key,
                            "agent_revision": context.agent_revision,
                            "memory_key": write.key,
                            "content": encoded.decode("utf-8"),
                            "content_digest": digest,
                            "byte_size": byte_size,
                            "provenance": json.dumps(write.provenance),
                            "redacted": write.redacted,
                            "expires_at": expires_at,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return _entry(row, tenant_id)

    async def list_metadata(
        self,
        tenant_id: str,
        namespace: str,
        *,
        agent_key: str | None = None,
        limit: int = 100,
    ) -> tuple[AgentMemoryMetadata, ...]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM agent_memory_entries
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND (
                                  CAST(:agent_key AS text) IS NULL
                                  OR producer_agent_key = CAST(:agent_key AS text)
                              )
                              AND deleted_at IS NULL
                              AND expires_at > clock_timestamp()
                            ORDER BY updated_at DESC, entry_id
                            LIMIT :limit
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "agent_key": agent_key,
                            "limit": limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_entry(row, tenant_id).metadata() for row in rows)

    async def delete(
        self,
        tenant_id: str,
        namespace: str,
        entry_id: UUID,
        *,
        actor_id: str,
    ) -> AgentMemoryMetadata:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE agent_memory_entries
                            SET deleted_at = clock_timestamp(), updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND entry_id = :entry_id
                              AND deleted_at IS NULL
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "entry_id": entry_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError("agent memory entry does not exist")
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                entry_id=entry_id,
                evidence={
                    "namespace": row["namespace_name"],
                    "scope": row["scope"],
                    "key": row["memory_key"],
                    "contentDigest": row["content_digest"],
                },
            )
        return _entry(row, tenant_id).metadata()


def _scope_key(context: AgentMemoryContext) -> str:
    if context.scope is AgentMemoryScope.EXECUTION:
        return str(context.execution_id)
    if context.scope is AgentMemoryScope.PRIVATE:
        return f"{context.agent_key}@{context.agent_revision}"
    if context.scope is AgentMemoryScope.SHARED and context.shared_scope is not None:
        return context.shared_scope
    raise ValueError("agent memory context has an invalid scope boundary")


def _entry(row: RowMapping, tenant_id: str) -> AgentMemoryEntry:
    scope = AgentMemoryScope(str(row["scope"]))
    return AgentMemoryEntry(
        entryId=row["entry_id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        agentKey=row["producer_agent_key"],
        agentRevision=row["producer_agent_revision"],
        executionId=row["source_execution_id"],
        scope=scope,
        sharedScope=row["scope_key"] if scope is AgentMemoryScope.SHARED else None,
        key=row["memory_key"],
        value=row["content"],
        contentDigest=row["content_digest"],
        byteSize=row["byte_size"],
        provenance=row["provenance"],
        redacted=row["redacted"],
        version=row["version"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
        expiresAt=row["expires_at"],
    )


async def _write_audit(
    connection: AsyncConnection,
    tenant_id: UUID,
    *,
    actor_id: str,
    entry_id: UUID,
    evidence: dict[str, object],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                event_id, tenant_id, actor_id, action, resource_type, resource_id,
                outcome, reason, correlation_id, source, evidence, occurred_at
            ) VALUES (
                :event_id, :tenant_id, :actor_id, 'agent.memory.delete',
                'agent_memory', :resource_id, 'SUCCESS', 'deleted agent memory entry',
                :correlation_id, '{"component":"agent-memory-repository"}'::jsonb,
                CAST(:evidence AS jsonb), :occurred_at
            )
            """
        ),
        {
            "event_id": new_runtime_id(),
            "tenant_id": tenant_id,
            "actor_id": actor_id,
            "resource_id": str(entry_id),
            "correlation_id": new_runtime_id(),
            "evidence": json.dumps(evidence),
            "occurred_at": datetime.now(UTC),
        },
    )
