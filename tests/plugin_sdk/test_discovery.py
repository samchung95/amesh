from __future__ import annotations

import asyncio
import hashlib
import json
import os
import zipfile
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from tests.fixtures.api_stubs import DefaultTenantQuotaStub as _TenantQuotaStub

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_operational_control_repository,
    get_plugin_catalog_manager,
    get_plugin_policy_service,
    get_tenant_service,
)
from amesh.cli import build_parser
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    OperationalBoundary,
    OperationalControlDecision,
    PermissionAction,
    PrincipalType,
    RunningWorkPolicy,
)
from amesh.dsl import FlowDefinition
from amesh.plugin_sdk import (
    ExtensionType,
    PluginCatalogManager,
    PluginContractError,
    PluginDiscoverySource,
    PluginIsolationPlanner,
    PluginLifecycleStatus,
    PluginResolver,
    PluginSourceKind,
    PluginTypeReference,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")


def _manifest(
    name: str,
    version: str,
    resource_type: str,
    *,
    dependencies: tuple[tuple[str, str], ...] = (),
    platform_range: str = ">=0.2.0,<1.0.0",
    deprecated: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schemaVersion": "amesh.plugin/v1",
        "name": name,
        "version": version,
        "vendor": "Test vendor",
        "license": "MIT",
        "compatibility": {
            "platformVersion": platform_range,
            "protocolVersions": ["amesh.plugin.rpc/v1"],
        },
        "entryPoints": [
            {
                "name": "main",
                "resourceType": resource_type,
                "type": "task",
                "transport": "stdio",
                "target": "bin/plugin",
                "configurationSchema": {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "type": "object",
                    "additionalProperties": False,
                },
                "documentation": {
                    "title": resource_type,
                    "description": f"Fixture for {resource_type}.",
                    "category": "Tests",
                },
            }
        ],
        "dependencies": [
            {"name": dependency, "versionRange": version_range}
            for dependency, version_range in dependencies
        ],
    }
    if deprecated:
        payload["deprecations"] = [
            {
                "subject": name,
                "deprecatedIn": version,
                "message": "Use the replacement package.",
            }
        ]
    return payload


def _write_plugin(
    root: Path,
    directory: str,
    manifest: dict[str, Any],
) -> Path:
    package = root / directory
    package.mkdir(parents=True)
    (package / "amesh-plugin.json").write_text(
        json.dumps(manifest, sort_keys=True),
        encoding="utf-8",
    )
    (package / "payload.txt").write_text(directory, encoding="utf-8")
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


def test_catalog_discovers_and_classifies_all_lifecycle_states(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _write_plugin(source, "task-v1", _manifest("vendor.task", "1.0.0", "vendor.task"))
    _write_plugin(source, "task-v2", _manifest("vendor.task", "2.0.0", "vendor.task"))
    _write_plugin(
        source,
        "deprecated",
        _manifest("vendor.deprecated", "1.0.0", "vendor.deprecated", deprecated=True),
    )
    _write_plugin(
        source,
        "incompatible",
        _manifest(
            "vendor.incompatible",
            "1.0.0",
            "vendor.incompatible",
            platform_range=">=9.0.0",
        ),
    )
    invalid = source / "invalid"
    invalid.mkdir()
    (invalid / "amesh-plugin.json").write_text("{}", encoding="utf-8")

    manager = _manager(source, tmp_path / "installed")
    status_by_identity = {
        record.identity: record.status
        for record in manager.snapshot.packages
        if record.identity is not None
    }

    assert status_by_identity[("amesh.core", "0.2.0")] is PluginLifecycleStatus.ACTIVE
    assert status_by_identity[("vendor.task", "2.0.0")] is PluginLifecycleStatus.ACTIVE
    assert status_by_identity[("vendor.task", "1.0.0")] is PluginLifecycleStatus.INSTALLED
    assert status_by_identity[("vendor.deprecated", "1.0.0")] is PluginLifecycleStatus.DEPRECATED
    assert (
        status_by_identity[("vendor.incompatible", "1.0.0")] is PluginLifecycleStatus.INCOMPATIBLE
    )
    assert any(
        record.manifest is None and record.status is PluginLifecycleStatus.QUARANTINED
        for record in manager.snapshot.packages
    )


def test_resolution_pins_exact_versions_dependencies_and_isolated_roots(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _write_plugin(source, "shared-v1", _manifest("vendor.shared", "1.5.0", "shared.v1"))
    _write_plugin(source, "shared-v2", _manifest("vendor.shared", "2.5.0", "shared.v2"))
    _write_plugin(
        source,
        "alpha",
        _manifest(
            "vendor.alpha",
            "1.0.0",
            "vendor.alpha",
            dependencies=(("vendor.shared", ">=1.0.0,<2.0.0"),),
        ),
    )
    _write_plugin(
        source,
        "beta",
        _manifest(
            "vendor.beta",
            "1.0.0",
            "vendor.beta",
            dependencies=(("vendor.shared", ">=2.0.0,<3.0.0"),),
        ),
    )
    manager = _manager(source, tmp_path / "installed")
    resolver = PluginResolver(manager.snapshot)

    alpha = resolver.resolve((PluginTypeReference(kind=ExtensionType.TASK, type="vendor.alpha"),))
    pins = {package.name: package for package in alpha.packages}
    assert pins["vendor.alpha"].version == "1.0.0"
    assert pins["vendor.shared"].version == "1.5.0"
    assert all(package.content_digest.startswith("sha256:") for package in alpha.packages)

    plans = {
        plan.package.name: plan for plan in PluginIsolationPlanner(manager.snapshot).plan(alpha)
    }
    assert plans["vendor.alpha"].dependency_roots == {
        "vendor.shared": plans["vendor.shared"].content_root
    }
    assert plans["vendor.alpha"].content_root != plans["vendor.shared"].content_root
    assert plans["vendor.alpha"].environment["PYTHONNOUSERSITE"] == "1"

    with pytest.raises(PluginContractError, match="cannot be satisfied"):
        resolver.resolve(
            (
                PluginTypeReference(kind=ExtensionType.TASK, type="vendor.alpha"),
                PluginTypeReference(kind=ExtensionType.TASK, type="vendor.beta"),
            )
        )


def test_duplicate_types_are_quarantined_before_activation(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _write_plugin(source, "one", _manifest("vendor.one", "1.0.0", "vendor.duplicate"))
    _write_plugin(source, "two", _manifest("vendor.two", "1.0.0", "vendor.duplicate"))

    manager = _manager(source, tmp_path / "installed")
    conflicts = [
        record
        for record in manager.snapshot.packages
        if record.identity is not None and record.identity[0] in {"vendor.one", "vendor.two"}
    ]

    assert {record.status for record in conflicts} == {PluginLifecycleStatus.QUARANTINED}
    assert all("duplicate type" in record.diagnostics[0] for record in conflicts)


def test_refresh_preserves_old_resolution_and_advances_new_selection(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _write_plugin(source, "v1", _manifest("vendor.refresh", "1.0.0", "vendor.refresh"))
    manager = _manager(source, tmp_path / "installed")
    reference = PluginTypeReference(kind=ExtensionType.TASK, type="vendor.refresh")
    first = PluginResolver(manager.snapshot).resolve((reference,))

    _write_plugin(source, "v2", _manifest("vendor.refresh", "2.0.0", "vendor.refresh"))
    manager.refresh()
    second = PluginResolver(manager.snapshot).resolve((reference,))

    assert first.packages[0].version == "1.0.0"
    assert second.packages[0].version == "2.0.0"
    assert first.resolution_digest != second.resolution_digest


def test_verified_offline_bundle_installation_rejects_digest_and_path_tampering(
    tmp_path: Path,
) -> None:
    bundle = tmp_path / "offline.amesh-plugin"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr(
            "amesh-plugin.json",
            json.dumps(_manifest("vendor.offline", "1.0.0", "vendor.offline")),
        )
        archive.writestr("bin/plugin", "fixture")
    digest = f"sha256:{hashlib.sha256(bundle.read_bytes()).hexdigest()}"
    manager = PluginCatalogManager(
        install_root=tmp_path / "installed",
        platform_version="0.2.0",
    )

    with pytest.raises(ValueError, match="digest mismatch"):
        manager.install_offline_bundle(bundle, expected_digest="sha256:" + "0" * 64)
    installed = manager.install_offline_bundle(bundle, expected_digest=digest)
    assert installed.manifest.name == "vendor.offline"
    assert any(
        record.identity == ("vendor.offline", "1.0.0")
        and record.status is PluginLifecycleStatus.ACTIVE
        for record in manager.snapshot.packages
    )

    unsafe = tmp_path / "unsafe.amesh-plugin"
    with zipfile.ZipFile(unsafe, "w") as archive:
        archive.writestr("../escape", "no")
        archive.writestr(
            "amesh-plugin.json",
            json.dumps(_manifest("vendor.unsafe", "1.0.0", "vendor.unsafe")),
        )
    unsafe_digest = f"sha256:{hashlib.sha256(unsafe.read_bytes()).hexdigest()}"
    with pytest.raises(ValueError, match="unsafe plugin bundle member"):
        manager.install_offline_bundle(unsafe, expected_digest=unsafe_digest)


def test_configured_registry_installs_verified_bundle_and_cli_parses_operator_commands(
    tmp_path: Path,
) -> None:
    registry = tmp_path / "registry"
    registry.mkdir()
    bundle = registry / "registry.amesh-plugin"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr(
            "amesh-plugin.json",
            json.dumps(_manifest("vendor.registry", "1.0.0", "vendor.registry")),
        )
    digest = f"sha256:{hashlib.sha256(bundle.read_bytes()).hexdigest()}"
    index = registry / "index.json"
    index.write_text(
        json.dumps(
            {
                "schemaVersion": "amesh.plugin-registry/v1",
                "packages": [
                    {"bundle": bundle.name, "contentDigest": digest},
                ],
            }
        ),
        encoding="utf-8",
    )

    manager = PluginCatalogManager(
        sources=(
            PluginDiscoverySource(
                kind=PluginSourceKind.REGISTRY,
                location=str(index),
            ),
        ),
        install_root=tmp_path / "installed",
        platform_version="0.2.0",
    )
    record = next(
        item for item in manager.snapshot.packages if item.identity == ("vendor.registry", "1.0.0")
    )
    assert record.status is PluginLifecycleStatus.ACTIVE
    assert record.content_digest == digest
    parsed = build_parser().parse_args(["plugins", "install", str(bundle), "--sha256", digest])
    assert parsed.plugin_command == "install"
    assert parsed.path == bundle


def test_flow_resolution_pins_embedded_package_and_catalog_api_refreshes(tmp_path: Path) -> None:
    manager = PluginCatalogManager(
        install_root=tmp_path / "installed",
        platform_version="0.2.0",
    )
    flow = FlowDefinition.model_validate(
        {
            "id": "plugin_pin",
            "namespace": "tests.plugins",
            "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
        }
    )
    resolution = PluginResolver(manager.snapshot).resolve_flow(flow)
    assert resolution.resources[0].package == "amesh.core"
    assert resolution.resources[0].version == "0.2.0"

    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="plugin-operator",
    )
    authorization = _PluginAuthorizationStub()
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: authorization
    app.dependency_overrides[get_tenant_service] = _TenantQuotaStub
    app.dependency_overrides[get_operational_control_repository] = _OperationalControlStub
    app.dependency_overrides[get_plugin_catalog_manager] = lambda: manager
    app.dependency_overrides[get_plugin_policy_service] = _PluginPolicyStub
    bundle = tmp_path / "api-install.amesh-plugin"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr(
            "amesh-plugin.json",
            json.dumps(_manifest("vendor.api", "1.0.0", "vendor.api")),
        )
    digest = f"sha256:{hashlib.sha256(bundle.read_bytes()).hexdigest()}"

    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as client:
            listed = await client.get(
                "/api/v1/plugins",
                headers={"X-Amesh-Tenant": "default"},
            )
            refreshed = await client.post(
                "/api/v1/plugins/refresh",
                headers={"X-Amesh-Tenant": "default"},
            )
            installed = await client.post(
                "/api/v1/plugins/install",
                params={"contentDigest": digest},
                content=bundle.read_bytes(),
                headers={
                    "X-Amesh-Tenant": "default",
                    "content-type": "application/vnd.amesh.plugin+zip",
                },
            )
        assert listed.status_code == 200
        assert listed.json()["schemaVersion"] == "amesh.plugin-catalog/v1"
        assert "contentPath" not in listed.json()["packages"][0]
        assert refreshed.status_code == 200
        assert refreshed.json()["generation"] == listed.json()["generation"] + 1
        assert installed.status_code == 200
        assert any(
            package.get("manifest", {}).get("name") == "vendor.api"
            for package in installed.json()["packages"]
        )

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


@pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
def test_flow_revision_and_execution_persist_the_original_resolution(
    tmp_path: Path, migrated_test_database_url: str
) -> None:
    async def scenario() -> None:
        source = tmp_path / "source"
        source.mkdir()
        _write_plugin(source, "v1", _manifest("vendor.pin", "1.0.0", "vendor.pin"))
        manager = _manager(source, tmp_path / "installed")
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(
            engine,
            plugin_resolution_provider=lambda flow: (
                PluginResolver(manager.snapshot).resolve_flow(flow).revision_payload()
            ),
        )
        first_flow = FlowDefinition.model_validate(
            {
                "id": "pinned_flow",
                "namespace": "tests.plugins",
                "description": "first",
                "tasks": [{"id": "run", "type": "vendor.pin"}],
            }
        )
        try:
            await repository.apply_flow(first_flow, tenant_id="default")
            first_revision = (
                await repository.list_flow_revisions(
                    first_flow.namespace,
                    first_flow.id,
                    tenant_id="default",
                )
            )[0]
            assert first_revision.plugin_resolution["packages"][0]["version"] == "1.0.0"

            _write_plugin(source, "v2", _manifest("vendor.pin", "2.0.0", "vendor.pin"))
            manager.refresh()
            execution = await repository.create_execution(
                first_flow,
                tenant_id="default",
                inputs={},
            )
            async with engine.connect() as connection:
                execution_pin = await connection.scalar(
                    text(
                        "SELECT revisions.plugin_resolution FROM executions "
                        "JOIN flow_revisions revisions "
                        "ON revisions.id = executions.flow_revision_id "
                        "WHERE executions.id = :execution_id"
                    ),
                    {"execution_id": execution.execution_id},
                )
            assert execution_pin == first_revision.plugin_resolution

            second_flow = first_flow.model_copy(update={"description": "second"})
            await repository.apply_flow(second_flow, tenant_id="default")
            revisions = await repository.list_flow_revisions(
                first_flow.namespace,
                first_flow.id,
                tenant_id="default",
            )
            assert revisions[1].plugin_resolution["packages"][0]["version"] == "2.0.0"
        finally:
            await engine.dispose()

    asyncio.run(scenario())


class _PluginAuthorizationStub:
    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        assert request.resource_type == "plugin"
        assert request.action in {PermissionAction.VIEW, PermissionAction.MANAGE}
        return AuthorizationDecision(
            allowed=True,
            reason_code="allowed",
            summary="test plugin access",
            policy_version=1,
        )


class _OperationalControlStub:
    async def evaluate(
        self,
        boundary: OperationalBoundary,
        **kwargs: object,
    ) -> OperationalControlDecision:
        del kwargs
        return OperationalControlDecision(
            blocked=False,
            boundary=boundary,
            runningWorkPolicy=RunningWorkPolicy.CONTINUE,
        )


class _PluginPolicyStub:
    async def enforce_manifest_administration(
        self,
        manifest: Any,
        content_digest: str,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> None:
        assert manifest.name == "vendor.api"
        assert content_digest.startswith("sha256:")
        assert tenant_id == "default"
        assert actor_id
