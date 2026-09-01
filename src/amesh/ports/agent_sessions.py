from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import Protocol
from uuid import UUID

from amesh.domain.agent_progress import AgentProgressEvent, AgentSessionEventCursor
from amesh.domain.agent_sessions import (
    AgentSessionDetail,
    AgentSessionRecord,
    AgentSessionStart,
    AgentSessionTransition,
)


class AgentSessionRepository(Protocol):
    def session_guard(
        self,
        tenant_id: str,
        task_run_id: UUID,
        attempt: int,
    ) -> AbstractAsyncContextManager[None]: ...

    async def start_session(self, start: AgentSessionStart) -> AgentSessionRecord: ...

    async def transition(
        self,
        session_id: UUID,
        *,
        tenant_id: str,
        transition: AgentSessionTransition,
    ) -> AgentSessionRecord: ...

    async def get_session(
        self,
        tenant_id: str,
        task_run_id: UUID,
        attempt: int,
    ) -> AgentSessionDetail: ...

    async def list_execution_sessions(
        self,
        tenant_id: str,
        execution_id: UUID,
    ) -> tuple[AgentSessionRecord, ...]: ...

    async def get_execution_by_service_session_id(
        self,
        tenant_id: str,
        service_session_id: UUID,
    ) -> UUID: ...

    async def list_service_sessions(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
        owner_id: str | None = None,
    ) -> tuple[tuple[UUID, UUID, str | None, AgentSessionRecord | None], ...]: ...

    async def list_progress_events(
        self,
        tenant_id: str,
        service_session_id: UUID,
        *,
        after: AgentSessionEventCursor | None = None,
        limit: int = 100,
    ) -> tuple[AgentProgressEvent, ...]: ...
