from __future__ import annotations

from amesh.dsl.models import TriggerDefinition
from amesh.ports import (
    PollingTriggerAdapter,
    RealtimeTriggerAdapter,
    TriggerOccurrenceAcceptance,
    TriggerRuntimeRepository,
    TriggerRuntimeState,
)


class TriggerRuntimeService:
    """Coordinates plugin adapters with durable occurrence and checkpoint commits."""

    def __init__(self, repository: TriggerRuntimeRepository) -> None:
        self._repository = repository

    async def poll_once(
        self,
        state: TriggerRuntimeState,
        definition: TriggerDefinition,
        adapter: PollingTriggerAdapter,
        *,
        limit: int = 100,
    ) -> list[TriggerOccurrenceAcceptance]:
        if definition.type not in adapter.trigger_types:
            raise ValueError(f"adapter does not support trigger type {definition.type!r}")
        result = await adapter.poll(
            definition.model_dump(mode="json", by_alias=True, exclude_none=True),
            checkpoint=state.checkpoint,
            cursor=state.cursor,
            limit=min(max(limit, 1), definition.max_pending),
        )
        accepted: list[TriggerOccurrenceAcceptance] = []
        for candidate in result.occurrences:
            accepted.append(
                await self._repository.accept_occurrence(
                    tenant_id=state.tenant_id,
                    namespace=state.namespace,
                    flow_id=state.flow_id,
                    flow_revision=state.flow_revision,
                    trigger_id=state.trigger_id,
                    occurrence_key=candidate.occurrence_key,
                    payload=candidate.payload,
                    metadata={
                        **candidate.metadata,
                        "source": "polling-adapter",
                        "observedAt": candidate.observed_at.isoformat(),
                    },
                    max_pending=definition.max_pending,
                    max_attempts=definition.max_attempts,
                    retry_delay=definition.retry_delay,
                )
            )
        evaluated_at = max(
            (candidate.observed_at for candidate in result.occurrences),
            default=state.updated_at,
        )
        await self._repository.update_checkpoint(
            tenant_id=state.tenant_id,
            trigger_definition_id=state.trigger_definition_id,
            checkpoint=result.checkpoint,
            cursor=result.cursor,
            evaluated_at=evaluated_at,
            next_evaluation_at=result.next_evaluation_at,
            decision=f"persisted {len(accepted)} polling occurrence(s) and checkpoint",
        )
        await adapter.acknowledge(checkpoint=result.checkpoint, cursor=result.cursor)
        return accepted

    async def consume_realtime(
        self,
        state: TriggerRuntimeState,
        definition: TriggerDefinition,
        adapter: RealtimeTriggerAdapter,
        *,
        limit: int | None = None,
    ) -> list[TriggerOccurrenceAcceptance]:
        if definition.type not in adapter.trigger_types:
            raise ValueError(f"adapter does not support trigger type {definition.type!r}")
        accepted: list[TriggerOccurrenceAcceptance] = []
        bound = min(limit or definition.max_pending, definition.max_pending)
        async for candidate in adapter.subscribe(
            definition.model_dump(mode="json", by_alias=True, exclude_none=True),
            checkpoint=state.checkpoint,
            cursor=state.cursor,
        ):
            result = await self._repository.accept_occurrence(
                tenant_id=state.tenant_id,
                namespace=state.namespace,
                flow_id=state.flow_id,
                flow_revision=state.flow_revision,
                trigger_id=state.trigger_id,
                occurrence_key=candidate.occurrence_key,
                payload=candidate.payload,
                metadata={
                    **candidate.metadata,
                    "source": "realtime-adapter",
                    "observedAt": candidate.observed_at.isoformat(),
                },
                max_pending=definition.max_pending,
                max_attempts=definition.max_attempts,
                retry_delay=definition.retry_delay,
            )
            accepted.append(result)
            await adapter.acknowledge(candidate.occurrence_key)
            if len(accepted) >= bound:
                break
        return accepted
