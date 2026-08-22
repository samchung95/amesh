from pathlib import Path

import pytest

from amesh.dsl import FlowDefinition, compile_flow_tasks, validate_flow_document, visible_output_ids
from amesh.dsl.models import TaskDefinition


def test_example_flow_is_valid() -> None:
    result = validate_flow_document(Path("examples/hello-world.yaml").read_bytes())
    assert result.valid
    assert result.semantic_hash
    assert result.canonical
    assert result.canonical["id"] == "hello_world"


def test_duplicate_task_id_is_rejected() -> None:
    result = validate_flow_document(
        """
id: duplicate
namespace: tests
tasks:
  - id: same
    type: core.log
  - id: same
    type: core.return
"""
    )
    assert not result.valid
    assert any(issue.code == "duplicate_task_id" for issue in result.issues)


def test_dependency_cycle_is_rejected() -> None:
    result = validate_flow_document(
        """
id: cycle
namespace: tests
tasks:
  - id: a
    type: core.return
    dependsOn: [b]
  - id: b
    type: core.return
    dependsOn: [a]
"""
    )
    assert not result.valid
    assert any(issue.code == "dependency_cycle" for issue in result.issues)


def test_nested_flowables_compile_to_a_deterministic_plan() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "nested",
            "namespace": "tests",
            "tasks": [
                {
                    "id": "sequence",
                    "type": "core.sequential",
                    "failurePolicy": "CONTINUE_ON_ERROR",
                    "tasks": [
                        {"id": "first", "type": "core.return"},
                        {"id": "second", "type": "core.return"},
                    ],
                },
                {
                    "id": "after",
                    "type": "core.return",
                    "dependsOn": ["sequence"],
                },
            ],
        }
    )

    plan = compile_flow_tasks(flow)

    assert [node.task.id for node in plan] == ["sequence", "first", "second", "after"]
    assert [node.dependencies for node in plan] == [(), (), ("first",), ("sequence",)]
    assert plan[0].children == ("first", "second")
    assert visible_output_ids("second", plan) == frozenset({"first"})
    assert visible_output_ids("after", plan) == frozenset({"sequence"})


def test_working_directory_flowable_is_sequential_and_paths_are_bounded() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "workspace",
            "namespace": "tests",
            "tasks": [
                {
                    "id": "shared",
                    "type": "core.workingDirectory",
                    "inputFiles": {"input/data.txt": "s3://bucket/input"},
                    "outputFiles": ["*.txt"],
                    "maxConcurrency": 1,
                    "tasks": [
                        {"id": "first", "type": "core.shell", "command": ["one"]},
                        {"id": "second", "type": "core.shell", "command": ["two"]},
                    ],
                }
            ],
        }
    )

    plan = compile_flow_tasks(flow)
    assert [node.mode for node in plan] == ["WORKING_DIRECTORY", None, None]
    assert plan[2].dependencies == ("first",)

    for field, value in (
        ("inputFiles", {"../escape": "s3://bucket/input"}),
        ("outputFiles", ["/absolute.txt"]),
        ("outputManifest", "../manifest.json"),
    ):
        payload = flow.tasks[0].model_dump(mode="python", by_alias=True)
        payload[field] = value
        with pytest.raises(ValueError, match="workspace paths"):
            TaskDefinition.model_validate(payload)


def test_nested_flowable_dependencies_are_validated_within_their_sibling_scope() -> None:
    result = validate_flow_document(
        """
id: nested_invalid
namespace: tests
tasks:
  - id: graph
    type: core.dag
    tasks:
      - id: a
        type: core.return
        dependsOn: [b]
      - id: b
        type: core.return
        dependsOn: [a]
      - id: missing
        type: core.return
        dependsOn: [outside]
"""
    )

    assert not result.valid
    assert {issue.code for issue in result.issues} >= {
        "dependency_cycle",
        "missing_dependency",
    }


def test_conditional_flowables_compile_ordered_branch_paths() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "conditional",
            "namespace": "tests",
            "tasks": [
                {
                    "id": "choose",
                    "type": "core.if",
                    "condition": "{{ inputs.route == 'primary' }}",
                    "then": [{"id": "primary", "type": "core.return"}],
                    "elseIf": [
                        {
                            "id": "secondary",
                            "condition": "{{ inputs.route == 'secondary' }}",
                            "tasks": [{"id": "secondary_task", "type": "core.return"}],
                        }
                    ],
                    "else": [{"id": "fallback", "type": "core.return"}],
                },
                {
                    "id": "switch",
                    "type": "core.switch",
                    "value": "{{ inputs.tier }}",
                    "cases": {
                        "paid": [{"id": "paid", "type": "core.return"}],
                        "default": [{"id": "free", "type": "core.return"}],
                    },
                    "predicateCases": [
                        {
                            "id": "priority",
                            "condition": "{{ inputs.score > 90 }}",
                            "tasks": [{"id": "priority", "type": "core.return"}],
                        }
                    ],
                },
            ],
        }
    )

    plan = compile_flow_tasks(flow)

    assert [node.task.id for node in plan] == [
        "choose",
        "primary",
        "secondary_task",
        "fallback",
        "switch",
        "paid",
        "priority",
        "free",
    ]
    assert [node.branch_id for node in plan] == [
        None,
        "then",
        "else-if:secondary",
        "else",
        None,
        "case:paid",
        "predicate:priority",
        "default",
    ]


