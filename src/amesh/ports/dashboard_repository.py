from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from amesh.domain.dashboards import (
    DashboardDefinition,
    DashboardQuery,
    DashboardQueryResult,
    DashboardSpec,
)

from .errors import VersionConflict


class DashboardVersionConflict(VersionConflict):
    """Raised when a dashboard update uses a stale expected version."""


class DashboardQueryTimeout(RuntimeError):
    """Raised when a bounded dashboard query exceeds its statement timeout."""


class DashboardRepository(Protocol):
    async def list_definitions(self, *, tenant_id: str) -> Sequence[DashboardDefinition]: ...

    async def get_definition(
        self,
        dashboard_id: str,
        *,
        tenant_id: str,
    ) -> DashboardDefinition: ...

    async def upsert_definition(
        self,
        dashboard_id: str,
        spec: DashboardSpec,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None,
    ) -> DashboardDefinition: ...

    async def delete_definition(
        self,
        dashboard_id: str,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int,
    ) -> None: ...

    async def execute_query(
        self,
        query: DashboardQuery,
        *,
        tenant_id: str,
    ) -> DashboardQueryResult: ...
