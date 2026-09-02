from __future__ import annotations

from typing import Protocol
from uuid import UUID

from amesh.domain.plugin_policy import (
    EffectivePluginPolicy,
    PluginPolicyDecision,
    PluginPolicyImpactPreview,
    PluginPolicyRule,
    PluginPolicyRuleCreate,
    PluginQuarantine,
    PluginQuarantineCreate,
)


class PluginPolicyRepository(Protocol):
    async def effective_policy(
        self,
        tenant_id: str,
        *,
        namespace: str | None,
        default_allow: bool,
    ) -> EffectivePluginPolicy: ...

    async def create_rule(
        self, tenant_id: str, request: PluginPolicyRuleCreate, *, actor_id: str
    ) -> PluginPolicyRule: ...

    async def update_rule(
        self,
        tenant_id: str,
        rule_id: UUID,
        request: PluginPolicyRuleCreate,
        *,
        actor_id: str,
    ) -> PluginPolicyRule: ...

    async def get_rule(self, tenant_id: str, rule_id: UUID) -> PluginPolicyRule: ...

    async def delete_rule(self, tenant_id: str, rule_id: UUID, *, actor_id: str) -> None: ...

    async def create_quarantine(
        self, tenant_id: str, request: PluginQuarantineCreate, *, actor_id: str
    ) -> PluginQuarantine: ...

    async def release_quarantine(
        self, tenant_id: str, quarantine_id: UUID, *, actor_id: str, reason: str
    ) -> PluginQuarantine: ...

    async def record_decision(
        self, decision: PluginPolicyDecision, *, actor_id: str
    ) -> PluginPolicyDecision: ...

    async def list_decisions(
        self, tenant_id: str, *, limit: int = 100
    ) -> tuple[PluginPolicyDecision, ...]: ...

    async def frozen_resolution(
        self, tenant_id: str, namespace: str, flow_id: str, revision: int
    ) -> dict[str, object] | None: ...

    async def migrate_legacy_resolution(
        self,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        expected: dict[str, object],
        replacement: dict[str, object],
        actor_id: str,
    ) -> dict[str, object]: ...

    async def quarantine_legacy_resolution(
        self,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        expected: dict[str, object],
        actor_id: str,
        reason: str,
    ) -> bool: ...

    async def impact_preview(
        self, tenant_id: str, request: PluginQuarantineCreate
    ) -> PluginPolicyImpactPreview: ...


__all__ = ["PluginPolicyRepository"]
