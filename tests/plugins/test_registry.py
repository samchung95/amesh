from __future__ import annotations

import asyncio
import base64
import importlib
import io
import json
import threading
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from tests.fixtures.api_stubs import DefaultTenantQuotaStub as _TenantQuotaStub

from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_self_hosted_plugin_registry,
    get_tenant_service,
    require_tenant_context,
)
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    PermissionAction,
    PrincipalType,
)
from amesh.plugin_sdk import (
    PluginCatalogManager,
    PluginCertificationStatus,
    PluginDiscoverySource,
    PluginLifecycleStatus,
    PluginMarketplaceSignals,
    PluginRegistryAttachmentKind,
    PluginRegistryMetadata,
    PluginRegistryPolicy,
    PluginRegistryPublishAttachment,
    PluginRegistryPublishRequest,
    PluginSecurityStatus,
    PluginSourceKind,
    verify_registry_index,
)
from amesh.plugins import SelfHostedPluginRegistry

app_module = importlib.import_module("amesh.app")

_KEY = b"registry-test-signing-key-32-bytes-minimum"


def test_plugin_refresh_endpoint_offloads_catalog_refresh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    main_thread = threading.get_ident()
    refresh_threads: list[int] = []
    snapshot = object()

    class Catalog:
        def refresh(self) -> object:
            refresh_threads.append(threading.get_ident())
            return snapshot

    async def authorize(*args: object, **kwargs: object) -> None:
        del args, kwargs

    monkeypatch.setattr(app_module, "authorize_request", authorize)

    async def scenario() -> None:
        assert (
            await app_module.refresh_plugins(Catalog(), object(), object(), None)  # type: ignore[arg-type]
        ) is snapshot

    asyncio.run(scenario())
    assert refresh_threads
    assert all(thread_id != main_thread for thread_id in refresh_threads)


def _manifest(*, version: str = "1.2.3") -> dict[str, object]:
    return {
        "schemaVersion": "amesh.plugin/v1",
        "name": "vendor.registry",
        "version": version,
        "vendor": "Registry vendor",
        "license": "Apache-2.0",
        "compatibility": {
            "platformVersion": ">=0.2.0,<1.0.0",
            "protocolVersions": ["amesh.plugin.rpc/v1"],
        },
        "entryPoints": [
            {
                "name": "task",
                "resourceType": "vendor.registry.task",
                "type": "task",
                "transport": "stdio",
                "target": "bin/plugin",
                "configurationSchema": {"type": "object"},
                "documentation": {
                    "title": "Registry task",
                    "description": "Signed registry fixture.",
                    "category": "Tests",
                },
            }
        ],
    }


def _bundle(*, payload: str = "fixture", version: str = "1.2.3") -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("amesh-plugin.json", json.dumps(_manifest(version=version)))
        archive.writestr("bin/plugin", payload)
    return output.getvalue()


def _metadata() -> PluginRegistryMetadata:
    return PluginRegistryMetadata(
        license="Apache-2.0",
        sourceUrl="https://source.example/vendor.registry",
        documentationUrl="https://docs.example/vendor.registry",
        supportedPlatformRange=">=0.2.0,<1.0.0",
        sdkRange=">=1.0.0,<2.0.0",
        changelogUrl="https://source.example/vendor.registry/changelog",
    )


def _attachments() -> dict[PluginRegistryAttachmentKind, tuple[str, bytes]]:
    return {
        PluginRegistryAttachmentKind.SBOM: (
            "application/spdx+json",
            b'{"spdxVersion":"SPDX-2.3"}',
        ),
        PluginRegistryAttachmentKind.VULNERABILITY_REPORT: (
            "application/vnd.amesh.vulnerability+json",
            b'{"critical":0,"high":0}',
        ),
        PluginRegistryAttachmentKind.PROVENANCE: (
            "application/vnd.in-toto+json",
            b'{"predicateType":"https://slsa.dev/provenance/v1"}',
        ),
    }


