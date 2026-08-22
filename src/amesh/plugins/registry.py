from __future__ import annotations

import base64
import binascii
import io
import json
import os
import tempfile
import zipfile
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from threading import RLock
from typing import Any

import yaml
from pydantic import ValidationError

from amesh.plugin_sdk.manifest import PluginManifest
from amesh.plugin_sdk.registry import (
    PluginMarketplaceSignals,
    PluginRegistryAttachment,
    PluginRegistryAttachmentKind,
    PluginRegistryIndex,
    PluginRegistryMetadata,
    PluginRegistryPackage,
    PluginRegistryPublishRequest,
    content_digest,
    sign_registry_index,
    sign_registry_package,
    sign_registry_payload,
    verify_registry_artifact,
    verify_registry_attachment,
    verify_registry_index,
)

_MANIFEST_NAMES = ("amesh-plugin.json", "amesh-plugin.yaml", "amesh-plugin.yml")
_REQUIRED_ATTACHMENTS = frozenset(PluginRegistryAttachmentKind)


class SelfHostedPluginRegistry:
    """Filesystem-backed immutable OSS registry with signed metadata and offline transfer."""

    def __init__(
        self,
        root: str | Path,
        *,
        key_id: str,
        signing_key: bytes,
        trusted_keys: Mapping[str, bytes] | None = None,
    ) -> None:
        if not key_id:
            raise ValueError("registry signing key id is required")
        if len(signing_key) < 32:
            raise ValueError("registry signing keys must contain at least 32 bytes")
        self._root = Path(root).resolve()
        self._blob_root = self._root / "blobs"
        self._index_path = self._root / "index.json"
        self._key_id = key_id
        self._signing_key = signing_key
        self._trusted_keys = {**(trusted_keys or {}), key_id: signing_key}
        self._lock = RLock()
        self._blob_root.mkdir(parents=True, exist_ok=True)
        if not self._index_path.exists():
            self._persist(())
        self.snapshot()

    @property
    def root(self) -> Path:
        return self._root

    def snapshot(self) -> PluginRegistryIndex:
        with self._lock:
            payload = json.loads(self._index_path.read_text(encoding="utf-8"))
            index = PluginRegistryIndex.model_validate(payload)
            verify_registry_index(index, self._trusted_keys)
            return index

    def publish_request(self, request: PluginRegistryPublishRequest) -> PluginRegistryPackage:
        try:
            bundle = base64.b64decode(request.bundle_base64, validate=True)
            attachments = {
                item.kind: (
                    item.media_type,
                    base64.b64decode(item.content_base64, validate=True),
                )
                for item in request.attachments
            }
        except (ValueError, binascii.Error) as exc:
            raise ValueError("registry publish content must use valid base64") from exc
        return self.publish(
            bundle,
            metadata=request.metadata,
            attachments=attachments,
            signals=request.signals,
        )

    def publish(
        self,
        bundle: bytes,
        *,
        metadata: PluginRegistryMetadata,
        attachments: Mapping[PluginRegistryAttachmentKind, tuple[str, bytes]],
        signals: PluginMarketplaceSignals | None = None,
    ) -> PluginRegistryPackage:
        if set(attachments) != _REQUIRED_ATTACHMENTS:
            required = ", ".join(sorted(item.value for item in _REQUIRED_ATTACHMENTS))
            raise ValueError(f"registry publish requires exactly these attachments: {required}")
        manifest = _bundle_manifest(bundle)
        if metadata.license != manifest.license:
            raise ValueError("registry license metadata must match the plugin manifest")
        if metadata.supported_platform_range != manifest.compatibility.platform_version:
            raise ValueError("registry platform range must match the plugin manifest")
        digest = content_digest(bundle)
        with self._lock:
            packages = list(self.snapshot().packages)
            existing = next(
                (
                    package
                    for package in packages
                    if package.name == manifest.name and package.version == manifest.version
                ),
                None,
            )
            if existing is not None:
                if existing.content_digest != digest:
                    raise ValueError(
                        "plugin name and semantic version already identify a different immutable digest"
                    )
                return existing

            self._write_blob(digest, bundle)
            attachment_records: list[PluginRegistryAttachment] = []
            for kind in sorted(attachments, key=lambda item: item.value):
                media_type, content = attachments[kind]
                attachment_digest = content_digest(content)
                self._write_blob(attachment_digest, content)
                attachment_records.append(
                    PluginRegistryAttachment(
                        kind=kind,
                        mediaType=media_type,
                        blob=_blob_location(attachment_digest),
                        contentDigest=attachment_digest,
                        signature=sign_registry_payload(
                            content,
                            key_id=self._key_id,
                            key=self._signing_key,
                        ),
                    )
                )

            package = PluginRegistryPackage(
                name=manifest.name,
                version=manifest.version,
                bundle=_blob_location(digest),
                contentDigest=digest,
                manifest=manifest,
                metadata=metadata,
                attachments=tuple(attachment_records),
                signals=signals or PluginMarketplaceSignals(),
                artifactSignature=sign_registry_payload(
                    bundle,
                    key_id=self._key_id,
                    key=self._signing_key,
                ),
                publishedAt=datetime.now(UTC),
            )
            package = sign_registry_package(
                package,
                key_id=self._key_id,
                key=self._signing_key,
            )
            packages.append(package)
            self._persist(packages)
            return package

    def release(self, name: str, version: str) -> PluginRegistryPackage:
        package = next(
            (
                item
                for item in self.snapshot().packages
                if item.name == name and item.version == version
            ),
            None,
        )
        if package is None:
            raise KeyError(f"plugin release not found: {name}@{version}")
        return package

    def yank(self, name: str, version: str, *, reason: str) -> PluginRegistryPackage:
        if not reason.strip():
            raise ValueError("yank reason is required")
        with self._lock:
            packages = list(self.snapshot().packages)
            for index, package in enumerate(packages):
                if package.name == name and package.version == version:
                    updated = package.model_copy(
                        update={
                            "yanked": True,
                            "yanked_at": datetime.now(UTC),
                            "yank_reason": reason,
                            "metadata_signature": None,
                        }
                    )
                    updated = sign_registry_package(
                        updated,
                        key_id=self._key_id,
                        key=self._signing_key,
                    )
                    packages[index] = updated
                    self._persist(packages)
                    return updated
        raise KeyError(f"plugin release not found: {name}@{version}")

    def download(self, digest: str) -> bytes:
        with self._lock:
            packages = list(self.snapshot().packages)
            matching = [
                (index, package)
                for index, package in enumerate(packages)
                if package.content_digest == digest
            ]
            if not matching:
                raise KeyError(f"plugin artifact not found: {digest}")
            content = self._read_blob(digest)
            for index, package in matching:
                verify_registry_artifact(package, content, self._trusted_keys)
                signals = package.signals.model_copy(
                    update={"downloads": package.signals.downloads + 1}
                )
                updated = package.model_copy(
                    update={"signals": signals, "metadata_signature": None}
                )
                packages[index] = sign_registry_package(
                    updated,
                    key_id=self._key_id,
                    key=self._signing_key,
                )
            self._persist(packages)
            return content

    def export_offline(self) -> bytes:
        with self._lock:
            index = self.snapshot()
            output = io.BytesIO()
            with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(
                    "index.json",
                    index.model_dump_json(by_alias=True, exclude_none=True, indent=2),
                )
                digests = {package.content_digest for package in index.packages} | {
                    attachment.content_digest
                    for package in index.packages
                    for attachment in package.attachments
                }
                for digest in sorted(digests):
                    archive.writestr(_blob_location(digest), self._read_blob(digest))
            return output.getvalue()

    def import_offline(self, content: bytes) -> PluginRegistryIndex:
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                _validate_archive(archive)
                index = PluginRegistryIndex.model_validate_json(archive.read("index.json"))
                verify_registry_index(index, self._trusted_keys)
                blobs = {
                    digest: archive.read(_blob_location(digest))
                    for digest in {package.content_digest for package in index.packages}
                    | {
                        attachment.content_digest
                        for package in index.packages
                        for attachment in package.attachments
                    }
                }
        except (KeyError, OSError, ValidationError, zipfile.BadZipFile) as exc:
            raise ValueError("invalid offline plugin registry bundle") from exc

        for package in index.packages:
            verify_registry_artifact(package, blobs[package.content_digest], self._trusted_keys)
            for attachment in package.attachments:
                verify_registry_attachment(
                    attachment,
                    blobs[attachment.content_digest],
                    self._trusted_keys,
                )

        with self._lock:
            packages = list(self.snapshot().packages)
            by_identity = {(item.name, item.version): item for item in packages}
            for package in index.packages:
                identity = (package.name, package.version)
                existing = by_identity.get(identity)
                if existing is not None and existing.content_digest != package.content_digest:
                    raise ValueError(
                        "offline import conflicts with an existing immutable plugin release"
                    )
                if existing is None:
                    packages.append(package)
                    by_identity[identity] = package
                self._write_blob(package.content_digest, blobs[package.content_digest])
                for attachment in package.attachments:
                    self._write_blob(
                        attachment.content_digest,
                        blobs[attachment.content_digest],
                    )
            return self._persist(packages)

    def _read_blob(self, digest: str) -> bytes:
        path = self._blob_path(digest)
        if not path.is_file():
            raise KeyError(f"registry blob not found: {digest}")
        content = path.read_bytes()
        if content_digest(content) != digest:
            raise ValueError(f"registry blob digest verification failed: {digest}")
        return content

    def _write_blob(self, digest: str, content: bytes) -> None:
        if content_digest(content) != digest:
            raise ValueError("registry blob content does not match its digest")
        destination = self._blob_path(digest)
        if destination.exists():
            if destination.read_bytes() != content:
                raise ValueError(f"immutable registry blob collision: {digest}")
            return
        with tempfile.NamedTemporaryFile(dir=self._blob_root, delete=False) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, destination)

    def _blob_path(self, digest: str) -> Path:
        if len(digest) != 71 or not digest.startswith("sha256:"):
            raise ValueError("registry digest must use sha256:<64 lowercase hex characters>")
        suffix = digest.removeprefix("sha256:")
        if any(character not in "0123456789abcdef" for character in suffix):
            raise ValueError("registry digest must use lowercase hexadecimal")
        return self._blob_root / suffix

    def _persist(
        self,
        packages: list[PluginRegistryPackage] | tuple[PluginRegistryPackage, ...],
    ) -> PluginRegistryIndex:
        ordered = tuple(
            sorted(
                packages,
                key=lambda item: (item.name or "", item.version or "", item.content_digest),
            )
        )
        index = sign_registry_index(
            PluginRegistryIndex(packages=ordered),
            key_id=self._key_id,
            key=self._signing_key,
        )
        self._root.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=self._root,
            delete=False,
        ) as temporary:
            temporary.write(index.model_dump_json(by_alias=True, exclude_none=True, indent=2))
            temporary.write("\n")
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, self._index_path)
        return index


def _bundle_manifest(content: bytes) -> PluginManifest:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            _validate_archive(archive)
            manifest_names = [
                name
                for name in archive.namelist()
                if PurePosixPath(name).name in _MANIFEST_NAMES and not name.endswith("/")
            ]
            if len(manifest_names) != 1:
                raise ValueError("plugin bundle must contain exactly one manifest")
            name = manifest_names[0]
            raw = archive.read(name).decode("utf-8")
            payload: Any = json.loads(raw) if name.endswith(".json") else yaml.safe_load(raw)
    except (UnicodeDecodeError, json.JSONDecodeError, yaml.YAMLError, zipfile.BadZipFile) as exc:
        raise ValueError("invalid plugin bundle manifest") from exc
    if not isinstance(payload, dict):
        raise ValueError("plugin bundle manifest root must be an object")
    return PluginManifest.model_validate(payload)


def _validate_archive(archive: zipfile.ZipFile) -> None:
    for member in archive.infolist():
        path = PurePosixPath(member.filename)
        if path.is_absolute() or ".." in path.parts or "\\" in member.filename:
            raise ValueError(f"unsafe registry archive member: {member.filename}")


def _blob_location(digest: str) -> str:
    return f"blobs/{digest.removeprefix('sha256:')}"
