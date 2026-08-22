from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Final, Literal

from pydantic import ValidationError

from .models import (
    FlowDefinition,
    FlowValidationResult,
    InputDefinition,
    SourcePosition,
    SourceRange,
    TaskDefinition,
    TriggerDefinition,
    ValidationIssue,
)
from .registry import ResourceKind, ResourceSchemaRegistry, default_resource_registry
from .source import (
    FlowDocumentError,
    FlowSourceSyntaxError,
    PathPart,
    SourceMap,
    format_path,
    parse_flow_source,
)

IR_VERSION: Final[Literal["amesh.flow/v1"]] = "amesh.flow/v1"

_ALIASES = {
    "api_version": "apiVersion",
    "depends_on": "dependsOn",
    "run_if": "runIf",
    "timeout_seconds": "timeoutSeconds",
    "max_attempts": "maxAttempts",
    "delay_seconds": "delaySeconds",
    "backoff_multiplier": "backoffMultiplier",
    "max_interval_seconds": "maxIntervalSeconds",
    "jitter_ratio": "jitterRatio",
    "condition_error_policy": "conditionErrorPolicy",
    "then_tasks": "then",
    "else_if": "elseIf",
    "else_tasks": "else",
    "predicate_cases": "predicateCases",
    "error_selector": "errorSelector",
    "finally_tasks": "finally",
    "after_execution": "afterExecution",
}
_TASK_STRUCTURE_FIELDS = {
    "id",
    "type",
    "description",
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
_TRIGGER_STRUCTURE_FIELDS = {"id", "type", "disabled"}
_INPUT_STRUCTURE_FIELDS = {"id", "type", "required", "description", "sensitive"}


def _walk_tasks(
    tasks: Iterable[TaskDefinition],
    prefix: tuple[PathPart, ...] = ("tasks",),
) -> Iterable[tuple[tuple[PathPart, ...], TaskDefinition]]:
    for index, task in enumerate(tasks):
        path = (*prefix, index)
        yield path, task
        for child_prefix, children in _child_task_groups(task, path):
            yield from _walk_tasks(children, child_prefix)


def _child_task_groups(
    task: TaskDefinition,
    path: tuple[PathPart, ...],
) -> Iterable[tuple[tuple[PathPart, ...], list[TaskDefinition]]]:
    if task.tasks:
        yield (*path, "tasks"), task.tasks
    if task.then_tasks:
        yield (*path, "then"), task.then_tasks
    for index, branch in enumerate(task.else_if):
        yield (*path, "elseIf", index, "tasks"), branch.tasks
    if task.else_tasks:
        yield (*path, "else"), task.else_tasks
    for case, tasks in task.cases.items():
        yield (*path, "cases", case), tasks
    for index, branch in enumerate(task.predicate_cases):
        yield (*path, "predicateCases", index, "tasks"), branch.tasks
    if task.errors:
        yield (*path, "errors"), task.errors


def _issue(
    *,
    code: str,
    message: str,
    path: Sequence[PathPart],
    hint: str,
    source_map: SourceMap | None,
) -> ValidationIssue:
    normalized_path = tuple(
        _ALIASES.get(part, part) if isinstance(part, str) else part for part in path
    )
    return ValidationIssue(
        code=code,
        message=message,
        path=format_path(normalized_path),
        hint=hint,
        sourceRange=source_map.range_for(normalized_path) if source_map is not None else None,
    )


def _duplicate_issues(flow: FlowDefinition, source_map: SourceMap | None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    collections: tuple[tuple[str, Sequence[InputDefinition | TriggerDefinition]], ...] = (
        ("inputs", flow.inputs),
        ("triggers", flow.triggers),
    )
    for collection_name, values in collections:
        seen: dict[str, int] = {}
        for index, value in enumerate(values):
            previous = seen.get(value.id)
            if previous is not None:
                issues.append(
                    _issue(
                        code="duplicate_id",
                        message=f"duplicate {collection_name[:-1]} id {value.id!r}",
                        path=(collection_name, index, "id"),
                        hint=f"Rename this identifier; it first appears at {collection_name}[{previous}].",
                        source_map=source_map,
                    )
                )
            else:
                seen[value.id] = index

    seen_tasks: dict[str, tuple[PathPart, ...]] = {}
    groups = (
        _walk_tasks(flow.tasks),
        _walk_tasks(flow.errors, ("errors",)),
        _walk_tasks(flow.finally_tasks, ("finally",)),
        _walk_tasks(flow.after_execution, ("afterExecution",)),
    )
    for group in groups:
        for path, task in group:
            previous_path = seen_tasks.get(task.id)
            if previous_path is not None:
                issues.append(
                    _issue(
                        code="duplicate_task_id",
                        message=(
                            f"task id {task.id!r} is already used at {format_path(previous_path)}"
                        ),
                        path=(*path, "id"),
                        hint="Give every primary or lifecycle task a unique identifier.",
                        source_map=source_map,
                    )
                )
            else:
                seen_tasks[task.id] = path
    return issues


def _dependency_issues(
    tasks: list[TaskDefinition],
    source_map: SourceMap | None,
    prefix: tuple[PathPart, ...] = ("tasks",),
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    ids = {task.id for task in tasks}
    graph: dict[str, list[str]] = {task.id: task.depends_on for task in tasks}

    for index, task in enumerate(tasks):
        for dependency_index, dependency in enumerate(task.depends_on):
            if dependency not in ids:
                issues.append(
                    _issue(
                        code="missing_dependency",
                        message=f"task {task.id!r} depends on unknown sibling task {dependency!r}",
                        path=(*prefix, index, "dependsOn", dependency_index),
                        hint="Reference the id of a sibling task or remove the dependency.",
                        source_map=source_map,
                    )
                )
        for child_prefix, children in _child_task_groups(task, (*prefix, index)):
            issues.extend(_dependency_issues(children, source_map, child_prefix))

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, chain: list[str]) -> None:
        if node in visiting:
            start = chain.index(node)
            cycle = [*chain[start:], node]
            issues.append(
                _issue(
                    code="dependency_cycle",
                    message="dependency cycle: " + " -> ".join(cycle),
                    path=prefix,
                    hint="Remove or redirect at least one dependency in this cycle.",
                    source_map=source_map,
                )
            )
            return
        if node in visited:
            return
        visiting.add(node)
        chain.append(node)
        for dependency in graph.get(node, []):
            if dependency in graph:
                visit(dependency, chain)
        chain.pop()
        visiting.remove(node)
        visited.add(node)

    for task_id in sorted(graph):
        visit(task_id, [])
    return issues


def _statically_true(expression: str) -> bool:
    normalized = "".join(expression.lower().split())
    return normalized in {"true", "{{true}}"}


def _conditional_issues(
    flow: FlowDefinition,
    source_map: SourceMap | None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    groups = (
        _walk_tasks(flow.tasks),
        _walk_tasks(flow.errors, ("errors",)),
        _walk_tasks(flow.finally_tasks, ("finally",)),
        _walk_tasks(flow.after_execution, ("afterExecution",)),
    )
    for group in groups:
        for path, task in group:
            if task.type == "core.if":
                branches = [("then", task.condition or "")]
                branches.extend((branch.id, branch.condition) for branch in task.else_if)
                seen_ids: set[str] = set()
                seen_conditions: dict[str, str] = {}
                unconditional: str | None = None
                for index, (branch_id, condition) in enumerate(branches):
                    if index > 0 and branch_id in seen_ids:
                        issues.append(
                            _issue(
                                code="duplicate_case",
                                message=f"duplicate else-if branch id {branch_id!r}",
                                path=(*path, "elseIf", index - 1, "id"),
                                hint="Give every else-if branch a unique id.",
                                source_map=source_map,
                            )
                        )
                    seen_ids.add(branch_id)
                    normalized = " ".join(condition.split())
                    if normalized in seen_conditions:
                        issues.append(
                            _issue(
                                code="duplicate_condition",
                                message=(
                                    f"conditional branch {branch_id!r} repeats condition from "
                                    f"{seen_conditions[normalized]!r}"
                                ),
                                path=path,
                                hint="Remove or change the duplicate condition.",
                                source_map=source_map,
                            )
                        )
                    else:
                        seen_conditions[normalized] = branch_id
                    if unconditional is not None:
                        issues.append(
                            _issue(
                                code="unreachable_branch",
                                message=(
                                    f"conditional branch {branch_id!r} is unreachable after "
                                    f"unconditional branch {unconditional!r}"
                                ),
                                path=path,
                                hint="Move or remove the unconditional branch.",
                                source_map=source_map,
                            )
                        )
                    elif _statically_true(condition):
                        unconditional = branch_id
                    if index == 0 and unconditional is not None and task.else_tasks:
                        continue
                if unconditional is not None and task.else_tasks:
                    issues.append(
                        _issue(
                            code="unreachable_branch",
                            message=f"else branch is unreachable after {unconditional!r}",
                            path=(*path, "else"),
                            hint="Remove the else branch or make preceding conditions conditional.",
                            source_map=source_map,
                        )
                    )
            elif task.type == "core.switch":
                switch_seen_ids: set[str] = set()
                switch_seen_conditions: dict[str, str] = {}
                switch_unconditional: str | None = None
                for index, branch in enumerate(task.predicate_cases):
                    if branch.id in switch_seen_ids:
                        issues.append(
                            _issue(
                                code="duplicate_case",
                                message=f"duplicate predicate case id {branch.id!r}",
                                path=(*path, "predicateCases", index, "id"),
                                hint="Give every predicate case a unique id.",
                                source_map=source_map,
                            )
                        )
                    switch_seen_ids.add(branch.id)
                    normalized = " ".join(branch.condition.split())
                    if normalized in switch_seen_conditions:
                        issues.append(
                            _issue(
                                code="duplicate_condition",
                                message=(
                                    f"predicate case {branch.id!r} repeats condition from "
                                    f"{switch_seen_conditions[normalized]!r}"
                                ),
                                path=(*path, "predicateCases", index, "condition"),
                                hint="Remove or change the duplicate predicate.",
                                source_map=source_map,
                            )
                        )
                    else:
                        switch_seen_conditions[normalized] = branch.id
                    if switch_unconditional is not None:
                        issues.append(
                            _issue(
                                code="unreachable_branch",
                                message=(
                                    f"predicate case {branch.id!r} is unreachable after "
                                    f"unconditional predicate {switch_unconditional!r}"
                                ),
                                path=(*path, "predicateCases", index),
                                hint="Move or remove the unconditional predicate.",
                                source_map=source_map,
                            )
                        )
                    elif _statically_true(branch.condition):
                        switch_unconditional = branch.id
                if switch_unconditional is not None and "default" in task.cases:
                    issues.append(
                        _issue(
                            code="unreachable_branch",
                            message=(
                                f"default case is unreachable after unconditional predicate "
                                f"{switch_unconditional!r}"
                            ),
                            path=(*path, "cases", "default"),
                            hint="Remove the default case or make preceding predicates conditional.",
                            source_map=source_map,
                        )
                    )
    return issues


def _resource_issues(
    flow: FlowDefinition,
    registry: ResourceSchemaRegistry,
    source_map: SourceMap | None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    task_groups = (
        _walk_tasks(flow.tasks),
        _walk_tasks(flow.errors, ("errors",)),
        _walk_tasks(flow.finally_tasks, ("finally",)),
        _walk_tasks(flow.after_execution, ("afterExecution",)),
    )
    for group in task_groups:
        for path, task in group:
            structural_fields = _TASK_STRUCTURE_FIELDS
            if task.type in {"core.while", "core.until"}:
                structural_fields = structural_fields - {"condition"}
            configuration = _configuration(task, structural_fields)
            issues.extend(
                _registry_issues(
                    registry,
                    ResourceKind.TASK,
                    task.type,
                    configuration,
                    path,
                    source_map,
                )
            )
    for index, trigger in enumerate(flow.triggers):
        issues.extend(
            _registry_issues(
                registry,
                ResourceKind.TRIGGER,
                trigger.type,
                _configuration(trigger, _TRIGGER_STRUCTURE_FIELDS),
                ("triggers", index),
                source_map,
            )
        )
    for index, input_definition in enumerate(flow.inputs):
        issues.extend(
            _registry_issues(
                registry,
                ResourceKind.INPUT,
                input_definition.type,
                _configuration(input_definition, _INPUT_STRUCTURE_FIELDS),
                ("inputs", index),
                source_map,
            )
        )
    return issues


def _lifecycle_issues(
    flow: FlowDefinition,
    source_map: SourceMap | None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    def inspect(
        tasks: list[TaskDefinition],
        prefix: tuple[PathPart, ...],
        *,
        in_error_block: bool,
        in_lifecycle_block: bool,
    ) -> None:
        for index, task in enumerate(tasks):
            path = (*prefix, index)
            if task.error_selector is not None and not in_error_block:
                issues.append(
                    _issue(
                        code="misplaced_error_selector",
                        message="errorSelector is valid only on a task inside an errors block",
                        path=(*path, "errorSelector"),
                        hint="Move the task into an errors block or remove errorSelector.",
                        source_map=source_map,
                    )
                )
            if in_lifecycle_block and task.errors:
                issues.append(
                    _issue(
                        code="recursive_error_handler",
                        message="lifecycle tasks cannot declare nested errors handlers",
                        path=(*path, "errors"),
                        hint="Move recursive recovery into a bounded subflow or ordinary task retry.",
                        source_map=source_map,
                    )
                )
            for child_prefix, children in _child_task_groups(task, path):
                is_error_children = child_prefix[-1] == "errors"
                inspect(
                    children,
                    child_prefix,
                    in_error_block=is_error_children,
                    in_lifecycle_block=in_lifecycle_block or is_error_children,
                )

    inspect(flow.tasks, ("tasks",), in_error_block=False, in_lifecycle_block=False)
    inspect(flow.errors, ("errors",), in_error_block=True, in_lifecycle_block=True)
    inspect(flow.finally_tasks, ("finally",), in_error_block=False, in_lifecycle_block=True)
    inspect(
        flow.after_execution,
        ("afterExecution",),
        in_error_block=False,
        in_lifecycle_block=True,
    )
    return issues


def _configuration(model: Any, structural_fields: set[str]) -> dict[str, Any]:
    payload = model.model_dump(
        mode="json",
        by_alias=True,
        exclude_none=True,
        exclude_defaults=True,
    )
    return {
        key: value
        for key, value in payload.items()
        if key not in structural_fields and not key.startswith("x-")
    }


def _registry_issues(
    registry: ResourceSchemaRegistry,
    kind: ResourceKind,
    resource_type: str,
    configuration: Mapping[str, Any],
    path: tuple[PathPart, ...],
    source_map: SourceMap | None,
) -> list[ValidationIssue]:
    return [
        _issue(
            code=error.code,
            message=error.message,
            path=(*path, *error.path),
            hint=error.hint,
            source_map=source_map,
        )
        for error in registry.validate(kind, resource_type, configuration)
    ]


def _canonical_hash(flow: FlowDefinition) -> tuple[dict[str, Any], str]:
    canonical = flow.model_dump(mode="json", by_alias=True, exclude_none=True)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return canonical, hashlib.sha256(encoded).hexdigest()


def _schema_hint(error_type: str) -> str:
    if error_type == "missing":
        return "Add the required field at the indicated object."
    if error_type == "extra_forbidden":
        return "Remove the field or rename an intentional extension with the x- prefix."
    if error_type in {"list_type", "dict_type", "string_type", "int_type", "bool_type"}:
        return "Use the field type declared by the flow schema."
    return "Correct the value using the generated flow schema and editor metadata."


def _unknown_core_issues(
    data: Mapping[str, Any],
    source_map: SourceMap | None,
) -> list[ValidationIssue]:
    known = {field.alias or name for name, field in FlowDefinition.model_fields.items()} | set(
        FlowDefinition.model_fields
    )
    return [
        _issue(
            code="unknown_core_field",
            message=f"unknown core field {key!r}",
            path=(key,),
            hint="Remove the field or rename an intentional extension with the x- prefix.",
            source_map=source_map,
        )
        for key in data
        if key not in known and not key.startswith("x-")
    ]


def _origin_range() -> SourceRange:
    return SourceRange(
        start=SourcePosition(line=1, column=1, offset=0),
        end=SourcePosition(line=1, column=2, offset=1),
    )


def validate_flow_document(
    source: str | bytes | dict[str, Any],
    *,
    registry: ResourceSchemaRegistry | None = None,
) -> FlowValidationResult:
    """Parse and validate a flow document without performing I/O or plugin execution."""

    try:
        parsed = parse_flow_source(source)
    except FlowSourceSyntaxError as exc:
        return FlowValidationResult(
            valid=False,
            issues=[
                ValidationIssue(
                    code="invalid_yaml",
                    message=str(exc),
                    path="$",
                    hint="Correct the YAML or JSON syntax at the indicated range.",
                    sourceRange=exc.source_range,
                )
            ],
        )
    except FlowDocumentError as exc:
        return FlowValidationResult(
            valid=False,
            issues=[
                ValidationIssue(
                    code="document_type",
                    message=str(exc),
                    path="$",
                    hint="Use a YAML or JSON object as the flow document root.",
                    sourceRange=_origin_range() if not isinstance(source, dict) else None,
                )
            ],
        )

    unknown_core_issues = _unknown_core_issues(parsed.data, parsed.source_map)
    if unknown_core_issues:
        return FlowValidationResult(
            valid=False,
            irVersion=IR_VERSION,
            issues=unknown_core_issues,
        )

    try:
        flow = FlowDefinition.model_validate(parsed.data)
    except ValidationError as exc:
        issues = [
            _issue(
                code="schema_validation",
                message=error["msg"],
                path=tuple(error["loc"]),
                hint=_schema_hint(str(error["type"])),
                source_map=parsed.source_map,
            )
            for error in exc.errors()
        ]
        return FlowValidationResult(valid=False, irVersion=IR_VERSION, issues=issues)

    active_registry = registry or default_resource_registry()
    issues = _duplicate_issues(flow, parsed.source_map)
    issues.extend(_dependency_issues(flow.tasks, parsed.source_map))
    issues.extend(_dependency_issues(flow.errors, parsed.source_map, ("errors",)))
    issues.extend(_dependency_issues(flow.finally_tasks, parsed.source_map, ("finally",)))
    issues.extend(_dependency_issues(flow.after_execution, parsed.source_map, ("afterExecution",)))
    issues.extend(_conditional_issues(flow, parsed.source_map))
    issues.extend(_lifecycle_issues(flow, parsed.source_map))
    issues.extend(_resource_issues(flow, active_registry, parsed.source_map))

    if issues:
        return FlowValidationResult(valid=False, irVersion=IR_VERSION, issues=issues)

    canonical, semantic_hash = _canonical_hash(flow)
    return FlowValidationResult(
        valid=True,
        irVersion=IR_VERSION,
        semantic_hash=semantic_hash,
        canonical=canonical,
    )
