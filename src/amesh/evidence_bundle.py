"""Canonical, bounded execution evidence bundles.

This module is deliberately an adapter-free contract.  A durable repository can
persist :class:`EvidenceBundle` values and a REST, CLI or SDK surface can use
the same :class:`EvidenceBundleStore` authorization and pagination boundary.
Secrets and hidden model reasoning are removed while records are constructed;
provider continuation tokens remain private to the continuation object.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar, Protocol, TypeVar, cast
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

from amesh.domain import canonical_hash, canonical_json

EVIDENCE_SCHEMA_VERSION = "1.0"
_REDACTED = "[REDACTED]"
_OMITTED = "[OMITTED]"
_SECRET_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "authorization",
        "credential",
        "password",
        "secret",
        "token",
        "access_token",
        "refresh_token",
        "client_secret",
    }
)
_HIDDEN_REASONING_KEYS = frozenset(
    {
        "chain_of_thought",
        "chainofthought",
        "hidden_reasoning",
        "hiddenreasoning",
        "private_reasoning",
        "privaterationale",
        "model_rationale",
        "modelrationale",
        "private_chain_of_thought",
        "privatechainofthought",
        "reasoning",
        "thoughts",
        "scratchpad",
    }
)


class EvidenceBundleError(ValueError):
    """Base class for invalid or conflicting evidence."""


class EvidenceConflictError(EvidenceBundleError):
    """Raised when an immutable bundle identity is reused with different data."""


class EvidenceIntegrityError(EvidenceBundleError):
    """Raised when content-addressed evidence does not match its digest."""


class EvidenceAccessDenied(PermissionError):
    """Raised when a caller is not authorized for a tenant's evidence."""


class EvidenceNotFoundError(LookupError):
    """The requested execution has no evidence bundle."""


class EvidenceUnavailableError(RuntimeError):
    """The evidence repository or external object store cannot be read."""


class EvidencePresence(StrEnum):
    """Explicit section semantics; an empty value is not an outage."""

    PRESENT = "present"
    ABSENT = "absent"
    UNAVAILABLE = "unavailable"


class CostState(StrEnum):
    """Cost has a deliberate state rather than an ambiguous null amount."""

    PRICED = "priced"
    UNPRICED = "unpriced"
    UNAVAILABLE = "unavailable"


class EvidenceRecord(BaseModel):
    """One immutable, ordered piece of execution evidence."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    record_id: UUID | str = Field(alias="recordId")
    kind: str = Field(min_length=1, max_length=128)
    sequence: int = Field(default=0, ge=0)
    correlation_id: UUID | str = Field(alias="correlationId")
    occurred_at: datetime = Field(alias="occurredAt")
    schema_digest: str | None = Field(default=None, alias="schemaDigest")
    availability: EvidencePresence = EvidencePresence.PRESENT
    payload: Mapping[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def redact_input(cls, value: Any) -> Any:
        if isinstance(value, Mapping):
            data = dict(value)
            data["payload"] = _redact(data.get("payload", {}))
            return data
        return value

    @model_validator(mode="after")
    def validate_timestamp(self) -> EvidenceRecord:
        if self.occurred_at.tzinfo is None:
            raise ValueError("evidence timestamps must be timezone-aware")
        return self


class EvidencePin(BaseModel):
    """An exact client/provider/model/tool/control revision used by an execution."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    pin_id: str = Field(alias="pinId", min_length=1)
    category: str = Field(min_length=1, max_length=64)
    subject: str = Field(min_length=1, max_length=255)
    revision: str = Field(min_length=1, max_length=255)
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    schema_digest: str | None = Field(default=None, alias="schemaDigest")


