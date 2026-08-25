from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from math import floor
from uuid import UUID
from zoneinfo import ZoneInfo

from croniter import croniter

from amesh.domain import OperationalBoundary, new_runtime_id
from amesh.dsl import FlowDefinition
from amesh.dsl.models import TriggerDefinition
from amesh.expressions import ExpressionContext, ExpressionEngine, NativeExpressionEngine
from amesh.ports import (
    ExecutionLaunchSource,
    ExecutionRepository,
    OperationalControlEvaluator,
    PersistedExecution,
    SchedulerRepository,
    ScheduleState,
    TriggerOccurrenceState,
    TriggerRuntimeRepository,
)


class ScheduleAction(StrEnum):
    NOT_DUE = "NOT_DUE"
    FIRED = "FIRED"
    SKIPPED = "SKIPPED"
    COALESCED = "COALESCED"
    BACKFILL_REQUIRED = "BACKFILL_REQUIRED"


@dataclass(frozen=True)
class CronOccurrence:
    trigger_id: str
    scheduled_for: datetime


@dataclass(frozen=True)
class SchedulePreview:
    trigger_id: str
    eligible: bool
    explanation: str
    occurrences: tuple[CronOccurrence, ...]


@dataclass(frozen=True)
class ScheduleEvaluation:
    trigger_id: str
    action: ScheduleAction
    explanation: str
    due_occurrences: tuple[CronOccurrence, ...]
    executions: tuple[PersistedExecution, ...]
    state: ScheduleState


