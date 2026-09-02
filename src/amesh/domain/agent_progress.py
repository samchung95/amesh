from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Mapping
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Annotated, Literal
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_CURSOR_PREFIX = "v1."
_TERMINAL_PROGRESS_STATUSES = frozenset(
    {
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "TRUNCATED",
    }
)


class AgentProgressActivity(StrEnum):
    THINKING = "THINKING"
    MODEL = "MODEL"
    POLICY = "POLICY"
    TOOL = "TOOL"
    APPROVAL = "APPROVAL"
    VALIDATION = "VALIDATION"
    ARTIFACT = "ARTIFACT"
    OUTPUT = "OUTPUT"
    TERMINAL = "TERMINAL"


class AgentProgressStatus(StrEnum):
    STARTED = "STARTED"
    DELTA = "DELTA"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"
    TRUNCATED = "TRUNCATED"


class AgentStatusDetail(BaseModel):
    """An AMESH-owned factual lifecycle description."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: Literal["STATUS"] = "STATUS"
    code: str = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9_.-]*$")
    label: str | None = Field(default=None, min_length=1, max_length=256)


class AgentPublicSummaryDetail(BaseModel):
    """Bounded text explicitly classified by an adapter as public, never hidden reasoning."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: Literal["PUBLIC_SUMMARY"] = "PUBLIC_SUMMARY"
    text: str = Field(min_length=1, max_length=4096)
    source: Literal["provider_public_summary"] = "provider_public_summary"
    truncated: bool = False

    @field_validator("text")
    @classmethod
    def reject_nul(cls, value: str) -> str:
        if "\x00" in value:
            raise ValueError("public progress summary cannot contain NUL")
        return value


AgentProgressDetail = Annotated[
    AgentStatusDetail | AgentPublicSummaryDetail,
    Field(discriminator="kind"),
]


class AgentProgressLimits(BaseModel):
    """Frame validation plus optional operator ceilings for progress ingestion."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    max_frame_bytes: int = Field(default=16_384, alias="maxFrameBytes", ge=512, le=1_048_576)
    max_frames_per_segment: int | None = Field(
        default=None,
        alias="maxFramesPerSegment",
        ge=1,
        le=4096,
    )
    max_segments_per_session: int | None = Field(
        default=None,
        alias="maxSegmentsPerSession",
        ge=1,
        le=16_384,
    )
    max_frames_per_session: int | None = Field(
        default=None,
        alias="maxFramesPerSession",
        ge=1,
        le=65_536,
    )
    max_buffered_frames: int = Field(
        default=256,
        alias="maxBufferedFrames",
        ge=1,
        le=4096,
    )
    max_frames_per_second: int | None = Field(
        default=None,
        alias="maxFramesPerSecond",
        ge=1,
        le=1000,
    )
    heartbeat_seconds: float = Field(
        default=5.0,
        alias="heartbeatSeconds",
        gt=0,
        le=60,
    )


class AgentProgressLimitExceeded(ValueError):
    """A bounded progress producer exceeded a declared limit."""


class AgentProgressFrame(BaseModel):
    """One safe provider- or harness-neutral progress item before journal acceptance."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.agent-progress/v1"] = Field(
        default="amesh.agent-progress/v1",
        alias="schemaVersion",
    )
    attempt_session_id: UUID = Field(alias="attemptSessionId")
    attempt: int = Field(ge=1)
    turn: int | None = Field(default=None, ge=1)
    activity: AgentProgressActivity
    status: AgentProgressStatus
    activity_id: str = Field(
        alias="activityId",
        min_length=1,
        max_length=255,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]*$",
    )
    segment_id: UUID | None = Field(default=None, alias="segmentId")
    source_id: str = Field(
        alias="sourceId",
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]*$",
    )
    source_sequence: int = Field(alias="sourceSequence", ge=1)
    occurred_at: datetime = Field(alias="occurredAt")
    detail: AgentProgressDetail | None = None

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurredAt must include a time-zone offset")
        return value

    @model_validator(mode="after")
    def validate_segment_semantics(self) -> AgentProgressFrame:
        if self.activity is AgentProgressActivity.THINKING and self.segment_id is None:
            raise ValueError("thinking progress requires segmentId")
        if self.status in {AgentProgressStatus.DELTA, AgentProgressStatus.TRUNCATED} and (
            self.segment_id is None
        ):
            raise ValueError(f"{self.status.value} progress requires segmentId")
        return self

    @property
    def event_key(self) -> str:
        identity = f"{self.source_id}:{self.source_sequence}".encode()
        digest = hashlib.sha256(identity).hexdigest()[:32]
        return f"progress:{self.attempt}:{digest}"

    @property
    def fingerprint(self) -> str:
        payload = self.model_dump(mode="json", by_alias=True)
        payload.pop("occurredAt")
        encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        return "sha256:" + hashlib.sha256(encoded).hexdigest()


