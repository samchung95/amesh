from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

import httpx
import pytest

from amesh.app import (
    _bounded_agent_progress_page,
    app,
    authenticate_actor,
    get_agent_session_repository,
    get_authorization_service,
    get_repository,
    require_tenant_context,
)
from amesh.domain import (
    ActorContext,
    AgentProgressActivity,
    AgentProgressEvent,
    AgentProgressFrame,
    AgentProgressStatus,
    AgentSessionEventCursor,
    AgentSessionState,
    AuthorizationDecision,
    AuthorizationRequest,
    ExecutionState,
    PrincipalType,
)
from amesh.ports import PersistedExecution


def _progress_event(
    service_session_id: UUID,
    attempt_session_id: UUID,
    *,
    index: int,
    attempt: int = 1,
    activity: AgentProgressActivity,
    status: AgentProgressStatus,
) -> AgentProgressEvent:
    segment_id = uuid4() if activity is AgentProgressActivity.THINKING else None
    frame = AgentProgressFrame(
        attemptSessionId=attempt_session_id,
        attempt=attempt,
        turn=1,
        activity=activity,
        status=status,
        activityId=f"activity:{attempt}:{index}",
        segmentId=segment_id,
        sourceId="api:test",
        sourceSequence=index,
        occurredAt=datetime(2026, 8, 31, 12, 0, index, tzinfo=UTC),
    )
    cursor = AgentSessionEventCursor(
        serviceSessionId=service_session_id,
        attemptSessionId=attempt_session_id,
        attempt=attempt,
        eventIndex=index,
    )
    return AgentProgressEvent(
        serviceSessionId=service_session_id,
        eventId=uuid4(),
        eventIndex=index,
        cursor=cursor.encode(),
        acceptedAt=frame.occurred_at,
        frame=frame,
    )


def _execution(
    service_session_id: UUID,
    actor: ActorContext,
    *,
    state: ExecutionState = ExecutionState.RUNNING,
) -> PersistedExecution:
    now = datetime.now(UTC)
    return PersistedExecution(
        execution_id=uuid4(),
        tenant_id="default",
        state=state,
        epoch=1,
        version=1,
        namespace="research",
        flow_id="agent_session_research",
        created_at=now,
        updated_at=now,
        trigger={
            "ameshAgentSessionId": str(service_session_id),
            "ameshActorId": str(actor.principal_id),
        },
    )