class CronScheduler:
    """Deterministic temporal scheduler with optional PostgreSQL cursor ownership."""

    def __init__(
        self,
        repository: ExecutionRepository,
        scheduler_repository: SchedulerRepository | None = None,
        *,
        owner_id: UUID | None = None,
        lease_duration: timedelta = timedelta(seconds=30),
        expressions: ExpressionEngine | None = None,
        trigger_runtime: TriggerRuntimeRepository | None = None,
        operational_controls: OperationalControlEvaluator | None = None,
    ) -> None:
        if lease_duration.total_seconds() <= 0:
            raise ValueError("scheduler lease duration must be positive")
        self._repository = repository
        self._scheduler_repository = scheduler_repository
        self._owner_id = owner_id or new_runtime_id()
        self._lease_duration = lease_duration
        self._expressions = expressions or NativeExpressionEngine()
        self._trigger_runtime = trigger_runtime
        self._operational_controls = operational_controls

    def next_occurrence(
        self,
        trigger: TriggerDefinition,
        *,
        after: datetime,
    ) -> CronOccurrence:
        scheduled_for = _next_schedule_instant(trigger, _require_aware(after))
        return CronOccurrence(trigger_id=trigger.id, scheduled_for=scheduled_for)

    def preview(
        self,
        trigger: TriggerDefinition,
        *,
        after: datetime,
        count: int = 5,
        flow: FlowDefinition | None = None,
    ) -> SchedulePreview:
        if count < 1 or count > 100:
            raise ValueError("schedule preview count must be between 1 and 100")
        _require_schedule_trigger(trigger)
        cursor = _require_aware(after)
        if trigger.start_at is not None:
            cursor = max(
                cursor,
                trigger.start_at.astimezone(UTC) - timedelta(microseconds=1),
            )
        occurrences: list[CronOccurrence] = []
        for _ in range(count):
            occurrence = self.next_occurrence(trigger, after=cursor)
            if trigger.end_at is not None and occurrence.scheduled_for > trigger.end_at.astimezone(
                UTC
            ):
                break
            occurrences.append(occurrence)
            cursor = occurrence.scheduled_for
        preview_at = occurrences[0].scheduled_for if occurrences else cursor
        reason = (
            self._constraint_reason(flow, trigger, preview_at)
            if flow is not None
            else _constraint_reason(None, trigger, preview_at)
        )
        explanation = reason or f"next {len(occurrences)} occurrence(s) are eligible"
        return SchedulePreview(
            trigger_id=trigger.id,
            eligible=reason is None and bool(occurrences),
            explanation=explanation,
            occurrences=tuple(occurrences),
        )

    async def fire_occurrence(
        self,
        flow: FlowDefinition,
        *,
        trigger_id: str,
        scheduled_for: datetime,
        tenant_id: str,
        inputs: dict[str, object] | None = None,
        occurrence_metadata: dict[str, object] | None = None,
    ) -> PersistedExecution | None:
        trigger = _find_trigger(flow, trigger_id)
        scheduled_utc = _require_aware(scheduled_for).astimezone(UTC).replace(microsecond=0)
        if not _is_schedule_instant(trigger, scheduled_utc):
            raise ValueError(
                f"{scheduled_utc.isoformat()} is not an occurrence of trigger {trigger.id!r}"
            )
        reason = self._constraint_reason(flow, trigger, scheduled_utc)
        if reason is not None:
            raise ValueError(reason)
        if self._operational_controls is not None:
            for boundary in (
                OperationalBoundary.TRIGGERS,
                OperationalBoundary.NEW_EXECUTIONS,
            ):
                decision = await self._operational_controls.evaluate(
                    boundary,
                    tenant_id=tenant_id,
                    namespace=flow.namespace,
                    flow_id=flow.id,
                    component_id=f"scheduler:{self._owner_id}",
                    component_role="SCHEDULER",
                )
                if decision.blocked:
                    raise RuntimeError(f"{boundary.value.lower()} blocked by operational control")
        occurrence_key = (
            f"{trigger.type}:{flow.namespace}:{flow.id}:{flow.revision}:"
            f"{trigger.id}:{scheduled_utc.isoformat()}"
        )
        trigger_context: dict[str, object] = {
            "id": trigger.id,
            "type": trigger.type,
            "date": scheduled_utc.isoformat(),
            "timezone": trigger.timezone,
        }
        trigger_context.update(occurrence_metadata or {})
        claimed = None
        if self._trigger_runtime is not None:
            acceptance = await self._trigger_runtime.accept_occurrence(
                tenant_id=tenant_id,
                namespace=flow.namespace,
                flow_id=flow.id,
                flow_revision=flow.revision,
                trigger_id=trigger.id,
                occurrence_key=occurrence_key,
                payload=inputs or {},
                metadata={
                    "source": "schedule",
                    "observedAt": scheduled_utc.isoformat(),
                    **(occurrence_metadata or {}),
                },
                max_pending=trigger.max_pending,
                max_attempts=trigger.max_attempts,
                retry_delay=trigger.retry_delay,
            )
            if acceptance.duplicate and acceptance.occurrence.execution_id is not None:
                return await self._repository.get_execution(
                    acceptance.occurrence.execution_id,
                    tenant_id=tenant_id,
                )
            if acceptance.duplicate:
                return None
            if acceptance.occurrence.state is not TriggerOccurrenceState.ACCEPTED:
                return None
            claimed = await self._trigger_runtime.claim_occurrence(
                acceptance.occurrence.occurrence_id,
                tenant_id=tenant_id,
                owner_id=self._owner_id,
                lease_duration=self._lease_duration,
            )
        try:
            execution = await self._repository.create_execution(
                flow,
                tenant_id=tenant_id,
                inputs=inputs or {},
                trigger=trigger_context,
                launch_source=ExecutionLaunchSource.SCHEDULED,
                idempotency_key=occurrence_key,
            )
        except Exception as exc:
            if self._trigger_runtime is not None and claimed is not None:
                await self._trigger_runtime.fail_occurrence(
                    claimed.occurrence_id,
                    tenant_id=tenant_id,
                    owner_id=self._owner_id,
                    fencing_token=claimed.fencing_token,
                    error=str(exc),
                    retry_delay=trigger.retry_delay,
                )
            raise
        if self._trigger_runtime is not None and claimed is not None:
            await self._trigger_runtime.complete_occurrence(
                claimed.occurrence_id,
                tenant_id=tenant_id,
                owner_id=self._owner_id,
                fencing_token=claimed.fencing_token,
                execution_id=execution.execution_id,
                evidence={
                    "decision": "launched",
                    "reason": "scheduled occurrence created an execution",
                    "scheduledFor": scheduled_utc.isoformat(),
                },
            )
        return execution

    async def fire_due_occurrences(
        self,
        flow: FlowDefinition,
        *,
        at: datetime,
        tenant_id: str,
    ) -> list[PersistedExecution]:
        evaluations = await self.evaluate_due_occurrences(flow, at=at, tenant_id=tenant_id)
        return [execution for item in evaluations for execution in item.executions]

    async def evaluate_due_occurrences(
        self,
        flow: FlowDefinition,
        *,
        at: datetime,
        tenant_id: str,
    ) -> list[ScheduleEvaluation]:
        if self._scheduler_repository is None:
            raise RuntimeError("persistent scheduler repository is required for due evaluation")
        evaluated_at = _require_aware(at).astimezone(UTC)
        evaluations: list[ScheduleEvaluation] = []
        for trigger in flow.triggers:
            if trigger.type not in {"core.cron", "core.interval"}:
                continue
            evaluations.append(
                await self._evaluate_trigger(
                    flow,
                    trigger,
                    evaluated_at=evaluated_at,
                    tenant_id=tenant_id,
                )
            )
        return evaluations

    async def _evaluate_trigger(
        self,
        flow: FlowDefinition,
        trigger: TriggerDefinition,
        *,
        evaluated_at: datetime,
        tenant_id: str,
    ) -> ScheduleEvaluation:
        if self._scheduler_repository is None:
            raise RuntimeError("persistent scheduler repository is required for due evaluation")
        initial_next_fire = _initial_next_fire(trigger, evaluated_at)
        state = await self._scheduler_repository.claim_schedule(
            tenant_id=tenant_id,
            namespace=flow.namespace,
            flow_id=flow.id,
            flow_revision=flow.revision,
            trigger_id=trigger.id,
            initial_next_fire_at=initial_next_fire,
            due_before=evaluated_at,
            owner_id=self._owner_id,
            lease_duration=self._lease_duration,
        )
        if not state.claimed:
            explanation = (
                "schedule is not due"
                if state.next_fire_at is None or state.next_fire_at > evaluated_at
                else "schedule is owned by another live scheduler"
            )
            return ScheduleEvaluation(
                trigger_id=trigger.id,
                action=ScheduleAction.NOT_DUE,
                explanation=explanation,
                due_occurrences=(),
                executions=(),
                state=state,
            )

        due, next_fire = _due_occurrences(trigger, state.next_fire_at, evaluated_at)
        constraint = self._constraint_reason(
            flow, trigger, due[0].scheduled_for if due else evaluated_at
        )
        selected: list[CronOccurrence] = []
        metadata: dict[str, object] | None = None
        action = ScheduleAction.SKIPPED
        missed = [
            item
            for item in due
            if (evaluated_at - item.scheduled_for).total_seconds() > trigger.misfire_grace_seconds
        ]
        current = [item for item in due if item not in missed]
        if constraint is not None:
            explanation = constraint
        elif trigger.misfire_policy == "CATCH_UP":
            selected = due
            action = ScheduleAction.FIRED
            explanation = f"catch-up launched {len(selected)} occurrence(s)"
        elif trigger.misfire_policy == "COALESCE" and missed:
            selected = [due[-1]]
            metadata = {
                "misfirePolicy": "COALESCE",
                "coalescedFrom": due[0].scheduled_for.isoformat(),
                "coalescedThrough": due[-1].scheduled_for.isoformat(),
                "coalescedCount": len(due),
            }
            action = ScheduleAction.COALESCED
            explanation = f"coalesced {len(due)} due occurrences into one launch"
        elif trigger.misfire_policy == "BACKFILL" and missed:
            selected = current
            action = ScheduleAction.BACKFILL_REQUIRED
            explanation = (
                f"{len(missed)} missed occurrence(s) require a backfill; "
                f"{len(current)} current occurrence(s) launched"
            )
        else:
            selected = current
            action = ScheduleAction.FIRED if selected else ScheduleAction.SKIPPED
            explanation = (
                f"launched {len(selected)} current occurrence(s); skipped {len(missed)} misfire(s)"
            )

        executions: list[PersistedExecution] = []
        for occurrence in selected:
            execution = await self.fire_occurrence(
                flow,
                trigger_id=trigger.id,
                scheduled_for=occurrence.scheduled_for,
                tenant_id=tenant_id,
                occurrence_metadata=metadata,
            )
            if execution is not None:
                executions.append(execution)
        completed = await self._scheduler_repository.complete_schedule(
            tenant_id=tenant_id,
            trigger_definition_id=state.trigger_definition_id,
            owner_id=self._owner_id,
            fencing_token=state.fencing_token,
            evaluated_at=evaluated_at,
            next_fire_at=next_fire,
            last_occurrence_at=selected[-1].scheduled_for if selected else None,
            decision=explanation,
            missed_count=len(missed),
        )
        return ScheduleEvaluation(
            trigger_id=trigger.id,
            action=action,
            explanation=explanation,
            due_occurrences=tuple(due),
            executions=tuple(executions),
            state=completed,
        )

    def _constraint_reason(
        self,
        flow: FlowDefinition,
        trigger: TriggerDefinition,
        scheduled_for: datetime,
    ) -> str | None:
        reason = _constraint_reason(flow, trigger, scheduled_for)
        if reason is not None or trigger.condition is None:
            return reason
        context = ExpressionContext(
            flow={"id": flow.id, "namespace": flow.namespace, "revision": flow.revision},
            trigger={
                "id": trigger.id,
                "type": trigger.type,
                "date": scheduled_for,
                "timezone": trigger.timezone,
            },
            variables=flow.variables,
            labels=flow.labels,
            namespace={"id": flow.namespace},
        )
        if not self._expressions.evaluate_condition(trigger.condition, context):
            return f"trigger {trigger.id!r} condition evaluated false"
        return None


