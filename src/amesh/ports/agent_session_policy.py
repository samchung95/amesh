from __future__ import annotations

from typing import Protocol
from uuid import UUID

from amesh.domain.agent_session_policy import (
    AgentSessionPolicy,
    AgentSessionPolicyRevision,
)


class AgentSessionPolicyVersionConflict(RuntimeError):
    """Raised when a policy update carries a stale expected revision."""


class AgentSessionPolicyRepository(Protocol):
    async def save_revision(
        self,
        tenant_id: str,
        policy: AgentSessionPolicy,
        *,
        actor_id: str,
        namespace: str | None = None,
        application_id: str | None = None,
        expected_revision: int | None = None,
    ) -> AgentSessionPolicyRevision: ...

    async def get_revision(
        self,
        tenant_id: str,
        *,
        namespace: str | None = None,
        application_id: str | None = None,
        revision: int | None = None,
        policy_id: UUID | None = None,
    ) -> AgentSessionPolicyRevision: ...

    async def effective_revisions(
        self,
        tenant_id: str,
        *,
        namespace: str,
        application_id: str | None = None,
    ) -> tuple[AgentSessionPolicyRevision, ...]: ...

    async def list_revisions(
        self,
        tenant_id: str,
        *,
        namespace: str | None = None,
        application_id: str | None = None,
        limit: int = 100,
    ) -> tuple[AgentSessionPolicyRevision, ...]: ...


__all__ = [
    "AgentSessionPolicyRepository",
    "AgentSessionPolicyVersionConflict",
]
