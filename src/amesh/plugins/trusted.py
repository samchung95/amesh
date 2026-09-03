from __future__ import annotations

import asyncio
import importlib.util
import inspect
import sys
import types
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from time import monotonic, perf_counter
from typing import Any

import psutil
from pydantic import BaseModel, ConfigDict, Field

from amesh.config import Settings, TrustedPluginApproval
from amesh.dsl import TaskDefinition
from amesh.dsl.task_configuration import TASK_STRUCTURAL_FIELDS
from amesh.executor import (
    TaskConfigurationError,
    TaskExecutionContext,
    TaskHandler,
    TaskPlatformError,
)
from amesh.observability import (
    PLUGIN_CALLBACK_DURATION,
    PLUGIN_CALLBACK_ERRORS,
    PLUGIN_CALLBACKS,
    PLUGIN_CIRCUIT_OPEN,
    PLUGIN_MEMORY_BYTES,
    PLUGIN_QUARANTINES,
    instrument_async_operation,
)
from amesh.plugin_sdk import (
    ExtensionType,
    PluginCapabilityGrant,
    PluginCatalogManager,
    PluginDiscoverySource,
    PluginLifecycleStatus,
    PluginOperation,
    PluginPackageRecord,
    PluginRegistryPolicy,
    PluginRequest,
    PluginResolution,
    PluginResponse,
    PluginSession,
    PluginSourceKind,
)
from amesh.plugin_sdk.errors import PluginErrorDetail, PluginErrorPhase
from amesh.plugin_sdk.harness import PluginContractHarness, PluginHandler

_INVARIANT_CODES = {
    "plugin.runtime.invocation_mismatch",
    "plugin.runtime.timeout",
    "plugin.runtime.unhandled",
}


class TrustedPluginState(StrEnum):
    REGISTERED = "registered"
    STARTING = "starting"
    ACTIVE = "active"
    STOPPING = "stopping"
    STOPPED = "stopped"
    QUARANTINED = "quarantined"


class TrustedCircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"