def _find_trigger(flow: FlowDefinition, trigger_id: str) -> TriggerDefinition:
    trigger = next((candidate for candidate in flow.triggers if candidate.id == trigger_id), None)
    if trigger is None:
        raise LookupError(f"trigger {trigger_id!r} does not exist")
    _require_schedule_trigger(trigger)
    return trigger


def _require_schedule_trigger(trigger: TriggerDefinition) -> None:
    if trigger.type not in {"core.cron", "core.interval"}:
        raise ValueError(f"trigger {trigger.id!r} is not a temporal schedule")


def _constraint_reason(
    flow: FlowDefinition | None,
    trigger: TriggerDefinition,
    scheduled_for: datetime,
) -> str | None:
    if flow is not None and flow.disabled:
        return f"flow {flow.namespace}.{flow.id} is disabled"
    if trigger.disabled:
        return f"trigger {trigger.id!r} is disabled"
    if trigger.paused:
        return f"trigger {trigger.id!r} is paused"
    scheduled_utc = scheduled_for.astimezone(UTC)
    if trigger.start_at is not None and scheduled_utc < trigger.start_at.astimezone(UTC):
        return f"trigger {trigger.id!r} has not reached its start"
    if trigger.end_at is not None and scheduled_utc > trigger.end_at.astimezone(UTC):
        return f"trigger {trigger.id!r} is past its end"
    return None


