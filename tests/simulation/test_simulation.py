from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from amesh.determinism import DeterminismPolicyPin, build_determinism_envelope
from amesh.domain import TaskRunState
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import reduce_orchestration
from amesh.ports import PersistedTaskRun
from amesh.simulation import (
    REDUCER_SEMANTICS_VERSION,
    SIMULATOR_VERSION,
    SimulationEstimateModel,
    SimulationFixture,
    SimulationFixtureSource,
    SimulationPolicyDecision,
    SimulationRequest,
    SimulationSubstitution,
    SimulationTaskState,
    compare_simulation_plans,
    simulate_flow,
    verify_simulation_evidence,
)


def _flow(*, revision: int = 3, include_archive: bool = False) -> FlowDefinition:
    tasks: list[dict[str, object]] = [
        {
            "id": "lookup",
            "type": "vendor.lookup",
            "retry": {"maxAttempts": 3, "delaySeconds": 1},
        },
        {
            "id": "route",
            "type": "core.if",
            "dependsOn": ["lookup"],
            "condition": "{{ trigger.kind == 'primary' }}",
            "then": [
                {
                    "id": "accepted",
                    "type": "core.return",
                    "value": "{{ outputs.lookup.status }}",
                }
            ],
            "else": [{"id": "rejected", "type": "core.return", "value": "rejected"}],
        },
    ]
    if include_archive:
        tasks.append(
            {
                "id": "archive",
                "type": "core.shell",
                "dependsOn": ["route"],
                "command": ["archive", "{{ inputs.customer }}"],
            }
        )
    return FlowDefinition.model_validate(
        {
            "id": "preview",
            "namespace": "team.data",
            "revision": revision,
            "inputs": [{"id": "customer", "type": "string", "required": True}],
            "concurrency": [
                {
                    "id": "customer",
                    "scope": "KEY",
                    "key": "{{ inputs.customer }}",
                    "limit": 1,
                }
            ],
            "tasks": tasks,
            "outputs": {"decision": "{{ outputs.accepted.value | default('unknown') }}"},
        }
    )


def _request(*, archive_fixture: bool = False) -> SimulationRequest:
    fixtures = {
        "lookup": SimulationFixture(
            source=SimulationFixtureSource.RECORDED,
            output={"status": "approved"},
            failuresBeforeSuccess=1,
            recordedAt=datetime(2026, 8, 23, tzinfo=UTC),
        )
    }
    if archive_fixture:
        fixtures["archive"] = SimulationFixture(output={"stored": True})
    return SimulationRequest(
        inputs={"customer": "acme"},
        triggerContext={"kind": "primary"},
        fixtures=fixtures,
        estimateModels={
            "vendor.lookup": SimulationEstimateModel(
                durationSeconds=0.5,
                apiCalls=1,
                costUsd=0.02,
            ),
            "core.shell": SimulationEstimateModel(
                durationSeconds=2,
                storageBytes=1024,
            ),
        },
    )


def test_simulation_expands_graph_evaluates_context_and_suppresses_side_effects() -> None:
    plan = simulate_flow(
        _flow(),
        _request(),
        plugin_set={"vendor.lookup": "2.1.0"},
        tenant_id="tenant-a",
    )

    tasks = {item.task_id: item for item in plan.tasks}
    assert plan.simulator_version == SIMULATOR_VERSION
    assert plan.reducer_semantics_version == REDUCER_SEMANTICS_VERSION
    assert plan.side_effects_suppressed is True
    assert tasks["lookup"].substitution is SimulationSubstitution.RECORDED
    assert tasks["lookup"].attempts == 2
    assert tasks["lookup"].state is SimulationTaskState.SUCCESS
    assert tasks["accepted"].state is SimulationTaskState.SUCCESS
    assert tasks["rejected"].state is SimulationTaskState.SKIPPED
    assert tasks["lookup"].concurrency_buckets == ("EXECUTION:KEY:tenant-a/acme",)
    assert plan.estimates.task_count == 4
    assert plan.estimates.api_calls == 2
    assert plan.estimates.cost_usd == 0.04
    assert plan.unknowns == ()