class AgentProgressSourceFrame(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    source_id: str = Field(alias="sourceId", min_length=1, max_length=128)
    source_sequence: int = Field(alias="sourceSequence", ge=1)
    fingerprint: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class AgentProgressSequenceState(BaseModel):
    """Pure reducer state used by each attempt's progress sink."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    attempt_session_id: UUID | None = Field(default=None, alias="attemptSessionId")
    attempt: int | None = Field(default=None, ge=1)
    accepted_sources: tuple[AgentProgressSourceFrame, ...] = Field(
        default=(),
        alias="acceptedSources",
    )
    active_segment_id: UUID | None = Field(default=None, alias="activeSegmentId")
    active_segment_frame_count: int = Field(default=0, alias="activeSegmentFrameCount", ge=0)
    closed_segment_ids: frozenset[UUID] = Field(default=frozenset(), alias="closedSegmentIds")
    segment_count: int = Field(default=0, alias="segmentCount", ge=0)
    accepted_frame_count: int = Field(default=0, alias="acceptedFrameCount", ge=0)
    accepted_occurred_at: tuple[datetime, ...] = Field(default=(), alias="acceptedOccurredAt")
    truncated: bool = False


class AgentProgressAcceptance(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    state: AgentProgressSequenceState
    duplicate: bool = False


def accept_progress_frame(
    state: AgentProgressSequenceState,
    frame: AgentProgressFrame,
    *,
    limits: AgentProgressLimits | None = None,
) -> AgentProgressAcceptance:
    """Validate idempotency, bounds and non-reopening segment semantics."""

    effective_limits = limits or AgentProgressLimits()
    if state.attempt_session_id is not None and (
        state.attempt_session_id != frame.attempt_session_id or state.attempt != frame.attempt
    ):
        raise ValueError("progress frame belongs to a different session attempt")

    existing = next(
        (
            item
            for item in state.accepted_sources
            if item.source_id == frame.source_id and item.source_sequence == frame.source_sequence
        ),
        None,
    )
    if existing is not None:
        if existing.fingerprint != frame.fingerprint:
            raise ValueError("progress source sequence was reused with different content")
        return AgentProgressAcceptance(state=state, duplicate=True)

    if state.truncated:
        raise ValueError("progress stream was truncated")

    if len(frame.model_dump_json(by_alias=True).encode()) > effective_limits.max_frame_bytes:
        raise AgentProgressLimitExceeded("progress frame exceeds maxFrameBytes")

    prior_sequence = max(
        (
            item.source_sequence
            for item in state.accepted_sources
            if item.source_id == frame.source_id
        ),
        default=0,
    )
    if frame.source_sequence != prior_sequence + 1:
        raise ValueError("progress sourceSequence must be contiguous for each sourceId")
    is_truncated = frame.status is AgentProgressStatus.TRUNCATED
    if (
        effective_limits.max_frames_per_session is not None
        and state.accepted_frame_count >= effective_limits.max_frames_per_session
        and not is_truncated
    ):
        raise AgentProgressLimitExceeded("progress session exceeds maxFramesPerSession")

    if state.accepted_occurred_at and frame.occurred_at < state.accepted_occurred_at[-1]:
        raise ValueError("progress frames must remain in chronological order")
    if effective_limits.max_frames_per_second is not None:
        window_start = frame.occurred_at - timedelta(seconds=1)
        recent_count = sum(item >= window_start for item in state.accepted_occurred_at)
        if recent_count >= effective_limits.max_frames_per_second and not is_truncated:
            raise AgentProgressLimitExceeded("progress session exceeds maxFramesPerSecond")

    closed = set(state.closed_segment_ids)
    active = state.active_segment_id
    active_count = state.active_segment_frame_count
    segment_count = state.segment_count
    segment = frame.segment_id
    if segment is None:
        if active is not None:
            closed.add(active)
        active = None
        active_count = 0
    else:
        if segment in closed:
            raise ValueError("closed progress segment cannot receive another frame")
        if active != segment:
            if frame.status is AgentProgressStatus.DELTA:
                raise ValueError("a new progress segment must begin with STARTED")
            if active is not None:
                closed.add(active)
            active = segment
            active_count = 0
            segment_count += 1
            if (
                effective_limits.max_segments_per_session is not None
                and segment_count > effective_limits.max_segments_per_session
                and not is_truncated
            ):
                raise AgentProgressLimitExceeded("progress session exceeds maxSegmentsPerSession")
        active_count += 1
        if (
            effective_limits.max_frames_per_segment is not None
            and active_count > effective_limits.max_frames_per_segment
            and not is_truncated
        ):
            raise AgentProgressLimitExceeded("progress segment exceeds maxFramesPerSegment")
        if frame.status.value in _TERMINAL_PROGRESS_STATUSES:
            closed.add(segment)
            active = None
            active_count = 0

    accepted = AgentProgressSourceFrame(
        sourceId=frame.source_id,
        sourceSequence=frame.source_sequence,
        fingerprint=frame.fingerprint,
    )
    next_state = AgentProgressSequenceState(
        attemptSessionId=frame.attempt_session_id,
        attempt=frame.attempt,
        acceptedSources=(*state.accepted_sources, accepted),
        activeSegmentId=active,
        activeSegmentFrameCount=active_count,
        closedSegmentIds=frozenset(closed),
        segmentCount=segment_count,
        acceptedFrameCount=state.accepted_frame_count + 1,
        acceptedOccurredAt=(*state.accepted_occurred_at, frame.occurred_at),
        truncated=is_truncated,
    )
    return AgentProgressAcceptance(state=next_state)


def make_truncated_progress_frame(
    frame: AgentProgressFrame,
    state: AgentProgressSequenceState,
) -> AgentProgressFrame:
    """Create the historical deterministic marker used before EPIC-834."""

    segment_id = state.active_segment_id or frame.segment_id
    if segment_id in state.closed_segment_ids:
        segment_id = None
    if segment_id is None:
        segment_id = uuid5(
            NAMESPACE_URL,
            f"amesh-progress-truncated:{frame.attempt_session_id}",
        )
    return AgentProgressFrame(
        attemptSessionId=frame.attempt_session_id,
        attempt=frame.attempt,
        turn=frame.turn,
        activity=AgentProgressActivity.TERMINAL,
        status=AgentProgressStatus.TRUNCATED,
        activityId="progress.truncated",
        segmentId=segment_id,
        sourceId=f"amesh:progress-limit:{frame.attempt_session_id}",
        sourceSequence=1,
        occurredAt=frame.occurred_at,
        detail=AgentStatusDetail(
            code="progress.truncated",
            label="Progress limit reached",
        ),
    )


def close_progress_segment(state: AgentProgressSequenceState) -> AgentProgressSequenceState:
    """Close the active segment when any canonical non-progress work intervenes."""

    if state.active_segment_id is None:
        return state
    return state.model_copy(
        update={
            "active_segment_id": None,
            "active_segment_frame_count": 0,
            "closed_segment_ids": frozenset({*state.closed_segment_ids, state.active_segment_id}),
        }
    )


class AgentSessionEventCursor(BaseModel):
    """Opaque logical-session cursor spanning attempt-local journal indexes."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.agent-session-cursor/v1"] = Field(
        default="amesh.agent-session-cursor/v1",
        alias="schemaVersion",
    )
    service_session_id: UUID = Field(alias="serviceSessionId")
    attempt_session_id: UUID | None = Field(default=None, alias="attemptSessionId")
    attempt: int = Field(ge=0)
    event_index: int = Field(alias="eventIndex", ge=0)

    @model_validator(mode="after")
    def validate_position(self) -> AgentSessionEventCursor:
        if self.attempt == 0 and (self.attempt_session_id is not None or self.event_index != 0):
            raise ValueError(
                "initial cursor must use attempt 0, eventIndex 0 and no attemptSessionId"
            )
        if self.attempt > 0 and self.attempt_session_id is None:
            raise ValueError("attempt cursor requires attemptSessionId")
        return self

    @property
    def position(self) -> tuple[int, int]:
        return self.attempt, self.event_index

    def encode(self) -> str:
        encoded = (
            base64.urlsafe_b64encode(self.model_dump_json(by_alias=True).encode())
            .decode()
            .rstrip("=")
        )
        return _CURSOR_PREFIX + encoded

    @classmethod
    def decode(cls, token: str) -> AgentSessionEventCursor:
        try:
            if not token.startswith(_CURSOR_PREFIX) or len(token) > 512:
                raise ValueError
            encoded = token.removeprefix(_CURSOR_PREFIX)
            padding = "=" * (-len(encoded) % 4)
            raw = base64.b64decode(encoded + padding, altchars=b"-_", validate=True)
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError
            return cls.model_validate(payload)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid agent-session cursor") from exc

    def require_service_session(self, service_session_id: UUID) -> None:
        if self.service_session_id != service_session_id:
            raise ValueError("agent-session cursor belongs to a different service session")