class PromptCacheUsage(BaseModel):
    """Prompt-cache evidence kept separate from task cache and invocation replay."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    state: EvidencePresence = EvidencePresence.UNAVAILABLE
    read_tokens: int | None = Field(default=None, alias="readTokens", ge=0)
    write_tokens: int | None = Field(default=None, alias="writeTokens", ge=0)
    hit_ratio: Decimal | None = Field(default=None, alias="hitRatio", ge=0, le=1)
    cost_effect_usd: Decimal | None = Field(default=None, alias="costEffectUsd")

    @model_validator(mode="after")
    def validate_state(self) -> PromptCacheUsage:
        values = (self.read_tokens, self.write_tokens, self.hit_ratio, self.cost_effect_usd)
        if self.state is EvidencePresence.PRESENT and all(item is None for item in values):
            raise ValueError("present prompt-cache usage requires at least one value")
        if self.state is not EvidencePresence.PRESENT and any(item is not None for item in values):
            raise ValueError("absent or unavailable prompt-cache usage cannot include values")
        return self


class TokenUsage(BaseModel):
    """Usage with explicit absence semantics and stable correlation."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    usage_id: str = Field(alias="usageId", min_length=1)
    correlation_id: UUID | str = Field(alias="correlationId")
    state: EvidencePresence = EvidencePresence.PRESENT
    input_tokens: int | None = Field(default=None, alias="inputTokens", ge=0)
    output_tokens: int | None = Field(default=None, alias="outputTokens", ge=0)
    total_tokens: int | None = Field(default=None, alias="totalTokens", ge=0)
    prompt_cache: PromptCacheUsage = Field(
        default_factory=PromptCacheUsage,
        alias="promptCache",
    )

    @model_validator(mode="after")
    def validate_state(self) -> TokenUsage:
        if self.state is EvidencePresence.PRESENT and all(
            item is None for item in (self.input_tokens, self.output_tokens, self.total_tokens)
        ):
            raise ValueError("present token usage requires at least one token count")
        if self.state is not EvidencePresence.PRESENT and any(
            item is not None for item in (self.input_tokens, self.output_tokens, self.total_tokens)
        ):
            raise ValueError("absent or unavailable token usage cannot include token counts")
        return self


