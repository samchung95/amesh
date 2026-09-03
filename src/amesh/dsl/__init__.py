from importlib import import_module
from typing import TYPE_CHECKING, Any

from .descriptors import (
    HandlerConfigurationContract,
    TaskRuntimeOwnership,
    TaskSpecification,
)
from .flowables import (
    DYNAMIC_FLOWABLE_MODES,
    FLOWABLE_MODES,
    FLOWABLE_TASK_TYPES,
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

_LAZY_EXPORTS = {
    "validate_flow_document": "amesh.dsl.validator",
    "validator": "amesh.dsl.validator",
}

if TYPE_CHECKING:
    from .validator import validate_flow_document as validate_flow_document


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(module_name)
    value = module if name == "validator" else getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *_LAZY_EXPORTS})


__all__ = [
    "DYNAMIC_FLOWABLE_MODES",
    "FLOWABLE_MODES",
    "FLOWABLE_TASK_TYPES",
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
    "HandlerConfigurationContract",
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
    "TaskRuntimeOwnership",
    "TaskSpecification",
    "TaskTimeoutMode",
    "compile_execution_tasks",
    "compile_flow_tasks",
    "default_resource_registry",
    "parse_editable_flow_document",
    "validate_flow_document",
    "validator",
    "visible_output_ids",
]