def test_static_conditional_duplicates_and_unreachable_branches_are_rejected() -> None:
    result = validate_flow_document(
        """
id: invalid_conditions
namespace: tests
tasks:
  - id: choose
    type: core.if
    condition: "{{ inputs.enabled }}"
    then:
      - id: first
        type: core.return
    elseIf:
      - id: always
        condition: "{{ true }}"
        tasks:
          - id: always_task
            type: core.return
      - id: duplicate
        condition: "{{ true }}"
        tasks:
          - id: duplicate_task
            type: core.return
    else:
      - id: unreachable
        type: core.return
"""
    )

    assert not result.valid
    assert {issue.code for issue in result.issues} >= {
        "duplicate_condition",
        "unreachable_branch",
    }


def test_condition_contract_composes_across_task_trigger_retry_error_and_output_contexts() -> None:
    result = validate_flow_document(
        """
id: condition_composition
namespace: tests
tasks:
  - id: optional
    type: core.return
    value: ready
    runIf: "{{ inputs.enabled }}"
    retry:
      maxAttempts: 2
      condition: "{{ taskrun.failureCategory == 'INFRASTRUCTURE' }}"
triggers:
  - id: schedule
    type: core.cron
    cron: "0 * * * *"
    condition: "{{ trigger.source == 'SCHEDULE' }}"
errors:
  - id: notify
    type: core.return
    value: failed
    runIf: "{{ execution.state == 'FAILED' }}"
outputs:
  selected: "{{ outputs.optional.value if inputs.enabled else 'skipped' }}"
"""
    )

    assert result.valid
    assert result.canonical is not None
    assert result.canonical["tasks"][0]["retry"]["condition"]
    assert result.canonical["triggers"][0]["condition"]
    assert result.canonical["errors"][0]["runIf"]
    assert result.canonical["outputs"]["selected"]


def test_snake_case_depends_on_is_honoured() -> None:
    result = validate_flow_document(
        """
id: cycle
namespace: tests
tasks:
  - id: a
    type: core.return
    depends_on: [b]
  - id: b
    type: core.return
    depends_on: [a]
"""
    )
    assert not result.valid
    assert any(issue.code == "dependency_cycle" for issue in result.issues)


def test_snake_case_and_camel_case_dependencies_hash_identically() -> None:
    snake = validate_flow_document(
        '{"id":"x","namespace":"tests","tasks":[{"id":"a","type":"core.return"},'
        '{"id":"b","type":"core.return","depends_on":["a"]}]}'
    )
    camel = validate_flow_document(
        '{"id":"x","namespace":"tests","tasks":[{"id":"a","type":"core.return"},'
        '{"id":"b","type":"core.return","dependsOn":["a"]}]}'
    )
    assert snake.valid and camel.valid
    assert snake.semantic_hash == camel.semantic_hash


def test_conflicting_dependency_spellings_are_rejected() -> None:
    result = validate_flow_document(
        '{"id":"x","namespace":"tests","tasks":[{"id":"a","type":"core.return"},'
        '{"id":"b","type":"core.return","dependsOn":["a"],"depends_on":["a"]}]}'
    )
    assert not result.valid
    assert any(issue.code == "schema_validation" for issue in result.issues)


def test_semantic_hash_ignores_mapping_order() -> None:
    left = validate_flow_document(
        '{"id":"x","namespace":"tests","tasks":[{"id":"a","type":"core.return","value":1}]}'
    )
    right = validate_flow_document(
        '{"tasks":[{"type":"core.return","value":1,"id":"a"}],"namespace":"tests","id":"x"}'
    )
    assert left.valid and right.valid
    assert left.semantic_hash == right.semantic_hash


def test_canonical_identifier_policy_is_applied_to_flow_components() -> None:
    result = validate_flow_document(
        """
id: bad flow
namespace: company..team
tasks:
  - id: bad task
    type: core.return
"""
    )

    assert not result.valid
    assert {issue.path for issue in result.issues} >= {"id", "namespace", "tasks.0.id"}


def test_lifecycle_handlers_validate_selectors_and_bounded_recursion() -> None:
    valid = validate_flow_document(
        """
id: lifecycle
namespace: tests
tasks:
  - id: group
    type: core.sequential
    tasks:
      - id: work
        type: core.return
    errors:
      - id: local_handler
        type: core.return
        errorSelector:
          states: [FAILED]
          categories: [USER_CODE]
          taskIds: [work]
          condition: "{{ error.taskId == 'work' }}"
finally:
  - id: cleanup
    type: core.return
afterExecution:
  - id: publish
    type: core.return
"""
    )
    recursive = validate_flow_document(
        """
id: recursive
namespace: tests
tasks:
  - id: work
    type: core.return
errors:
  - id: handler
    type: core.sequential
    errors:
      - id: nested_handler
        type: core.return
    tasks:
      - id: cleanup
        type: core.return
"""
    )
    misplaced = validate_flow_document(
        """
id: misplaced
namespace: tests
tasks:
  - id: work
    type: core.return
    errorSelector:
      states: [FAILED]
"""
    )

    assert valid.valid
    assert not recursive.valid
    assert any(issue.code == "recursive_error_handler" for issue in recursive.issues)
    assert not misplaced.valid
    assert any(issue.code == "misplaced_error_selector" for issue in misplaced.issues)
