from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from amesh.domain import (
    FlowTestDefinition,
    FlowTestExpectation,
    FlowTestFixture,
    FlowTestFixtureSource,
    canonical_hash,
)
from amesh.domain.admission import AdmissionResourceType, resolve_admission_policies
from amesh.dsl import FlowDefinition, PlannedTask, compile_execution_tasks
from amesh.expressions import ExpressionContext, NativeExpressionEngine
from amesh.flow_testing import FlowTestSimulator
from amesh.workflow.data_contracts import validate_flow_inputs

SIMULATOR_VERSION = "amesh.simulator/v1"
REDUCER_SEMANTICS_VERSION = "amesh.reducer/v1"
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
_FLOWABLE_TYPES = frozenset(
    {
        "core.sequential",
        "core.parallel",
        "core.dag",
        "core.foreach",
        "core.while",
        "core.until",
        "core.if",
        "core.switch",
        "core.workingDirectory",
    }
)
_DETERMINISTIC_RUNNABLE_TYPES = frozenset({"core.log", "core.return"})


class SimulationFixtureSource(StrEnum):
    MOCK = "MOCK"
    RECORDED = "RECORDED"
    SCHEMA_ONLY = "SCHEMA_ONLY"


class SimulationSubstitution(StrEnum):
    FLOWABLE = "FLOWABLE"
    DETERMINISTIC = "DETERMINISTIC"
    MOCK = "MOCK"
    RECORDED = "RECORDED"
    SCHEMA_ONLY = "SCHEMA_ONLY"
    UNKNOWN = "UNKNOWN"


