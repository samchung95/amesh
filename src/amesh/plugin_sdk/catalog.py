from __future__ import annotations

import hashlib
import io
import json
import os
import tempfile
import zipfile
from collections import defaultdict
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path, PurePosixPath
from threading import RLock
from typing import Any, Literal
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import url2pathname

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from semantic_version import SimpleSpec, Version  # type: ignore[import-untyped]

from amesh import __version__
from amesh.dsl import ResourceKind, ResourceSchemaRegistry, default_resource_registry

from .manifest import (
    PLUGIN_PROTOCOL_VERSION,
    ExtensionType,
    PluginCompatibility,
    PluginDocumentation,
    PluginEntryPoint,
    PluginManifest,
    PluginTransport,
)
from .registry import (
    PluginMarketplaceSignals,
    PluginRegistryAttachment,
    PluginRegistryIndex,
    PluginRegistryMetadata,
    PluginRegistryPolicy,
    verify_registry_artifact,
    verify_registry_index,
)

PLUGIN_CATALOG_VERSION = "amesh.plugin-catalog/v1"
PLUGIN_BUNDLE_MANIFESTS = (
    "amesh-plugin.json",
    "amesh-plugin.yaml",
    "amesh-plugin.yml",
)
_DIGEST_PATTERN = r"^sha256:[0-9a-f]{64}$"
_DIGEST_MARKER = ".amesh-content-digest"


class PluginSourceKind(StrEnum):
    EMBEDDED = "embedded"
    DIRECTORY = "directory"
    REGISTRY = "registry"
    OFFLINE_BUNDLE = "offline-bundle"


class PluginLifecycleStatus(StrEnum):
    INSTALLED = "installed"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    INCOMPATIBLE = "incompatible"
    QUARANTINED = "quarantined"
    YANKED = "yanked"


