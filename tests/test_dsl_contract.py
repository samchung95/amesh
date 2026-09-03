from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from typing import Any, cast

import pytest
from pydantic import ValidationError

from amesh.dsl import (
    EditorMetadata,
    ResourceKind,
    ResourceSchemaDescriptor,
    TaskConfiguration,
    TaskDefinition,
    TaskRuntimeOwnership,
    TaskSpecification,
    TaskTimeoutMode,
    default_resource_registry,
    parse_editable_flow_document,
    validate_flow_document,
)
from amesh.dsl.handler_contracts import (
    bind_builtin_handler_contract,
    builtin_handler_contract,
)
from amesh.dsl.models import FlowDefinition
from amesh.dsl.specifications import agent_task_specifications, core_task_specifications
from amesh.dsl.task_configuration import TASK_STRUCTURAL_FIELDS
from amesh.dsl.validator import TASK_STRUCTURAL_FIELDS as VALIDATOR_TASK_STRUCTURAL_FIELDS


def test_every_builtin_task_specification_is_authoritative_in_default_registry() -> None:
    specifications = (*core_task_specifications(), *agent_task_specifications())
    registry = default_resource_registry()
    catalog_tasks = {
        item["type"]: item
        for item in registry.catalog()["resources"]
        if item["kind"] == ResourceKind.TASK.value
    }

    assert (
        len(specifications) == len({specification.type for specification in specifications}) == 50
    )
    assert set(catalog_tasks) == {specification.type for specification in specifications}
    for specification in specifications:
        assert isinstance(specification, TaskSpecification)
        assert specification.kind is ResourceKind.TASK
        assert specification.configuration_schema == (
            specification.configuration_contract.model_json_schema()
        )
        assert specification.configuration_schema == (
            builtin_handler_contract(specification.type).model_json_schema()
        )
        assert registry.task_specification(specification.type) == specification
        assert registry.descriptor(ResourceKind.TASK, specification.type) == (
            specification.descriptor
        )
        assert catalog_tasks[specification.type] == {
            "type": specification.type,
            "kind": specification.kind.value,
            "configurationSchema": dict(specification.configuration_schema),
            "editor": specification.editor.as_dict(),
        }


def test_non_model_builtin_schema_drift_is_rejected_by_runtime_authority() -> None:
    drifted_schema = {
        "type": "object",
        "properties": {
            "value": {},
            "timeoutSeconds": {"type": "number", "exclusiveMinimum": 0},
            "unexpected": {"type": "string"},
        },
        "additionalProperties": False,
    }

    with pytest.raises(
        ValueError,
        match=r"task specification schema drifted from handler contract: core\.return",
    ):
        bind_builtin_handler_contract("core.return", drifted_schema)


def test_builtin_task_ownership_is_explicit_and_plugin_kinds_remain_dynamic() -> None:
    registry = default_resource_registry()
    specifications = registry.task_specifications()

    assert all(
        specification.runtime_ownership
        in {
            TaskRuntimeOwnership.HANDLER,
            TaskRuntimeOwnership.EXECUTOR,
            TaskRuntimeOwnership.FLOWABLE,
        }
        for specification in specifications
    )
    registry.register(
        ResourceSchemaDescriptor(
            type="vendor.dynamic",
            kind=ResourceKind.TASK,
            configuration_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
                "additionalProperties": False,
            },
            editor=EditorMetadata(
                title="Dynamic",
                description="A dynamically registered plugin task.",
                category="Plugins",
            ),
        )
    )

    assert registry.task_specification("vendor.dynamic") is None
    assert registry.validate(ResourceKind.TASK, "vendor.dynamic", {"message": "ok"}) == ()


def test_explicit_null_configuration_is_validated_and_handler_view_stays_raw() -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "switch",
            "type": "core.switch",
            "value": None,
            "cases": {"default": [{"id": "done", "type": "core.return", "value": "ok"}]},
        }
    )
    result = validate_flow_document(
        """id: explicit-null
namespace: tests.dsl
tasks:
  - id: switch
    type: core.switch
    value: null
    cases:
      default:
        - id: done
          type: core.return
          value: ok
"""
    )

    assert dict(task.configuration) == {"value": None}
    assert dict(task.configuration.handler_view()) == {"value": None}
    assert result.valid, result.issues


def test_configuration_contract_serializes_datetime_and_preserves_handler_value() -> None:
    deadline = datetime(2026, 9, 3, tzinfo=UTC)
    task = TaskDefinition.model_validate(
        {
            "id": "approval",
            "type": "core.approval",
            "title": "Review request",
            "assigneeIds": ["11111111-1111-4111-8111-111111111111"],
            "deadlineAt": deadline,
        }
    )

    assert task.configuration["deadlineAt"] == "2026-09-03T00:00:00Z"
    assert task.configuration.handler_view()["deadlineAt"] == deadline
    assert not default_resource_registry().validate(
        ResourceKind.TASK,
        task.type,
        task.configuration,
    )


