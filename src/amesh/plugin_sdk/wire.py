from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from .contracts import PluginRequest, PluginResponse
from .manifest import ExtensionType

PLUGIN_WIRE_VERSION = "amesh.plugin.wire/v1"
JSON_RPC_VERSION = "2.0"
PLUGIN_METHOD_HANDSHAKE = "amesh.handshake"
PLUGIN_METHOD_DISCOVER = "amesh.discover"
PLUGIN_METHOD_VALIDATE = "amesh.validate"
PLUGIN_METHOD_INVOKE = "amesh.invoke"
PLUGIN_METHOD_CANCEL = "amesh.cancel"
PLUGIN_METHOD_SHUTDOWN = "amesh.shutdown"
PLUGIN_NOTIFICATION_HEARTBEAT = "amesh.heartbeat"
PLUGIN_NOTIFICATION_LOG = "amesh.log"
PLUGIN_NOTIFICATION_METRIC = "amesh.metric"
PLUGIN_NOTIFICATION_ARTIFACT = "amesh.artifact"
PLUGIN_NOTIFICATION_ASSET = "amesh.asset"


class PluginWireFeature(StrEnum):
    SCHEMA_DISCOVERY = "schema-discovery"
    VALIDATION = "validation"
    EXECUTION = "execution"
    CANCELLATION = "cancellation"
    HEARTBEATS = "heartbeats"
    LOGS = "logs"
    METRICS = "metrics"
    ARTIFACTS = "artifacts"
    ASSETS = "assets"


SUPPORTED_WIRE_FEATURES = tuple(PluginWireFeature)
REQUIRED_WIRE_FEATURES = tuple(
    feature for feature in SUPPORTED_WIRE_FEATURES if feature is not PluginWireFeature.ASSETS
)


class JsonRpcError(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    code: int
    message: str = Field(min_length=1, max_length=4096)
    data: dict[str, Any] = Field(default_factory=dict)


class JsonRpcRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    jsonrpc: Literal["2.0"] = "2.0"
    id: str = Field(min_length=1, max_length=255)
    method: str = Field(min_length=1, max_length=255)
    params: dict[str, Any] = Field(default_factory=dict)


class JsonRpcNotification(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    jsonrpc: Literal["2.0"] = "2.0"
    method: str = Field(min_length=1, max_length=255)
    params: dict[str, Any] = Field(default_factory=dict)


class JsonRpcResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    jsonrpc: Literal["2.0"] = "2.0"
    id: str = Field(min_length=1, max_length=255)
    result: dict[str, Any] | None = None
    error: JsonRpcError | None = None

    @model_validator(mode="after")
    def require_exactly_one_outcome(self) -> JsonRpcResponse:
        if (self.result is None) == (self.error is None):
            raise ValueError("JSON-RPC response requires exactly one of result or error")
        return self


class PluginHandshakeParams(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    protocol_versions: tuple[str, ...] = Field(alias="protocolVersions", min_length=1)
    required_features: tuple[PluginWireFeature, ...] = Field(
        alias="requiredFeatures",
        min_length=1,
    )
    plugin: str
    version: str
    content_digest: str = Field(alias="contentDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    session_id: str = Field(alias="sessionId", min_length=1, max_length=255)
    workload_token: SecretStr = Field(alias="workloadToken", repr=False)
    expires_at: datetime = Field(alias="expiresAt")


class PluginHandshakeResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    protocol_version: Literal["amesh.plugin.wire/v1"] = Field(alias="protocolVersion")
    features: tuple[PluginWireFeature, ...]
    plugin: str
    version: str
    content_digest: str = Field(alias="contentDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    session_id: str = Field(alias="sessionId", min_length=1, max_length=255)
    workload_token: SecretStr = Field(alias="workloadToken", repr=False)


class PluginCapabilityEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    capability_tokens: dict[str, SecretStr] = Field(
        default_factory=dict,
        alias="capabilityTokens",
        repr=False,
    )
    secrets: dict[str, SecretStr] = Field(default_factory=dict, repr=False)
    files: dict[str, str] = Field(default_factory=dict)
    allowed_egress: tuple[str, ...] = Field(default=(), alias="allowedEgress")
    platform_apis: tuple[str, ...] = Field(default=(), alias="platformApis")


class PluginInvocationParams(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: str = Field(alias="sessionId", min_length=1, max_length=255)
    workload_token: SecretStr = Field(alias="workloadToken", repr=False)
    request: PluginRequest
    capabilities: PluginCapabilityEnvelope = Field(default_factory=PluginCapabilityEnvelope)


class PluginAuthenticatedParams(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: str = Field(alias="sessionId", min_length=1, max_length=255)
    workload_token: SecretStr = Field(alias="workloadToken", repr=False)
    invocation_id: str | None = Field(default=None, alias="invocationId", max_length=255)


class PluginWireEntryPoint(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str
    type: ExtensionType
    resource_type: str = Field(alias="resourceType")
    configuration_schema: dict[str, Any] = Field(alias="configurationSchema")
    output_schema: dict[str, Any] | None = Field(default=None, alias="outputSchema")


class PluginDiscoveryResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: str = Field(alias="sessionId")
    workload_token: SecretStr = Field(alias="workloadToken", repr=False)
    entry_points: tuple[PluginWireEntryPoint, ...] = Field(alias="entryPoints")


class PluginMetric(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=256)
    kind: Literal["counter", "gauge", "timer"] = "gauge"
    value: float
    unit: str | None = Field(default=None, max_length=64)
    labels: dict[str, str] = Field(default_factory=dict)


class PluginArtifact(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    uri: str = Field(min_length=1, max_length=4096)
    size_bytes: int = Field(alias="sizeBytes", ge=0)
    media_type: str | None = Field(default=None, alias="mediaType", max_length=255)
    checksum_sha256: str | None = Field(
        default=None,
        alias="checksumSha256",
        pattern=r"^[0-9a-f]{64}$",
    )
    logical_path: str | None = Field(default=None, alias="logicalPath", max_length=4096)


class PluginAsset(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    provider: str = Field(min_length=1, max_length=128)
    account: str = Field(default="default", min_length=1, max_length=255)
    location: str = Field(default="global", min_length=1, max_length=512)
    asset_type: str = Field(alias="assetType", min_length=1, max_length=128)
    external_key: str = Field(alias="externalKey", min_length=1, max_length=1024)
    display_name: str = Field(alias="displayName", min_length=1, max_length=512)
    access_mode: Literal["READ", "WRITE"] = Field(alias="accessMode")
    description: str = Field(default="", max_length=4096)
    owner: str | None = Field(default=None, max_length=255)
    contacts: tuple[str, ...] = ()
    domain_group: str | None = Field(default=None, alias="domainGroup", max_length=255)
    tags: tuple[str, ...] = ()
    custom_metadata: dict[str, Any] = Field(default_factory=dict, alias="customMetadata")
    artifact_uri: str | None = Field(default=None, alias="artifactUri", max_length=4096)


class PluginInvocationResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: str = Field(alias="sessionId")
    workload_token: SecretStr = Field(alias="workloadToken", repr=False)
    response: PluginResponse


class PluginWireContract(BaseModel):
    """Schema bundle for language-neutral SDK generation and compatibility checks."""

    request: JsonRpcRequest
    notification: JsonRpcNotification
    response: JsonRpcResponse
    handshake: PluginHandshakeParams
    ready: PluginHandshakeResult
    invocation: PluginInvocationParams
    discovery: PluginDiscoveryResult
    authenticated: PluginAuthenticatedParams
    metric: PluginMetric
    artifact: PluginArtifact
    asset: PluginAsset
