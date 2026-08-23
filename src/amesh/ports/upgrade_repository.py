from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from amesh.domain import PersistedEventMigration, UpgradeDatabaseInventory


class UpgradeRepository(Protocol):
    async def inventory(self) -> UpgradeDatabaseInventory: ...

    async def flow_documents(self) -> tuple[Mapping[str, Any], ...]: ...

    async def tenant_slugs(self) -> tuple[str, ...]: ...

    async def preview_event_upcast(self) -> PersistedEventMigration: ...

    async def upcast_events(
        self,
        confirmation: str,
        *,
        actor_id: str,
        reason: str,
        batch_size: int = 1_000,
    ) -> PersistedEventMigration: ...
