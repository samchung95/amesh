from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.config import IsolatedPluginServiceConfig, Settings, TrustedPluginApproval
from amesh.domain import (
    FailureCategory,
    ToolDescriptor,
    ToolImpact,
    ToolInvocationRequest,
    ToolPolicy,
    ToolProviderKind,
    ToolProviderRef,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import (
    InProcessExecutor,
    TaskCancellationChannel,
    TaskCompletion,
    TaskExecutionContext,
    TaskExecutionFailure,
)
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database
from amesh.plugin_sdk import (
    ExtensionType,
    PluginCatalogManager,
    PluginDiscoverySource,
    PluginPackagePin,
    PluginResolution,
    PluginResolver,
    PluginResourcePin,
    PluginSourceKind,
)
from amesh.plugins import IsolatedPluginRuntime, IsolatedPluginState, build_isolated_runtime
from amesh.tasks import GovernedToolInvoker, InMemoryToolInvocationJournal

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"


def _manifest(*, resource_type: str = "vendor.isolated") -> dict[str, Any]:
    return {
        "schemaVersion": "amesh.plugin/v1",
        "name": "vendor.isolated",
        "version": "1.0.0",
        "vendor": "Test vendor",
        "license": "MIT",
        "compatibility": {
            "platformVersion": ">=0.2.0,<1.0.0",
            "protocolVersions": ["amesh.plugin.rpc/v1"],
        },
        "entryPoints": [
            {
                "name": "main",
                "resourceType": resource_type,
                "type": "task",
                "transport": "stdio",
                "target": "service:main",
                "configurationSchema": {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"],
                    "additionalProperties": False,
                },
                "documentation": {
                    "title": "Isolated fixture",
                    "description": "Language-neutral process runtime fixture.",
                    "category": "Tests",
                },
            }
        ],
        "capabilities": {
            "required": ["task.execute"],
            "networkAccess": "restricted",
            "allowedEgress": ["api.example.test:443"],
            "filesystemAccess": "workspace-read",
            "secretScopes": ["fixture.token"],
        },
    }


def _service_source(*, crash_once: bool = False, delay: float = 0, burn_cpu: bool = False) -> str:
    return f"""
import asyncio
import json
import os
import time
from pathlib import Path

from amesh.plugin_sdk import (
    PluginArtifact,
    PluginAsset,
    PluginLog,
    PluginManifest,
    PluginMetric,
    PluginOperation,
    PluginResponse,
    ProcessPluginResult,
    serve_stdio_plugin,
)

ROOT = Path(__file__).parent
MANIFEST = PluginManifest.model_validate(json.loads((ROOT / "amesh-plugin.json").read_text()))

async def execute(request, capabilities):
    marker = ROOT / "crashed.marker"
    if {crash_once!r} and not marker.exists():
        marker.write_text("crashed", encoding="utf-8")
        os._exit(17)
    if {delay!r}:
        await asyncio.sleep({delay!r})
    if {burn_cpu!r}:
        started = time.monotonic()
        while time.monotonic() - started < 1:
            pass
    return ProcessPluginResult(
        response=PluginResponse(
            invocationId=request.session.invocation_id,
            output={{
                "message": request.configuration["message"],
                "hasSecret": "fixture.token" in capabilities.secrets,
                "hasFile": "input" in capabilities.files,
                "egress": list(capabilities.allowed_egress),
                "platformApis": list(capabilities.platform_apis),
                "hasCapabilityToken": "task.execute" in capabilities.capability_tokens,
            }},
            logs=(PluginLog(message="isolated fixture executed"),),
        ),
        metrics=(PluginMetric(name="fixture.count", kind="counter", value=1),),
        artifacts=(PluginArtifact(uri="s3://amesh/fixture.txt", sizeBytes=7),),
        assets=((PluginAsset(
            provider="pg",
            assetType="table",
            externalKey="orders",
            displayName="Orders",
            accessMode="READ",
        ),) if request.configuration["message"] == "hello" else ()),
    )

asyncio.run(serve_stdio_plugin(MANIFEST, {{("main", PluginOperation.EXECUTE): execute}}))
"""


def _runtime(
    tmp_path: Path,
    *,
    crash_once: bool = False,
    delay: float = 0,
    wall_time: float = 5,
    max_output_bytes: int = 1024 * 1024,
    memory_bytes: int | None = None,
    cpu_seconds: float | None = None,
    burn_cpu: bool = False,
) -> tuple[
    IsolatedPluginRuntime,
    PluginResolution,
    IsolatedPluginServiceConfig,
    PluginCatalogManager,
]:
    source = tmp_path / "source"
    package = source / "vendor-isolated"
    package.mkdir(parents=True)
    (package / "amesh-plugin.json").write_text(
        json.dumps(_manifest(), sort_keys=True), encoding="utf-8"
    )
    (package / "service.py").write_text(
        _service_source(crash_once=crash_once, delay=delay, burn_cpu=burn_cpu),
        encoding="utf-8",
    )
    manager = PluginCatalogManager(
        sources=(PluginDiscoverySource(kind=PluginSourceKind.DIRECTORY, location=str(source)),),
        install_root=tmp_path / "installed",
        platform_version="0.2.0",
    )
    record = next(
        item for item in manager.snapshot.packages if item.identity == ("vendor.isolated", "1.0.0")
    )
    assert record.content_digest is not None
    profile = IsolatedPluginServiceConfig(
        name="vendor.isolated",
        version="1.0.0",
        contentDigest=record.content_digest,
        command=(sys.executable, "service.py"),
        platformApis=("artifacts.write",),
        startupTimeoutSeconds=3,
        heartbeatTimeoutSeconds=1,
        wallTimeSeconds=wall_time,
        cancelGraceSeconds=0.5,
        tokenTtlSeconds=60,
        maxOutputBytes=max_output_bytes,
        memoryBytes=memory_bytes,
        cpuSeconds=cpu_seconds,
        maxConcurrency=1,
    )
    runtime = IsolatedPluginRuntime(
        manager,
        (profile,),
        monitor_interval_seconds=0.01,
    )
    resolution = PluginResolution(
        catalogDigest=manager.snapshot.catalog_digest,
        resolutionDigest="sha256:" + "0" * 64,
        packages=(
            PluginPackagePin(
                name="vendor.isolated",
                version="1.0.0",
                contentDigest=record.content_digest,
                sourceKind=PluginSourceKind.DIRECTORY,
            ),
        ),
        resources=(
            PluginResourcePin(
                kind=ExtensionType.TASK,
                type="vendor.isolated",
                package="vendor.isolated",
                version="1.0.0",
                contentDigest=record.content_digest,
            ),
        ),
    )
    return runtime, resolution, profile, manager


def _context(*, cancellation: TaskCancellationChannel | None = None) -> TaskExecutionContext:
    return TaskExecutionContext(
        tenant_id="default",
        execution_id=uuid4(),
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=uuid4(),
        inputs={},
        outputs={},
        variables={},
        secrets={"fixture.token": "secret-value", "undeclared": "not-granted"},
        files={"input": "s3://amesh/input.txt"},
        cancellation=cancellation or TaskCancellationChannel(),
    )


def test_isolated_process_negotiates_capabilities_and_records_evidence(tmp_path: Path) -> None:
    runtime, resolution, _, _ = _runtime(tmp_path)

    async def scenario() -> None:
        await runtime.ensure_configured()
        handler = runtime.task_handlers(resolution)["vendor.isolated"]
        completion = await handler(
            TaskDefinition.model_validate(
                {"id": "isolated", "type": "vendor.isolated", "message": "hello"}
            ),
            _context(),
        )
        assert isinstance(completion, TaskCompletion)
        assert completion.output == {
            "message": "hello",
            "hasSecret": True,
            "hasFile": True,
            "egress": ["api.example.test:443"],
            "platformApis": ["artifacts.write"],
            "hasCapabilityToken": True,
        }
        assert completion.logs[0].message == "isolated fixture executed"
        assert completion.metrics[0].name == "fixture.count"
        assert completion.artifacts[0].uri == "s3://amesh/fixture.txt"
        assert completion.assets[0].external_key == "orders"
        assert completion.assets[0].access_mode.value == "READ"
        status = runtime.snapshot().plugins[0]
        assert status.state is IsolatedPluginState.READY
        assert status.starts == 1
        assert status.completed == 1
        assert status.last_pid is not None

    asyncio.run(scenario())


def test_tool_provider_binding_uses_isolated_rpc_runtime(tmp_path: Path) -> None:
    runtime, _, _, _ = _runtime(tmp_path)
    identity = ToolProviderRef(kind=ToolProviderKind.PLUGIN, key="vendor.isolated", revision=1)
    descriptor = ToolDescriptor(
        provider=identity,
        name="main",
        inputSchema={
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
            "additionalProperties": False,
        },
        impact=ToolImpact.HIGH_IMPACT,
    )

    async def scenario() -> None:
        await runtime.ensure_configured()
        provider = runtime.tool_provider(identity, (descriptor,))
        result = await GovernedToolInvoker(provider, InMemoryToolInvocationJournal()).invoke(
            ToolInvocationRequest(
                provider=identity,
                toolName="main",
                arguments={"message": "bound"},
                allowWrite=True,
                approvalGranted=True,
            ),
            ToolPolicy(allowedTools=("main",), allowHighImpact=True),
        )
        assert result.output["message"] == "bound"

    asyncio.run(scenario())


def test_crashed_service_restarts_on_same_revision_handler(tmp_path: Path) -> None:
    runtime, resolution, _, _ = _runtime(tmp_path, crash_once=True)

    async def scenario() -> None:
        await runtime.ensure_configured()
        handler = runtime.task_handlers(resolution)["vendor.isolated"]
        task = TaskDefinition.model_validate(
            {"id": "isolated", "type": "vendor.isolated", "message": "retry"}
        )
        with pytest.raises(TaskExecutionFailure) as raised:
            await handler(task, _context())
        assert raised.value.category is FailureCategory.RETRYABLE
        completion = await handler(task, _context())
        assert isinstance(completion, TaskCompletion)
        assert completion.output["message"] == "retry"
        status = runtime.snapshot().plugins[0]
        assert status.starts == 2
        assert status.restarts == 1
        assert status.crashes == 1
        assert status.completed == 1

    asyncio.run(scenario())


def test_settings_build_runtime_and_reject_overlapping_tiers(tmp_path: Path) -> None:
    _, resolution, profile, _ = _runtime(tmp_path)
    settings = Settings(
        plugin_directories=(str(tmp_path / "source"),),
        plugin_install_root=str(tmp_path / "other-installed"),
        isolated_plugin_services=(profile,),
    )
    built = build_isolated_runtime(
        settings,
        PluginCatalogManager(
            sources=(
                PluginDiscoverySource(
                    kind=PluginSourceKind.DIRECTORY,
                    location=str(tmp_path / "source"),
                ),
            ),
            install_root=tmp_path / "other-installed",
            platform_version="0.2.0",
        ),
    )

    async def scenario() -> None:
        await built.ensure_configured()
        assert "vendor.isolated" in built.task_handlers(resolution)

    asyncio.run(scenario())

    with pytest.raises(ValueError, match="both trusted and isolated"):
        Settings(
            trusted_plugin_approvals=(
                TrustedPluginApproval(
                    name=profile.name,
                    version=profile.version,
                    contentDigest=profile.content_digest,
                ),
            ),
            isolated_plugin_services=(profile,),
        )


class _DelayedCancellation(TaskCancellationChannel):
    async def wait(self, *, poll_interval: float = 0.05) -> None:
        del poll_interval
        await asyncio.sleep(0.1)


@pytest.mark.parametrize(
    ("runtime_options", "context", "expected_category", "expected_code"),
    (
        (
            {"delay": 1, "wall_time": 0.15},
            _context(),
            FailureCategory.TIMED_OUT,
            "plugin.isolated.wall_time",
        ),
        (
            {"delay": 1},
            _context(cancellation=_DelayedCancellation()),
            FailureCategory.CANCELLED,
            "plugin.isolated.cancelled",
        ),
        (
            {"max_output_bytes": 2048},
            _context(),
            FailureCategory.USER_CODE,
            "plugin.isolated.frame_limit",
        ),
        (
            {"delay": 1, "memory_bytes": 4 * 1024 * 1024},
            _context(),
            FailureCategory.USER_CODE,
            "plugin.isolated.memory_limit",
        ),
        (
            {"burn_cpu": True, "cpu_seconds": 0.01},
            _context(),
            FailureCategory.USER_CODE,
            "plugin.isolated.cpu_limit",
        ),
    ),
)
def test_isolated_runtime_enforces_call_limits_and_cancellation(
    tmp_path: Path,
    runtime_options: dict[str, Any],
    context: TaskExecutionContext,
    expected_category: FailureCategory,
    expected_code: str,
) -> None:
    runtime, resolution, _, _ = _runtime(tmp_path, **runtime_options)

    async def scenario() -> None:
        await runtime.ensure_configured()
        handler = runtime.task_handlers(resolution)["vendor.isolated"]
        message = "x" * 4096 if expected_code == "plugin.isolated.frame_limit" else "bounded"
        with pytest.raises(TaskExecutionFailure) as raised:
            await handler(
                TaskDefinition.model_validate(
                    {"id": "isolated", "type": "vendor.isolated", "message": message}
                ),
                context,
            )
        assert raised.value.category is expected_category
        assert raised.value.evidence == {"code": expected_code}

    asyncio.run(scenario())


@pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
def test_crash_retry_preserves_durable_task_ownership(tmp_path: Path) -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        runtime, _, _, manager = _runtime(tmp_path, crash_once=True)
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        repository = PostgresExecutionRepository(
            engine,
            plugin_resolution_provider=lambda flow: (
                PluginResolver(manager.snapshot).resolve_flow(flow).revision_payload()
            ),
        )
        flow = FlowDefinition.model_validate(
            {
                "id": "isolated_retry",
                "namespace": "tests.plugins",
                "tasks": [
                    {
                        "id": "run",
                        "type": "vendor.isolated",
                        "message": "durable",
                        "retry": {"maxAttempts": 2, "delaySeconds": 0},
                    }
                ],
            }
        )
        try:
            await repository.apply_flow(flow, tenant_id="default")
            revision = (
                await repository.list_flow_revisions(
                    flow.namespace,
                    flow.id,
                    tenant_id="default",
                )
            )[0]
            await runtime.ensure_configured()
            executor = InProcessExecutor(
                repository,
                handlers=runtime.task_handlers(revision.plugin_resolution),
            )
            execution_id = await executor.create_execution(flow, tenant_id="default")
            completed = await executor.run_to_completion(
                flow,
                execution_id,
                tenant_id="default",
            )
            assert completed.state.value == "SUCCESS"
            assert len(completed.task_runs) == 1
            assert completed.task_runs[0].current_attempt == 2
            assert completed.task_runs[0].result is not None
            assert completed.task_runs[0].result["message"] == "durable"
            status = runtime.snapshot().plugins[0]
            assert status.crashes == 1
            assert status.restarts == 1
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
