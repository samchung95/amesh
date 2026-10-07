from __future__ import annotations

from datetime import datetime
from typing import Protocol

from amesh.config import IdentityGroupMapping
from amesh.domain.authentication import ProviderIdentity
from amesh.domain.federation import FederatedClaims, FederationState


class AmbiguousFederatedIdentity(PermissionError):
    """Raised when provider claims could link more than one account."""


class FederationStateRejected(PermissionError):
    """Raised when redirect state is missing, expired, consumed or mismatched."""


class FederationRepository(Protocol):
    async def record_event(
        self,
        provider_id: str,
        *,
        action: str,
        outcome: str,
        reason: str,
        evidence: dict[str, object] | None = None,
    ) -> None: ...

    async def create_state(self, token: str, state: FederationState) -> None: ...

    async def consume_state(
        self,
        token: str,
        *,
        provider_id: str,
        now: datetime,
    ) -> FederationState: ...

    async def resolve_identity(
        self,
        claims: FederatedClaims,
        *,
        group_mappings: tuple[IdentityGroupMapping, ...],
        default_tenant: str | None,
        default_role: str | None,
    ) -> ProviderIdentity: ...
