"""Application service for previewing, applying and recovering a release gate."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Protocol
from uuid import UUID

from amesh.domain.promotion import (
    EvidenceArtifact,
    PromotionError,
    PromotionEvidenceError,
    PromotionGate,
    PromotionPolicy,
    PromotionTargetKind,
    ReleaseAction,
    ReleaseHistoryEntry,
    ReleaseTarget,
    evaluate_promotion_gate,
)
from amesh.ports.promotion_repository import PromotionRepository


class PromotionPolicyStore(Protocol):
    async def put_policy(self, policy: PromotionPolicy) -> PromotionPolicy: ...


class PromotionActionResult:
    """Stable service result that pairs the new target with its immutable event."""

    def __init__(self, target: ReleaseTarget, event: ReleaseHistoryEntry) -> None:
        self.target = target
        self.event = event


class PromotionService:
    def __init__(self, repository: PromotionRepository) -> None:
        self._repository = repository

    async def create_policy(self, policy: PromotionPolicy) -> PromotionPolicy:
        return await self._repository.put_policy(policy)

    async def record_evidence(self, artifact: EvidenceArtifact) -> EvidenceArtifact:
        return await self._repository.put_evidence(artifact)

    async def get_policy(self, tenant_id: str, policy_id: UUID) -> PromotionPolicy:
        return await self._repository.get_policy(tenant_id, policy_id)

    async def preview(
        self,
        policy: PromotionPolicy,
        *,
        now: datetime | None = None,
        approvals: Mapping[str, int] | None = None,
    ) -> PromotionGate:
        evidence = tuple(
            await self._repository.list_evidence(
                policy.tenant_id,
                configuration_digest=policy.configuration_digest,
            )
        )
        return evaluate_promotion_gate(policy, evidence, now=now, approvals=approvals)

    async def apply(
        self,
        policy: PromotionPolicy,
        *,
        expected_version: int,
        actor_id: str,
        reason: str,
        now: datetime | None = None,
        approvals: Mapping[str, int] | None = None,
    ) -> PromotionActionResult:
        gate = await self.preview(policy, now=now, approvals=approvals)
        if not gate.passed:
            raise PromotionEvidenceError(", ".join(gate.failures))
        target = await self._repository.get_target(
            policy.tenant_id, policy.target_kind.value, policy.target_key
        )
        updated, event = await self._repository.apply_target(
            target,
            action=ReleaseAction.PROMOTE.value,
            to_revision=policy.target_revision,
            to_configuration_digest=policy.configuration_digest,
            gate_digest=gate.digest,
            expected_version=expected_version,
            actor_id=actor_id,
            reason=reason,
        )
        return PromotionActionResult(updated, event)

    async def rollback(
        self,
        tenant_id: str,
        target_kind: PromotionTargetKind,
        target_key: str,
        *,
        to_revision: int,
        expected_version: int,
        actor_id: str,
        reason: str,
    ) -> PromotionActionResult:
        target = await self._repository.get_target(tenant_id, target_kind.value, target_key)
        history = await self._repository.history(tenant_id, target_kind.value, target_key)
        prior = next(
            (
                item
                for item in reversed(history)
                if item.to_revision == to_revision and item.to_configuration_digest is not None
            ),
            None,
        )
        if prior is None:
            raise PromotionError("rollback target is not an exact prior release revision")
        if target.active_revision == to_revision:
            raise PromotionError("rollback target is already active")
        updated, event = await self._repository.apply_target(
            target,
            action=ReleaseAction.ROLLBACK.value,
            to_revision=to_revision,
            to_configuration_digest=prior.to_configuration_digest,
            gate_digest=prior.gate_digest,
            expected_version=expected_version,
            actor_id=actor_id,
            reason=reason,
        )
        return PromotionActionResult(updated, event)

    async def kill_switch(
        self,
        tenant_id: str,
        target_kind: PromotionTargetKind,
        target_key: str,
        *,
        expected_version: int,
        actor_id: str,
        reason: str,
    ) -> PromotionActionResult:
        target = await self._repository.get_target(tenant_id, target_kind.value, target_key)
        updated, event = await self._repository.apply_target(
            target,
            action=ReleaseAction.KILL_SWITCH.value,
            to_revision=target.active_revision,
            to_configuration_digest=target.active_configuration_digest,
            gate_digest=None,
            expected_version=expected_version,
            actor_id=actor_id,
            reason=reason,
        )
        return PromotionActionResult(updated, event)

    async def get_target(
        self, tenant_id: str, target_kind: PromotionTargetKind, target_key: str
    ) -> ReleaseTarget:
        return await self._repository.get_target(tenant_id, target_kind.value, target_key)

    async def get_history(
        self, tenant_id: str, target_kind: PromotionTargetKind, target_key: str
    ) -> tuple[ReleaseHistoryEntry, ...]:
        return tuple(await self._repository.history(tenant_id, target_kind.value, target_key))


__all__ = ["PromotionActionResult", "PromotionService"]
