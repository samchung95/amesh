from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException

from amesh.api.models import AgentSessionCreateRequest
from amesh.api.task_briefs import admit_task_brief
from amesh.authorization import AuthorizationDenied
from amesh.domain import ActorContext, AuthorizationDecision, PrincipalType
from amesh.domain.artifacts import ArtifactRef, build_artifact_reference
from amesh.domain.task_briefs import AgentTaskBrief, bind_task_brief


def artifact() -> ArtifactRef:
    return ArtifactRef(
        reference=build_artifact_reference("approved/evidence.json", 3, "a" * 64),
        contentAddress="sha256:" + "a" * 64,
        tenantId="default",
        namespace="research",
        path="approved/evidence.json",
        version=3,
        sizeBytes=1000000,
        checksumSha256="a" * 64,
        provenance={
            "source": "namespace-file",
            "originNamespace": "research",
            "createdBy": "consumer",
            "createdAt": datetime.now(UTC),
        },
        retention={},
    )


def test_brief_admission_checks_scope_digest_and_artifact_authority_without_loading_bytes():
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="consumer"
    )
    session_id = uuid4()
    reference = artifact()
    calls = []

    class Authorization:
        allow = True

        async def require(self, request):
            calls.append(("authorize", request.namespace))
            decision = AuthorizationDecision(
                allowed=self.allow, reason_code="FIXTURE", summary="fixture", policy_version=1
            )
            if not self.allow:
                raise AuthorizationDenied(decision)
            return decision

    class Artifacts:
        async def get_artifact(self, namespace, path, **kwargs):
            assert calls[-1] == ("authorize", "research")
            assert namespace == "research" and path == reference.path and kwargs["version"] == 3
            calls.append(("metadata", path))
            return reference

    authorization = Authorization()
    kwargs = dict(
        tenant_id="default",
        namespace="research",
        session_id=session_id,
        actor=actor,
        authorization_service=authorization,
        namespace_resources=Artifacts(),
    )
    document = AgentTaskBrief(
        schemaId="consumer/task",
        schemaVersion="1",
        content={"decision": "approved"},
        artifacts=(reference,),
    )

    async def scenario():
        accepted = await admit_task_brief(document, turn=1, **kwargs)
        assert accepted is not None and accepted.document.artifacts == (reference,)
        assert calls == [("authorize", "research"), ("metadata", reference.path)]
        # A million-byte artifact contributes only its bounded reference, never its bytes.
        assert accepted.document.estimated_tokens < document.max_estimated_tokens
        inherited = await admit_task_brief(None, previous=accepted, turn=2, **kwargs)
        assert inherited == accepted
        with pytest.raises(HTTPException) as stale:
            await admit_task_brief(
                document, previous=accepted, expected_digest="sha256:" + "0" * 64, turn=2, **kwargs
            )
        assert stale.value.status_code == 409
        before = len(calls)
        with pytest.raises(HTTPException) as wrong_session:
            await admit_task_brief(
                None, previous=accepted, turn=2, **{**kwargs, "session_id": uuid4()}
            )
        assert wrong_session.value.status_code == 403 and len(calls) == before
        other_actor = actor.model_copy(update={"principal_id": uuid4()})
        with pytest.raises(HTTPException) as wrong_producer:
            await admit_task_brief(
                document,
                previous=accepted,
                expected_digest=accepted.digest,
                turn=2,
                **{**kwargs, "actor": other_actor},
            )
        assert wrong_producer.value.status_code == 403
        for update in ({"tenant_id": "other"}, {"namespace": "other"}):
            outside = document.model_copy(
                update={"artifacts": (reference.model_copy(update=update),)}
            )
            with pytest.raises(HTTPException) as denied:
                await admit_task_brief(outside, turn=1, **kwargs)
            assert denied.value.status_code == 403
        forged = document.model_copy(
            update={"artifacts": (reference.model_copy(update={"size_bytes": 1}),)}
        )
        with pytest.raises(ValueError, match="stored immutable version"):
            await admit_task_brief(forged, turn=1, **kwargs)
        authorization.allow = False
        before = len(calls)
        with pytest.raises(HTTPException):
            await admit_task_brief(document, turn=1, **kwargs)
        assert len(calls) == before + 1  # Denial precedes even metadata retrieval.

    asyncio.run(scenario())


@pytest.mark.parametrize("content,allocation", [("x" * 17000, 4096), ("x" * 1024, 64)])
def test_oversized_brief_fails_request_validation_before_admission(content, allocation):
    with pytest.raises(ValueError, match="taskBrief exceeds"):
        AgentSessionCreateRequest.model_validate(
            {
                "agentRef": "research/helper@1",
                "taskBrief": {
                    "schemaId": "consumer/task",
                    "schemaVersion": "1",
                    "content": {"text": content},
                    "maxEstimatedTokens": allocation,
                },
            }
        )


def test_brief_digest_covers_document_and_authenticated_scope():
    brief = bind_task_brief(
        AgentTaskBrief(schemaId="consumer/task", schemaVersion="1", content={"goal": "approved"}),
        tenant_id="default",
        namespace="research",
        session_id=uuid4(),
        producer_id=uuid4(),
        turn=1,
    )
    altered = brief.model_dump(mode="json", by_alias=True)
    altered["document"]["content"]["goal"] = "substituted"
    with pytest.raises(ValueError, match="immutable digest"):
        type(brief).model_validate(altered)
    assert "approved" not in str(brief.pin())
