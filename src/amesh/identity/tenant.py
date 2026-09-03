from __future__ import annotations

from amesh.domain.tenancy import TenantDefinition, TenantExport, TenantPolicy, TenantStatus
from amesh.ports.tenant_repository import TenantRepository


class TenantService:
    def __init__(self, repository: TenantRepository) -> None:
        self._repository = repository

    async def create(
        self,
        *,
        slug: str,
        display_name: str,
        policy: TenantPolicy,
        actor_id: str,
    ) -> TenantDefinition:
        return await self._repository.create(
            TenantDefinition(slug=slug, display_name=display_name, policy=policy),
            actor_id=actor_id,
        )

    async def get(self, tenant_slug: str) -> TenantDefinition:
        return await self._repository.get(tenant_slug)

    async def require_active(self, tenant_slug: str) -> TenantDefinition:
        return await self._repository.require_active(tenant_slug)

    async def list(self) -> list[TenantDefinition]:
        return await self._repository.list()

    async def suspend(self, tenant_slug: str, *, actor_id: str) -> TenantDefinition:
        return await self._repository.set_status(
            tenant_slug,
            TenantStatus.SUSPENDED,
            actor_id=actor_id,
        )

    async def delete(self, tenant_slug: str, *, actor_id: str) -> TenantDefinition:
        await self._repository.export(tenant_slug, actor_id=actor_id)
        return await self._repository.set_status(
            tenant_slug,
            TenantStatus.TOMBSTONED,
            actor_id=actor_id,
        )

    async def restore(self, tenant_slug: str, *, actor_id: str) -> TenantDefinition:
        return await self._repository.set_status(
            tenant_slug,
            TenantStatus.ACTIVE,
            actor_id=actor_id,
        )

    async def update_policy(
        self,
        tenant_slug: str,
        policy: TenantPolicy,
        *,
        actor_id: str,
    ) -> TenantDefinition:
        return await self._repository.set_policy(tenant_slug, policy, actor_id=actor_id)

    async def export(self, tenant_slug: str, *, actor_id: str) -> TenantExport:
        return await self._repository.export(tenant_slug, actor_id=actor_id)

    async def consume_api_request(self, tenant_slug: str) -> int:
        return await self._repository.consume_api_request(tenant_slug)

    async def reserve_storage_bytes(self, tenant_slug: str, amount: int) -> int:
        return await self._repository.reserve_storage_bytes(tenant_slug, amount)

    async def release_storage_bytes(self, tenant_slug: str, amount: int) -> int:
        return await self._repository.release_storage_bytes(tenant_slug, amount)
