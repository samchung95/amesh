from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .resources import canonical_hash, canonical_json

_CONTEXT_SCHEMA_V1: Literal["amesh.agent-context/v1"] = "amesh.agent-context/v1"
_CONTEXT_SCHEMA_V2: Literal["amesh.agent-context/v2"] = "amesh.agent-context/v2"
_CONTEXT_SCHEMA_V3: Literal["amesh.agent-context/v3"] = "amesh.agent-context/v3"
_CONTEXT_ALGORITHM_V1: Literal["amesh.recent-complete-turns/v1"] = "amesh.recent-complete-turns/v1"
_CONTEXT_ALGORITHM_V2: Literal["amesh.recent-complete-turns/v2"] = "amesh.recent-complete-turns/v2"
_CONTEXT_PROJECTION_VERSIONS = Literal["v1", "v2"]


class AgentContextPolicy(BaseModel):
    """Provider-neutral hard bounds for one derived model context."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    max_messages: int = Field(default=64, alias="maxMessages", ge=3, le=10_000)
    max_bytes: int = Field(default=262_144, alias="maxBytes", ge=256, le=100_000_000)
    max_estimated_tokens: int = Field(
        default=65_536,
        alias="maxEstimatedTokens",
        ge=64,
        le=10_000_000,
    )
    context_window_tokens: int | None = Field(
        default=None,
        alias="contextWindowTokens",
        ge=65,
        le=10_000_000,
    )
    reserved_completion_tokens: int = Field(
        default=4096,
        alias="reservedCompletionTokens",
        ge=1,
        le=1_000_000,
    )

    @model_validator(mode="after")
    def validate_completion_reserve(self) -> AgentContextPolicy:
        if (
            self.context_window_tokens is not None
            and self.context_window_tokens <= self.reserved_completion_tokens
        ):
            raise ValueError("contextWindowTokens must exceed reservedCompletionTokens")
        return self


class AgentHarnessContextBudget(BaseModel):
    """Calculated hard limits offered to one replaceable session harness turn."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.agent-context-budget/v1"] = Field(
        default="amesh.agent-context-budget/v1",
        alias="schemaVersion",
    )
    context_window_tokens: int = Field(alias="contextWindowTokens", ge=2)
    max_input_tokens: int = Field(alias="maxInputTokens", ge=1)
    reserved_completion_tokens: int = Field(alias="reservedCompletionTokens", ge=1)
    compaction_trigger_tokens: int = Field(alias="compactionTriggerTokens", ge=1)
    request_overhead_estimated_tokens: int = Field(
        default=0,
        alias="requestOverheadEstimatedTokens",
        ge=0,
    )
    max_messages: int = Field(alias="maxMessages", ge=1)
    max_bytes: int = Field(alias="maxBytes", ge=1)

    @model_validator(mode="after")
    def validate_window(self) -> AgentHarnessContextBudget:
        admitted = (
            self.max_input_tokens
            + self.reserved_completion_tokens
            + self.request_overhead_estimated_tokens
        )
        if admitted > self.context_window_tokens:
            raise ValueError("context budget exceeds contextWindowTokens")
        if self.compaction_trigger_tokens > self.max_input_tokens:
            raise ValueError("compactionTriggerTokens cannot exceed maxInputTokens")
        return self


