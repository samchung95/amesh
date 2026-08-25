from __future__ import annotations

import asyncio
import json
import os
import secrets
import shutil
import subprocess
from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import psutil
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from amesh.config import IsolatedPluginServiceConfig, Settings
from amesh.domain import FailureCategory
from amesh.dsl import TaskDefinition
from amesh.executor import (
    TaskArtifactRecord,
    TaskAssetRecord,
    TaskCancellationChannel,
    TaskCompletion,
    TaskConfigurationError,
    TaskExecutionContext,
    TaskExecutionFailure,
    TaskHandler,
    TaskLogRecord,
    TaskMetricRecord,
)
from amesh.observability import instrument_async_operation
from amesh.plugin_sdk import (
    ExtensionType,
    PluginCatalogManager,
    PluginDiscoveryResult,
    PluginFilesystemAccess,
    PluginHandshakeResult,
    PluginInvocationResult,
    PluginLifecycleStatus,
    PluginManifest,
    PluginMetric,
    PluginNetworkAccess,
    PluginOperation,
    PluginPackageRecord,
    PluginRequest,
    PluginResolution,
    PluginResponse,
    PluginSession,
    PluginTransport,
)
from amesh.plugin_sdk.errors import PluginErrorPhase
from amesh.plugin_sdk.wire import (
    PLUGIN_METHOD_CANCEL,
    PLUGIN_METHOD_DISCOVER,
    PLUGIN_METHOD_HANDSHAKE,
    PLUGIN_METHOD_INVOKE,
    PLUGIN_METHOD_SHUTDOWN,
    PLUGIN_METHOD_VALIDATE,
    PLUGIN_NOTIFICATION_ARTIFACT,
    PLUGIN_NOTIFICATION_ASSET,
    PLUGIN_NOTIFICATION_HEARTBEAT,
    PLUGIN_NOTIFICATION_LOG,
    PLUGIN_NOTIFICATION_METRIC,
    PLUGIN_WIRE_VERSION,
    REQUIRED_WIRE_FEATURES,
    JsonRpcNotification,
    JsonRpcRequest,
    JsonRpcResponse,
    PluginArtifact,
    PluginAsset,
    PluginAuthenticatedParams,
    PluginCapabilityEnvelope,
)
from amesh.ports import LogLevel, LogSourceStream, MetricKind

if TYPE_CHECKING:
    from amesh.domain import ToolDescriptor, ToolInvocationRequest, ToolProviderRef

    from .tool_provider import IsolatedPluginToolProvider

_TASK_STRUCTURE_FIELDS = {
    "id",
    "type",
    "description",
    "runLabels",
    "dependsOn",
    "runIf",
    "conditionErrorPolicy",
    "retry",
    "tasks",
    "condition",
    "then",
    "elseIf",
    "else",
    "cases",
    "predicateCases",
    "errors",
    "errorSelector",
    "contract",
    "taskCache",
}
_SAFE_ENVIRONMENT = ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LANG", "LC_ALL")