def _signals() -> PluginMarketplaceSignals:
    return PluginMarketplaceSignals(
        lastMaintainedAt=datetime.now(UTC),
        certification=PluginCertificationStatus.CERTIFIED,
        security=PluginSecurityStatus.CURRENT,
    )


def test_registry_publishes_signed_immutable_metadata_and_preserves_yanked_history(
    tmp_path: Path,
) -> None:
    registry = SelfHostedPluginRegistry(
        tmp_path / "registry",
        key_id="test",
        signing_key=_KEY,
    )
    bundle = _bundle()
    release = registry.publish(
        bundle,
        metadata=_metadata(),
        attachments=_attachments(),
        signals=_signals(),
    )

    assert release.name == "vendor.registry"
    assert release.version == "1.2.3"
    assert release.artifact_signature is not None
    assert release.metadata_signature is not None
    assert {item.kind for item in release.attachments} == set(PluginRegistryAttachmentKind)
    assert release.signals.trust_disclaimer.endswith("not a trust guarantee.")
    verify_registry_index(registry.snapshot(), {"test": _KEY})

    installed = PluginCatalogManager(
        sources=(
            PluginDiscoverySource(
                kind=PluginSourceKind.REGISTRY,
                location=str(registry.root / "index.json"),
            ),
        ),
        install_root=tmp_path / "installed",
        platform_version="0.2.0",
        registry_verification_keys={"test": _KEY},
        require_registry_signatures=True,
    )
    record = next(item for item in installed.snapshot.packages if item.identity == release.identity)
    assert record.status is PluginLifecycleStatus.ACTIVE
    assert record.registry_metadata == _metadata()
    assert record.marketplace_signals is not None
    assert record.marketplace_signals.certification is PluginCertificationStatus.CERTIFIED

    with pytest.raises(ValueError, match="different immutable digest"):
        registry.publish(
            _bundle(payload="changed"),
            metadata=_metadata(),
            attachments=_attachments(),
        )

    assert registry.download(release.content_digest) == bundle
    assert registry.release("vendor.registry", "1.2.3").signals.downloads == 1
    yanked = registry.yank("vendor.registry", "1.2.3", reason="security advisory TEST-1")
    assert yanked.yanked is True
    assert registry.download(release.content_digest) == bundle
    assert (registry.root / "blobs" / release.content_digest.removeprefix("sha256:")).is_file()

    after_yank = PluginCatalogManager(
        sources=(
            PluginDiscoverySource(
                kind=PluginSourceKind.REGISTRY,
                location=str(registry.root / "index.json"),
            ),
        ),
        install_root=tmp_path / "installed",
        platform_version="0.2.0",
        registry_verification_keys={"test": _KEY},
        require_registry_signatures=True,
    )
    record = next(
        item for item in after_yank.snapshot.packages if item.identity == release.identity
    )
    assert record.status is PluginLifecycleStatus.YANKED
    assert record.diagnostics == ("security advisory TEST-1",)


def test_registry_rejects_tampering_and_enforces_network_source_policy(tmp_path: Path) -> None:
    registry = SelfHostedPluginRegistry(
        tmp_path / "registry",
        key_id="test",
        signing_key=_KEY,
    )
    release = registry.publish(
        _bundle(),
        metadata=_metadata(),
        attachments=_attachments(),
    )
    blob = registry.root / "blobs" / release.content_digest.removeprefix("sha256:")
    blob.write_bytes(b"tampered")

    manager = PluginCatalogManager(
        sources=(
            PluginDiscoverySource(
                kind=PluginSourceKind.REGISTRY,
                location=str(registry.root / "index.json"),
            ),
        ),
        install_root=tmp_path / "installed",
        registry_verification_keys={"test": _KEY},
        require_registry_signatures=True,
    )
    assert any(
        item.status is PluginLifecycleStatus.QUARANTINED
        and "digest mismatch" in item.diagnostics[0]
        for item in manager.snapshot.packages
    )

    policy = PluginRegistryPolicy(
        allowedOrigins=("https://registry.example",),
        mirrors={"https://registry.example": "https://mirror.internal"},
        proxyUrl="http://proxy.internal:8080",
    )
    assert (
        policy.resolve("https://registry.example/plugins/index.json")
        == "https://mirror.internal/plugins/index.json"
    )
    with pytest.raises(ValueError, match="not allowlisted"):
        policy.resolve("https://untrusted.example/index.json")
    with pytest.raises(ValueError, match="offline policy"):
        PluginRegistryPolicy(allowedOrigins=("https://registry.example",), offline=True).resolve(
            "https://registry.example/index.json"
        )