class AgentContextReceipt(BaseModel):
    """Content-addressed proof for a bounded projection of an immutable transcript."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal[
        "amesh.agent-context/v1",
        "amesh.agent-context/v2",
        "amesh.agent-context/v3",
    ] = Field(
        default=_CONTEXT_SCHEMA_V1,
        alias="schemaVersion",
    )
    algorithm: str = Field(default=_CONTEXT_ALGORITHM_V1, min_length=1, max_length=255)
    turn: int = Field(ge=1)
    transcript_digest: str = Field(alias="transcriptDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    context_digest: str = Field(alias="contextDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    receipt_digest: str = Field(alias="receiptDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    transcript_message_count: int = Field(alias="transcriptMessageCount", ge=1)
    context_message_count: int = Field(alias="contextMessageCount", ge=1)
    transcript_bytes: int = Field(alias="transcriptBytes", ge=1)
    context_bytes: int = Field(alias="contextBytes", ge=1)
    context_estimated_tokens: int = Field(alias="contextEstimatedTokens", ge=1)
    message_headroom: int = Field(alias="messageHeadroom", ge=0)
    byte_headroom: int = Field(alias="byteHeadroom", ge=0)
    estimated_token_headroom: int = Field(alias="estimatedTokenHeadroom", ge=0)
    retained_source_indexes: tuple[int, ...] = Field(alias="retainedSourceIndexes")
    omitted_source_indexes: tuple[int, ...] = Field(alias="omittedSourceIndexes")
    compacted: bool
    marker_included: bool = Field(alias="markerIncluded")
    complete_turns_preserved: bool = Field(alias="completeTurnsPreserved")
    harness_adapter: str | None = Field(
        default=None,
        alias="harnessAdapter",
        min_length=1,
        max_length=128,
    )
    harness_version: str | None = Field(
        default=None,
        alias="harnessVersion",
        min_length=1,
        max_length=128,
    )
    context_window_tokens: int | None = Field(
        default=None,
        alias="contextWindowTokens",
        ge=2,
    )
    max_input_tokens: int | None = Field(default=None, alias="maxInputTokens", ge=1)
    reserved_completion_tokens: int | None = Field(
        default=None,
        alias="reservedCompletionTokens",
        ge=1,
    )
    compaction_trigger_tokens: int | None = Field(
        default=None,
        alias="compactionTriggerTokens",
        ge=1,
    )
    request_overhead_estimated_tokens: int | None = Field(
        default=None,
        alias="requestOverheadEstimatedTokens",
        ge=0,
    )

    @model_validator(mode="after")
    def validate_version_pair(self) -> AgentContextReceipt:
        if self.schema_version in {_CONTEXT_SCHEMA_V1, _CONTEXT_SCHEMA_V2}:
            expected_algorithm = (
                _CONTEXT_ALGORITHM_V1
                if self.schema_version == _CONTEXT_SCHEMA_V1
                else _CONTEXT_ALGORITHM_V2
            )
            if self.algorithm != expected_algorithm:
                raise ValueError(
                    "context receipt schemaVersion and algorithm must use the same version"
                )
            return self
        required = (
            self.harness_adapter,
            self.harness_version,
            self.context_window_tokens,
            self.max_input_tokens,
            self.reserved_completion_tokens,
            self.compaction_trigger_tokens,
            self.request_overhead_estimated_tokens,
        )
        if any(value is None for value in required):
            raise ValueError("v3 context receipts require harness and context-budget evidence")
        return self


class AgentContextProjection(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    messages: tuple[dict[str, Any], ...]
    receipt: AgentContextReceipt


def calculate_agent_context_budget(
    policy: AgentContextPolicy,
    *,
    max_completion_tokens: int,
    request_overhead_estimated_tokens: int = 0,
) -> AgentHarnessContextBudget:
    """Resolve a policy into one turn's input and completion allocations."""

    if max_completion_tokens < 1:
        raise ValueError("max completion tokens must be positive")
    if request_overhead_estimated_tokens < 0:
        raise ValueError("request overhead cannot be negative")
    completion_reserve = min(max_completion_tokens, policy.reserved_completion_tokens)
    context_window = policy.context_window_tokens or (
        policy.max_estimated_tokens
        + policy.reserved_completion_tokens
        + request_overhead_estimated_tokens
    )
    max_input = min(
        policy.max_estimated_tokens,
        context_window - completion_reserve - request_overhead_estimated_tokens,
    )
    if max_input < 1:
        raise ValueError("context window leaves no capacity for model input")
    return AgentHarnessContextBudget(
        contextWindowTokens=context_window,
        maxInputTokens=max_input,
        reservedCompletionTokens=completion_reserve,
        compactionTriggerTokens=max_input,
        requestOverheadEstimatedTokens=request_overhead_estimated_tokens,
        maxMessages=policy.max_messages,
        maxBytes=policy.max_bytes,
    )