def test_canonical_flow_revalidation_is_idempotent() -> None:
    first = validate_flow_document(
        """id: canonical-round-trip
namespace: tests.dsl
tasks:
  - id: result
    type: core.return
    value: ready
"""
    )
    assert first.valid, first.issues
    assert first.canonical is not None

    second = validate_flow_document(first.canonical)

    assert second.valid, second.issues
    assert second.canonical == first.canonical
    assert second.semantic_hash == first.semantic_hash


def test_task_configuration_and_canonical_task_models_are_immutable() -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "done",
            "type": "core.return",
            "runLabels": {"stage": "acceptance"},
            "value": {"nested": []},
        }
    )
    configuration = task.configuration

    assert isinstance(configuration, TaskConfiguration)
    assert configuration.kind == "core.return"
    assert dict(configuration) == {"value": {"nested": []}}
    with pytest.raises(ValidationError, match="Instance is frozen"):
        cast(Any, task).id = "changed"
    with pytest.raises(TypeError):
        cast(Any, configuration)["value"] = "changed"

    detached_value = cast(dict[str, list[str]], configuration["value"])
    detached_value["nested"].append("changed")
    mutable = configuration.mutable_copy()
    cast(dict[str, list[str]], mutable["value"])["nested"].append("also changed")

    assert task.configuration["value"] == {"nested": []}
    dumped = task.model_dump(mode="json", by_alias=True, exclude_none=True)
    assert dumped["runLabels"] == {"stage": "acceptance"}
    assert dumped["value"] == {"nested": []}
    assert "configuration" not in dumped
    assert TaskDefinition.model_validate(dumped) == task


def test_task_structural_fields_have_one_authority_and_preserve_filtering_semantics() -> None:
    assert VALIDATOR_TASK_STRUCTURAL_FIELDS is TASK_STRUCTURAL_FIELDS
    assert (
        frozenset(
            {
                "id",
                "type",
                "description",
                "runLabels",
                "dependsOn",
                "runIf",
                "conditionErrorPolicy",
                "retry",
                "tasks",
                "condition",
                "then",
                "elseIf",
                "else",
                "cases",
                "predicateCases",
                "errors",
                "errorSelector",
                "contract",
                "taskCache",
            }
        )
        == TASK_STRUCTURAL_FIELDS
    )

    loop = TaskDefinition.model_validate(
        {
            "id": "loop",
            "type": "core.while",
            "condition": "{{ outputs.keepGoing }}",
            "maxIterations": 2,
            "tasks": [{"id": "done", "type": "core.return", "value": True}],
        }
    )
    plugin_task = TaskDefinition.model_validate(
        {
            "id": "plugin",
            "type": "vendor.example",
            "message": "hello",
            "x-debug": True,
        }
    )

    assert dict(loop.configuration) == {
        "condition": "{{ outputs.keepGoing }}",
        "maxIterations": 2,
    }
    assert dict(plugin_task.configuration) == {"message": "hello"}


def test_task_configuration_does_not_serialize_descendant_tasks() -> None:
    unserializable_child_value = object()
    task = TaskDefinition.model_validate(
        {
            "id": "parent",
            "type": "core.sequential",
            "tasks": [
                {
                    "id": "child",
                    "type": "core.return",
                    "value": unserializable_child_value,
                }
            ],
        }
    )

    assert dict(task.configuration) == {}
    assert task.tasks[0].model_extra == {"value": unserializable_child_value}


def test_unknown_task_kind_has_a_stable_source_diagnostic() -> None:
    source = """id: unknown
namespace: tests.dsl
tasks:
  - id: missing
    type: vendor.missing
    answer: 1
"""

    first = validate_flow_document(source)
    second = validate_flow_document(source)

    assert not first.valid
    assert len(first.issues) == 1
    issue = first.issues[0]
    assert (issue.code, issue.message, issue.path, issue.hint) == (
        "unknown_resource_type",
        "no task schema is registered for 'vendor.missing'",
        "tasks.0",
        "Install or register the resource plugin, or correct its type.",
    )
    assert issue.source_range is not None
    assert first.issues == second.issues


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