class PluginDiscoverySource(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: PluginSourceKind
    location: str = Field(min_length=1, max_length=4096)

    @field_validator("kind")
    @classmethod
    def reject_implicit_embedded_source(cls, value: PluginSourceKind) -> PluginSourceKind:
        if value is PluginSourceKind.EMBEDDED:
            raise ValueError("embedded distributions are supplied by the platform")
        return value


class PluginPackageRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    manifest: PluginManifest | None = None
    content_digest: str | None = Field(default=None, alias="contentDigest")
    source_kind: PluginSourceKind = Field(alias="sourceKind")
    source_location: str = Field(alias="sourceLocation")
    content_path: str | None = Field(default=None, alias="contentPath", exclude=True)
    status: PluginLifecycleStatus
    diagnostics: tuple[str, ...] = ()
    registry_metadata: PluginRegistryMetadata | None = Field(default=None, alias="registryMetadata")
    registry_attachments: tuple[PluginRegistryAttachment, ...] = Field(
        default=(), alias="registryAttachments"
    )
    marketplace_signals: PluginMarketplaceSignals | None = Field(
        default=None, alias="marketplaceSignals"
    )

    @property
    def identity(self) -> tuple[str, str] | None:
        if self.manifest is None:
            return None
        return self.manifest.name, self.manifest.version


class PluginCatalogSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: Literal["amesh.plugin-catalog/v1"] = Field(
        default="amesh.plugin-catalog/v1",
        alias="schemaVersion",
    )
    generation: int = Field(ge=1)
    catalog_digest: str = Field(alias="catalogDigest", pattern=_DIGEST_PATTERN)
    generated_at: datetime = Field(alias="generatedAt")
    packages: tuple[PluginPackageRecord, ...]


class InstalledPluginBundle(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    manifest: PluginManifest
    content_digest: str = Field(alias="contentDigest", pattern=_DIGEST_PATTERN)
    content_path: str = Field(alias="contentPath")


class PluginBundleInstaller:
    """Installs verified bundles into digest-addressed roots without importing their code."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def installed(self, expected_digest: str) -> InstalledPluginBundle | None:
        digest = _validated_digest(expected_digest)
        destination = self._root / digest.removeprefix("sha256:")
        if not destination.is_dir():
            return None
        manifest_path = _single_manifest(destination)
        marker = destination / _DIGEST_MARKER
        if not marker.is_file() or marker.read_text(encoding="utf-8").strip() != digest:
            return None
        return InstalledPluginBundle(
            manifest=_load_manifest(manifest_path),
            contentDigest=digest,
            contentPath=str(destination),
        )

    def inspect_bytes(self, content: bytes, *, expected_digest: str) -> PluginManifest:
        digest = _validated_digest(expected_digest)
        actual = _bytes_digest(content)
        if actual != digest:
            raise ValueError(f"bundle digest mismatch: expected {digest}, received {actual}")
        with tempfile.TemporaryDirectory(prefix="amesh-plugin-inspect-") as temporary:
            extraction_root = Path(temporary) / "extracted"
            extraction_root.mkdir()
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                _validate_archive_members(archive)
                archive.extractall(extraction_root)
            return _load_manifest(_single_manifest(extraction_root))

    def install(self, bundle: str | Path, *, expected_digest: str) -> InstalledPluginBundle:
        return self.install_bytes(Path(bundle).read_bytes(), expected_digest=expected_digest)

    def install_bytes(
        self,
        content: bytes,
        *,
        expected_digest: str,
    ) -> InstalledPluginBundle:
        digest = _validated_digest(expected_digest)
        actual = _bytes_digest(content)
        if actual != digest:
            raise ValueError(f"bundle digest mismatch: expected {digest}, received {actual}")
        existing = self.installed(digest)
        if existing is not None:
            return existing

        destination = self._root / digest.removeprefix("sha256:")
        with tempfile.TemporaryDirectory(prefix="amesh-plugin-", dir=self._root) as temporary:
            extraction_root = Path(temporary) / "extracted"
            extraction_root.mkdir()
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                _validate_archive_members(archive)
                archive.extractall(extraction_root)
            manifest_path = _single_manifest(extraction_root)
            manifest = _load_manifest(manifest_path)
            content_root = manifest_path.parent
            if destination.exists():
                installed = self.installed(digest)
                if installed is None:
                    raise ValueError(f"invalid existing plugin installation at {destination}")
                return installed
            os.replace(content_root, destination)
        (destination / _DIGEST_MARKER).write_text(digest + "\n", encoding="utf-8")
        return InstalledPluginBundle(
            manifest=manifest,
            contentDigest=digest,
            contentPath=str(destination),
        )


class PluginCatalogManager:
    """Owns immutable catalog snapshots while previously returned pins remain valid."""

    def __init__(
        self,
        *,
        sources: Iterable[PluginDiscoverySource] = (),
        install_root: str | Path | None = None,
        platform_version: str = __version__,
        registry_timeout_seconds: float = 10.0,
        registry_policy: PluginRegistryPolicy | None = None,
        registry_verification_keys: Mapping[str, bytes] | None = None,
        require_registry_signatures: bool = False,
    ) -> None:
        self._sources = tuple(sources)
        self._platform_version = platform_version
        self._registry_timeout_seconds = registry_timeout_seconds
        self._registry_policy = registry_policy or PluginRegistryPolicy()
        self._registry_verification_keys = dict(registry_verification_keys or {})
        self._require_registry_signatures = require_registry_signatures
        self._installer = PluginBundleInstaller(
            install_root or Path(tempfile.gettempdir()) / "amesh-plugins"
        )
        self._lock = RLock()
        self._snapshot: PluginCatalogSnapshot | None = None
        self.refresh()

    @property
    def snapshot(self) -> PluginCatalogSnapshot:
        with self._lock:
            if self._snapshot is None:
                raise RuntimeError("plugin catalog has not been initialized")
            return self._snapshot

    def refresh(self) -> PluginCatalogSnapshot:
        with self._lock:
            records = [self._embedded_core_package()]
            for source in self._sources:
                if source.kind is PluginSourceKind.DIRECTORY:
                    records.extend(self._discover_directory(Path(source.location), source))
                elif source.kind is PluginSourceKind.REGISTRY:
                    records.extend(self._discover_registry(source))
                else:
                    records.append(
                        _quarantined(source.kind, source.location, "unsupported discovery source")
                    )
            install_source = PluginDiscoverySource(
                kind=PluginSourceKind.DIRECTORY,
                location=str(self._installer.root),
            )
            records.extend(self._discover_directory(self._installer.root, install_source))
            classified = self._classify(records)
            catalog_digest = _catalog_digest(classified)
            generation = 1 if self._snapshot is None else self._snapshot.generation + 1
            self._snapshot = PluginCatalogSnapshot(
                generation=generation,
                catalogDigest=catalog_digest,
                generatedAt=datetime.now(UTC),
                packages=classified,
            )
            return self._snapshot

    def install_offline_bundle(
        self,
        bundle: str | Path,
        *,
        expected_digest: str,
    ) -> InstalledPluginBundle:
        installed = self._installer.install(bundle, expected_digest=expected_digest)
        self.refresh()
        return installed

    def install_offline_bundle_bytes(
        self,
        content: bytes,
        *,
        expected_digest: str,
    ) -> InstalledPluginBundle:
        installed = self._installer.install_bytes(content, expected_digest=expected_digest)
        self.refresh()
        return installed

    def inspect_offline_bundle_bytes(
        self,
        content: bytes,
        *,
        expected_digest: str,
    ) -> PluginManifest:
        return self._installer.inspect_bytes(content, expected_digest=expected_digest)

    def resource_registry(self) -> ResourceSchemaRegistry:
        registry = default_resource_registry()
        for package in self.snapshot.packages:
            if (
                package.status is not PluginLifecycleStatus.ACTIVE
                or package.manifest is None
                or package.source_kind is PluginSourceKind.EMBEDDED
            ):
                continue
            for entry in package.manifest.entry_points:
                if entry.type not in {ExtensionType.TASK, ExtensionType.TRIGGER}:
                    continue
                kind = (
                    ResourceKind.TASK if entry.type is ExtensionType.TASK else ResourceKind.TRIGGER
                )
                from amesh.dsl import EditorMetadata, ResourceSchemaDescriptor

                registry.register(
                    ResourceSchemaDescriptor(
                        type=entry.resolved_resource_type,
                        kind=kind,
                        configuration_schema=entry.configuration_schema,
                        editor=EditorMetadata(
                            title=entry.documentation.title,
                            description=entry.documentation.description,
                            category=entry.documentation.category,
                            property_order=entry.documentation.property_order,
                        ),
                    )
                )
        return registry

    def _discover_directory(
        self,
        root: Path,
        source: PluginDiscoverySource,
    ) -> list[PluginPackageRecord]:
        if not root.is_dir():
            return [_quarantined(source.kind, source.location, "plugin directory does not exist")]
        manifests = sorted(
            {
                path
                for name in PLUGIN_BUNDLE_MANIFESTS
                for path in root.rglob(name)
                if path.is_file()
            }
        )
        records: list[PluginPackageRecord] = []
        for manifest_path in manifests:
            package_root = manifest_path.parent
            try:
                marker = package_root / _DIGEST_MARKER
                digest = (
                    _validated_digest(marker.read_text(encoding="utf-8").strip())
                    if marker.is_file()
                    else _directory_digest(package_root)
                )
                records.append(
                    PluginPackageRecord(
                        manifest=_load_manifest(manifest_path),
                        contentDigest=digest,
                        sourceKind=source.kind,
                        sourceLocation=str(manifest_path),
                        contentPath=str(package_root.resolve()),
                        status=PluginLifecycleStatus.INSTALLED,
                    )
                )
            except (OSError, ValueError, ValidationError, yaml.YAMLError) as exc:
                records.append(_quarantined(source.kind, str(manifest_path), _safe_diagnostic(exc)))
        return records

    def _discover_registry(self, source: PluginDiscoverySource) -> list[PluginPackageRecord]:
        try:
            payload = json.loads(self._read_location(source.location).decode("utf-8"))
            index = PluginRegistryIndex.model_validate(payload)
            verify_registry_index(
                index,
                self._registry_verification_keys,
                require_signatures=self._require_registry_signatures,
            )
        except (OSError, ValueError, ValidationError, httpx.HTTPError) as exc:
            return [_quarantined(source.kind, source.location, _safe_diagnostic(exc))]
        records: list[PluginPackageRecord] = []
        for item in index.packages:
            try:
                if item.yanked:
                    if item.manifest is None:
                        raise ValueError("yanked registry metadata must include its manifest")
                    records.append(
                        PluginPackageRecord(
                            manifest=item.manifest,
                            contentDigest=item.content_digest,
                            sourceKind=PluginSourceKind.REGISTRY,
                            sourceLocation=source.location,
                            status=PluginLifecycleStatus.YANKED,
                            diagnostics=(item.yank_reason or "registry version is yanked",),
                            registryMetadata=item.metadata,
                            registryAttachments=item.attachments,
                            marketplaceSignals=item.signals,
                        )
                    )
                    continue
                installed = self._installer.installed(item.content_digest)
                if installed is None:
                    bundle_location = _resolve_location(source.location, item.bundle)
                    content = self._read_location(bundle_location)
                    verify_registry_artifact(
                        item,
                        content,
                        self._registry_verification_keys,
                        require_signature=self._require_registry_signatures,
                    )
                    installed = self._installer.install_bytes(
                        content,
                        expected_digest=item.content_digest,
                    )
                if item.name is not None and (
                    installed.manifest.name != item.name
                    or installed.manifest.version != item.version
                ):
                    raise ValueError("registry identity does not match the installed manifest")
                records.append(
                    PluginPackageRecord(
                        manifest=installed.manifest,
                        contentDigest=installed.content_digest,
                        sourceKind=PluginSourceKind.REGISTRY,
                        sourceLocation=source.location,
                        contentPath=installed.content_path,
                        status=PluginLifecycleStatus.INSTALLED,
                        registryMetadata=item.metadata,
                        registryAttachments=item.attachments,
                        marketplaceSignals=item.signals,
                    )
                )
            except (OSError, ValueError, ValidationError, httpx.HTTPError) as exc:
                records.append(_quarantined(source.kind, source.location, _safe_diagnostic(exc)))
        return records

    def _read_location(self, location: str) -> bytes:
        resolved = self._registry_policy.resolve(location)
        parsed = urlparse(resolved)
        if parsed.scheme in {"http", "https"}:
            response = httpx.get(
                resolved,
                timeout=self._registry_timeout_seconds,
                follow_redirects=False,
                proxy=self._registry_policy.proxy_url,
            )
            response.raise_for_status()
            return response.content
        if parsed.scheme == "file":
            path = Path(url2pathname(unquote(parsed.path)))
            return path.read_bytes()
        return Path(resolved).read_bytes()

    def _classify(
        self,
        discovered: Iterable[PluginPackageRecord],
    ) -> tuple[PluginPackageRecord, ...]:
        records = _deduplicate_records(discovered)
        classified: list[PluginPackageRecord] = []
        for record in records:
            if record.manifest is None:
                classified.append(record)
                continue
            compatibility = _compatibility_diagnostics(
                record.manifest,
                platform_version=self._platform_version,
            )
            dependency_ranges = _dependency_range_diagnostics(record.manifest)
            diagnostics = compatibility + dependency_ranges
            if diagnostics:
                classified.append(
                    record.model_copy(
                        update={
                            "status": PluginLifecycleStatus.INCOMPATIBLE,
                            "diagnostics": diagnostics,
                        }
                    )
                )
            elif _is_deprecated(record.manifest):
                classified.append(
                    record.model_copy(update={"status": PluginLifecycleStatus.DEPRECATED})
                )
            else:
                classified.append(record)

        classified = _quarantine_identity_conflicts(classified)
        classified = _quarantine_type_conflicts(classified)
        classified = _mark_missing_dependencies(classified)

        eligible_by_name: dict[str, list[int]] = defaultdict(list)
        for index, record in enumerate(classified):
            if record.manifest is not None and record.status is PluginLifecycleStatus.INSTALLED:
                eligible_by_name[record.manifest.name].append(index)
        for indexes in eligible_by_name.values():
            active_index = max(
                indexes,
                key=lambda index: (
                    Version(classified[index].manifest.version),  # type: ignore[union-attr]
                    classified[index].content_digest or "",
                ),
            )
            classified[active_index] = classified[active_index].model_copy(
                update={"status": PluginLifecycleStatus.ACTIVE}
            )
        return tuple(sorted(classified, key=_record_sort_key))

    def _embedded_core_package(self) -> PluginPackageRecord:
        manifest = _core_manifest()
        digest = _bytes_digest(
            json.dumps(
                manifest.model_dump(mode="json", by_alias=True, exclude_none=True),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        return PluginPackageRecord(
            manifest=manifest,
            contentDigest=digest,
            sourceKind=PluginSourceKind.EMBEDDED,
            sourceLocation="python:amesh.core",
            contentPath="python:amesh.core",
            status=PluginLifecycleStatus.INSTALLED,
        )


def _core_manifest() -> PluginManifest:
    entry_points: list[PluginEntryPoint] = []
    catalog = default_resource_registry().catalog()
    for index, resource in enumerate(catalog["resources"]):
        kind = resource["kind"]
        if kind not in {ResourceKind.TASK.value, ResourceKind.TRIGGER.value}:
            continue
        editor = resource["editor"]
        entry_points.append(
            PluginEntryPoint(
                name=f"resource.{index}",
                resourceType=resource["type"],
                type=ExtensionType(kind),
                transport=PluginTransport.STDIO,
                target=f"amesh.builtin:{resource['type']}",
                configurationSchema=resource["configurationSchema"],
                documentation=PluginDocumentation(
                    title=editor["title"],
                    description=editor["description"],
                    category=editor["category"],
                    propertyOrder=tuple(editor["propertyOrder"]),
                ),
            )
        )
    return PluginManifest(
        name="amesh.core",
        version=__version__,
        vendor="AMESH contributors",
        license="AGPL-3.0-only",
        description="Embedded AMESH core resource distribution.",
        compatibility=PluginCompatibility(
            platformVersion=f">={__version__}",
            protocolVersions=(PLUGIN_PROTOCOL_VERSION,),
        ),
        entryPoints=tuple(entry_points),
    )


def _load_manifest(path: Path) -> PluginManifest:
    content = path.read_text(encoding="utf-8")
    payload: Any = json.loads(content) if path.suffix == ".json" else yaml.safe_load(content)
    if not isinstance(payload, Mapping):
        raise ValueError("plugin manifest root must be an object")
    return PluginManifest.model_validate(payload)


def _single_manifest(root: Path) -> Path:
    manifests = sorted(
        {path for name in PLUGIN_BUNDLE_MANIFESTS for path in root.rglob(name) if path.is_file()}
    )
    if len(manifests) != 1:
        raise ValueError("plugin bundle must contain exactly one manifest")
    return manifests[0]


def _directory_digest(root: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f"plugin package cannot contain symlink: {relative.as_posix()}")
        if _DIGEST_MARKER in relative.parts or any(
            part in {".git", ".venv", "__pycache__"} for part in relative.parts
        ):
            continue
        encoded_path = relative.as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(encoded_path).to_bytes(8, "big"))
        digest.update(encoded_path)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return f"sha256:{digest.hexdigest()}"


def _bytes_digest(content: bytes) -> str:
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def _validated_digest(value: str) -> str:
    if len(value) != 71 or not value.startswith("sha256:"):
        raise ValueError("content digest must use sha256:<64 lowercase hex characters>")
    try:
        int(value.removeprefix("sha256:"), 16)
    except ValueError as exc:
        raise ValueError("content digest must use sha256:<64 lowercase hex characters>") from exc
    if value != value.lower():
        raise ValueError("content digest must use lowercase hexadecimal")
    return value


def _validate_archive_members(archive: zipfile.ZipFile) -> None:
    for member in archive.infolist():
        path = PurePosixPath(member.filename)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise ValueError(f"unsafe plugin bundle member: {member.filename!r}")
        unix_mode = member.external_attr >> 16
        if unix_mode & 0o170000 == 0o120000:
            raise ValueError(f"plugin bundle cannot contain symlink: {member.filename!r}")


def _compatibility_diagnostics(
    manifest: PluginManifest,
    *,
    platform_version: str,
) -> tuple[str, ...]:
    diagnostics: list[str] = []
    try:
        if not SimpleSpec(manifest.compatibility.platform_version).match(Version(platform_version)):
            diagnostics.append(
                f"platform {platform_version} does not satisfy "
                f"{manifest.compatibility.platform_version}"
            )
    except ValueError:
        diagnostics.append(
            f"invalid platform version range {manifest.compatibility.platform_version!r}"
        )
    if PLUGIN_PROTOCOL_VERSION not in manifest.compatibility.protocol_versions:
        diagnostics.append(f"protocol {PLUGIN_PROTOCOL_VERSION} is not supported")
    return tuple(diagnostics)


def _dependency_range_diagnostics(manifest: PluginManifest) -> tuple[str, ...]:
    diagnostics: list[str] = []
    for dependency in manifest.dependencies:
        try:
            SimpleSpec(dependency.version_range)
        except ValueError:
            diagnostics.append(
                f"dependency {dependency.name} has invalid range {dependency.version_range!r}"
            )
    return tuple(diagnostics)


def _is_deprecated(manifest: PluginManifest) -> bool:
    return any(item.subject in {"*", "package", manifest.name} for item in manifest.deprecations)


def _deduplicate_records(
    records: Iterable[PluginPackageRecord],
) -> list[PluginPackageRecord]:
    unique: list[PluginPackageRecord] = []
    seen: set[tuple[str, str, str | None]] = set()
    for record in records:
        identity = record.identity
        if identity is None:
            unique.append(record)
            continue
        key = (*identity, record.content_digest)
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def _quarantine_identity_conflicts(
    records: list[PluginPackageRecord],
) -> list[PluginPackageRecord]:
    identities: dict[tuple[str, str], set[str | None]] = defaultdict(set)
    for record in records:
        if record.identity is not None:
            identities[record.identity].add(record.content_digest)
    conflicts = {identity for identity, digests in identities.items() if len(digests) > 1}
    return [
        _with_diagnostic(record, PluginLifecycleStatus.QUARANTINED, "duplicate identity")
        if record.identity in conflicts
        else record
        for record in records
    ]


def _quarantine_type_conflicts(
    records: list[PluginPackageRecord],
) -> list[PluginPackageRecord]:
    providers: dict[tuple[ExtensionType, str], set[str]] = defaultdict(set)
    for record in records:
        if record.manifest is None or record.status in {
            PluginLifecycleStatus.QUARANTINED,
            PluginLifecycleStatus.INCOMPATIBLE,
            PluginLifecycleStatus.YANKED,
        }:
            continue
        for entry in record.manifest.entry_points:
            providers[(entry.type, entry.resolved_resource_type)].add(record.manifest.name)
    conflicts = {key for key, names in providers.items() if len(names) > 1}
    classified: list[PluginPackageRecord] = []
    for record in records:
        if record.manifest is None:
            classified.append(record)
            continue
        duplicate = next(
            (
                key
                for key in conflicts
                if any(
                    entry.type is key[0] and entry.resolved_resource_type == key[1]
                    for entry in record.manifest.entry_points
                )
            ),
            None,
        )
        if duplicate is None:
            classified.append(record)
        else:
            classified.append(
                _with_diagnostic(
                    record,
                    PluginLifecycleStatus.QUARANTINED,
                    f"duplicate type {duplicate[0].value}/{duplicate[1]}",
                )
            )
    return classified


def _mark_missing_dependencies(
    records: list[PluginPackageRecord],
) -> list[PluginPackageRecord]:
    candidates: dict[str, list[PluginPackageRecord]] = defaultdict(list)
    for record in records:
        if record.manifest is not None and record.status not in {
            PluginLifecycleStatus.QUARANTINED,
            PluginLifecycleStatus.INCOMPATIBLE,
            PluginLifecycleStatus.YANKED,
        }:
            candidates[record.manifest.name].append(record)
    classified: list[PluginPackageRecord] = []
    for record in records:
        if record.manifest is None or record.status in {
            PluginLifecycleStatus.QUARANTINED,
            PluginLifecycleStatus.INCOMPATIBLE,
            PluginLifecycleStatus.YANKED,
        }:
            classified.append(record)
            continue
        missing: list[str] = []
        for dependency in record.manifest.dependencies:
            if dependency.optional:
                continue
            spec = SimpleSpec(dependency.version_range)
            if not any(
                item.manifest is not None and spec.match(Version(item.manifest.version))
                for item in candidates.get(dependency.name, ())
            ):
                missing.append(
                    f"dependency {dependency.name} has no version matching "
                    f"{dependency.version_range}"
                )
        if missing:
            classified.append(
                record.model_copy(
                    update={
                        "status": PluginLifecycleStatus.INCOMPATIBLE,
                        "diagnostics": (*record.diagnostics, *missing),
                    }
                )
            )
        else:
            classified.append(record)
    return classified


def _with_diagnostic(
    record: PluginPackageRecord,
    status: PluginLifecycleStatus,
    diagnostic: str,
) -> PluginPackageRecord:
    return record.model_copy(
        update={
            "status": status,
            "diagnostics": (*record.diagnostics, diagnostic),
        }
    )


def _quarantined(
    kind: PluginSourceKind,
    location: str,
    diagnostic: str,
) -> PluginPackageRecord:
    return PluginPackageRecord(
        sourceKind=kind,
        sourceLocation=location,
        status=PluginLifecycleStatus.QUARANTINED,
        diagnostics=(diagnostic,),
    )


def _record_sort_key(record: PluginPackageRecord) -> tuple[str, str, str, str]:
    if record.manifest is None:
        return ("~", "~", record.source_kind.value, record.source_location)
    return (
        record.manifest.name,
        record.manifest.version,
        record.content_digest or "",
        record.source_location,
    )


def _catalog_digest(records: Iterable[PluginPackageRecord]) -> str:
    payload = [
        {
            "name": record.manifest.name if record.manifest else None,
            "version": record.manifest.version if record.manifest else None,
            "contentDigest": record.content_digest,
            "status": record.status.value,
            "diagnostics": list(record.diagnostics),
        }
        for record in records
    ]
    return _bytes_digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _resolve_location(index_location: str, bundle_location: str) -> str:
    parsed = urlparse(index_location)
    if parsed.scheme in {"http", "https", "file"}:
        return urljoin(index_location, bundle_location)
    bundle = Path(bundle_location)
    if bundle.is_absolute():
        return str(bundle)
    return str((Path(index_location).resolve().parent / bundle).resolve())


def _safe_diagnostic(exc: BaseException) -> str:
    if isinstance(exc, ValidationError):
        return "invalid plugin metadata"
    return str(exc) or type(exc).__name__
