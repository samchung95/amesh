from __future__ import annotations

import asyncio
from collections.abc import Callable
from uuid import UUID, uuid4

import httpx
import pytest
from tests.api.test_agent_progress_api import _execution

from amesh.app import (
    app,
    authenticate_actor,
    get_agent_session_repository,
    get_authorization_service,
    get_repository,
    require_tenant_context,
)
from amesh.domain import (
    ActorContext,
    AgentProgressEvent,
    AgentSessionDetail,
    AgentSessionEvent,
    AgentSessionEventCursor,
    AgentSessionRecord,
    AgentSessionState,
    AuthorizationDecision,
    AuthorizationRequest,
    ExecutionState,
    PrincipalType,
)
from amesh.domain.agent_progress import project_agent_session_lifecycle_frame


class SnapshotStore:
    def __init__(self) -> None:
        self.session_id = uuid4()
        self.actor = ActorContext(
            principal_id=uuid4(), principal_type=PrincipalType.USER, display="owner"
        )
        self.execution = _execution(self.session_id, self.actor)
        self.executions = {self.execution.execution_id: self.execution}
        self.records: dict[UUID, AgentSessionRecord] = {}
        self.events: dict[UUID, tuple[AgentSessionEvent, ...]] = {}
        self.after_detail: Callable[[], None] | None = None
        self.allow = True
        self.authorized = False
        self.detail_reads = 0
        self.start()

    def start(self, attempt: int = 1) -> None:
        record = AgentSessionRecord(
            tenantId="default",
            namespace="research",
            executionId=self.execution.execution_id,
            taskRunId=uuid4(),
            attempt=attempt,
            capabilityPinId=uuid4(),
            envelopeDigest="sha256:" + "1" * 64,
            version=1,
            checkpoint={"messages": [{"role": "user", "content": "PRIVATE PROMPT"}]},
        )
        self.records[self.execution.execution_id] = record
        self.events[record.session_id] = (
            AgentSessionEvent(
                sessionId=record.session_id,
                eventIndex=1,
                eventKey="start",
                eventType="session.started",
                payload={"prompt": "PRIVATE PROMPT", "continuation": "PRIVATE CONTINUATION"},
            ),
        )

    def finish(self, *, execution_transition: bool = True, failed: bool = False) -> None:
        record = self.records[self.execution.execution_id]
        self.records[self.execution.execution_id] = record.model_copy(
            update={
                "version": 2,
                "state": AgentSessionState.FAILED if failed else AgentSessionState.SUCCEEDED,
                "error": "Output rejected" if failed else None,
            }
        )
        self.events[record.session_id] += (
            AgentSessionEvent(
                sessionId=record.session_id,
                eventIndex=2,
                eventKey="terminal",
                eventType="session.failed" if failed else "output.accepted",
                payload={}
                if failed
                else {
                    "result": {
                        "answer": "turn one",
                        "prompt": "PRIVATE PROMPT",
                        "token": "PRIVATE TOKEN",
                    }
                },
            ),
        )
        if execution_transition:
            self.execution = self.execution.model_copy(
                update={
                    "version": 2,
                    "state": ExecutionState.FAILED if failed else ExecutionState.SUCCESS,
                }
            )
            self.executions[self.execution.execution_id] = self.execution

    def follow_up(self) -> None:
        self.execution = self.execution.model_copy(
            update={
                "execution_id": uuid4(),
                "state": ExecutionState.QUEUED,
                "version": 1,
                "trigger": {**self.execution.trigger, "ameshAgentSessionTurn": 2},
            }
        )
        self.executions[self.execution.execution_id] = self.execution

    async def get_execution_by_service_session_id(self, tenant_id: str, requested: UUID) -> UUID:
        assert tenant_id == "default" and requested == self.session_id
        return self.execution.execution_id

    async def get_execution(self, requested: UUID, *, tenant_id: str):
        assert tenant_id == "default"
        return self.executions[requested]

    async def list_execution_sessions(self, tenant_id: str, execution_id: UUID):
        assert self.authorized and tenant_id == "default"
        record = self.records.get(execution_id)
        return (record,) if record else ()

    async def get_session(self, tenant_id: str, task_run_id: UUID, attempt: int):
        assert self.authorized and tenant_id == "default"
        self.detail_reads += 1
        record = next(
            r
            for r in self.records.values()
            if r.task_run_id == task_run_id and r.attempt == attempt
        )
        if self.after_detail:
            self.after_detail()
        return AgentSessionDetail(session=record, events=self.events[record.session_id])

    async def list_progress_events(self, tenant_id: str, requested: UUID, *, after=None, limit=100):
        assert self.authorized and tenant_id == "default" and requested == self.session_id
        result = []
        for record in sorted(self.records.values(), key=lambda r: r.attempt):
            for event in self.events[record.session_id]:
                cursor = AgentSessionEventCursor(
                    serviceSessionId=requested,
                    attemptSessionId=record.session_id,
                    attempt=record.attempt,
                    eventIndex=event.event_index,
                )
                if after is not None and cursor.position <= after.position:
                    continue
                result.append(
                    AgentProgressEvent(
                        serviceSessionId=requested,
                        eventId=event.event_id,
                        eventIndex=event.event_index,
                        cursor=cursor.encode(),
                        acceptedAt=event.occurred_at,
                        frame=project_agent_session_lifecycle_frame(
                            attempt_session_id=record.session_id,
                            attempt=record.attempt,
                            event_id=event.event_id,
                            event_index=event.event_index,
                            event_type=event.event_type,
                            payload=event.payload,
                            occurred_at=event.occurred_at,
                        ),
                    )
                )
        return tuple(result[:limit])

    async def decide(self, request: AuthorizationRequest):
        self.authorized = self.allow
        return AuthorizationDecision(
            allowed=self.allow, reason_code="FIXTURE", summary="fixture", policy_version=1
        )


