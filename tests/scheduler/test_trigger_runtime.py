from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

from amesh.dsl.models import TriggerDefinition
from amesh.ports import (
    TriggerAdapterOccurrence,
    TriggerOccurrence,
    TriggerOccurrenceAcceptance,
    TriggerOccurrenceState,
    TriggerPollResult,
    TriggerRuntimeState,
)
from amesh.triggers import TriggerRuntimeService


def _runtime_state(trigger_type: str) -> TriggerRuntimeState:
    now = datetime.now(UTC)
    return TriggerRuntimeState(
        trigger_definition_id=uuid4(),
        tenant_id="default",
        namespace="tests.adapters",
        flow_id="consumer",
        flow_revision=1,
        trigger_id="source",
        trigger_type=trigger_type,
        active=True,
        paused=False,
        checkpoint={"offset": 1},
        cursor="1",
        last_decision="ready",
        updated_at=now,
    )


class FakeRepository:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    async def accept_occurrence(self, **kwargs: object) -> TriggerOccurrenceAcceptance:
        self.calls.append(f"accept:{kwargs['occurrence_key']}")
        now = datetime.now(UTC)
        occurrence = TriggerOccurrence(
            occurrence_id=uuid4(),
            tenant_id=str(kwargs["tenant_id"]),
            trigger_definition_id=uuid4(),
            namespace=str(kwargs["namespace"]),
            flow_id=str(kwargs["flow_id"]),
            flow_revision=int(str(kwargs["flow_revision"])),
            trigger_id=str(kwargs["trigger_id"]),
            trigger_type="plugin.events",
            occurrence_key=str(kwargs["occurrence_key"]),
            state=TriggerOccurrenceState.ACCEPTED,
            attempt=0,
            max_attempts=int(str(kwargs["max_attempts"])),
            available_at=now,
            created_at=now,
            updated_at=now,
        )
        return TriggerOccurrenceAcceptance(
            occurrence=occurrence,
            accepted=True,
            reason="accepted",
        )

    async def update_checkpoint(self, **kwargs: object) -> TriggerRuntimeState:
        self.calls.append(f"checkpoint:{kwargs['cursor']}")
        return _runtime_state("plugin.events")


class FakePollingAdapter:
    trigger_types = frozenset({"plugin.events"})

    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    async def poll(
        self,
        definition: dict[str, object],
        *,
        checkpoint: dict[str, object],
        cursor: str | None,
        limit: int,
    ) -> TriggerPollResult:
        del definition, checkpoint, cursor, limit
        self.calls.append("poll")
        return TriggerPollResult(
            occurrences=(
                TriggerAdapterOccurrence(
                    occurrence_key="event-2",
                    payload={"value": 2},
                    observed_at=datetime.now(UTC),
                ),
            ),
            checkpoint={"offset": 2},
            cursor="2",
        )

    async def acknowledge(
        self,
        *,
        checkpoint: dict[str, object],
        cursor: str | None,
    ) -> None:
        del checkpoint
        self.calls.append(f"ack:{cursor}")


class FakeRealtimeAdapter:
    trigger_types = frozenset({"plugin.events"})

    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    async def subscribe(
        self,
        definition: dict[str, object],
        *,
        checkpoint: dict[str, object],
        cursor: str | None,
    ) -> AsyncIterator[TriggerAdapterOccurrence]:
        del definition, checkpoint, cursor
        yield TriggerAdapterOccurrence(
            occurrence_key="live-1",
            observed_at=datetime.now(UTC),
        )

    async def acknowledge(self, occurrence_key: str) -> None:
        self.calls.append(f"ack:{occurrence_key}")


def test_polling_checkpoint_is_persisted_before_source_acknowledgement() -> None:
    async def scenario() -> None:
        calls: list[str] = []
        service = TriggerRuntimeService(FakeRepository(calls))  # type: ignore[arg-type]
        results = await service.poll_once(
            _runtime_state("plugin.events"),
            TriggerDefinition(id="source", type="plugin.events"),
            FakePollingAdapter(calls),
        )
        assert len(results) == 1
        assert calls == ["poll", "accept:event-2", "checkpoint:2", "ack:2"]

    asyncio.run(scenario())


def test_realtime_source_is_acknowledged_only_after_durable_acceptance() -> None:
    async def scenario() -> None:
        calls: list[str] = []
        service = TriggerRuntimeService(FakeRepository(calls))  # type: ignore[arg-type]
        results = await service.consume_realtime(
            _runtime_state("plugin.events"),
            TriggerDefinition(id="source", type="plugin.events"),
            FakeRealtimeAdapter(calls),
            limit=1,
        )
        assert len(results) == 1
        assert calls == ["accept:live-1", "ack:live-1"]

    asyncio.run(scenario())
