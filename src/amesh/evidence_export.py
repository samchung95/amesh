from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from amesh.ports import ExecutionEvidenceEvent, MetadataRepository


class EvidenceExportPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)

    retention_seconds: int = Field(default=604_800, ge=1)
    sample_rate: float = Field(default=1.0, ge=0, le=1)
    batch_size: int = Field(default=500, ge=1, le=1000)
    sensitive_fields: frozenset[str] = frozenset(
        {"api_key", "apikey", "authorization", "credential", "password", "secret", "token"}
    )


class EvidenceSink(Protocol):
    async def send(self, events: tuple[ExecutionEvidenceEvent, ...]) -> None: ...


class EvidenceExportResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    next_cursor: int = Field(ge=0)
    exported: int = Field(ge=0)
    dropped: int = Field(ge=0)
    sink_available: bool


class EvidenceExporter:
    """Best-effort evidence exporter kept outside the execution completion path."""

    def __init__(
        self,
        repository: MetadataRepository,
        sink: EvidenceSink,
        policy: EvidenceExportPolicy | None = None,
    ) -> None:
        self._repository = repository
        self._sink = sink
        self._policy = policy or EvidenceExportPolicy()

    async def export_once(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        after_cursor: int = 0,
        now: datetime | None = None,
    ) -> EvidenceExportResult:
        events = await self._repository.list_evidence_events(
            execution_id,
            tenant_id=tenant_id,
            after_cursor=after_cursor,
            limit=self._policy.batch_size,
        )
        next_cursor = events[-1].cursor if events else after_cursor
        cutoff = (now or datetime.now(UTC)) - timedelta(seconds=self._policy.retention_seconds)
        selected = tuple(
            event.model_copy(update={"payload": self._redact(event.payload)})
            for event in events
            if event.ingested_at >= cutoff and self._sample(event)
        )
        try:
            if selected:
                await self._sink.send(selected)
        except Exception:
            return EvidenceExportResult(
                next_cursor=after_cursor,
                exported=0,
                dropped=len(events),
                sink_available=False,
            )
        return EvidenceExportResult(
            next_cursor=next_cursor,
            exported=len(selected),
            dropped=len(events) - len(selected),
            sink_available=True,
        )

    def _sample(self, event: ExecutionEvidenceEvent) -> bool:
        if self._policy.sample_rate >= 1:
            return True
        if self._policy.sample_rate <= 0:
            return False
        bucket = int.from_bytes(hashlib.sha256(event.event_id.bytes).digest()[:8], "big")
        return bucket / (2**64 - 1) < self._policy.sample_rate

    def _redact(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: (
                    "[REDACTED]"
                    if key.casefold().replace("-", "_") in self._policy.sensitive_fields
                    else self._redact(item)
                )
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self._redact(item) for item in value]
        return value
