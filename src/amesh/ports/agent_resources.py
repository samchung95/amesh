from __future__ import annotations

from typing import Protocol

from amesh.domain.agent_resources import (
    AgentCapabilityPin,
    AgentResolutionRequest,
    AgentResourceKind,
    AgentResourceRevision,
    AgentResourceSpec,
)


class AgentResourceRepository(Protocol):
    async def save_resource(
        self,
        tenant_id: str,
        spec: AgentResourceSpec,
        *,
        actor_id: str,
    ) -> AgentResourceRevision: ...

    async def get_resource(
        self,
        tenant_id: str,
        namespace: str,
        kind: AgentResourceKind,
        key: str,
        *,
        revision: int | None = None,
    ) -> AgentResourceRevision: ...

    async def list_resources(
        self,
        tenant_id: str,
        namespace: str,
        *,
        kind: AgentResourceKind | None = None,
    ) -> tuple[AgentResourceRevision, ...]: ...

    async def resolve_agent(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        request: AgentResolutionRequest,
        *,
        actor_id: str,
    ) -> AgentCapabilityPin: ...
