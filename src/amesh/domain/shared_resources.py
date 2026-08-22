from __future__ import annotations

import json
import re
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_DURATION = re.compile(
    r"^P(?=.+)(?:\d+(?:[.,]\d+)?Y)?(?:\d+(?:[.,]\d+)?M)?(?:\d+(?:[.,]\d+)?W)?"
    r"(?:\d+(?:[.,]\d+)?D)?(?:T(?=.+)(?:\d+(?:[.,]\d+)?H)?"
    r"(?:\d+(?:[.,]\d+)?M)?(?:\d+(?:[.,]\d+)?S)?)?$",
    re.IGNORECASE,
)


def normalize_resource_path(value: str) -> str:
    normalized = value.replace("\\", "/").strip("/")
    segments = normalized.split("/")
    if not normalized or any(segment in {"", ".", ".."} for segment in segments):
        raise ValueError("resource path must be a normalized relative path")
    if len(normalized) > 1024:
        raise ValueError("resource path cannot exceed 1024 characters")
    return normalized


def normalize_resource_key(value: str) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > 256 or any(char.isspace() for char in normalized):
        raise ValueError("resource key must contain 1-256 non-whitespace characters")
    return normalized


class KeyValueType(StrEnum):
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    DATETIME = "DATETIME"
    DATE = "DATE"
    DURATION = "DURATION"
    JSON = "JSON"


def validate_typed_value(value_type: KeyValueType, value: Any) -> Any:
    if value_type is KeyValueType.STRING:
        if not isinstance(value, str):
            raise ValueError("STRING key-value requires a string")
    elif value_type is KeyValueType.NUMBER:
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValueError("NUMBER key-value requires a number")
    elif value_type is KeyValueType.BOOLEAN:
        if not isinstance(value, bool):
            raise ValueError("BOOLEAN key-value requires a boolean")
    elif value_type is KeyValueType.DATETIME:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("DATETIME key-value requires ISO-8601") from exc
        if parsed.tzinfo is None:
            raise ValueError("DATETIME key-value requires a time-zone offset")
        value = parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")
    elif value_type is KeyValueType.DATE:
        try:
            value = date.fromisoformat(str(value)).isoformat()
        except ValueError as exc:
            raise ValueError("DATE key-value requires ISO-8601") from exc
    elif value_type is KeyValueType.DURATION and (
        not isinstance(value, str) or _DURATION.fullmatch(value) is None
    ):
        raise ValueError("DURATION key-value requires ISO-8601")
    try:
        encoded = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("key-value must be JSON serializable") from exc
    if len(encoded.encode()) > 1_048_576:
        raise ValueError("key-value cannot exceed 1 MiB")
    return value


class NamespaceFile(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    namespace: str
    path: str
    version: int = Field(ge=1)
    resource_version: int = Field(alias="resourceVersion", ge=1)
    size_bytes: int = Field(alias="sizeBytes", ge=0)
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")
    content_type: str | None = Field(default=None, alias="contentType")
    metadata: dict[str, Any] = Field(default_factory=dict)
    origin_namespace: str = Field(alias="originNamespace")
    inherited: bool = False
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class NamespaceFileVersion(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    namespace: str
    path: str
    version: int = Field(ge=1)
    size_bytes: int = Field(alias="sizeBytes", ge=0)
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")
    content_type: str | None = Field(default=None, alias="contentType")
    object_uri: str = Field(alias="objectUri", exclude=True)
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(alias="createdAt")


class KeyValueWrite(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    value_type: KeyValueType = Field(alias="type")
    value: Any
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    metadata: dict[str, Any] = Field(default_factory=dict)
    expected_version: int | None = Field(default=None, alias="expectedVersion", ge=0)

    @model_validator(mode="after")
    def validate_value_and_expiry(self) -> KeyValueWrite:
        object.__setattr__(self, "value", validate_typed_value(self.value_type, self.value))
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise ValueError("expiresAt must include a time-zone offset")
        return self


class KeyValueEntry(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    namespace: str
    key: str
    value_type: KeyValueType = Field(alias="type")
    value: Any
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    metadata: dict[str, Any] = Field(default_factory=dict)
    resource_version: int = Field(alias="resourceVersion", ge=1)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class KeyValueChange(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    cursor: int = Field(ge=1)
    namespace: str
    key: str
    operation: str
    resource_version: int = Field(alias="resourceVersion", ge=1)
    value_type: KeyValueType | None = Field(default=None, alias="type")
    metadata: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(alias="occurredAt")


class SecretBindingWrite(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    provider: str = Field(default="env", pattern=r"^env$")
    provider_reference: str = Field(alias="providerReference", min_length=1, max_length=512)
    metadata: dict[str, Any] = Field(default_factory=dict)
    expected_version: int | None = Field(default=None, alias="expectedVersion", ge=0)

    @field_validator("provider_reference")
    @classmethod
    def validate_environment_name(cls, value: str) -> str:
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value) is None:
            raise ValueError("env provider reference must be an environment variable name")
        return value


class SecretBinding(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    namespace: str
    key: str
    provider: str
    provider_reference: str = Field(alias="providerReference")
    metadata: dict[str, Any] = Field(default_factory=dict)
    resource_version: int = Field(alias="resourceVersion", ge=1)
    inherited: bool = False
    origin_namespace: str = Field(alias="originNamespace")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class NamespaceFileExport(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    path: str
    content_base64: str = Field(alias="contentBase64")
    content_type: str | None = Field(default=None, alias="contentType")
    metadata: dict[str, Any] = Field(default_factory=dict)


class KeyValueExport(KeyValueWrite):
    key: str


class SecretBindingExport(SecretBindingWrite):
    key: str


class NamespaceResourceBundle(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: str = Field(default="amesh.namespace-resources/v1", alias="schemaVersion")
    source_namespace: str = Field(alias="sourceNamespace")
    exported_at: datetime = Field(alias="exportedAt")
    files: tuple[NamespaceFileExport, ...] = ()
    key_values: tuple[KeyValueExport, ...] = Field(default=(), alias="keyValues")
    secrets: tuple[SecretBindingExport, ...] = ()
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")
