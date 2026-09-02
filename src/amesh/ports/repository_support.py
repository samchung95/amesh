"""Cross-cutting contracts shared by persistence adapters."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, TypeVar
from uuid import UUID

TransactionContra = TypeVar("TransactionContra", contravariant=True)
TransactionCo = TypeVar("TransactionCo", covariant=True)


class Clock(Protocol):
    """Injectable source of timezone-aware timestamps."""

    def now(self) -> datetime: ...


class JsonCodec(Protocol):
    """Consistent JSON serialization boundary for repositories."""

    def dumps(self, value: Any, *, canonical: bool = False) -> str: ...

    def loads(self, value: str | bytes | bytearray) -> Any: ...


@dataclass(frozen=True)
class AuditWrite:
    """Adapter-neutral audit event written inside an existing transaction."""

    tenant_id: UUID
    actor_id: str
    action: str
    resource_type: str
    resource_id: str | None
    source_component: str
    outcome: str = "SUCCESS"
    reason: str | None = None
    evidence: Mapping[str, object] = field(default_factory=dict)


class AuditWriter(Protocol[TransactionContra]):
    """Write an audit record atomically with its owning repository operation."""

    async def write(self, transaction: TransactionContra, record: AuditWrite) -> UUID: ...


class TransactionManager(Protocol[TransactionCo]):
    """Open tenant-scoped and tenant-administration transactions."""

    def tenant(
        self,
        tenant_id: str,
    ) -> AbstractAsyncContextManager[tuple[TransactionCo, UUID]]: ...

    def admin(self) -> AbstractAsyncContextManager[TransactionCo]: ...


__all__ = ["AuditWrite", "AuditWriter", "Clock", "JsonCodec", "TransactionManager"]
