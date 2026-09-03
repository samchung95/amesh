from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import pytest
from prometheus_client import generate_latest
from sqlalchemy.ext.asyncio import create_async_engine
from tests.fixtures.api_stubs import DefaultTenantQuotaStub as _TenantQuotaStub

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_tenant_service,
    get_trusted_plugin_runtime,
)
from amesh.config import Settings, TrustedPluginApproval
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    PermissionAction,
    PrincipalType,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.dsl.task_configuration import TASK_STRUCTURAL_FIELDS
from amesh.executor import InProcessExecutor, TaskExecutionContext
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database
from amesh.plugin_sdk import (
    ExtensionType,
    PluginCatalogManager,
    PluginDiscoverySource,
    PluginOperation,
    PluginPackagePin,
    PluginRequest,
    PluginResolution,
    PluginResolver,
    PluginResourcePin,
    PluginSession,
    PluginSourceKind,
)
from amesh.plugins import (
    TrustedCircuitState,
    TrustedPluginRuntime,
    TrustedPluginState,
    build_trusted_runtime,
)
from amesh.plugins.trusted import TASK_STRUCTURAL_FIELDS as TRUSTED_TASK_STRUCTURAL_FIELDS

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"


def _manifest(name: str, version: str, resource_type: str) -> dict[str, Any]:
    return {
        "schemaVersion": "amesh.plugin/v1",
        "name": name,
        "version": version,
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
                "target": "python:plugin.py:execute",
                "configurationSchema": {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"],
                    "additionalProperties": False,
                },
                "documentation": {
                    "title": resource_type,
                    "description": "Trusted runtime fixture.",
                    "category": "Tests",
                },
            }
        ],
    }


def _package(
    root: Path,
    *,
    name: str = "vendor.trusted",
    version: str = "1.0.0",
    resource_type: str = "vendor.trusted",
    source: str,
) -> Path:
    package = root / f"{name}-{version}"
    package.mkdir(parents=True)
    (package / "amesh-plugin.json").write_text(
        json.dumps(_manifest(name, version, resource_type), sort_keys=True),
        encoding="utf-8",
    )
    (package / "plugin.py").write_text(source, encoding="utf-8")
    return package


def _manager(source: Path, install_root: Path) -> PluginCatalogManager:
    return PluginCatalogManager(
        sources=(
            PluginDiscoverySource(
                kind=PluginSourceKind.DIRECTORY,
                location=str(source),
            ),
        ),
        install_root=install_root,
        platform_version="0.2.0",
    )


def _approval(manager: PluginCatalogManager, name: str, version: str) -> TrustedPluginApproval:
    record = next(item for item in manager.snapshot.packages if item.identity == (name, version))
    assert record.content_digest is not None
    return TrustedPluginApproval(
        name=name,
        version=version,
        contentDigest=record.content_digest,
    )


def _runtime(
    manager: PluginCatalogManager,
    *approvals: TrustedPluginApproval,
    callback_timeout: float = 1,
    lifecycle_timeout: float = 1,
    failure_threshold: int = 2,
    reset_seconds: float = 0.001,
    quarantine_threshold: int = 3,
) -> TrustedPluginRuntime:
    return TrustedPluginRuntime(
        manager,
        approvals,
        callback_timeout_seconds=callback_timeout,
        lifecycle_timeout_seconds=lifecycle_timeout,
        failure_threshold=failure_threshold,
        reset_seconds=reset_seconds,
        quarantine_threshold=quarantine_threshold,
    )


def _resolution(
    manager: PluginCatalogManager,
    approval: TrustedPluginApproval,
    resource_type: str = "vendor.trusted",
) -> PluginResolution:
    return PluginResolution(
        catalogDigest=manager.snapshot.catalog_digest,
        resolutionDigest="sha256:" + "0" * 64,
        packages=(
            PluginPackagePin(
                name=approval.name,
                version=approval.version,
                contentDigest=approval.content_digest,
                sourceKind=PluginSourceKind.DIRECTORY,
            ),
        ),
        resources=(
            PluginResourcePin(
                kind=ExtensionType.TASK,
                type=resource_type,
                package=approval.name,
                version=approval.version,
                contentDigest=approval.content_digest,
            ),
        ),
    )


