from __future__ import annotations

from typing import Protocol

from amesh.domain.administration import AdministrationAuditEntry
from amesh.domain.feature_flags import FeatureFlag, FeatureFlagDecision

from .errors import VersionConflict


class FeatureFlagVersionConflict(VersionConflict):
    """Raised when an update carries a stale expected version."""


class FeatureFlagRepository(Protocol):
    async def upsert(
        self,
        flag: FeatureFlag,
        *,
        actor_id: str,
        expected_version: int | None = None,
        administration_audit: dict[str, object] | None = None,
    ) -> FeatureFlag: ...

    async def list_for_context(
        self,
        tenant_id: str,
        *,
        namespace: str | None = None,
    ) -> tuple[FeatureFlag, ...]: ...

    async def evaluate(
        self,
        key: str,
        tenant_id: str,
        *,
        namespace: str | None = None,
        default: bool = False,
    ) -> FeatureFlagDecision: ...

    async def audit_configuration_reload(
        self,
        *,
        actor_id: str,
        outcome: str,
        changed_fields: tuple[str, ...],
        reason: str,
    ) -> None: ...

    async def audit_administration_action(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        action: str,
        resource_id: str,
        outcome: str,
        reason: str,
        evidence: dict[str, object],
    ) -> None: ...

    async def list_administration_audit(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> tuple[AdministrationAuditEntry, ...]: ...