class IsolatedPluginState(StrEnum):
    READY = "ready"
    RUNNING = "running"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class IsolatedPluginRuntimeStatus(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    name: str
    version: str
    content_digest: str = Field(alias="contentDigest")
    launcher: str
    state: IsolatedPluginState
    active_calls: int = Field(default=0, alias="activeCalls")
    starts: int = 0
    restarts: int = 0
    crashes: int = 0
    completed: int = 0
    last_pid: int | None = Field(default=None, alias="lastPid")
    last_error_code: str | None = Field(default=None, alias="lastErrorCode")


class IsolatedPluginRuntimeSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    catalog_generation: int = Field(alias="catalogGeneration", ge=1)
    plugins: tuple[IsolatedPluginRuntimeStatus, ...]


class IsolatedPluginRuntimeError(TaskExecutionFailure):
    def __init__(self, message: str, category: FailureCategory, code: str) -> None:
        super().__init__(message, category, evidence={"code": code})
        self.code = code


@dataclass
class _Registration:
    profile: IsolatedPluginServiceConfig
    record: PluginPackageRecord
    root: Path
    task_entries: dict[str, str]
    semaphore: asyncio.Semaphore
    active_calls: int = 0
    starts: int = 0
    restarts: int = 0
    crashes: int = 0
    completed: int = 0
    last_pid: int | None = None
    last_error_code: str | None = None
    restart_pending: bool = False

    @property
    def manifest(self) -> PluginManifest:
        if self.record.manifest is None:
            raise RuntimeError("isolated plugin registration lost its manifest")
        return self.record.manifest

    @property
    def identity(self) -> tuple[str, str, str]:
        return (self.profile.name, self.profile.version, self.profile.content_digest)


@dataclass
class _Evidence:
    logs: list[TaskLogRecord] = field(default_factory=list)
    metrics: list[TaskMetricRecord] = field(default_factory=list)
    artifacts: list[TaskArtifactRecord] = field(default_factory=list)
    assets: list[TaskAssetRecord] = field(default_factory=list)


@dataclass
class _OutputBudget:
    maximum: int
    consumed: int = 0

    def add(self, amount: int) -> None:
        self.consumed += amount
        if self.consumed > self.maximum:
            raise IsolatedPluginRuntimeError(
                "isolated plugin exceeded its output limit",
                FailureCategory.USER_CODE,
                "plugin.isolated.output_limit",
            )


class _ToolCancellation(TaskCancellationChannel):
    def __init__(self) -> None:
        super().__init__()
        self._event = asyncio.Event()

    async def requested(self) -> bool:
        return self._event.is_set()

    async def wait(self, *, poll_interval: float = 0.05) -> None:
        del poll_interval
        await self._event.wait()

    def cancel(self) -> None:
        self._event.set()


class _PluginProcess:
    def __init__(
        self,
        process: asyncio.subprocess.Process,
        registration: _Registration,
        session_id: str,
        workload_token: str,
    ) -> None:
        self.process = process
        self.registration = registration
        self.session_id = session_id
        self.workload_token = workload_token
        self.budget = _OutputBudget(registration.profile.max_output_bytes)
        self.stderr_task = asyncio.create_task(self._drain_stderr())
        self.next_id = 1
        self.session_established = False

    async def send_request(self, method: str, params: dict[str, Any]) -> str:
        request_id = str(self.next_id)
        self.next_id += 1
        await self._write(JsonRpcRequest(id=request_id, method=method, params=params))
        return request_id

    async def send_notification(self, method: str, params: dict[str, Any]) -> None:
        await self._write(JsonRpcNotification(method=method, params=params))

    async def response(
        self,
        request_id: str,
        *,
        timeout_seconds: float,
        evidence: _Evidence | None = None,
    ) -> dict[str, Any]:
        while True:
            payload = await self._read_frame(timeout_seconds)
            if "id" not in payload:
                notification = JsonRpcNotification.model_validate(payload)
                self._authenticate(notification.params)
                if evidence is not None:
                    self._record_notification(notification, evidence)
                continue
            response = JsonRpcResponse.model_validate(payload)
            if response.id != request_id:
                raise IsolatedPluginRuntimeError(
                    "isolated plugin returned an unexpected response id",
                    FailureCategory.PLATFORM,
                    "plugin.isolated.response_id",
                )
            if response.error is not None:
                if self.session_established:
                    self._authenticate(response.error.data)
                raise IsolatedPluginRuntimeError(
                    response.error.message,
                    FailureCategory.USER_CODE,
                    "plugin.isolated.rpc_error",
                )
            if response.result is None:
                raise IsolatedPluginRuntimeError(
                    "isolated plugin returned an empty RPC result",
                    FailureCategory.PLATFORM,
                    "plugin.isolated.empty_result",
                )
            self._authenticate(response.result)
            return response.result

    async def close(self) -> None:
        self.stderr_task.cancel()
        with suppress(asyncio.CancelledError, IsolatedPluginRuntimeError):
            await self.stderr_task

    async def _write(self, value: BaseModel) -> None:
        if self.process.stdin is None:
            raise IsolatedPluginRuntimeError(
                "isolated plugin stdin is unavailable",
                FailureCategory.RETRYABLE,
                "plugin.isolated.stdin_unavailable",
            )
        payload = (
            json.dumps(
                value.model_dump(mode="json", by_alias=True, exclude_none=True),
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n"
        )
        self.process.stdin.write(payload)
        try:
            await self.process.stdin.drain()
        except (BrokenPipeError, ConnectionResetError) as exc:
            raise IsolatedPluginRuntimeError(
                "isolated plugin process exited while receiving a request",
                FailureCategory.RETRYABLE,
                "plugin.isolated.crashed",
            ) from exc

    async def _read_frame(self, timeout_seconds: float) -> dict[str, Any]:
        if self.process.stdout is None:
            raise IsolatedPluginRuntimeError(
                "isolated plugin stdout is unavailable",
                FailureCategory.RETRYABLE,
                "plugin.isolated.stdout_unavailable",
            )
        try:
            async with asyncio.timeout(timeout_seconds):
                line = await self.process.stdout.readline()
        except TimeoutError as exc:
            raise IsolatedPluginRuntimeError(
                "isolated plugin heartbeat timed out",
                FailureCategory.RETRYABLE,
                "plugin.isolated.heartbeat_timeout",
            ) from exc
        except ValueError as exc:
            raise IsolatedPluginRuntimeError(
                "isolated plugin emitted an oversized frame",
                FailureCategory.USER_CODE,
                "plugin.isolated.frame_limit",
            ) from exc
        if not line:
            raise IsolatedPluginRuntimeError(
                "isolated plugin process exited unexpectedly",
                FailureCategory.RETRYABLE,
                "plugin.isolated.crashed",
            )
        self.budget.add(len(line))
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise IsolatedPluginRuntimeError(
                "isolated plugin emitted invalid JSON",
                FailureCategory.USER_CODE,
                "plugin.isolated.invalid_json",
            ) from exc
        if not isinstance(payload, dict):
            raise IsolatedPluginRuntimeError(
                "isolated plugin emitted a non-object JSON-RPC frame",
                FailureCategory.USER_CODE,
                "plugin.isolated.invalid_frame",
            )
        return payload

    async def _drain_stderr(self) -> None:
        if self.process.stderr is None:
            return
        while line := await self.process.stderr.readline():
            self.budget.add(len(line))

    def _authenticate(self, params: Mapping[str, Any]) -> None:
        authenticated = PluginAuthenticatedParams.model_validate(
            {
                "sessionId": params.get("sessionId"),
                "workloadToken": params.get("workloadToken"),
                "invocationId": params.get("invocationId"),
            }
        )
        if authenticated.session_id != self.session_id or not secrets.compare_digest(
            authenticated.workload_token.get_secret_value(), self.workload_token
        ):
            raise IsolatedPluginRuntimeError(
                "isolated plugin workload identity mismatch",
                FailureCategory.PLATFORM,
                "plugin.isolated.identity_mismatch",
            )

    def _record_notification(self, notification: JsonRpcNotification, evidence: _Evidence) -> None:
        params = notification.params
        if notification.method == PLUGIN_NOTIFICATION_HEARTBEAT:
            return
        if notification.method == PLUGIN_NOTIFICATION_LOG:
            log = params.get("log")
            if not isinstance(log, dict):
                raise ValueError("plugin log notification is invalid")
            level = LogLevel(str(log.get("level", "INFO")))
            evidence.logs.append(
                TaskLogRecord(
                    level=level,
                    logger=f"plugin.{self.registration.profile.name}",
                    message=str(log.get("message", "")),
                    fields=dict(log.get("fields", {})),
                    sourceStream=LogSourceStream.PLUGIN,
                    occurredAt=log.get("occurredAt", datetime.now(UTC)),
                )
            )
            return
        if notification.method == PLUGIN_NOTIFICATION_METRIC:
            metric = PluginMetric.model_validate(params.get("metric"))
            evidence.metrics.append(
                TaskMetricRecord(
                    name=metric.name,
                    kind=MetricKind(metric.kind.upper()),
                    value=Decimal(str(metric.value)),
                    unit=metric.unit,
                    labels=metric.labels,
                )
            )
            return
        if notification.method == PLUGIN_NOTIFICATION_ARTIFACT:
            artifact = PluginArtifact.model_validate(params.get("artifact"))
            evidence.artifacts.append(TaskArtifactRecord.model_validate(artifact.model_dump()))
            return
        if notification.method == PLUGIN_NOTIFICATION_ASSET:
            asset = PluginAsset.model_validate(params.get("asset"))
            evidence.assets.append(TaskAssetRecord.model_validate(asset.model_dump()))
            return
        raise IsolatedPluginRuntimeError(
            "isolated plugin emitted an unknown notification",
            FailureCategory.PLATFORM,
            "plugin.isolated.unknown_notification",
        )


class IsolatedPluginRuntime:
    """Runs exact revision-pinned plugins in authenticated child processes."""

    def __init__(
        self,
        catalog: PluginCatalogManager,
        profiles: tuple[IsolatedPluginServiceConfig, ...],
        *,
        monitor_interval_seconds: float,
    ) -> None:
        self._catalog = catalog
        self._profiles = profiles
        self._monitor_interval_seconds = monitor_interval_seconds
        self._catalog_generation = catalog.snapshot.generation
        self._registrations: dict[tuple[str, str, str], _Registration] = {}
        self._unavailable: dict[tuple[str, str, str], IsolatedPluginRuntimeStatus] = {}
        self._tool_cancellations: dict[str, _ToolCancellation] = {}
        self._lock = asyncio.Lock()

    async def ensure_configured(self) -> None:
        async with self._lock:
            generation = self._catalog.snapshot.generation
            if generation == self._catalog_generation and (
                self._registrations or self._unavailable or not self._profiles
            ):
                return
            self._catalog_generation = generation
            self._registrations.clear()
            self._unavailable.clear()
            for profile in self._profiles:
                identity = (profile.name, profile.version, profile.content_digest)
                try:
                    self._registrations[identity] = self._registration(profile)
                except (RuntimeError, ValueError) as exc:
                    self._unavailable[identity] = IsolatedPluginRuntimeStatus(
                        name=profile.name,
                        version=profile.version,
                        contentDigest=profile.content_digest,
                        launcher=profile.launcher,
                        state=IsolatedPluginState.UNAVAILABLE,
                        lastErrorCode=type(exc).__name__,
                    )

    def task_handlers(
        self, resolution: PluginResolution | Mapping[str, object]
    ) -> dict[str, TaskHandler]:
        resolved = (
            resolution
            if isinstance(resolution, PluginResolution)
            else PluginResolution.model_validate(resolution)
        )
        handlers: dict[str, TaskHandler] = {}
        for pin in resolved.resources:
            if pin.kind is not ExtensionType.TASK:
                continue
            registration = self._registrations.get((pin.package, pin.version, pin.content_digest))
            if registration is None:
                continue
            entry_name = registration.task_entries.get(pin.type)
            if entry_name is None:
                continue
            if pin.type in handlers:
                raise RuntimeError(f"isolated task identity {pin.type!r} was already registered")
            handlers[pin.type] = self._task_handler(registration, entry_name)
        return handlers

    def tool_provider(
        self,
        identity: ToolProviderRef,
        tools: tuple[ToolDescriptor, ...],
    ) -> IsolatedPluginToolProvider:
        """Bind neutral tool calls to this runtime's isolated RPC boundary."""

        from .tool_provider import IsolatedPluginToolProvider

        return IsolatedPluginToolProvider(
            identity,
            tools,
            lambda request: self.invoke_tool(identity, request),
            cancel=self.cancel_tool,
        )

    async def invoke_tool(
        self,
        identity: ToolProviderRef,
        request: ToolInvocationRequest,
    ) -> dict[str, Any]:
        """Execute one manifest entry point through the existing child process."""

        from amesh.domain import ToolProviderKind

        if identity.kind is not ToolProviderKind.PLUGIN:
            raise ValueError("isolated runtime tool calls require a plugin provider")
        await self.ensure_configured()
        registrations = [
            item for item in self._registrations.values() if item.profile.name == identity.key
        ]
        if len(registrations) != 1:
            raise ValueError(
                f"plugin provider {identity.key!r} does not resolve to exactly one isolated revision"
            )
        registration = registrations[0]
        entry = next(
            (
                item
                for item in registration.manifest.entry_points
                if item.name == request.tool_name
                or item.resolved_resource_type == request.tool_name
            ),
            None,
        )
        if entry is None:
            raise LookupError(f"isolated plugin tool {request.tool_name!r} is unavailable")
        from amesh.plugin_sdk import (
            PluginCapabilityEnvelope,
            PluginOperation,
            PluginRequest,
            PluginSession,
        )

        capability_tokens = {
            capability: secrets.token_urlsafe(24)
            for capability in registration.manifest.capabilities.required
        }
        declared = registration.manifest.capabilities
        scoped_secrets = {
            scope: value
            for scope, value in zip(declared.secret_scopes, request.secret_values, strict=False)
        }
        context_secrets = {
            scope: value.get_secret_value() for scope, value in scoped_secrets.items()
        }
        capabilities = PluginCapabilityEnvelope(
            capabilityTokens={name: SecretStr(token) for name, token in capability_tokens.items()},
            secrets={name: value for name, value in scoped_secrets.items()},
            allowedEgress=(
                declared.allowed_egress
                if declared.network_access is PluginNetworkAccess.RESTRICTED
                else ()
            ),
            platformApis=registration.profile.platform_apis,
        )
        plugin_request = PluginRequest(
            plugin=registration.manifest.name,
            entryPoint=entry.name,
            operation=PluginOperation.EXECUTE,
            session=PluginSession(
                tenantId=request.tenant_id,
                invocationId=str(request.invocation_id),
                capabilityTokens={
                    name: SecretStr(token) for name, token in capability_tokens.items()
                },
            ),
            configuration=dict(request.arguments),
            input=dict(request.arguments),
            context={
                "executionId": str(request.execution_id),
                "taskRunId": str(request.task_run_id),
                "attempt": request.attempt,
            },
        )
        cancellation = _ToolCancellation()
        context = TaskExecutionContext(
            tenant_id=request.tenant_id,
            execution_id=request.execution_id,
            task_run_id=request.task_run_id,
            attempt=request.attempt,
            attempt_id=request.invocation_id,
            inputs=request.arguments,
            outputs={},
            variables={},
            namespace=request.namespace,
            secrets=context_secrets,
            cancellation=cancellation,
        )
        self._tool_cancellations[str(request.invocation_id)] = cancellation
        try:
            completion = await self._invoke(
                registration,
                plugin_request,
                capabilities,
                context,
            )
            return completion.output
        finally:
            self._tool_cancellations.pop(str(request.invocation_id), None)

    async def cancel_tool(self, invocation_id: str) -> None:
        cancellation = self._tool_cancellations.get(invocation_id)
        if cancellation is not None:
            cancellation.cancel()

    def snapshot(self) -> IsolatedPluginRuntimeSnapshot:
        statuses = [self._status(item) for item in self._registrations.values()]
        statuses.extend(self._unavailable.values())
        return IsolatedPluginRuntimeSnapshot(
            catalogGeneration=self._catalog_generation,
            plugins=tuple(
                sorted(statuses, key=lambda item: (item.name, item.version, item.content_digest))
            ),
        )

    def _registration(self, profile: IsolatedPluginServiceConfig) -> _Registration:
        record = next(
            (
                item
                for item in self._catalog.snapshot.packages
                if item.manifest is not None
                and item.manifest.name == profile.name
                and item.manifest.version == profile.version
                and item.content_digest == profile.content_digest
                and item.status in {PluginLifecycleStatus.ACTIVE, PluginLifecycleStatus.INSTALLED}
            ),
            None,
        )
        if record is None or record.manifest is None or record.content_path is None:
            raise ValueError("configured isolated plugin package is absent or unavailable")
        root = Path(record.content_path).resolve()
        if not root.is_dir():
            raise ValueError("configured isolated plugin package has no content root")
        if any(
            entry.transport is not PluginTransport.STDIO for entry in record.manifest.entry_points
        ):
            raise ValueError("local-process plugin entry points must use stdio transport")
        task_entries = {
            entry.resolved_resource_type: entry.name
            for entry in record.manifest.entry_points
            if entry.type is ExtensionType.TASK
        }
        return _Registration(
            profile=profile,
            record=record,
            root=root,
            task_entries=task_entries,
            semaphore=asyncio.Semaphore(profile.max_concurrency),
        )

    def _task_handler(self, registration: _Registration, entry_name: str) -> TaskHandler:
        async def handle(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
            payload = task.model_dump(
                mode="json", by_alias=True, exclude_none=True, exclude_defaults=True
            )
            configuration = {
                key: value
                for key, value in payload.items()
                if key not in _TASK_STRUCTURE_FIELDS and not key.startswith("x-")
            }
            capability_tokens = {
                capability: secrets.token_urlsafe(24)
                for capability in registration.manifest.capabilities.required
            }
            request = PluginRequest(
                plugin=registration.manifest.name,
                entryPoint=entry_name,
                operation=PluginOperation.EXECUTE,
                session=PluginSession(
                    tenantId=context.tenant_id,
                    invocationId=str(context.attempt_id),
                    capabilityTokens={
                        name: SecretStr(token) for name, token in capability_tokens.items()
                    },
                ),
                configuration=configuration,
                input=dict(context.inputs),
                context={
                    "executionId": str(context.execution_id),
                    "taskRunId": str(context.task_run_id),
                    "attempt": context.attempt,
                    "outputs": dict(context.outputs),
                    "variables": dict(context.variables),
                    "trigger": dict(context.trigger),
                },
            )
            capabilities = self._capabilities(registration, context, capability_tokens)
            return await self._invoke(registration, request, capabilities, context)

        return handle

    def _capabilities(
        self,
        registration: _Registration,
        context: TaskExecutionContext,
        capability_tokens: dict[str, str],
    ) -> PluginCapabilityEnvelope:
        declared = registration.manifest.capabilities
        secrets_for_call = {
            scope: SecretStr(context.secrets[scope])
            for scope in declared.secret_scopes
            if scope in context.secrets
        }
        files = (
            dict(context.files)
            if declared.filesystem_access is not PluginFilesystemAccess.NONE
            else {}
        )
        return PluginCapabilityEnvelope(
            capabilityTokens={name: SecretStr(token) for name, token in capability_tokens.items()},
            secrets=secrets_for_call,
            files=files,
            allowedEgress=(
                declared.allowed_egress
                if declared.network_access is PluginNetworkAccess.RESTRICTED
                else ()
            ),
            platformApis=registration.profile.platform_apis,
        )

    @instrument_async_operation("plugin", "outbound-call")
    async def _invoke(
        self,
        registration: _Registration,
        request: PluginRequest,
        capabilities: PluginCapabilityEnvelope,
        context: TaskExecutionContext,
    ) -> TaskCompletion:
        async with registration.semaphore:
            registration.active_calls += 1
            process: _PluginProcess | None = None
            crashed = False
            try:
                process = await self._start(registration)
                await self._handshake(process, registration)
                await self._discover(process, registration)
                invocation_payload = _invocation_payload(
                    process.session_id, process.workload_token, request, capabilities
                )
                validation_id = await process.send_request(
                    PLUGIN_METHOD_VALIDATE, invocation_payload
                )
                validation = PluginInvocationResult.model_validate(
                    await process.response(
                        validation_id,
                        timeout_seconds=registration.profile.startup_timeout_seconds,
                    )
                )
                self._raise_plugin_errors(validation.response)
                evidence = _Evidence()
                invocation_id = await process.send_request(PLUGIN_METHOD_INVOKE, invocation_payload)
                invocation_task = asyncio.create_task(
                    process.response(
                        invocation_id,
                        timeout_seconds=registration.profile.heartbeat_timeout_seconds,
                        evidence=evidence,
                    )
                )
                cancellation_task = asyncio.create_task(context.cancellation.wait())
                monitor_task = asyncio.create_task(self._monitor(process))
                try:
                    async with asyncio.timeout(registration.profile.wall_time_seconds):
                        result = await self._await_invocation(
                            process,
                            invocation_task,
                            cancellation_task,
                            monitor_task,
                            request.session.invocation_id,
                        )
                except TimeoutError as exc:
                    raise IsolatedPluginRuntimeError(
                        "isolated plugin exceeded its wall-time limit",
                        FailureCategory.TIMED_OUT,
                        "plugin.isolated.wall_time",
                    ) from exc
                finally:
                    for task_to_stop in (invocation_task, cancellation_task, monitor_task):
                        task_to_stop.cancel()
                    for task_to_stop in (invocation_task, cancellation_task, monitor_task):
                        with suppress(asyncio.CancelledError, IsolatedPluginRuntimeError):
                            await task_to_stop
                invocation = PluginInvocationResult.model_validate(result)
                self._raise_plugin_errors(invocation.response)
                registration.completed += 1
                registration.last_error_code = None
                return TaskCompletion(
                    output=invocation.response.output,
                    logs=tuple(evidence.logs),
                    metrics=tuple(evidence.metrics),
                    artifacts=tuple(evidence.artifacts),
                    assets=tuple(evidence.assets),
                )
            except IsolatedPluginRuntimeError as exc:
                registration.last_error_code = exc.code
                crashed = exc.code in {
                    "plugin.isolated.crashed",
                    "plugin.isolated.stdin_unavailable",
                    "plugin.isolated.stdout_unavailable",
                    "plugin.isolated.heartbeat_timeout",
                }
                if crashed:
                    registration.crashes += 1
                    registration.restart_pending = True
                raise
            finally:
                if process is not None:
                    await self._stop_process(process)
                registration.active_calls -= 1

    async def _await_invocation(
        self,
        process: _PluginProcess,
        invocation_task: asyncio.Task[dict[str, Any]],
        cancellation_task: asyncio.Task[None],
        monitor_task: asyncio.Task[None],
        invocation_id: str,
    ) -> dict[str, Any]:
        done, _ = await asyncio.wait(
            {invocation_task, cancellation_task, monitor_task, process.stderr_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        if invocation_task in done:
            return await invocation_task
        if monitor_task in done:
            await monitor_task
            return await invocation_task
        if process.stderr_task in done:
            await process.stderr_task
            return await invocation_task
        await process.send_notification(
            PLUGIN_METHOD_CANCEL,
            _authenticated_payload(process, {"invocationId": invocation_id}),
        )
        with suppress(TimeoutError, IsolatedPluginRuntimeError):
            async with asyncio.timeout(process.registration.profile.cancel_grace_seconds):
                await invocation_task
        raise IsolatedPluginRuntimeError(
            "isolated plugin invocation was cancelled",
            FailureCategory.CANCELLED,
            "plugin.isolated.cancelled",
        )

    async def _start(self, registration: _Registration) -> _PluginProcess:
        command = _resolve_command(registration.root, registration.profile.command)
        environment = {name: os.environ[name] for name in _SAFE_ENVIRONMENT if name in os.environ}
        environment.update(registration.profile.environment)
        environment["PYTHONNOUSERSITE"] = "1"
        keyword_arguments: dict[str, Any] = {}
        if os.name == "nt":
            keyword_arguments["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else:
            keyword_arguments["start_new_session"] = True
        try:
            child = await asyncio.create_subprocess_exec(
                *command,
                cwd=registration.root,
                env=environment,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=min(registration.profile.max_output_bytes, 1024 * 1024),
                **keyword_arguments,
            )
        except OSError as exc:
            raise IsolatedPluginRuntimeError(
                "isolated plugin process could not be started",
                FailureCategory.RETRYABLE,
                "plugin.isolated.start_failed",
            ) from exc
        registration.starts += 1
        if registration.restart_pending:
            registration.restarts += 1
            registration.restart_pending = False
        registration.last_pid = child.pid
        session_id = secrets.token_urlsafe(18)
        return _PluginProcess(child, registration, session_id, secrets.token_urlsafe(32))

    async def _handshake(self, process: _PluginProcess, registration: _Registration) -> None:
        request_id = await process.send_request(
            PLUGIN_METHOD_HANDSHAKE,
            {
                "protocolVersions": [PLUGIN_WIRE_VERSION],
                "requiredFeatures": [feature.value for feature in REQUIRED_WIRE_FEATURES],
                "plugin": registration.profile.name,
                "version": registration.profile.version,
                "contentDigest": registration.profile.content_digest,
                "sessionId": process.session_id,
                "workloadToken": process.workload_token,
                "expiresAt": (
                    datetime.now(UTC) + timedelta(seconds=registration.profile.token_ttl_seconds)
                ).isoformat(),
            },
        )
        ready = PluginHandshakeResult.model_validate(
            await process.response(
                request_id,
                timeout_seconds=registration.profile.startup_timeout_seconds,
            )
        )
        if (
            ready.protocol_version != PLUGIN_WIRE_VERSION
            or set(REQUIRED_WIRE_FEATURES).difference(ready.features)
            or ready.plugin != registration.profile.name
            or ready.version != registration.profile.version
            or ready.content_digest != registration.profile.content_digest
            or ready.session_id != process.session_id
            or not secrets.compare_digest(
                ready.workload_token.get_secret_value(), process.workload_token
            )
        ):
            raise IsolatedPluginRuntimeError(
                "isolated plugin failed protocol negotiation",
                FailureCategory.CONFIGURATION,
                "plugin.isolated.negotiation_failed",
            )
        process.session_established = True

    async def _discover(self, process: _PluginProcess, registration: _Registration) -> None:
        request_id = await process.send_request(
            PLUGIN_METHOD_DISCOVER,
            _authenticated_payload(process),
        )
        discovery = PluginDiscoveryResult.model_validate(
            await process.response(
                request_id,
                timeout_seconds=registration.profile.startup_timeout_seconds,
            )
        )
        actual = tuple(
            entry.model_dump(mode="json", by_alias=True, exclude_none=True)
            for entry in discovery.entry_points
        )
        expected = tuple(
            {
                "name": entry.name,
                "type": entry.type.value,
                "resourceType": entry.resolved_resource_type,
                "configurationSchema": entry.configuration_schema,
                **(
                    {"outputSchema": entry.output_schema} if entry.output_schema is not None else {}
                ),
            }
            for entry in registration.manifest.entry_points
        )
        if actual != expected:
            raise IsolatedPluginRuntimeError(
                "isolated plugin discovery does not match its signed manifest",
                FailureCategory.CONFIGURATION,
                "plugin.isolated.discovery_mismatch",
            )

    async def _monitor(self, process: _PluginProcess) -> None:
        profile = process.registration.profile
        while process.process.returncode is None:
            try:
                root = psutil.Process(process.process.pid)
                processes = (root, *root.children(recursive=True))
                memory = sum(item.memory_info().rss for item in processes if item.is_running())
                cpu = sum(
                    item.cpu_times().user + item.cpu_times().system
                    for item in processes
                    if item.is_running()
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return
            if profile.memory_bytes is not None and memory > profile.memory_bytes:
                raise IsolatedPluginRuntimeError(
                    "isolated plugin exceeded its memory limit",
                    FailureCategory.USER_CODE,
                    "plugin.isolated.memory_limit",
                )
            if profile.cpu_seconds is not None and cpu > profile.cpu_seconds:
                raise IsolatedPluginRuntimeError(
                    "isolated plugin exceeded its CPU limit",
                    FailureCategory.USER_CODE,
                    "plugin.isolated.cpu_limit",
                )
            await asyncio.sleep(self._monitor_interval_seconds)

    async def _stop_process(self, process: _PluginProcess) -> None:
        if process.process.returncode is None:
            with suppress(IsolatedPluginRuntimeError):
                await process.send_notification(
                    PLUGIN_METHOD_SHUTDOWN,
                    _authenticated_payload(process),
                )
            with suppress(TimeoutError):
                async with asyncio.timeout(process.registration.profile.cancel_grace_seconds):
                    await process.process.wait()
        if process.process.returncode is None:
            await asyncio.to_thread(_terminate_tree, process.process.pid)
            with suppress(TimeoutError):
                async with asyncio.timeout(2):
                    await process.process.wait()
        await process.close()

    def _raise_plugin_errors(self, response: PluginResponse) -> None:
        if not response.errors:
            return
        message = "; ".join(error.message for error in response.errors)
        if any(
            error.phase
            in {
                PluginErrorPhase.CONFIGURATION,
                PluginErrorPhase.COMPATIBILITY,
                PluginErrorPhase.CAPABILITY,
            }
            for error in response.errors
        ):
            raise TaskConfigurationError(message)
        raise IsolatedPluginRuntimeError(
            message,
            FailureCategory.USER_CODE,
            "plugin.isolated.plugin_error",
        )

    def _status(self, registration: _Registration) -> IsolatedPluginRuntimeStatus:
        state = (
            IsolatedPluginState.RUNNING
            if registration.active_calls
            else (
                IsolatedPluginState.DEGRADED
                if registration.last_error_code is not None
                else IsolatedPluginState.READY
            )
        )
        return IsolatedPluginRuntimeStatus(
            name=registration.profile.name,
            version=registration.profile.version,
            contentDigest=registration.profile.content_digest,
            launcher=registration.profile.launcher,
            state=state,
            activeCalls=registration.active_calls,
            starts=registration.starts,
            restarts=registration.restarts,
            crashes=registration.crashes,
            completed=registration.completed,
            lastPid=registration.last_pid,
            lastErrorCode=registration.last_error_code,
        )


def build_isolated_runtime(
    settings: Settings,
    catalog: PluginCatalogManager,
) -> IsolatedPluginRuntime:
    return IsolatedPluginRuntime(
        catalog,
        settings.isolated_plugin_services,
        monitor_interval_seconds=settings.isolated_plugin_monitor_interval_seconds,
    )


def _authenticated_payload(
    process: _PluginProcess,
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "sessionId": process.session_id,
        "workloadToken": process.workload_token,
        **(payload or {}),
    }


def _invocation_payload(
    session_id: str,
    workload_token: str,
    request: PluginRequest,
    capabilities: PluginCapabilityEnvelope,
) -> dict[str, Any]:
    request_payload = request.model_dump(mode="json", by_alias=True, exclude_none=True)
    request_payload["session"]["capabilityTokens"] = {
        name: token.get_secret_value() for name, token in request.session.capability_tokens.items()
    }
    capability_payload = capabilities.model_dump(mode="json", by_alias=True, exclude_none=True)
    capability_payload["capabilityTokens"] = {
        name: token.get_secret_value() for name, token in capabilities.capability_tokens.items()
    }
    capability_payload["secrets"] = {
        name: value.get_secret_value() for name, value in capabilities.secrets.items()
    }
    return {
        "sessionId": session_id,
        "workloadToken": workload_token,
        "request": request_payload,
        "capabilities": capability_payload,
    }


def _resolve_command(root: Path, configured: tuple[str, ...]) -> tuple[str, ...]:
    resolved: list[str] = []
    for index, value in enumerate(configured):
        candidate = (root / value).resolve()
        if candidate.is_relative_to(root) and candidate.exists():
            resolved.append(str(candidate))
            continue
        if index == 0 and not Path(value).is_absolute():
            executable = shutil.which(value)
            if executable is not None:
                resolved.append(executable)
                continue
        resolved.append(value)
    return tuple(resolved)


def _terminate_tree(pid: int) -> None:
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    processes = (*parent.children(recursive=True), parent)
    for process in processes:
        with suppress(psutil.NoSuchProcess):
            process.terminate()
    _, alive = psutil.wait_procs(processes, timeout=1)
    for process in alive:
        with suppress(psutil.NoSuchProcess):
            process.kill()