@pytest.mark.anyio
async def test_registry_offline_export_import_and_authorized_api(tmp_path: Path) -> None:
    source = SelfHostedPluginRegistry(
        tmp_path / "source",
        key_id="test",
        signing_key=_KEY,
    )
    source.publish(
        _bundle(),
        metadata=_metadata(),
        attachments=_attachments(),
        signals=_signals(),
    )
    exported = source.export_offline()
    destination = SelfHostedPluginRegistry(
        tmp_path / "destination",
        key_id="test",
        signing_key=_KEY,
    )
    imported = destination.import_offline(exported)
    assert [(item.name, item.version) for item in imported.packages] == [
        ("vendor.registry", "1.2.3")
    ]

    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="registry-operator",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: _AuthorizationStub()
    app.dependency_overrides[get_tenant_service] = _TenantQuotaStub
    app.dependency_overrides[require_tenant_context] = lambda: "default"
    app.dependency_overrides[get_self_hosted_plugin_registry] = lambda: SelfHostedPluginRegistry(
        tmp_path / "api",
        key_id="test",
        signing_key=_KEY,
    )

    publish_request = PluginRegistryPublishRequest(
        bundleBase64=base64.b64encode(_bundle()).decode("ascii"),
        metadata=_metadata(),
        attachments=tuple(
            PluginRegistryPublishAttachment(
                kind=kind,
                mediaType=media_type,
                contentBase64=base64.b64encode(content).decode("ascii"),
            )
            for kind, (media_type, content) in _attachments().items()
        ),
        signals=_signals(),
    )

    try:
        transport = httpx.ASGITransport(app=app)
        headers = {"X-Amesh-Tenant": "default"}
        async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as client:
            published = await client.post(
                "/api/v1/plugin-registry/packages",
                json=publish_request.model_dump(mode="json", by_alias=True),
                headers=headers,
            )
            listed = await client.get("/api/v1/plugin-registry/index", headers=headers)
            release = await client.get(
                "/api/v1/plugin-registry/packages/vendor.registry/1.2.3",
                headers=headers,
            )
            digest = published.json()["contentDigest"].removeprefix("sha256:")
            downloaded = await client.get(
                f"/api/v1/plugin-registry/blobs/{digest}", headers=headers
            )
            yanked = await client.post(
                "/api/v1/plugin-registry/packages/vendor.registry/1.2.3/yank",
                json={"reason": "operator advisory"},
                headers=headers,
            )
            offline = await client.get("/api/v1/plugin-registry/offline-export", headers=headers)
        assert published.status_code == 200
        assert listed.status_code == 200
        assert listed.json()["signature"]["keyId"] == "test"
        assert release.json()["metadata"]["sdkRange"] == ">=1.0.0,<2.0.0"
        assert downloaded.content == _bundle()
        assert yanked.json()["yanked"] is True
        assert offline.headers["content-type"].startswith(
            "application/vnd.amesh.plugin-registry+zip"
        )

    finally:
        app.dependency_overrides.clear()


class _AuthorizationStub:
    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        assert request.resource_type == "plugin"
        assert request.action in {PermissionAction.VIEW, PermissionAction.MANAGE}
        return AuthorizationDecision(
            allowed=True,
            reason_code="allowed",
            summary="registry test authorization",
            policy_version=1,
        )
