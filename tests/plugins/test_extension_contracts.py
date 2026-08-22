from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from amesh.dsl.models import TriggerDefinition
from amesh.plugin_sdk import (
    ConditionEmulator,
    ConnectorFaultPlan,
    ExtensionCallContext,
    ExtensionCallController,
    ExtensionCallPolicy,
    ExtensionCancelledError,
    ExtensionRetryableError,
    ExtensionType,
    NotificationEmulator,
    PluginCapabilities,
    PluginCompatibility,
    PluginConditionRequest,
    PluginConditionResult,
    PluginDocumentation,
    PluginEntryPoint,
    PluginLifecycleEvent,
    PluginLifecycleEventType,
    PluginManifest,
    PluginNotificationDeliveryPolicy,
    PluginNotificationRequest,
    PluginNotificationResult,
    PluginTransport,
    PluginTriggerOccurrence,
    PluginTriggerPollResult,
    PollingTriggerEmulator,
    RealtimeTriggerEmulator,
    normalize_occurrence_key,
    validate_extension_configuration,
)
from amesh.plugins import (
    PluginConditionEvaluator,
    PluginNotificationDispatcher,
    PluginPollingTriggerAdapter,
    PluginRealtimeTriggerAdapter,
)
from amesh.ports import (
    TriggerOccurrence,
    TriggerOccurrenceAcceptance,
    TriggerOccurrenceState,
    TriggerRuntimeState,
)
from amesh.triggers import TriggerRuntimeService


def _state(trigger_type: str = "vendor.events") -> TriggerRuntimeState:
    now = datetime.now(UTC)
    return TriggerRuntimeState(
        trigger_definition_id=uuid4(),
        tenant_id="default",
        namespace="tests.extensions",
        flow_id="consumer",
        flow_revision=1,
        trigger_id="source",
        trigger_type=trigger_type,
        active=True,
        paused=False,
        checkpoint={"offset": 0},
        cursor="0",
        last_decision="ready",
        updated_at=now,
    )


class _Repository:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.keys: set[str] = set()
        self.checkpoint: dict[str, Any] = {}

    async def accept_occurrence(self, **kwargs: object) -> TriggerOccurrenceAcceptance:
        key = str(kwargs["occurrence_key"])
        duplicate = key in self.keys
        self.keys.add(key)
        self.calls.append(f"accept:{key}:{duplicate}")
        now = datetime.now(UTC)
        return TriggerOccurrenceAcceptance(
            occurrence=TriggerOccurrence(
                occurrence_id=uuid4(),
                tenant_id=str(kwargs["tenant_id"]),
                trigger_definition_id=uuid4(),
                namespace=str(kwargs["namespace"]),
                flow_id=str(kwargs["flow_id"]),
                flow_revision=int(str(kwargs["flow_revision"])),
                trigger_id=str(kwargs["trigger_id"]),
                trigger_type="vendor.events",
                occurrence_key=key,
                state=TriggerOccurrenceState.ACCEPTED,
                attempt=0,
                max_attempts=int(str(kwargs["max_attempts"])),
                available_at=now,
                created_at=now,
                updated_at=now,
            ),
            duplicate=duplicate,
            accepted=not duplicate,
            reason="duplicate" if duplicate else "accepted",
        )

    async def update_checkpoint(self, **kwargs: object) -> TriggerRuntimeState:
        checkpoint = kwargs["checkpoint"]
        assert isinstance(checkpoint, dict)
        self.checkpoint = dict(checkpoint)
        self.calls.append(f"checkpoint:{kwargs['cursor']}")
        return _state()


