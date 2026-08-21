from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from amesh.domain.tenancy import TenantDefinition, TenantExport, TenantPolicy, TenantStatus


class TenantUnavailableError(LookupError):
    """Raised when a tenant is absent or unavailable for runtime work."""


class TenantQuotaExceeded(RuntimeError):
    """Raised when a tenant policy budget rejects new work."""


class TenantRepository(Protocol):
    async def create(self, tenant: TenantDefinition, *, actor_id: str) -> TenantDefinition: ...

    async def get(self, tenant_slug: str) -> TenantDefinition: ...

    async def require_active(self, tenant_slug: str) -> TenantDefinition: ...

    async def list(self) -> list[TenantDefinition]: ...

    async def set_status(
        self,
        tenant_slug: str,
        status: TenantStatus,
        *,
        actor_id: str,
    ) -> TenantDefinition: ...

    async def set_policy(
        self,
        tenant_slug: str,
        policy: TenantPolicy,
        *,
        actor_id: str,
    ) -> TenantDefinition: ...

    async def export(self, tenant_slug: str, *, actor_id: str) -> TenantExport: ...

    async def list_active_for_worker_group(self, worker_group: str) -> Sequence[str]: ...

    async def consume_api_request(self, tenant_slug: str) -> int: ...

    async def reserve_storage_bytes(self, tenant_slug: str, amount: int) -> int: ...

    async def release_storage_bytes(self, tenant_slug: str, amount: int) -> int: ...
