from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from amesh.capability_catalog import (
    CapabilityAttachmentTarget,
    CapabilityKind,
    CapabilityStatus,
    build_capability_catalog,
    filter_capability_catalog,
    project_agent_resource,
    project_mcp_connection,
    project_plugin_package,
)
from amesh.domain.agent_primitives import (
    McpConnectionRevision,
    McpConnectionSpec,
    McpToolImpact,
    McpToolPin,
)
from amesh.domain.agent_resources import (
    AgentDefinitionSpec,
    AgentHardLimits,
    AgentMemoryPolicy,
    AgentPermissions,
    AgentResourceRef,
    AgentResourceRevision,
    PromptSpec,
    agent_resource_digest,
)
from amesh.plugin_sdk.manifest import (
    ExtensionType,
    PluginCapabilities,
    PluginCompatibility,
    PluginDocumentation,
    PluginEntryPoint,
    PluginManifest,
    PluginNetworkAccess,
    PluginTransport,
)
from amesh.plugin_sdk.registry import PluginRegistryPackage


def _resource(spec: PromptSpec | AgentDefinitionSpec) -> AgentResourceRevision:
    return AgentResourceRevision(
        tenantId="tenant-1",
        namespace=spec.namespace,
        kind=spec.kind,
        key=spec.key,
        revision=2,
        digest=agent_resource_digest(spec),
        spec=spec,
        createdBy="tester",
        createdAt=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _connection() -> McpConnectionRevision:
    tool = McpToolPin(
        name="search",
        description="Search records",
        inputSchema={"type": "object", "additionalProperties": False},
        outputSchema={"type": "array"},
        impact=McpToolImpact.READ_ONLY,
    )
    spec = McpConnectionSpec(
        key="catalog",
        namespace="agents.demo",
        endpoint="https://mcp.example.test/mcp",
        credentialRef="mcp-token",
        toolAllowlist=("search",),
        tools=(tool,),
    )
    return McpConnectionRevision(
        connectionId=UUID("00000000-0000-0000-0000-000000000002"),
        tenantId="tenant-1",
        revision=3,
        digest=spec.digest,
        spec=spec,
        createdBy="tester",
        createdAt=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _plugin() -> PluginRegistryPackage:
    manifest = PluginManifest(
        name="vendor.tools",
        version="1.2.3",
        vendor="Vendor",
        license="Apache-2.0",
        description="Safe catalog fixture",
        compatibility=PluginCompatibility(platformVersion=">=0.2.0"),
        capabilities=PluginCapabilities(
            required=("network",),
            networkAccess=PluginNetworkAccess.RESTRICTED,
            allowedEgress=("api.example.test",),
            secretScopes=("plugin-token",),
        ),
        entryPoints=(
            PluginEntryPoint(
                name="search",
                type=ExtensionType.TASK,
                transport=PluginTransport.STDIO,
                target="bin/search",
                configurationSchema={"type": "object"},
                documentation=PluginDocumentation(
                    title="Search",
                    description="Search task",
                    category="tools",
                ),
            ),
        ),
    )
    return PluginRegistryPackage(
        name=manifest.name,
        version=manifest.version,
        bundle="private-bundle-bytes",
        contentDigest="sha256:" + "a" * 64,
        manifest=manifest,
    )


def test_agent_resource_projection_is_exact_and_does_not_expose_body() -> None:
    prompt = _resource(
        PromptSpec(
            key="house-style",
            namespace="agents.demo",
            title="House style",
            content="PRIVATE PROMPT BODY",
            variables={"audience": "operator"},
        )
    )

    item = project_agent_resource(prompt)

    assert item.kind is CapabilityKind.PROMPT
    assert item.catalog_id == "prompt:house-style:2"
    assert item.revision == 2
    assert item.attachment.target is CapabilityAttachmentTarget.AGENT_DEFINITION
    assert item.schemas["variables"]["properties"]["audience"]["description"] == "operator"
    assert "PRIVATE PROMPT BODY" not in item.model_dump_json()


def test_mcp_projection_pins_tool_to_connection_and_schema() -> None:
    connection = _connection()

    items = project_mcp_connection(connection)
    tool = next(item for item in items if item.kind is CapabilityKind.MCP_TOOL)
    reference = tool.attachment.reference

    assert [item.kind for item in items] == [CapabilityKind.MCP_CONNECTION, CapabilityKind.MCP_TOOL]
    assert tool.impact.value == "READ_ONLY"
    assert reference is not None
    assert reference.connection_key == "catalog"
    assert reference.connection_revision == 3
    assert reference.schema_digest == connection.spec.tools[0].schema_digest
    assert "mcp-token" not in tool.model_dump_json()


def test_plugin_projection_is_safe_and_non_attachable() -> None:
    item = project_plugin_package(_plugin())

    assert item.kind is CapabilityKind.PLUGIN
    assert item.revision == "1.2.3"
    assert item.status is CapabilityStatus.AVAILABLE
    assert item.attachment.target is CapabilityAttachmentTarget.NONE
    assert "private-bundle-bytes" not in item.model_dump_json()
    assert "bin/search" not in item.model_dump_json()
    assert item.permissions.secret_scopes == ("plugin-token",)


def test_catalog_is_deterministic_independent_of_source_order() -> None:
    prompt = _resource(
        PromptSpec(
            key="house-style",
            namespace="agents.demo",
            title="House style",
            content="Private",
        )
    )
    agent = _resource(
        AgentDefinitionSpec(
            key="researcher",
            namespace="agents.demo",
            title="Researcher",
            instructions="Private instructions",
            inputSchema={"type": "object"},
            outputSchema={"type": "object"},
            modelPolicy=AgentResourceRef(key="policy", revision=1),
            memoryPolicy=AgentMemoryPolicy(),
            permissions=AgentPermissions(),
            hardLimits=AgentHardLimits(
                maxTotalTokens=100,
                maxCostUsd=Decimal("1"),
                maxDurationSeconds=30,
                maxToolCalls=0,
                maxTurns=1,
                maxLoopIterations=0,
                maxRecursionDepth=0,
                maxConcurrency=1,
            ),
            evaluationPolicy={},
        )
    )
    first = build_capability_catalog([prompt, agent], [_connection()], [_plugin()])
    second = build_capability_catalog(
        [agent, prompt],
        [_connection()],
        [_plugin()],
        namespace="agents.demo",
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        limit=20,
    )

    assert first.catalog_digest == second.catalog_digest
    assert first.namespace is None
    assert second.namespace == "agents.demo"
    assert second.returned == second.total
    assert not second.truncated
    agent_item = next(item for item in second.items if item.kind is CapabilityKind.AGENT)
    assert agent_item.attachment.target is CapabilityAttachmentTarget.WORKFLOW
    assert [item.catalog_id for item in first.items] == sorted(
        item.catalog_id for item in first.items
    )


def test_catalog_filter_is_case_insensitive_and_bounded() -> None:
    catalog = build_capability_catalog(
        [
            _resource(
                PromptSpec(
                    key="house-style",
                    namespace="agents.demo",
                    title="House Style",
                    content="Private",
                )
            )
        ],
        [_connection()],
        [_plugin()],
        namespace="agents.demo",
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    filtered = filter_capability_catalog(
        catalog,
        query="SEARCH",
        kinds=("mcp-tool",),
        statuses=(CapabilityStatus.AVAILABLE,),
        limit=1,
    )

    assert filtered.namespace == catalog.namespace
    assert filtered.source_access == catalog.source_access
    assert filtered.total == 1
    assert filtered.returned == 1
    assert not filtered.truncated
    assert filtered.items[0].kind is CapabilityKind.MCP_TOOL