class EvidenceCost(BaseModel):
    """Provider-neutral cost state; only priced values carry an amount."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    cost_id: str = Field(alias="costId", min_length=1)
    correlation_id: UUID | str = Field(alias="correlationId")
    state: CostState
    amount: str | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)

    @model_validator(mode="after")
    def validate_state(self) -> EvidenceCost:
        if self.state is CostState.PRICED and (self.amount is None or self.currency is None):
            raise ValueError("priced cost requires amount and currency")
        if self.state is not CostState.PRICED and self.amount is not None:
            raise ValueError("unpriced or unavailable cost cannot include amount")
        return self


class ProtectedContinuation(BaseModel):
    """Provider continuation metadata whose opaque token is never serializable."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    provider_id: str = Field(alias="providerId", min_length=1)
    revision: str = Field(min_length=1)
    token_digest: str = Field(alias="tokenDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    _token: str = PrivateAttr(default="")

    @classmethod
    def create(cls, provider_id: str, revision: str, token: str) -> ProtectedContinuation:
        if not token:
            raise ValueError("continuation token cannot be empty")
        value = cls(
            providerId=provider_id,
            revision=revision,
            tokenDigest="sha256:" + hashlib.sha256(token.encode("utf-8")).hexdigest(),
        )
        object.__setattr__(value, "_token", token)
        return value

    def token_for_provider(self, provider_id: str, revision: str) -> str:
        if (provider_id, revision) != (self.provider_id, self.revision):
            raise EvidenceAccessDenied("continuation is pinned to a different provider revision")
        if not self._token:
            raise EvidenceUnavailableError(
                "opaque continuation token is unavailable for resumption"
            )
        return self._token

    def public_metadata(self) -> dict[str, str]:
        return {
            "providerId": self.provider_id,
            "revision": self.revision,
            "tokenDigest": self.token_digest,
        }

    def __repr__(self) -> str:
        return (
            f"ProtectedContinuation(provider_id={self.provider_id!r}, revision={self.revision!r})"
        )


_RECORD_SECTIONS: tuple[str, ...] = (
    "decisions",
    "trace",
    "inputs",
    "outputs",
    "task_attempts",
    "agent_sessions",
    "external_invocations",
    "state_transitions",
    "logs",
    "metrics",
    "files",
    "errors",
    "approvals",
    "interventions",
    "controls",
)
_SECTION_ALIASES: dict[str, str] = {
    "task_attempts": "taskAttempts",
    "agent_sessions": "agentSessions",
    "external_invocations": "externalInvocations",
    "state_transitions": "stateTransitions",
    "token_usage": "tokenUsage",
    "section_status": "sectionStatus",
}


class EvidenceBundle(BaseModel):
    """Versioned canonical projection of one execution's evidence."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: str = Field(default=EVIDENCE_SCHEMA_VERSION, alias="schemaVersion")
    execution_id: UUID | str = Field(alias="executionId")
    tenant_id: str = Field(alias="tenantId", min_length=1)
    correlation_id: UUID | str = Field(alias="correlationId")
    created_at: datetime = Field(alias="createdAt")
    pins: tuple[EvidencePin, ...] = ()
    decisions: tuple[EvidenceRecord, ...] = ()
    trace: tuple[EvidenceRecord, ...] = ()
    inputs: tuple[EvidenceRecord, ...] = ()
    outputs: tuple[EvidenceRecord, ...] = ()
    task_attempts: tuple[EvidenceRecord, ...] = Field(default=(), alias="taskAttempts")
    agent_sessions: tuple[EvidenceRecord, ...] = Field(default=(), alias="agentSessions")
    external_invocations: tuple[EvidenceRecord, ...] = Field(
        default=(), alias="externalInvocations"
    )
    state_transitions: tuple[EvidenceRecord, ...] = Field(default=(), alias="stateTransitions")
    logs: tuple[EvidenceRecord, ...] = ()
    metrics: tuple[EvidenceRecord, ...] = ()
    files: tuple[EvidenceRecord, ...] = ()
    errors: tuple[EvidenceRecord, ...] = ()
    approvals: tuple[EvidenceRecord, ...] = ()
    interventions: tuple[EvidenceRecord, ...] = ()
    controls: tuple[EvidenceRecord, ...] = ()
    token_usage: tuple[TokenUsage, ...] = Field(default=(), alias="tokenUsage")
    costs: tuple[EvidenceCost, ...] = ()
    continuations: tuple[ProtectedContinuation, ...] = ()
    section_status: Mapping[str, EvidencePresence] = Field(
        default_factory=dict, alias="sectionStatus"
    )
    bundle_digest: str | None = Field(default=None, alias="bundleDigest")

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if not isinstance(value, Mapping):
            return value
        data = dict(value)
        for name in _RECORD_SECTIONS:
            alias = _SECTION_ALIASES.get(name, name)
            if alias in data:
                data[alias] = tuple(sorted(data[alias], key=_record_key))
                if alias != name:
                    data.pop(name, None)
            elif name in data:
                data[alias] = tuple(sorted(data[name], key=_record_key))
                if alias != name:
                    data.pop(name, None)
        for name in ("pins", "token_usage", "costs", "continuations"):
            alias = _SECTION_ALIASES.get(name, name)
            if alias in data:
                data[alias] = tuple(sorted(data[alias], key=_stable_item_key))
                if alias != name:
                    data.pop(name, None)
            elif name in data:
                data[alias] = tuple(sorted(data[name], key=_stable_item_key))
                if alias != name:
                    data.pop(name, None)
        status_value = data.get("sectionStatus", data.get("section_status", {}))
        statuses = dict(status_value)
        for name in (*_RECORD_SECTIONS, "pins", "token_usage", "costs", "continuations"):
            alias = _SECTION_ALIASES.get(name, name)
            values = data.get(alias, data.get(name, ()))
            if name not in statuses and alias not in statuses:
                statuses[name] = EvidencePresence.PRESENT if values else EvidencePresence.ABSENT
        data["sectionStatus"] = statuses
        return data

    @model_validator(mode="after")
    def validate_timestamp(self) -> EvidenceBundle:
        if self.created_at.tzinfo is None:
            raise ValueError("bundle timestamp must be timezone-aware")
        return self

    @property
    def digest(self) -> str:
        """Return the SHA-256 digest of the canonical bundle without its digest field."""

        return "sha256:" + canonical_hash(self._canonical_payload())

    def canonical_digest(self) -> str:
        return self.digest

    def verify(self) -> None:
        if self.bundle_digest is not None and self.bundle_digest != self.digest:
            raise EvidenceIntegrityError("evidence bundle digest mismatch")
        self.verify_schema()

    def verify_schema(self) -> None:
        if self.schema_version != EVIDENCE_SCHEMA_VERSION:
            raise EvidenceBundleError(
                f"unsupported evidence schema {self.schema_version!r}; expected {EVIDENCE_SCHEMA_VERSION!r}"
            )

    def sealed(self) -> EvidenceBundle:
        """Return an immutable copy carrying its computed digest."""

        return self.model_copy(update={"bundle_digest": self.digest})

    def externalize_large_fields(
        self,
        store: EvidenceObjectStore,
        *,
        max_inline_bytes: int = 64 * 1024,
    ) -> EvidenceBundle:
        if max_inline_bytes < 1:
            raise ValueError("max_inline_bytes must be positive")
        updates: dict[str, tuple[EvidenceRecord, ...]] = {}
        for section in _RECORD_SECTIONS:
            records: list[EvidenceRecord] = []
            for record in getattr(self, section):
                payload = _externalize(record.payload, store, max_inline_bytes)
                records.append(record.model_copy(update={"payload": payload}))
            updates[section] = tuple(records)
        return self.model_copy(update={**updates, "bundle_digest": None}).sealed()

    def verify_externalized_fields(self, store: EvidenceObjectStore) -> None:
        for section in _RECORD_SECTIONS:
            for record in getattr(self, section):
                _verify_external_refs(record.payload, store)

    def _canonical_payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        payload.pop("bundleDigest", None)
        return payload


class EvidenceObjectReference(BaseModel):
    """Content-addressed reference replacing an oversized inline value."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    uri: str
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    size_bytes: int = Field(alias="sizeBytes", ge=0)
    media_type: str = Field(default="application/json", alias="mediaType")


class EvidenceObjectStore(Protocol):
    """Minimal synchronous object-storage contract for externalized fields."""

    def put(
        self, content: bytes, *, media_type: str = "application/json"
    ) -> EvidenceObjectReference: ...

    def get(self, reference: EvidenceObjectReference) -> bytes: ...


class MemoryEvidenceObjectStore:
    """Reference implementation used by contract tests and local tooling."""

    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}
        self.available = True

    def put(
        self, content: bytes, *, media_type: str = "application/json"
    ) -> EvidenceObjectReference:
        if not self.available:
            raise EvidenceUnavailableError("evidence object store is unavailable")
        digest = "sha256:" + hashlib.sha256(content).hexdigest()
        existing = self._objects.get(digest)
        if existing is not None and existing != content:
            raise EvidenceConflictError("content-addressed object digest conflict")
        self._objects[digest] = content
        return EvidenceObjectReference(
            uri=f"memory://evidence/{digest[7:]}",
            digest=digest,
            sizeBytes=len(content),
            mediaType=media_type,
        )

    def get(self, reference: EvidenceObjectReference) -> bytes:
        if not self.available:
            raise EvidenceUnavailableError("evidence object store is unavailable")
        try:
            content = self._objects[reference.digest]
        except KeyError as exc:
            raise EvidenceNotFoundError("externalized evidence object is absent") from exc
        actual = "sha256:" + hashlib.sha256(content).hexdigest()
        if actual != reference.digest or len(content) != reference.size_bytes:
            raise EvidenceIntegrityError("externalized evidence object digest mismatch")
        return content

    def tamper(self, digest: str, content: bytes) -> None:
        """Test hook for corruption detection; production stores must reject this state."""

        if digest not in self._objects:
            raise EvidenceNotFoundError("externalized evidence object is absent")
        self._objects[digest] = content


