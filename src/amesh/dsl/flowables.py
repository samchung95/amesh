from __future__ import annotations

from dataclasses import dataclass

from .models import FlowableFailurePolicy, FlowDefinition, TaskDefinition

FLOWABLE_MODES = {
    "core.sequential": "SEQUENTIAL",
    "core.parallel": "PARALLEL",
    "core.dag": "DAG",
}


@dataclass(frozen=True)
class PlannedTask:
    task: TaskDefinition
    order: int
    parent_id: str | None
    dependencies: tuple[str, ...]
    children: tuple[str, ...]
    mode: str | None
    failure_policy: FlowableFailurePolicy
    max_concurrency: int | None

    @property
    def flowable(self) -> bool:
        return self.mode is not None


def compile_flow_tasks(flow: FlowDefinition) -> tuple[PlannedTask, ...]:
    """Compile nested flowables into one deterministic, durable task plan."""

    planned: list[PlannedTask] = []
    next_order = 0

    def walk(
        tasks: list[TaskDefinition],
        *,
        parent_id: str | None,
        entry_dependencies: tuple[str, ...],
        parent_mode: str | None,
    ) -> None:
        nonlocal next_order
        previous_id: str | None = None
        for task in tasks:
            order = next_order
            next_order += 1
            dependencies = [*entry_dependencies, *task.depends_on]
            if parent_mode == "SEQUENTIAL" and previous_id is not None:
                dependencies.append(previous_id)
            unique_dependencies = tuple(dict.fromkeys(dependencies))
            mode = FLOWABLE_MODES.get(task.type)
            node = PlannedTask(
                task=task,
                order=order,
                parent_id=parent_id,
                dependencies=unique_dependencies,
                children=tuple(child.id for child in task.tasks),
                mode=mode,
                failure_policy=task.failure_policy,
                max_concurrency=task.max_concurrency,
            )
            planned.append(node)
            if mode is not None:
                walk(
                    task.tasks,
                    parent_id=task.id,
                    entry_dependencies=unique_dependencies,
                    parent_mode=mode,
                )
            previous_id = task.id

    walk(
        flow.tasks,
        parent_id=None,
        entry_dependencies=(),
        parent_mode=None,
    )
    return tuple(sorted(planned, key=lambda node: node.order))


def visible_output_ids(task_id: str, plan: tuple[PlannedTask, ...]) -> frozenset[str]:
    """Return only transitive dependency outputs visible to one task."""

    by_id = {node.task.id: node for node in plan}
    visible: set[str] = set()
    pending = list(by_id[task_id].dependencies)
    while pending:
        dependency = pending.pop()
        if dependency in visible:
            continue
        visible.add(dependency)
        node = by_id.get(dependency)
        if node is not None:
            pending.extend(node.dependencies)
    return frozenset(visible)