def _request(approval: TrustedPluginApproval) -> PluginRequest:
    return PluginRequest(
        plugin=approval.name,
        entryPoint="main",
        operation=PluginOperation.EXECUTE,
        session=PluginSession(tenantId="default", invocationId=str(uuid4())),
        configuration={"message": "hello"},
    )


def test_approved_runtime_lifecycle_namespace_task_dispatch_and_telemetry(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    package = _package(
        source,
        source="""
from pathlib import Path
from amesh.plugin_sdk import PluginResponse

started = False

async def plugin_start(context):
    global started
    started = context.name == "vendor.trusted"

async def plugin_stop(context):
    Path(__file__).with_name("stopped.txt").write_text(context.namespace, encoding="utf-8")

def plugin_memory_bytes():
    return 42

async def execute(request):
    return PluginResponse(
        invocationId=request.session.invocation_id,
        output={"started": started, "configuration": dict(request.configuration)},
    )
""",
    )
    manager = _manager(source, tmp_path / "installed")
    approval = _approval(manager, "vendor.trusted", "1.0.0")
    runtime = _runtime(manager, approval)
    original_path = tuple(sys.path)

    async def scenario() -> None:
        await runtime.ensure_started()
        status = runtime.snapshot().plugins[0]
        assert status.state is TrustedPluginState.ACTIVE
        assert status.namespace is not None
        assert status.namespace.startswith("_amesh_trusted_")
        assert status.owned_memory_bytes == 42
        assert status.process_memory_bytes is not None
        assert "vendor.trusted" not in sys.modules
        assert tuple(sys.path) == original_path

        handler = runtime.task_handlers(_resolution(manager, approval))["vendor.trusted"]
        output = await handler(
            TaskDefinition.model_validate(
                {
                    "id": "trusted",
                    "type": "vendor.trusted",
                    "description": "structural metadata",
                    "runLabels": {"stage": "test"},
                    "message": "hello",
                    "x-debug": True,
                }
            ),
            TaskExecutionContext(
                tenant_id="default",
                execution_id=uuid4(),
                task_run_id=uuid4(),
                attempt=1,
                attempt_id=uuid4(),
                inputs={},
                outputs={},
                variables={},
            ),
        )
        assert output == {"started": True, "configuration": {"message": "hello"}}
        measured = runtime.snapshot().plugins[0]
        assert measured.callbacks == 1
        assert measured.average_latency_ms >= 0
        await runtime.stop()
        assert runtime.snapshot().plugins[0].state is TrustedPluginState.STOPPED
        assert not any(name.startswith(status.namespace or "unused") for name in sys.modules)

    asyncio.run(scenario())
    assert (package / "stopped.txt").is_file()
    metrics = generate_latest().decode("utf-8")
    assert 'amesh_plugin_callbacks_total{entry_point="main",operation="execute"' in metrics
    assert 'measurement="plugin-owned"' in metrics


def test_trusted_runtime_imports_the_authoritative_task_structural_fields() -> None:
    assert TRUSTED_TASK_STRUCTURAL_FIELDS is TASK_STRUCTURAL_FIELDS


def test_unapproved_package_is_never_imported(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _package(
        source,
        source="""
raise RuntimeError("unapproved package was imported")
""",
    )
    manager = _manager(source, tmp_path / "installed")
    runtime = _runtime(manager)

    asyncio.run(runtime.ensure_started())

    assert runtime.snapshot().plugins == ()


def test_timeout_opens_circuit_then_repeated_invariants_quarantine(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _package(
        source,
        source="""
import asyncio
from amesh.plugin_sdk import PluginResponse

async def execute(request):
    await asyncio.sleep(0.05)
    return PluginResponse(invocationId=request.session.invocation_id)
""",
    )
    manager = _manager(source, tmp_path / "installed")
    approval = _approval(manager, "vendor.trusted", "1.0.0")
    runtime = _runtime(
        manager,
        approval,
        callback_timeout=0.005,
        failure_threshold=1,
        reset_seconds=0.001,
        quarantine_threshold=2,
    )

    async def scenario() -> None:
        await runtime.ensure_started()
        first = await runtime.invoke(
            _request(approval),
            version=approval.version,
            content_digest=approval.content_digest,
        )
        assert first.errors[0].code == "plugin.runtime.timeout"
        assert runtime.snapshot().plugins[0].circuit is TrustedCircuitState.OPEN
        blocked = await runtime.invoke(
            _request(approval),
            version=approval.version,
            content_digest=approval.content_digest,
        )
        assert blocked.errors[0].code == "plugin.runtime.circuit_open"
        await asyncio.sleep(0.002)
        second = await runtime.invoke(
            _request(approval),
            version=approval.version,
            content_digest=approval.content_digest,
        )
        assert second.errors[0].code == "plugin.runtime.timeout"
        status = runtime.snapshot().plugins[0]
        assert status.state is TrustedPluginState.QUARANTINED
        assert status.invariant_violations == 2
        quarantined = await runtime.invoke(
            _request(approval),
            version=approval.version,
            content_digest=approval.content_digest,
        )
        assert quarantined.errors[0].code == "plugin.runtime.quarantined"
        await runtime.stop()

    asyncio.run(scenario())


def test_lifecycle_timeout_is_bounded_and_quarantined(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _package(
        source,
        source="""
import asyncio
from amesh.plugin_sdk import PluginResponse

async def plugin_start(context):
    await asyncio.sleep(0.05)

async def execute(request):
    return PluginResponse(invocationId=request.session.invocation_id)
""",
    )
    manager = _manager(source, tmp_path / "installed")
    approval = _approval(manager, "vendor.trusted", "1.0.0")
    runtime = _runtime(manager, approval, lifecycle_timeout=0.005)

    asyncio.run(runtime.ensure_started())

    status = runtime.snapshot().plugins[0]
    assert status.state is TrustedPluginState.QUARANTINED
    assert status.last_error_code == "plugin.runtime.lifecycle_timeout"
    assert status.namespace is None
    assert not any(
        name.startswith(f"_amesh_trusted_{approval.content_digest.removeprefix('sha256:')}")
        for name in sys.modules
    )


def test_stop_hook_timeout_is_bounded(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _package(
        source,
        source="""
import asyncio
from amesh.plugin_sdk import PluginResponse

async def plugin_stop(context):
    await asyncio.sleep(0.05)

async def execute(request):
    return PluginResponse(invocationId=request.session.invocation_id)
""",
    )
    manager = _manager(source, tmp_path / "installed")
    approval = _approval(manager, "vendor.trusted", "1.0.0")
    runtime = _runtime(manager, approval, lifecycle_timeout=0.005)

    async def scenario() -> None:
        await runtime.ensure_started()
        await runtime.stop()

    asyncio.run(scenario())
    status = runtime.snapshot().plugins[0]
    assert status.state is TrustedPluginState.STOPPED
    assert status.last_error_code == "plugin.runtime.lifecycle_stop"


def test_exact_resolution_dispatches_selected_version(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    for version in ("1.0.0", "2.0.0"):
        _package(
            source,
            version=version,
            source=f"""
from amesh.plugin_sdk import PluginResponse

async def execute(request):
    return PluginResponse(invocationId=request.session.invocation_id, output={{"version": "{version}"}})
""",
        )
    manager = _manager(source, tmp_path / "installed")
    v1 = _approval(manager, "vendor.trusted", "1.0.0")
    v2 = _approval(manager, "vendor.trusted", "2.0.0")
    runtime = _runtime(manager, v1, v2)

    async def scenario() -> None:
        await runtime.ensure_started()
        for approval in (v1, v2):
            handler = runtime.task_handlers(_resolution(manager, approval))["vendor.trusted"]
            output = await handler(
                TaskDefinition.model_validate(
                    {"id": "trusted", "type": "vendor.trusted", "message": "hello"}
                ),
                TaskExecutionContext(
                    tenant_id="default",
                    execution_id=uuid4(),
                    task_run_id=uuid4(),
                    attempt=1,
                    attempt_id=uuid4(),
                    inputs={},
                    outputs={},
                    variables={},
                ),
            )
            assert output == {"version": approval.version}
        await runtime.stop()

    asyncio.run(scenario())


def test_runtime_status_endpoint_requires_plugin_view_permission(tmp_path: Path) -> None:
    manager = PluginCatalogManager(
        install_root=tmp_path / "installed",
        platform_version="0.2.0",
    )
    runtime = _runtime(manager)
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="plugin-viewer",
    )
    authorization = _PluginAuthorizationStub()
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: authorization
    app.dependency_overrides[get_tenant_service] = _TenantQuotaStub
    app.dependency_overrides[get_trusted_plugin_runtime] = lambda: runtime

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                "/api/v1/plugins/trusted-runtime",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200
        assert response.json() == {"catalogGeneration": 1, "plugins": []}

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()
    assert authorization.requests == [PermissionAction.VIEW]


def test_settings_parse_unique_exact_approvals(tmp_path: Path) -> None:
    digest = "sha256:" + "a" * 64
    settings = Settings(
        _env_file=None,
        trusted_plugin_approvals=json.dumps(
            [{"name": "vendor.trusted", "version": "1.0.0", "contentDigest": digest}]
        ),
    )
    runtime = build_trusted_runtime(
        settings,
        PluginCatalogManager(
            install_root=tmp_path / "installed",
            platform_version="0.2.0",
        ),
    )

    assert settings.trusted_plugin_approvals[0].content_digest == digest
    assert runtime.snapshot().plugins == ()
    with pytest.raises(ValueError, match="unique exact identities"):
        Settings(
            _env_file=None,
            trusted_plugin_approvals=[
                {"name": "vendor.trusted", "version": "1.0.0", "contentDigest": digest},
                {"name": "vendor.trusted", "version": "1.0.0", "contentDigest": digest},
            ],
        )


@pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
def test_pinned_plugin_executes_through_in_process_executor(tmp_path: Path) -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        source = tmp_path / "source"
        source.mkdir()
        _package(
            source,
            source="""
from amesh.plugin_sdk import PluginResponse

async def execute(request):
    return PluginResponse(
        invocationId=request.session.invocation_id,
        output={"message": request.configuration["message"]},
    )
""",
        )
        manager = _manager(source, tmp_path / "installed")
        approval = _approval(manager, "vendor.trusted", "1.0.0")
        runtime = _runtime(manager, approval)
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
                "id": "trusted_runtime",
                "namespace": "tests.plugins",
                "tasks": [
                    {
                        "id": "run",
                        "type": "vendor.trusted",
                        "message": "executed",
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
            await runtime.ensure_started()
            executor = InProcessExecutor(
                repository,
                handlers=runtime.task_handlers(revision.plugin_resolution),
                resource_registry=manager.resource_registry(),
            )
            execution_id = await executor.create_execution(flow, tenant_id="default")
            completed = await executor.run_to_completion(
                flow,
                execution_id,
                tenant_id="default",
            )
            assert completed.state.value == "SUCCESS"
            runs = await repository.list_task_runs(execution_id, tenant_id="default")
            assert runs[0].result == {"message": "executed"}
        finally:
            await runtime.stop()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


class _PluginAuthorizationStub:
    def __init__(self) -> None:
        self.requests: list[PermissionAction] = []

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        assert request.resource_type == "plugin"
        self.requests.append(request.action)
        return AuthorizationDecision(
            allowed=True,
            reason_code="allowed",
            summary="test plugin access",
            policy_version=1,
        )
