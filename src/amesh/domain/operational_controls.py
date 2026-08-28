from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .identity import new_runtime_id


class AnnouncementSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AnnouncementAudience(StrEnum):
    INSTANCE = "INSTANCE"
    TENANT = "TENANT"
    NAMESPACE = "NAMESPACE"


class OperationalControlKind(StrEnum):
    MAINTENANCE = "MAINTENANCE"
    KILL_SWITCH = "KILL_SWITCH"


class OperationalControlScope(StrEnum):
    INSTANCE = "INSTANCE"
    TENANT = "TENANT"
    NAMESPACE = "NAMESPACE"
    FLOW = "FLOW"
    PLUGIN = "PLUGIN"
    RUNNER = "RUNNER"


class OperationalBoundary(StrEnum):
    AUTHORING = "AUTHORING"
    NEW_EXECUTIONS = "NEW_EXECUTIONS"
    TRIGGERS = "TRIGGERS"
    API_WRITES = "API_WRITES"
    WORKER_DISPATCH = "WORKER_DISPATCH"


class RunningWorkPolicy(StrEnum):
    CONTINUE = "CONTINUE"
    DRAIN = "DRAIN"
    CANCEL = "CANCEL"


class OperationalControlState(StrEnum):
    ACTIVE = "ACTIVE"
    BYPASSED = "BYPASSED"
    DEACTIVATED = "DEACTIVATED"
    EXPIRED = "EXPIRED"


class OperationalControlActionKind(StrEnum):
    EXTEND = "EXTEND"
    BYPASS = "BYPASS"
    DEACTIVATE = "DEACTIVATE"


class AnnouncementCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=4000)
    severity: AnnouncementSeverity = AnnouncementSeverity.INFO
    audience: AnnouncementAudience = AnnouncementAudience.TENANT
    namespace: str | None = Field(default=None, max_length=255)
    starts_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        alias="startsAt",
    )
    expires_at: datetime = Field(alias="expiresAt")

    @model_validator(mode="after")
    def validate_window_and_audience(self) -> AnnouncementCreateRequest:
        if self.starts_at.tzinfo is None or self.expires_at.tzinfo is None:
            raise ValueError("announcement timestamps must be timezone-aware")
        if self.expires_at <= self.starts_at:
            raise ValueError("announcement expiry must be after its start")
        if self.audience is AnnouncementAudience.NAMESPACE and not self.namespace:
            raise ValueError("namespace audience requires a namespace")
        if self.audience is not AnnouncementAudience.NAMESPACE and self.namespace is not None:
            raise ValueError("only namespace announcements can declare a namespace")
        return self


