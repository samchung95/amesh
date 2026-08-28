from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID, uuid4

import pytest

from amesh.domain import ExecutionState
from amesh.dsl.models import FlowDefinition, TaskDefinition, TriggerDefinition
from amesh.ports import (
    ExecutionLaunchSource,
    ExecutionRepository,
    PersistedExecution,
    ScheduleState,
    TriggerOccurrence,
    TriggerOccurrenceAcceptance,
    TriggerOccurrenceState,
)
from amesh.scheduler import CronScheduler, ScheduleAction


class MemoryExecutionRepository:
    def __init__(self) -> None:
        self.executions: dict[str, PersistedExecution] = {}

    async def create_execution(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        inputs: dict[str, Any],
        trigger: dict[str, Any] | None = None,
        launch_source: ExecutionLaunchSource = ExecutionLaunchSource.MANUAL,
        idempotency_key: str | None = None,
        actor_id: str = "system:executor",
    ) -> PersistedExecution:
        del actor_id
        key = idempotency_key or str(uuid4())
        existing = self.executions.get(key)
        if existing is not None:
            return existing
        now = datetime.now(UTC)
        execution = PersistedExecution(
            execution_id=uuid4(),
            tenant_id=tenant_id,
            state=ExecutionState.RUNNING,
            epoch=1,
            version=0,
            namespace=flow.namespace,
            flow_id=flow.id,
            inputs=inputs,
            trigger={"source": launch_source.value, **(trigger or {})},
            created_at=now,
            updated_at=now,
        )
        self.executions[key] = execution
        return execution


class MemorySchedulerRepository:
    def __init__(self) -> None:
        self.state: ScheduleState | None = None

    async def database_time(self) -> datetime:
        return datetime.now(UTC)

    async def claim_schedule(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        flow_revision: int,
        trigger_id: str,
        initial_next_fire_at: datetime | None,
        due_before: datetime,
        owner_id: UUID,
        lease_duration: timedelta,
    ) -> ScheduleState:
        if self.state is None:
            self.state = ScheduleState(
                trigger_definition_id=uuid4(),
                tenant_id=tenant_id,
                namespace=namespace,
                flow_id=flow_id,
                flow_revision=flow_revision,
                trigger_id=trigger_id,
                next_fire_at=initial_next_fire_at,
                fencing_token=0,
                last_decision="schedule initialized",
                missed_count=0,
            )
        if self.state.next_fire_at is None or self.state.next_fire_at > due_before:
            return self.state.model_copy(update={"claimed": False})
        self.state = self.state.model_copy(
            update={
                "owner_id": owner_id,
                "fencing_token": self.state.fencing_token + 1,
                "lease_expires_at": due_before + lease_duration,
                "claimed": True,
            }
        )
        return self.state

    async def complete_schedule(
        self,
        *,
        tenant_id: str,
        trigger_definition_id: UUID,
        owner_id: UUID,
        fencing_token: int,
        evaluated_at: datetime,
        next_fire_at: datetime | None,
        last_occurrence_at: datetime | None,
        decision: str,
        missed_count: int,
    ) -> ScheduleState:
        assert self.state is not None
        assert self.state.tenant_id == tenant_id
        assert self.state.trigger_definition_id == trigger_definition_id
        assert self.state.owner_id == owner_id
        assert self.state.fencing_token == fencing_token
        self.state = self.state.model_copy(
            update={
                "next_fire_at": next_fire_at,
                "last_evaluated_at": evaluated_at,
                "last_occurrence_at": last_occurrence_at,
                "owner_id": None,
                "lease_expires_at": None,
                "last_decision": decision,
                "missed_count": missed_count,
                "claimed": False,
            }
        )
        return self.state

    async def get_schedule_state(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        flow_revision: int,
        trigger_id: str,
    ) -> ScheduleState:
        del tenant_id, namespace, flow_id, flow_revision, trigger_id
        if self.state is None:
            raise LookupError("schedule does not exist")
        return self.state


