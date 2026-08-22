# Trigger, condition and notification extension contracts

AMESH publishes the `amesh.plugin.extension/v1` contract in
`schemas/plugin-extensions.schema.json`. The Python SDK exposes the same immutable models and
transport-neutral protocols. Connector implementations do not mutate platform state directly.

## Polling triggers

A polling extension receives the trigger definition, its last durable checkpoint and cursor, and a
bounded result limit. It returns source occurrences plus the next checkpoint. Each source identity
is normalized to a stable `plugin:v1:sha256:` key. The trigger runtime accepts every occurrence,
persists the new checkpoint, and only then calls the plugin acknowledgement hook. Repeated source
identities therefore converge on the platform deduplication record.

## Realtime triggers

A realtime extension opens a connection with an explicit maximum in-flight count. It yields typed
occurrences and accepts source-key acknowledgements only after platform persistence. The adapter
closes the connection after exhaustion, bounded consumption, cancellation or connector failure.
A retryable disconnect is surfaced to the caller so its scheduling policy can reconnect from the
last durable source position.

## Conditions and notifications

Conditions receive configuration, input and execution context and return `matched`, a human-readable
reason and structured evidence. `PluginConditionEvaluator.validate()` applies the manifest JSON
Schema locally before any connector call.

Notification plugins receive a typed execution or task lifecycle event and an explicit delivery key,
channel, severity, retry count, timeout and retry delay. The dispatcher applies that delivery policy
through the same call controller used by triggers and conditions.

## Shared call and capability policy

`ExtensionCallController` applies bounded attempts, per-attempt deadlines and cooperative
cancellation. Every adapter resolves only requested secret scopes declared by the manifest; missing
or undeclared scopes fail before invoking connector code. Plaintext secret values remain wrapped in
the call context and are excluded from model representations.

For local connector tests, `PollingTriggerEmulator`, `RealtimeTriggerEmulator`,
`ConditionEmulator` and `NotificationEmulator` record calls and acknowledgements.
`ConnectorFaultPlan` injects retryable failures, delays, realtime disconnects and duplicates.

```powershell
uv run pytest -q tests/plugins/test_extension_contracts.py tests/test_trigger_runtime.py
```