class FilesystemEvidenceObjectStore:
    """Local-profile content-addressed object store with read-time integrity checks."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)

    def put(
        self, content: bytes, *, media_type: str = "application/json"
    ) -> EvidenceObjectReference:
        digest = "sha256:" + hashlib.sha256(content).hexdigest()
        destination = self._path_for(digest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if destination.read_bytes() != content:
                raise EvidenceConflictError("content-addressed object digest conflict")
        else:
            temporary = destination.with_suffix(".tmp")
            temporary.write_bytes(content)
            temporary.replace(destination)
        return EvidenceObjectReference(
            uri=f"file://{destination.as_posix()}",
            digest=digest,
            sizeBytes=len(content),
            mediaType=media_type,
        )

    def get(self, reference: EvidenceObjectReference) -> bytes:
        try:
            content = self._path_for(reference.digest).read_bytes()
        except FileNotFoundError as exc:
            raise EvidenceNotFoundError("externalized evidence object is absent") from exc
        actual = "sha256:" + hashlib.sha256(content).hexdigest()
        if actual != reference.digest or len(content) != reference.size_bytes:
            raise EvidenceIntegrityError("externalized evidence object digest mismatch")
        return content

    def _path_for(self, digest: str) -> Path:
        if not digest.startswith("sha256:") or len(digest) != 71:
            raise EvidenceIntegrityError("invalid content-addressed object digest")
        return self._root / digest[7:]


T = TypeVar("T")


class EvidencePage[T](BaseModel):
    """Bounded cursor page shared by REST, CLI and SDK retrieval surfaces."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    items: tuple[T, ...]
    next_cursor: str | None = Field(default=None, alias="nextCursor")
    limit: int = Field(ge=1)
    total: int = Field(ge=0)


