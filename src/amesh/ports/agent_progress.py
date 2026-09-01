from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain.agent_progress import AgentProgressFrame


class AgentProgressContext(BaseModel):
    """Stable AMESH identities supplied to a progress producer, never inferred by it."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    service_session_id: UUID = Field(alias="serviceSessionId")
    execution_id: UUID = Field(alias="executionId")
    task_run_id: UUID = Field(alias="taskRunId")
    attempt_session_id: UUID = Field(alias="attemptSessionId")
    attempt: int = Field(ge=1)


class AgentProgressReceipt(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    event_id: UUID = Field(alias="eventId")
    event_index: int = Field(alias="eventIndex", ge=1)
    cursor: str = Field(min_length=1, max_length=512)
    duplicate: bool = False


class AgentProgressSink(Protocol):
    async def append(
        self,
        context: AgentProgressContext,
        frame: AgentProgressFrame,
    ) -> AgentProgressReceipt: ...

    async def close_active_segment(
        self,
        context: AgentProgressContext,
        *,
        occurred_at: datetime,
    ) -> None: ...


__all__ = ["AgentProgressContext", "AgentProgressReceipt", "AgentProgressSink"]