def test_task_timeout_mode_preserves_legacy_defaults_and_requires_unbounded_opt_in() -> None:
    legacy = TaskDefinition.model_validate({"id": "legacy", "type": "agent.mcp"})
    bounded = TaskDefinition.model_validate(
        {
            "id": "bounded",
            "type": "agent.mcp",
            "timeoutMode": "BOUNDED",
            "timeoutSeconds": 7,
        }
    )
    disabled = TaskDefinition.model_validate(
        {"id": "disabled", "type": "agent.mcp", "timeoutMode": "DISABLED"}
    )

    assert legacy.timeout_mode is TaskTimeoutMode.BOUNDED
    assert "timeoutMode" not in legacy.model_dump(mode="json", by_alias=True)
    assert bounded.timeout_seconds == 7
    assert disabled.timeout_mode is TaskTimeoutMode.DISABLED
    assert disabled.model_dump(mode="json", by_alias=True, exclude_none=True) == {
        **legacy.model_dump(mode="json", by_alias=True, exclude_none=True),
        "id": "disabled",
        "timeoutMode": "DISABLED",
    }

    with pytest.raises(ValueError, match="requires timeoutSeconds to be absent"):
        TaskDefinition.model_validate(
            {
                "id": "conflicting",
                "type": "agent.mcp",
                "timeoutMode": "DISABLED",
                "timeoutSeconds": 7,
            }
        )
    with pytest.raises(ValueError, match="requires timeoutSeconds to be absent"):
        TaskDefinition.model_validate(
            {
                "id": "explicit-null",
                "type": "agent.mcp",
                "timeoutMode": "DISABLED",
                "timeoutSeconds": None,
            }
        )


def test_agent_catalogs_expose_and_validate_task_timeout_mode() -> None:
    registry = default_resource_registry()

    for resource_type in ("agent.mcp", "agent.session"):
        descriptor = registry.descriptor(ResourceKind.TASK, resource_type)
        assert descriptor is not None
        assert descriptor.configuration_schema["properties"]["timeoutMode"] == {
            "type": "string",
            "enum": ["BOUNDED", "DISABLED"],
        }
        timeout_position = descriptor.editor.property_order.index("timeoutSeconds")
        assert descriptor.editor.property_order[timeout_position - 1] == "timeoutMode"

    assert not registry.validate(
        ResourceKind.TASK,
        "agent.mcp",
        {"endpoint": "in-process://test", "tool": "echo", "timeoutMode": "DISABLED"},
    )
    assert registry.validate(
        ResourceKind.TASK,
        "agent.mcp",
        {
            "endpoint": "in-process://test",
            "tool": "echo",
            "timeoutMode": "DISABLED",
            "timeoutSeconds": 7,
        },
    )


def test_bounded_model_catalog_allows_budgetless_provider_bounded_tasks() -> None:
    registry = default_resource_registry()
    base = {
        "provider": {"adapter": "openai-codex-app-server", "engineRef": "team-codex"},
        "model": "gpt-5.6-luna",
        "prompt": "Return JSON with ok set to true.",
        "dataHandling": {"egress": "DENY_SECRETS", "promptRetention": "HASH_ONLY"},
        "outputSchema": {"type": "object"},
    }

    assert registry.validate(ResourceKind.TASK, "agent.structured", base)
    assert not registry.validate(
        ResourceKind.TASK,
        "agent.structured",
        {**base, "ceilingMode": "PROVIDER_BOUNDED"},
    )


def test_agent_llm_contract_matches_supported_provider_and_tool_fields() -> None:
    registry = default_resource_registry()
    descriptor = registry.descriptor(ResourceKind.TASK, "agent.llm")
    assert descriptor is not None
    root_properties = descriptor.configuration_schema["properties"]
    assert {"provider", "model", "prompt", "messages", "parameters"} <= set(root_properties)
    assert set(descriptor.editor.property_order) <= set(root_properties)
    configuration = {
        "provider": {
            "adapter": "openai-compatible",
            "revision": "2026-09-01",
            "endpoint": "https://models.example.test/v1/chat/completions",
            "credentialRef": "models",
        },
        "model": "example/chat",
        "prompt": "Reply ready.",
        "ceilingMode": "PROVIDER_BOUNDED",
        "maxCompletionTokens": 16,
        "dataHandling": {
            "egress": "REDACT_SECRETS",
            "promptRetention": "REDACTED",
        },
        "parameters": {"temperature": 0},
    }

    assert not registry.validate(ResourceKind.TASK, "agent.llm", configuration)
    for unsupported in ({"tools": []}, {"outputSchema": {}}, {"bogus": True}):
        issues = registry.validate(
            ResourceKind.TASK,
            "agent.llm",
            {**configuration, **unsupported},
        )
        assert len(issues) == 1
        assert issues[0].code == "resource_schema_validation"
        assert "Additional properties are not allowed" in issues[0].message

    reserved_option_issues = registry.validate(
        ResourceKind.TASK,
        "agent.llm",
        {**configuration, "parameters": {"providerOptions": {"model": "override"}}},
    )
    assert reserved_option_issues