class Announcement(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    announcement_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    tenant_id: str | None = Field(default=None, alias="tenantId")
    title: str
    message: str
    severity: AnnouncementSeverity
    audience: AnnouncementAudience
    namespace: str | None = None
    starts_at: datetime = Field(alias="startsAt")
    expires_at: datetime = Field(alias="expiresAt")
    active: bool
    version: int = Field(ge=1)
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class OperationalControlCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    kind: OperationalControlKind
    name: str = Field(min_length=1, max_length=200)
    scope: OperationalControlScope
    namespace: str | None = Field(default=None, max_length=255)
    flow_id: str | None = Field(default=None, alias="flowId", max_length=255)
    plugin_id: str | None = Field(default=None, alias="pluginId", max_length=255)
    runner_id: str | None = Field(default=None, alias="runnerId", max_length=255)
    boundaries: tuple[OperationalBoundary, ...] = Field(min_length=1)
    running_work_policy: RunningWorkPolicy = Field(
        default=RunningWorkPolicy.DRAIN,
        alias="runningWorkPolicy",
    )
    reason: str = Field(min_length=3, max_length=4000)
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    review_at: datetime | None = Field(default=None, alias="reviewAt")

    @model_validator(mode="after")
    def validate_scope_and_review(self) -> OperationalControlCreateRequest:
        fields = {
            OperationalControlScope.INSTANCE: (),
            OperationalControlScope.TENANT: (),
            OperationalControlScope.NAMESPACE: ("namespace",),
            OperationalControlScope.FLOW: ("namespace", "flow_id"),
            OperationalControlScope.PLUGIN: ("plugin_id",),
            OperationalControlScope.RUNNER: ("runner_id",),
        }
        required = fields[self.scope]
        declared = {
            "namespace": self.namespace,
            "flow_id": self.flow_id,
            "plugin_id": self.plugin_id,
            "runner_id": self.runner_id,
        }
        if any(not declared[name] for name in required):
            raise ValueError(f"{self.scope.value.lower()} control target is incomplete")
        if any(value is not None for name, value in declared.items() if name not in required):
            raise ValueError(f"{self.scope.value.lower()} control has unrelated target fields")
        now = datetime.now(UTC)
        if self.expires_at is None and self.review_at is None:
            raise ValueError("emergency controls require an expiry or review time")
        for value in (self.expires_at, self.review_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("control timestamps must be timezone-aware")
            if value is not None and value <= now:
                raise ValueError("control expiry and review times must be in the future")
        if len(set(self.boundaries)) != len(self.boundaries):
            raise ValueError("control boundaries must be unique")
        return self


class OperationalControlActionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    action: OperationalControlActionKind
    reason: str = Field(min_length=3, max_length=4000)
    expected_version: int = Field(alias="expectedVersion", ge=1)
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    review_at: datetime | None = Field(default=None, alias="reviewAt")
    bypass_until: datetime | None = Field(default=None, alias="bypassUntil")

    @model_validator(mode="after")
    def validate_action(self) -> OperationalControlActionRequest:
        now = datetime.now(UTC)
        if self.action is OperationalControlActionKind.EXTEND:
            if self.expires_at is None and self.review_at is None:
                raise ValueError("extension requires an expiry or review time")
            if self.bypass_until is not None:
                raise ValueError("extension cannot include bypassUntil")
        elif self.action is OperationalControlActionKind.BYPASS:
            if self.bypass_until is None:
                raise ValueError("bypass requires bypassUntil")
            if self.expires_at is not None or self.review_at is not None:
                raise ValueError("bypass cannot extend the control")
        elif any(
            value is not None for value in (self.expires_at, self.review_at, self.bypass_until)
        ):
            raise ValueError("deactivation does not accept time fields")
        for value in (self.expires_at, self.review_at, self.bypass_until):
            if value is not None and value.tzinfo is None:
                raise ValueError("control action timestamps must be timezone-aware")
            if value is not None and value <= now:
                raise ValueError("control action timestamps must be in the future")
        return self


class OperationalControlAcknowledgement(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    component_id: str = Field(alias="componentId")
    component_role: str = Field(alias="componentRole")
    control_version: int = Field(alias="controlVersion", ge=1)
    acknowledged_at: datetime = Field(alias="acknowledgedAt")


class OperationalControl(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    control_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    tenant_id: str | None = Field(default=None, alias="tenantId")
    kind: OperationalControlKind
    name: str
    scope: OperationalControlScope
    namespace: str | None = None
    flow_id: str | None = Field(default=None, alias="flowId")
    plugin_id: str | None = Field(default=None, alias="pluginId")
    runner_id: str | None = Field(default=None, alias="runnerId")
    boundaries: tuple[OperationalBoundary, ...]
    running_work_policy: RunningWorkPolicy = Field(alias="runningWorkPolicy")
    reason: str
    state: OperationalControlState
    version: int = Field(ge=1)
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    review_at: datetime | None = Field(default=None, alias="reviewAt")
    bypass_until: datetime | None = Field(default=None, alias="bypassUntil")
    bypass_reason: str | None = Field(default=None, alias="bypassReason")
    created_by: str = Field(alias="createdBy")
    updated_by: str = Field(alias="updatedBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    acknowledgements: tuple[OperationalControlAcknowledgement, ...] = ()


class OperationalControlDecision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    blocked: bool
    boundary: OperationalBoundary
    running_work_policy: RunningWorkPolicy = Field(alias="runningWorkPolicy")
    controls: tuple[OperationalControl, ...] = ()


class OperationalControlEvent(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    event_id: UUID = Field(alias="eventId")
    control_id: UUID = Field(alias="controlId")
    action: str
    actor_id: str = Field(alias="actorId")
    reason: str
    evidence: dict[str, object]
    occurred_at: datetime = Field(alias="occurredAt")
