from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .agent_sessions import AgentHarnessPin, AgentSessionCounters


class AgentSessionFleetQuery(BaseModel):
    """Bounded tenant fleet query with a fixed newest-first ordering."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    limit: int = Field(default=100, ge=1, le=100)
    cursor: str | None = Field(default=None, max_length=2048)
    state: str | None = Field(default=None, min_length=1, max_length=32)
    namespace: str | None = Field(default=None, min_length=1, max_length=255)
    agent_ref: str | None = Field(default=None, alias="agentRef", min_length=1, max_length=512)
    owner_id: str | None = Field(default=None, alias="ownerId", min_length=1, max_length=255)
    harness: str | None = Field(default=None, min_length=1, max_length=128)
    created_from: datetime | None = Field(default=None, alias="createdFrom")
    created_to: datetime | None = Field(default=None, alias="createdTo")

    @model_validator(mode="after")
    def validate_window_and_state(self) -> AgentSessionFleetQuery:
        if (
            self.created_from is not None
            and self.created_to is not None
            and self.created_to < self.created_from
        ):
            raise ValueError("createdTo cannot be earlier than createdFrom")
        allowed_states = {
            "CREATED",
            "QUEUED",
            "RUNNING",
            "PAUSED",
            "CANCELLING",
            "CANCELLED",
            "SUCCEEDED",
            "FAILED",
            "WARNING",
            "RESTARTING",
        }
        if self.state is not None and self.state not in allowed_states:
            raise ValueError("unsupported agent-session fleet state")
        return self

    def fingerprint(self) -> str:
        payload = self.model_dump(mode="json", by_alias=True, exclude={"cursor", "limit"})
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:32]


class AgentSessionFleetItem(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: UUID = Field(alias="sessionId")
    attempt_session_id: UUID | None = Field(default=None, alias="attemptSessionId")
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    agent_ref: str | None = Field(default=None, alias="agentRef")
    application_id: str | None = Field(default=None, alias="applicationId")
    owner_id: str | None = Field(default=None, alias="ownerId")
    execution_id: UUID = Field(alias="executionId")
    task_run_id: UUID | None = Field(default=None, alias="taskRunId")
    attempt: int | None = Field(default=None, ge=1)
    state: str
    phase: str | None = None
    version: int | None = Field(default=None, ge=0)
    execution_version: int = Field(alias="executionVersion", ge=0)
    execution_epoch: int = Field(alias="executionEpoch", ge=0)
    capability_pin_id: UUID | None = Field(default=None, alias="capabilityPinId")
    envelope_digest: str | None = Field(default=None, alias="envelopeDigest")
    harness: AgentHarnessPin | None = None
    counters: AgentSessionCounters = Field(default_factory=AgentSessionCounters)
    model_invocation_count: int = Field(default=0, alias="modelInvocationCount", ge=0)
    tool_invocation_count: int = Field(default=0, alias="toolInvocationCount", ge=0)
    failed_invocation_count: int = Field(default=0, alias="failedInvocationCount", ge=0)
    dependency_keys: tuple[str, ...] = Field(default=(), alias="dependencyKeys", max_length=20)
    dependency_health: str = Field(default="HEALTHY", alias="dependencyHealth")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    policy_provenance: dict[str, Any] | None = Field(default=None, alias="policyProvenance")


class AgentSessionFleetAggregates(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    matched_executions: int = Field(alias="matchedExecutions", ge=0)
    active: int = Field(ge=0)
    terminal: int = Field(ge=0)
    by_state: dict[str, int] = Field(default_factory=dict, alias="byState")
    total_turns: int = Field(default=0, alias="totalTurns", ge=0)
    total_tool_calls: int = Field(default=0, alias="totalToolCalls", ge=0)
    total_tokens: int = Field(default=0, alias="totalTokens", ge=0)
    total_cost_usd: str = Field(default="0", alias="totalCostUsd")
    model_invocations: int = Field(default=0, alias="modelInvocations", ge=0)
    tool_invocations: int = Field(default=0, alias="toolInvocations", ge=0)
    failed_invocations: int = Field(default=0, alias="failedInvocations", ge=0)
    degraded_dependencies: int = Field(default=0, alias="degradedDependencies", ge=0)


class AgentSessionFleetPage(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    items: tuple[AgentSessionFleetItem, ...]
    next_cursor: str | None = Field(default=None, alias="nextCursor")
    aggregates: AgentSessionFleetAggregates
    read_at: datetime = Field(alias="readAt")


class AgentSessionInstanceTenantAggregate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    tenant_id: UUID = Field(alias="tenantId")
    tenant_slug: str = Field(alias="tenantSlug")
    matched_executions: int = Field(alias="matchedExecutions", ge=0)
    active: int = Field(ge=0)
    terminal: int = Field(ge=0)
    by_state: dict[str, int] = Field(default_factory=dict, alias="byState")


class AgentSessionInstanceAggregate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    tenants: tuple[AgentSessionInstanceTenantAggregate, ...]
    matched_executions: int = Field(alias="matchedExecutions", ge=0)
    active: int = Field(ge=0)
    terminal: int = Field(ge=0)
    read_at: datetime = Field(alias="readAt")


def counters_from_json(value: Any) -> AgentSessionCounters:
    if not isinstance(value, dict):
        return AgentSessionCounters()
    return AgentSessionCounters.model_validate(value)
