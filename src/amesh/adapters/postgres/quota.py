from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from amesh.ports.tenant_repository import TenantQuotaExceeded


class TenantQuotaType(StrEnum):
    STORAGE_BYTES = "STORAGE_BYTES"
    LOG_BYTES = "LOG_BYTES"
    API_REQUESTS = "API_REQUESTS"


async def reserve_tenant_quota(
    connection: AsyncConnection,
    tenant_id: UUID,
    quota_type: TenantQuotaType,
    amount: int,
    limit: int,
    *,
    window_start: datetime | None = None,
) -> int:
    if amount < 0:
        raise ValueError("quota reservation amount cannot be negative")
    window = window_start or datetime(1970, 1, 1, tzinfo=UTC)
    value = await connection.scalar(
        text(
            """
            INSERT INTO tenant_quota_usage (
                tenant_id, quota_type, window_start, amount
            )
            SELECT :tenant_id, :quota_type, :window_start,
                   CAST(:amount AS bigint)
            WHERE CAST(:amount AS bigint) <= CAST(:limit AS bigint)
            ON CONFLICT (tenant_id, quota_type, window_start) DO UPDATE
            SET amount = tenant_quota_usage.amount + EXCLUDED.amount,
                updated_at = clock_timestamp()
            WHERE tenant_quota_usage.amount + EXCLUDED.amount <= CAST(:limit AS bigint)
            RETURNING amount
            """
        ),
        {
            "tenant_id": tenant_id,
            "quota_type": quota_type.value,
            "window_start": window,
            "amount": amount,
            "limit": limit,
        },
    )
    if value is None:
        raise TenantQuotaExceeded(f"tenant {quota_type.value.lower()} quota exceeded")
    return int(value)


async def release_tenant_quota(
    connection: AsyncConnection,
    tenant_id: UUID,
    quota_type: TenantQuotaType,
    amount: int,
) -> int:
    if amount < 0:
        raise ValueError("quota release amount cannot be negative")
    value = await connection.scalar(
        text(
            """
            UPDATE tenant_quota_usage
            SET amount = greatest(amount - :amount, 0), updated_at = clock_timestamp()
            WHERE tenant_id = :tenant_id
              AND quota_type = :quota_type
              AND window_start = '1970-01-01T00:00:00Z'::timestamptz
            RETURNING amount
            """
        ),
        {"tenant_id": tenant_id, "quota_type": quota_type.value, "amount": amount},
    )
    return int(value or 0)
