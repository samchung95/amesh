from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .agent_context import AgentContextReceipt
from .agent_tool_plan import ToolPlanLedger
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


class AgentSessionEventType(StrEnum):
    SESSION_STARTED = "session.started"
    CONTEXT_PROJECTED = "context.projected"
    CONTEXT_COMPACTED = "context.compacted"
    MODEL_RESPONSE = "model.response"
    POLICY_AUTHORIZED = "policy.authorized"
    RELEASE_APPROVED = "release.approved"
    TOOL_RESULT = "tool.result"
    EVALUATION_COMPLETED = "evaluation.completed"
    MEMORY_WRITTEN = "memory.written"
    OUTPUT_REJECTED = "output.rejected"
    OUTPUT_ACCEPTED = "output.accepted"
    SESSION_FAILED = "session.failed"


class AgentBillingCertainty(StrEnum):
    EXACT = "exact"
    LOWER_BOUND = "lower_bound"
    UNRESOLVED = "unresolved"


class AgentSessionCounters(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    turns: int = Field(default=0, ge=0)
    loop_iterations: int = Field(default=0, alias="loopIterations", ge=0)
    tool_calls: int = Field(default=0, alias="toolCalls", ge=0)
    input_tokens: int = Field(default=0, alias="inputTokens", ge=0)
    output_tokens: int = Field(default=0, alias="outputTokens", ge=0)
    reasoning_tokens: int = Field(default=0, alias="reasoningTokens", ge=0)
    total_tokens: int = Field(default=0, alias="totalTokens", ge=0)
    cache_read_tokens: int = Field(default=0, alias="cacheReadTokens", ge=0)
    cache_write_tokens: int = Field(default=0, alias="cacheWriteTokens", ge=0)
    cost_usd: Decimal = Field(default=Decimal("0"), alias="costUsd", ge=0)
    priced_model_invocations: int = Field(
        default=0,
        alias="pricedModelInvocations",
        ge=0,
    )
    unresolved_model_invocations: int = Field(
        default=0,
        alias="unresolvedModelInvocations",
        ge=0,
    )
    billing_certainty: AgentBillingCertainty = Field(
        default=AgentBillingCertainty.EXACT,
        alias="billingCertainty",
    )
    repair_attempts: int = Field(default=0, alias="repairAttempts", ge=0)


class AgentHarnessPin(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    adapter: str = Field(min_length=1, max_length=128)
    adapter_version: str = Field(alias="adapterVersion", min_length=1, max_length=128)
    protocol: str = Field(min_length=1, max_length=128)


class AgentModelContinuationRef(BaseModel):
    """Public handle to private provider continuation state."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    invocation_id: UUID = Field(alias="invocationId")
    provider_id: str = Field(alias="providerId", min_length=1, max_length=255)
    provider_revision: str = Field(alias="providerRevision", min_length=1, max_length=255)
    token_digest: str = Field(alias="tokenDigest", pattern=r"^sha256:[0-9a-f]{64}$")


class AgentModelContinuationBinding(BaseModel):
    """A safe continuation handle bound to its canonical assistant message."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def normalize_flat_ref(cls, value: object) -> object:
        if not isinstance(value, dict) or "continuation" in value:
            return value
        ref_keys = {
            "invocationId",
            "providerId",
            "providerRevision",
            "tokenDigest",
            "invocation_id",
            "provider_id",
            "provider_revision",
            "token_digest",
        }
        if not ref_keys.issubset(value):
            return value
        normalized = dict(value)
        normalized["continuation"] = {
            key: normalized.pop(key) for key in ref_keys if key in normalized
        }
        return normalized

    source_message_index: int = Field(alias="sourceMessageIndex", ge=0)
    continuation: AgentModelContinuationRef

    @property
    def invocation_id(self) -> UUID:
        return self.continuation.invocation_id


class AgentSessionCheckpoint(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_continuation_aliases(cls, value: object) -> object:
        if not isinstance(value, dict) or "modelContinuations" in value:
            return value
        normalized = dict(value)
        for alias in (
            "modelContinuationBindings",
            "continuationBindings",
            "model_continuation_bindings",
            "continuation_bindings",
        ):
            if alias in normalized:
                normalized["modelContinuations"] = normalized.pop(alias)
                break
        return normalized

    messages: tuple[dict[str, Any], ...] = ()
    next_turn: int = Field(default=1, alias="nextTurn", ge=1)
    last_accepted_operation: str | None = Field(default=None, alias="lastAcceptedOperation")
    pending_action: dict[str, Any] | None = Field(default=None, alias="pendingAction")
    pending_turn: int | None = Field(default=None, alias="pendingTurn", ge=1)
    memory_entries: tuple[dict[str, Any], ...] = Field(default=(), alias="memoryEntries")
    evaluation_outcomes: tuple[dict[str, Any], ...] = Field(default=(), alias="evaluationOutcomes")
    release_approved: bool = Field(default=False, alias="releaseApproved")
    memory_write: dict[str, Any] | None = Field(default=None, alias="memoryWrite")
    model_continuation: AgentModelContinuationRef | None = Field(
        default=None,
        alias="modelContinuation",
    )
    model_continuations: tuple[AgentModelContinuationBinding, ...] = Field(
        default=(),
        alias="modelContinuations",
        max_length=64,
    )
    last_context_receipt: AgentContextReceipt | None = Field(
        default=None,
        alias="lastContextReceipt",
    )
    tool_plan: ToolPlanLedger | None = Field(default=None, alias="toolPlan")

    @model_validator(mode="after")
    def validate_model_continuations(self) -> AgentSessionCheckpoint:
        indexes = tuple(item.source_message_index for item in self.model_continuations)
        if indexes != tuple(sorted(set(indexes))):
            raise ValueError("model continuations must be ordered by unique sourceMessageIndex")
        return self

    @property
    def continuation_bindings(self) -> tuple[AgentModelContinuationBinding, ...]:
        return self.model_continuations

    @property
    def model_continuation_bindings(self) -> tuple[AgentModelContinuationBinding, ...]:
        return self.model_continuations

    @property
    def model_continuation_history(self) -> tuple[AgentModelContinuationBinding, ...]:
        return self.model_continuations


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
    harness: AgentHarnessPin | None = None


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
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    event_key: str = Field(alias="eventKey", min_length=1, max_length=255)
    event_type: AgentSessionEventType = Field(alias="eventType")
    payload: dict[str, Any] = Field(default_factory=dict)
    checkpoint: AgentSessionCheckpoint
    counters: AgentSessionCounters
    final_result: dict[str, Any] | None = Field(default=None, alias="finalResult")
    error: str | None = Field(default=None, max_length=4096)
    harness: AgentHarnessPin | None = None


class AgentSessionDetail(BaseModel):
    model_config = ConfigDict(frozen=True)

    session: AgentSessionRecord
    events: tuple[AgentSessionEvent, ...]
