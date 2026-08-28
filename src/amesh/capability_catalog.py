"""Deterministic, redacted projections of agent capabilities.

The catalog is deliberately a projection.  Immutable resource, connection and
plugin ledgers remain authoritative; this module only selects the fields that
are useful for discovery and exact attachment.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .domain.agent_primitives import McpConnectionRevision
from .domain.agent_resources import (
    AgentDefinitionSpec,
    AgentEvaluationSpec,
    AgentResourceKind,
    AgentResourceRevision,
    ModelPolicySpec,
    PromptSpec,
    SkillSpec,
)
from .domain.resources import canonical_hash
from .domain.tool_provider import ToolProviderKind
from .plugin_sdk.manifest import ExtensionType
from .plugin_sdk.registry import PluginRegistryPackage


class CapabilityKind(StrEnum):
    """Kinds exposed by the cross-resource catalog."""

    PROMPT = "prompt"
    SKILL = "skill"
    MODEL_POLICY = "model-policy"
    EVALUATION = "evaluation"
    AGENT = "agent"
    MCP_CONNECTION = "mcp-connection"
    MCP_TOOL = "mcp-tool"
    PLUGIN = "plugin"


class CapabilityStatus(StrEnum):
    AVAILABLE = "available"
    DEPRECATED = "deprecated"
    INCOMPATIBLE = "incompatible"
    UNAVAILABLE = "unavailable"
    DENIED = "denied"
    SCHEMA_DRIFT = "schema-drift"
    YANKED = "yanked"


class CapabilityImpact(StrEnum):
    NONE = "NONE"
    READ_ONLY = "READ_ONLY"
    IDEMPOTENT_WRITE = "IDEMPOTENT_WRITE"
    HIGH_IMPACT = "HIGH_IMPACT"


class CapabilityAttachmentTarget(StrEnum):
    AGENT_DEFINITION = "agent-definition"
    WORKFLOW = "workflow"
    NONE = "none"


class CapabilitySource(StrEnum):
    AGENTS = "agents"
    CONNECTIONS = "connections"
    PLUGINS = "plugins"


class CapabilitySourceAccessStatus(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"


class CapabilitySourceAccess(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    source: CapabilitySource
    status: CapabilitySourceAccessStatus
    diagnostics: tuple[str, ...] = ()


class CapabilityPermissions(BaseModel):
    """Non-secret policy declarations needed to assess compatibility."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    delegated_capabilities: tuple[str, ...] = Field(default=(), alias="delegatedCapabilities")
    tool_allowlist: tuple[str, ...] = Field(default=(), alias="toolAllowlist")
    secret_scopes: tuple[str, ...] = Field(default=(), alias="secretScopes")
    network_hosts: tuple[str, ...] = Field(default=(), alias="networkHosts")
    allowed_egress: tuple[str, ...] = Field(default=(), alias="allowedEgress")
    filesystem_read_roots: tuple[str, ...] = Field(default=(), alias="filesystemReadRoots")
    filesystem_write_roots: tuple[str, ...] = Field(default=(), alias="filesystemWriteRoots")
    allow_high_impact: bool = Field(default=False, alias="allowHighImpact")


