from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException

from amesh.api.dependencies import authorize_request
from amesh.authorization import AuthorizationService
from amesh.domain import ActorContext, PermissionAction
from amesh.domain.task_briefs import AgentTaskBrief, AgentTaskBriefRevision, bind_task_brief
from amesh.workflow.shared_resources import NamespaceResourceService


async def admit_task_brief(
    document: AgentTaskBrief | None,
    *,
    previous: AgentTaskBriefRevision | None = None,
    expected_digest: str | None = None,
    tenant_id: str,
    namespace: str,
    session_id: UUID,
    turn: int,
    actor: ActorContext,
    authorization_service: AuthorizationService,
    namespace_resources: NamespaceResourceService | None,
) -> AgentTaskBriefRevision | None:
    if previous is not None and (
        previous.tenant_id != tenant_id
        or previous.namespace != namespace
        or previous.session_id != session_id
        or previous.producer_id != actor.principal_id
    ):
        raise HTTPException(
            status_code=403, detail="task brief is outside the producer session scope"
        )
    if document is not None and expected_digest != (previous.digest if previous else None):
        raise HTTPException(
            status_code=409, detail="expectedBriefDigest must match the current task brief"
        )
    selected = document or (previous.document if previous else None)
    if selected is None:
        return None
    for artifact in selected.artifacts:
        if artifact.tenant_id != tenant_id or artifact.namespace != namespace:
            raise HTTPException(
                status_code=403, detail="task brief artifact is outside the session scope"
            )
        await authorize_request(
            authorization_service,
            actor,
            resource_type="namespace_file",
            action=PermissionAction.READ,
            tenant_id=tenant_id,
            namespace=namespace,
        )
        if namespace_resources is None:
            raise LookupError("task brief artifact service is unavailable")
        actual = await namespace_resources.get_artifact(
            namespace,
            artifact.path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            version=artifact.version,
        )
        if (actual.reference, actual.content_address, actual.size_bytes) != (
            artifact.reference,
            artifact.content_address,
            artifact.size_bytes,
        ):
            raise ValueError("task brief artifact does not match the stored immutable version")
    return (
        bind_task_brief(
            selected,
            tenant_id=tenant_id,
            namespace=namespace,
            session_id=session_id,
            producer_id=actor.principal_id,
            turn=turn,
        )
        if document is not None
        else previous
    )