class EvidenceReadResult(BaseModel):
    """Explicit read outcome so absent and unavailable are never conflated."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    state: EvidencePresence
    page: EvidencePage[EvidenceRecord] | None = None


class EvidenceBundleStore:
    """Tenant-scoped immutable bundle store with bounded cursor retrieval."""

    _MAX_PAGE: ClassVar[int] = 500

    def __init__(self) -> None:
        self._bundles: dict[tuple[str, str], EvidenceBundle] = {}
        self.available = True

    def put(self, bundle: EvidenceBundle) -> EvidenceBundle:
        if not self.available:
            raise EvidenceUnavailableError("evidence repository is unavailable")
        bundle.verify()
        sealed = bundle.sealed()
        key = (bundle.tenant_id, str(bundle.execution_id))
        existing = self._bundles.get(key)
        if existing is not None and existing.digest != sealed.digest:
            raise EvidenceConflictError("execution evidence conflicts with an immutable bundle")
        self._bundles[key] = existing or sealed
        return self._bundles[key]

    def get(
        self, execution_id: UUID | str, *, tenant_id: str, principal_tenant_id: str
    ) -> EvidenceBundle:
        self._authorize(tenant_id, principal_tenant_id)
        if not self.available:
            raise EvidenceUnavailableError("evidence repository is unavailable")
        try:
            return self._bundles[(tenant_id, str(execution_id))]
        except KeyError as exc:
            raise EvidenceNotFoundError("execution evidence is absent") from exc

    def page(
        self,
        execution_id: UUID | str,
        *,
        tenant_id: str,
        principal_tenant_id: str,
        section: str = "trace",
        cursor: str | None = None,
        limit: int = 100,
    ) -> EvidencePage[EvidenceRecord]:
        bundle = self.get(
            execution_id, tenant_id=tenant_id, principal_tenant_id=principal_tenant_id
        )
        if section not in _RECORD_SECTIONS:
            raise ValueError(f"unknown evidence section {section!r}")
        if not 1 <= limit <= self._MAX_PAGE:
            raise ValueError(f"limit must be between 1 and {self._MAX_PAGE}")
        records = getattr(bundle, section)
        start = _decode_cursor(cursor)
        if start > len(records):
            raise ValueError("cursor is outside evidence section")
        end = min(start + limit, len(records))
        return EvidencePage[EvidenceRecord](
            items=records[start:end],
            nextCursor=str(end) if end < len(records) else None,
            limit=limit,
            total=len(records),
        )

    def read_page(self, *args: Any, **kwargs: Any) -> EvidenceReadResult:
        try:
            return EvidenceReadResult(
                state=EvidencePresence.PRESENT, page=self.page(*args, **kwargs)
            )
        except EvidenceNotFoundError:
            return EvidenceReadResult(state=EvidencePresence.ABSENT)
        except EvidenceUnavailableError:
            return EvidenceReadResult(state=EvidencePresence.UNAVAILABLE)

    @staticmethod
    def _authorize(tenant_id: str, principal_tenant_id: str) -> None:
        if tenant_id != principal_tenant_id:
            raise EvidenceAccessDenied("evidence is not available to this tenant")


class CanonicalEvidenceBuilder:
    """Project persisted event records into the canonical bundle contract."""

    @staticmethod
    def from_events(
        execution_id: UUID | str,
        tenant_id: str,
        events: tuple[Any, ...] | list[Any],
        *,
        created_at: datetime,
        correlation_id: UUID | str | None = None,
        inputs: Mapping[str, Any] | None = None,
        outputs: Mapping[str, Any] | None = None,
    ) -> EvidenceBundle:
        if created_at.tzinfo is None:
            raise ValueError("bundle timestamp must be timezone-aware")
        fallback_correlation = correlation_id or str(execution_id)
        grouped: dict[str, Any] = {name: [] for name in _RECORD_SECTIONS}
        trace: list[EvidenceRecord] = []
        token_usage: list[TokenUsage] = []
        costs: list[EvidenceCost] = []
        for event in events:
            kind = _event_value(event, "kind")
            payload = _event_value(event, "payload")
            occurred_at = _event_value(event, "occurred_at")
            if not isinstance(occurred_at, datetime):
                raise ValueError("evidence event occurred_at must be a datetime")
            event_id = _event_value(event, "event_id")
            sequence = int(_event_value(event, "cursor") or 0)
            record = EvidenceRecord(
                recordId=event_id,
                kind=str(_event_value(event, "event_type") or kind),
                sequence=sequence,
                correlationId=fallback_correlation,
                occurredAt=occurred_at,
                payload=payload if isinstance(payload, Mapping) else {},
            )
            trace.append(record)
            section = _canonical_event_section(kind, record.kind)
            if section is not None:
                grouped[section].append(record)
            if _event_value(event, "task_run_id") is not None:
                grouped["task_attempts"].append(record)
            if section == "external_invocations":
                usage = _event_usage(payload)
                if usage is not None:
                    token_usage.append(
                        TokenUsage(
                            usageId=f"{event_id}:usage",
                            correlationId=fallback_correlation,
                            inputTokens=usage.get("inputTokens"),
                            outputTokens=usage.get("outputTokens"),
                            totalTokens=usage.get("totalTokens"),
                            promptCache=usage.get("promptCache", {}),
                        )
                    )
                costs.append(_event_cost(event_id, fallback_correlation, payload))
        grouped.pop("trace")
        if inputs is not None:
            grouped["inputs"] = [
                EvidenceRecord(
                    recordId=f"{execution_id}:inputs",
                    kind="execution.inputs",
                    sequence=0,
                    correlationId=fallback_correlation,
                    occurredAt=created_at,
                    payload=inputs,
                )
            ]
        if outputs is not None:
            grouped["outputs"] = [
                EvidenceRecord(
                    recordId=f"{execution_id}:outputs",
                    kind="execution.outputs",
                    sequence=0,
                    correlationId=fallback_correlation,
                    occurredAt=created_at,
                    payload=outputs,
                )
            ]
        return EvidenceBundle(
            executionId=execution_id,
            tenantId=tenant_id,
            correlationId=fallback_correlation,
            createdAt=created_at,
            trace=tuple(trace),
            tokenUsage=tuple(token_usage),
            costs=tuple(costs),
            **grouped,
        )


def _canonical_event_section(kind: Any, event_type: str) -> str | None:
    """Map persisted metadata kinds to the stable bundle section contract."""

    normalized_kind = str(kind).upper()
    direct = {
        "STATE": "state_transitions",
        "LOG": "logs",
        "METRIC": "metrics",
        "OUTPUT": "outputs",
        "ARTIFACT": "files",
        "AGENT": "agent_sessions",
        "MODEL": "external_invocations",
        "TOOL": "external_invocations",
        "ERROR": "errors",
        "APPROVAL": "approvals",
        "INTERVENTION": "interventions",
        "CONTROL": "controls",
        "DECISION": "decisions",
    }
    if normalized_kind != "STATE":
        return direct.get(normalized_kind)
    normalized_type = event_type.casefold().replace("_", ".")
    if normalized_type.startswith("agent."):
        return "agent_sessions"
    if normalized_type.startswith(("model.", "tool.", "mcp.")):
        return "external_invocations"
    for marker, section in (
        ("approval", "approvals"),
        ("intervention", "interventions"),
        ("control", "controls"),
        ("decision", "decisions"),
    ):
        if marker in normalized_type:
            return section
    if "error" in normalized_type or "failed" in normalized_type:
        return "errors"
    return direct[normalized_kind]


def _event_usage(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, Mapping):
        return None
    raw = payload.get("usageNormalized", payload.get("usage"))
    if not isinstance(raw, Mapping):
        return None
    values: dict[str, Any] = {}
    for public, candidates in (
        ("inputTokens", ("inputTokens", "input_tokens", "prompt_tokens")),
        ("outputTokens", ("outputTokens", "output_tokens", "completion_tokens")),
        ("totalTokens", ("totalTokens", "total_tokens")),
    ):
        value = next((raw.get(candidate) for candidate in candidates if candidate in raw), None)
        values[public] = value if isinstance(value, int) and not isinstance(value, bool) else None
    if not any(value is not None for value in values.values()):
        return None
    raw_cache = raw.get("promptCache", payload.get("promptCache"))
    if isinstance(raw_cache, Mapping) and raw_cache.get("state") == "reported":
        values["promptCache"] = {
            "state": EvidencePresence.PRESENT,
            "readTokens": raw_cache.get("readTokens"),
            "writeTokens": raw_cache.get("writeTokens"),
            "hitRatio": raw_cache.get("hitRatio"),
            "costEffectUsd": raw_cache.get("costEffectUsd"),
        }
    else:
        values["promptCache"] = {"state": EvidencePresence.UNAVAILABLE}
    return values


def _event_cost(event_id: Any, correlation_id: UUID | str, payload: Any) -> EvidenceCost:
    amount: Any = None
    if isinstance(payload, Mapping):
        amount = payload.get("costUsd")
        normalized = payload.get("costNormalized")
        if amount is None and isinstance(normalized, Mapping):
            amount = normalized.get("amountUsd", normalized.get("amount"))
    if amount is None:
        return EvidenceCost(
            costId=f"{event_id}:cost",
            correlationId=correlation_id,
            state=CostState.UNPRICED,
        )
    return EvidenceCost(
        costId=f"{event_id}:cost",
        correlationId=correlation_id,
        state=CostState.PRICED,
        amount=str(amount),
        currency="USD",
    )


def _event_value(event: Any, name: str) -> Any:
    if isinstance(event, Mapping):
        return event.get(name)
    return getattr(event, name, None)


def _record_key(record: EvidenceRecord | Mapping[str, Any]) -> tuple[int, str, str, str]:
    if isinstance(record, Mapping):
        sequence = record.get("sequence", 0)
        occurred_at = record.get("occurredAt", record.get("occurred_at"))
        kind = record.get("kind", "")
        record_id = record.get("recordId", record.get("record_id", ""))
    else:
        sequence = record.sequence
        occurred_at = record.occurred_at
        kind = record.kind
        record_id = record.record_id
    if isinstance(occurred_at, datetime):
        occurred = occurred_at.astimezone(UTC).isoformat()
    else:
        occurred = str(occurred_at or "")
    return (int(sequence), occurred, str(kind), str(record_id))


def _stable_item_key(value: Any) -> tuple[str, ...]:
    if isinstance(value, Mapping):
        data = value
        return (
            str(
                data.get(
                    "pinId", data.get("usageId", data.get("costId", data.get("providerId", "")))
                )
            ),
            str(data.get("category", data.get("correlationId", data.get("revision", "")))),
            str(data.get("subject", data.get("tokenDigest", ""))),
        )
    if isinstance(value, EvidencePin):
        return (value.pin_id, value.category, value.subject)
    if isinstance(value, TokenUsage):
        return (value.usage_id, str(value.correlation_id), "")
    if isinstance(value, EvidenceCost):
        return (value.cost_id, str(value.correlation_id), "")
    if isinstance(value, ProtectedContinuation):
        return (value.provider_id, value.revision, value.token_digest)
    return (str(value),)


def _decode_cursor(cursor: str | None) -> int:
    if cursor is None:
        return 0
    try:
        value = int(cursor)
    except ValueError as exc:
        raise ValueError("cursor must be a non-negative integer") from exc
    if value < 0:
        raise ValueError("cursor must be a non-negative integer")
    return value


def _redact(value: Any, *, key: str | None = None) -> Any:
    normalized = "" if key is None else key.casefold().replace("-", "_")
    compact = normalized.replace("_", "")
    if normalized in _HIDDEN_REASONING_KEYS or compact in _HIDDEN_REASONING_KEYS:
        return _OMITTED
    if normalized in _SECRET_KEYS or compact in {item.replace("_", "") for item in _SECRET_KEYS}:
        return _REDACTED
    if isinstance(value, BaseModel):
        return _redact(value.model_dump(mode="json", by_alias=True), key=key)
    if isinstance(value, Mapping):
        return {str(item_key): _redact(item, key=str(item_key)) for item_key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_redact(item) for item in value]
    if isinstance(value, str) and "-----BEGIN " in value:
        return _REDACTED
    return value


def _externalize(
    value: Mapping[str, Any], store: EvidenceObjectStore, limit: int
) -> Mapping[str, Any]:
    clean = cast(Mapping[str, Any], _redact(value))
    if len(canonical_json(clean)) <= limit:
        return clean
    content = canonical_json(clean)
    reference = store.put(content)
    return {"externalRef": reference.model_dump(mode="json", by_alias=True)}


def _verify_external_refs(value: Any, store: EvidenceObjectStore) -> None:
    if isinstance(value, Mapping):
        external = value.get("externalRef")
        if external is not None:
            reference = EvidenceObjectReference.model_validate(external)
            content = store.get(reference)
            try:
                json.loads(content)
            except json.JSONDecodeError as exc:
                raise EvidenceIntegrityError("externalized evidence is not valid JSON") from exc
            return
        for item in value.values():
            _verify_external_refs(item, store)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _verify_external_refs(item, store)


__all__ = [
    "EVIDENCE_SCHEMA_VERSION",
    "CanonicalEvidenceBuilder",
    "CostState",
    "EvidenceAccessDenied",
    "EvidenceBundle",
    "EvidenceBundleError",
    "EvidenceBundleStore",
    "EvidenceConflictError",
    "EvidenceCost",
    "EvidenceIntegrityError",
    "EvidenceNotFoundError",
    "EvidenceObjectReference",
    "EvidenceObjectStore",
    "EvidencePage",
    "EvidencePin",
    "EvidencePresence",
    "EvidenceReadResult",
    "EvidenceRecord",
    "EvidenceUnavailableError",
    "FilesystemEvidenceObjectStore",
    "MemoryEvidenceObjectStore",
    "PromptCacheUsage",
    "ProtectedContinuation",
    "TokenUsage",
]
