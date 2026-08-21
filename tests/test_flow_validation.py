from pathlib import Path

from amesh.dsl import FlowDefinition, compile_flow_tasks, validate_flow_document, visible_output_ids


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
