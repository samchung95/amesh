from __future__ import annotations

from typing import Protocol

from amesh.domain.agent_session_fleet import (
    AgentSessionFleetPage,
    AgentSessionFleetQuery,
    AgentSessionInstanceAggregate,
)


class AgentSessionFleetCursorError(ValueError):
    """Raised when a fleet cursor is malformed or does not match its query."""


class AgentSessionFleetRepository(Protocol):
    async def list_fleet(
        self,
        tenant_id: str,
        query: AgentSessionFleetQuery,
    ) -> AgentSessionFleetPage: ...

    async def instance_aggregate(self) -> AgentSessionInstanceAggregate: ...