class CapabilityReference(BaseModel):
    """A canonical exact pin suitable for a future attach command."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: CapabilityKind
    key: str = Field(min_length=1, max_length=512)
    revision: int | str
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    provider_kind: ToolProviderKind | None = Field(default=None, alias="providerKind")
    provider_key: str | None = Field(default=None, alias="providerKey")
    provider_revision: int | None = Field(default=None, alias="providerRevision", ge=1)
    provider_digest: str | None = Field(
        default=None,
        alias="providerDigest",
        pattern=r"^sha256:[0-9a-f]{64}$",
    )
    connection_key: str | None = Field(default=None, alias="connectionKey")
    connection_revision: int | None = Field(default=None, alias="connectionRevision", ge=1)
    connection_digest: str | None = Field(
        default=None,
        alias="connectionDigest",
        pattern=r"^sha256:[0-9a-f]{64}$",
    )
    tool_name: str | None = Field(default=None, alias="toolName")
    schema_digest: str | None = Field(
        default=None,
        alias="schemaDigest",
        pattern=r"^sha256:[0-9a-f]{64}$",
    )


class CapabilityAttachment(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    target: CapabilityAttachmentTarget
    reference: CapabilityReference | None = None
    constraints: tuple[str, ...] = ()


class CapabilityCatalogItem(BaseModel):
    """Safe, bounded description of one attachable or supporting capability."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    catalog_id: str = Field(alias="catalogId", min_length=1, max_length=1024)
    kind: CapabilityKind
    key: str = Field(min_length=1, max_length=512)
    human_label: str = Field(alias="humanLabel", min_length=1, max_length=512)
    revision: int | str
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    status: CapabilityStatus = CapabilityStatus.AVAILABLE
    description: str = Field(default="", max_length=4096)
    schemas: dict[str, Any] = Field(default_factory=dict)
    impact: CapabilityImpact = CapabilityImpact.NONE
    permissions: CapabilityPermissions = Field(default_factory=CapabilityPermissions)
    provider_compatibility: tuple[str, ...] = Field(default=(), alias="providerCompatibility")
    attachment: CapabilityAttachment
    diagnostics: tuple[str, ...] = ()


