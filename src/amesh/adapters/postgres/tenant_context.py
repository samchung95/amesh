from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.observability import current_trace_context
from amesh.ports.tenant_repository import TenantUnavailableError


async def resolve_active_tenant_id(
    connection: AsyncConnection,
    tenant_slug: str,
) -> UUID:
    tenant_id_value = await connection.scalar(
        text("SELECT amesh_resolve_active_tenant(:tenant_slug)"),
        {"tenant_slug": tenant_slug},
    )
    if tenant_id_value is None:
        raise TenantUnavailableError("tenant unavailable")
    return UUID(str(tenant_id_value))


@asynccontextmanager
async def tenant_admin_transaction(engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with engine.connect() as raw_connection:
        connection = await raw_connection.execution_options(isolation_level="READ COMMITTED")
        async with connection.begin():
            admin_role_can_inventory = bool(
                await connection.scalar(
                    text(
                        "SELECT has_table_privilege("
                        "'amesh_tenant_admin', 'amesh_schema_migrations', 'SELECT'"
                        ")"
                    )
                )
            )
            if not admin_role_can_inventory:
                raise RuntimeError(
                    "amesh_tenant_admin is missing grants from 0075_restricted_repository_roles.sql"
                )
            await connection.execute(text("SET LOCAL ROLE amesh_tenant_admin"))
            yield connection


@asynccontextmanager
async def tenant_transaction(
    engine: AsyncEngine,
    tenant_slug: str,
) -> AsyncIterator[tuple[AsyncConnection, UUID]]:
    async with engine.connect() as raw_connection:
        connection = await raw_connection.execution_options(isolation_level="READ COMMITTED")
        async with connection.begin():
            await connection.execute(text("SET LOCAL ROLE amesh_runtime"))
            tenant_id = await resolve_active_tenant_id(connection, tenant_slug)
            await connection.execute(
                text("SELECT set_config('amesh.tenant_id', :tenant_id, true)"),
                {"tenant_id": str(tenant_id)},
            )
            await connection.execute(
                text("SELECT set_config('amesh.trace_context', :trace_context, true)"),
                {"trace_context": json.dumps(current_trace_context())},
            )
            yield connection, tenant_id