def test_schema_only_and_missing_fixtures_are_explicit() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "unknowns",
            "namespace": "tests.simulation",
            "tasks": [
                {"id": "declared", "type": "vendor.schema"},
                {"id": "missing", "type": "vendor.external"},
            ],
        }
    )
    request = SimulationRequest(
        fixtures={
            "declared": SimulationFixture(
                source="SCHEMA_ONLY",
                outputSchema={
                    "type": "object",
                    "properties": {"count": {"type": "integer"}},
                },
            )
        }
    )

    plan = simulate_flow(flow, request)
    tasks = {item.task_id: item for item in plan.tasks}

    assert tasks["declared"].substitution is SimulationSubstitution.SCHEMA_ONLY
    assert tasks["declared"].output == {"count": 0}
    assert tasks["missing"].state is SimulationTaskState.UNKNOWN
    assert "TASK_OUTPUT_UNKNOWN:tasks.missing" in {
        f"{item.code}:{item.path}" for item in plan.unknowns
    }
    assert plan.estimates.critical_path_seconds is None


def test_signed_evidence_is_deterministic_and_tamper_evident() -> None:
    key = b"simulation-test-signing-key-32-bytes-minimum"
    plan = simulate_flow(_flow(), _request(), signing_key=key, signing_key_id="test-key")

    assert plan.evidence is not None
    assert plan.evidence.key_id == "test-key"
    assert verify_simulation_evidence(plan, key) is True
    tampered = plan.model_copy(update={"semantic_hash": "tampered"})
    assert verify_simulation_evidence(tampered, key) is False


def test_plan_diff_compares_revisions_plugins_estimates_and_unknowns() -> None:
    before = simulate_flow(
        _flow(revision=3),
        _request(),
        plugin_set={"vendor.lookup": "2.1.0"},
    )
    after = simulate_flow(
        _flow(revision=4, include_archive=True),
        _request(archive_fixture=True),
        plugin_set={"vendor.lookup": "2.2.0"},
    )

    diff = compare_simulation_plans(before, after)

    assert diff.plugin_set_changed is True
    assert diff.added_tasks == ("archive",)
    assert diff.estimate_delta["storageBytes"] == 1024
    assert diff.before_plan_id != diff.after_plan_id


def test_simulator_graph_conforms_to_real_reducer_initial_readiness() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "reducer_conformance",
            "namespace": "tests.simulation",
            "tasks": [
                {"id": "left", "type": "core.return", "value": "left"},
                {"id": "right", "type": "core.return", "value": "right"},
                {
                    "id": "join",
                    "type": "core.return",
                    "dependsOn": ["left", "right"],
                    "value": "joined",
                },
            ],
        }
    )
    plan = simulate_flow(flow, SimulationRequest())
    execution_id = uuid4()
    runs = [
        PersistedTaskRun(
            task_run_id=uuid4(),
            execution_id=execution_id,
            task_id=task_id,
            state=TaskRunState.WAITING,
            current_attempt=0,
            version=1,
        )
        for task_id in ("left", "right", "join")
    ]

    reducer = reduce_orchestration(flow, runs, now=datetime(2026, 8, 23, tzinfo=UTC))
    simulator_ready = tuple(
        item.task_id for item in plan.tasks if not item.dependencies and item.parent_id is None
    )

    assert reducer.runnable_task_ids == simulator_ready == ("left", "right")


