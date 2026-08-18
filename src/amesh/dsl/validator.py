from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from typing import Any

import yaml
from pydantic import ValidationError

from .models import (
    FlowDefinition,
    FlowValidationResult,
    InputDefinition,
    TaskDefinition,
    TriggerDefinition,
    ValidationIssue,
)


class FlowDocumentError(ValueError):
    """Raised when a source document cannot be decoded into a mapping."""


def _walk_tasks(
    tasks: Iterable[TaskDefinition], prefix: str = "tasks"
) -> Iterable[tuple[str, TaskDefinition]]:
    for index, task in enumerate(tasks):
        path = f"{prefix}[{index}]"
        yield path, task
        yield from _walk_tasks(task.tasks, f"{path}.tasks")


def _duplicate_issues(flow: FlowDefinition) -> list[ValidationIssue]:
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
                    ValidationIssue(
                        code="duplicate_id",
                        message=f"duplicate {collection_name[:-1]} id {value.id!r}",
                        path=f"{collection_name}[{index}].id",
                    )
                )
            else:
                seen[value.id] = index

    seen_tasks: dict[str, str] = {}
    for path, task in _walk_tasks([*flow.tasks, *flow.errors, *flow.finally_tasks]):
        previous_path = seen_tasks.get(task.id)
        if previous_path is not None:
            issues.append(
                ValidationIssue(
                    code="duplicate_task_id",
                    message=f"task id {task.id!r} is already used at {previous_path}",
                    path=f"{path}.id",
                )
            )
        else:
            seen_tasks[task.id] = path
    return issues


def _dependency_issues(tasks: list[TaskDefinition], prefix: str = "tasks") -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    ids = {task.id for task in tasks}
    graph: dict[str, list[str]] = {task.id: task.depends_on for task in tasks}

    for index, task in enumerate(tasks):
        for dependency in task.depends_on:
            if dependency not in ids:
                issues.append(
                    ValidationIssue(
                        code="missing_dependency",
                        message=f"task {task.id!r} depends on unknown sibling task {dependency!r}",
                        path=f"{prefix}[{index}].dependsOn",
                    )
                )
        issues.extend(_dependency_issues(task.tasks, f"{prefix}[{index}].tasks"))

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, chain: list[str]) -> None:
        if node in visiting:
            start = chain.index(node)
            cycle = [*chain[start:], node]
            issues.append(
                ValidationIssue(
                    code="dependency_cycle",
                    message="dependency cycle: " + " -> ".join(cycle),
                    path=prefix,
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


def _canonical_hash(flow: FlowDefinition) -> tuple[dict[str, Any], str]:
    canonical = flow.model_dump(mode="json", by_alias=True, exclude_none=True)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return canonical, hashlib.sha256(encoded).hexdigest()


def validate_flow_document(source: str | bytes | dict[str, Any]) -> FlowValidationResult:
    """Parse and validate a flow document without performing I/O or plugin execution."""

    try:
        if isinstance(source, dict):
            raw: Any = source
        else:
            raw = yaml.safe_load(source)
    except yaml.YAMLError as exc:
        return FlowValidationResult(
            valid=False,
            issues=[
                ValidationIssue(
                    code="invalid_yaml",
                    message=str(exc),
                    path="$",
                )
            ],
        )

    if not isinstance(raw, dict):
        raise FlowDocumentError("flow document must decode to an object")

    try:
        flow = FlowDefinition.model_validate(raw)
    except ValidationError as exc:
        issues = [
            ValidationIssue(
                code="schema_validation",
                message=error["msg"],
                path=".".join(str(part) for part in error["loc"]) or "$",
            )
            for error in exc.errors()
        ]
        return FlowValidationResult(valid=False, issues=issues)

    issues = _duplicate_issues(flow)
    issues.extend(_dependency_issues(flow.tasks))
    issues.extend(_dependency_issues(flow.errors, "errors"))
    issues.extend(_dependency_issues(flow.finally_tasks, "finally"))

    if issues:
        return FlowValidationResult(valid=False, issues=issues)

    canonical, semantic_hash = _canonical_hash(flow)
    return FlowValidationResult(valid=True, semantic_hash=semantic_hash, canonical=canonical)
