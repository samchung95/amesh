from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .identity import NaturalId


class AdmissionResourceType(StrEnum):
    EXECUTION = "EXECUTION"
    TASK = "TASK"


class AdmissionScope(StrEnum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    NAMESPACE = "NAMESPACE"
    FLOW = "FLOW"
    WORKER_GROUP = "WORKER_GROUP"
    KEY = "KEY"


class AdmissionBehavior(StrEnum):
    QUEUE = "QUEUE"
    CANCEL = "CANCEL"
    FAIL = "FAIL"
    REPLACE = "REPLACE"
    SKIP = "SKIP"


class AdmissionOutcome(StrEnum):
    ADMITTED = "ADMITTED"
    QUEUED = "QUEUED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    REPLACED = "REPLACED"
    SKIPPED = "SKIPPED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"


class ConcurrencyLimit(BaseModel):
    """A versioned DSL concurrency rule shared by flows and tasks."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    id: NaturalId
    scope: AdmissionScope
    limit: int = Field(ge=1, le=1_000_000)
    behavior: AdmissionBehavior = AdmissionBehavior.QUEUE
    key: str | None = Field(default=None, min_length=1, max_length=2048)
    worker_group: NaturalId | None = Field(default=None, alias="workerGroup")
    lease_seconds: int = Field(default=3600, alias="leaseSeconds", ge=1, le=604_800)

    @model_validator(mode="after")
    def require_scope_selector(self) -> ConcurrencyLimit:
        if self.scope is AdmissionScope.KEY and self.key is None:
            raise ValueError("KEY concurrency scope requires key")
        if self.scope is not AdmissionScope.KEY and self.key is not None:
            raise ValueError("concurrency key is only valid for KEY scope")
        if self.scope is AdmissionScope.WORKER_GROUP and self.worker_group is None:
            raise ValueError("WORKER_GROUP concurrency scope requires workerGroup")
        if self.scope is not AdmissionScope.WORKER_GROUP and self.worker_group is not None:
            raise ValueError("workerGroup is only valid for WORKER_GROUP scope")
        if self.behavior is AdmissionBehavior.REPLACE and self.scope is AdmissionScope.GLOBAL:
            raise ValueError("REPLACE is not allowed at GLOBAL scope")
        return self


class ResolvedAdmissionPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)

    policy_id: str
    scope: AdmissionScope
    bucket: str
    limit: int = Field(ge=1)
    behavior: AdmissionBehavior
    lease_seconds: int = Field(ge=1)


class AdmissionDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    request_id: UUID
    resource_type: AdmissionResourceType
    resource_id: UUID
    outcome: AdmissionOutcome
    reason: str
    limiting_policy_id: str | None = None
    limiting_scope: AdmissionScope | None = None
    limiting_bucket: str | None = None
    active_count: int = Field(default=0, ge=0)
    limit: int | None = Field(default=None, ge=1)
    queue_position: int | None = Field(default=None, ge=1)
    queue_age_seconds: float = Field(default=0, ge=0)
    priority: int = 0
    created_at: datetime
    admitted_at: datetime | None = None
    released_at: datetime | None = None
    replaced_resource_id: UUID | None = None


class AdmissionDiagnostics(BaseModel):
    model_config = ConfigDict(frozen=True)

    active_reservations: int = Field(ge=0)
    queued_requests: int = Field(ge=0)
    oldest_queue_age_seconds: float = Field(ge=0)
    pressure_by_policy: dict[str, int] = Field(default_factory=dict)


def resolve_admission_policies(
    limits: Iterable[ConcurrencyLimit],
    *,
    resource_type: AdmissionResourceType,
    tenant_id: str,
    namespace: str,
    flow_id: str,
    render_key: Callable[[str], Any],
) -> tuple[ResolvedAdmissionPolicy, ...]:
    """Resolve safe expression keys once before entering the admission transaction."""

    resolved: list[ResolvedAdmissionPolicy] = []
    for policy in limits:
        selector = {
            AdmissionScope.GLOBAL: "global",
            AdmissionScope.TENANT: tenant_id,
            AdmissionScope.NAMESPACE: f"{tenant_id}/{namespace}",
            AdmissionScope.FLOW: f"{tenant_id}/{namespace}/{flow_id}",
            AdmissionScope.WORKER_GROUP: f"{tenant_id}/{policy.worker_group}",
        }.get(policy.scope)
        if policy.scope is AdmissionScope.KEY:
            assert policy.key is not None
            rendered = render_key(policy.key)
            if isinstance(rendered, (dict, list, set, tuple)) or rendered is None:
                raise ValueError(f"concurrency policy {policy.id!r} key must render to a scalar")
            selector = f"{tenant_id}/{rendered}"
        assert selector is not None
        resolved.append(
            ResolvedAdmissionPolicy(
                policy_id=policy.id,
                scope=policy.scope,
                bucket=f"{resource_type.value}:{policy.scope.value}:{selector}",
                limit=policy.limit,
                behavior=policy.behavior,
                lease_seconds=policy.lease_seconds,
            )
        )
    return tuple(resolved)


def admission_policy_payload(
    policies: Iterable[ResolvedAdmissionPolicy],
) -> list[Mapping[str, Any]]:
    return [policy.model_dump(mode="json") for policy in policies]
