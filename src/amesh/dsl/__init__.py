from importlib import import_module
from typing import TYPE_CHECKING, Any

from .descriptors import TaskSpecification
from .flowables import (
    DYNAMIC_FLOWABLE_MODES,
    FLOWABLE_MODES,
    LifecyclePhase,
    PlannedTask,
    compile_execution_tasks,
    compile_flow_tasks,
    visible_output_ids,
)
from .models import (
    CheckActionDefinition,
    CheckDefinition,
    ConditionalBranch,
    ConditionErrorPolicy,
    ErrorSelector,
    FlowableFailurePolicy,
    FlowDefinition,
    FlowValidationResult,
    PluginDefaultDefinition,
    RunnableTaskContract,
    SourcePosition,
    SourceRange,
    TaskCacheInvalidationPolicy,
    TaskCachePolicy,
    TaskCacheScope,
    TaskDefinition,
    TaskResourceLimits,
    TaskTimeoutMode,
)
from .registry import (
    EditorMetadata,
    ResourceKind,
    ResourceSchemaDescriptor,
    ResourceSchemaRegistry,
    default_resource_registry,
)
from .source import EditableFlowDocument, FlowDocumentError, parse_editable_flow_document
from .task_configuration import TaskConfiguration

_LAZY_EXPORTS = {"validate_flow_document": "amesh.dsl.validator"}

if TYPE_CHECKING:
    from .validator import validate_flow_document as validate_flow_document


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *_LAZY_EXPORTS})


__all__ = [
    "DYNAMIC_FLOWABLE_MODES",
    "FLOWABLE_MODES",
    "CheckActionDefinition",
    "CheckDefinition",
    "ConditionErrorPolicy",
    "ConditionalBranch",
    "EditableFlowDocument",
    "EditorMetadata",
    "ErrorSelector",
    "FlowDefinition",
    "FlowDocumentError",
    "FlowValidationResult",
    "FlowableFailurePolicy",
    "LifecyclePhase",
    "PlannedTask",
    "PluginDefaultDefinition",
    "ResourceKind",
    "ResourceSchemaDescriptor",
    "ResourceSchemaRegistry",
    "RunnableTaskContract",
    "SourcePosition",
    "SourceRange",
    "TaskCacheInvalidationPolicy",
    "TaskCachePolicy",
    "TaskCacheScope",
    "TaskConfiguration",
    "TaskDefinition",
    "TaskResourceLimits",
    "TaskSpecification",
    "TaskTimeoutMode",
    "compile_execution_tasks",
    "compile_flow_tasks",
    "default_resource_registry",
    "parse_editable_flow_document",
    "validate_flow_document",
    "visible_output_ids",
]
