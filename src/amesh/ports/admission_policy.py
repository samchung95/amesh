from __future__ import annotations

from typing import Protocol
from uuid import UUID

from amesh.domain.policy import PolicyDecision, PolicyDocument, PolicyRevision


class AdmissionPolicyRepository(Protocol):
    async def effective_revisions(
        self, tenant_id: str, *, namespace: str
    ) -> tuple[PolicyRevision, ...]: ...

    async def save_revision(
        self, tenant_id: str, document: PolicyDocument, *, actor_id: str
    ) -> PolicyRevision: ...

    async def get_revision(
        self, tenant_id: str, policy_key: str, *, revision: int | None = None
    ) -> PolicyRevision: ...

    async def record_decision(
        self,
        decision: PolicyDecision,
        *,
        actor_id: str,
        execution_id: UUID | None = None,
        task_run_id: UUID | None = None,
    ) -> PolicyDecision: ...

    async def list_decisions(
        self, tenant_id: str, *, limit: int = 100
    ) -> tuple[PolicyDecision, ...]: ...


__all__ = ["AdmissionPolicyRepository"]