def _manifest() -> PluginManifest:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"threshold": {"type": "integer"}},
        "required": ["threshold"],
        "additionalProperties": False,
    }
    documentation = PluginDocumentation(
        title="Extension",
        description="Extension contract fixture.",
        category="Tests",
    )
    return PluginManifest(
        name="vendor.extensions",
        version="1.0.0",
        vendor="Test vendor",
        license="MIT",
        compatibility=PluginCompatibility(platformVersion=">=0.2.0"),
        capabilities=PluginCapabilities(secretScopes=("provider.token",)),
        entryPoints=(
            PluginEntryPoint(
                name="events",
                resourceType="vendor.events",
                type=ExtensionType.TRIGGER,
                transport=PluginTransport.STDIO,
                target="service:events",
                configurationSchema=schema,
                documentation=documentation,
            ),
            PluginEntryPoint(
                name="condition",
                resourceType="vendor.condition",
                type=ExtensionType.CONDITION,
                transport=PluginTransport.STDIO,
                target="service:condition",
                configurationSchema=schema,
                documentation=documentation,
            ),
            PluginEntryPoint(
                name="notify",
                resourceType="vendor.notify",
                type=ExtensionType.NOTIFICATION,
                transport=PluginTransport.STDIO,
                target="service:notify",
                configurationSchema={
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "type": "object",
                },
                documentation=documentation,
            ),
        ),
    )


def test_polling_adapter_normalizes_duplicates_and_acknowledges_after_checkpoint() -> None:
    occurrence = PluginTriggerOccurrence(
        sourceKey="message-42",
        partition="partition-a",
        payload={"value": 42},
    )
    emulator = PollingTriggerEmulator(
        batches=(
            PluginTriggerPollResult(
                occurrences=(occurrence,),
                checkpoint={"offset": 42},
                cursor="42",
            ),
        ),
        fault_plan=ConnectorFaultPlan(duplicateCount=2),
    )
    adapter = PluginPollingTriggerAdapter(
        _manifest(),
        frozenset({"vendor.events"}),
        emulator,
        requested_secret_scopes=("provider.token",),
        available_secrets={"provider.token": "scoped", "unrelated": "hidden"},
    )
    repository = _Repository()

    async def scenario() -> None:
        results = await TriggerRuntimeService(repository).poll_once(  # type: ignore[arg-type]
            _state(),
            TriggerDefinition(id="source", type="vendor.events"),
            adapter,
        )
        assert len(results) == 2
        assert [item.duplicate for item in results] == [False, True]
        assert repository.checkpoint == {"offset": 42}
        assert emulator.acknowledgements[0].cursor == "42"
        assert set(emulator.contexts[0].secrets) == {"provider.token"}
        assert repository.calls[-1] == "checkpoint:42"
        assert results[0].occurrence.occurrence_key == normalize_occurrence_key(
            "message-42", partition="partition-a"
        )

    asyncio.run(scenario())


def test_realtime_adapter_lifecycle_backpressure_and_durable_acknowledgement() -> None:
    occurrences = tuple(
        PluginTriggerOccurrence(sourceKey=f"live-{index}", payload={"index": index})
        for index in range(2)
    )
    emulator = RealtimeTriggerEmulator(occurrences)
    adapter = PluginRealtimeTriggerAdapter(
        _manifest(),
        frozenset({"vendor.events"}),
        emulator,
        policy=ExtensionCallPolicy(maxInFlight=1),
        requested_secret_scopes=("provider.token",),
        available_secrets={"provider.token": "scoped", "unrelated": "hidden"},
    )
    repository = _Repository()

    async def scenario() -> None:
        accepted = await TriggerRuntimeService(repository).consume_realtime(  # type: ignore[arg-type]
            _state(),
            TriggerDefinition(id="source", type="vendor.events"),
            adapter,
            limit=2,
        )
        assert len(accepted) == 2
        assert emulator.connections[0].acknowledged == ["live-0", "live-1"]
        assert emulator.connections[0].closed is True
        assert set(emulator.contexts[0].secrets) == {"provider.token"}

    asyncio.run(scenario())


