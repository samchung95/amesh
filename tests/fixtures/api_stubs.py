from __future__ import annotations


class TenantQuotaStub:
    async def consume_api_request(self, tenant_slug: str) -> int:
        del tenant_slug
        return 1


class NonEmptyTenantQuotaStub:
    async def consume_api_request(self, tenant_slug: str) -> int:
        assert tenant_slug
        return 1


class DefaultTenantQuotaStub:
    async def consume_api_request(self, tenant_slug: str) -> int:
        assert tenant_slug == "default"
        return 1
