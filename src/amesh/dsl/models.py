from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Any, Literal, cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from croniter import croniter
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator, model_validator

from amesh.domain.admission import ConcurrencyLimit
from amesh.domain.agent_mesh import (
    AgentHandoffEndpoint,
    AgentMeshDefinition,
    AgentMeshSessionBudget,
    AgentRoutePolicySignal,
    AgentRouteRequest,
)
from amesh.domain.identity import NamespaceId, NaturalId
from amesh.domain.runner import RunnerExtension, RunnerNetworkPolicy, RunnerSecurityPolicy

MAX_TASK_NESTING_DEPTH = 16


def _validate_user_label_map(value: dict[str, str]) -> dict[str, str]:
    for key, item in value.items():
        if not key or len(key) > 128 or len(item) > 256:
            raise ValueError("label keys must be 1-128 characters and values at most 256")
        if key.startswith(("amesh.", "system.")):
            raise ValueError(f"label {key!r} uses a protected system prefix")
    return value


def _validate_workspace_path(value: str, *, allow_glob: bool) -> str:
    if not value or len(value) > 4096:
        raise ValueError("workspace paths must contain 1-4096 characters")
    if "\\" in value or value.startswith("/"):
        raise ValueError("workspace paths must use relative POSIX syntax")
    parts = PurePosixPath(value).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("workspace paths cannot contain empty, current or parent segments")
    if ":" in parts[0]:
        raise ValueError("workspace paths cannot contain a drive or URI scheme")
    if not allow_glob and any(character in value for character in "*?[]"):
        raise ValueError("workspace input paths cannot contain glob syntax")
    return value