def test_progress_page_cursor_reconnect_has_no_gaps_or_duplicates() -> None:
    service_session_id = uuid4()
    attempt_session_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="owner",
    )
    execution = _execution(service_session_id, actor)
    events = (
        _progress_event(
            service_session_id,
            attempt_session_id,
            index=1,
            activity=AgentProgressActivity.THINKING,
            status=AgentProgressStatus.STARTED,
        ),
        _progress_event(
            service_session_id,
            attempt_session_id,
            index=2,
            activity=AgentProgressActivity.TOOL,
            status=AgentProgressStatus.COMPLETED,
        ),
        _progress_event(
            service_session_id,
            attempt_session_id,
            index=3,
            activity=AgentProgressActivity.THINKING,
            status=AgentProgressStatus.STARTED,
        ),
    )
    calls: list[str] = []

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution.execution_id and tenant_id == "default"
            return execution

    class Sessions:
        async def get_execution_by_service_session_id(
            self,
            tenant_id: str,
            requested: UUID,
        ) -> UUID:
            assert tenant_id == "default" and requested == service_session_id
            return execution.execution_id

        async def list_progress_events(
            self,
            tenant_id: str,
            requested: UUID,
            *,
            after: AgentSessionEventCursor | None = None,
            limit: int = 100,
        ) -> tuple[AgentProgressEvent, ...]:
            assert calls and calls[-1] == "authorized"
            assert tenant_id == "default" and requested == service_session_id
            position = after.position if after is not None else (0, 0)
            return tuple(
                event
                for event in events
                if AgentSessionEventCursor.decode(event.cursor).position > position
            )[:limit]

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            calls.append("authorized")
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="owner view",
                policy_version=1,
                matched_role_names=("viewer",),
            )

    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            first = await client.get(
                f"/api/v1/agent-sessions/{service_session_id}/progress",
                params={"limit": 2},
                headers={"X-Amesh-Tenant": "default"},
            )
            assert first.status_code == 200, first.text
            first_body = first.json()
            assert [item["frame"]["activity"] for item in first_body["events"]] == [
                "THINKING",
                "TOOL",
            ]

            second = await client.get(
                f"/api/v1/agent-sessions/{service_session_id}/progress",
                params={"after": first_body["nextCursor"], "limit": 2},
                headers={"X-Amesh-Tenant": "default"},
            )
            assert second.status_code == 200, second.text
            second_body = second.json()
            assert [item["eventId"] for item in second_body["events"]] == [str(events[2].event_id)]
            assert second_body["nextCursor"] == events[2].cursor

            wrong_cursor = AgentSessionEventCursor(
                serviceSessionId=uuid4(),
                attemptSessionId=attempt_session_id,
                attempt=1,
                eventIndex=1,
            ).encode()
            wrong = await client.get(
                f"/api/v1/agent-sessions/{service_session_id}/progress",
                params={"after": wrong_cursor},
                headers={"X-Amesh-Tenant": "default"},
            )
            assert wrong.status_code == 400, wrong.text
            assert "different service session" in wrong.json()["detail"]

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_progress_page_clamps_requested_limit_to_declared_buffer_bound(monkeypatch) -> None:
    service_session_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="owner",
    )
    execution = _execution(service_session_id, actor)
    observed_limits: list[int] = []

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            return execution

    class Sessions:
        async def get_execution_by_service_session_id(
            self,
            tenant_id: str,
            requested: UUID,
        ) -> UUID:
            return execution.execution_id

        async def list_progress_events(
            self,
            tenant_id: str,
            requested: UUID,
            *,
            after: AgentSessionEventCursor | None = None,
            limit: int = 100,
        ) -> tuple[AgentProgressEvent, ...]:
            observed_limits.append(limit)
            return ()

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="owner view",
                policy_version=1,
                matched_role_names=("viewer",),
            )

    monkeypatch.setattr("amesh.app._AGENT_PROGRESS_MAX_BUFFERED_FRAMES", 2)
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                f"/api/v1/agent-sessions/{service_session_id}/progress",
                params={"limit": 1000},
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200, response.text
        assert observed_limits == [2]

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_progress_stream_denies_before_repository_iteration_or_response_bytes() -> None:
    service_session_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="denied-owner",
    )
    execution = _execution(service_session_id, actor)

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution.execution_id and tenant_id == "default"
            return execution

    class Sessions:
        async def get_execution_by_service_session_id(
            self,
            tenant_id: str,
            requested: UUID,
        ) -> UUID:
            assert tenant_id == "default" and requested == service_session_id
            return execution.execution_id

        async def list_progress_events(
            self,
            tenant_id: str,
            requested: UUID,
            *,
            after: AgentSessionEventCursor | None = None,
            limit: int = 100,
        ) -> tuple[AgentProgressEvent, ...]:
            raise AssertionError("authorization must run before progress iteration")

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            return AuthorizationDecision(
                allowed=False,
                reason_code="EXPLICIT_DENY",
                summary="session progress denied",
                policy_version=1,
                matched_role_names=("denied",),
            )

    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                f"/api/v1/agent-sessions/{service_session_id}/progress/stream",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 403, response.text
        assert "heartbeat" not in response.text

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_progress_stream_replays_direct_events_from_last_event_id_and_stops_at_terminal() -> None:
    service_session_id = uuid4()
    attempt_session_id = uuid4()
    retry_attempt_session_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="owner",
    )
    execution = _execution(service_session_id, actor)
    events = (
        _progress_event(
            service_session_id,
            attempt_session_id,
            index=1,
            activity=AgentProgressActivity.THINKING,
            status=AgentProgressStatus.STARTED,
        ),
        _progress_event(
            service_session_id,
            attempt_session_id,
            index=2,
            activity=AgentProgressActivity.TOOL,
            status=AgentProgressStatus.COMPLETED,
        ),
        _progress_event(
            service_session_id,
            attempt_session_id,
            index=3,
            activity=AgentProgressActivity.TERMINAL,
            status=AgentProgressStatus.FAILED,
        ),
        _progress_event(
            service_session_id,
            retry_attempt_session_id,
            index=1,
            attempt=2,
            activity=AgentProgressActivity.THINKING,
            status=AgentProgressStatus.STARTED,
        ),
        _progress_event(
            service_session_id,
            retry_attempt_session_id,
            index=2,
            attempt=2,
            activity=AgentProgressActivity.TERMINAL,
            status=AgentProgressStatus.COMPLETED,
        ),
    )

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution.execution_id and tenant_id == "default"
            return execution

    class Sessions:
        async def get_execution_by_service_session_id(
            self,
            tenant_id: str,
            requested: UUID,
        ) -> UUID:
            assert tenant_id == "default" and requested == service_session_id
            return execution.execution_id

        async def list_progress_events(
            self,
            tenant_id: str,
            requested: UUID,
            *,
            after: AgentSessionEventCursor | None = None,
            limit: int = 100,
        ) -> tuple[AgentProgressEvent, ...]:
            assert tenant_id == "default" and requested == service_session_id
            position = after.position if after is not None else (0, 0)
            return tuple(
                event
                for event in events
                if AgentSessionEventCursor.decode(event.cursor).position > position
            )[:limit]

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="owner view",
                policy_version=1,
                matched_role_names=("viewer",),
            )

    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                f"/api/v1/agent-sessions/{service_session_id}/progress/stream",
                headers={
                    "X-Amesh-Tenant": "default",
                    "Last-Event-ID": events[1].cursor,
                },
            )
            assert response.status_code == 200, response.text
            lines = [json.loads(line) for line in response.text.splitlines()]
            assert [line["frame"]["activity"] for line in lines] == [
                "TERMINAL",
                "THINKING",
                "TERMINAL",
            ]
            assert all("type" not in line for line in lines)
            final_first_attempt = await client.get(
                f"/api/v1/agent-sessions/{service_session_id}/progress/stream",
                params={"after": events[2].cursor},
                headers={"X-Amesh-Tenant": "default"},
            )
            assert final_first_attempt.status_code == 200, final_first_attempt.text
            replayed_retry = [json.loads(line) for line in final_first_attempt.text.splitlines()]
            assert [line["frame"]["activity"] for line in replayed_retry] == [
                "THINKING",
                "TERMINAL",
            ]

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("cursor_input", ["after", "last-event-id"])
def test_progress_stream_closes_after_final_terminal_cursor_without_heartbeat(
    cursor_input: str,
) -> None:
    service_session_id = uuid4()
    attempt_session_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="owner",
    )
    execution = _execution(service_session_id, actor)
    terminal = _progress_event(
        service_session_id,
        attempt_session_id,
        index=3,
        activity=AgentProgressActivity.TERMINAL,
        status=AgentProgressStatus.COMPLETED,
    )
    cursor = terminal.cursor

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution.execution_id and tenant_id == "default"
            return execution

    class Sessions:
        async def get_execution_by_service_session_id(
            self,
            tenant_id: str,
            requested: UUID,
        ) -> UUID:
            assert tenant_id == "default" and requested == service_session_id
            return execution.execution_id

        async def list_progress_events(
            self,
            tenant_id: str,
            requested: UUID,
            *,
            after: AgentSessionEventCursor | None = None,
            limit: int = 100,
        ) -> tuple[AgentProgressEvent, ...]:
            assert tenant_id == "default" and requested == service_session_id
            assert after is not None and after.encode() == cursor
            return ()

        async def list_execution_sessions(
            self,
            tenant_id: str,
            requested: UUID,
        ) -> tuple[object, ...]:
            assert tenant_id == "default" and requested == execution.execution_id

            class Attempt:
                session_id = attempt_session_id
                attempt = 1
                state = AgentSessionState.SUCCEEDED

            return (Attempt(),)

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="owner view",
                policy_version=1,
                matched_role_names=("viewer",),
            )

    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                f"/api/v1/agent-sessions/{service_session_id}/progress/stream",
                params=({"after": cursor} if cursor_input == "after" else None),
                headers={
                    "X-Amesh-Tenant": "default",
                    **({"Last-Event-ID": cursor} if cursor_input == "last-event-id" else {}),
                },
            )
        assert response.status_code == 200, response.text
        assert response.text == ""

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_progress_stream_keeps_heartbeat_while_later_retry_is_running(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service_session_id = uuid4()
    attempt_session_id = uuid4()
    retry_attempt_session_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="owner",
    )
    execution = _execution(service_session_id, actor)
    terminal = _progress_event(
        service_session_id,
        attempt_session_id,
        index=3,
        activity=AgentProgressActivity.TERMINAL,
        status=AgentProgressStatus.FAILED,
    )

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution.execution_id and tenant_id == "default"
            return execution

    class Sessions:
        async def get_execution_by_service_session_id(
            self,
            tenant_id: str,
            requested: UUID,
        ) -> UUID:
            assert tenant_id == "default" and requested == service_session_id
            return execution.execution_id

        async def list_progress_events(
            self,
            tenant_id: str,
            requested: UUID,
            *,
            after: AgentSessionEventCursor | None = None,
            limit: int = 100,
        ) -> tuple[AgentProgressEvent, ...]:
            assert tenant_id == "default" and requested == service_session_id
            assert after is not None and after.encode() == terminal.cursor
            return ()

        async def list_execution_sessions(
            self,
            tenant_id: str,
            requested: UUID,
        ) -> tuple[object, ...]:
            assert tenant_id == "default" and requested == execution.execution_id

            class TerminalAttempt:
                session_id = attempt_session_id
                attempt = 1
                state = AgentSessionState.FAILED

            class RunningRetryAttempt:
                session_id = retry_attempt_session_id
                attempt = 2
                state = AgentSessionState.RUNNING

            return TerminalAttempt(), RunningRetryAttempt()

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="owner view",
                policy_version=1,
                matched_role_names=("viewer",),
            )

    monkeypatch.setattr("amesh.app._AGENT_PROGRESS_STREAM_MAX_POLLS", 1)
    monkeypatch.setattr("amesh.app._AGENT_PROGRESS_STREAM_POLL_SECONDS", 0)
    monkeypatch.setattr("amesh.app._AGENT_PROGRESS_STREAM_HEARTBEAT_SECONDS", 0)
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                f"/api/v1/agent-sessions/{service_session_id}/progress/stream",
                params={"after": terminal.cursor},
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200, response.text
        lines = [json.loads(line) for line in response.text.splitlines()]
        assert lines == [
            {
                "type": "heartbeat",
                "sessionId": str(service_session_id),
                "cursor": terminal.cursor,
            }
        ]

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_progress_stream_authorizes_before_bytes_and_emits_bounded_heartbeat(
    monkeypatch,
) -> None:
    service_session_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="owner",
    )
    execution = _execution(service_session_id, actor, state=ExecutionState.QUEUED)
    authorized = False

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution.execution_id and tenant_id == "default"
            return execution

    class Sessions:
        async def get_execution_by_service_session_id(
            self,
            tenant_id: str,
            requested: UUID,
        ) -> UUID:
            assert tenant_id == "default" and requested == service_session_id
            return execution.execution_id

        async def list_progress_events(
            self,
            tenant_id: str,
            requested: UUID,
            *,
            after: AgentSessionEventCursor | None = None,
            limit: int = 100,
        ) -> tuple[AgentProgressEvent, ...]:
            assert authorized
            return ()

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            nonlocal authorized
            authorized = True
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="owner view",
                policy_version=1,
                matched_role_names=("viewer",),
            )

    monkeypatch.setattr("amesh.app._AGENT_PROGRESS_STREAM_MAX_POLLS", 3)
    monkeypatch.setattr("amesh.app._AGENT_PROGRESS_STREAM_POLL_SECONDS", 0)
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                f"/api/v1/agent-sessions/{service_session_id}/progress/stream",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200, response.text
        lines = response.text.splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0]) == {
            "type": "heartbeat",
            "sessionId": str(service_session_id),
            "cursor": AgentSessionEventCursor(
                serviceSessionId=service_session_id,
                attemptSessionId=None,
                attempt=0,
                eventIndex=0,
            ).encode(),
        }

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_bounded_progress_page_timeout_cancels_slow_observer(monkeypatch) -> None:
    service_session_id = uuid4()
    cancelled = False

    class Sessions:
        async def list_progress_events(
            self,
            tenant_id: str,
            requested: UUID,
            *,
            after: AgentSessionEventCursor | None = None,
            limit: int = 100,
        ) -> tuple[AgentProgressEvent, ...]:
            nonlocal cancelled
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                cancelled = True
                raise
            return ()

    monkeypatch.setattr("amesh.app._AGENT_PROGRESS_STREAM_POLL_TIMEOUT_SECONDS", 0.01)

    async def scenario() -> None:
        with pytest.raises(asyncio.TimeoutError):
            await _bounded_agent_progress_page(
                Sessions(),
                "default",
                service_session_id,
                after=AgentSessionEventCursor(
                    serviceSessionId=service_session_id,
                    attemptSessionId=None,
                    attempt=0,
                    eventIndex=0,
                ),
                limit=100,
            )

    asyncio.run(scenario())
    assert cancelled
