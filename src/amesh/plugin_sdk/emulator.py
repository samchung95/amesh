from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field

from .extensions import (
    ExtensionCallContext,
    ExtensionRetryableError,
    PluginConditionRequest,
    PluginConditionResult,
    PluginNotificationRequest,
    PluginNotificationResult,
    PluginPollingRequest,
    PluginRealtimeRequest,
    PluginRealtimeTriggerConnection,
    PluginTriggerCheckpoint,
    PluginTriggerOccurrence,
    PluginTriggerPollResult,
)


class ConnectorFaultPlan(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    retryable_failures: tuple[int, ...] = Field(default=(), alias="retryableFailures")
    delay_seconds: float = Field(default=0, alias="delaySeconds", ge=0, le=300)
    disconnect_after: int | None = Field(default=None, alias="disconnectAfter", ge=0)
    duplicate_count: int = Field(default=1, alias="duplicateCount", ge=1, le=100)


@dataclass
class PollingTriggerEmulator:
    batches: tuple[PluginTriggerPollResult, ...]
    fault_plan: ConnectorFaultPlan = field(default_factory=ConnectorFaultPlan)
    calls: int = 0
    acknowledgements: list[PluginTriggerCheckpoint] = field(default_factory=list)
    contexts: list[ExtensionCallContext] = field(default_factory=list)

    async def poll(
        self,
        request: PluginPollingRequest,
        context: ExtensionCallContext,
    ) -> PluginTriggerPollResult:
        del request
        self.calls += 1
        self.contexts.append(context)
        await _inject_fault(self.calls, self.fault_plan)
        if not self.batches:
            return PluginTriggerPollResult()
        batch = self.batches[min(self.calls - 1, len(self.batches) - 1)]
        return batch.model_copy(
            update={"occurrences": batch.occurrences * self.fault_plan.duplicate_count}
        )

    async def acknowledge(
        self,
        checkpoint: PluginTriggerCheckpoint,
        context: ExtensionCallContext,
    ) -> None:
        del context
        self.acknowledgements.append(checkpoint)


@dataclass
class RealtimeTriggerEmulator:
    occurrences: tuple[PluginTriggerOccurrence, ...]
    fault_plan: ConnectorFaultPlan = field(default_factory=ConnectorFaultPlan)
    connections: list[_RealtimeConnection] = field(default_factory=list)
    contexts: list[ExtensionCallContext] = field(default_factory=list)

    async def connect(
        self,
        request: PluginRealtimeRequest,
        context: ExtensionCallContext,
    ) -> PluginRealtimeTriggerConnection:
        self.contexts.append(context)
        connection = _RealtimeConnection(
            occurrences=self.occurrences * self.fault_plan.duplicate_count,
            max_in_flight=request.max_in_flight,
            fault_plan=self.fault_plan,
        )
        self.connections.append(connection)
        return connection


@dataclass
class _RealtimeConnection:
    occurrences: tuple[PluginTriggerOccurrence, ...]
    max_in_flight: int
    fault_plan: ConnectorFaultPlan
    acknowledged: list[str] = field(default_factory=list)
    closed: bool = False
    _pending: set[str] = field(default_factory=set)

    async def _events(self) -> AsyncIterator[PluginTriggerOccurrence]:
        for index, occurrence in enumerate(self.occurrences):
            if self.fault_plan.disconnect_after == index:
                raise ExtensionRetryableError("emulated realtime connector disconnected")
            if len(self._pending) >= self.max_in_flight:
                raise RuntimeError("emulated realtime connector backpressure limit exceeded")
            if self.fault_plan.delay_seconds:
                await asyncio.sleep(self.fault_plan.delay_seconds)
            self._pending.add(occurrence.source_key)
            yield occurrence

    def __aiter__(self) -> AsyncIterator[PluginTriggerOccurrence]:
        return self._events()

    async def acknowledge(self, source_key: str) -> None:
        if source_key not in self._pending:
            raise ValueError("cannot acknowledge an occurrence that is not in flight")
        self._pending.remove(source_key)
        self.acknowledged.append(source_key)

    async def close(self) -> None:
        self.closed = True


@dataclass
class ConditionEmulator:
    result: PluginConditionResult
    fault_plan: ConnectorFaultPlan = field(default_factory=ConnectorFaultPlan)
    calls: int = 0
    contexts: list[ExtensionCallContext] = field(default_factory=list)

    async def evaluate(
        self,
        request: PluginConditionRequest,
        context: ExtensionCallContext,
    ) -> PluginConditionResult:
        del request
        self.calls += 1
        self.contexts.append(context)
        await _inject_fault(self.calls, self.fault_plan)
        return self.result


@dataclass
class NotificationEmulator:
    result: PluginNotificationResult
    fault_plan: ConnectorFaultPlan = field(default_factory=ConnectorFaultPlan)
    calls: int = 0
    deliveries: list[PluginNotificationRequest] = field(default_factory=list)
    contexts: list[ExtensionCallContext] = field(default_factory=list)

    async def send(
        self,
        request: PluginNotificationRequest,
        context: ExtensionCallContext,
    ) -> PluginNotificationResult:
        self.calls += 1
        self.deliveries.append(request)
        self.contexts.append(context)
        await _inject_fault(self.calls, self.fault_plan)
        return self.result


async def _inject_fault(call: int, plan: ConnectorFaultPlan) -> None:
    if plan.delay_seconds:
        await asyncio.sleep(plan.delay_seconds)
    if call in plan.retryable_failures:
        raise ExtensionRetryableError(f"emulated retryable connector failure on call {call}")