def create_harness_context_receipt(
    source_messages: tuple[dict[str, Any], ...],
    selected_messages: tuple[dict[str, Any], ...],
    budget: AgentHarnessContextBudget,
    *,
    turn: int,
    algorithm: str,
    harness_adapter: str,
    harness_version: str,
    retained_source_indexes: tuple[int, ...],
    omitted_source_indexes: tuple[int, ...],
) -> AgentContextReceipt:
    """Validate a harness-selected source subset and produce its v3 receipt."""

    if not source_messages or not selected_messages:
        raise ValueError("harness context requires non-empty source and selected messages")
    retained = tuple(retained_source_indexes)
    omitted = tuple(omitted_source_indexes)
    all_indexes = tuple(range(len(source_messages)))
    if retained != tuple(sorted(set(retained))) or omitted != tuple(sorted(set(omitted))):
        raise ValueError("context source indexes must be sorted and unique")
    if tuple(sorted((*retained, *omitted))) != all_indexes:
        raise ValueError("retained and omitted indexes must partition the source transcript")
    expected_messages = tuple(source_messages[index] for index in retained)
    if canonical_json(selected_messages) != canonical_json(expected_messages):
        raise ValueError("selected context messages must exactly match retained source messages")

    prefix_indexes, dialogue_groups = _message_groups(source_messages)
    if retained[: len(prefix_indexes)] != prefix_indexes:
        raise ValueError("harness context must preserve the pinned message prefix")
    retained_set = set(retained)
    complete_turns_preserved = all(
        retained_set.isdisjoint(group) or retained_set.issuperset(group)
        for group in dialogue_groups
    )
    if not complete_turns_preserved:
        raise ValueError("harness context must retain or omit complete dialogue groups")
    if dialogue_groups and not retained_set.issuperset(dialogue_groups[-1]):
        raise ValueError("harness context must retain the newest complete dialogue group")

    context_bytes, estimated_tokens = _size(selected_messages)
    if len(selected_messages) > budget.max_messages:
        raise ValueError("harness context exceeds maxMessages")
    if context_bytes > budget.max_bytes:
        raise ValueError("harness context exceeds maxBytes")
    if estimated_tokens > budget.max_input_tokens:
        raise ValueError("harness context exceeds maxInputTokens")

    transcript_bytes, _ = _size(source_messages)
    receipt_data: dict[str, Any] = {
        "schemaVersion": _CONTEXT_SCHEMA_V3,
        "algorithm": algorithm,
        "turn": turn,
        "transcriptDigest": _digest(source_messages),
        "contextDigest": _digest(selected_messages),
        "transcriptMessageCount": len(source_messages),
        "contextMessageCount": len(selected_messages),
        "transcriptBytes": transcript_bytes,
        "contextBytes": context_bytes,
        "contextEstimatedTokens": estimated_tokens,
        "messageHeadroom": budget.max_messages - len(selected_messages),
        "byteHeadroom": budget.max_bytes - context_bytes,
        "estimatedTokenHeadroom": budget.max_input_tokens - estimated_tokens,
        "retainedSourceIndexes": retained,
        "omittedSourceIndexes": omitted,
        "compacted": bool(omitted),
        "markerIncluded": False,
        "completeTurnsPreserved": complete_turns_preserved,
        "harnessAdapter": harness_adapter,
        "harnessVersion": harness_version,
        "contextWindowTokens": budget.context_window_tokens,
        "maxInputTokens": budget.max_input_tokens,
        "reservedCompletionTokens": budget.reserved_completion_tokens,
        "compactionTriggerTokens": budget.compaction_trigger_tokens,
        "requestOverheadEstimatedTokens": budget.request_overhead_estimated_tokens,
    }
    receipt_data["receiptDigest"] = "sha256:" + canonical_hash(receipt_data)
    return AgentContextReceipt.model_validate(receipt_data)


def verify_harness_context_receipt(
    source_messages: tuple[dict[str, Any], ...],
    selected_messages: tuple[dict[str, Any], ...],
    budget: AgentHarnessContextBudget,
    receipt: AgentContextReceipt,
) -> None:
    """Fail closed unless a v3 receipt exactly proves the offered projection."""

    if receipt.schema_version != _CONTEXT_SCHEMA_V3:
        raise ValueError("harness model calls require an agent-context/v3 receipt")
    expected = create_harness_context_receipt(
        source_messages,
        selected_messages,
        budget,
        turn=receipt.turn,
        algorithm=receipt.algorithm,
        harness_adapter=receipt.harness_adapter or "",
        harness_version=receipt.harness_version or "",
        retained_source_indexes=receipt.retained_source_indexes,
        omitted_source_indexes=receipt.omitted_source_indexes,
    )
    if expected != receipt:
        raise ValueError("harness context receipt does not match the selected messages")


