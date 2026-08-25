"""Durable application service for provider-neutral differential execution."""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy

from .differential import (
    Comparator,
    ComparisonReport,
    DifferentialSpec,
    Executor,
    RunObservation,
    ShadowExecutionError,
    ShadowRun,
    ShadowRunContext,
    compare_runs,
)
from .repository import (
    DifferentialState,
    PostgresDifferentialShadowRepository,
)


class DurableDifferentialService:
    """Coordinate shadow execution through durable, restart-safe PostgreSQL records."""

    def __init__(
        self,
        repository: PostgresDifferentialShadowRepository,
        *,
        comparators: Sequence[Comparator] = (),
    ) -> None:
        self._repository = repository
        self._comparators = tuple(comparators)

    async def run(
        self,
        spec: DifferentialSpec,
        executor: Executor,
        *,
        actor_id: str,
    ) -> ComparisonReport:
        record = await self._repository.create_or_get(spec, actor_id=actor_id)
        if record.state is DifferentialState.SUCCEEDED:
            if record.report is None:
                raise RuntimeError("completed differential has no report")
            return record.report

        left = await self._run_side(spec, "left", executor)
        right = await self._run_side(spec, "right", executor)
        report = compare_runs(spec, left, right, comparators=self._comparators)
        completed = await self._repository.complete(spec.tenant_id, spec.spec_id, report)
        if completed.report is None:
            raise RuntimeError("completed differential has no report")
        return completed.report

    async def get(
        self,
        tenant_id: str,
        namespace: str,
        idempotency_key: str,
    ) -> ComparisonReport:
        record = await self._repository.get(tenant_id, namespace, idempotency_key)
        if record.report is None:
            raise LookupError("differential report unavailable")
        return record.report

    async def _run_side(
        self,
        spec: DifferentialSpec,
        side: str,
        executor: Executor,
    ) -> ShadowRun:
        run = await self._repository.claim_side(spec.tenant_id, spec.spec_id, side)
        if run.state is DifferentialState.SUCCEEDED:
            return run.shadow_run()

        context = ShadowRunContext(spec)
        configuration = spec.left if side == "left" else spec.right
        try:
            observation = executor(configuration, deepcopy(spec.inputs), context)
            observation = self._validated_observation(side, observation, context)
        except Exception as exc:
            await self._repository.record_failure(
                spec.tenant_id,
                run.run_id,
                f"{type(exc).__name__}: {exc}"[:4096],
            )
            raise
        accepted = await self._repository.record_observation(
            spec.tenant_id,
            run.run_id,
            observation,
        )
        return accepted.shadow_run()

    @staticmethod
    def _validated_observation(
        side: str,
        observation: RunObservation,
        context: ShadowRunContext,
    ) -> RunObservation:
        effects = tuple(context.effects)
        if observation.effects and observation.effects != effects:
            raise ShadowExecutionError(
                f"{side} adapter reported an effect outside the shadow context"
            )
        return observation.model_copy(update={"effects": effects})
