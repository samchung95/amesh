from __future__ import annotations

from typing import overload

from amesh.domain.execution import ExecutionCommand, TaskRunCommand
from amesh.observability import current_trace_context


@overload
def attach_current_trace_context(command: ExecutionCommand) -> ExecutionCommand: ...


@overload
def attach_current_trace_context(command: TaskRunCommand) -> TaskRunCommand: ...


def attach_current_trace_context(
    command: ExecutionCommand | TaskRunCommand,
) -> ExecutionCommand | TaskRunCommand:
    """Attach ambient trace state at the runtime shell, outside the pure domain."""

    return command.model_copy(update={"trace_context": current_trace_context()})
