from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import parse_qs, quote, unquote, urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .shared_resources import normalize_resource_path

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_VERSION = re.compile(r"^[1-9][0-9]*$")
_SCHEMA_VERSION = "amesh.artifact-ref/v1"


class ArtifactProvenance(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    source: str = Field(min_length=1, max_length=255)
    origin_namespace: str = Field(alias="originNamespace", min_length=1, max_length=255)
    created_by: str = Field(alias="createdBy", min_length=1, max_length=255)
    created_at: datetime = Field(alias="createdAt")
    lineage: tuple[str, ...] = ()


class ArtifactRetention(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    retention_until: datetime | None = Field(default=None, alias="retentionUntil")
    legal_hold: bool = Field(default=False, alias="legalHold")

    @field_validator("retention_until")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("retentionUntil must include a time-zone offset")
        return value


class ArtifactRef(BaseModel):
    """A tenant-safe, content-addressed reference to a namespace artifact."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: str = Field(default=_SCHEMA_VERSION, alias="schemaVersion")
    reference: str = Field(min_length=1, max_length=4096)
    content_address: str = Field(alias="contentAddress", pattern=r"^sha256:[0-9a-f]{64}$")
    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    namespace: str = Field(min_length=1, max_length=255)
    path: str = Field(min_length=1, max_length=1024)
    version: int = Field(ge=1)
    media_type: str | None = Field(default=None, alias="mediaType", max_length=255)
    size_bytes: int = Field(alias="sizeBytes", ge=0)
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")
    provenance: ArtifactProvenance
    retention: ArtifactRetention

    @model_validator(mode="after")
    def validate_content_reference(self) -> ArtifactRef:
        reference_path, reference_version, reference_checksum = parse_artifact_reference(
            self.reference
        )
        if reference_path != self.path or reference_version != self.version:
            raise ValueError("artifact reference does not match its path or version")
        if reference_checksum != self.checksum_sha256:
            raise ValueError("artifact reference digest does not match checksumSha256")
        if self.content_address != f"sha256:{self.checksum_sha256}":
            raise ValueError("contentAddress must match checksumSha256")
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(f"schemaVersion must be {_SCHEMA_VERSION}")
        return self


def build_artifact_reference(path: str, version: int, checksum_sha256: str) -> str:
    normalized_path = normalize_resource_path(path)
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise ValueError("artifact version must be positive")
    if _SHA256.fullmatch(checksum_sha256) is None:
        raise ValueError("artifact checksum must be a lowercase SHA-256 digest")
    return (
        f"nsfile:///{quote(normalized_path, safe='/')}?version={version}&sha256={checksum_sha256}"
    )


def parse_artifact_reference(reference: str) -> tuple[str, int, str]:
    """Parse the exact opaque namespace-artifact reference syntax."""

    parsed = urlsplit(reference)
    if (
        parsed.scheme != "nsfile"
        or parsed.netloc
        or parsed.fragment
        or not parsed.path.startswith("/")
        or not parsed.path.removeprefix("/")
    ):
        raise ValueError("artifact reference must be an opaque nsfile reference")
    raw_path = unquote(parsed.path.removeprefix("/"))
    path = normalize_resource_path(raw_path)
    values = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
    if set(values) != {"version", "sha256"} or any(len(items) != 1 for items in values.values()):
        raise ValueError("artifact reference query must contain version and sha256 only")
    version_value = values["version"][0]
    checksum = values["sha256"][0]
    if _VERSION.fullmatch(version_value) is None:
        raise ValueError("artifact reference version must be a positive integer")
    if _SHA256.fullmatch(checksum) is None:
        raise ValueError("artifact reference sha256 must be a lowercase SHA-256 digest")
    return path, int(version_value), checksum


__all__ = [
    "ArtifactProvenance",
    "ArtifactRef",
    "ArtifactRetention",
    "build_artifact_reference",
    "parse_artifact_reference",
]