def project_agent_context(
    messages: tuple[dict[str, Any], ...],
    policy: AgentContextPolicy,
    *,
    turn: int,
    version: _CONTEXT_PROJECTION_VERSIONS = "v2",
) -> AgentContextProjection:
    """Retain pinned prefix and newest complete assistant/follow-up groups within all bounds.

    Version 2 keeps the model-visible compaction marker stable as the transcript grows. Version 1
    remains available for replaying or comparing legacy projections; persisted v1 receipts are also
    accepted by ``AgentContextReceipt``.
    """

    if not messages:
        raise ValueError("agent context projection requires a non-empty transcript")
    prefix_indexes, dialogue_groups = _message_groups(messages)
    retained_groups = list(dialogue_groups)
    omitted: list[int] = []
    transcript_digest = _digest(messages)

    while True:
        retained_indexes = (
            *prefix_indexes,
            *(index for group in retained_groups for index in group),
        )
        compacted = bool(omitted)
        context = _context_messages(
            messages,
            prefix_indexes,
            retained_groups,
            transcript_digest=transcript_digest,
            omitted_count=len(omitted),
            version=version,
        )
        context_bytes, estimated_tokens = _size(context)
        if _fits(context, context_bytes, estimated_tokens, policy):
            break
        if len(retained_groups) <= 1:
            raise ValueError(
                "agent pinned instructions, input and newest complete turn exceed contextPolicy"
            )
        omitted.extend(retained_groups.pop(0))

    omitted_indexes = tuple(sorted(omitted))
    retained_source_indexes = tuple(retained_indexes)
    transcript_bytes, _ = _size(messages)
    receipt_data: dict[str, Any] = {
        "schemaVersion": _CONTEXT_SCHEMA_V1 if version == "v1" else _CONTEXT_SCHEMA_V2,
        "algorithm": _CONTEXT_ALGORITHM_V1 if version == "v1" else _CONTEXT_ALGORITHM_V2,
        "turn": turn,
        "transcriptDigest": transcript_digest,
        "contextDigest": _digest(context),
        "transcriptMessageCount": len(messages),
        "contextMessageCount": len(context),
        "transcriptBytes": transcript_bytes,
        "contextBytes": context_bytes,
        "contextEstimatedTokens": estimated_tokens,
        "messageHeadroom": policy.max_messages - len(context),
        "byteHeadroom": policy.max_bytes - context_bytes,
        "estimatedTokenHeadroom": policy.max_estimated_tokens - estimated_tokens,
        "retainedSourceIndexes": retained_source_indexes,
        "omittedSourceIndexes": omitted_indexes,
        "compacted": compacted,
        "markerIncluded": compacted,
        "completeTurnsPreserved": True,
    }
    receipt_data["receiptDigest"] = "sha256:" + canonical_hash(receipt_data)
    return AgentContextProjection(
        messages=context,
        receipt=AgentContextReceipt.model_validate(receipt_data),
    )


def _message_groups(
    messages: tuple[dict[str, Any], ...],
) -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    first_assistant = next(
        (index for index, message in enumerate(messages) if message.get("role") == "assistant"),
        len(messages),
    )
    prefix = tuple(range(first_assistant))
    groups: list[list[int]] = []
    for index in range(first_assistant, len(messages)):
        role = messages[index].get("role")
        if role == "assistant" or not groups:
            groups.append([index])
        else:
            groups[-1].append(index)
    return prefix, tuple(tuple(group) for group in groups)


def _context_messages(
    messages: tuple[dict[str, Any], ...],
    prefix_indexes: tuple[int, ...],
    dialogue_groups: list[tuple[int, ...]],
    *,
    transcript_digest: str,
    omitted_count: int,
    version: _CONTEXT_PROJECTION_VERSIONS,
) -> tuple[dict[str, Any], ...]:
    prefix = tuple(messages[index] for index in prefix_indexes)
    dialogue = tuple(messages[index] for group in dialogue_groups for index in group)
    if omitted_count == 0:
        return (*prefix, *dialogue)
    if version == "v2":
        marker_content = (
            "AMESH compacted older complete turns from model context. "
            "Refer to the durable context receipt for provenance."
        )
    else:
        marker_content = (
            "AMESH compacted older complete turns from model context. "
            f"Canonical transcript {transcript_digest}; omitted messages: {omitted_count}."
        )
    marker = {"role": "system", "content": marker_content}
    return (*prefix, marker, *dialogue)


def _size(messages: tuple[dict[str, Any], ...]) -> tuple[int, int]:
    byte_count = len(canonical_json(messages))
    return byte_count, max(1, (byte_count + 3) // 4)


def _fits(
    messages: tuple[dict[str, Any], ...],
    byte_count: int,
    estimated_tokens: int,
    policy: AgentContextPolicy,
) -> bool:
    return (
        len(messages) <= policy.max_messages
        and byte_count <= policy.max_bytes
        and estimated_tokens <= policy.max_estimated_tokens
    )


def _digest(messages: tuple[dict[str, Any], ...]) -> str:
    return "sha256:" + canonical_hash(messages)
