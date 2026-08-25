from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import Protocol
from uuid import UUID

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