def test_agent_llm_handler_contract_enforces_nested_model_budget_invariants() -> None:
    specification = default_resource_registry().task_specification("agent.llm")
    assert specification is not None
    configuration = {
        "provider": {
            "endpoint": "https://models.example.test/v1/chat/completions",
            "credentialRef": "models",
        },
        "model": "example/chat",
        "prompt": "Reply ready.",
        "budget": {
            "maxTotalTokens": 8,
            "maxCompletionTokens": 9,
            "maxCostUsd": "0.01",
        },
        "dataHandling": {
            "egress": "REDACT_SECRETS",
            "promptRetention": "REDACTED",
        },
    }

    with pytest.raises(ValueError, match="maxCompletionTokens cannot exceed maxTotalTokens"):
        specification.configuration_contract.validate(configuration)


def test_model_task_registry_accepts_public_continuation_and_timeout_controls() -> None:
    registry = default_resource_registry()
    invocation_id = "11111111-1111-4111-8111-111111111111"
    common = {
        "provider": {
            "adapter": "openai-compatible",
            "endpoint": "https://models.example.test/v1/chat/completions",
            "credentialRef": "models",
        },
        "model": "example/chat",
        "ceilingMode": "PROVIDER_BOUNDED",
        "dataHandling": {
            "egress": "REDACT_SECRETS",
            "promptRetention": "REDACTED",
        },
        "timeoutMode": "DISABLED",
        "continuationFromInvocationId": invocation_id,
        "continuationSources": [
            {"messageIndex": 0, "invocationId": invocation_id},
        ],
    }
    completion_limited = {**common, "maxCompletionTokens": 16}
    configurations = {
        "agent.llm": {**completion_limited, "prompt": "Reply ready."},
        "agent.chat": {**completion_limited, "prompt": "Reply ready."},
        "agent.embedding": {**common, "input": "Embed this."},
        "agent.structured": {
            **completion_limited,
            "prompt": "Reply ready.",
            "outputSchema": {"type": "object"},
        },
        "agent.toolCall": {
            **completion_limited,
            "prompt": "Reply ready.",
            "tools": [{"name": "echo", "inputSchema": {"type": "object"}}],
        },
    }

    for task_type, configuration in configurations.items():
        assert not registry.validate(ResourceKind.TASK, task_type, configuration)
        for internal_field in ("invocationKey", "progressContext"):
            issues = registry.validate(
                ResourceKind.TASK,
                task_type,
                {**configuration, internal_field: "not-public"},
            )
            assert len(issues) == 1
            assert "Additional properties are not allowed" in issues[0].message

    embedding_limit_issues = registry.validate(
        ResourceKind.TASK,
        "agent.embedding",
        {**configurations["agent.embedding"], "maxCompletionTokens": 16},
    )
    assert len(embedding_limit_issues) == 1
    assert "Additional properties are not allowed" in embedding_limit_issues[0].message

    budget = {
        "maxTotalTokens": 32,
        "maxCompletionTokens": 16,
        "maxCostUsd": "0.01",
    }
    for task_type in ("agent.llm", "agent.chat", "agent.structured", "agent.toolCall"):
        conflicting = {**configurations[task_type], "budget": budget}
        assert registry.validate(ResourceKind.TASK, task_type, conflicting)
        specification = registry.task_specification(task_type)
        assert specification is not None
        with pytest.raises(ValueError, match="budget and maxCompletionTokens"):
            specification.configuration_contract.validate(conflicting)


def test_model_task_contract_rejects_disabled_timeout_with_finite_timeout() -> None:
    specification = default_resource_registry().task_specification("agent.chat")
    assert specification is not None

    with pytest.raises(ValueError, match="timeoutSeconds to be absent"):
        specification.configuration_contract.validate(
            {
                "provider": {
                    "adapter": "openai-compatible",
                    "endpoint": "https://models.example.test/v1/chat/completions",
                    "credentialRef": "models",
                },
                "model": "example/chat",
                "prompt": "Reply ready.",
                "ceilingMode": "PROVIDER_BOUNDED",
                "maxCompletionTokens": 16,
                "dataHandling": {
                    "egress": "REDACT_SECRETS",
                    "promptRetention": "REDACTED",
                },
                "timeoutMode": "DISABLED",
                "timeoutSeconds": 10,
            }
        )


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


