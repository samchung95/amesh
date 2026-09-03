from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .models import FlowableFailurePolicy, FlowDefinition, TaskDefinition

FLOWABLE_MODES = {
    "agent.mesh": "AGENT_MESH",
    "core.sequential": "SEQUENTIAL",
    "core.parallel": "PARALLEL",
    "core.dag": "DAG",
    "core.foreach": "FOREACH",
    "core.while": "WHILE",
    "core.until": "UNTIL",
    "core.if": "IF",
    "core.switch": "SWITCH",
    "core.workingDirectory": "WORKING_DIRECTORY",
}
FLOWABLE_TASK_TYPES = frozenset(FLOWABLE_MODES)

DYNAMIC_FLOWABLE_MODES = frozenset({"FOREACH", "WHILE", "UNTIL"})


class LifecyclePhase(StrEnum):
    MAIN = "MAIN"
    ERROR = "ERROR"
    FINALLY = "FINALLY"
    AFTER_EXECUTION = "AFTER_EXECUTION"


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
    branch_id: str | None
    lifecycle_phase: LifecyclePhase = LifecyclePhase.MAIN
    handler_owner_id: str | None = None

    @property
    def flowable(self) -> bool:
        return self.mode is not None

    @property
    def dynamic(self) -> bool:
        return self.mode in DYNAMIC_FLOWABLE_MODES


def _compile_task_group(
    tasks: list[TaskDefinition],
    *,
    start_order: int,
    lifecycle_phase: LifecyclePhase,
    handler_owner_id: str | None,
    root_sequential: bool,
) -> tuple[PlannedTask, ...]:
    planned: list[PlannedTask] = []
    next_order = start_order

    def walk(
        tasks: list[TaskDefinition],
        *,
        parent_id: str | None,
        entry_dependencies: tuple[str, ...],
        parent_mode: str | None,
        branch_id: str | None,
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
            child_groups = task.child_task_groups()
            node = PlannedTask(
                task=task,
                order=order,
                parent_id=parent_id,
                dependencies=unique_dependencies,
                children=tuple(child.id for _, children in child_groups for child in children),
                mode=mode,
                failure_policy=task.failure_policy,
                max_concurrency=task.max_concurrency,
                branch_id=branch_id,
                lifecycle_phase=lifecycle_phase,
                handler_owner_id=handler_owner_id,
            )
            planned.append(node)
            if mode is not None and mode not in DYNAMIC_FLOWABLE_MODES:
                for child_branch_id, children in child_groups:
                    walk(
                        children,
                        parent_id=task.id,
                        entry_dependencies=unique_dependencies,
                        parent_mode=(
                            "SEQUENTIAL" if mode in {"IF", "SWITCH", "WORKING_DIRECTORY"} else mode
                        ),
                        branch_id=(
                            (
                                f"{branch_id}/{child_branch_id}"
                                if branch_id is not None
                                else child_branch_id
                            )
                            if mode in {"IF", "SWITCH"}
                            else branch_id
                        ),
                    )
            previous_id = task.id

    walk(
        tasks,
        parent_id=None,
        entry_dependencies=(),
        parent_mode="SEQUENTIAL" if root_sequential else None,
        branch_id=None,
    )
    return tuple(sorted(planned, key=lambda node: node.order))


def compile_flow_tasks(flow: FlowDefinition) -> tuple[PlannedTask, ...]:
    """Compile the primary nested flowable graph into a deterministic task plan."""

    return _compile_task_group(
        flow.tasks,
        start_order=0,
        lifecycle_phase=LifecyclePhase.MAIN,
        handler_owner_id=None,
        root_sequential=False,
    )


def compile_execution_tasks(flow: FlowDefinition) -> tuple[PlannedTask, ...]:
    """Compile primary and lifecycle tasks with explicit phase and handler ownership."""

    planned = list(compile_flow_tasks(flow))

    def append_group(
        tasks: list[TaskDefinition],
        phase: LifecyclePhase,
        owner_id: str,
    ) -> None:
        if not tasks:
            return
        planned.extend(
            _compile_task_group(
                tasks,
                start_order=len(planned),
                lifecycle_phase=phase,
                handler_owner_id=owner_id,
                root_sequential=True,
            )
        )

    for owner in tuple(planned):
        if owner.lifecycle_phase is LifecyclePhase.MAIN:
            append_group(owner.task.errors, LifecyclePhase.ERROR, owner.task.id)
    append_group(flow.errors, LifecyclePhase.ERROR, "flow")
    append_group(flow.finally_tasks, LifecyclePhase.FINALLY, "flow")
    append_group(flow.after_execution, LifecyclePhase.AFTER_EXECUTION, "flow")
    return tuple(planned)


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
