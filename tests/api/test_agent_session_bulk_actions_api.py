from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from amesh.api.models import AgentSessionBulkActionRequest
from amesh.authorization import AuthorizationDenied
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    PermissionAction,
    PrincipalType,
)


class _Authorization:
    def __init__(self, *, allowed: bool = True) -> None:
        self.allowed = allowed
        self.requests: list[AuthorizationRequest] = []

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.requests.append(request)
        decision = AuthorizationDecision(
            allowed=self.allowed,
            reason_code="ROLE_GRANT" if self.allowed else "NO_MATCHING_GRANT",
            summary="test decision",
            policy_version=1,
            matched_role_names=("test-role",),
        )
        if not decision.allowed:
            raise AuthorizationDenied(decision)
        return decision


def _request(*session_ids: UUID, action: str = "pause") -> AgentSessionBulkActionRequest:
    return AgentSessionBulkActionRequest.model_validate(
        {
            "action": action,
            "items": [
                {
                    "sessionId": str(session_id),
                    "expectedVersion": index + 10,
                    "expectedEpoch": index + 1,
                }
                for index, session_id in enumerate(session_ids)
            ],
            "reason": "operator requested a bounded test action",
            "confirmation": f"{action.upper()} {len(session_ids)} AGENT SESSIONS",
        }
    )


def test_bulk_action_route_requires_both_new_tenant_scoped_permissions() -> None:
    import importlib

    app_module = importlib.import_module("amesh.app")
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    authorization = _Authorization(allowed=False)
    mutations: list[UUID] = []

    async def apply(*args: object, **kwargs: object) -> None:
        mutations.append(args[0])  # pragma: no cover

    original = app_module._apply_execution_control_authorized
    app_module._apply_execution_control_authorized = apply
    try:
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                app_module.bulk_control_agent_sessions(
                    _request(uuid4()),
                    object(),
                    object(),
                    actor,
                    authorization,
                    "tenant-a",
                )
            )
    finally:
        app_module._apply_execution_control_authorized = original

    assert exc_info.value.status_code == 403
    assert [
        (item.resource_type, item.action, item.tenant_id, item.namespace)
        for item in authorization.requests
    ] == [
        ("agent_session_administration", PermissionAction.VIEW, "tenant-a", None),
    ]
    assert mutations == []


def test_bulk_action_forwards_fences_and_returns_partial_results() -> None:
    import importlib

    app_module = importlib.import_module("amesh.app")
    first_session, second_session = uuid4(), uuid4()
    first_execution, second_execution = uuid4(), uuid4()
    authorization = _Authorization()
    calls: list[tuple[UUID, object, int, int]] = []

    async def resolve(
        session_id: UUID,
        *,
        repository: object,
        sessions: object,
        tenant_id: str,
    ) -> SimpleNamespace:
        return SimpleNamespace(
            execution_id=first_execution if session_id == first_session else second_execution
        )

    async def apply(
        execution_id: UUID,
        request: object,
        repository: object,
        actor: ActorContext,
        tenant_id: str,
    ) -> None:
        calls.append(
            (execution_id, request.action, request.expected_version, request.expected_epoch)
        )
        if execution_id == first_execution:
            raise HTTPException(status_code=409, detail="stale execution fence")

    original_resolve = app_module._get_service_agent_session_execution
    original_apply = app_module._apply_execution_control_authorized
    app_module._get_service_agent_session_execution = resolve
    app_module._apply_execution_control_authorized = apply
    try:
        response = asyncio.run(
            app_module.bulk_control_agent_sessions(
                _request(first_session, second_session),
                object(),
                object(),
                ActorContext(
                    principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
                ),
                authorization,
                "tenant-a",
            )
        )
    finally:
        app_module._get_service_agent_session_execution = original_resolve
        app_module._apply_execution_control_authorized = original_apply

    assert response.total == 2
    assert response.applied == 1
    assert response.rejected == 1
    assert [result.status for result in response.results] == ["rejected", "applied"]
    assert calls == [
        (first_execution, "PAUSE", 10, 1),
        (second_execution, "PAUSE", 11, 2),
    ]


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        ("duplicate", "unique sessionId"),
        ("confirmation", "confirmation"),
        ("too_many", "at most 25"),
    ],
)
def test_bulk_action_guards_reject_before_mutation(mutator: str, message: str) -> None:
    session_id = uuid4()
    payload = {
        "action": "pause",
        "items": [{"sessionId": str(session_id), "expectedVersion": 1, "expectedEpoch": 1}],
        "reason": "guard test",
        "confirmation": "PAUSE 1 AGENT SESSIONS",
    }
    if mutator == "duplicate":
        payload["items"].append(payload["items"][0])
        payload["confirmation"] = "PAUSE 2 AGENT SESSIONS"
    elif mutator == "confirmation":
        payload["confirmation"] = "PAUSE 1 SESSIONS"
    else:
        payload["items"] = [
            {"sessionId": str(uuid4()), "expectedVersion": 1, "expectedEpoch": 1} for _ in range(26)
        ]
        payload["confirmation"] = "PAUSE 26 AGENT SESSIONS"

    with pytest.raises(ValueError, match=message):
        AgentSessionBulkActionRequest.model_validate(payload)
