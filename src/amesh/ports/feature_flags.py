from __future__ import annotations

from typing import Protocol

from amesh.domain.feature_flags import FeatureFlag, FeatureFlagDecision


class FeatureFlagVersionConflict(RuntimeError):
    """Raised when an update carries a stale expected version."""


class FeatureFlagRepository(Protocol):
    async def upsert(
        self,
        flag: FeatureFlag,
        *,
        actor_id: str,
        expected_version: int | None = None,
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
