from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from amesh.domain.promotion import (
    EvidenceArtifact,
    PromotionPolicy,
    ReleaseHistoryEntry,
    ReleaseTarget,
)


class PromotionRepository(Protocol):
    async def put_policy(self, policy: PromotionPolicy) -> PromotionPolicy: ...

    async def get_policy(self, tenant_id: str, policy_id: UUID) -> PromotionPolicy: ...

    async def put_evidence(self, artifact: EvidenceArtifact) -> EvidenceArtifact: ...

    async def list_evidence(
        self, tenant_id: str, *, configuration_digest: str
    ) -> Sequence[EvidenceArtifact]: ...

    async def get_target(
        self, tenant_id: str, target_kind: str, target_key: str
    ) -> ReleaseTarget: ...

    async def apply_target(
        self,
        target: ReleaseTarget,
        *,
        action: str,
        to_revision: int | None,
        to_configuration_digest: str | None,
        gate_digest: str | None,
        expected_version: int,
        actor_id: str,
        reason: str,
    ) -> tuple[ReleaseTarget, ReleaseHistoryEntry]: ...

    async def history(
        self, tenant_id: str, target_kind: str, target_key: str
    ) -> Sequence[ReleaseHistoryEntry]: ...
