from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PLUGIN_MANIFEST_VERSION = "amesh.plugin/v1"
PLUGIN_PROTOCOL_VERSION = "amesh.plugin.rpc/v1"
_SEMVER_PATTERN = (
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
_NAME_PATTERN = r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$"
_RESOURCE_TYPE_PATTERN = r"^[A-Za-z][A-Za-z0-9]*(?:[.-][A-Za-z0-9]+)*$"


class ExtensionType(StrEnum):
    TASK = "task"
    TRIGGER = "trigger"
    CONDITION = "condition"
    RUNNER = "runner"
    STORAGE = "storage"
    SECRET = "secret"
    EXPRESSION = "expression"
    NOTIFICATION = "notification"


class PluginTransport(StrEnum):
    STDIO = "stdio"
    GRPC = "grpc"
    HTTP = "http"


class PluginNetworkAccess(StrEnum):
    NONE = "none"
    RESTRICTED = "restricted"


class PluginFilesystemAccess(StrEnum):
    NONE = "none"
    WORKSPACE_READ = "workspace-read"
    WORKSPACE_WRITE = "workspace-write"


class PluginDependency(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str = Field(pattern=_NAME_PATTERN, max_length=255)
    version_range: str = Field(alias="versionRange", min_length=1, max_length=128)
    optional: bool = False

    @field_validator("version_range")
    @classmethod
    def validate_version_range(cls, value: str) -> str:
        if value.strip() != value or any(ord(character) < 32 for character in value):
            raise ValueError("versionRange must be a trimmed printable semantic-version range")
        return value


class PluginCompatibility(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    platform_version: str = Field(
        alias="platformVersion",
        min_length=1,
        max_length=128,
    )
    protocol_versions: tuple[str, ...] = Field(
        default=(PLUGIN_PROTOCOL_VERSION,),
        alias="protocolVersions",
        min_length=1,
    )

    @field_validator("platform_version")
    @classmethod
    def validate_platform_version(cls, value: str) -> str:
        if value.strip() != value or any(ord(character) < 32 for character in value):
            raise ValueError("platformVersion must be a trimmed printable semantic-version range")
        return value

    @field_validator("protocol_versions")
    @classmethod
    def validate_protocol_versions(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("protocolVersions must be unique")
        return value


class PluginCapabilities(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    required: tuple[str, ...] = ()
    network_access: PluginNetworkAccess = Field(
        default=PluginNetworkAccess.NONE,
        alias="networkAccess",
    )
    allowed_egress: tuple[str, ...] = Field(default=(), alias="allowedEgress")
    filesystem_access: PluginFilesystemAccess = Field(
        default=PluginFilesystemAccess.NONE,
        alias="filesystemAccess",
    )
    secret_scopes: tuple[str, ...] = Field(default=(), alias="secretScopes")

    @field_validator("required", "allowed_egress", "secret_scopes")
    @classmethod
    def validate_unique_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("capability declaration values must be unique")
        if any(not item or item.strip() != item for item in value):
            raise ValueError("capability declaration values must be non-empty and trimmed")
        return value

    @model_validator(mode="after")
    def validate_network_access(self) -> PluginCapabilities:
        if self.network_access is PluginNetworkAccess.NONE and self.allowed_egress:
            raise ValueError("allowedEgress requires restricted networkAccess")
        return self


class PluginDocumentation(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=4096)
    category: str = Field(min_length=1, max_length=128)
    property_order: tuple[str, ...] = Field(default=(), alias="propertyOrder")
    icon: str | None = Field(default=None, max_length=512)
    documentation_url: str | None = Field(default=None, alias="documentationUrl", max_length=2048)
    examples: tuple[dict[str, Any], ...] = ()


class PluginEntryPoint(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str = Field(pattern=_NAME_PATTERN, max_length=255)
    resource_type: str | None = Field(
        default=None,
        alias="resourceType",
        pattern=_RESOURCE_TYPE_PATTERN,
        max_length=255,
    )
    type: ExtensionType
    api_version: Literal["amesh.extension/v1"] = Field(
        default="amesh.extension/v1",
        alias="apiVersion",
    )
    transport: PluginTransport
    target: str = Field(min_length=1, max_length=2048)
    configuration_schema: dict[str, Any] = Field(alias="configurationSchema")
    output_schema: dict[str, Any] | None = Field(default=None, alias="outputSchema")
    documentation: PluginDocumentation

    @property
    def resolved_resource_type(self) -> str:
        return self.resource_type or self.name

    @field_validator("configuration_schema", "output_schema")
    @classmethod
    def validate_json_schema(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        try:
            Draft202012Validator.check_schema(value)
        except SchemaError as exc:
            raise ValueError(f"invalid Draft 2020-12 JSON Schema: {exc.message}") from exc
        return value


class PluginDeprecation(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    subject: str = Field(min_length=1, max_length=255)
    deprecated_in: str = Field(alias="deprecatedIn", pattern=_SEMVER_PATTERN)
    removed_in: str | None = Field(default=None, alias="removedIn", pattern=_SEMVER_PATTERN)
    replacement: str | None = Field(default=None, max_length=255)
    message: str = Field(min_length=1, max_length=4096)


class PluginManifest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.plugin/v1"] = Field(
        default="amesh.plugin/v1",
        alias="schemaVersion",
    )
    name: str = Field(pattern=_NAME_PATTERN, max_length=255)
    version: str = Field(pattern=_SEMVER_PATTERN)
    vendor: str = Field(min_length=1, max_length=255)
    license: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4096)
    compatibility: PluginCompatibility
    entry_points: tuple[PluginEntryPoint, ...] = Field(alias="entryPoints", min_length=1)
    dependencies: tuple[PluginDependency, ...] = ()
    capabilities: PluginCapabilities = Field(default_factory=PluginCapabilities)
    deprecations: tuple[PluginDeprecation, ...] = ()

    @model_validator(mode="after")
    def validate_unique_declarations(self) -> PluginManifest:
        entry_names = [item.name for item in self.entry_points]
        if len(entry_names) != len(set(entry_names)):
            raise ValueError("plugin entry point names must be unique")
        entry_keys = [(item.type, item.resolved_resource_type) for item in self.entry_points]
        if len(entry_keys) != len(set(entry_keys)):
            raise ValueError("plugin entry point type/resourceType pairs must be unique")
        dependency_names = [item.name for item in self.dependencies]
        if len(dependency_names) != len(set(dependency_names)):
            raise ValueError("plugin dependency names must be unique")
        if self.name in dependency_names:
            raise ValueError("plugin cannot depend on itself")
        return self
