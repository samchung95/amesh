from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from amesh.config import IdentityGroupMapping
from amesh.domain.authentication import ProviderIdentity
from amesh.domain.federation import FederatedClaims, FederationState, ScimResourceRecord


class AmbiguousFederatedIdentity(PermissionError):
    """Raised when provider claims could link more than one account."""


class FederationStateRejected(PermissionError):
    """Raised when redirect state is missing, expired, consumed or mismatched."""


class FederationReplayRejected(PermissionError):
    """Raised when a signed identity assertion has already been accepted."""


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

    async def attach_request_id(self, token: str, request_id: str) -> None: ...

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

    async def record_assertion(
        self,
        provider_id: str,
        assertion_id: str,
        *,
        expires_at: datetime,
    ) -> None: ...

    async def list_scim(
        self,
        provider_id: str,
        resource_type: str,
        *,
        handle: str | None = None,
    ) -> tuple[ScimResourceRecord, ...]: ...

    async def get_scim(
        self,
        provider_id: str,
        resource_type: str,
        principal_id: UUID,
    ) -> ScimResourceRecord: ...

    async def create_scim(
        self,
        provider_id: str,
        resource_type: str,
        *,
        handle: str,
        resource_name: str,
        display_name: str,
        enabled: bool,
        external_id: str | None,
        tenant: str,
        role: str,
        member_ids: tuple[UUID, ...] = (),
    ) -> ScimResourceRecord: ...

    async def update_scim(
        self,
        provider_id: str,
        resource_type: str,
        principal_id: UUID,
        *,
        display_name: str | None = None,
        enabled: bool | None = None,
        member_ids: tuple[UUID, ...] | None = None,
    ) -> ScimResourceRecord: ...

    async def delete_scim(
        self,
        provider_id: str,
        resource_type: str,
        principal_id: UUID,
    ) -> None: ...
