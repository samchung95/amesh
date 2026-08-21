from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from croniter import croniter

from amesh.dsl import FlowDefinition
from amesh.dsl.models import TriggerDefinition
from amesh.ports import ExecutionLaunchSource, ExecutionRepository, PersistedExecution


@dataclass(frozen=True)
class CronOccurrence:
    trigger_id: str
    scheduled_for: datetime


class CronScheduler:
    """Calculates cron times while PostgreSQL execution idempotency owns uniqueness."""

    def __init__(self, repository: ExecutionRepository) -> None:
        self._repository = repository

    def next_occurrence(
        self,
        trigger: TriggerDefinition,
        *,
        after: datetime,
    ) -> CronOccurrence:
        cron_expression = _require_cron_trigger(trigger)
        localized_after = _require_aware(after).astimezone(ZoneInfo(trigger.timezone))
        scheduled_for = croniter(cron_expression, localized_after).get_next(datetime)
        return CronOccurrence(
            trigger_id=trigger.id,
            scheduled_for=scheduled_for.astimezone(UTC),
        )

    async def fire_occurrence(
        self,
        flow: FlowDefinition,
        *,
        trigger_id: str,
        scheduled_for: datetime,
        tenant_id: str,
        inputs: dict[str, object] | None = None,
    ) -> PersistedExecution:
        trigger = next(
            (
                candidate
                for candidate in flow.triggers
                if candidate.id == trigger_id and not candidate.disabled
            ),
            None,
        )
        if trigger is None:
            raise LookupError(f"enabled trigger {trigger_id!r} does not exist")
        cron_expression = _require_cron_trigger(trigger)
        scheduled_utc = _require_aware(scheduled_for).astimezone(UTC).replace(microsecond=0)
        scheduled_local = scheduled_utc.astimezone(ZoneInfo(trigger.timezone))
        if not croniter.match(cron_expression, scheduled_local):
            raise ValueError(
                f"{scheduled_utc.isoformat()} is not an occurrence of trigger {trigger.id!r}"
            )
        occurrence_key = (
            f"cron:{flow.namespace}:{flow.id}:{flow.revision}:"
            f"{trigger.id}:{scheduled_utc.isoformat()}"
        )
        return await self._repository.create_execution(
            flow,
            tenant_id=tenant_id,
            inputs=inputs or {},
            trigger={
                "id": trigger.id,
                "type": trigger.type,
                "date": scheduled_utc.isoformat(),
                "timezone": trigger.timezone,
            },
            launch_source=ExecutionLaunchSource.SCHEDULED,
            idempotency_key=occurrence_key,
        )

    async def fire_due_occurrences(
        self,
        flow: FlowDefinition,
        *,
        at: datetime,
        tenant_id: str,
    ) -> list[PersistedExecution]:
        scheduled_for = _require_aware(at).astimezone(UTC).replace(second=0, microsecond=0)
        executions: list[PersistedExecution] = []
        for trigger in flow.triggers:
            if trigger.disabled or trigger.type != "core.cron":
                continue
            cron_expression = _require_cron_trigger(trigger)
            scheduled_local = scheduled_for.astimezone(ZoneInfo(trigger.timezone))
            if croniter.match(cron_expression, scheduled_local):
                executions.append(
                    await self.fire_occurrence(
                        flow,
                        trigger_id=trigger.id,
                        scheduled_for=scheduled_for,
                        tenant_id=tenant_id,
                    )
                )
        return executions


def _require_cron_trigger(trigger: TriggerDefinition) -> str:
    if trigger.type != "core.cron" or trigger.cron is None:
        raise ValueError(f"trigger {trigger.id!r} is not a core.cron trigger")
    return trigger.cron


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("cron timestamps must include timezone information")
    return value