class TrustedPluginRuntimeStatus(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    name: str
    version: str
    content_digest: str = Field(alias="contentDigest")
    namespace: str | None = None
    state: TrustedPluginState
    circuit: TrustedCircuitState
    callbacks: int = 0
    errors: int = 0
    consecutive_failures: int = Field(default=0, alias="consecutiveFailures")
    invariant_violations: int = Field(default=0, alias="invariantViolations")
    average_latency_ms: float = Field(default=0, alias="averageLatencyMs")
    owned_memory_bytes: int | None = Field(default=None, alias="ownedMemoryBytes")
    process_memory_bytes: int | None = Field(default=None, alias="processMemoryBytes")
    last_error_code: str | None = Field(default=None, alias="lastErrorCode")


class TrustedPluginRuntimeSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    catalog_generation: int = Field(alias="catalogGeneration", ge=1)
    plugins: tuple[TrustedPluginRuntimeStatus, ...]


class TrustedPluginLifecycleContext(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    name: str
    version: str
    content_digest: str = Field(alias="contentDigest")
    namespace: str


LifecycleHook = Callable[[TrustedPluginLifecycleContext], Awaitable[None]]
MemoryHook = Callable[[], int]


@dataclass
class _Registration:
    record: PluginPackageRecord
    namespace: str
    harness: PluginContractHarness
    task_entries: dict[str, str]
    start_hook: LifecycleHook | None
    stop_hook: LifecycleHook | None
    memory_hook: MemoryHook | None
    state: TrustedPluginState = TrustedPluginState.REGISTERED
    circuit: TrustedCircuitState = TrustedCircuitState.CLOSED
    callbacks: int = 0
    errors: int = 0
    consecutive_failures: int = 0
    invariant_violations: int = 0
    latency_seconds: float = 0
    owned_memory_bytes: int | None = None
    process_memory_bytes: int | None = None
    last_error_code: str | None = None
    opened_at: float | None = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    @property
    def identity(self) -> tuple[str, str, str]:
        manifest = self.record.manifest
        if manifest is None or self.record.content_digest is None:
            raise RuntimeError("trusted registration lost its immutable identity")
        return manifest.name, manifest.version, self.record.content_digest


class TrustedPluginRuntime:
    """Runs exact administrator-approved Python plugins inside private import namespaces."""

    def __init__(
        self,
        catalog: PluginCatalogManager,
        approvals: tuple[TrustedPluginApproval, ...],
        *,
        callback_timeout_seconds: float,
        lifecycle_timeout_seconds: float,
        failure_threshold: int,
        reset_seconds: float,
        quarantine_threshold: int,
    ) -> None:
        self._catalog = catalog
        self._approvals = approvals
        self._callback_timeout_seconds = callback_timeout_seconds
        self._lifecycle_timeout_seconds = lifecycle_timeout_seconds
        self._failure_threshold = failure_threshold
        self._reset_seconds = reset_seconds
        self._quarantine_threshold = quarantine_threshold
        self._registrations: dict[tuple[str, str, str], _Registration] = {}
        self._failed: dict[tuple[str, str, str], TrustedPluginRuntimeStatus] = {}
        self._resource_owners: dict[tuple[ExtensionType, str], str] = {}
        self._lock = asyncio.Lock()
        self._catalog_generation = catalog.snapshot.generation

    async def ensure_started(self) -> None:
        async with self._lock:
            generation = self._catalog.snapshot.generation
            if generation != self._catalog_generation:
                self._failed.clear()
            self._catalog_generation = generation
            for approval in self._approvals:
                identity = (approval.name, approval.version, approval.content_digest)
                if identity in self._registrations or identity in self._failed:
                    continue
                registration: _Registration | None = None
                try:
                    registration = self._load_approved(approval)
                    await self._start(registration)
                    self._registrations[identity] = registration
                except Exception as exc:
                    _unload_namespace(
                        registration.namespace
                        if registration is not None
                        else _namespace_for(approval.content_digest)
                    )
                    self._rebuild_resource_owners()
                    self._failed[identity] = TrustedPluginRuntimeStatus(
                        name=approval.name,
                        version=approval.version,
                        contentDigest=approval.content_digest,
                        state=TrustedPluginState.QUARANTINED,
                        circuit=TrustedCircuitState.OPEN,
                        errors=1,
                        invariantViolations=1,
                        lastErrorCode=_registration_error_code(exc),
                    )
                    PLUGIN_QUARANTINES.labels(
                        approval.name,
                        approval.version,
                        "registration",
                    ).inc()

    async def stop(self) -> None:
        async with self._lock:
            for registration in reversed(tuple(self._registrations.values())):
                await self._stop(registration)

    @instrument_async_operation("plugin", "callback")
    async def invoke(
        self, request: PluginRequest, *, version: str, content_digest: str
    ) -> PluginResponse:
        registration = self._registrations.get((request.plugin, version, content_digest))
        if registration is None:
            return _error_response(
                request,
                "plugin.runtime.not_approved",
                "the exact plugin package is not approved for in-process execution",
            )
        async with registration.lock:
            if registration.state is TrustedPluginState.QUARANTINED:
                return _error_response(
                    request,
                    "plugin.runtime.quarantined",
                    "the plugin package is quarantined",
                )
            if registration.state is not TrustedPluginState.ACTIVE:
                return _error_response(
                    request,
                    "plugin.runtime.not_active",
                    "the plugin package is not active",
                )
            if registration.circuit is TrustedCircuitState.OPEN:
                if (
                    registration.opened_at is not None
                    and monotonic() - registration.opened_at >= self._reset_seconds
                ):
                    registration.circuit = TrustedCircuitState.HALF_OPEN
                    self._set_circuit_metric(registration)
                else:
                    return _error_response(
                        request,
                        "plugin.runtime.circuit_open",
                        "the plugin callback circuit is open",
                        retryable=True,
                    )

            started = perf_counter()
            response: PluginResponse
            try:
                async with asyncio.timeout(self._callback_timeout_seconds):
                    response = await registration.harness.invoke(request)
            except TimeoutError:
                response = _error_response(
                    request,
                    "plugin.runtime.timeout",
                    "the plugin callback exceeded its configured timeout",
                    retryable=True,
                )
            except Exception:
                response = _error_response(
                    request,
                    "plugin.runtime.unhandled",
                    "the plugin runtime failed",
                )
            elapsed = perf_counter() - started
            await self._record_callback(registration, request, response, elapsed)
            return response

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
                raise RuntimeError(f"trusted task identity {pin.type!r} was already registered")
            handlers[pin.type] = self._task_handler(registration, entry_name)
        return handlers

    def snapshot(self) -> TrustedPluginRuntimeSnapshot:
        statuses = [self._status(item) for item in self._registrations.values()]
        statuses.extend(self._failed.values())
        return TrustedPluginRuntimeSnapshot(
            catalogGeneration=self._catalog_generation,
            plugins=tuple(
                sorted(statuses, key=lambda item: (item.name, item.version, item.content_digest))
            ),
        )

    def _load_approved(self, approval: TrustedPluginApproval) -> _Registration:
        record = next(
            (
                item
                for item in self._catalog.snapshot.packages
                if item.manifest is not None
                and item.manifest.name == approval.name
                and item.manifest.version == approval.version
                and item.content_digest == approval.content_digest
                and item.status in {PluginLifecycleStatus.ACTIVE, PluginLifecycleStatus.INSTALLED}
            ),
            None,
        )
        if record is None or record.manifest is None or record.content_path is None:
            raise ValueError("approved package is absent or unavailable")
        root = Path(record.content_path).resolve()
        if not root.is_dir():
            raise ValueError("approved package does not have a local content root")
        namespace = _namespace_for(approval.content_digest)
        modules: dict[Path, types.ModuleType] = {}
        handlers: dict[tuple[str, PluginOperation], PluginHandler] = {}
        task_entries: dict[str, str] = {}
        for entry in record.manifest.entry_points:
            module_path, attribute = _python_target(root, entry.target)
            module = modules.get(module_path)
            if module is None:
                module = _load_module(namespace, root, module_path)
                modules[module_path] = module
            handler = getattr(module, attribute, None)
            if handler is None or not callable(handler) or not inspect.iscoroutinefunction(handler):
                raise ValueError(f"entry point {entry.name!r} must target an async callable")
            operation = _operation_for(entry.type)
            handlers[(entry.name, operation)] = handler
            if entry.type is ExtensionType.TASK:
                task_entries[entry.resolved_resource_type] = entry.name

        start_hook = _single_hook(modules.values(), "plugin_start", asynchronous=True)
        stop_hook = _single_hook(modules.values(), "plugin_stop", asynchronous=True)
        memory_hook = _single_hook(modules.values(), "plugin_memory_bytes", asynchronous=False)
        grant = PluginCapabilityGrant(
            capabilities=record.manifest.capabilities.required,
            networkAccess=record.manifest.capabilities.network_access,
            allowedEgress=record.manifest.capabilities.allowed_egress,
            filesystemAccess=record.manifest.capabilities.filesystem_access,
            secretScopes=record.manifest.capabilities.secret_scopes,
        )
        registration = _Registration(
            record=record,
            namespace=namespace,
            harness=PluginContractHarness(record.manifest, handlers, grant=grant),
            task_entries=task_entries,
            start_hook=start_hook,
            stop_hook=stop_hook,
            memory_hook=memory_hook,
        )
        for resource_type in task_entries:
            key = (ExtensionType.TASK, resource_type)
            owner = self._resource_owners.get(key)
            if owner is not None and owner != record.manifest.name:
                raise ValueError(
                    f"resource identity task/{resource_type} is already owned by {owner}"
                )
            self._resource_owners[key] = record.manifest.name
        return registration

    async def _start(self, registration: _Registration) -> None:
        registration.state = TrustedPluginState.STARTING
        if registration.start_hook is not None:
            context = self._lifecycle_context(registration)
            async with asyncio.timeout(self._lifecycle_timeout_seconds):
                await registration.start_hook(context)
        registration.state = TrustedPluginState.ACTIVE
        await self._observe_memory(registration)

    async def _stop(self, registration: _Registration) -> None:
        if registration.state is TrustedPluginState.STOPPED:
            return
        if registration.state is not TrustedPluginState.QUARANTINED:
            registration.state = TrustedPluginState.STOPPING
        try:
            if registration.stop_hook is not None:
                async with asyncio.timeout(self._lifecycle_timeout_seconds):
                    await registration.stop_hook(self._lifecycle_context(registration))
        except Exception:
            registration.errors += 1
            registration.last_error_code = "plugin.runtime.lifecycle_stop"
        finally:
            if registration.state is not TrustedPluginState.QUARANTINED:
                registration.state = TrustedPluginState.STOPPED
            _unload_namespace(registration.namespace)

    def _task_handler(self, registration: _Registration, entry_name: str) -> TaskHandler:
        manifest = registration.record.manifest
        digest = registration.record.content_digest
        if manifest is None or digest is None:
            raise RuntimeError("trusted registration lost its immutable identity")

        async def handle(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
            payload = task.model_dump(
                mode="json",
                by_alias=True,
                exclude_none=True,
                exclude_defaults=True,
            )
            configuration = {
                key: value
                for key, value in payload.items()
                if key not in TASK_STRUCTURAL_FIELDS and not key.startswith("x-")
            }
            request = PluginRequest(
                plugin=manifest.name,
                entryPoint=entry_name,
                operation=PluginOperation.EXECUTE,
                session=PluginSession(
                    tenantId=context.tenant_id,
                    invocationId=str(context.attempt_id),
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
            response = await self.invoke(
                request,
                version=manifest.version,
                content_digest=digest,
            )
            if response.errors:
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
                raise TaskPlatformError(message)
            return response.output

        return handle

    async def _record_callback(
        self,
        registration: _Registration,
        request: PluginRequest,
        response: PluginResponse,
        elapsed: float,
    ) -> None:
        manifest = registration.record.manifest
        if manifest is None:
            return
        registration.callbacks += 1
        registration.latency_seconds += elapsed
        outcome = "success" if response.succeeded else "error"
        PLUGIN_CALLBACKS.labels(
            manifest.name,
            manifest.version,
            request.entry_point,
            request.operation.value,
            outcome,
        ).inc()
        PLUGIN_CALLBACK_DURATION.labels(
            manifest.name,
            manifest.version,
            request.entry_point,
            request.operation.value,
        ).observe(elapsed)
        if response.errors:
            registration.errors += 1
            registration.last_error_code = response.errors[0].code
            runtime_failure = any(
                error.phase is PluginErrorPhase.RUNTIME for error in response.errors
            )
            registration.consecutive_failures = (
                registration.consecutive_failures + 1 if runtime_failure else 0
            )
            for error in response.errors:
                PLUGIN_CALLBACK_ERRORS.labels(manifest.name, manifest.version, error.code).inc()
                if error.code in _INVARIANT_CODES:
                    registration.invariant_violations += 1
            if registration.invariant_violations >= self._quarantine_threshold:
                registration.state = TrustedPluginState.QUARANTINED
                registration.circuit = TrustedCircuitState.OPEN
                registration.opened_at = monotonic()
                PLUGIN_QUARANTINES.labels(
                    manifest.name,
                    manifest.version,
                    registration.last_error_code or "invariant",
                ).inc()
            elif registration.consecutive_failures >= self._failure_threshold:
                registration.circuit = TrustedCircuitState.OPEN
                registration.opened_at = monotonic()
        else:
            registration.consecutive_failures = 0
            registration.circuit = TrustedCircuitState.CLOSED
            registration.opened_at = None
        self._set_circuit_metric(registration)
        await self._observe_memory(registration)
        if (
            registration.state is not TrustedPluginState.QUARANTINED
            and registration.invariant_violations >= self._quarantine_threshold
        ):
            registration.state = TrustedPluginState.QUARANTINED
            registration.circuit = TrustedCircuitState.OPEN
            registration.opened_at = monotonic()
            PLUGIN_QUARANTINES.labels(
                manifest.name,
                manifest.version,
                registration.last_error_code or "invariant",
            ).inc()
            self._set_circuit_metric(registration)

    async def _observe_memory(self, registration: _Registration) -> None:
        manifest = registration.record.manifest
        if manifest is None:
            return
        registration.process_memory_bytes = psutil.Process().memory_info().rss
        PLUGIN_MEMORY_BYTES.labels(manifest.name, manifest.version, "host-process").set(
            registration.process_memory_bytes
        )
        if registration.memory_hook is not None:
            try:
                async with asyncio.timeout(self._callback_timeout_seconds):
                    owned = await asyncio.to_thread(registration.memory_hook)
                if isinstance(owned, bool) or not isinstance(owned, int) or owned < 0:
                    raise ValueError("plugin_memory_bytes must return a non-negative integer")
                registration.owned_memory_bytes = owned
                PLUGIN_MEMORY_BYTES.labels(manifest.name, manifest.version, "plugin-owned").set(
                    owned
                )
            except Exception:
                registration.errors += 1
                registration.invariant_violations += 1
                registration.last_error_code = "plugin.runtime.memory_hook"

    def _set_circuit_metric(self, registration: _Registration) -> None:
        manifest = registration.record.manifest
        if manifest is not None:
            PLUGIN_CIRCUIT_OPEN.labels(manifest.name, manifest.version).set(
                0 if registration.circuit is TrustedCircuitState.CLOSED else 1
            )

    def _status(self, registration: _Registration) -> TrustedPluginRuntimeStatus:
        manifest = registration.record.manifest
        digest = registration.record.content_digest
        if manifest is None or digest is None:
            raise RuntimeError("trusted registration lost its immutable identity")
        return TrustedPluginRuntimeStatus(
            name=manifest.name,
            version=manifest.version,
            contentDigest=digest,
            namespace=registration.namespace,
            state=registration.state,
            circuit=registration.circuit,
            callbacks=registration.callbacks,
            errors=registration.errors,
            consecutiveFailures=registration.consecutive_failures,
            invariantViolations=registration.invariant_violations,
            averageLatencyMs=(
                registration.latency_seconds / registration.callbacks * 1000
                if registration.callbacks
                else 0
            ),
            ownedMemoryBytes=registration.owned_memory_bytes,
            processMemoryBytes=registration.process_memory_bytes,
            lastErrorCode=registration.last_error_code,
        )

    def _rebuild_resource_owners(self) -> None:
        self._resource_owners.clear()
        for registration in self._registrations.values():
            manifest = registration.record.manifest
            if manifest is None:
                continue
            for resource_type in registration.task_entries:
                self._resource_owners[(ExtensionType.TASK, resource_type)] = manifest.name

    @staticmethod
    def _lifecycle_context(registration: _Registration) -> TrustedPluginLifecycleContext:
        manifest = registration.record.manifest
        digest = registration.record.content_digest
        if manifest is None or digest is None:
            raise RuntimeError("trusted registration lost its immutable identity")
        return TrustedPluginLifecycleContext(
            name=manifest.name,
            version=manifest.version,
            contentDigest=digest,
            namespace=registration.namespace,
        )


def build_plugin_catalog(settings: Settings) -> PluginCatalogManager:
    sources = (
        *(
            PluginDiscoverySource(kind=PluginSourceKind.DIRECTORY, location=location)
            for location in settings.plugin_directories
        ),
        *(
            PluginDiscoverySource(kind=PluginSourceKind.REGISTRY, location=location)
            for location in settings.plugin_registries
        ),
    )
    verification_keys = {
        key_id: secret.get_secret_value().encode("utf-8")
        for key_id, secret in settings.plugin_registry_verification_keys.items()
    }
    verification_keys[settings.plugin_registry_signing_key_id] = (
        settings.plugin_registry_signing_key.get_secret_value().encode("utf-8")
    )
    return PluginCatalogManager(
        sources=sources,
        install_root=settings.plugin_install_root,
        registry_timeout_seconds=settings.plugin_registry_timeout_seconds,
        registry_policy=PluginRegistryPolicy(
            allowedOrigins=settings.plugin_registry_allowed_origins,
            mirrors=settings.plugin_registry_mirrors,
            proxyUrl=settings.plugin_registry_proxy_url,
            offline=settings.plugin_registry_offline,
        ),
        registry_verification_keys=verification_keys,
        require_registry_signatures=settings.plugin_trust_mode == "signed-only",
    )


def build_trusted_runtime(
    settings: Settings,
    catalog: PluginCatalogManager,
) -> TrustedPluginRuntime:
    return TrustedPluginRuntime(
        catalog,
        settings.trusted_plugin_approvals,
        callback_timeout_seconds=settings.trusted_plugin_callback_timeout_seconds,
        lifecycle_timeout_seconds=settings.trusted_plugin_lifecycle_timeout_seconds,
        failure_threshold=settings.trusted_plugin_failure_threshold,
        reset_seconds=settings.trusted_plugin_reset_seconds,
        quarantine_threshold=settings.trusted_plugin_quarantine_threshold,
    )


def _python_target(root: Path, target: str) -> tuple[Path, str]:
    if not target.startswith("python:"):
        raise ValueError("trusted in-process entry points require python:<module.py>:<callable>")
    specification = target.removeprefix("python:")
    try:
        relative, attribute = specification.rsplit(":", 1)
    except ValueError as exc:
        raise ValueError(
            "trusted in-process entry points require python:<module.py>:<callable>"
        ) from exc
    if not relative or not attribute or not attribute.isidentifier():
        raise ValueError("trusted Python target is invalid")
    relative_path = Path(relative)
    if relative_path.is_absolute() or relative_path.suffix != ".py":
        raise ValueError("trusted Python target must name a relative .py file")
    path = (root / relative_path).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("trusted Python target escapes or is absent from the package root")
    return path, attribute


def _load_module(namespace: str, root: Path, path: Path) -> types.ModuleType:
    root_module = sys.modules.get(namespace)
    if root_module is None:
        root_module = types.ModuleType(namespace)
        root_module.__package__ = namespace
        root_module.__path__ = [str(root)]
        sys.modules[namespace] = root_module
    relative = path.relative_to(root).with_suffix("")
    if relative.name == "__init__":
        raise ValueError("trusted Python entry point targets cannot use __init__.py")
    module_parts = relative.parts
    for index in range(1, len(module_parts)):
        parent_name = ".".join((namespace, *module_parts[:index]))
        if parent_name not in sys.modules:
            parent = types.ModuleType(parent_name)
            parent.__package__ = parent_name
            parent.__path__ = [str(root.joinpath(*module_parts[:index]))]
            sys.modules[parent_name] = parent
    module_name = ".".join((namespace, *module_parts))
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load trusted Python module {relative.as_posix()!r}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    return module


def _single_hook(
    modules: Any,
    name: str,
    *,
    asynchronous: bool,
) -> Any:
    hooks = {getattr(module, name) for module in modules if hasattr(module, name)}
    if not hooks:
        return None
    if len(hooks) != 1:
        raise ValueError(f"trusted package declares multiple {name} hooks")
    hook = next(iter(hooks))
    if not callable(hook) or inspect.iscoroutinefunction(hook) is not asynchronous:
        expected = "async" if asynchronous else "synchronous"
        raise ValueError(f"{name} must be a {expected} callable")
    return hook


def _operation_for(extension_type: ExtensionType) -> PluginOperation:
    return {
        ExtensionType.TASK: PluginOperation.EXECUTE,
        ExtensionType.TRIGGER: PluginOperation.POLL,
        ExtensionType.CONDITION: PluginOperation.EVALUATE,
        ExtensionType.RUNNER: PluginOperation.RUN,
        ExtensionType.STORAGE: PluginOperation.GET,
        ExtensionType.SECRET: PluginOperation.RESOLVE,
        ExtensionType.EXPRESSION: PluginOperation.EVALUATE,
        ExtensionType.NOTIFICATION: PluginOperation.SEND,
    }[extension_type]


def _error_response(
    request: PluginRequest,
    code: str,
    message: str,
    *,
    retryable: bool = False,
) -> PluginResponse:
    return PluginResponse(
        invocationId=request.session.invocation_id,
        errors=(
            PluginErrorDetail(
                code=code,
                message=message,
                phase=PluginErrorPhase.RUNTIME,
                retryable=retryable,
            ),
        ),
    )


def _registration_error_code(exc: BaseException) -> str:
    if isinstance(exc, TimeoutError):
        return "plugin.runtime.lifecycle_timeout"
    return "plugin.runtime.registration"


def _namespace_for(content_digest: str) -> str:
    return f"_amesh_trusted_{content_digest.removeprefix('sha256:')}"


def _unload_namespace(namespace: str) -> None:
    for module_name in tuple(sys.modules):
        if module_name == namespace or module_name.startswith(namespace + "."):
            sys.modules.pop(module_name, None)