class RetryWaitTriggerRuntime:
    def __init__(self, scheduled_for: datetime) -> None:
        self.scheduled_for = scheduled_for
        self.claimed = False

    async def accept_occurrence(self, **kwargs: object) -> TriggerOccurrenceAcceptance:
        now = datetime.now(UTC)
        return TriggerOccurrenceAcceptance(
            occurrence=TriggerOccurrence(
                occurrence_id=uuid4(),
                tenant_id=str(kwargs["tenant_id"]),
                trigger_definition_id=uuid4(),
                namespace=str(kwargs["namespace"]),
                flow_id=str(kwargs["flow_id"]),
                flow_revision=int(str(kwargs["flow_revision"])),
                trigger_id=str(kwargs["trigger_id"]),
                trigger_type="core.cron",
                occurrence_key=str(kwargs["occurrence_key"]),
                state=TriggerOccurrenceState.RETRY_WAIT,
                attempt=1,
                max_attempts=3,
                available_at=now + timedelta(seconds=30),
                metadata={"source": "schedule"},
                created_at=now,
                updated_at=now,
            ),
            duplicate=True,
            accepted=False,
            reason="duplicate occurrence already retry_wait",
        )

    async def claim_occurrence(self, *args: object, **kwargs: object) -> TriggerOccurrence:
        del args, kwargs
        self.claimed = True
        raise AssertionError("retry-wait duplicate must remain with the occurrence worker")


def _scheduler() -> CronScheduler:
    return CronScheduler(cast(ExecutionRepository, object()))


def test_cron_dst_gap_is_skipped_and_overlap_uses_earliest_instant_once() -> None:
    trigger = TriggerDefinition(
        id="berlin_0230",
        type="core.cron",
        cron="30 2 * * *",
        timezone="Europe/Berlin",
    )
    scheduler = _scheduler()

    after_spring = datetime(2026, 3, 28, 2, tzinfo=UTC)
    assert scheduler.next_occurrence(trigger, after=after_spring).scheduled_for == datetime(
        2026, 3, 30, 0, 30, tzinfo=UTC
    )

    before_overlap = datetime(2026, 10, 24, 2, tzinfo=UTC)
    earliest = scheduler.next_occurrence(trigger, after=before_overlap).scheduled_for
    assert earliest == datetime(2026, 10, 25, 0, 30, tzinfo=UTC)
    assert scheduler.next_occurrence(trigger, after=earliest).scheduled_for == datetime(
        2026, 10, 26, 1, 30, tzinfo=UTC
    )


def test_interval_preview_honors_start_and_explains_condition() -> None:
    trigger = TriggerDefinition.model_validate(
        {
            "id": "quarter_hour",
            "type": "core.interval",
            "interval": "PT15M",
            "timezone": "UTC",
            "start": "2026-08-21T12:00:00Z",
            "condition": "{{ vars.enabled }}",
        }
    )
    flow = FlowDefinition(
        id="preview",
        namespace="tests.scheduler.preview",
        variables={"enabled": False},
        triggers=[trigger],
        tasks=[TaskDefinition(id="done", type="core.return", value="done")],
    )

    preview = _scheduler().preview(
        trigger,
        after=datetime(2026, 8, 21, 11, 0, tzinfo=UTC),
        count=2,
        flow=flow,
    )

    assert [item.scheduled_for for item in preview.occurrences] == [
        datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        datetime(2026, 8, 21, 12, 15, tzinfo=UTC),
    ]
    assert not preview.eligible
    assert preview.explanation == "trigger 'quarter_hour' condition evaluated false"


