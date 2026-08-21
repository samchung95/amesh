from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.ports.tenant_repository import TenantUnavailableError


@asynccontextmanager
async def tenant_admin_transaction(engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with engine.connect() as connection, connection.begin():
        await connection.execute(text("SET LOCAL ROLE amesh_tenant_admin"))
        yield connection


@asynccontextmanager
async def tenant_transaction(
    engine: AsyncEngine,
    tenant_slug: str,
) -> AsyncIterator[tuple[AsyncConnection, UUID]]:
    async with engine.connect() as connection, connection.begin():
        await connection.execute(text("SET LOCAL ROLE amesh_runtime"))
        tenant_id_value = await connection.scalar(
            text("SELECT amesh_resolve_active_tenant(:tenant_slug)"),
            {"tenant_slug": tenant_slug},
        )
        if tenant_id_value is None:
            raise TenantUnavailableError("tenant unavailable")
        tenant_id = UUID(str(tenant_id_value))
        await connection.execute(
            text("SELECT set_config('amesh.tenant_id', :tenant_id, true)"),
            {"tenant_id": str(tenant_id)},
        )
        yield connection, tenant_id
