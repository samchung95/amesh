from __future__ import annotations

from amesh.dsl.descriptors import ResourceSchemaDescriptor

from .agent_tasks import agent_task_specifications
from .common import TaskSpecification
from .core_tasks import core_task_specifications
from .resources import resource_specifications


def all_descriptors() -> tuple[ResourceSchemaDescriptor, ...]:
    """Return built-in task, trigger and input descriptors in stable source order."""

    task_descriptors = tuple(
        specification.descriptor
        for specification in (*core_task_specifications(), *agent_task_specifications())
    )
    return (*task_descriptors, *resource_specifications())


__all__ = [
    "TaskSpecification",
    "agent_task_specifications",
    "all_descriptors",
    "core_task_specifications",
    "resource_specifications",
]
