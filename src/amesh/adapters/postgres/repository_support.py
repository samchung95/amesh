"""Shared PostgreSQL repository composition services."""

from __future__ import annotations

import json
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.ports.repository_support import (
    AuditWrite,
    AuditWriter,
    Clock,
    JsonCodec,
    TransactionManager,
)

from .tenant_context import tenant_admin_transaction, tenant_transaction


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)


class StandardJsonCodec(JsonCodec):
    def dumps(self, value: Any, *, canonical: bool = False) -> str:
        if canonical:
            return json.dumps(value, sort_keys=True, separators=(",", ":"))
        return json.dumps(value)

    def loads(self, value: str | bytes | bytearray) -> Any:
        return json.loads(value)


class PostgresTransactionManager(TransactionManager[AsyncConnection]):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    def tenant(
        self,
        tenant_id: str,
    ) -> AbstractAsyncContextManager[tuple[AsyncConnection, UUID]]:
        return tenant_transaction(self._engine, tenant_id)

    def admin(self) -> AbstractAsyncContextManager[AsyncConnection]:
        return tenant_admin_transaction(self._engine)


class PostgresAuditWriter(AuditWriter[AsyncConnection]):
    def __init__(self, *, clock: Clock, codec: JsonCodec) -> None:
        self._clock = clock
        self._codec = codec

    async def write(self, transaction: AsyncConnection, record: AuditWrite) -> UUID:
        event_id = new_runtime_id()
        await transaction.execute(
            text(
                """
                INSERT INTO audit_events (
                    event_id, tenant_id, actor_id, action, resource_type, resource_id,
                    outcome, reason, correlation_id, source, evidence, occurred_at
                ) VALUES (
                    :event_id, :tenant_id, :actor_id, :action, :resource_type,
                    :resource_id, :outcome, :reason, :correlation_id,
                    CAST(:source AS jsonb), CAST(:evidence AS jsonb), :occurred_at
                )
                """
            ),
            {
                "event_id": event_id,
                "tenant_id": record.tenant_id,
                "actor_id": record.actor_id,
                "action": record.action,
                "resource_type": record.resource_type,
                "resource_id": record.resource_id,
                "outcome": record.outcome,
                "reason": record.reason,
                "correlation_id": new_runtime_id(),
                "source": self._codec.dumps({"component": record.source_component}),
                "evidence": self._codec.dumps(dict(record.evidence)),
                "occurred_at": self._clock.now(),
            },
        )
        return event_id


@dataclass(frozen=True)
class PostgresRepositoryServices:
    transactions: TransactionManager[AsyncConnection]
    audit: AuditWriter[AsyncConnection]
    codec: JsonCodec
    clock: Clock


def build_repository_services(engine: AsyncEngine) -> PostgresRepositoryServices:
    clock = SystemClock()
    codec = StandardJsonCodec()
    return PostgresRepositoryServices(
        transactions=PostgresTransactionManager(engine),
        audit=PostgresAuditWriter(clock=clock, codec=codec),
        codec=codec,
        clock=clock,
    )


class PostgresRepositoryBase:
    """Composition-only base for incrementally migrated PostgreSQL repositories."""

    def __init__(
        self,
        engine: AsyncEngine,
        *,
        services: PostgresRepositoryServices | None = None,
    ) -> None:
        self._engine = engine
        self._services = services or build_repository_services(engine)


__all__ = [
    "PostgresAuditWriter",
    "PostgresRepositoryBase",
    "PostgresRepositoryServices",
    "PostgresTransactionManager",
    "StandardJsonCodec",
    "SystemClock",
    "build_repository_services",
]