class AgentProgressEvent(BaseModel):
    """Safe progress frame after acceptance into the canonical journal."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.agent-progress-event/v1"] = Field(
        default="amesh.agent-progress-event/v1",
        alias="schemaVersion",
    )
    service_session_id: UUID = Field(alias="serviceSessionId")
    event_id: UUID = Field(alias="eventId")
    event_index: int = Field(alias="eventIndex", ge=1)
    cursor: str = Field(min_length=1, max_length=512)
    accepted_at: datetime = Field(alias="acceptedAt")
    frame: AgentProgressFrame

    @field_validator("accepted_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("acceptedAt must include a time-zone offset")
        return value


_LIFECYCLE_PROGRESS: dict[
    str,
    tuple[AgentProgressActivity, AgentProgressStatus, str, str],
] = {
    "session.started": (
        AgentProgressActivity.MODEL,
        AgentProgressStatus.STARTED,
        "session.started",
        "Agent session started",
    ),
    "context.projected": (
        AgentProgressActivity.MODEL,
        AgentProgressStatus.STARTED,
        "model.context_projected",
        "Model context prepared",
    ),
    "context.compacted": (
        AgentProgressActivity.MODEL,
        AgentProgressStatus.STARTED,
        "model.context_compacted",
        "Model context compacted",
    ),
    "model.response": (
        AgentProgressActivity.MODEL,
        AgentProgressStatus.COMPLETED,
        "model.completed",
        "Model response completed",
    ),
    "policy.authorized": (
        AgentProgressActivity.POLICY,
        AgentProgressStatus.COMPLETED,
        "policy.authorized",
        "Policy authorized the action",
    ),
    "release.approved": (
        AgentProgressActivity.APPROVAL,
        AgentProgressStatus.COMPLETED,
        "approval.completed",
        "Release approval completed",
    ),
    "tool.result": (
        AgentProgressActivity.TOOL,
        AgentProgressStatus.COMPLETED,
        "tool.completed",
        "Tool work completed",
    ),
    "evaluation.completed": (
        AgentProgressActivity.VALIDATION,
        AgentProgressStatus.COMPLETED,
        "validation.completed",
        "Output evaluation completed",
    ),
    "memory.written": (
        AgentProgressActivity.ARTIFACT,
        AgentProgressStatus.COMPLETED,
        "artifact.memory_written",
        "Session memory written",
    ),
    "output.rejected": (
        AgentProgressActivity.OUTPUT,
        AgentProgressStatus.FAILED,
        "output.rejected",
        "Output validation rejected the result",
    ),
    "output.accepted": (
        AgentProgressActivity.TERMINAL,
        AgentProgressStatus.COMPLETED,
        "session.succeeded",
        "Agent session succeeded",
    ),
    "session.completed": (
        AgentProgressActivity.TERMINAL,
        AgentProgressStatus.COMPLETED,
        "session.succeeded",
        "Agent session succeeded",
    ),
    "session.failed": (
        AgentProgressActivity.TERMINAL,
        AgentProgressStatus.FAILED,
        "session.failed",
        "Agent session failed",
    ),
    "session.cancelled": (
        AgentProgressActivity.TERMINAL,
        AgentProgressStatus.CANCELLED,
        "session.cancelled",
        "Agent session was cancelled",
    ),
}


def project_agent_session_lifecycle_frame(
    *,
    attempt_session_id: UUID,
    attempt: int,
    event_id: UUID,
    event_index: int,
    event_type: str,
    payload: Mapping[str, object],
    occurred_at: datetime,
) -> AgentProgressFrame:
    """Project a journal lifecycle row without forwarding its generic payload."""

    activity, status, code, label = _LIFECYCLE_PROGRESS.get(
        event_type,
        (
            AgentProgressActivity.POLICY,
            AgentProgressStatus.COMPLETED,
            "lifecycle.recorded",
            "Session lifecycle event recorded",
        ),
    )
    if event_type == "output.rejected" and payload.get("repairScheduled") is False:
        activity = AgentProgressActivity.TERMINAL
        code = "session.failed"
        label = "Agent session failed output validation"
    raw_turn = payload.get("turn")
    turn = raw_turn if isinstance(raw_turn, int) and not isinstance(raw_turn, bool) else None
    if turn is not None and turn < 1:
        turn = None
    event_identity = f"journal:{event_id}"
    return AgentProgressFrame(
        attemptSessionId=attempt_session_id,
        attempt=attempt,
        turn=turn,
        activity=activity,
        status=status,
        activityId=event_identity,
        sourceId=f"journal:{attempt_session_id}",
        sourceSequence=event_index,
        occurredAt=occurred_at,
        detail=AgentStatusDetail(code=code, label=label),
    )


__all__ = [
    "AgentProgressAcceptance",
    "AgentProgressActivity",
    "AgentProgressDetail",
    "AgentProgressEvent",
    "AgentProgressFrame",
    "AgentProgressLimitExceeded",
    "AgentProgressLimits",
    "AgentProgressSequenceState",
    "AgentProgressSourceFrame",
    "AgentProgressStatus",
    "AgentPublicSummaryDetail",
    "AgentSessionEventCursor",
    "AgentStatusDetail",
    "accept_progress_frame",
    "close_progress_segment",
    "make_truncated_progress_frame",
    "project_agent_session_lifecycle_frame",
]
