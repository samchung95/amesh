from pathlib import Path

from amesh.dsl import validate_flow_document


def test_example_flow_is_valid() -> None:
    result = validate_flow_document(Path("examples/hello-world.yaml").read_bytes())
    assert result.valid
    assert result.semantic_hash
    assert result.canonical
    assert result.canonical["id"] == "hello_world"


def test_duplicate_task_id_is_rejected() -> None:
    result = validate_flow_document(
        '''
id: duplicate
namespace: tests
tasks:
  - id: same
    type: core.log
  - id: same
    type: core.return
'''
    )
    assert not result.valid
    assert any(issue.code == "duplicate_task_id" for issue in result.issues)


def test_dependency_cycle_is_rejected() -> None:
    result = validate_flow_document(
        '''
id: cycle
namespace: tests
tasks:
  - id: a
    type: core.return
    dependsOn: [b]
  - id: b
    type: core.return
    dependsOn: [a]
'''
    )
    assert not result.valid
    assert any(issue.code == "dependency_cycle" for issue in result.issues)


def test_semantic_hash_ignores_mapping_order() -> None:
    left = validate_flow_document(
        '{"id":"x","namespace":"tests","tasks":[{"id":"a","type":"core.return","value":1}]}'
    )
    right = validate_flow_document(
        '{"tasks":[{"type":"core.return","value":1,"id":"a"}],"namespace":"tests","id":"x"}'
    )
    assert left.valid and right.valid
    assert left.semantic_hash == right.semantic_hash
