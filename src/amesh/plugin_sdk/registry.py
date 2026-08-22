from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .manifest import PluginManifest

PLUGIN_REGISTRY_VERSION = "amesh.plugin-registry/v1"
_DIGEST_PATTERN = r"^sha256:[0-9a-f]{64}$"
_SIGNATURE_PATTERN = r"^[0-9a-f]{64}$"


class PluginRegistryAttachmentKind(StrEnum):
    SBOM = "sbom"
    VULNERABILITY_REPORT = "vulnerability-report"
    PROVENANCE = "provenance"


class PluginCertificationStatus(StrEnum):
    UNVERIFIED = "unverified"
    COMMUNITY = "community"
    VERIFIED = "verified"
    CERTIFIED = "certified"


class PluginSecurityStatus(StrEnum):
    UNKNOWN = "unknown"
    CURRENT = "current"
    ADVISORY = "advisory"
    CRITICAL = "critical"


class PluginRegistrySignature(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key_id: str = Field(alias="keyId", min_length=1, max_length=255)
    algorithm: Literal["hmac-sha256"] = "hmac-sha256"
    value: str = Field(pattern=_SIGNATURE_PATTERN)


class PluginRegistryMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    license: str = Field(min_length=1, max_length=255)
    source_url: str = Field(alias="sourceUrl", min_length=1, max_length=2048)
    documentation_url: str = Field(alias="documentationUrl", min_length=1, max_length=2048)
    supported_platform_range: str = Field(
        alias="supportedPlatformRange", min_length=1, max_length=128
    )
    sdk_range: str = Field(alias="sdkRange", min_length=1, max_length=128)
    changelog_url: str = Field(alias="changelogUrl", min_length=1, max_length=2048)


class PluginMarketplaceSignals(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    downloads: int = Field(default=0, ge=0)
    last_maintained_at: datetime | None = Field(default=None, alias="lastMaintainedAt")
    certification: PluginCertificationStatus = PluginCertificationStatus.UNVERIFIED
    security: PluginSecurityStatus = PluginSecurityStatus.UNKNOWN
    trust_disclaimer: Literal["Signals are informational and are not a trust guarantee."] = Field(
        default="Signals are informational and are not a trust guarantee.",
        alias="trustDisclaimer",
    )


class PluginRegistryAttachment(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: PluginRegistryAttachmentKind
    media_type: str = Field(alias="mediaType", min_length=1, max_length=255)
    blob: str = Field(min_length=1, max_length=4096)
    content_digest: str = Field(alias="contentDigest", pattern=_DIGEST_PATTERN)
    signature: PluginRegistrySignature


class PluginRegistryPackage(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    version: str | None = Field(default=None, min_length=1, max_length=128)
    bundle: str = Field(min_length=1, max_length=4096)
    content_digest: str = Field(alias="contentDigest", pattern=_DIGEST_PATTERN)
    manifest: PluginManifest | None = None
    metadata: PluginRegistryMetadata | None = None
    attachments: tuple[PluginRegistryAttachment, ...] = ()
    signals: PluginMarketplaceSignals = Field(default_factory=PluginMarketplaceSignals)
    artifact_signature: PluginRegistrySignature | None = Field(
        default=None, alias="artifactSignature"
    )
    metadata_signature: PluginRegistrySignature | None = Field(
        default=None, alias="metadataSignature"
    )
    published_at: datetime | None = Field(default=None, alias="publishedAt")
    yanked: bool = False
    yanked_at: datetime | None = Field(default=None, alias="yankedAt")
    yank_reason: str | None = Field(default=None, alias="yankReason", max_length=4096)

    @property
    def identity(self) -> tuple[str, str] | None:
        if self.name is None or self.version is None:
            return None
        return self.name, self.version

    @model_validator(mode="after")
    def validate_release_identity(self) -> PluginRegistryPackage:
        if (self.name is None) != (self.version is None):
            raise ValueError("registry package name and version must be declared together")
        if self.manifest is not None and (
            self.name != self.manifest.name or self.version != self.manifest.version
        ):
            raise ValueError("registry identity must match the embedded plugin manifest")
        kinds = [attachment.kind for attachment in self.attachments]
        if len(kinds) != len(set(kinds)):
            raise ValueError("registry attachment kinds must be unique")
        if self.yanked and (self.yanked_at is None or self.yank_reason is None):
            raise ValueError("yanked packages require a timestamp and reason")
        return self


class PluginRegistryIndex(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.plugin-registry/v1"] = Field(
        default="amesh.plugin-registry/v1",
        alias="schemaVersion",
    )
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="generatedAt")
    packages: tuple[PluginRegistryPackage, ...] = ()
    signature: PluginRegistrySignature | None = None


class PluginRegistryPublishAttachment(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: PluginRegistryAttachmentKind
    media_type: str = Field(alias="mediaType", min_length=1, max_length=255)
    content_base64: str = Field(alias="contentBase64", min_length=1)


class PluginRegistryPublishRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    bundle_base64: str = Field(alias="bundleBase64", min_length=1)
    metadata: PluginRegistryMetadata
    attachments: tuple[PluginRegistryPublishAttachment, ...]
    signals: PluginMarketplaceSignals = Field(default_factory=PluginMarketplaceSignals)


class PluginRegistryYankRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    reason: str = Field(min_length=1, max_length=4096)


class PluginRegistryPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    allowed_origins: tuple[str, ...] = Field(default=(), alias="allowedOrigins")
    mirrors: dict[str, str] = Field(default_factory=dict)
    proxy_url: str | None = Field(default=None, alias="proxyUrl", max_length=2048)
    offline: bool = False

    @field_validator("allowed_origins")
    @classmethod
    def validate_allowed_origins(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(_origin(item) for item in value)
        if len(normalized) != len(set(normalized)):
            raise ValueError("registry allowed origins must be unique")
        return normalized

    @field_validator("mirrors")
    @classmethod
    def validate_mirrors(cls, value: dict[str, str]) -> dict[str, str]:
        return {_origin(source): target.rstrip("/") for source, target in value.items()}

    def resolve(self, location: str) -> str:
        parsed = urlparse(location)
        if parsed.scheme not in {"http", "https"}:
            return location
        if self.offline:
            raise ValueError("network registry access is disabled by offline policy")
        origin = _origin(location)
        if origin not in self.allowed_origins:
            raise ValueError(f"registry origin is not allowlisted: {origin}")
        mirror = self.mirrors.get(origin)
        if mirror is None:
            return location
        suffix = parsed.path or "/"
        if parsed.query:
            suffix += f"?{parsed.query}"
        return mirror + suffix


def content_digest(content: bytes) -> str:
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def sign_registry_payload(content: bytes, *, key_id: str, key: bytes) -> PluginRegistrySignature:
    if len(key) < 32:
        raise ValueError("registry signing keys must contain at least 32 bytes")
    return PluginRegistrySignature(
        keyId=key_id,
        value=hmac.new(key, content, hashlib.sha256).hexdigest(),
    )


def sign_registry_package(
    package: PluginRegistryPackage,
    *,
    key_id: str,
    key: bytes,
) -> PluginRegistryPackage:
    signature = sign_registry_payload(
        _package_signing_payload(package),
        key_id=key_id,
        key=key,
    )
    return package.model_copy(update={"metadata_signature": signature})


def sign_registry_index(
    index: PluginRegistryIndex,
    *,
    key_id: str,
    key: bytes,
) -> PluginRegistryIndex:
    signature = sign_registry_payload(
        _index_signing_payload(index),
        key_id=key_id,
        key=key,
    )
    return index.model_copy(update={"signature": signature})


def verify_registry_index(
    index: PluginRegistryIndex,
    keys: dict[str, bytes],
    *,
    require_signatures: bool = True,
) -> None:
    _verify_signature(
        index.signature,
        _index_signing_payload(index),
        keys,
        require=require_signatures,
        subject="registry index",
    )
    for package in index.packages:
        _verify_signature(
            package.metadata_signature,
            _package_signing_payload(package),
            keys,
            require=require_signatures,
            subject=f"registry metadata {package.name or package.content_digest}",
        )


def verify_registry_artifact(
    package: PluginRegistryPackage,
    content: bytes,
    keys: dict[str, bytes],
    *,
    require_signature: bool = True,
) -> None:
    actual = content_digest(content)
    if actual != package.content_digest:
        raise ValueError(
            f"registry artifact digest mismatch: expected {package.content_digest}, received {actual}"
        )
    _verify_signature(
        package.artifact_signature,
        content,
        keys,
        require=require_signature,
        subject=f"plugin artifact {package.name or package.content_digest}",
    )


def verify_registry_attachment(
    attachment: PluginRegistryAttachment,
    content: bytes,
    keys: dict[str, bytes],
) -> None:
    actual = content_digest(content)
    if actual != attachment.content_digest:
        raise ValueError(
            f"registry attachment digest mismatch: expected {attachment.content_digest}, received {actual}"
        )
    _verify_signature(
        attachment.signature,
        content,
        keys,
        require=True,
        subject=f"registry attachment {attachment.kind.value}",
    )


def _verify_signature(
    signature: PluginRegistrySignature | None,
    content: bytes,
    keys: dict[str, bytes],
    *,
    require: bool,
    subject: str,
) -> None:
    if signature is None:
        if require:
            raise ValueError(f"{subject} is unsigned")
        return
    key = keys.get(signature.key_id)
    if key is None:
        raise ValueError(f"{subject} uses an untrusted signing key: {signature.key_id}")
    expected = hmac.new(key, content, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature.value, expected):
        raise ValueError(f"{subject} signature verification failed")


def _package_signing_payload(package: PluginRegistryPackage) -> bytes:
    payload = package.model_dump(mode="json", by_alias=True, exclude_none=True)
    payload.pop("metadataSignature", None)
    return _canonical_json(payload)


def _index_signing_payload(index: PluginRegistryIndex) -> bytes:
    payload = index.model_dump(mode="json", by_alias=True, exclude_none=True)
    payload.pop("signature", None)
    return _canonical_json(payload)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _origin(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("registry origins must be absolute HTTP(S) URLs")
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"
