from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from amesh.domain import (
    BackfillPreview,
    BackfillRecord,
    BackfillSelectionKind,
    BackfillSpec,
    BackfillState,
    canonical_hash,
)
from amesh.ports import (
    BackfillItemDefinition,
    BackfillRepository,
    ExecutionLaunchSource,
    ExecutionRepository,
    TenantQuotaExceeded,
)


class BackfillService:
    """Plans and pumps deterministic historical executions through the normal engine."""

    def __init__(
        self,
        execution_repository: ExecutionRepository,
        backfill_repository: BackfillRepository,
    ) -> None:
        self._executions = execution_repository
        self._backfills = backfill_repository

    async def preview(self, spec: BackfillSpec, *, tenant_id: str) -> BackfillPreview:
        flow = await self._executions.get_flow(
            spec.namespace,
            spec.flow_id,
            tenant_id=tenant_id,
            revision=spec.flow_revision,
        )
        items = await self._item_definitions(spec, tenant_id=tenant_id)
        fingerprint = canonical_hash(
            {
                "tenantId": tenant_id,
                "namespace": spec.namespace,
                "flowId": spec.flow_id,
                "flowRevision": spec.flow_revision,
                "selection": spec.selection.model_dump(mode="json", by_alias=True),
            }
        )[:16]
        count = len(items)
        return BackfillPreview(
            selectionKind=spec.selection.kind,
            executionCount=count,
            estimatedTaskRuns=count * len(flow.tasks),
            estimatedCostUnits=count * len(flow.tasks),
            idempotencyKeyTemplate=f"backfill:{fingerprint}:{{occurrenceKey}}",
            warnings=(
                "Preview is a dry run and creates no executions.",
                "Tasks with external effects should use occurrence-scoped idempotency keys.",
                "Submission pins the selected flow revision and uses normal admission limits.",
            ),
        )

    async def create(
        self,
        spec: BackfillSpec,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> BackfillRecord:
        flow = await self._executions.get_flow(
            spec.namespace,
            spec.flow_id,
            tenant_id=tenant_id,
            revision=spec.flow_revision,
        )
        items = await self._item_definitions(spec, tenant_id=tenant_id)
        backfill = await self._backfills.create_backfill(
            spec,
            items,
            tenant_id=tenant_id,
            actor_id=actor_id,
            task_count=len(flow.tasks),
        )
        return await self.pump(backfill.backfill_id, tenant_id=tenant_id)

    async def pump(self, backfill_id: UUID, *, tenant_id: str) -> BackfillRecord:
        backfill = await self._backfills.get_backfill(backfill_id, tenant_id=tenant_id)
        if backfill.state is not BackfillState.RUNNING:
            return backfill
        capacity = min(
            await self._backfills.launch_capacity(backfill_id, tenant_id=tenant_id),
            100,
        )
        if capacity == 0:
            return await self._backfills.refresh_backfill(backfill_id, tenant_id=tenant_id)
        flow = await self._executions.get_flow(
            backfill.namespace,
            backfill.flow_id,
            tenant_id=tenant_id,
            revision=backfill.flow_revision,
        )
        for item in await self._backfills.list_pending_items(
            backfill_id,
            tenant_id=tenant_id,
            limit=capacity,
        ):
            inputs = dict(backfill.inputs)
            labels = dict(backfill.labels)
            if item.source_execution_id is not None:
                source = await self._executions.get_execution(
                    item.source_execution_id,
                    tenant_id=tenant_id,
                )
                inputs = {**source.inputs, **inputs}
                labels = {**source.labels, **labels}
            labels.update(
                {
                    "amesh.backfill.id": str(backfill_id),
                    "amesh.backfill.item": str(item.item_id),
                }
            )
            trigger = {
                "backfillId": str(backfill_id),
                "backfillItemId": str(item.item_id),
                "occurrenceKey": item.occurrence_key,
                "scheduledFor": (
                    item.scheduled_for.astimezone(UTC).isoformat()
                    if item.scheduled_for is not None
                    else None
                ),
                "partition": item.partition_key,
                "sourceExecutionId": (
                    str(item.source_execution_id) if item.source_execution_id is not None else None
                ),
            }
            try:
                execution = await self._executions.create_execution(
                    flow,
                    tenant_id=tenant_id,
                    inputs=inputs,
                    trigger=trigger,
                    launch_source=(
                        ExecutionLaunchSource.REPLAY
                        if backfill.selection_kind is BackfillSelectionKind.REPLAY
                        else ExecutionLaunchSource.BACKFILL
                    ),
                    idempotency_key=f"backfill:{backfill_id}:{item.occurrence_key}",
                    actor_id="system:backfill-worker",
                    labels=labels,
                    priority=backfill.priority,
                )
            except TenantQuotaExceeded:
                break
            await self._backfills.link_execution(
                backfill_id,
                item.item_id,
                execution.execution_id,
                tenant_id=tenant_id,
            )
        return await self._backfills.refresh_backfill(backfill_id, tenant_id=tenant_id)

    async def process_active(self, *, tenant_id: str, limit: int = 100) -> int:
        processed = 0
        for backfill in await self._backfills.list_backfills(
            tenant_id=tenant_id,
            limit=limit,
        ):
            if backfill.state is BackfillState.RUNNING:
                await self.pump(backfill.backfill_id, tenant_id=tenant_id)
                processed += 1
        return processed

    async def _item_definitions(
        self, spec: BackfillSpec, *, tenant_id: str
    ) -> tuple[BackfillItemDefinition, ...]:
        keys = spec.selection.item_keys()
        items: list[BackfillItemDefinition] = []
        for key in keys:
            scheduled_for: datetime | None = None
            partition_key: str | None = None
            source_execution_id: UUID | None = None
            if key.startswith("time:"):
                scheduled_for = datetime.fromisoformat(key.removeprefix("time:"))
            elif key.startswith("occurrence:"):
                scheduled_for = datetime.fromisoformat(key.removeprefix("occurrence:"))
            elif key.startswith("partition:"):
                partition_key = key.removeprefix("partition:")
            elif key.startswith("replay:"):
                source_execution_id = UUID(key.removeprefix("replay:"))
                source = await self._executions.get_execution(
                    source_execution_id,
                    tenant_id=tenant_id,
                )
                if (
                    source.namespace != spec.namespace
                    or source.flow_id != spec.flow_id
                    or source.flow_revision != spec.flow_revision
                ):
                    raise ValueError("all replay sources must match the selected flow and revision")
            items.append(
                BackfillItemDefinition(
                    occurrence_key=key,
                    scheduled_for=scheduled_for,
                    partition_key=partition_key,
                    source_execution_id=source_execution_id,
                )
            )
        return tuple(items)
