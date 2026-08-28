from __future__ import annotations

import re
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)
from uuid6 import uuid7

_NATURAL_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_-]*$"
_TENANT_SLUG_PATTERN = r"^[a-z0-9][a-z0-9-]*$"
_NATURAL_ID = re.compile(_NATURAL_ID_PATTERN)
_TENANT_SLUG = re.compile(_TENANT_SLUG_PATTERN)
_INTERNAL_PREFIX = "_amesh"


class InvalidIdentifier(ValueError):
    """Raised when a resource identifier violates the canonical policy."""


def validate_natural_id(value: str) -> str:
    if not _NATURAL_ID.fullmatch(value):
        raise InvalidIdentifier(
            "identifier must start with an alphanumeric character and contain only "
            "letters, numbers, underscores and hyphens"
        )
    if value.casefold().startswith(_INTERNAL_PREFIX):
        raise InvalidIdentifier(f"identifier prefix {_INTERNAL_PREFIX!r} is reserved")
    return value


def validate_tenant_slug(value: str) -> str:
    if not _TENANT_SLUG.fullmatch(value):
        raise InvalidIdentifier(
            "tenant slug must be lowercase, start with an alphanumeric character and "
            "contain only lowercase letters, numbers and hyphens"
        )
    return value


def validate_namespace(value: str) -> str:
    for segment in value.split("."):
        validate_natural_id(segment)
    return value


NaturalId = Annotated[
    str,
    StringConstraints(min_length=1, max_length=128, pattern=_NATURAL_ID_PATTERN),
    AfterValidator(validate_natural_id),
]
TenantSlug = Annotated[
    str,
    StringConstraints(min_length=1, max_length=63, pattern=_TENANT_SLUG_PATTERN),
    AfterValidator(validate_tenant_slug),
]
NamespaceId = Annotated[
    str,
    StringConstraints(min_length=1, max_length=255),
    AfterValidator(validate_namespace),
]


def new_runtime_id() -> UUID:
    """Return a monotonically sortable RFC 9562 UUIDv7 value."""

    return uuid7()


class RuntimeResourceType(StrEnum):
    TENANT = "tenant"
    NAMESPACE = "namespace"
    FLOW = "flow"
    FLOW_REVISION = "flow_revision"
    EXECUTION = "execution"
    TASK_RUN = "task_run"
    TRIGGER = "trigger"
    WORKER = "worker"
    PLUGIN = "plugin"
    ASSET = "asset"


class RuntimeIdentity(BaseModel):
    model_config = ConfigDict(frozen=True)

    resource_type: RuntimeResourceType
    id: UUID = Field(default_factory=new_runtime_id)


class TenantKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: TenantSlug


class NamespaceKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant: TenantSlug
    namespace: NamespaceId


class FlowKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant: TenantSlug
    namespace: NamespaceId
    flow_id: NaturalId


class FlowRevisionKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    flow: FlowKey
    revision: int = Field(ge=1)


class TaskRunKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    task_path: NaturalId
    iteration_key: str | None = Field(default=None, max_length=512)


class TriggerKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    flow: FlowKey
    trigger_id: NaturalId


class WorkerKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    worker_group: NaturalId
    instance_name: str = Field(min_length=1, max_length=255)


class PluginKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: NamespaceId
    version: str = Field(min_length=1, max_length=128)
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        if value.strip() != value or any(character.isspace() for character in value):
            raise InvalidIdentifier("plugin version cannot contain whitespace")
        return value


class AssetKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant: TenantSlug
    provider: NaturalId
    external_key: str = Field(min_length=1, max_length=1024)

    @field_validator("external_key")
    @classmethod
    def validate_external_key(cls, value: str) -> str:
        if any(ord(character) < 32 for character in value):
            raise InvalidIdentifier("asset external key cannot contain control characters")
        return value
