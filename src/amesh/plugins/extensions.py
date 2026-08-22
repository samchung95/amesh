from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Mapping
from typing import Any

from amesh.plugin_sdk import PluginManifest
from amesh.plugin_sdk.errors import PluginContractError, PluginErrorDetail
from amesh.plugin_sdk.extensions import (
    ExtensionCallContext,
    ExtensionCallController,
    ExtensionCallPolicy,
    PluginConditionExtension,
    PluginConditionRequest,
    PluginConditionResult,
    PluginNotificationExtension,
    PluginNotificationRequest,
    PluginNotificationResult,
    PluginPollingRequest,
    PluginPollingTriggerExtension,
    PluginRealtimeRequest,
    PluginRealtimeTriggerConnection,
    PluginRealtimeTriggerExtension,
    PluginTriggerCheckpoint,
    scope_extension_secrets,
    validate_extension_configuration,
)
from amesh.ports import TriggerAdapterOccurrence, TriggerPollResult


class PluginPollingTriggerAdapter:
    """Bridges a typed plugin poller into the durable trigger runtime contract."""

    def __init__(
        self,
        manifest: PluginManifest,
        trigger_types: frozenset[str],
        extension: PluginPollingTriggerExtension,
        *,
        policy: ExtensionCallPolicy | None = None,
        requested_secret_scopes: tuple[str, ...] = (),
        available_secrets: Mapping[str, str] | None = None,
    ) -> None:
        self.trigger_types = trigger_types
        self._extension = extension
        self._controller = ExtensionCallController(policy or ExtensionCallPolicy())
        self._secrets = scope_extension_secrets(
            manifest.capabilities.secret_scopes,
            requested_secret_scopes,
            available_secrets or {},
        )

    async def poll(
        self,
        definition: dict[str, Any],
        *,
        checkpoint: dict[str, Any],
        cursor: str | None,
        limit: int,
    ) -> TriggerPollResult:
        request = PluginPollingRequest(
            definition=definition,
            checkpoint=checkpoint,
            cursor=cursor,
            limit=limit,
        )
        result = await self._controller.call(
            lambda context: self._extension.poll(request, context),
            secrets=self._secrets,
        )
        return TriggerPollResult(
            occurrences=tuple(
                TriggerAdapterOccurrence(
                    occurrence_key=item.occurrence_key,
                    payload=item.payload,
                    metadata={
                        **item.metadata,
                        "pluginSourceKey": item.source_key,
                        **({"pluginPartition": item.partition} if item.partition else {}),
                    },
                    observed_at=item.observed_at,
                )
                for item in result.occurrences
            ),
            checkpoint=result.checkpoint,
            cursor=result.cursor,
            next_evaluation_at=result.next_evaluation_at,
        )

    async def acknowledge(
        self,
        *,
        checkpoint: dict[str, Any],
        cursor: str | None,
    ) -> None:
        value = PluginTriggerCheckpoint(checkpoint=checkpoint, cursor=cursor)
        await self._controller.call(
            lambda context: self._extension.acknowledge(value, context),
            secrets=self._secrets,
        )


