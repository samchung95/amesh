from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain import canonical_hash
from amesh.dsl import FlowDefinition, PlannedTask, TaskDefinition, compile_execution_tasks
from amesh.dsl.flowables import DYNAMIC_FLOWABLE_MODES, FLOWABLE_MODES
from amesh.dsl.models import MAX_TASK_NESTING_DEPTH

DETERMINISM_ENVELOPE_VERSION = "amesh.determinism-envelope/v1"
_DETERMINISTIC_RUNNABLE_TYPES = frozenset({"core.log", "core.return"})
_LOOP_DEFAULT_MAX_ITERATIONS = 10_000
_LOOP_DEFAULT_MAX_DURATION_SECONDS = 3_600.0
_LOOP_DEFAULT_MAX_TASK_RUNS = 100_000
_LOOP_DEFAULT_INLINE_PAYLOAD_BYTES = 65_536
_SUBFLOW_DEFAULT_MAX_DEPTH = 16


class DeterminismPolicyPin(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    category: str
    key: str
    revision: int | None = Field(default=None, ge=1)
    digest: str


class DeterminismNode(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    logical_id: str = Field(alias="logicalId")
    task_type: str = Field(alias="taskType")
    order: int = Field(ge=0)
    parent_id: str | None = Field(default=None, alias="parentId")
    branch_id: str | None = Field(default=None, alias="branchId")
    dependencies: tuple[str, ...] = ()
    lifecycle_phase: str = Field(alias="lifecyclePhase")
    mode: str | None = None
    max_concurrency: int | None = Field(default=None, alias="maxConcurrency", ge=1)


class DynamicExecutionBound(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    task_id: str = Field(alias="taskId")
    kind: str
    template_task_ids: tuple[str, ...] = Field(default=(), alias="templateTaskIds")
    max_iterations: int | None = Field(default=None, alias="maxIterations", ge=1)
    max_duration_seconds: float | None = Field(
        default=None,
        alias="maxDurationSeconds",
        gt=0,
    )
    max_task_runs: int | None = Field(default=None, alias="maxTaskRuns", ge=1)
    max_concurrency: int | None = Field(default=None, alias="maxConcurrency", ge=1)
    max_depth: int | None = Field(default=None, alias="maxDepth", ge=1)
    inline_payload_bytes: int | None = Field(
        default=None,
        alias="inlinePayloadBytes",
        ge=1,
    )
    iteration_key_pattern: str | None = Field(default=None, alias="iterationKeyPattern")
    worst_case_task_runs: int = Field(alias="worstCaseTaskRuns", ge=1)


class NondeterministicOperation(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    task_id: str = Field(alias="taskId")
    task_type: str = Field(alias="taskType")
    deterministic_output: bool = Field(default=False, alias="deterministicOutput")
    replay_requirement: str = Field(
        default="PINNED_METADATA_OR_RECORDED_FIXTURE",
        alias="replayRequirement",
    )


class DeterminismEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: str = Field(
        default=DETERMINISM_ENVELOPE_VERSION,
        alias="schemaVersion",
    )
    revision: int = Field(ge=1)
    semantic_hash: str = Field(alias="semanticHash")
    plugin_set_hash: str = Field(alias="pluginSetHash")
    policy_pins: tuple[DeterminismPolicyPin, ...] = Field(default=(), alias="policyPins")
    nodes: tuple[DeterminismNode, ...]
    dynamic_bounds: tuple[DynamicExecutionBound, ...] = Field(alias="dynamicBounds")
    maximum_task_nesting_depth: int = Field(alias="maximumTaskNestingDepth", ge=1)
    configured_task_nesting_depth: int = Field(alias="configuredTaskNestingDepth", ge=1)
    worst_case_task_runs: int = Field(alias="worstCaseTaskRuns", ge=1)
    nondeterministic_operations: tuple[NondeterministicOperation, ...] = Field(
        alias="nondeterministicOperations"
    )
    envelope_digest: str = Field(alias="envelopeDigest")


@dataclass(frozen=True)
class _TaskAnalysis:
    nesting_depth: int
    worst_case_task_runs: int


def build_determinism_envelope(
    flow: FlowDefinition,
    *,
    semantic_hash: str,
    plugin_set: Mapping[str, Any],
    policy_pins: Iterable[DeterminismPolicyPin] = (),
) -> DeterminismEnvelope:
    """Project the version-pinned controls that make one flow execution reproducible."""

    plan = compile_execution_tasks(flow)
    task_analysis, configured_nesting_depth, worst_case_task_runs = _analyze_flow_tasks(flow)
    normalized_pins = tuple(
        sorted(policy_pins, key=lambda item: (item.category, item.key, item.revision or 0))
    )
    nodes = tuple(_determinism_node(node) for node in plan)
    dynamic_bounds = tuple(
        bound for node in plan if (bound := _dynamic_bound(node, task_analysis)) is not None
    )
    nondeterministic_operations = tuple(
        NondeterministicOperation(taskId=task.id, taskType=task.type)
        for task in _walk_tasks(flow)
        if task.type not in FLOWABLE_MODES and task.type not in _DETERMINISTIC_RUNNABLE_TYPES
    )
    plugin_set_hash = canonical_hash(dict(plugin_set))
    payload = {
        "schemaVersion": DETERMINISM_ENVELOPE_VERSION,
        "revision": flow.revision,
        "semanticHash": semantic_hash,
        "pluginSetHash": plugin_set_hash,
        "policyPins": [item.model_dump(mode="json", by_alias=True) for item in normalized_pins],
        "nodes": [item.model_dump(mode="json", by_alias=True) for item in nodes],
        "dynamicBounds": [item.model_dump(mode="json", by_alias=True) for item in dynamic_bounds],
        "maximumTaskNestingDepth": MAX_TASK_NESTING_DEPTH,
        "configuredTaskNestingDepth": configured_nesting_depth,
        "worstCaseTaskRuns": worst_case_task_runs,
        "nondeterministicOperations": [
            item.model_dump(mode="json", by_alias=True) for item in nondeterministic_operations
        ],
    }
    return DeterminismEnvelope(
        revision=flow.revision,
        semanticHash=semantic_hash,
        pluginSetHash=plugin_set_hash,
        policyPins=normalized_pins,
        nodes=nodes,
        dynamicBounds=dynamic_bounds,
        maximumTaskNestingDepth=MAX_TASK_NESTING_DEPTH,
        configuredTaskNestingDepth=configured_nesting_depth,
        worstCaseTaskRuns=worst_case_task_runs,
        nondeterministicOperations=nondeterministic_operations,
        envelopeDigest=canonical_hash(payload),
    )


def admission_policy_pins(metadata: Mapping[str, Any] | None) -> tuple[DeterminismPolicyPin, ...]:
    if metadata is None:
        return ()
    raw_pins = metadata.get("policyPins")
    if not isinstance(raw_pins, list):
        return ()
    pins: list[DeterminismPolicyPin] = []
    for raw_pin in raw_pins:
        if not isinstance(raw_pin, Mapping):
            continue
        key = raw_pin.get("policyKey")
        revision = raw_pin.get("revision")
        digest = raw_pin.get("digest")
        if isinstance(key, str) and isinstance(revision, int) and isinstance(digest, str):
            pins.append(
                DeterminismPolicyPin(
                    category="ADMISSION",
                    key=key,
                    revision=revision,
                    digest=digest,
                )
            )
    return tuple(pins)


def _determinism_node(node: PlannedTask) -> DeterminismNode:
    return DeterminismNode(
        logicalId=node.task.id,
        taskType=node.task.type,
        order=node.order,
        parentId=node.parent_id,
        branchId=node.branch_id,
        dependencies=node.dependencies,
        lifecyclePhase=node.lifecycle_phase.value,
        mode=node.mode,
        maxConcurrency=node.max_concurrency,
    )


def _dynamic_bound(
    node: PlannedTask,
    task_analysis: Mapping[int, _TaskAnalysis],
) -> DynamicExecutionBound | None:
    task = node.task
    extra = task.configuration
    if node.mode in DYNAMIC_FLOWABLE_MODES:
        max_iterations = _positive_int(extra.get("maxIterations"), _LOOP_DEFAULT_MAX_ITERATIONS)
        max_task_runs = _positive_int(extra.get("maxTaskRuns"), _LOOP_DEFAULT_MAX_TASK_RUNS)
        child_worst_case = sum(
            task_analysis[id(child)].worst_case_task_runs for child in task.tasks
        )
        return DynamicExecutionBound(
            taskId=task.id,
            kind=node.mode or task.type,
            templateTaskIds=tuple(child.id for child in task.tasks),
            maxIterations=max_iterations,
            maxDurationSeconds=_positive_float(
                extra.get("maxDurationSeconds"),
                _LOOP_DEFAULT_MAX_DURATION_SECONDS,
            ),
            maxTaskRuns=max_task_runs,
            maxConcurrency=task.max_concurrency or 1,
            inlinePayloadBytes=_positive_int(
                extra.get("inlinePayloadBytes"),
                _LOOP_DEFAULT_INLINE_PAYLOAD_BYTES,
            ),
            iterationKeyPattern=f"{task.id}:{{index:08d}}",
            worstCaseTaskRuns=1 + max_iterations * child_worst_case,
        )
    if task.type == "core.subflow":
        return DynamicExecutionBound(
            taskId=task.id,
            kind="SUBFLOW",
            maxDepth=_positive_int(extra.get("maxDepth"), _SUBFLOW_DEFAULT_MAX_DEPTH),
            maxConcurrency=task.max_concurrency or 1,
            worstCaseTaskRuns=1,
        )
    return None


def _walk_tasks(flow: FlowDefinition) -> tuple[TaskDefinition, ...]:
    tasks: list[TaskDefinition] = []

    def walk(group: list[TaskDefinition]) -> None:
        for task in group:
            tasks.append(task)
            for _branch, children in task.child_task_groups():
                walk(children)
            walk(task.errors)

    walk(flow.tasks)
    walk(flow.errors)
    walk(flow.finally_tasks)
    walk(flow.after_execution)
    return tuple(tasks)


def _analyze_flow_tasks(
    flow: FlowDefinition,
) -> tuple[dict[int, _TaskAnalysis], int, int]:
    analyses: dict[int, _TaskAnalysis] = {}

    def analyze(task: TaskDefinition) -> _TaskAnalysis:
        children = tuple(
            [child for _branch, group in task.child_task_groups() for child in group]
            + list(task.errors)
        )
        child_analyses = tuple(analyze(child) for child in children)
        child_runs = sum(item.worst_case_task_runs for item in child_analyses)
        mode = FLOWABLE_MODES.get(task.type)
        worst_case_runs = 1 + child_runs
        if mode in DYNAMIC_FLOWABLE_MODES:
            max_iterations = _positive_int(
                task.configuration.get("maxIterations"),
                _LOOP_DEFAULT_MAX_ITERATIONS,
            )
            worst_case_runs = 1 + max_iterations * child_runs
        analysis = _TaskAnalysis(
            nesting_depth=1
            + max(
                (item.nesting_depth for item in child_analyses),
                default=0,
            ),
            worst_case_task_runs=worst_case_runs,
        )
        analyses[id(task)] = analysis
        return analysis

    roots = (*flow.tasks, *flow.errors, *flow.finally_tasks, *flow.after_execution)
    root_analyses = tuple(analyze(task) for task in roots)
    return (
        analyses,
        max((item.nesting_depth for item in root_analyses), default=1),
        sum(item.worst_case_task_runs for item in root_analyses),
    )


def _positive_int(value: Any, default: int) -> int:
    return (
        value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else default
    )


def _positive_float(value: Any, default: float) -> float:
    return (
        float(value)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0
        else default
    )
