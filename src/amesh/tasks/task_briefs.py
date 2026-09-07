from __future__ import annotations

from pydantic import ValidationError

from amesh.domain.task_briefs import AgentTaskBriefRevision
from amesh.executor import TaskExecutionContext


def selected_task_brief(context: TaskExecutionContext) -> AgentTaskBriefRevision | None:
    value = context.trigger.get("ameshTaskBrief")
    if value is None:
        return None
    try:
        brief = AgentTaskBriefRevision.model_validate(value)
    except ValidationError:
        raise PermissionError("accepted task brief is invalid") from None
    if (
        brief.tenant_id != context.tenant_id
        or brief.namespace != context.namespace
        or str(brief.session_id) != context.trigger.get("ameshAgentSessionId")
        or str(brief.producer_id) != context.trigger.get("ameshActorId")
    ):
        raise PermissionError("accepted task brief is outside the execution scope")
    return brief