class SimulationTaskState(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    UNKNOWN = "UNKNOWN"


class SimulationFixture(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    source: SimulationFixtureSource = SimulationFixtureSource.MOCK
    output: dict[str, JsonValue] = Field(default_factory=dict)
    output_schema: dict[str, JsonValue] = Field(default_factory=dict, alias="outputSchema")
    error: str | None = Field(default=None, max_length=4000)
    failures_before_success: int = Field(default=0, alias="failuresBeforeSuccess", ge=0, le=99)
    recorded_at: datetime | None = Field(default=None, alias="recordedAt")

    @model_validator(mode="after")
    def validate_fixture(self) -> SimulationFixture:
        if self.error is not None and (self.output or self.output_schema):
            raise ValueError("a simulation fixture cannot declare output/schema and error")
        if self.source is SimulationFixtureSource.RECORDED and self.recorded_at is None:
            raise ValueError("recorded simulation fixtures require recordedAt")
        if self.source is SimulationFixtureSource.SCHEMA_ONLY and not self.output_schema:
            raise ValueError("schema-only simulation fixtures require outputSchema")
        if self.source is not SimulationFixtureSource.SCHEMA_ONLY and self.output_schema:
            raise ValueError("outputSchema is valid only for schema-only fixtures")
        if self.recorded_at is not None and self.recorded_at.tzinfo is None:
            raise ValueError("recordedAt must be timezone-aware")
        return self


class SimulationEstimateModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    duration_seconds: float = Field(default=0, alias="durationSeconds", ge=0)
    storage_bytes: int = Field(default=0, alias="storageBytes", ge=0)
    api_calls: int = Field(default=0, alias="apiCalls", ge=0)
    cost_usd: float = Field(default=0, alias="costUsd", ge=0)


class SimulationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    inputs: dict[str, JsonValue] = Field(default_factory=dict)
    variables: dict[str, JsonValue] = Field(default_factory=dict)
    trigger_context: dict[str, JsonValue] = Field(default_factory=dict, alias="triggerContext")
    fixtures: dict[str, SimulationFixture] = Field(default_factory=dict)
    estimate_models: dict[str, SimulationEstimateModel] = Field(
        default_factory=dict,
        alias="estimateModels",
    )
    default_runner: str = Field(default="kubernetes", alias="defaultRunner", min_length=1)
    sign_evidence: bool = Field(default=True, alias="signEvidence")


class SimulationUnknown(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    path: str
    reason: str


class SimulationPolicyDecision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    category: str
    policy_id: str = Field(alias="policyId")
    allowed: bool
    reason: str
    details: dict[str, JsonValue] = Field(default_factory=dict)


class SimulationTaskPlan(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    task_id: str = Field(alias="taskId")
    task_type: str = Field(alias="taskType")
    order: int = Field(ge=0)
    parent_id: str | None = Field(default=None, alias="parentId")
    dependencies: tuple[str, ...] = ()
    lifecycle_phase: str = Field(alias="lifecyclePhase")
    substitution: SimulationSubstitution
    state: SimulationTaskState
    attempts: int = Field(ge=0)
    max_attempts: int = Field(alias="maxAttempts", ge=1)
    output: dict[str, JsonValue] | None = None
    runner: str | None = None
    concurrency_buckets: tuple[str, ...] = Field(default=(), alias="concurrencyBuckets")
    expression_status: str = Field(alias="expressionStatus")
    reason: str


class SimulationEstimates(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    task_count: int = Field(alias="taskCount", ge=0)
    critical_path_seconds: float | None = Field(alias="criticalPathSeconds", ge=0)
    runner_demand: dict[str, int] = Field(default_factory=dict, alias="runnerDemand")
    storage_bytes: int = Field(alias="storageBytes", ge=0)
    api_calls: int = Field(alias="apiCalls", ge=0)
    cost_usd: float = Field(alias="costUsd", ge=0)
    modeled_task_count: int = Field(alias="modeledTaskCount", ge=0)


class SimulationEvidence(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    algorithm: str = "HMAC-SHA256"
    key_id: str = Field(alias="keyId")
    payload_digest: str = Field(alias="payloadDigest")
    signature: str


class SimulationPlan(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: str = Field(default="amesh.simulation-plan/v1", alias="schemaVersion")
    simulator_version: str = Field(default=SIMULATOR_VERSION, alias="simulatorVersion")
    reducer_semantics_version: str = Field(
        default=REDUCER_SEMANTICS_VERSION,
        alias="reducerSemanticsVersion",
    )
    expression_version: str = Field(alias="expressionVersion")
    plan_id: str = Field(alias="planId")
    namespace: str
    flow_id: str = Field(alias="flowId")
    revision: int = Field(ge=1)
    semantic_hash: str = Field(alias="semanticHash")
    plugin_set_hash: str = Field(alias="pluginSetHash")
    input_hash: str = Field(alias="inputHash")
    tasks: tuple[SimulationTaskPlan, ...]
    estimates: SimulationEstimates
    policy_decisions: tuple[SimulationPolicyDecision, ...] = Field(alias="policyDecisions")
    unknowns: tuple[SimulationUnknown, ...]
    side_effects_suppressed: bool = Field(default=True, alias="sideEffectsSuppressed")
    evidence: SimulationEvidence | None = None


class SimulationPlanDiff(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: str = Field(default="amesh.simulation-diff/v1", alias="schemaVersion")
    before_plan_id: str = Field(alias="beforePlanId")
    after_plan_id: str = Field(alias="afterPlanId")
    plugin_set_changed: bool = Field(alias="pluginSetChanged")
    added_tasks: tuple[str, ...] = Field(alias="addedTasks")
    removed_tasks: tuple[str, ...] = Field(alias="removedTasks")
    changed_tasks: tuple[str, ...] = Field(alias="changedTasks")
    estimate_delta: dict[str, float] = Field(alias="estimateDelta")
    unknowns_added: tuple[str, ...] = Field(alias="unknownsAdded")
    unknowns_resolved: tuple[str, ...] = Field(alias="unknownsResolved")


class SimulationComparison(BaseModel):
    model_config = ConfigDict(frozen=True)

    before: SimulationPlan
    after: SimulationPlan
    diff: SimulationPlanDiff


def simulate_flow(
    flow: FlowDefinition,
    request: SimulationRequest,
    *,
    semantic_hash: str | None = None,
    plugin_set: Mapping[str, Any] | None = None,
    tenant_id: str = "simulation",
    policy_decisions: Iterable[SimulationPolicyDecision] = (),
    signing_key: bytes | None = None,
    signing_key_id: str = "local",
) -> SimulationPlan:
    """Compile a side-effect-free, deterministic plan for one flow revision."""

    inputs = validate_flow_inputs(flow, dict(request.inputs))
    variables = {**flow.variables, **request.variables}
    resolved_policy_decisions = tuple(policy_decisions)
    resolved_semantic_hash = semantic_hash or canonical_hash(flow)
    resolved_plugin_set = dict(plugin_set or {"taskTypes": sorted(_task_types(flow))})
    plugin_set_hash = canonical_hash(resolved_plugin_set)
    plan = compile_execution_tasks(flow)
    expression_engine = NativeExpressionEngine()
    context = ExpressionContext(
        flow={"id": flow.id, "namespace": flow.namespace, "revision": flow.revision},
        trigger=request.trigger_context,
        inputs=inputs,
        variables=variables,
        labels=flow.labels,
    )

    unknowns: list[SimulationUnknown] = []
    fixtures = _flow_test_fixtures(flow, request, unknowns)
    definition = FlowTestDefinition(
        tenantId=tenant_id,
        namespace=flow.namespace,
        flowId=flow.id,
        testId="simulation",
        name="Deterministic simulation",
        revision=flow.revision,
        flowSemanticHash=resolved_semantic_hash,
        pluginSetHash=plugin_set_hash,
        inputs=inputs,
        variables=dict(request.variables),
        fixtures=fixtures,
        expected=FlowTestExpectation(),
        tags=(),
        version=1,
        createdBy="system:simulator",
        updatedBy="system:simulator",
        createdAt=_EPOCH,
        updatedAt=_EPOCH,
    )
    try:
        observed = FlowTestSimulator().simulate(
            flow,
            definition,
            trigger_context=dict(request.trigger_context),
        )
        observed_by_id = {item.task_id: item for item in observed.tasks}
    except (TypeError, ValueError) as exc:
        observed_by_id = {}
        unknowns.append(
            SimulationUnknown(
                code="SIMULATION_EVALUATION_UNKNOWN",
                path="flow",
                reason=str(exc),
            )
        )

    flow_buckets = _resolve_concurrency_buckets(
        flow.concurrency,
        tenant_id=tenant_id,
        namespace=flow.namespace,
        flow_id=flow.id,
        context=context,
        expression_engine=expression_engine,
        resource_type=AdmissionResourceType.EXECUTION,
        path="flow.concurrency",
        unknowns=unknowns,
    )
    task_plans: list[SimulationTaskPlan] = []
    static_by_id = {node.task.id: node for node in plan}
    observed_outputs: dict[str, Any] = {}
    for order, result in enumerate(observed_by_id.values()):
        node = static_by_id.get(result.task_id)
        task = node.task if node is not None else None
        fixture = request.fixtures.get(result.task_id) or (
            request.fixtures.get(task.id) if task is not None else None
        )
        substitution = _substitution(result.task_type, fixture)
        state = SimulationTaskState(result.state.value)
        reason = result.reason
        if substitution is SimulationSubstitution.UNKNOWN:
            state = SimulationTaskState.UNKNOWN
            reason = "output is unknown because no mock, recording or schema placeholder was declared"
        expression_status = "EVALUATED"
        concurrency_buckets: tuple[str, ...] = ()
        max_attempts = max(result.attempts, 1)
        runner = _runner(result.task_type, task, request.default_runner)
        if task is not None:
            task_context = ExpressionContext(
                flow=context.flow,
                trigger=context.trigger,
                inputs=context.inputs,
                outputs=observed_outputs,
                variables=context.variables,
                labels=context.labels,
            )
            max_attempts = task.retry.max_attempts
            concurrency_buckets = _resolve_concurrency_buckets(
                task.concurrency,
                tenant_id=tenant_id,
                namespace=flow.namespace,
                flow_id=flow.id,
                context=task_context,
                expression_engine=expression_engine,
                resource_type=AdmissionResourceType.TASK,
                path=f"tasks.{task.id}.concurrency",
                unknowns=unknowns,
            )
            try:
                expression_engine.render_task(task, task_context)
            except ValueError as exc:
                expression_status = "UNKNOWN"
                unknowns.append(
                    SimulationUnknown(
                        code="EXPRESSION_VALUE_UNKNOWN",
                        path=f"tasks.{task.id}",
                        reason=str(exc),
                    )
                )
        task_plans.append(
            SimulationTaskPlan(
                taskId=result.task_id,
                taskType=result.task_type,
                order=(node.order if node is not None else len(plan) + order),
                parentId=(node.parent_id if node is not None else _generated_parent(result.task_id)),
                dependencies=(node.dependencies if node is not None else ()),
                lifecyclePhase=result.lifecycle_phase,
                substitution=substitution,
                state=state,
                attempts=result.attempts,
                maxAttempts=max_attempts,
                output=result.output,
                runner=runner,
                concurrencyBuckets=tuple(dict.fromkeys((*flow_buckets, *concurrency_buckets))),
                expressionStatus=expression_status,
                reason=reason,
            )
        )
        if result.output is not None:
            observed_outputs[result.task_id] = result.output

    if not task_plans:
        task_plans.extend(
            _unevaluated_task(node, request, flow_buckets, request.default_runner)
            for node in plan
        )

    estimates = _estimate(tuple(task_plans), request.estimate_models, unknowns)
    normalized_unknowns = tuple(_deduplicate_unknowns(unknowns))
    unsigned_payload = {
        "simulatorVersion": SIMULATOR_VERSION,
        "reducerSemanticsVersion": REDUCER_SEMANTICS_VERSION,
        "expressionVersion": expression_engine.compatibility_version,
        "namespace": flow.namespace,
        "flowId": flow.id,
        "revision": flow.revision,
        "semanticHash": resolved_semantic_hash,
        "pluginSetHash": plugin_set_hash,
        "inputHash": canonical_hash(
            {"inputs": inputs, "variables": variables, "trigger": request.trigger_context}
        ),
        "tasks": [item.model_dump(mode="json", by_alias=True) for item in task_plans],
        "estimates": estimates.model_dump(mode="json", by_alias=True),
        "policyDecisions": [
            item.model_dump(mode="json", by_alias=True) for item in resolved_policy_decisions
        ],
        "unknowns": [item.model_dump(mode="json") for item in normalized_unknowns],
        "sideEffectsSuppressed": True,
    }
    plan_id = canonical_hash(unsigned_payload)
    created = SimulationPlan(
        simulatorVersion=SIMULATOR_VERSION,
        reducerSemanticsVersion=REDUCER_SEMANTICS_VERSION,
        expressionVersion=expression_engine.compatibility_version,
        planId=plan_id,
        namespace=flow.namespace,
        flowId=flow.id,
        revision=flow.revision,
        semanticHash=resolved_semantic_hash,
        pluginSetHash=plugin_set_hash,
        inputHash=str(unsigned_payload["inputHash"]),
        policyDecisions=resolved_policy_decisions,
        unknowns=normalized_unknowns,
        tasks=tuple(task_plans),
        estimates=estimates,
    )
    if request.sign_evidence and signing_key is not None:
        created = created.model_copy(
            update={"evidence": sign_simulation_evidence(created, signing_key, signing_key_id)}
        )
    return created


def sign_simulation_evidence(
    plan: SimulationPlan,
    signing_key: bytes,
    key_id: str,
) -> SimulationEvidence:
    if len(signing_key) < 32:
        raise ValueError("simulation evidence signing key must contain at least 32 bytes")
    payload = _evidence_payload(plan)
    digest = hashlib.sha256(payload).hexdigest()
    signature = hmac.new(signing_key, b"amesh-simulation-v1\0" + payload, hashlib.sha256)
    return SimulationEvidence(
        keyId=key_id,
        payloadDigest=digest,
        signature=f"v1={signature.hexdigest()}",
    )


def verify_simulation_evidence(plan: SimulationPlan, signing_key: bytes) -> bool:
    if plan.evidence is None:
        return False
    payload = _evidence_payload(plan)
    if not hmac.compare_digest(hashlib.sha256(payload).hexdigest(), plan.evidence.payload_digest):
        return False
    expected = "v1=" + hmac.new(
        signing_key,
        b"amesh-simulation-v1\0" + payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, plan.evidence.signature)


def compare_simulation_plans(
    before: SimulationPlan,
    after: SimulationPlan,
) -> SimulationPlanDiff:
    before_tasks = {item.task_id: item for item in before.tasks}
    after_tasks = {item.task_id: item for item in after.tasks}
    shared = before_tasks.keys() & after_tasks.keys()
    changed = tuple(
        sorted(
            task_id
            for task_id in shared
            if before_tasks[task_id].model_dump(mode="json")
            != after_tasks[task_id].model_dump(mode="json")
        )
    )
    before_unknowns = {f"{item.code}:{item.path}" for item in before.unknowns}
    after_unknowns = {f"{item.code}:{item.path}" for item in after.unknowns}
    return SimulationPlanDiff(
        beforePlanId=before.plan_id,
        afterPlanId=after.plan_id,
        pluginSetChanged=before.plugin_set_hash != after.plugin_set_hash,
        addedTasks=tuple(sorted(after_tasks.keys() - before_tasks.keys())),
        removedTasks=tuple(sorted(before_tasks.keys() - after_tasks.keys())),
        changedTasks=changed,
        estimateDelta={
            "taskCount": float(after.estimates.task_count - before.estimates.task_count),
            "storageBytes": float(after.estimates.storage_bytes - before.estimates.storage_bytes),
            "apiCalls": float(after.estimates.api_calls - before.estimates.api_calls),
            "costUsd": round(after.estimates.cost_usd - before.estimates.cost_usd, 8),
            "criticalPathSeconds": round(
                (after.estimates.critical_path_seconds or 0)
                - (before.estimates.critical_path_seconds or 0),
                6,
            ),
        },
        unknownsAdded=tuple(sorted(after_unknowns - before_unknowns)),
        unknownsResolved=tuple(sorted(before_unknowns - after_unknowns)),
    )


def _flow_test_fixtures(
    flow: FlowDefinition,
    request: SimulationRequest,
    unknowns: list[SimulationUnknown],
) -> dict[str, FlowTestFixture]:
    converted: dict[str, FlowTestFixture] = {}
    dynamic_ids = {
        node.task.id
        for node in compile_execution_tasks(flow)
        if node.task.type in {"core.while", "core.until"}
    }
    for task_id, fixture in request.fixtures.items():
        output = (
            _schema_placeholder(fixture.output_schema)
            if fixture.source is SimulationFixtureSource.SCHEMA_ONLY
            else dict(fixture.output)
        )
        converted[task_id] = FlowTestFixture(
            source=(
                FlowTestFixtureSource.RECORDED
                if fixture.source is SimulationFixtureSource.RECORDED
                else FlowTestFixtureSource.INLINE
            ),
            output=output,
            error=fixture.error,
            failuresBeforeSuccess=fixture.failures_before_success,
            recordedAt=fixture.recorded_at,
        )
    for node in compile_execution_tasks(flow):
        if node.task.type == "core.log" and node.task.id not in converted:
            converted[node.task.id] = FlowTestFixture(output={})
        if node.task.id in dynamic_ids and node.task.id not in converted:
            converted[node.task.id] = FlowTestFixture(iterations=())
            unknowns.append(
                SimulationUnknown(
                    code="DYNAMIC_ITERATION_COUNT_UNKNOWN",
                    path=f"tasks.{node.task.id}",
                    reason="while/until iteration count requires a declared fixture",
                )
            )
        if (
            node.task.type not in _FLOWABLE_TYPES | _DETERMINISTIC_RUNNABLE_TYPES
            and node.task.id not in converted
        ):
            unknowns.append(
                SimulationUnknown(
                    code="TASK_OUTPUT_UNKNOWN",
                    path=f"tasks.{node.task.id}",
                    reason="external task has no mock, recording or schema-only placeholder",
                )
            )
    return converted


def _resolve_concurrency_buckets(
    limits: Iterable[Any],
    *,
    tenant_id: str,
    namespace: str,
    flow_id: str,
    context: ExpressionContext,
    expression_engine: NativeExpressionEngine,
    resource_type: AdmissionResourceType,
    path: str,
    unknowns: list[SimulationUnknown],
) -> tuple[str, ...]:
    try:
        resolved = resolve_admission_policies(
            limits,
            resource_type=resource_type,
            tenant_id=tenant_id,
            namespace=namespace,
            flow_id=flow_id,
            render_key=lambda value: expression_engine.render_value(value, context),
        )
    except ValueError as exc:
        unknowns.append(
            SimulationUnknown(code="CONCURRENCY_KEY_UNKNOWN", path=path, reason=str(exc))
        )
        return ()
    return tuple(item.bucket for item in resolved)


def _estimate(
    tasks: tuple[SimulationTaskPlan, ...],
    models: Mapping[str, SimulationEstimateModel],
    unknowns: list[SimulationUnknown],
) -> SimulationEstimates:
    builtins = {
        "core.log": SimulationEstimateModel(),
        "core.return": SimulationEstimateModel(),
        **{task_type: SimulationEstimateModel() for task_type in _FLOWABLE_TYPES},
    }
    resolved_models = {**builtins, **models}
    durations: dict[str, float] = {}
    runner_demand: dict[str, int] = {}
    storage_bytes = 0
    api_calls = 0
    cost_usd = 0.0
    modeled = 0
    missing_types: set[str] = set()
    for task in tasks:
        model = resolved_models.get(task.task_type)
        if model is None:
            missing_types.add(task.task_type)
            continue
        modeled += 1
        attempts = max(task.attempts, 1)
        durations[task.task_id] = model.duration_seconds * attempts
        storage_bytes += model.storage_bytes * attempts
        api_calls += model.api_calls * attempts
        cost_usd += model.cost_usd * attempts
        if task.runner is not None:
            runner_demand[task.runner] = runner_demand.get(task.runner, 0) + 1
    for task_type in sorted(missing_types):
        unknowns.append(
            SimulationUnknown(
                code="ESTIMATE_MODEL_UNAVAILABLE",
                path=f"estimateModels.{task_type}",
                reason="no duration, storage, API-call or cost model was declared",
            )
        )
    critical_path: float | None = _critical_path(tasks, durations)
    if missing_types:
        critical_path = None
    return SimulationEstimates(
        taskCount=len(tasks),
        criticalPathSeconds=critical_path,
        runnerDemand=dict(sorted(runner_demand.items())),
        storageBytes=storage_bytes,
        apiCalls=api_calls,
        costUsd=round(cost_usd, 8),
        modeledTaskCount=modeled,
    )


def _critical_path(
    tasks: tuple[SimulationTaskPlan, ...],
    durations: Mapping[str, float],
) -> float:
    elapsed: dict[str, float] = {}
    for task in sorted(tasks, key=lambda item: item.order):
        dependency_time = max((elapsed.get(item, 0) for item in task.dependencies), default=0)
        elapsed[task.task_id] = dependency_time + durations.get(task.task_id, 0)
    return round(max(elapsed.values(), default=0), 6)


def _substitution(
    task_type: str,
    fixture: SimulationFixture | None,
) -> SimulationSubstitution:
    if task_type in _FLOWABLE_TYPES:
        return SimulationSubstitution.FLOWABLE
    if task_type in _DETERMINISTIC_RUNNABLE_TYPES:
        return SimulationSubstitution.DETERMINISTIC
    if fixture is None:
        return SimulationSubstitution.UNKNOWN
    return SimulationSubstitution(fixture.source.value)


def _runner(task_type: str, task: Any | None, default_runner: str) -> str | None:
    if task_type != "core.shell" and not task_type.startswith("script."):
        return None
    if task is not None and task.task_runner is not None:
        return str(task.task_runner.type)
    return default_runner


def _unevaluated_task(
    node: PlannedTask,
    request: SimulationRequest,
    flow_buckets: tuple[str, ...],
    default_runner: str,
) -> SimulationTaskPlan:
    fixture = request.fixtures.get(node.task.id)
    return SimulationTaskPlan(
        taskId=node.task.id,
        taskType=node.task.type,
        order=node.order,
        parentId=node.parent_id,
        dependencies=node.dependencies,
        lifecyclePhase=node.lifecycle_phase.value,
        substitution=_substitution(node.task.type, fixture),
        state=SimulationTaskState.UNKNOWN,
        attempts=0,
        maxAttempts=node.task.retry.max_attempts,
        runner=_runner(node.task.type, node.task, default_runner),
        concurrencyBuckets=flow_buckets,
        expressionStatus="UNKNOWN",
        reason="the simulator could not resolve this task from the supplied context",
    )


def _schema_placeholder(schema: Mapping[str, JsonValue]) -> dict[str, JsonValue]:
    if schema.get("type") != "object":
        return {"value": None}
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return {}
    return {
        str(key): _schema_value(value if isinstance(value, dict) else {})
        for key, value in properties.items()
    }


def _schema_value(schema: Mapping[str, JsonValue]) -> JsonValue:
    if "const" in schema:
        return schema["const"]
    examples = schema.get("examples")
    if isinstance(examples, list) and examples:
        return examples[0]
    values: dict[str, JsonValue] = {
        "string": "",
        "integer": 0,
        "number": 0.0,
        "boolean": False,
        "array": [],
        "object": {},
    }
    return values.get(str(schema.get("type")))


def _generated_parent(task_id: str) -> str | None:
    return task_id.split("[", 1)[0] if "[" in task_id else None


def _task_types(flow: FlowDefinition) -> set[str]:
    return {node.task.type for node in compile_execution_tasks(flow)}


def _deduplicate_unknowns(
    unknowns: Iterable[SimulationUnknown],
) -> Iterable[SimulationUnknown]:
    seen: set[tuple[str, str, str]] = set()
    for unknown in unknowns:
        identity = (unknown.code, unknown.path, unknown.reason)
        if identity not in seen:
            seen.add(identity)
            yield unknown


def _evidence_payload(plan: SimulationPlan) -> bytes:
    payload = plan.model_dump(mode="json", by_alias=True, exclude={"evidence"})
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return encoded.encode("utf-8")
