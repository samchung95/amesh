from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .identity import NamespaceId, new_runtime_id


class AgentSessionState(StrEnum):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class AgentSessionPhase(StrEnum):
    READY = "READY"
    MODEL = "MODEL"
    POLICY = "POLICY"
    APPROVAL = "APPROVAL"
    TOOL = "TOOL"
    VALIDATING = "VALIDATING"
    COMPLETE = "COMPLETE"


class AgentSessionCounters(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    turns: int = Field(default=0, ge=0)
    loop_iterations: int = Field(default=0, alias="loopIterations", ge=0)
    tool_calls: int = Field(default=0, alias="toolCalls", ge=0)
    total_tokens: int = Field(default=0, alias="totalTokens", ge=0)
    cost_usd: Decimal = Field(default=Decimal("0"), alias="costUsd", ge=0)
    repair_attempts: int = Field(default=0, alias="repairAttempts", ge=0)


class AgentSessionCheckpoint(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    messages: tuple[dict[str, Any], ...] = ()
    next_turn: int = Field(default=1, alias="nextTurn", ge=1)
    last_accepted_operation: str | None = Field(default=None, alias="lastAcceptedOperation")
    pending_action: dict[str, Any] | None = Field(default=None, alias="pendingAction")
    pending_turn: int | None = Field(default=None, alias="pendingTurn", ge=1)


class AgentSessionStart(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    session_id: UUID = Field(default_factory=new_runtime_id, alias="sessionId")
    tenant_id: str = Field(alias="tenantId")
    namespace: NamespaceId
    execution_id: UUID = Field(alias="executionId")
    task_run_id: UUID = Field(alias="taskRunId")
    attempt: int = Field(ge=1)
    capability_pin_id: UUID = Field(alias="capabilityPinId")
    envelope_digest: str = Field(alias="envelopeDigest", pattern=r"^sha256:[0-9a-f]{64}$")


class AgentSessionRecord(AgentSessionStart):
    state: AgentSessionState = AgentSessionState.RUNNING
    phase: AgentSessionPhase = AgentSessionPhase.READY
    version: int = Field(default=0, ge=0)
    checkpoint: AgentSessionCheckpoint = Field(default_factory=AgentSessionCheckpoint)
    counters: AgentSessionCounters = Field(default_factory=AgentSessionCounters)
    final_result: dict[str, Any] | None = Field(default=None, alias="finalResult")
    error: str | None = Field(default=None, max_length=4096)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="createdAt")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="updatedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")


class AgentSessionEvent(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    event_id: UUID = Field(default_factory=new_runtime_id, alias="eventId")
    session_id: UUID = Field(alias="sessionId")
    event_index: int = Field(alias="eventIndex", ge=1)
    event_key: str = Field(alias="eventKey", min_length=1, max_length=255)
    event_type: str = Field(alias="eventType", min_length=1, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="occurredAt")


class AgentSessionTransition(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    event_key: str = Field(alias="eventKey", min_length=1, max_length=255)
    event_type: str = Field(alias="eventType", min_length=1, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)
    phase: AgentSessionPhase
    state: AgentSessionState = AgentSessionState.RUNNING
    checkpoint: AgentSessionCheckpoint
    counters: AgentSessionCounters
    final_result: dict[str, Any] | None = Field(default=None, alias="finalResult")
    error: str | None = Field(default=None, max_length=4096)


class AgentSessionDetail(BaseModel):
    model_config = ConfigDict(frozen=True)

    session: AgentSessionRecord
    events: tuple[AgentSessionEvent, ...]