class InputDefinition(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: NaturalId
    type: str = Field(min_length=1, max_length=256)
    required: bool = False
    default: Any | None = None
    description: str | None = None
    sensitive: bool = False
    display_name: str | None = Field(default=None, alias="displayName", max_length=256)
    placeholder: str | None = Field(default=None, max_length=512)
    prefill: Any | None = None
    validation: dict[str, Any] = Field(default_factory=dict)
    values: tuple[Any, ...] = ()
    item_type: str | None = Field(default=None, alias="itemType", min_length=1, max_length=256)
    value_schema: dict[str, Any] = Field(default_factory=dict, alias="schema")
    max_bytes: int | None = Field(default=None, alias="maxBytes", ge=1)

    @property
    def has_default(self) -> bool:
        return "default" in self.model_fields_set and self.default is not None


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


class ConditionErrorPolicy(StrEnum):
    FAIL = "FAIL"
    FALSE = "FALSE"
    FALLBACK = "FALLBACK"

    @classmethod
    def _missing_(cls, value: object) -> ConditionErrorPolicy | None:
        return cls.FALSE if value is False else None


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
    condition: str | None = Field(default=None, min_length=1, max_length=65_536)
    condition_error_policy: ConditionErrorPolicy = Field(
        default=ConditionErrorPolicy.FAIL,
        alias="conditionErrorPolicy",
    )

    @model_validator(mode="after")
    def validate_condition_policy(self) -> RetryPolicy:
        if self.condition_error_policy is ConditionErrorPolicy.FALLBACK:
            raise ValueError("retry conditionErrorPolicy cannot be FALLBACK")
        return self


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
    engine_scopes: tuple[NaturalId, ...] = Field(
        default=(),
        alias="engineScopes",
        exclude_if=lambda value: not value,
    )
    files: dict[str, str] = Field(default_factory=dict)
    resource_limits: TaskResourceLimits = Field(
        default_factory=TaskResourceLimits,
        alias="resourceLimits",
    )

    @field_validator("engine_scopes")
    @classmethod
    def validate_unique_engine_scopes(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("contract engineScopes values must be unique")
        return value


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


class ConditionalBranch(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: NaturalId
    condition: str = Field(min_length=1, max_length=65_536)
    tasks: list[TaskDefinition] = Field(min_length=1)


class ErrorSelector(BaseModel):
    """Typed selector applied to one task inside an errors block."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    states: tuple[Literal["FAILED", "CANCELLED"], ...] = ()
    categories: tuple[
        Literal[
            "RETRYABLE",
            "NON_RETRYABLE",
            "CANCELLED",
            "TIMED_OUT",
            "INFRASTRUCTURE",
            "CONFIGURATION",
            "USER_CODE",
            "PLATFORM",
        ],
        ...,
    ] = ()
    task_ids: tuple[NaturalId, ...] = Field(default=(), alias="taskIds")
    condition: str | None = Field(default=None, min_length=1, max_length=65_536)

    @model_validator(mode="after")
    def validate_unique_values(self) -> ErrorSelector:
        for name, values in (
            ("states", self.states),
            ("categories", self.categories),
            ("taskIds", self.task_ids),
        ):
            if len(set(values)) != len(values):
                raise ValueError(f"errorSelector {name} values must be unique")
        return self


class TaskTimeoutMode(StrEnum):
    BOUNDED = "BOUNDED"
    DISABLED = "DISABLED"


class TaskDefinition(BaseModel):
    # populate_by_name keeps snake_case spellings of aliased fields (depends_on,
    # run_if) from being silently swallowed into `extra` as inert plugin fields.
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: NaturalId
    type: str = Field(min_length=1, max_length=512)
    description: str | None = None
    run_labels: dict[str, str] = Field(default_factory=dict, alias="runLabels")

    _validate_run_labels = field_validator("run_labels")(_validate_user_label_map)
    depends_on: list[str] = Field(default_factory=list, alias="dependsOn")
    run_if: str | None = Field(default=None, alias="runIf")
    condition_error_policy: ConditionErrorPolicy = Field(
        default=ConditionErrorPolicy.FAIL,
        alias="conditionErrorPolicy",
    )
    retry: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout_mode: TaskTimeoutMode = Field(
        default=TaskTimeoutMode.BOUNDED,
        alias="timeoutMode",
        exclude_if=lambda value: value is TaskTimeoutMode.BOUNDED,
    )
    timeout_seconds: float | None = Field(default=None, gt=0, alias="timeoutSeconds")
    command: list[str] | None = None
    standard_input: str | None = Field(default=None, alias="stdin")
    image: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)
    resources: dict[str, Any] = Field(default_factory=dict)
    task_runner: RunnerExtension | None = Field(default=None, alias="taskRunner")
    runner_credentials: dict[str, NaturalId] = Field(
        default_factory=dict,
        alias="runnerCredentials",
    )
    network_policy: RunnerNetworkPolicy = Field(
        default_factory=RunnerNetworkPolicy,
        alias="networkPolicy",
    )
    security_policy: RunnerSecurityPolicy = Field(
        default_factory=RunnerSecurityPolicy,
        alias="securityPolicy",
    )
    input_files: dict[str, str] = Field(default_factory=dict, alias="inputFiles")
    output_files: tuple[str, ...] = Field(default=(), alias="outputFiles")
    output_manifest: str | None = Field(default=None, alias="outputManifest")
    workspace_quota_bytes: int = Field(
        default=104_857_600,
        alias="workspaceQuotaBytes",
        ge=1,
    )
    retain_diagnostics_on_failure: bool = Field(
        default=False,
        alias="retainDiagnosticsOnFailure",
    )
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
    condition: str | None = Field(default=None, min_length=1, max_length=65_536)
    then_tasks: list[TaskDefinition] = Field(default_factory=list, alias="then")
    else_if: list[ConditionalBranch] = Field(default_factory=list, alias="elseIf")
    else_tasks: list[TaskDefinition] = Field(default_factory=list, alias="else")
    cases: dict[str, list[TaskDefinition]] = Field(default_factory=dict)
    predicate_cases: list[ConditionalBranch] = Field(
        default_factory=list,
        alias="predicateCases",
    )
    errors: list[TaskDefinition] = Field(default_factory=list)
    error_selector: ErrorSelector | None = Field(default=None, alias="errorSelector")

    @model_validator(mode="before")
    @classmethod
    def reject_conflicting_spellings(cls, data: Any) -> Any:
        # With populate_by_name, either spelling is accepted alone; supplying
        # both would let the alias win while the other rides along as an inert
        # extra field, so it is rejected outright.
        if isinstance(data, dict):
            for name, alias in (
                ("depends_on", "dependsOn"),
                ("run_if", "runIf"),
                ("condition_error_policy", "conditionErrorPolicy"),
                ("timeout_mode", "timeoutMode"),
                ("then_tasks", "then"),
                ("else_if", "elseIf"),
                ("else_tasks", "else"),
                ("predicate_cases", "predicateCases"),
                ("error_selector", "errorSelector"),
                ("input_files", "inputFiles"),
                ("output_files", "outputFiles"),
                ("output_manifest", "outputManifest"),
                ("workspace_quota_bytes", "workspaceQuotaBytes"),
                ("retain_diagnostics_on_failure", "retainDiagnosticsOnFailure"),
                ("task_runner", "taskRunner"),
                ("runner_credentials", "runnerCredentials"),
                ("network_policy", "networkPolicy"),
                ("security_policy", "securityPolicy"),
                ("standard_input", "stdin"),
            ):
                if name in data and alias in data:
                    raise ValueError(f"task cannot set both {alias!r} and {name!r}")
        return data

    @model_validator(mode="after")
    def validate_timeout_mode(self) -> TaskDefinition:
        if (
            self.timeout_mode is TaskTimeoutMode.DISABLED
            and "timeout_seconds" in self.model_fields_set
        ):
            raise ValueError("DISABLED task timeout mode requires timeoutSeconds to be absent")
        return self

    @model_validator(mode="after")
    def validate_self_dependency(self) -> TaskDefinition:
        if self.id in self.depends_on:
            raise ValueError(f"task {self.id!r} cannot depend on itself")
        invalid_environment_variables = [
            name
            for name in self.runner_credentials
            if not name.replace("_", "a").isalnum() or name[0].isdigit()
        ]
        if invalid_environment_variables:
            raise ValueError(
                "runnerCredentials keys must be environment-variable names: "
                + ", ".join(sorted(invalid_environment_variables))
            )
        undeclared_scopes = set(self.runner_credentials.values()).difference(
            self.contract.secret_scopes
        )
        if undeclared_scopes:
            raise ValueError(
                "runnerCredentials reference undeclared contract secretScopes: "
                + ", ".join(sorted(undeclared_scopes))
            )
        conditional_children = any(
            (
                self.then_tasks,
                self.else_if,
                self.else_tasks,
                self.cases,
                self.predicate_cases,
            )
        )
        if (
            self.type
            in {
                "core.sequential",
                "core.parallel",
                "core.dag",
                "core.foreach",
                "core.while",
                "core.until",
                "core.workingDirectory",
                "agent.mesh",
            }
            and not self.tasks
        ):
            raise ValueError(f"flowable task {self.id!r} requires at least one child task")
        if self.type == "core.if":
            if self.condition is None or not self.then_tasks:
                raise ValueError("core.if requires condition and at least one then task")
            if self.tasks or self.cases or self.predicate_cases:
                raise ValueError("core.if accepts then/elseIf/else branches, not tasks or cases")
            if self.condition_error_policy is ConditionErrorPolicy.FALLBACK and not self.else_tasks:
                raise ValueError("core.if FALLBACK policy requires an else branch")
        elif self.type == "core.switch":
            if "value" not in (self.model_extra or {}):
                raise ValueError("core.switch requires value")
            if not self.cases and not self.predicate_cases:
                raise ValueError("core.switch requires cases or predicateCases")
            if self.tasks or self.condition or self.then_tasks or self.else_if or self.else_tasks:
                raise ValueError("core.switch accepts cases and predicateCases only")
            empty_cases = [case for case, tasks in self.cases.items() if not tasks]
            if empty_cases:
                raise ValueError(f"core.switch cases require tasks: {empty_cases}")
            if (
                self.condition_error_policy is ConditionErrorPolicy.FALLBACK
                and "default" not in self.cases
            ):
                raise ValueError("core.switch FALLBACK policy requires a default case")
        elif conditional_children or (
            self.condition is not None and self.type not in {"core.while", "core.until"}
        ):
            raise ValueError("conditional branch fields require core.if or core.switch")
        elif self.condition_error_policy is ConditionErrorPolicy.FALLBACK:
            raise ValueError("FALLBACK conditionErrorPolicy requires core.if or core.switch")
        if self.tasks and self.type not in {
            "core.sequential",
            "core.parallel",
            "core.dag",
            "core.foreach",
            "core.while",
            "core.until",
            "core.workingDirectory",
            "agent.mesh",
        }:
            raise ValueError("tasks may only be declared by a versioned built-in flowable contract")
        if self.run_if is not None and self.condition_error_policy is ConditionErrorPolicy.FALLBACK:
            raise ValueError("runIf cannot share a FALLBACK conditionErrorPolicy")
        if (self.tasks or conditional_children) and self.task_cache.enabled:
            raise ValueError("taskCache is supported only on runnable tasks")
        if self.errors and self.type not in {
            "core.sequential",
            "core.parallel",
            "core.dag",
            "core.foreach",
            "core.while",
            "core.until",
            "core.if",
            "core.switch",
            "core.workingDirectory",
            "agent.mesh",
        }:
            raise ValueError("local errors require a flowable task")
        if self.type == "core.workingDirectory" and self.max_concurrency not in {None, 1}:
            raise ValueError(
                "core.workingDirectory children are sequential; maxConcurrency must be 1"
            )
        if self.type == "agent.mesh":
            self._validate_agent_mesh()
        return self

    def _validate_agent_mesh(self) -> None:
        extra = self.model_extra or {}
        definition = AgentMeshDefinition.model_validate(
            {
                "topology": extra.get("topology"),
                "members": extra.get("members"),
                "budget": extra.get("budget"),
            }
        )
        if self.max_concurrency is None:
            raise ValueError("agent.mesh requires maxConcurrency")
        if self.max_concurrency > definition.budget.max_concurrency:
            raise ValueError("agent.mesh maxConcurrency exceeds budget.maxConcurrency")

        children = {child.id: child for child in self.tasks}
        member_by_id = {member.member_id: member for member in definition.members}
        member_by_task = {member.task: member for member in definition.members}
        unregistered_sessions = sorted(
            child.id
            for child in self.tasks
            if child.type == "agent.session" and child.id not in member_by_task
        )
        if unregistered_sessions:
            raise ValueError(
                "agent.mesh session children must be declared members: "
                + ", ".join(unregistered_sessions)
            )
        reservations: list[AgentMeshSessionBudget] = []
        for member in definition.members:
            child = children.get(member.task)
            if child is None or child.type != "agent.session":
                raise ValueError(
                    f"mesh member {member.member_id!r} must reference an agent.session child"
                )
            child_extra = child.model_extra or {}
            expected = {
                "agent": member.agent,
                "agentRevision": member.agent_revision,
                "meshId": self.id,
                "memberId": member.member_id,
            }
            mismatched = [key for key, value in expected.items() if child_extra.get(key) != value]
            if mismatched:
                raise ValueError(
                    f"mesh member {member.member_id!r} session identity mismatch: "
                    + ", ".join(mismatched)
                )
            reservations.append(
                AgentMeshSessionBudget.model_validate(child_extra.get("meshBudget"))
            )

        overcommitted: list[str] = []
        if sum(item.max_total_tokens for item in reservations) > definition.budget.max_total_tokens:
            overcommitted.append("maxTotalTokens")
        if sum((item.max_cost_usd for item in reservations), start=0) > (
            definition.budget.max_cost_usd
        ):
            overcommitted.append("maxCostUsd")
        if sum(item.max_duration_seconds for item in reservations) > (
            definition.budget.max_duration_seconds
        ):
            overcommitted.append("maxDurationSeconds")
        if sum(item.max_tool_calls for item in reservations) > definition.budget.max_tool_calls:
            overcommitted.append("maxToolCalls")
        if overcommitted:
            raise ValueError(
                "agent.mesh session reservations exceed parent budget: " + ", ".join(overcommitted)
            )

        route_tasks = [child for child in self.tasks if child.type == "agent.route"]
        if definition.topology.value == "ROUTER" and not route_tasks:
            raise ValueError("ROUTER agent.mesh requires an agent.route child")
        for route_task in route_tasks:
            request = AgentRouteRequest.model_validate(route_task.model_extra or {})
            for candidate in request.candidates:
                route_member = member_by_id.get(candidate.member_id)
                if route_member is None or (
                    candidate.task,
                    candidate.agent,
                    candidate.agent_revision,
                    candidate.capabilities,
                ) != (
                    route_member.task,
                    route_member.agent,
                    route_member.agent_revision,
                    route_member.capabilities,
                ):
                    raise ValueError(
                        f"agent.route candidate {candidate.member_id!r} must exactly match a mesh member"
                    )

        for handoff_task in (child for child in self.tasks if child.type == "agent.handoff"):
            handoff_extra = handoff_task.model_extra or {}
            source = AgentHandoffEndpoint.model_validate(handoff_extra.get("source"))
            destination = AgentHandoffEndpoint.model_validate(handoff_extra.get("destination"))
            AgentRoutePolicySignal.model_validate(handoff_extra.get("policy"))
            source_member = member_by_task.get(source.task)
            destination_member = member_by_task.get(destination.task)
            if source_member is None or (
                source.agent,
                source.agent_revision,
            ) != (source_member.agent, source_member.agent_revision):
                raise ValueError("agent.handoff source must exactly match a mesh member")
            if destination_member is None or (
                destination.agent,
                destination.agent_revision,
            ) != (destination_member.agent, destination_member.agent_revision):
                raise ValueError("agent.handoff destination must exactly match a mesh member")
            if source.task not in handoff_task.depends_on:
                raise ValueError("agent.handoff must directly depend on its source session")
            destination_task = children[destination.task]
            if handoff_task.id not in destination_task.depends_on:
                raise ValueError("agent.handoff destination must directly depend on the hand-off")

    @field_validator("input_files")
    @classmethod
    def validate_input_file_paths(cls, value: dict[str, str]) -> dict[str, str]:
        for path, reference in value.items():
            _validate_workspace_path(path, allow_glob=False)
            if not reference:
                raise ValueError("inputFiles references must not be empty")
        return value

    @field_validator("output_files")
    @classmethod
    def validate_output_file_paths(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("outputFiles patterns must be unique")
        for pattern in value:
            _validate_workspace_path(pattern, allow_glob=True)
        return value

    @field_validator("output_manifest")
    @classmethod
    def validate_output_manifest_path(cls, value: str | None) -> str | None:
        if value is not None:
            _validate_workspace_path(value, allow_glob=False)
        return value

    def child_task_groups(self) -> tuple[tuple[str, list[TaskDefinition]], ...]:
        if self.type == "core.if":
            groups: list[tuple[str, list[TaskDefinition]]] = [("then", self.then_tasks)]
            groups.extend((f"else-if:{branch.id}", branch.tasks) for branch in self.else_if)
            if self.else_tasks:
                groups.append(("else", self.else_tasks))
            return tuple(groups)
        if self.type == "core.switch":
            groups = [
                (f"case:{case}", tasks) for case, tasks in self.cases.items() if case != "default"
            ]
            groups.extend(
                (f"predicate:{branch.id}", branch.tasks) for branch in self.predicate_cases
            )
            if "default" in self.cases:
                groups.append(("default", self.cases["default"]))
            return tuple(groups)
        return (("tasks", self.tasks),) if self.tasks else ()


ConditionalBranch.model_rebuild()


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


class PluginDefaultDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    type: str = Field(min_length=1, max_length=512)
    values: dict[str, Any] = Field(default_factory=dict)
    forced: bool = False

    @field_validator("values")
    @classmethod
    def validate_values(cls, value: dict[str, Any]) -> dict[str, Any]:
        structural = {
            "id",
            "type",
            "tasks",
            "then",
            "elseIf",
            "else",
            "cases",
            "predicateCases",
            "errors",
        }
        invalid = sorted(structural.intersection(value))
        if invalid:
            raise ValueError(
                "plugin defaults cannot set structural properties: " + ", ".join(invalid)
            )
        if any(not key or len(key) > 128 for key in value):
            raise ValueError("plugin default property names must contain 1-128 characters")
        return value


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
    _validate_labels = field_validator("labels")(_validate_user_label_map)
    annotations: dict[str, str] = Field(default_factory=dict)
    plugin_defaults: list[PluginDefaultDefinition] = Field(
        default_factory=list,
        alias="pluginDefaults",
    )
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
    after_execution: list[TaskDefinition] = Field(default_factory=list, alias="afterExecution")

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
        configured_depth = max(
            (
                _task_nesting_depth(task, 1)
                for task in (
                    *self.tasks,
                    *self.errors,
                    *self.finally_tasks,
                    *self.after_execution,
                )
            ),
            default=1,
        )
        if configured_depth > MAX_TASK_NESTING_DEPTH:
            raise ValueError(
                f"task nesting depth exceeds the deterministic maximum of {MAX_TASK_NESTING_DEPTH}"
            )
        plugin_default_keys = [(item.type, item.forced) for item in self.plugin_defaults]
        if len(set(plugin_default_keys)) != len(plugin_default_keys):
            raise ValueError("flow pluginDefaults must have unique type/forced pairs")
        return self

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any) -> dict[str, Any]:
        schema = cast(dict[str, Any], handler(core_schema))
        schema["additionalProperties"] = False
        schema["patternProperties"] = {"^x-": {}}
        return schema


def _task_nesting_depth(task: TaskDefinition, current: int) -> int:
    children = [child for _branch, group in task.child_task_groups() for child in group] + list(
        task.errors
    )
    return max(
        (_task_nesting_depth(child, current + 1) for child in children),
        default=current,
    )


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
