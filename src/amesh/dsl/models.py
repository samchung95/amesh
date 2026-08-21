from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Literal, cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from croniter import croniter
from pydantic import BaseModel, ConfigDict, Field, model_validator

from amesh.domain.admission import ConcurrencyLimit
from amesh.domain.identity import NamespaceId, NaturalId


class InputDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: NaturalId
    type: str = Field(min_length=1, max_length=256)
    required: bool = False
    default: Any | None = None
    description: str | None = None
    sensitive: bool = False


class TriggerDefinition(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: NaturalId
    type: str = Field(min_length=1, max_length=512)
    disabled: bool = False
    paused: bool = False
    cron: str | None = None
    interval: timedelta | None = None
    timezone: str = "UTC"
    start_at: datetime | None = Field(default=None, alias="start")
    end_at: datetime | None = Field(default=None, alias="end")
    condition: str | None = None
    misfire_policy: Literal["SKIP", "CATCH_UP", "COALESCE", "BACKFILL"] = Field(
        default="SKIP",
        alias="misfirePolicy",
    )
    misfire_grace_seconds: int = Field(default=60, ge=0, alias="misfireGraceSeconds")
    max_catch_up: int = Field(default=1000, ge=1, le=10_000, alias="maxCatchUp")

    @model_validator(mode="after")
    def validate_cron(self) -> TriggerDefinition:
        if self.type not in {"core.cron", "core.interval"}:
            return self
        if self.type == "core.cron":
            if self.cron is None:
                raise ValueError("core.cron trigger requires cron")
            if not croniter.is_valid(self.cron):
                raise ValueError("core.cron trigger has an invalid cron expression")
            if self.interval is not None:
                raise ValueError("core.cron trigger cannot declare interval")
        else:
            if self.interval is None or self.interval.total_seconds() <= 0:
                raise ValueError("core.interval trigger requires a positive interval")
            if self.cron is not None:
                raise ValueError("core.interval trigger cannot declare cron")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown trigger timezone {self.timezone!r}") from exc
        for field_name, value in (("start", self.start_at), ("end", self.end_at)):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError(f"trigger {field_name} must include a timezone")
        if self.start_at is not None and self.end_at is not None and self.start_at >= self.end_at:
            raise ValueError("trigger start must precede end")
        return self


class RetryPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    max_attempts: int = Field(default=1, ge=1, le=100, alias="maxAttempts")
    delay_seconds: float = Field(default=0, ge=0, alias="delaySeconds")
    backoff_multiplier: float = Field(default=1, ge=1, alias="backoffMultiplier")
    max_interval_seconds: float | None = Field(
        default=None,
        gt=0,
        alias="maxIntervalSeconds",
    )
    jitter_ratio: float = Field(default=0, ge=0, le=1, alias="jitterRatio")


class TaskResourceLimits(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    max_output_bytes: int = Field(default=1_048_576, alias="maxOutputBytes", ge=1)
    max_log_bytes: int = Field(default=1_048_576, alias="maxLogBytes", ge=1)
    max_artifact_bytes: int = Field(default=104_857_600, alias="maxArtifactBytes", ge=1)


class RunnableTaskContract(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    secret_scopes: tuple[str, ...] = Field(default=(), alias="secretScopes")
    files: dict[str, str] = Field(default_factory=dict)
    resource_limits: TaskResourceLimits = Field(
        default_factory=TaskResourceLimits,
        alias="resourceLimits",
    )


class TaskDefinition(BaseModel):
    # populate_by_name keeps snake_case spellings of aliased fields (depends_on,
    # run_if) from being silently swallowed into `extra` as inert plugin fields.
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: NaturalId
    type: str = Field(min_length=1, max_length=512)
    description: str | None = None
    depends_on: list[str] = Field(default_factory=list, alias="dependsOn")
    run_if: str | None = Field(default=None, alias="runIf")
    retry: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout_seconds: float | None = Field(default=None, gt=0, alias="timeoutSeconds")
    command: list[str] | None = None
    image: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)
    resources: dict[str, Any] = Field(default_factory=dict)
    concurrency: list[ConcurrencyLimit] = Field(default_factory=list)
    priority: int = Field(default=0, ge=-1000, le=1000)
    worker_group: NaturalId | None = Field(default=None, alias="workerGroup")
    contract: RunnableTaskContract = Field(default_factory=RunnableTaskContract)
    tasks: list[TaskDefinition] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def reject_conflicting_spellings(cls, data: Any) -> Any:
        # With populate_by_name, either spelling is accepted alone; supplying
        # both would let the alias win while the other rides along as an inert
        # extra field, so it is rejected outright.
        if isinstance(data, dict):
            for name, alias in (("depends_on", "dependsOn"), ("run_if", "runIf")):
                if name in data and alias in data:
                    raise ValueError(f"task cannot set both {alias!r} and {name!r}")
        return data

    @model_validator(mode="after")
    def validate_self_dependency(self) -> TaskDefinition:
        if self.id in self.depends_on:
            raise ValueError(f"task {self.id!r} cannot depend on itself")
        return self


class FlowDefinition(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    api_version: Literal["amesh.flow/v1"] = Field(default="amesh.flow/v1", alias="apiVersion")
    id: NaturalId
    namespace: NamespaceId
    description: str | None = None
    revision: int = Field(default=1, ge=1)
    disabled: bool = False
    system: bool = False
    timeout_seconds: float | None = Field(default=None, gt=0, alias="timeoutSeconds")
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    inputs: list[InputDefinition] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)
    concurrency: list[ConcurrencyLimit] = Field(default_factory=list)
    priority: int = Field(default=0, ge=-1000, le=1000)
    tasks: list[TaskDefinition] = Field(min_length=1)
    triggers: list[TriggerDefinition] = Field(default_factory=list)
    outputs: dict[str, Any] = Field(default_factory=dict)
    errors: list[TaskDefinition] = Field(default_factory=list)
    finally_tasks: list[TaskDefinition] = Field(default_factory=list, alias="finally")

    @model_validator(mode="after")
    def reject_unknown_core_fields(self) -> FlowDefinition:
        unknown = sorted(key for key in (self.model_extra or {}) if not key.startswith("x-"))
        if unknown:
            raise ValueError(
                "unknown core fields: "
                + ", ".join(repr(key) for key in unknown)
                + "; extension fields must start with 'x-'"
            )
        return self

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any) -> dict[str, Any]:
        schema = cast(dict[str, Any], handler(core_schema))
        schema["additionalProperties"] = False
        schema["patternProperties"] = {"^x-": {}}
        return schema


class SourcePosition(BaseModel):
    line: int = Field(ge=1)
    column: int = Field(ge=1)
    offset: int = Field(ge=0)


class SourceRange(BaseModel):
    start: SourcePosition
    end: SourcePosition


class ValidationIssue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    message: str
    path: str
    hint: str
    source_range: SourceRange | None = Field(default=None, alias="sourceRange")
    severity: str = "error"


class FlowValidationResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    valid: bool
    ir_version: Literal["amesh.flow/v1"] | None = Field(default=None, alias="irVersion")
    semantic_hash: str | None = None
    canonical: dict[str, Any] | None = None
    issues: list[ValidationIssue] = Field(default_factory=list)