@pytest.fixture
def store():
    fixture = SnapshotStore()
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: fixture.actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: lambda: fixture,
            get_repository: lambda: fixture,
            get_agent_session_repository: lambda: fixture,
        }
    )
    yield fixture
    app.dependency_overrides.clear()


async def get(store: SnapshotStore, path="snapshot", **params):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
    ) as client:
        return await client.get(
            f"/api/v1/agent-sessions/{store.session_id}/{path}",
            params=params,
            headers={"X-Amesh-Tenant": "default"},
        )


@pytest.mark.parametrize("failed", [False, True])
def test_snapshot_terminal_transition_resumes_without_gap_and_binds_result(store, failed):
    async def scenario():
        initial = await get(store)
        assert initial.status_code == 200, initial.text
        snapshot = initial.json()
        assert snapshot["schemaVersion"] == "amesh.agent-session-snapshot/v1"
        assert snapshot["session"]["state"] == "RUNNING"
        assert snapshot["session"]["result"] is None
        assert snapshot["activity"]["cursor"] == snapshot["resumeCursor"]
        assert "PRIVATE" not in initial.text
        # Completion commits after hydration but before subscribing.
        store.finish(failed=failed)
        resumed = await get(store, "progress", after=snapshot["resumeCursor"])
        assert len(resumed.json()["events"]) == 1
        terminal_event = resumed.json()["events"][0]
        assert terminal_event["frame"]["activity"] == "TERMINAL"
        repeated = await get(store, "progress", after=snapshot["resumeCursor"])
        assert repeated.json()["events"][0]["eventId"] == terminal_event["eventId"]
        terminal = await get(store)
        body = terminal.json()
        assert body["executionId"] == snapshot["executionId"]
        assert body["turn"] == 1 and body["sessionVersion"] == 2
        assert body["session"]["state"] == ("FAILED" if failed else "SUCCEEDED")
        if failed:
            assert body["session"]["result"] is None
            assert body["session"]["error"] == "Output rejected"
        else:
            assert body["session"]["result"]["answer"] == "turn one"
        assert "PRIVATE" not in terminal.text
        assert (await get(store, "progress/stream", after=body["resumeCursor"])).text == ""
        before = (len(store.executions), dict(store.events))
        assert (await get(store)).json() == body
        assert before == (len(store.executions), store.events)

    asyncio.run(scenario())


def test_snapshot_follow_up_before_subscription_is_discoverable_without_old_result(store):
    async def scenario():
        store.finish()
        terminal = (await get(store)).json()
        store.follow_up()
        queued = (await get(store)).json()
        assert queued["executionId"] != terminal["executionId"]
        assert queued["turn"] == 2 and queued["session"]["state"] == "QUEUED"
        assert queued["session"]["result"] is None
        assert queued["attemptSessionId"] is None
        # A queued turn has no watermark yet and permits stable-ID replay.
        assert AgentSessionEventCursor.decode(queued["resumeCursor"]).attempt == 0
        store.start(attempt=2)
        store.finish()
        resumed = (await get(store, "progress/stream", after=terminal["resumeCursor"])).text
        assert str(store.records[store.execution.execution_id].session_id) in resumed
        assert terminal["attemptSessionId"] not in resumed
        latest = (await get(store)).json()
        assert latest["executionId"] == queued["executionId"] and latest["turn"] == 2

    asyncio.run(scenario())


def test_snapshot_clamps_events_to_record_version_when_terminal_commits_during_read(store):
    def transition():
        store.after_detail = None
        store.finish(execution_transition=False)

    store.after_detail = transition

    async def scenario():
        body = (await get(store)).json()
        assert body["sessionVersion"] == 1
        assert body["session"]["state"] == "RUNNING" and body["session"]["result"] is None
        resumed = (await get(store, "progress", after=body["resumeCursor"])).json()
        assert resumed["events"][0]["eventIndex"] == 2

    asyncio.run(scenario())


def test_snapshot_retries_follow_up_committed_during_read(store):
    def transition():
        store.after_detail = None
        store.finish()
        store.follow_up()

    store.after_detail = transition
    response = asyncio.run(get(store))
    assert response.status_code == 200, response.text
    assert response.json()["turn"] == 2
    assert response.json()["session"]["result"] is None


def test_snapshot_repeated_transition_returns_retryable_response(store):
    def change_version():
        store.execution = store.execution.model_copy(
            update={"version": store.execution.version + 1}
        )
        store.executions[store.execution.execution_id] = store.execution

    store.after_detail = change_version
    response = asyncio.run(get(store))
    assert response.status_code == 503 and response.headers["Retry-After"] == "1"
    assert store.detail_reads == 3


def test_snapshot_denies_before_journal_read_or_private_response_bytes(store):
    store.allow = False
    response = asyncio.run(get(store))
    assert response.status_code in {403, 404}
    assert store.detail_reads == 0 and "PRIVATE" not in response.text