def test_deterministic_envelope_pins_dynamic_bounds_and_stable_logical_order() -> None:
    source = {
        "id": "bounded",
        "namespace": "tests.simulation",
        "revision": 7,
        "tasks": [
            {
                "id": "route",
                "type": "core.if",
                "condition": "{{ true }}",
                "then": [{"id": "external", "type": "vendor.call"}],
                "else": [{"id": "fallback", "type": "core.return", "value": "safe"}],
            },
            {
                "id": "items",
                "type": "core.foreach",
                "items": ["a", "b"],
                "maxIterations": 3,
                "maxDurationSeconds": 12,
                "maxTaskRuns": 6,
                "inlinePayloadBytes": 128,
                "maxConcurrency": 2,
                "tasks": [
                    {"id": "prepare", "type": "core.return", "value": "ready"},
                    {"id": "publish", "type": "core.return", "value": "done"},
                ],
            },
            {
                "id": "child",
                "type": "core.subflow",
                "flowId": "child_flow",
                "revision": 2,
                "maxDepth": 4,
            },
        ],
    }
    flow = FlowDefinition.model_validate(source)
    decision = SimulationPolicyDecision(
        category="PLUGIN",
        policyId="plugin-decision-1",
        allowed=True,
        reason="allowed",
        details={"source": "policy-1"},
    )

    first = simulate_flow(
        flow,
        SimulationRequest(),
        semantic_hash="semantic-7",
        plugin_set={"vendor.call": "2.0.0"},
        policy_decisions=(decision,),
        determinism_policy_pins=(
            DeterminismPolicyPin(
                category="ADMISSION",
                key="release",
                revision=2,
                digest="policy-digest",
            ),
        ),
    ).deterministic_envelope
    second = simulate_flow(
        FlowDefinition.model_validate(flow.model_dump(mode="json", by_alias=True)),
        SimulationRequest(),
        semantic_hash="semantic-7",
        plugin_set={"vendor.call": "2.0.0"},
        policy_decisions=(decision,),
        determinism_policy_pins=(
            DeterminismPolicyPin(
                category="ADMISSION",
                key="release",
                revision=2,
                digest="policy-digest",
            ),
        ),
    ).deterministic_envelope

    assert first.envelope_digest == second.envelope_digest
    assert first.nodes == second.nodes
    assert first.revision == 7
    assert first.semantic_hash == "semantic-7"
    assert first.policy_pins[0].key == "release"
    assert next(node for node in first.nodes if node.logical_id == "external").branch_id == "then"
    loop = next(bound for bound in first.dynamic_bounds if bound.task_id == "items")
    assert loop.model_dump(mode="json", by_alias=True) == {
        "taskId": "items",
        "kind": "FOREACH",
        "templateTaskIds": ["prepare", "publish"],
        "maxIterations": 3,
        "maxDurationSeconds": 12.0,
        "maxTaskRuns": 6,
        "maxConcurrency": 2,
        "maxDepth": None,
        "inlinePayloadBytes": 128,
        "iterationKeyPattern": "items:{index:08d}",
        "worstCaseTaskRuns": 7,
    }
    subflow = next(bound for bound in first.dynamic_bounds if bound.task_id == "child")
    assert subflow.max_depth == 4
    assert {item.task_id for item in first.nondeterministic_operations} == {
        "external",
        "child",
    }


def test_determinism_analysis_has_bounded_configuration_access_at_maximum_depth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    width = 40
    nested: list[dict[str, object]] = [
        {"id": f"leaf_0_{index}", "type": "core.return", "value": index} for index in range(width)
    ]
    for depth in range(1, 16):
        nested = [
            {
                "id": f"group_{depth}",
                "type": "core.sequential",
                "tasks": nested,
            },
            *[
                {
                    "id": f"leaf_{depth}_{index}",
                    "type": "core.return",
                    "value": index,
                }
                for index in range(width)
            ],
        ]
    flow = FlowDefinition.model_validate(
        {
            "id": "bounded-analysis",
            "namespace": "tests.performance",
            "tasks": nested,
        }
    )
    task_count = 16 * width + 15
    accesses = 0
    configuration = TaskDefinition.configuration

    def tracked_configuration(task: TaskDefinition) -> object:
        nonlocal accesses
        accesses += 1
        return configuration.__get__(task, TaskDefinition)

    monkeypatch.setattr(TaskDefinition, "configuration", property(tracked_configuration))

    envelope = build_determinism_envelope(
        flow,
        semantic_hash="semantic",
        plugin_set={},
    )

    assert len(envelope.nodes) == task_count
    assert envelope.configured_task_nesting_depth == 16
    assert envelope.worst_case_task_runs == task_count
    assert accesses == task_count
