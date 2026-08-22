from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Literal, cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from croniter import croniter
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

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
    max_pending: int = Field(default=1000, ge=1, le=100_000, alias="maxPending")
    max_attempts: int = Field(default=3, ge=1, le=100, alias="maxAttempts")
    retry_delay: timedelta = Field(default=timedelta(seconds=30), alias="retryDelay")
    flow_namespace: NamespaceId | None = Field(default=None, alias="namespace")
    flow_id: NaturalId | None = Field(default=None, alias="flowId")
    states: tuple[Literal["CANCELLED", "SUCCESS", "FAILED", "WARNING"], ...] = ("SUCCESS",)
    inputs: dict[str, Any] = Field(default_factory=dict)
    max_depth: int = Field(default=16, ge=1, le=100, alias="maxDepth")

    @model_validator(mode="after")
    def validate_cron(self) -> TriggerDefinition:
        if self.retry_delay.total_seconds() <= 0:
            raise ValueError("trigger retryDelay must be positive")
        if self.type == "core.flow":
            if self.flow_id is None:
                raise ValueError("core.flow trigger requires flowId")
            if not self.states:
                raise ValueError("core.flow trigger requires at least one terminal state")
            if len(set(self.states)) != len(self.states):
                raise ValueError("core.flow trigger states must be unique")
            return self
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


class FlowableFailurePolicy(StrEnum):
    FAIL_FAST = "FAIL_FAST"
    CONTINUE_ON_ERROR = "CONTINUE_ON_ERROR"
    COLLECT_ALL = "COLLECT_ALL"


class RunnableTaskContract(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    secret_scopes: tuple[str, ...] = Field(default=(), alias="secretScopes")
    files: dict[str, str] = Field(default_factory=dict)
    resource_limits: TaskResourceLimits = Field(
        default_factory=TaskResourceLimits,
        alias="resourceLimits",
    )


class TaskCacheScope(StrEnum):
    TASK = "TASK"
    FLOW = "FLOW"
    NAMESPACE = "NAMESPACE"


class TaskCacheInvalidationPolicy(StrEnum):
    TTL_AND_REVISION = "TTL_AND_REVISION"
    MANUAL = "MANUAL"


class TaskCachePolicy(BaseModel):
    """Kestra-compatible task cache controls plus AMESH scoping extensions."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    enabled: bool = False
    ttl: timedelta | None = None
    namespace: NaturalId | None = None
    scope: TaskCacheScope = TaskCacheScope.TASK
    invalidation_policy: TaskCacheInvalidationPolicy = Field(
        default=TaskCacheInvalidationPolicy.TTL_AND_REVISION,
        alias="invalidationPolicy",
    )
    key_context: tuple[Literal["inputs", "variables", "labels", "trigger", "iteration"], ...] = (
        Field(
            default=("inputs", "variables", "labels", "trigger", "iteration"),
            alias="keyContext",
        )
    )
    code_version: str | None = Field(
        default=None, alias="codeVersion", min_length=1, max_length=256
    )

    @model_validator(mode="after")
    def validate_enabled_policy(self) -> TaskCachePolicy:
        if self.enabled and (self.ttl is None or self.ttl.total_seconds() <= 0):
            raise ValueError("enabled taskCache requires a positive ttl")
        if len(set(self.key_context)) != len(self.key_context):
            raise ValueError("taskCache keyContext values must be unique")
        return self


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
    failure_policy: FlowableFailurePolicy = Field(
        default=FlowableFailurePolicy.FAIL_FAST,
        alias="failurePolicy",
    )
    max_concurrency: int | None = Field(default=None, alias="maxConcurrency", ge=1, le=10_000)
    contract: RunnableTaskContract = Field(default_factory=RunnableTaskContract)
    task_cache: TaskCachePolicy = Field(default_factory=TaskCachePolicy, alias="taskCache")
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
        if (
            self.type
            in {
                "core.sequential",
                "core.parallel",
                "core.dag",
                "core.foreach",
                "core.while",
                "core.until",
            }
            and not self.tasks
        ):
            raise ValueError(f"flowable task {self.id!r} requires at least one child task")
        if self.tasks and self.task_cache.enabled:
            raise ValueError("taskCache is supported only on runnable tasks")
        return self


class CheckActionDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    type: Literal["NOTIFY", "RUN_FLOW"]
    namespace: NamespaceId | None = None
    flow_id: NaturalId | None = Field(default=None, alias="flowId")
    channel: str | None = Field(default=None, min_length=1, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)
    max_depth: int = Field(default=4, ge=1, le=16, alias="maxDepth")
    max_attempts: int = Field(default=3, ge=1, le=10, alias="maxAttempts")

    @model_validator(mode="after")
    def validate_target(self) -> CheckActionDefinition:
        if self.type == "RUN_FLOW" and self.flow_id is None:
            raise ValueError("RUN_FLOW check action requires flowId")
        if self.type == "NOTIFY" and self.channel is None:
            raise ValueError("NOTIFY check action requires channel")
        return self


class CheckDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: NaturalId
    type: Literal[
        "DURATION",
        "START_DELAY",
        "FRESHNESS",
        "COMPLETION_WINDOW",
        "OUTPUT",
        "EXPRESSION",
    ]
    severity: Literal["WARN", "FAIL"] = "FAIL"
    threshold: timedelta | None = None
    expression: str | None = Field(default=None, min_length=1, max_length=65_536)
    enabled: bool = True
    actions: tuple[CheckActionDefinition, ...] = Field(default=(), max_length=10)

    @model_validator(mode="after")
    def validate_check_contract(self) -> CheckDefinition:
        threshold_types = {"DURATION", "START_DELAY", "FRESHNESS", "COMPLETION_WINDOW"}
        expression_types = {"OUTPUT", "EXPRESSION"}
        if self.type in threshold_types:
            if self.threshold is None or self.threshold.total_seconds() <= 0:
                raise ValueError(f"{self.type} check requires a positive threshold")
            if self.expression is not None:
                raise ValueError(f"{self.type} check cannot declare expression")
        elif self.type in expression_types:
            if self.expression is None:
                raise ValueError(f"{self.type} check requires expression")
            if self.threshold is not None:
                raise ValueError(f"{self.type} check cannot declare threshold")
        return self


class FlowDefinition(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    _persisted_canonical_definition: str | None = PrivateAttr(default=None)
    _persisted_semantic_hash: str | None = PrivateAttr(default=None)

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
    checks: list[CheckDefinition] = Field(default_factory=list)
    check_policies: tuple[NaturalId, ...] = Field(default=(), alias="checkPolicies")
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
        check_ids = [check.id for check in self.checks]
        if len(set(check_ids)) != len(check_ids):
            raise ValueError("flow check ids must be unique")
        if len(set(self.check_policies)) != len(self.check_policies):
            raise ValueError("flow checkPolicies must be unique")
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
