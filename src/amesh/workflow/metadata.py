from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from amesh.dsl.models import (
    ConditionalBranch,
    FlowDefinition,
    PluginDefaultDefinition,
    TaskDefinition,
)

PROTECTED_LABEL_PREFIXES = ("amesh.", "system.")


class LabelNormalization(StrEnum):
    TRIM = "TRIM"
    LOWERCASE = "LOWERCASE"
    UPPERCASE = "UPPERCASE"


class WorkflowMetadataPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    required_labels: dict[str, str | None] = Field(default_factory=dict, alias="requiredLabels")
    denied_labels: tuple[str, ...] = Field(default=(), alias="deniedLabels")
    normalize_labels: dict[str, LabelNormalization] = Field(
        default_factory=dict,
        alias="normalizeLabels",
    )
    required_defaults: dict[str, tuple[str, ...]] = Field(
        default_factory=dict,
        alias="requiredDefaults",
    )
    denied_defaults: dict[str, tuple[str, ...]] = Field(
        default_factory=dict,
        alias="deniedDefaults",
    )
    normalize_defaults: dict[str, dict[str, LabelNormalization]] = Field(
        default_factory=dict,
        alias="normalizeDefaults",
    )

    @field_validator("required_labels", "normalize_labels")
    @classmethod
    def validate_label_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        validate_user_labels({key: "" for key in value})
        return value

    @field_validator("denied_labels")
    @classmethod
    def validate_denied_label_keys(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        validate_user_labels({key: "" for key in value})
        if len(set(value)) != len(value):
            raise ValueError("deniedLabels must be unique")
        return value

    @field_validator("required_defaults", "denied_defaults", "normalize_defaults")
    @classmethod
    def validate_default_selectors(cls, value: dict[str, Any]) -> dict[str, Any]:
        for task_type, selectors in value.items():
            if not task_type or len(task_type) > 512:
                raise ValueError("default policy task types must contain 1-512 characters")
            paths = selectors if isinstance(selectors, tuple) else tuple(selectors)
            if any(not path or len(path) > 256 for path in paths):
                raise ValueError("default policy property paths must contain 1-256 characters")
        return value


class NamespaceWorkflowMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    tenant_id: str = Field(alias="tenantId")
    namespace: str
    plugin_defaults: tuple[PluginDefaultDefinition, ...] = Field(
        default=(),
        alias="pluginDefaults",
    )
    policy: WorkflowMetadataPolicy = Field(default_factory=WorkflowMetadataPolicy)
    resource_version: int = Field(alias="resourceVersion", ge=1)
    created_by: str = Field(alias="createdBy")
    updated_by: str = Field(alias="updatedBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    @model_validator(mode="after")
    def validate_defaults(self) -> NamespaceWorkflowMetadata:
        keys = [(item.type, item.forced) for item in self.plugin_defaults]
        if len(keys) != len(set(keys)):
            raise ValueError("pluginDefaults must have unique type/forced pairs")
        return self


class NamespaceWorkflowMetadataUpdate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    plugin_defaults: tuple[PluginDefaultDefinition, ...] = Field(
        default=(),
        alias="pluginDefaults",
    )
    policy: WorkflowMetadataPolicy = Field(default_factory=WorkflowMetadataPolicy)
    expected_version: int | None = Field(default=None, alias="expectedVersion", ge=1)

    @model_validator(mode="after")
    def validate_defaults(self) -> NamespaceWorkflowMetadataUpdate:
        keys = [(item.type, item.forced) for item in self.plugin_defaults]
        if len(keys) != len(set(keys)):
            raise ValueError("pluginDefaults must have unique type/forced pairs")
        return self


class NamespaceWorkflowMetadataView(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    namespace: str
    lineage: tuple[NamespaceWorkflowMetadata, ...]


@dataclass(frozen=True)
class _DefaultSource:
    definition: PluginDefaultDefinition
    source: Literal["namespace", "flow"]
    namespace: str | None = None

    def origin(self, *, task_path: str) -> dict[str, Any]:
        return {
            "source": self.source,
            "namespace": self.namespace,
            "taskPath": task_path,
            "forced": self.definition.forced,
        }


def namespace_lineage(namespace: str) -> tuple[str, ...]:
    parts = namespace.split(".")
    return tuple(".".join(parts[: index + 1]) for index in range(len(parts)))


def validate_user_labels(labels: Mapping[str, str]) -> dict[str, str]:
    validated = dict(labels)
    for key, value in validated.items():
        if not key or len(key) > 128 or len(value) > 256:
            raise ValueError("label keys must be 1-128 characters and values at most 256")
        if key.startswith(PROTECTED_LABEL_PREFIXES):
            raise ValueError(f"label {key!r} uses a protected system prefix")
    return validated


def flow_system_labels(flow: FlowDefinition) -> dict[str, str]:
    return {
        "amesh.namespace": flow.namespace,
        "amesh.flow.id": flow.id,
        "amesh.flow.revision": str(flow.revision),
    }


def execution_system_labels(
    flow: FlowDefinition,
    execution_id: object,
    *,
    source: str,
) -> dict[str, str]:
    return {
        **flow_system_labels(flow),
        "amesh.execution.id": str(execution_id),
        "amesh.execution.source": source,
    }


def task_system_labels(
    execution_labels: Mapping[str, str],
    *,
    task_id: str,
    lifecycle_phase: str,
) -> dict[str, str]:
    return {
        **execution_labels,
        "amesh.task.id": task_id,
        "amesh.task.phase": lifecycle_phase,
    }


def resolve_flow_metadata(
    flow: FlowDefinition,
    scopes: Sequence[NamespaceWorkflowMetadata],
) -> tuple[FlowDefinition, dict[str, Any]]:
    ordered_scopes = sorted(
        scopes, key=lambda item: namespace_lineage(flow.namespace).index(item.namespace)
    )
    _validate_scope_lineage(flow.namespace, ordered_scopes)
    _validate_flow_labels(flow)
    policy = _merge_policies(tuple(item.policy for item in ordered_scopes))
    labels = _apply_label_policy(flow.labels, policy)

    namespace_sources = tuple(
        _DefaultSource(default, "namespace", scope.namespace)
        for scope in ordered_scopes
        for default in scope.plugin_defaults
    )
    flow_sources = tuple(_DefaultSource(default, "flow") for default in flow.plugin_defaults)
    sources = _normalize_and_validate_default_sources(
        flow,
        (*namespace_sources, *flow_sources),
        policy,
    )
    task_resolutions: dict[str, Any] = {}
    resolved = flow.model_copy(
        update={
            "labels": labels,
            "tasks": _resolve_tasks(flow.tasks, sources, task_resolutions, prefix="tasks"),
            "errors": _resolve_tasks(flow.errors, sources, task_resolutions, prefix="errors"),
            "finally_tasks": _resolve_tasks(
                flow.finally_tasks,
                sources,
                task_resolutions,
                prefix="finally",
            ),
            "after_execution": _resolve_tasks(
                flow.after_execution,
                sources,
                task_resolutions,
                prefix="afterExecution",
            ),
        }
    )
    _validate_flow_labels(resolved)
    if not sources and not ordered_scopes:
        return resolved, {}
    return resolved, {
        "schemaVersion": 1,
        "namespaceLineage": [item.namespace for item in ordered_scopes],
        "tasks": task_resolutions,
    }


def _validate_scope_lineage(
    namespace: str,
    scopes: Sequence[NamespaceWorkflowMetadata],
) -> None:
    lineage = set(namespace_lineage(namespace))
    invalid = sorted(scope.namespace for scope in scopes if scope.namespace not in lineage)
    if invalid:
        raise ValueError(
            "workflow metadata scopes are outside namespace lineage: " + ", ".join(invalid)
        )


def _validate_flow_labels(flow: FlowDefinition) -> None:
    validate_user_labels(flow.labels)
    for node in _walk_tasks(flow):
        validate_user_labels(node.run_labels)


def _walk_tasks(flow: FlowDefinition) -> tuple[TaskDefinition, ...]:
    pending = [*flow.tasks, *flow.errors, *flow.finally_tasks, *flow.after_execution]
    result: list[TaskDefinition] = []
    while pending:
        task = pending.pop(0)
        result.append(task)
        pending.extend(task.tasks)
        pending.extend(task.then_tasks)
        pending.extend(task.else_tasks)
        pending.extend(task.errors)
        for branch in (*task.else_if, *task.predicate_cases):
            pending.extend(branch.tasks)
        for children in task.cases.values():
            pending.extend(children)
    return tuple(result)


def _merge_policies(policies: Sequence[WorkflowMetadataPolicy]) -> WorkflowMetadataPolicy:
    required_labels: dict[str, str | None] = {}
    denied_labels: set[str] = set()
    normalize_labels: dict[str, LabelNormalization] = {}
    required_defaults: dict[str, set[str]] = {}
    denied_defaults: dict[str, set[str]] = {}
    normalize_defaults: dict[str, dict[str, LabelNormalization]] = {}
    for policy in policies:
        required_labels.update(policy.required_labels)
        denied_labels.update(policy.denied_labels)
        normalize_labels.update(policy.normalize_labels)
        for task_type, required_paths in policy.required_defaults.items():
            required_defaults.setdefault(task_type, set()).update(required_paths)
        for task_type, denied_paths in policy.denied_defaults.items():
            denied_defaults.setdefault(task_type, set()).update(denied_paths)
        for task_type, normalization_paths in policy.normalize_defaults.items():
            normalize_defaults.setdefault(task_type, {}).update(normalization_paths)
    return WorkflowMetadataPolicy(
        requiredLabels=required_labels,
        deniedLabels=tuple(sorted(denied_labels)),
        normalizeLabels=normalize_labels,
        requiredDefaults={key: tuple(sorted(value)) for key, value in required_defaults.items()},
        deniedDefaults={key: tuple(sorted(value)) for key, value in denied_defaults.items()},
        normalizeDefaults=normalize_defaults,
    )


def _apply_label_policy(
    labels: Mapping[str, str],
    policy: WorkflowMetadataPolicy,
) -> dict[str, str]:
    values = validate_user_labels(labels)
    denied = sorted(set(values).intersection(policy.denied_labels))
    if denied:
        raise ValueError("labels denied by namespace policy: " + ", ".join(denied))
    for key, normalization in policy.normalize_labels.items():
        if key in values:
            values[key] = _normalize_text(values[key], normalization)
    missing = sorted(set(policy.required_labels) - set(values))
    if missing:
        raise ValueError("labels required by namespace policy: " + ", ".join(missing))
    mismatched = sorted(
        key
        for key, expected in policy.required_labels.items()
        if expected is not None and values.get(key) != expected
    )
    if mismatched:
        raise ValueError("labels do not match namespace policy: " + ", ".join(mismatched))
    return values


def _normalize_and_validate_default_sources(
    flow: FlowDefinition,
    sources: Sequence[_DefaultSource],
    policy: WorkflowMetadataPolicy,
) -> tuple[_DefaultSource, ...]:
    normalized: list[_DefaultSource] = []
    for source in sources:
        values = deepcopy(source.definition.values)
        denied = [
            path
            for path in policy.denied_defaults.get(source.definition.type, ())
            if _has_path(values, path)
        ]
        if denied:
            raise ValueError(
                f"defaults for {source.definition.type!r} are denied by namespace policy: "
                + ", ".join(sorted(denied))
            )
        for path, operation in policy.normalize_defaults.get(source.definition.type, {}).items():
            if _has_path(values, path):
                current = _get_path(values, path)
                if not isinstance(current, str):
                    raise ValueError(
                        f"default {source.definition.type}.{path} must be a string to normalize"
                    )
                _set_path(values, path, _normalize_text(current, operation))
        normalized.append(
            _DefaultSource(
                source.definition.model_copy(update={"values": values}),
                source.source,
                source.namespace,
            )
        )

    task_types = {task.type for task in _walk_tasks(flow)}
    for task_type in sorted(task_types.intersection(policy.required_defaults)):
        combined: dict[str, Any] = {}
        for source in normalized:
            if source.definition.type == task_type:
                _merge_mapping(combined, source.definition.values, {}, source.origin(task_path="*"))
        missing = [
            path for path in policy.required_defaults[task_type] if not _has_path(combined, path)
        ]
        if missing:
            raise ValueError(
                f"defaults for {task_type!r} required by namespace policy: "
                + ", ".join(sorted(missing))
            )
    return tuple(normalized)


def _resolve_tasks(
    tasks: Sequence[TaskDefinition],
    sources: Sequence[_DefaultSource],
    resolutions: dict[str, Any],
    *,
    prefix: str,
) -> list[TaskDefinition]:
    return [_resolve_task(task, sources, resolutions, path=f"{prefix}.{task.id}") for task in tasks]


def _resolve_task(
    task: TaskDefinition,
    sources: Sequence[_DefaultSource],
    resolutions: dict[str, Any],
    *,
    path: str,
) -> TaskDefinition:
    matching = [source for source in sources if source.definition.type == task.type]
    namespace_nonforced = [
        source
        for source in matching
        if source.source == "namespace" and not source.definition.forced
    ]
    flow_nonforced = [
        source for source in matching if source.source == "flow" and not source.definition.forced
    ]
    flow_forced = [
        source for source in matching if source.source == "flow" and source.definition.forced
    ]
    namespace_forced = [
        source for source in matching if source.source == "namespace" and source.definition.forced
    ]
    ordered = [
        *namespace_nonforced,
        *flow_nonforced,
        None,
        *flow_forced,
        *reversed(namespace_forced),
    ]
    payload: dict[str, Any] = {"id": task.id, "type": task.type}
    origins: dict[str, dict[str, Any]] = {}
    for source in ordered:
        if source is None:
            explicit = _explicit_task_payload(task)
            _merge_mapping(
                payload,
                explicit,
                origins,
                {"source": "task", "taskPath": path, "forced": False},
            )
            continue
        _merge_mapping(payload, source.definition.values, origins, source.origin(task_path=path))
    resolved = TaskDefinition.model_validate(payload)
    resolved = resolved.model_copy(
        update={
            "tasks": _resolve_tasks(resolved.tasks, sources, resolutions, prefix=path),
            "then_tasks": _resolve_tasks(
                resolved.then_tasks,
                sources,
                resolutions,
                prefix=f"{path}.then",
            ),
            "else_tasks": _resolve_tasks(
                resolved.else_tasks,
                sources,
                resolutions,
                prefix=f"{path}.else",
            ),
            "errors": _resolve_tasks(
                resolved.errors,
                sources,
                resolutions,
                prefix=f"{path}.errors",
            ),
            "else_if": _resolve_branches(
                resolved.else_if,
                sources,
                resolutions,
                prefix=f"{path}.elseIf",
            ),
            "predicate_cases": _resolve_branches(
                resolved.predicate_cases,
                sources,
                resolutions,
                prefix=f"{path}.predicateCases",
            ),
            "cases": {
                case: _resolve_tasks(
                    children,
                    sources,
                    resolutions,
                    prefix=f"{path}.cases.{case}",
                )
                for case, children in resolved.cases.items()
            },
        }
    )
    if matching:
        inherited_paths = sorted(
            property_path for property_path, origin in origins.items() if origin["source"] != "task"
        )
        resolutions[path] = {
            "type": task.type,
            "effective": {
                property_path: _get_path(payload, property_path)
                for property_path in inherited_paths
            },
            "origins": {property_path: origins[property_path] for property_path in sorted(origins)},
        }
    return resolved


def _resolve_branches(
    branches: Sequence[ConditionalBranch],
    sources: Sequence[_DefaultSource],
    resolutions: dict[str, Any],
    *,
    prefix: str,
) -> list[ConditionalBranch]:
    return [
        branch.model_copy(
            update={
                "tasks": _resolve_tasks(
                    branch.tasks,
                    sources,
                    resolutions,
                    prefix=f"{prefix}.{branch.id}",
                )
            }
        )
        for branch in branches
    ]


def _explicit_task_payload(task: TaskDefinition) -> dict[str, Any]:
    encoded = task.model_dump(mode="python", by_alias=True, exclude_none=True)
    explicit: dict[str, Any] = {}
    for name in task.model_fields_set:
        field = type(task).model_fields.get(name)
        alias = field.alias if field is not None and field.alias else name
        if alias in encoded:
            explicit[alias] = encoded[alias]
        elif name in encoded:
            explicit[name] = encoded[name]
    explicit["id"] = task.id
    explicit["type"] = task.type
    return explicit


def _merge_mapping(
    target: dict[str, Any],
    incoming: Mapping[str, Any],
    origins: dict[str, dict[str, Any]],
    origin: dict[str, Any],
    *,
    prefix: str = "",
) -> None:
    for key, value in incoming.items():
        path = f"{prefix}.{key}" if prefix else key
        current = target.get(key)
        if isinstance(current, dict) and isinstance(value, Mapping):
            _merge_mapping(current, value, origins, origin, prefix=path)
        else:
            target[key] = deepcopy(value)
            for stale in [item for item in origins if item == path or item.startswith(path + ".")]:
                origins.pop(stale, None)
            if isinstance(value, Mapping):
                _record_origins(value, origins, origin, prefix=path)
            else:
                origins[path] = dict(origin)


def _record_origins(
    value: Mapping[str, Any],
    origins: dict[str, dict[str, Any]],
    origin: dict[str, Any],
    *,
    prefix: str,
) -> None:
    for key, nested in value.items():
        path = f"{prefix}.{key}"
        if isinstance(nested, Mapping):
            _record_origins(nested, origins, origin, prefix=path)
        else:
            origins[path] = dict(origin)


def _normalize_text(value: str, operation: LabelNormalization) -> str:
    if operation is LabelNormalization.TRIM:
        return value.strip()
    if operation is LabelNormalization.LOWERCASE:
        return value.lower()
    return value.upper()


def _has_path(value: Mapping[str, Any], path: str) -> bool:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False
        current = current[part]
    return True


def _get_path(value: Mapping[str, Any], path: str) -> Any:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise KeyError(path)
        current = current[part]
    return deepcopy(current)


def _set_path(value: dict[str, Any], path: str, item: Any) -> None:
    parts = path.split(".")
    current = value
    for part in parts[:-1]:
        nested = current.get(part)
        if not isinstance(nested, dict):
            raise ValueError(f"default property path {path!r} is not an object path")
        current = nested
    current[parts[-1]] = item
