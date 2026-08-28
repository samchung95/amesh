from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping

from amesh.ports import (
    KubernetesRunnerProfile,
    KubernetesRunnerProfileSet,
    RunnerCapabilities,
    RunnerId,
    RunnerReconciliationResult,
    RunnerRequest,
    RunnerResult,
    StaleRunnerAttemptError,
    TaskRunner,
)

from .job_runner import KubernetesJobRunner

KubernetesRunnerFactory = Callable[[KubernetesRunnerProfile], Awaitable[KubernetesJobRunner]]


class ProfiledKubernetesJobRunner(TaskRunner):
    """Routes task requests to operator-owned Kubernetes cluster profiles."""

    def __init__(
        self,
        profiles: tuple[KubernetesRunnerProfile, ...],
        *,
        runner_factory: KubernetesRunnerFactory | None = None,
    ) -> None:
        self._profiles = KubernetesRunnerProfileSet(profiles)
        self._runner_factory = runner_factory or self._default_runner_factory
        self._runners: dict[str, KubernetesJobRunner] = {}
        self._attempt_profiles: dict[str, tuple[str, int]] = {}
        self._lock = asyncio.Lock()

    @property
    def capabilities(self) -> RunnerCapabilities:
        return KubernetesJobRunner.CAPABILITIES

    async def run(self, request: RunnerRequest) -> RunnerResult:
        profile = self._profiles.select(request.namespace, request.worker_group)
        runner = await self._runner(profile)
        async with self._lock:
            current = self._attempt_profiles.get(request.attempt_id)
            if current is not None:
                raise RuntimeError(f"attempt {request.attempt_id!r} is already running")
            self._attempt_profiles[request.attempt_id] = (profile.name, request.fencing_token)
        try:
            return await runner.run(request)
        finally:
            async with self._lock:
                if self._attempt_profiles.get(request.attempt_id) == (
                    profile.name,
                    request.fencing_token,
                ):
                    del self._attempt_profiles[request.attempt_id]

    async def cancel(self, attempt_id: str, fencing_token: int) -> None:
        async with self._lock:
            current = self._attempt_profiles.get(attempt_id)
        if current is None or current[1] != fencing_token:
            raise StaleRunnerAttemptError(
                f"attempt {attempt_id!r} is inactive or fenced by a newer token"
            )
        profile = next(item for item in self._profiles.profiles if item.name == current[0])
        await (await self._runner(profile)).cancel(attempt_id, fencing_token)

    async def reconcile(
        self,
        active_attempts: Mapping[str, int],
    ) -> RunnerReconciliationResult:
        cleaned: set[str] = set()
        retained: set[str] = set()
        for profile in self._profiles.profiles:
            result = await (await self._runner(profile)).reconcile(active_attempts)
            cleaned.update(result.cleaned_attempts)
            retained.update(result.retained_attempts)
        return RunnerReconciliationResult(
            runner=RunnerId.KUBERNETES,
            cleanedAttempts=tuple(sorted(cleaned)),
            retainedAttempts=tuple(sorted(retained)),
        )

    async def close(self) -> None:
        for runner in tuple(self._runners.values()):
            await runner.close()
        self._runners.clear()

    async def _runner(self, profile: KubernetesRunnerProfile) -> KubernetesJobRunner:
        async with self._lock:
            runner = self._runners.get(profile.name)
            if runner is None:
                runner = await self._runner_factory(profile)
                self._runners[profile.name] = runner
            return runner

    @staticmethod
    async def _default_runner_factory(profile: KubernetesRunnerProfile) -> KubernetesJobRunner:
        if profile.context is None:
            return KubernetesJobRunner.from_in_cluster(
                namespace=profile.namespace,
                profile=profile,
            )
        return await KubernetesJobRunner.from_kube_config(
            namespace=profile.namespace,
            context=profile.context,
            profile=profile,
        )