def _initial_next_fire(trigger: TriggerDefinition, evaluated_at: datetime) -> datetime | None:
    baseline = evaluated_at - timedelta(minutes=1)
    if trigger.type == "core.interval":
        baseline = evaluated_at - timedelta(microseconds=1)
    if trigger.start_at is not None:
        baseline = max(baseline, trigger.start_at.astimezone(UTC) - timedelta(microseconds=1))
    candidate = _next_schedule_instant(trigger, baseline)
    if trigger.end_at is not None and candidate > trigger.end_at.astimezone(UTC):
        return None
    return candidate


def _due_occurrences(
    trigger: TriggerDefinition,
    next_fire_at: datetime | None,
    evaluated_at: datetime,
) -> tuple[list[CronOccurrence], datetime | None]:
    due: list[CronOccurrence] = []
    cursor = next_fire_at
    while cursor is not None and cursor <= evaluated_at and len(due) < trigger.max_catch_up:
        due.append(CronOccurrence(trigger_id=trigger.id, scheduled_for=cursor))
        candidate = _next_schedule_instant(trigger, cursor)
        cursor = (
            None
            if trigger.end_at is not None and candidate > trigger.end_at.astimezone(UTC)
            else candidate
        )
    return due, cursor


def _next_schedule_instant(trigger: TriggerDefinition, after: datetime) -> datetime:
    _require_schedule_trigger(trigger)
    after_utc = _require_aware(after).astimezone(UTC)
    if trigger.type == "core.interval":
        if trigger.interval is None:
            raise ValueError("core.interval trigger requires interval")
        anchor = (
            trigger.start_at.astimezone(UTC)
            if trigger.start_at is not None
            else datetime(1970, 1, 1, tzinfo=UTC)
        )
        seconds = trigger.interval.total_seconds()
        steps = max(floor((after_utc - anchor).total_seconds() / seconds) + 1, 0)
        return anchor + trigger.interval * steps

    if trigger.cron is None:
        raise ValueError("core.cron trigger requires cron")
    zone = ZoneInfo(trigger.timezone)
    local_cursor = after_utc.astimezone(zone).replace(tzinfo=None)
    iterator = croniter(trigger.cron, local_cursor)
    for _ in range(8):
        wall_time = iterator.get_next(datetime)
        instants = _valid_wall_instants(wall_time, zone)
        if instants:
            return instants[0]
    raise ValueError(f"trigger {trigger.id!r} has no valid occurrence after DST resolution")


