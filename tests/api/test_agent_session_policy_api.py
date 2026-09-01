from __future__ import annotations

import asyncio
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import HTTPException

from amesh.api.models import AgentSessionPolicyUpsertRequest
from amesh.authorization import AuthorizationDenied
from amesh.domain import (
    ActorContext,
    AgentSessionPolicy,
    AgentSessionPolicyRevision,
    AuthorizationDecision,
    AuthorizationRequest,
    PrincipalType,
    evaluate_agent_session_policies,
)


class _Authorization:
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self.requests: list[AuthorizationRequest] = []

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.requests.append(request)
        decision = AuthorizationDecision(
            allowed=self.allowed,
            reason_code="ROLE_GRANT" if self.allowed else "NO_MATCHING_GRANT",
            summary="test",
            policy_version=1,
            matched_role_names=("policy-admin",),
        )
        if not decision.allowed:
            raise AuthorizationDenied(decision)
        return decision


def _request(*, expected_revision: int | None = None) -> AgentSessionPolicyUpsertRequest:
    return AgentSessionPolicyUpsertRequest.model_validate(
        {
            "namespace": "research",
            "applicationId": "billing",
            "maxConcurrency": 4,
            "maxTotalTokens": 1000,
            "maxCostUsd": "2.50",
            "maxDurationSeconds": 600,
            "retentionSeconds": 3600,
            "expectedRevision": expected_revision,
        }
    )


def _actor() -> ActorContext:
    return ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="policy-admin"
    )


def test_policy_put_requires_strict_manage_permission_and_preserves_identity() -> None:
    import importlib

    app_module = importlib.import_module("amesh.app")
    authorization = _Authorization(allowed=True)
    saved: list[tuple[str, str | None, str | None, int | None]] = []

    class Repository:
        async def save_revision(self, tenant_id: str, policy: AgentSessionPolicy, **kwargs: object):
            saved.append(
                (
                    tenant_id,
                    kwargs["namespace"],
                    kwargs["application_id"],
                    kwargs["expected_revision"],
                )
            )
            return AgentSessionPolicyRevision(
                tenantId=tenant_id,
                namespace=kwargs["namespace"],
                applicationId=kwargs["application_id"],
                revision=1,
                spec=policy,
                digest=policy.digest,
                createdBy="admin",
                createdAt="2026-08-30T00:00:00Z",
            )

    result = asyncio.run(
        app_module.put_agent_session_policy(
            _request(expected_revision=0), Repository(), _actor(), authorization, "tenant-a"
        )
    )

    assert result.application_id == "billing"
    assert saved == [("tenant-a", "research", "billing", 0)]
    assert [
        (item.resource_type, item.action, item.namespace) for item in authorization.requests
    ] == [("agent_session_policy", "manage", "research")]


def test_policy_put_maps_stale_revision_to_conflict_without_save() -> None:
    import importlib

    app_module = importlib.import_module("amesh.app")
    authorization = _Authorization(allowed=True)

    class Repository:
        async def save_revision(self, *args: object, **kwargs: object):
            from amesh.ports import AgentSessionPolicyVersionConflict

            raise AgentSessionPolicyVersionConflict("stale")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            app_module.put_agent_session_policy(
                _request(expected_revision=4), Repository(), _actor(), authorization, "tenant-a"
            )
        )
    assert exc_info.value.status_code == 409


def test_application_policy_identity_requires_namespace() -> None:
    with pytest.raises(ValueError, match="requires namespace"):
        AgentSessionPolicyUpsertRequest.model_validate(
            {
                "applicationId": "billing",
                "maxConcurrency": 1,
                "maxTotalTokens": 1,
                "maxCostUsd": Decimal("0"),
                "maxDurationSeconds": 1,
                "retentionSeconds": 0,
            }
        )


def test_application_policy_scope_is_bound_to_authenticated_principal() -> None:
    import importlib

    app_module = importlib.import_module("amesh.app")
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="application-a"
    )

    assert app_module._resolve_agent_session_application_id(actor, None) == "application-a"
    with pytest.raises(HTTPException) as exc_info:
        app_module._resolve_agent_session_application_id(actor, "application-b")
    assert exc_info.value.status_code == 403

    policy = AgentSessionPolicy(
        admissionEnabled=False,
        maxConcurrency=1,
        maxTotalTokens=1,
        maxCostUsd=Decimal("0"),
        maxDurationSeconds=1,
        retentionSeconds=0,
    )
    revision = AgentSessionPolicyRevision(
        tenantId="tenant-a",
        namespace="research",
        applicationId="application-a",
        revision=1,
        spec=policy,
        digest=policy.digest,
        createdBy="admin",
        createdAt="2026-08-30T00:00:00Z",
    )
    with pytest.raises(ValueError, match="disabled"):
        evaluate_agent_session_policies(
            (revision,),
            envelope_max_total_tokens=1,
            envelope_max_cost_usd=Decimal("0"),
            envelope_max_duration_seconds=1,
            envelope_max_concurrency=1,
            requested_timeout_seconds=None,
            provider_ids=(),
            harness_id="pi",
            tool_ids=(),
        )
