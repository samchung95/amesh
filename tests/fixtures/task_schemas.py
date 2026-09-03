from __future__ import annotations

from amesh.dsl import (
    EditorMetadata,
    ResourceKind,
    ResourceSchemaDescriptor,
    ResourceSchemaRegistry,
    default_resource_registry,
)


def registered_test_task_registry(*task_types: str) -> ResourceSchemaRegistry:
    registry = default_resource_registry()
    for task_type in task_types:
        registry.register(
            ResourceSchemaDescriptor(
                type=task_type,
                kind=ResourceKind.TASK,
                configuration_schema={"type": "object"},
                editor=EditorMetadata(
                    title=task_type,
                    description="Test-only task handler.",
                    category="Tests",
                ),
            )
        )
    return registry
