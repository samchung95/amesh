from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .resources import canonical_hash, canonical_json

_CONTEXT_SCHEMA_V1: Literal["amesh.agent-context/v1"] = "amesh.agent-context/v1"
_CONTEXT_SCHEMA_V2: Literal["amesh.agent-context/v2"] = "amesh.agent-context/v2"
_CONTEXT_ALGORITHM_V1: Literal["amesh.recent-complete-turns/v1"] = (
    "amesh.recent-complete-turns/v1"
)
_CONTEXT_ALGORITHM_V2: Literal["amesh.recent-complete-turns/v2"] = (
    "amesh.recent-complete-turns/v2"
)
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


class AgentContextReceipt(BaseModel):
    """Content-addressed proof for a bounded projection of an immutable transcript."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.agent-context/v1", "amesh.agent-context/v2"] = Field(
        default=_CONTEXT_SCHEMA_V1,
        alias="schemaVersion",
    )
    algorithm: Literal["amesh.recent-complete-turns/v1", "amesh.recent-complete-turns/v2"] = (
        _CONTEXT_ALGORITHM_V1
    )
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

    @model_validator(mode="after")
    def validate_version_pair(self) -> AgentContextReceipt:
        expected_algorithm = (
            _CONTEXT_ALGORITHM_V1
            if self.schema_version == _CONTEXT_SCHEMA_V1
            else _CONTEXT_ALGORITHM_V2
        )
        if self.algorithm != expected_algorithm:
            raise ValueError("context receipt schemaVersion and algorithm must use the same version")
        return self


class AgentContextProjection(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    messages: tuple[dict[str, Any], ...]
    receipt: AgentContextReceipt


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