def _is_schedule_instant(trigger: TriggerDefinition, scheduled_for: datetime) -> bool:
    scheduled_utc = _require_aware(scheduled_for).astimezone(UTC)
    if trigger.type == "core.interval":
        if trigger.interval is None:
            return False
        anchor = (
            trigger.start_at.astimezone(UTC)
            if trigger.start_at is not None
            else datetime(1970, 1, 1, tzinfo=UTC)
        )
        elapsed = (scheduled_utc - anchor).total_seconds()
        return elapsed >= 0 and elapsed % trigger.interval.total_seconds() == 0
    if trigger.cron is None:
        return False
    zone = ZoneInfo(trigger.timezone)
    wall_time = scheduled_utc.astimezone(zone).replace(tzinfo=None)
    instants = _valid_wall_instants(wall_time, zone)
    return (
        bool(instants) and scheduled_utc == instants[0] and croniter.match(trigger.cron, wall_time)
    )


def _valid_wall_instants(wall_time: datetime, zone: ZoneInfo) -> list[datetime]:
    instants: set[datetime] = set()
    for fold in (0, 1):
        aware = wall_time.replace(tzinfo=zone, fold=fold)
        instant = aware.astimezone(UTC)
        round_trip = instant.astimezone(zone).replace(tzinfo=None)
        if round_trip == wall_time:
            instants.add(instant)
    return sorted(instants)


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("schedule timestamps must include timezone information")
    return value