@pytest.mark.parametrize(
    ("flow_disabled", "trigger_fields", "expected"),
    [
        (True, {}, "flow tests.scheduler.constraints.preview is disabled"),
        (False, {"disabled": True}, "trigger 'every_minute' is disabled"),
        (False, {"paused": True}, "trigger 'every_minute' is paused"),
        (
            False,
            {"end": "2026-08-21T11:59:00Z"},
            "trigger 'every_minute' is past its end",
        ),
    ],
)
def test_preview_explains_disabled_paused_and_end_constraints(
    flow_disabled: bool,
    trigger_fields: dict[str, object],
    expected: str,
) -> None:
    trigger = TriggerDefinition.model_validate(
        {
            "id": "every_minute",
            "type": "core.cron",
            "cron": "* * * * *",
            "timezone": "UTC",
            **trigger_fields,
        }
    )
    flow = FlowDefinition(
        id="preview",
        namespace="tests.scheduler.constraints",
        disabled=flow_disabled,
        triggers=[trigger],
        tasks=[TaskDefinition(id="done", type="core.return", value="done")],
    )

    preview = _scheduler().preview(
        trigger,
        after=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        count=1,
        flow=flow,
    )

    assert not preview.eligible
    assert preview.explanation == expected


@pytest.mark.parametrize(
    ("policy", "expected_action", "expected_launches"),
    [
        ("SKIP", ScheduleAction.SKIPPED, 0),
        ("CATCH_UP", ScheduleAction.FIRED, 5),
        ("COALESCE", ScheduleAction.COALESCED, 1),
        ("BACKFILL", ScheduleAction.BACKFILL_REQUIRED, 0),
    ],
)
def test_misfire_policy_is_applied_to_persisted_cursor(
    policy: str,
    expected_action: ScheduleAction,
    expected_launches: int,
) -> None:
    async def scenario() -> None:
        execution_repository = MemoryExecutionRepository()
        schedule_repository = MemorySchedulerRepository()
        trigger = TriggerDefinition.model_validate(
            {
                "id": "every_minute",
                "type": "core.cron",
                "cron": "* * * * *",
                "timezone": "UTC",
                "misfirePolicy": policy,
                "misfireGraceSeconds": 0,
            }
        )
        flow = FlowDefinition(
            id=f"misfire_{policy.lower()}",
            namespace="tests.scheduler.misfire",
            triggers=[trigger],
            tasks=[TaskDefinition(id="done", type="core.return", value="done")],
        )
        scheduler = CronScheduler(
            cast(ExecutionRepository, execution_repository),
            schedule_repository,
            owner_id=uuid4(),
        )

        first = await scheduler.evaluate_due_occurrences(
            flow,
            at=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
            tenant_id="default",
        )
        assert len(first[0].executions) == 1

        recovered = await scheduler.evaluate_due_occurrences(
            flow,
            at=datetime(2026, 8, 21, 12, 5, 30, tzinfo=UTC),
            tenant_id="default",
        )
        assert recovered[0].action is expected_action
        assert len(recovered[0].executions) == expected_launches
        assert recovered[0].state.missed_count == 5
        assert recovered[0].state.next_fire_at == datetime(2026, 8, 21, 12, 6, tzinfo=UTC)

    asyncio.run(scenario())


def test_retry_wait_duplicate_advances_schedule_without_duplicate_launch() -> None:
    async def scenario() -> None:
        execution_repository = MemoryExecutionRepository()
        schedule_repository = MemorySchedulerRepository()
        scheduled_for = datetime(2026, 8, 25, 12, 0, tzinfo=UTC)
        trigger_runtime = RetryWaitTriggerRuntime(scheduled_for)
        flow = FlowDefinition(
            id="retry_wait",
            namespace="tests.scheduler.retry_wait",
            triggers=[
                TriggerDefinition(
                    id="every_minute",
                    type="core.cron",
                    cron="* * * * *",
                    timezone="UTC",
                )
            ],
            tasks=[TaskDefinition(id="done", type="core.return", value="done")],
        )
        scheduler = CronScheduler(
            cast(ExecutionRepository, execution_repository),
            schedule_repository,
            owner_id=uuid4(),
            trigger_runtime=trigger_runtime,  # type: ignore[arg-type]
        )

        evaluation = await scheduler.evaluate_due_occurrences(
            flow,
            at=scheduled_for,
            tenant_id="default",
        )

        assert evaluation[0].action is ScheduleAction.FIRED
        assert evaluation[0].executions == ()
        assert evaluation[0].state.next_fire_at == scheduled_for + timedelta(minutes=1)
        assert execution_repository.executions == {}
        assert trigger_runtime.claimed is False

    asyncio.run(scenario())
