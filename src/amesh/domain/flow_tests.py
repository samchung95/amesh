from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .identity import new_runtime_id

FLOW_TEST_SIMULATOR_VERSION = "amesh.flow-test/v1"


class FlowTestOutcome(StrEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"


class FlowTestTaskState(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class FlowTestFixtureSource(StrEnum):
    INLINE = "INLINE"
    PLUGIN = "PLUGIN"
    RECORDED = "RECORDED"


class FlowTestFixture(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: FlowTestFixtureSource = FlowTestFixtureSource.INLINE
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = Field(default=None, max_length=4000)
    failures_before_success: int = Field(default=0, alias="failuresBeforeSuccess", ge=0, le=99)
    plugin_id: str | None = Field(default=None, alias="pluginId", max_length=512)
    plugin_version: str | None = Field(default=None, alias="pluginVersion", max_length=128)
    recorded_at: datetime | None = Field(default=None, alias="recordedAt")
    iterations: tuple[Any, ...] | None = None

    @model_validator(mode="after")
    def validate_source(self) -> FlowTestFixture:
        if self.error is not None and self.output:
            raise ValueError("a fixture cannot declare both output and error")
        if self.source is FlowTestFixtureSource.RECORDED and self.recorded_at is None:
            raise ValueError("recorded fixtures require recordedAt")
        if self.source is FlowTestFixtureSource.PLUGIN and self.plugin_id is None:
            raise ValueError("plugin fixtures require pluginId")
        if self.recorded_at is not None and self.recorded_at.tzinfo is None:
            raise ValueError("recordedAt must be timezone-aware")
        return self


class FlowTestExpectation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    state: FlowTestTaskState = FlowTestTaskState.SUCCESS
    outputs: dict[str, Any] | None = None
    task_states: dict[str, FlowTestTaskState] = Field(default_factory=dict, alias="taskStates")
    task_outputs: dict[str, dict[str, Any]] = Field(default_factory=dict, alias="taskOutputs")


class FlowTestDefinitionCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    test_id: str = Field(
        alias="testId", min_length=1, max_length=128, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$"
    )
    name: str = Field(min_length=1, max_length=200)
    revision: int = Field(ge=1)
    inputs: dict[str, Any] = Field(default_factory=dict)
    variables: dict[str, Any] = Field(default_factory=dict)
    fixtures: dict[str, FlowTestFixture] = Field(default_factory=dict)
    expected: FlowTestExpectation = Field(default_factory=FlowTestExpectation)
    tags: tuple[str, ...] = ()
    expected_version: int | None = Field(default=None, alias="expectedVersion", ge=1)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("test tags must be unique")
        if any(not item or len(item) > 128 for item in value):
            raise ValueError("test tags must contain 1-128 characters")
        return value


class FlowTestDefinition(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    definition_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    flow_id: str = Field(alias="flowId")
    test_id: str = Field(alias="testId")
    name: str
    revision: int = Field(ge=1)
    flow_semantic_hash: str = Field(alias="flowSemanticHash")
    plugin_set_hash: str = Field(alias="pluginSetHash")
    inputs: dict[str, Any]
    variables: dict[str, Any]
    fixtures: dict[str, FlowTestFixture]
    expected: FlowTestExpectation
    tags: tuple[str, ...]
    version: int = Field(ge=1)
    created_by: str = Field(alias="createdBy")
    updated_by: str = Field(alias="updatedBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class FlowTestAssertion(BaseModel):
    model_config = ConfigDict(frozen=True)

    path: str
    passed: bool
    expected: Any
    actual: Any


class FlowTestCoverage(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    tasks_total: int = Field(alias="tasksTotal", ge=0)
    tasks_covered: int = Field(alias="tasksCovered", ge=0)
    branches_total: int = Field(alias="branchesTotal", ge=0)
    branches_covered: int = Field(alias="branchesCovered", ge=0)
    handlers_total: int = Field(alias="handlersTotal", ge=0)
    handlers_covered: int = Field(alias="handlersCovered", ge=0)
    conditions_total: int = Field(alias="conditionsTotal", ge=0)
    conditions_covered: int = Field(alias="conditionsCovered", ge=0)
    percentage: float = Field(ge=0, le=100)
    disclaimer: str = (
        "Coverage is observed simulator execution, not proof of full workflow semantics."
    )


class SimulatedTaskResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    task_id: str = Field(alias="taskId")
    task_type: str = Field(alias="taskType")
    state: FlowTestTaskState
    attempts: int = Field(ge=0)
    output: dict[str, Any] | None = None
    branch: str | None = None
    lifecycle_phase: str = Field(alias="lifecyclePhase")
    fixture_source: FlowTestFixtureSource | None = Field(default=None, alias="fixtureSource")
    reason: str


class FlowTestCaseResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    test_id: str = Field(alias="testId")
    outcome: FlowTestOutcome
    state: FlowTestTaskState
    outputs: dict[str, Any]
    tasks: tuple[SimulatedTaskResult, ...]
    assertions: tuple[FlowTestAssertion, ...]
    coverage: FlowTestCoverage
    error: str | None = None


class FlowTestRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    test_ids: tuple[str, ...] = Field(default=(), alias="testIds")
    fail_fast: bool = Field(default=False, alias="failFast")

    @field_validator("test_ids")
    @classmethod
    def validate_test_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("testIds must be unique")
        return value


class FlowTestRunResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: str = Field(default="amesh.flow-test-result/v1", alias="schemaVersion")
    run_id: UUID = Field(default_factory=new_runtime_id, alias="runId")
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    flow_id: str = Field(alias="flowId")
    revision: int = Field(ge=1)
    flow_semantic_hash: str = Field(alias="flowSemanticHash")
    plugin_set_hash: str = Field(alias="pluginSetHash")
    simulator_version: str = Field(default=FLOW_TEST_SIMULATOR_VERSION, alias="simulatorVersion")
    outcome: FlowTestOutcome
    cases: tuple[FlowTestCaseResult, ...]
    coverage: FlowTestCoverage
    isolated: bool = True
    production_executions_created: int = Field(default=0, alias="productionExecutionsCreated")
    artifacts_created: int = Field(default=0, alias="artifactsCreated")
    secret_lookups: int = Field(default=0, alias="secretLookups")
    requested_by: str = Field(alias="requestedBy")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="createdAt")


class FlowTestQualityGateUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    enabled: bool = True
    minimum_coverage: float = Field(default=0, alias="minimumCoverage", ge=0, le=100)
    required_test_ids: tuple[str, ...] = Field(default=(), alias="requiredTestIds")
    expected_version: int | None = Field(default=None, alias="expectedVersion", ge=1)

    @field_validator("required_test_ids")
    @classmethod
    def validate_required_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("requiredTestIds must be unique")
        return value


class FlowTestQualityGate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    tenant_id: str = Field(alias="tenantId")
    namespace: str
    enabled: bool
    minimum_coverage: float = Field(alias="minimumCoverage", ge=0, le=100)
    required_test_ids: tuple[str, ...] = Field(alias="requiredTestIds")
    version: int = Field(ge=1)
    updated_by: str = Field(alias="updatedBy")
    updated_at: datetime = Field(alias="updatedAt")


class FlowTestGateDecision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    allowed: bool
    reason: str
    gate: FlowTestQualityGate | None = None
    result: FlowTestRunResult | None = None
