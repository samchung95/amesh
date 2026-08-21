from __future__ import annotations

import json
from time import perf_counter

import pytest

from amesh.dsl import (
    EditorMetadata,
    ResourceKind,
    ResourceSchemaDescriptor,
    default_resource_registry,
    parse_editable_flow_document,
    validate_flow_document,
)


def test_yaml_and_json_produce_the_same_versioned_canonical_ir() -> None:
    document = {
        "id": "same",
        "namespace": "tests.dsl",
        "tasks": [{"id": "done", "type": "core.return", "value": 1}],
    }
    yaml_result = validate_flow_document(
        "id: same\nnamespace: tests.dsl\ntasks:\n  - id: done\n    type: core.return\n    value: 1\n"
    )
    json_result = validate_flow_document(json.dumps(document))

    assert yaml_result.valid and json_result.valid
    assert yaml_result.ir_version == "amesh.flow/v1"
    assert yaml_result.canonical == json_result.canonical
    assert yaml_result.canonical is not None
    assert yaml_result.canonical["apiVersion"] == "amesh.flow/v1"
    assert yaml_result.semantic_hash == json_result.semantic_hash


def test_round_trip_edit_preserves_comments_and_existing_layout() -> None:
    source = """# owner note
id: editable # stable id
namespace: tests.dsl
tasks:
  - id: done
    type: core.return
    value: before # output note
"""
    document = parse_editable_flow_document(source)
    document.set_value(("tasks", 0, "value"), "after")
    rendered = document.render()

    assert "# owner note" in rendered
    assert "id: editable # stable id" in rendered
    assert "value: after" in rendered
    assert "# output note" in rendered
    assert document.render() == rendered
    assert validate_flow_document(rendered).valid


def test_all_supported_flow_sections_enter_the_canonical_ir() -> None:
    result = validate_flow_document(
        """apiVersion: amesh.flow/v1
id: complete
namespace: tests.dsl
description: complete shape
labels: {team: platform}
inputs:
  - id: name
    type: STRING
variables: {greeting: hello}
triggers:
  - id: inbound
    type: core.webhook
tasks:
  - id: main
    type: core.return
    value: "{{ vars.greeting }} {{ inputs.name }}"
errors:
  - id: recover
    type: core.return
    value: failed
finally:
  - id: cleanup
    type: core.return
    value: done
outputs: {result: "{{ outputs.main.value }}"}
x-editor-state: {zoom: 1}
"""
    )

    assert result.valid
    assert result.canonical is not None
    assert set(result.canonical) >= {
        "apiVersion",
        "id",
        "namespace",
        "description",
        "labels",
        "inputs",
        "variables",
        "triggers",
        "tasks",
        "errors",
        "finally",
        "outputs",
        "x-editor-state",
    }


def test_unknown_core_field_is_rejected_but_x_extension_is_hashed() -> None:
    unknown = validate_flow_document(
        "id: extension\nnamespace: tests.dsl\ntaks: []\ntasks:\n  - id: done\n    type: core.return\n"
    )
    extension = validate_flow_document(
        "id: extension\nnamespace: tests.dsl\nx-team: platform\ntasks:\n  - id: done\n    type: core.return\n"
    )

    assert not unknown.valid
    assert unknown.issues[0].code == "unknown_core_field"
    assert unknown.issues[0].path == "taks"
    assert unknown.issues[0].source_range is not None
    assert extension.valid
    assert extension.canonical is not None
    assert extension.canonical["x-team"] == "platform"


def test_every_source_validation_issue_has_range_and_remediation_hint() -> None:
    result = validate_flow_document(
        """id: invalid
namespace: tests.dsl
inputs:
  - id: duplicate
    type: STRING
  - id: duplicate
    type: STRING
tasks:
  - id: one
    type: core.return
    dependsOn: [missing]
  - id: two
    type: core.http
    url: 42
"""
    )

    assert not result.valid
    assert {issue.code for issue in result.issues} >= {
        "duplicate_id",
        "missing_dependency",
        "resource_schema_validation",
    }
    assert all(issue.source_range is not None for issue in result.issues)
    assert all(issue.hint for issue in result.issues)


def test_plugin_schema_validates_configuration_and_generates_editor_metadata() -> None:
    registry = default_resource_registry()
    registry.register(
        ResourceSchemaDescriptor(
            type="plugin.email",
            kind=ResourceKind.TASK,
            configuration_schema={
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {"to": {"type": "string"}},
                "required": ["to"],
                "additionalProperties": False,
            },
            editor=EditorMetadata(
                title="Email",
                description="Send a message.",
                category="Communication",
                property_order=("to",),
            ),
        )
    )
    invalid = validate_flow_document(
        "id: plugin\nnamespace: tests.dsl\ntasks:\n  - id: send\n    type: plugin.email\n    subject: nope\n",
        registry=registry,
    )
    valid = validate_flow_document(
        "id: plugin\nnamespace: tests.dsl\ntasks:\n  - id: send\n    type: plugin.email\n    to: team@example.com\n",
        registry=registry,
    )
    catalog_entry = next(
        item for item in registry.catalog()["resources"] if item["type"] == "plugin.email"
    )

    assert not invalid.valid
    assert {issue.code for issue in invalid.issues} == {"resource_schema_validation"}
    assert valid.valid
    assert catalog_entry["editor"]["propertyOrder"] == ["to"]
    assert catalog_entry["configurationSchema"]["required"] == ["to"]


def test_duplicate_yaml_mapping_key_has_a_machine_readable_location() -> None:
    result = validate_flow_document(
        "id: first\nid: second\nnamespace: tests.dsl\ntasks:\n  - id: done\n    type: core.return\n"
    )

    assert not result.valid
    assert result.issues[0].code == "invalid_yaml"
    assert result.issues[0].source_range is not None
    assert result.issues[0].source_range.start.line == 2


def test_semantic_hash_ignores_comments_and_yaml_formatting() -> None:
    compact = validate_flow_document(
        "{id: hash, namespace: tests.dsl, tasks: [{id: done, type: core.return, value: 1}]}"
    )
    commented = validate_flow_document(
        """# formatting is not semantic
id: hash
namespace: tests.dsl
tasks:
  - id: done # stable
    type: core.return
    value: 1
"""
    )

    assert compact.valid and commented.valid
    assert compact.semantic_hash == commented.semantic_hash


@pytest.mark.parametrize("runs", [5])
@pytest.mark.no_cover
def test_five_thousand_line_flow_validation_p95_is_below_one_second(runs: int) -> None:
    task_lines = [
        f"  - id: task_{index}\n    type: core.return\n    description: task {index}\n    value: {index}"
        for index in range(1_250)
    ]
    source = "id: large\nnamespace: tests.performance\ntasks:\n" + "\n".join(task_lines) + "\n"
    assert len(source.splitlines()) >= 5_000

    durations = []
    for _ in range(runs):
        started = perf_counter()
        result = validate_flow_document(source)
        durations.append(perf_counter() - started)
        assert result.valid

    p95 = sorted(durations)[-1]
    assert p95 < 1.0, f"5,000-line validation p95 was {p95:.3f}s"