def test_runtime_graph_injection_requires_a_declared_flowable_contract() -> None:
    with pytest.raises(ValueError, match="versioned built-in flowable contract"):
        FlowDefinition.model_validate(
            {
                "id": "injected",
                "namespace": "tests.dsl",
                "tasks": [
                    {
                        "id": "plugin",
                        "type": "vendor.arbitrary",
                        "tasks": [{"id": "hidden", "type": "core.return"}],
                    }
                ],
            }
        )


def test_task_nesting_has_a_deterministic_limit() -> None:
    nested: dict[str, object] = {"id": "done", "type": "core.return"}
    for depth in range(16):
        nested = {
            "id": f"level_{depth}",
            "type": "core.sequential",
            "tasks": [nested],
        }

    with pytest.raises(ValueError, match="task nesting depth exceeds"):
        FlowDefinition.model_validate(
            {
                "id": "too_deep",
                "namespace": "tests.dsl",
                "tasks": [nested],
            }
        )


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


def test_all_execution_check_contracts_validate_and_canonicalize() -> None:
    result = validate_flow_document(
        """id: checked
namespace: tests.dsl
checkPolicies: [baseline]
tasks:
  - id: result
    type: core.return
checks:
  - {id: duration, type: DURATION, threshold: PT1H}
  - {id: start, type: START_DELAY, threshold: PT30S}
  - {id: fresh, type: FRESHNESS, threshold: PT24H}
  - {id: window, type: COMPLETION_WINDOW, threshold: PT2H}
  - {id: output, type: OUTPUT, expression: "{{ outputs.result.value == 'ok' }}"}
  - id: expression
    type: EXPRESSION
    severity: WARN
    expression: "{{ execution.state == 'SUCCESS' }}"
    actions:
      - {type: NOTIFY, channel: operations, maxAttempts: 2}
      - {type: RUN_FLOW, flowId: handler, maxDepth: 3}
"""
    )

    assert result.valid
    assert result.canonical is not None
    assert [item["type"] for item in result.canonical["checks"]] == [
        "DURATION",
        "START_DELAY",
        "FRESHNESS",
        "COMPLETION_WINDOW",
        "OUTPUT",
        "EXPRESSION",
    ]
    assert result.canonical["checkPolicies"] == ["baseline"]


@pytest.mark.parametrize(
    "check",
    [
        "{id: duration, type: DURATION}",
        "{id: output, type: OUTPUT}",
        "{id: notify, type: EXPRESSION, expression: '{{ true }}', actions: [{type: NOTIFY}]} ",
        "{id: handler, type: EXPRESSION, expression: '{{ false }}', actions: [{type: RUN_FLOW}]} ",
    ],
)
def test_invalid_execution_check_contracts_are_rejected(check: str) -> None:
    result = validate_flow_document(
        f"id: checked\nnamespace: tests.dsl\ntasks:\n  - id: result\n    type: core.return\nchecks:\n  - {check}\n"
    )

    assert not result.valid


@pytest.mark.parametrize("runs", [5])
@pytest.mark.no_cover
def test_five_thousand_line_flow_validation_p95_is_below_one_second(runs: int) -> None:
    task_lines = [
        f"  - id: task_{index}\n    type: core.return\n    description: task {index}\n    value: {index}"
        for index in range(1_250)
    ]
    source = "id: large\nnamespace: tests.performance\ntasks:\n" + "\n".join(task_lines) + "\n"
    assert len(source.splitlines()) >= 5_000

    benchmark = """
import json
import sys
from time import perf_counter

from amesh.dsl import validate_flow_document

source = sys.stdin.read()
durations = []
try:
    warmup = validate_flow_document(source)
    if not warmup.valid:
        raise AssertionError("warmup validation failed")
    for _ in range(int(sys.argv[1])):
        started = perf_counter()
        result = validate_flow_document(source)
        durations.append(perf_counter() - started)
        if not result.valid:
            raise AssertionError("timed validation failed")
except Exception as error:
    print(json.dumps({"durations": durations, "error": f"{type(error).__name__}: {error}"}))
    raise SystemExit(1) from error
print(json.dumps({"durations": durations, "error": None}))
"""
    completed = subprocess.run(
        [sys.executable, "-c", benchmark, str(runs)],
        input=source,
        capture_output=True,
        check=False,
        env={
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("COV_CORE_", "COVERAGE_"))
        },
        text=True,
    )
    measurement = json.loads(completed.stdout)
    assert completed.returncode == 0, measurement["error"]
    durations = measurement["durations"]
    assert len(durations) == runs

    p95 = sorted(durations)[-1]
    assert p95 < 1.0, f"5,000-line validation p95 was {p95:.3f}s"
