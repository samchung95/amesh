"""Version-bracketed hydration over the existing execution and session journals."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException

from amesh.api.dependencies import (
    ActorDependency,
    AgentSessionRepositoryDependency,
    AuthorizationServiceDependency,
    RepositoryDependency,
)
from amesh.api.models import AgentSessionSnapshotResponse
from amesh.api.route_support import (
    _authorize_agent_session_access,
    _control_agent_session_summary,
    _get_service_agent_session_execution,
    _public_agent_session_detail,
    _queued_agent_session_summary,
)
from amesh.domain import AgentProgressEvent, AgentSessionDetail, AgentSessionEventCursor
from amesh.domain.agent_progress import AgentProgressFrame, project_agent_session_lifecycle_frame
from amesh.domain.agent_sessions import AgentSessionRecord


def _latest(records: tuple[AgentSessionRecord, ...]) -> AgentSessionRecord | None:
    return max(
        records, key=lambda item: (item.attempt, item.updated_at, item.session_id), default=None
    )


async def read_agent_session_snapshot(
    service_session_id: UUID,
    *,
    repository: RepositoryDependency,
    sessions: AgentSessionRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: str,
) -> AgentSessionSnapshotResponse:
    for _ in range(3):
        execution = await _get_service_agent_session_execution(
            service_session_id, repository=repository, sessions=sessions, tenant_id=tenant_id
        )
        await _authorize_agent_session_access(
            execution, actor=actor, authorization_service=authorization_service, tenant_id=tenant_id
        )
        record = _latest(await sessions.list_execution_sessions(tenant_id, execution.execution_id))
        detail = (
            await sessions.get_session(tenant_id, record.task_run_id, record.attempt)
            if record is not None
            else None
        )
        latest = _latest(await sessions.list_execution_sessions(tenant_id, execution.execution_id))
        checked = await _get_service_agent_session_execution(
            service_session_id, repository=repository, sessions=sessions, tenant_id=tenant_id
        )
        if (checked.execution_id, checked.version, checked.epoch) != (
            execution.execution_id,
            execution.version,
            execution.epoch,
        ) or (latest.session_id if latest else None) != (record.session_id if record else None):
            continue
        cursor = AgentSessionEventCursor(
            serviceSessionId=service_session_id, attempt=0, eventIndex=0
        )
        activity = None
        agent_ref = execution.trigger.get("ameshAgentRef")
        agent_ref = agent_ref if isinstance(agent_ref, str) else None
        summary = _queued_agent_session_summary(service_session_id, execution, agent_ref=agent_ref)
        if detail is not None:
            # Under READ COMMITTED the events query may see commits after the record read.
            detail = AgentSessionDetail(
                session=detail.session,
                events=tuple(e for e in detail.events if e.event_index <= detail.session.version),
            )
            summary = _control_agent_session_summary(
                service_session_id,
                execution,
                _public_agent_session_detail(detail, after_event_index=0, limit=1).session,
                agent_ref=agent_ref,
            )
            if detail.events:
                event = detail.events[-1]
                cursor = AgentSessionEventCursor(
                    serviceSessionId=service_session_id,
                    attemptSessionId=detail.session.session_id,
                    attempt=detail.session.attempt,
                    eventIndex=event.event_index,
                )
                frame = (
                    AgentProgressFrame.model_validate(event.payload["frame"])
                    if event.event_type == "progress.frame"
                    else project_agent_session_lifecycle_frame(
                        attempt_session_id=detail.session.session_id,
                        attempt=detail.session.attempt,
                        event_id=event.event_id,
                        event_index=event.event_index,
                        event_type=event.event_type,
                        payload=event.payload,
                        occurred_at=event.occurred_at,
                    )
                )
                activity = AgentProgressEvent(
                    serviceSessionId=service_session_id,
                    eventId=event.event_id,
                    eventIndex=event.event_index,
                    cursor=cursor.encode(),
                    acceptedAt=event.occurred_at,
                    frame=frame,
                )
        return AgentSessionSnapshotResponse(
            sessionId=service_session_id,
            executionId=execution.execution_id,
            turn=int(execution.trigger.get("ameshAgentSessionTurn", 1)),
            executionVersion=execution.version,
            executionEpoch=execution.epoch,
            attemptSessionId=detail.session.session_id if detail else None,
            sessionVersion=detail.session.version if detail else None,
            session=summary,
            activity=activity,
            resumeCursor=cursor.encode(),
        )
    raise HTTPException(
        status_code=503,
        detail="agent session changed during snapshot; retry",
        headers={"Retry-After": "1"},
    )
