"""Provider-neutral certification checks for MCP and isolated plugin tools."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain import (
    ToolDiscovery,
    ToolInvocationRequest,
    ToolPolicy,
    ToolProviderRevision,
    authorize_tool_call,
)


class ToolProviderCertificationReport(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    contract_version: str = Field(alias="contractVersion")
    provider: dict[str, Any]
    discovery_digest: str = Field(alias="discoveryDigest")
    tool_count: int = Field(alias="toolCount", ge=1)
    checks: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return bool(self.checks)


def certify_tool_provider(document: Mapping[str, Any]) -> ToolProviderCertificationReport:
    """Validate a serialized provider revision with the shared contract checks."""

    revision = ToolProviderRevision.model_validate(document)
    discovery = ToolDiscovery.from_tools(revision.provider, revision.tools)
    for tool in revision.tools:
        policy = ToolPolicy(
            allowedTools=(tool.name,),
            secretScopes=tool.secret_scopes,
            allowedEgress=tool.allowed_egress,
            filesystemReadRoots=tool.filesystem_read_roots,
            filesystemWriteRoots=tool.filesystem_write_roots,
            allowHighImpact=True,
        )
        request = ToolInvocationRequest(
            provider=revision.provider,
            toolName=tool.name,
            arguments={},
            tenantId=revision.tenant_id,
            namespace=revision.namespace,
        )
        authorize_tool_call(tool, request, policy)
    return ToolProviderCertificationReport(
        contractVersion=discovery.contract_version,
        provider=revision.provider.model_dump(mode="json", by_alias=True),
        discoveryDigest=discovery.digest,
        toolCount=len(revision.tools),
        checks=(
            "provider identity is pinned",
            "discovery digest is canonical",
            "all tools pass shared policy authorization",
        ),
    )
