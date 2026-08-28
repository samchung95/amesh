from __future__ import annotations

from typing import Protocol
from uuid import UUID

from amesh.domain.agent_memory import (
    AgentMemoryContext,
    AgentMemoryEntry,
    AgentMemoryMetadata,
    AgentMemoryWrite,
)


class AgentMemoryRepository(Protocol):
    async def read(
        self,
        tenant_id: str,
        context: AgentMemoryContext,
        keys: tuple[str, ...],
    ) -> tuple[AgentMemoryEntry, ...]: ...

    async def write(
        self,
        tenant_id: str,
        context: AgentMemoryContext,
        write: AgentMemoryWrite,
    ) -> AgentMemoryEntry: ...

    async def list_metadata(
        self,
        tenant_id: str,
        namespace: str,
        *,
        agent_key: str | None = None,
        limit: int = 100,
    ) -> tuple[AgentMemoryMetadata, ...]: ...

    async def delete(
        self,
        tenant_id: str,
        namespace: str,
        entry_id: UUID,
        *,
        actor_id: str,
    ) -> AgentMemoryMetadata: ...
