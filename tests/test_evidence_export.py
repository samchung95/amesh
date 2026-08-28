from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

from amesh.evidence_export import EvidenceExporter
from amesh.ports import ExecutionEvidenceEvent, MetadataRepository


def _event() -> ExecutionEvidenceEvent:
    now = datetime.now(UTC)
    return ExecutionEvidenceEvent(
        cursor=7,
        event_id=uuid4(),
        execution_id=uuid4(),
        kind="LOG",
        event_type="log.info",
        payload={"message": "safe", "authorization": "secret-canary"},
        occurred_at=now,
        ingested_at=now,
    )


def test_exporter_redacts_again_before_shipment() -> None:
    event = _event()

    class Repository:
        async def list_evidence_events(self, *args: Any, **kwargs: Any) -> list[Any]:
            return [event]

    class Sink:
        received: tuple[ExecutionEvidenceEvent, ...] = ()

        async def send(self, events: tuple[ExecutionEvidenceEvent, ...]) -> None:
            self.received = events

    sink = Sink()
    result = asyncio.run(
        EvidenceExporter(cast(MetadataRepository, Repository()), sink).export_once(
            event.execution_id,
            tenant_id="default",
        )
    )

    assert result.exported == 1
    assert result.next_cursor == 7
    assert sink.received[0].payload["authorization"] == "[REDACTED]"


def test_exporter_sink_outage_is_best_effort_and_keeps_cursor() -> None:
    event = _event()

    class Repository:
        async def list_evidence_events(self, *args: Any, **kwargs: Any) -> list[Any]:
            return [event]

    class OfflineSink:
        async def send(self, events: tuple[ExecutionEvidenceEvent, ...]) -> None:
            del events
            raise OSError("optional sink unavailable")

    result = asyncio.run(
        EvidenceExporter(cast(MetadataRepository, Repository()), OfflineSink()).export_once(
            event.execution_id,
            tenant_id="default",
        )
    )

    assert result.sink_available is False
    assert result.next_cursor == 0
    assert result.exported == 0
