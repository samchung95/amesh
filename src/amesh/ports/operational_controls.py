from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from amesh.domain import (
    Announcement,
    AnnouncementCreateRequest,
    OperationalBoundary,
    OperationalControl,
    OperationalControlActionRequest,
    OperationalControlCreateRequest,
    OperationalControlDecision,
    OperationalControlEvent,
)


class OperationalControlEvaluator(Protocol):
    async def evaluate(
        self,
        boundary: OperationalBoundary,
        *,
        tenant_id: str,
        namespace: str | None = None,
        flow_id: str | None = None,
        plugin_ids: Sequence[str] = (),
        runner_ids: Sequence[str] = (),
        component_id: str | None = None,
        component_role: str | None = None,
    ) -> OperationalControlDecision: ...


class OperationalControlRepository(OperationalControlEvaluator, Protocol):
    async def create_announcement(
        self,
        request: AnnouncementCreateRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> Announcement: ...

    async def list_announcements(
        self,
        tenant_id: str,
        *,
        namespace: str | None = None,
        include_inactive: bool = False,
    ) -> tuple[Announcement, ...]: ...

    async def deactivate_announcement(
        self,
        announcement_id: UUID,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int,
    ) -> Announcement: ...

    async def create_control(
        self,
        request: OperationalControlCreateRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> OperationalControl: ...

    async def list_controls(self, tenant_id: str) -> tuple[OperationalControl, ...]: ...

    async def get_control(self, control_id: UUID, *, tenant_id: str) -> OperationalControl: ...

    async def apply_action(
        self,
        control_id: UUID,
        request: OperationalControlActionRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> OperationalControl: ...

    async def acknowledge_active(
        self,
        *,
        tenant_ids: Sequence[str],
        component_id: str,
        component_role: str,
    ) -> int: ...

    async def list_events(
        self, tenant_id: str, *, limit: int = 200
    ) -> tuple[OperationalControlEvent, ...]: ...


__all__ = ["OperationalControlEvaluator", "OperationalControlRepository"]
