from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid5

from amesh.domain import (
    BackfillPreview,
    BackfillRecord,
    BackfillResourcePin,
    BackfillSelectionKind,
    BackfillSpec,
    BackfillState,
    OperationalBoundary,
    canonical_hash,
    frozen_input_digest,
)
from amesh.ports import (
    BackfillItemDefinition,
    BackfillRepository,
    ExecutionLaunchSource,
    ExecutionRepository,
    OperationalControlEvaluator,
    TenantQuotaExceeded,
)


class BackfillService:
    """Plans and pumps deterministic historical executions through the normal engine."""

    def __init__(
        self,
        execution_repository: ExecutionRepository,
        backfill_repository: BackfillRepository,
        operational_controls: OperationalControlEvaluator | None = None,
    ) -> None:
        self._executions = execution_repository
        self._backfills = backfill_repository
        self._operational_controls = operational_controls

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
            replaySources=spec.replay_sources,
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
        if await self._launch_blocked(
            tenant_id=tenant_id,
            namespace=spec.namespace,
            flow_id=spec.flow_id,
        ):
            raise ValueError("new backfill executions are blocked by operational control")
        flow = await self._executions.get_flow(
            spec.namespace,
            spec.flow_id,
            tenant_id=tenant_id,
            revision=spec.flow_revision,
        )
        items = await self._item_definitions(spec, tenant_id=tenant_id)
        backfill_id = (
            _replay_backfill_id(spec, tenant_id=tenant_id)
            if spec.selection.kind is BackfillSelectionKind.REPLAY
            else None
        )
        backfill = await self._backfills.create_backfill(
            spec,
            items,
            tenant_id=tenant_id,
            actor_id=actor_id,
            task_count=len(flow.tasks),
            backfill_id=backfill_id,
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
        if await self._launch_blocked(
            tenant_id=tenant_id,
            namespace=backfill.namespace,
            flow_id=backfill.flow_id,
        ):
            return await self._backfills.refresh_backfill(backfill_id, tenant_id=tenant_id)
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
                inputs = dict(source.inputs)
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
                "replaySource": (
                    next(
                        (
                            attestation.model_dump(mode="json", by_alias=True)
                            for attestation in backfill.replay_sources
                            if attestation.source_execution_id == item.source_execution_id
                        ),
                        None,
                    )
                    if item.source_execution_id is not None
                    else None
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
                attestation = next(
                    (
                        item
                        for item in spec.replay_sources
                        if item.source_execution_id == source_execution_id
                    ),
                    None,
                )
                if attestation is None:
                    raise ValueError(
                        f"replay source {source_execution_id} has no frozen source attestation"
                    )
                if attestation.frozen_input_digest != frozen_input_digest(source.inputs):
                    raise ValueError(
                        f"replay source {source_execution_id} inputs changed after attestation"
                    )
                if attestation.resource_pins != _resource_pins(source):
                    raise ValueError(
                        f"replay source {source_execution_id} resource pins do not match source"
                    )
            items.append(
                BackfillItemDefinition(
                    occurrence_key=key,
                    scheduled_for=scheduled_for,
                    partition_key=partition_key,
                    source_execution_id=source_execution_id,
                )
            )
        return tuple(items)

    async def _launch_blocked(
        self,
        *,
        tenant_id: str,
        namespace: str,
        flow_id: str,
    ) -> bool:
        if self._operational_controls is None:
            return False
        decision = await self._operational_controls.evaluate(
            OperationalBoundary.NEW_EXECUTIONS,
            tenant_id=tenant_id,
            namespace=namespace,
            flow_id=flow_id,
            component_id="scheduler:backfill",
            component_role="SCHEDULER",
        )
        return decision.blocked


def _replay_backfill_id(spec: BackfillSpec, *, tenant_id: str) -> UUID:
    identity = {
        "tenantId": tenant_id,
        "namespace": spec.namespace,
        "flowId": spec.flow_id,
        "flowRevision": spec.flow_revision,
        "sourceExecutionIds": sorted(str(value) for value in spec.selection.source_execution_ids),
        "idempotencyKey": spec.idempotency_key,
        "replaySources": sorted(
            (item.model_dump(mode="json", by_alias=True) for item in spec.replay_sources),
            key=lambda item: item["sourceExecutionId"],
        ),
    }
    return uuid5(NAMESPACE_URL, f"amesh:replay:{canonical_hash(identity)}")


def _resource_pins(source: object) -> tuple[BackfillResourcePin, ...]:
    trigger = getattr(source, "trigger", None)
    envelope = trigger.get("_ameshDeterminism") if isinstance(trigger, Mapping) else None
    if not isinstance(envelope, Mapping):
        raise ValueError("replay source has no exact determinism envelope")
    revision = envelope.get("revision")
    semantic_hash = envelope.get("semanticHash")
    plugin_set_hash = envelope.get("pluginSetHash")
    envelope_digest = envelope.get("envelopeDigest")
    if not isinstance(revision, int) or not isinstance(semantic_hash, str):
        raise ValueError("replay source has an invalid flow revision pin")
    if not isinstance(plugin_set_hash, str) or not isinstance(envelope_digest, str):
        raise ValueError("replay source has no exact plugin-set or envelope pin")
    if revision != getattr(source, "flow_revision", None):
        raise ValueError("replay source determinism revision does not match its execution")
    pins = [
        BackfillResourcePin(key="flow", revision=revision, digest=semantic_hash),
        BackfillResourcePin(key="plugin-set", revision=revision, digest=plugin_set_hash),
        BackfillResourcePin(key="determinism-envelope", revision=revision, digest=envelope_digest),
    ]
    raw_policy_pins = envelope.get("policyPins", ())
    if not isinstance(raw_policy_pins, (list, tuple)):
        raise ValueError("replay source has invalid policy pins")
    for raw_pin in raw_policy_pins:
        if not isinstance(raw_pin, Mapping):
            raise ValueError("replay source has invalid policy pin")
        category = raw_pin.get("category")
        key = raw_pin.get("key")
        pin_revision = raw_pin.get("revision")
        digest = raw_pin.get("digest")
        if (
            not isinstance(category, str)
            or not isinstance(key, str)
            or not isinstance(pin_revision, int)
            or not isinstance(digest, str)
        ):
            raise ValueError("replay source has invalid policy pin")
        pins.append(
            BackfillResourcePin(
                key=f"{category}:{key}",
                revision=pin_revision,
                digest=digest,
            )
        )
    return tuple(pins)