def test_condition_validation_is_offline_and_evaluation_is_explainable_and_scoped() -> None:
    polling_emulator = PollingTriggerEmulator(())
    assert validate_extension_configuration(_manifest(), "events", {"threshold": "invalid"})
    assert polling_emulator.calls == 0

    emulator = ConditionEmulator(
        PluginConditionResult(
            matched=True,
            reason="threshold exceeded",
            evidence={"observed": 9, "threshold": 5},
        ),
        fault_plan=ConnectorFaultPlan(retryableFailures=(1,)),
    )
    evaluator = PluginConditionEvaluator(
        _manifest(),
        "condition",
        emulator,
        policy=ExtensionCallPolicy(maxAttempts=2, timeoutSeconds=1),
        requested_secret_scopes=("provider.token",),
        available_secrets={"provider.token": "scoped", "unrelated": "hidden"},
    )

    assert evaluator.validate({"threshold": "invalid"})
    assert emulator.calls == 0

    async def scenario() -> None:
        result = await evaluator.evaluate(
            PluginConditionRequest(
                configuration={"threshold": 5},
                input={"value": 9},
            )
        )
        assert result.matched is True
        assert result.reason == "threshold exceeded"
        assert result.evidence == {"observed": 9, "threshold": 5}
        assert emulator.calls == 2
        assert set(emulator.contexts[-1].secrets) == {"provider.token"}

    asyncio.run(scenario())


def test_notification_receives_typed_event_delivery_policy_and_retry() -> None:
    emulator = NotificationEmulator(
        PluginNotificationResult(
            delivered=True,
            providerId="provider-123",
            evidence={"status": 202},
        ),
        fault_plan=ConnectorFaultPlan(retryableFailures=(1,)),
    )
    dispatcher = PluginNotificationDispatcher(
        _manifest(),
        emulator,
        requested_secret_scopes=("provider.token",),
        available_secrets={"provider.token": "scoped", "unrelated": "hidden"},
    )
    request = PluginNotificationRequest(
        event=PluginLifecycleEvent(
            eventId="event-1",
            type=PluginLifecycleEventType.EXECUTION_FAILED,
            tenantId="default",
            namespace="tests.extensions",
            flowId="flow",
            executionId=str(uuid4()),
            occurredAt=datetime.now(UTC),
            payload={"reason": "fixture"},
        ),
        policy=PluginNotificationDeliveryPolicy(
            deliveryKey="event-1:notify",
            channel="operations",
            severity="ERROR",
            maxAttempts=2,
            timeoutSeconds=1,
            retryDelaySeconds=0,
        ),
    )

    async def scenario() -> None:
        result = await dispatcher.send(request)
        assert result.delivered is True
        assert result.provider_id == "provider-123"
        assert emulator.calls == 2
        assert emulator.deliveries == [request, request]
        assert set(emulator.contexts[-1].secrets) == {"provider.token"}

    asyncio.run(scenario())


def test_shared_extension_controller_applies_timeout_cancellation_and_faults() -> None:
    async def scenario() -> None:
        attempts = 0

        async def retry_once(context: ExtensionCallContext) -> str:
            nonlocal attempts
            del context
            attempts += 1
            if attempts == 1:
                raise ExtensionRetryableError("retry")
            return "ok"

        controller = ExtensionCallController(ExtensionCallPolicy(maxAttempts=2, timeoutSeconds=1))
        assert await controller.call(retry_once) == "ok"

        cancellation = asyncio.Event()
        cancellation.set()
        with pytest.raises(ExtensionCancelledError):
            await controller.call(retry_once, cancellation=cancellation)

        async def blocks(context: ExtensionCallContext) -> str:
            del context
            await asyncio.sleep(1)
            return "late"

        with pytest.raises(TimeoutError):
            await ExtensionCallController(ExtensionCallPolicy(timeoutSeconds=0.01)).call(blocks)

    asyncio.run(scenario())


def test_realtime_fault_fixture_disconnects_and_still_closes_connection() -> None:
    emulator = RealtimeTriggerEmulator(
        (
            PluginTriggerOccurrence(sourceKey="first"),
            PluginTriggerOccurrence(sourceKey="second"),
        ),
        fault_plan=ConnectorFaultPlan(disconnectAfter=1),
    )
    adapter = PluginRealtimeTriggerAdapter(_manifest(), frozenset({"vendor.events"}), emulator)

    async def scenario() -> None:
        with pytest.raises(ExtensionRetryableError):
            await TriggerRuntimeService(_Repository()).consume_realtime(  # type: ignore[arg-type]
                _state(),
                TriggerDefinition(id="source", type="vendor.events"),
                adapter,
                limit=2,
            )
        assert emulator.connections[0].acknowledged == ["first"]
        assert emulator.connections[0].closed is True

    asyncio.run(scenario())