class PluginRealtimeTriggerAdapter:
    """Bridges a lifecycle-aware plugin stream with bounded in-flight acknowledgement."""

    def __init__(
        self,
        manifest: PluginManifest,
        trigger_types: frozenset[str],
        extension: PluginRealtimeTriggerExtension,
        *,
        policy: ExtensionCallPolicy | None = None,
        requested_secret_scopes: tuple[str, ...] = (),
        available_secrets: Mapping[str, str] | None = None,
    ) -> None:
        self.trigger_types = trigger_types
        self._extension = extension
        self._controller = ExtensionCallController(policy or ExtensionCallPolicy())
        self._secrets = scope_extension_secrets(
            manifest.capabilities.secret_scopes,
            requested_secret_scopes,
            available_secrets or {},
        )
        self._connection: PluginRealtimeTriggerConnection | None = None
        self._pending: dict[str, str] = {}

    async def subscribe(
        self,
        definition: dict[str, Any],
        *,
        checkpoint: dict[str, Any],
        cursor: str | None,
    ) -> AsyncIterator[TriggerAdapterOccurrence]:
        request = PluginRealtimeRequest(
            definition=definition,
            checkpoint=checkpoint,
            cursor=cursor,
            maxInFlight=self._controller.policy.max_in_flight,
        )
        connection = await self._controller.call(
            lambda context: self._extension.connect(request, context),
            secrets=self._secrets,
        )
        self._connection = connection
        try:
            async for item in connection:
                key = item.occurrence_key
                if key in self._pending:
                    raise RuntimeError("realtime plugin emitted a duplicate in-flight identity")
                self._pending[key] = item.source_key
                yield TriggerAdapterOccurrence(
                    occurrence_key=key,
                    payload=item.payload,
                    metadata={
                        **item.metadata,
                        "pluginSourceKey": item.source_key,
                        **({"pluginPartition": item.partition} if item.partition else {}),
                    },
                    observed_at=item.observed_at,
                )
        finally:
            await connection.close()
            self._connection = None
            self._pending.clear()

    async def acknowledge(self, occurrence_key: str) -> None:
        connection = self._connection
        source_key = self._pending.get(occurrence_key)
        if connection is None or source_key is None:
            raise ValueError("realtime plugin occurrence is not awaiting acknowledgement")

        async def acknowledge(context: ExtensionCallContext) -> None:
            del context
            await connection.acknowledge(source_key)

        await self._controller.call(acknowledge, secrets=self._secrets)
        self._pending.pop(occurrence_key, None)


class PluginConditionEvaluator:
    def __init__(
        self,
        manifest: PluginManifest,
        entry_point_name: str,
        extension: PluginConditionExtension,
        *,
        policy: ExtensionCallPolicy | None = None,
        requested_secret_scopes: tuple[str, ...] = (),
        available_secrets: Mapping[str, str] | None = None,
    ) -> None:
        self._manifest = manifest
        self._entry_point_name = entry_point_name
        self._extension = extension
        self._controller = ExtensionCallController(policy or ExtensionCallPolicy())
        self._requested_secret_scopes = requested_secret_scopes
        self._available_secrets = available_secrets or {}

    def validate(self, configuration: Mapping[str, Any]) -> tuple[PluginErrorDetail, ...]:
        return validate_extension_configuration(
            self._manifest,
            self._entry_point_name,
            configuration,
        )

    async def evaluate(
        self,
        request: PluginConditionRequest,
        *,
        cancellation: asyncio.Event | None = None,
    ) -> PluginConditionResult:
        errors = self.validate(request.configuration)
        if errors:
            raise PluginContractError(*errors)
        secrets = scope_extension_secrets(
            self._manifest.capabilities.secret_scopes,
            self._requested_secret_scopes,
            self._available_secrets,
        )
        return await self._controller.call(
            lambda context: self._extension.evaluate(request, context),
            secrets=secrets,
            cancellation=cancellation,
        )


class PluginNotificationDispatcher:
    def __init__(
        self,
        manifest: PluginManifest,
        extension: PluginNotificationExtension,
        *,
        requested_secret_scopes: tuple[str, ...] = (),
        available_secrets: Mapping[str, str] | None = None,
    ) -> None:
        self._manifest = manifest
        self._extension = extension
        self._requested_secret_scopes = requested_secret_scopes
        self._available_secrets = available_secrets or {}

    async def send(
        self,
        request: PluginNotificationRequest,
        *,
        cancellation: asyncio.Event | None = None,
    ) -> PluginNotificationResult:
        secrets = scope_extension_secrets(
            self._manifest.capabilities.secret_scopes,
            self._requested_secret_scopes,
            self._available_secrets,
        )
        controller = ExtensionCallController(
            ExtensionCallPolicy(
                maxAttempts=request.policy.max_attempts,
                timeoutSeconds=request.policy.timeout_seconds,
                retryDelaySeconds=request.policy.retry_delay_seconds,
            )
        )
        return await controller.call(
            lambda context: self._extension.send(request, context),
            secrets=secrets,
            cancellation=cancellation,
        )