class CapabilityCatalog(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.capability-catalog/v1"] = Field(
        default="amesh.capability-catalog/v1", alias="schemaVersion"
    )
    namespace: str | None = None
    generated_at: datetime = Field(alias="generatedAt")
    catalog_digest: str = Field(alias="catalogDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    source_access: tuple[CapabilitySourceAccess, ...] = Field(default=(), alias="sourceAccess")
    total: int = Field(ge=0)
    returned: int = Field(ge=0)
    truncated: bool = False
    items: tuple[CapabilityCatalogItem, ...] = ()

    @property
    def entries(self) -> tuple[CapabilityCatalogItem, ...]:
        """Compatibility spelling for callers that call catalog rows entries."""

        return self.items


def _reference(
    *, kind: CapabilityKind, key: str, revision: int | str, digest: str, **kwargs: Any
) -> CapabilityReference:
    return CapabilityReference(
        kind=kind,
        key=key,
        revision=revision,
        digest=digest,
        **kwargs,
    )


def _resource_attachment(resource: AgentResourceRevision) -> CapabilityAttachment:
    if resource.kind is AgentResourceKind.AGENT:
        target = CapabilityAttachmentTarget.WORKFLOW
        constraint = "agent definitions attach to workflow agent nodes"
    else:
        target = CapabilityAttachmentTarget.AGENT_DEFINITION
        constraint = "resource revisions attach to agent definitions by exact key and revision"
    return CapabilityAttachment(
        target=target,
        reference=_reference(
            kind=CapabilityKind(resource.kind.value.lower().replace("_", "-")),
            key=resource.key,
            revision=resource.revision,
            digest=resource.digest,
        ),
        constraints=(constraint,),
    )


def _resource_permissions(resource: AgentResourceRevision) -> CapabilityPermissions:
    spec = resource.spec
    if isinstance(spec, AgentDefinitionSpec):
        permissions = spec.permissions
        return CapabilityPermissions(
            delegatedCapabilities=permissions.delegated_capabilities,
            toolAllowlist=permissions.tool_allowlist,
            secretScopes=permissions.secret_scopes,
            networkHosts=permissions.network_hosts,
            filesystemReadRoots=permissions.filesystem_read_roots,
            filesystemWriteRoots=permissions.filesystem_write_roots,
            allowHighImpact=permissions.allow_high_impact_tools,
        )
    if isinstance(spec, SkillSpec):
        return CapabilityPermissions(delegatedCapabilities=spec.requested_capabilities)
    if isinstance(spec, ModelPolicySpec):
        return CapabilityPermissions(
            delegatedCapabilities=tuple(
                feature for route in spec.routes for feature in route.required_features
            )
        )
    return CapabilityPermissions()


def _resource_projection(resource: AgentResourceRevision) -> CapabilityCatalogItem:
    spec = resource.spec
    kind = CapabilityKind(resource.kind.value.lower().replace("_", "-"))
    schemas: dict[str, Any] = {}
    compatibility: tuple[str, ...] = ()
    description = ""
    label = resource.key

    if isinstance(spec, PromptSpec):
        label = spec.title
        schemas = {
            "variables": {
                "type": "object",
                "properties": {
                    key: {"type": "string", "description": description}
                    for key, description in sorted(spec.variables.items())
                },
                "additionalProperties": False,
            }
        }
    elif isinstance(spec, SkillSpec):
        label = spec.title
        description = spec.description
        schemas = {"requestedCapabilities": list(spec.requested_capabilities)}
    elif isinstance(spec, ModelPolicySpec):
        label = spec.title
        schemas = {
            "routes": [
                {
                    "routeId": route.route_id,
                    "model": route.model,
                    "requiredFeatures": list(route.required_features),
                    "adapter": route.provider.adapter,
                }
                for route in spec.routes
            ]
        }
        compatibility = tuple(
            sorted({f"{route.provider.adapter}:{route.model}" for route in spec.routes})
        )
    elif isinstance(spec, AgentEvaluationSpec):
        label = spec.title
        description = spec.description
        schemas = {
            "assertions": list(spec.assertions),
            "rubric": [
                {"key": criterion.key, "assertion": criterion.assertion}
                for criterion in spec.rubric
            ],
        }
    elif isinstance(spec, AgentDefinitionSpec):
        label = spec.title
        description = spec.description
        schemas = {"inputSchema": spec.input_schema, "outputSchema": spec.output_schema}
        compatibility = tuple(sorted(spec.permissions.network_hosts))

    return CapabilityCatalogItem(
        catalogId=f"{kind.value}:{resource.key}:{resource.revision}",
        kind=kind,
        key=resource.key,
        humanLabel=label,
        revision=resource.revision,
        digest=resource.digest,
        description=description,
        schemas=schemas,
        permissions=_resource_permissions(resource),
        providerCompatibility=compatibility,
        attachment=_resource_attachment(resource),
    )


def project_agent_resource(resource: AgentResourceRevision) -> CapabilityCatalogItem:
    """Project one immutable agent resource without exposing its body."""

    return _resource_projection(resource)


def project_mcp_connection(connection: McpConnectionRevision) -> tuple[CapabilityCatalogItem, ...]:
    """Project a connection and its exact pinned tools."""

    spec = connection.spec
    connection_ref = _reference(
        kind=CapabilityKind.MCP_CONNECTION,
        key=spec.key,
        revision=connection.revision,
        digest=connection.digest,
    )
    connection_item = CapabilityCatalogItem(
        catalogId=f"mcp-connection:{spec.key}:{connection.revision}",
        kind=CapabilityKind.MCP_CONNECTION,
        key=spec.key,
        humanLabel=spec.key,
        revision=connection.revision,
        digest=connection.digest,
        schemas={
            "tools": {
                tool.name: {
                    "inputSchema": tool.input_schema,
                    "outputSchema": tool.output_schema,
                }
                for tool in sorted(spec.tools, key=lambda item: item.name)
            }
        },
        permissions=CapabilityPermissions(toolAllowlist=tuple(sorted(spec.tool_allowlist))),
        attachment=CapabilityAttachment(
            target=CapabilityAttachmentTarget.NONE,
            reference=connection_ref,
            constraints=(
                "connections are configured supporting resources; attach an exact pinned tool",
            ),
        ),
    )
    tools = tuple(
        CapabilityCatalogItem(
            catalogId=(
                f"mcp-tool:{spec.key}:{connection.revision}:{tool.name}:{tool.schema_digest}"
            ),
            kind=CapabilityKind.MCP_TOOL,
            key=tool.name,
            humanLabel=tool.name,
            revision=connection.revision,
            digest=connection.digest,
            description=tool.description,
            schemas={"inputSchema": tool.input_schema, "outputSchema": tool.output_schema},
            impact=CapabilityImpact(tool.impact.value),
            permissions=CapabilityPermissions(toolAllowlist=(tool.name,)),
            providerCompatibility=("mcp",),
            attachment=CapabilityAttachment(
                target=CapabilityAttachmentTarget.AGENT_DEFINITION,
                reference=_reference(
                    kind=CapabilityKind.MCP_TOOL,
                    key=tool.name,
                    revision=connection.revision,
                    digest=connection.digest,
                    providerKind=ToolProviderKind.MCP,
                    providerKey=spec.key,
                    providerRevision=connection.revision,
                    providerDigest=connection.digest,
                    connectionKey=spec.key,
                    connectionRevision=connection.revision,
                    connectionDigest=connection.digest,
                    toolName=tool.name,
                    schemaDigest=tool.schema_digest,
                ),
                constraints=("tool schema digest must remain pinned at attachment time",),
            ),
        )
        for tool in sorted(spec.tools, key=lambda item: item.name)
    )
    return (connection_item, *tools)


def _plugin_status(package: PluginRegistryPackage) -> tuple[CapabilityStatus, tuple[str, ...]]:
    if package.yanked:
        return CapabilityStatus.YANKED, (package.yank_reason or "plugin package was yanked",)
    return CapabilityStatus.AVAILABLE, ()


def project_plugin_package(package: PluginRegistryPackage) -> CapabilityCatalogItem:
    """Project a registry package without exposing its bundle or registry payload."""

    status, diagnostics = _plugin_status(package)
    manifest = package.manifest
    name = package.name or f"bundle-{package.content_digest.removeprefix('sha256:')[:16]}"
    revision = package.version or package.content_digest
    label = f"{name}@{package.version}" if package.version else name
    description = manifest.description if manifest and manifest.description else ""
    schemas: dict[str, Any] = {}
    compatibility: tuple[str, ...] = ()
    permissions = CapabilityPermissions()
    impact = CapabilityImpact.NONE
    if manifest is not None:
        schemas = {
            "entryPoints": {
                entry.name: {
                    "type": entry.type.value,
                    "configurationSchema": entry.configuration_schema,
                    "outputSchema": entry.output_schema,
                }
                for entry in sorted(manifest.entry_points, key=lambda item: item.name)
            }
        }
        compatibility = (
            f"platform:{manifest.compatibility.platform_version}",
            *(f"protocol:{version}" for version in manifest.compatibility.protocol_versions),
        )
        permissions = CapabilityPermissions(
            delegatedCapabilities=manifest.capabilities.required,
            secretScopes=manifest.capabilities.secret_scopes,
            allowedEgress=manifest.capabilities.allowed_egress,
        )
        if manifest.capabilities.filesystem_access.value == "workspace-read":
            permissions = permissions.model_copy(update={"filesystem_read_roots": ("workspace",)})
        elif manifest.capabilities.filesystem_access.value == "workspace-write":
            permissions = permissions.model_copy(
                update={
                    "filesystem_read_roots": ("workspace",),
                    "filesystem_write_roots": ("workspace",),
                }
            )
        if any(entry.type is ExtensionType.TASK for entry in manifest.entry_points):
            impact = CapabilityImpact.HIGH_IMPACT
    return CapabilityCatalogItem(
        catalogId=f"plugin:{name}:{revision}:{package.content_digest}",
        kind=CapabilityKind.PLUGIN,
        key=name,
        humanLabel=label,
        revision=revision,
        digest=package.content_digest,
        status=status,
        description=description,
        schemas=schemas,
        impact=impact,
        permissions=permissions,
        providerCompatibility=compatibility,
        attachment=CapabilityAttachment(
            target=CapabilityAttachmentTarget.NONE,
            reference=_reference(
                kind=CapabilityKind.PLUGIN,
                key=name,
                revision=revision,
                digest=package.content_digest,
            ),
            constraints=(
                "plugin packages are managed capabilities; attach a resolved plugin resource",
            ),
        ),
        diagnostics=diagnostics,
    )


def build_capability_catalog(
    agent_resources: Iterable[AgentResourceRevision] = (),
    mcp_connections: Iterable[McpConnectionRevision] = (),
    plugin_packages: Iterable[PluginRegistryPackage] = (),
    *,
    namespace: str | None = None,
    generated_at: datetime | None = None,
    source_access: Iterable[CapabilitySourceAccess] = (),
    limit: int | None = None,
) -> CapabilityCatalog:
    """Build a stable catalog from immutable source records."""

    items = [*(project_agent_resource(item) for item in agent_resources)]
    for connection in mcp_connections:
        items.extend(project_mcp_connection(connection))
    items.extend(project_plugin_package(item) for item in plugin_packages)
    ordered = tuple(sorted(items, key=lambda item: (item.kind.value, item.catalog_id)))
    total = len(ordered)
    if limit is not None and limit < 1:
        raise ValueError("capability catalog limit must be positive")
    returned_items = ordered if limit is None else ordered[:limit]
    digest = _catalog_digest(returned_items)
    access = tuple(source_access)
    if not access:
        access = tuple(
            CapabilitySourceAccess(source=source, status=CapabilitySourceAccessStatus.ALLOWED)
            for source in CapabilitySource
        )
    return CapabilityCatalog(
        namespace=namespace,
        generatedAt=generated_at or datetime.now(UTC),
        catalogDigest=digest,
        sourceAccess=access,
        total=total,
        returned=len(returned_items),
        truncated=len(returned_items) < total,
        items=returned_items,
    )


project_capability_catalog = build_capability_catalog


def _catalog_digest(items: Iterable[CapabilityCatalogItem]) -> str:
    return "sha256:" + canonical_hash(
        [item.model_dump(mode="json", by_alias=True, exclude_none=True) for item in items]
    )


def filter_capability_catalog(
    catalog: CapabilityCatalog,
    *,
    query: str | None = None,
    kinds: Iterable[CapabilityKind] = (),
    statuses: Iterable[CapabilityStatus] = (),
    limit: int | None = None,
) -> CapabilityCatalog:
    """Return a deterministic bounded view while preserving catalog provenance."""

    if limit is not None and limit < 1:
        raise ValueError("capability catalog limit must be positive")
    selected_kinds = {CapabilityKind(kind) for kind in kinds}
    selected_statuses = {CapabilityStatus(status) for status in statuses}
    normalized_query = query.casefold() if query is not None else None

    def matches(item: CapabilityCatalogItem) -> bool:
        if selected_kinds and item.kind not in selected_kinds:
            return False
        if selected_statuses and item.status not in selected_statuses:
            return False
        if normalized_query is None:
            return True
        searchable = " ".join(
            (item.catalog_id, item.key, item.human_label, item.description)
        ).casefold()
        return normalized_query in searchable

    filtered = tuple(item for item in catalog.items if matches(item))
    returned_items = filtered if limit is None else filtered[:limit]
    return catalog.model_copy(
        update={
            "catalog_digest": _catalog_digest(returned_items),
            "total": len(filtered),
            "returned": len(returned_items),
            "truncated": len(returned_items) < len(filtered),
            "items": returned_items,
        }
    )


__all__ = [
    "CapabilityAttachment",
    "CapabilityAttachmentTarget",
    "CapabilityCatalog",
    "CapabilityCatalogItem",
    "CapabilityImpact",
    "CapabilityKind",
    "CapabilityPermissions",
    "CapabilityReference",
    "CapabilitySource",
    "CapabilitySourceAccess",
    "CapabilitySourceAccessStatus",
    "CapabilityStatus",
    "build_capability_catalog",
    "filter_capability_catalog",
    "project_agent_resource",
    "project_capability_catalog",
    "project_mcp_connection",
    "project_plugin_package",
]
