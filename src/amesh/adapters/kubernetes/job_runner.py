from __future__ import annotations

import asyncio
import hashlib
import math
from collections.abc import Mapping
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from kubernetes.aio import client, config  # type: ignore[import-untyped]
from kubernetes.aio.client.exceptions import ApiException  # type: ignore[import-untyped]

from amesh.ports import (
    KubernetesJobRunnerExtension,
    RunnerCapabilities,
    RunnerDiagnostics,
    RunnerId,
    RunnerLog,
    RunnerLogStream,
    RunnerMetrics,
    RunnerReconciliationResult,
    RunnerRequest,
    RunnerResult,
    RunnerStatus,
    StaleRunnerAttemptError,
    TaskRunner,
    validate_runner_request,
)

_CAPABILITIES = RunnerCapabilities(
    runner=RunnerId.KUBERNETES,
    acceptsCommand=True,
    requiresCommand=True,
    acceptsImage=True,
    requiresImage=True,
    supportsFiles=False,
    supportsWorkingDirectory=False,
    supportsResources=True,
    supportsSecurityPolicy=True,
    supportsScopedCredentials=True,
    supportsReconciliation=True,
    extensionType=RunnerId.KUBERNETES,
    cancellationEscalation=("delete", "foreground-propagation", "api-retry"),
)


@dataclass
class _ActiveJob:
    name: str
    fencing_token: int
    cancel_requested: bool = False


class KubernetesJobRunner(TaskRunner):
    """Runs one fenced task attempt as one deterministic Kubernetes Job."""

    CAPABILITIES = _CAPABILITIES

    def __init__(
        self,
        *,
        namespace: str,
        api_client: client.ApiClient | None = None,
        poll_interval_seconds: float = 0.25,
        cleanup_finished_jobs: bool = True,
    ) -> None:
        self._namespace = namespace
        self._api_client = api_client or client.ApiClient()
        self._batch = client.BatchV1Api(self._api_client)
        self._core = client.CoreV1Api(self._api_client)
        self._poll_interval_seconds = poll_interval_seconds
        self._cleanup_finished_jobs = cleanup_finished_jobs
        self._active: dict[str, _ActiveJob] = {}
        self._lock = asyncio.Lock()

    @property
    def capabilities(self) -> RunnerCapabilities:
        return self.CAPABILITIES

    @classmethod
    async def from_kube_config(
        cls,
        *,
        namespace: str,
        context: str | None = None,
        poll_interval_seconds: float = 0.25,
        cleanup_finished_jobs: bool = True,
    ) -> KubernetesJobRunner:
        await config.load_kube_config(context=context)
        return cls(
            namespace=namespace,
            poll_interval_seconds=poll_interval_seconds,
            cleanup_finished_jobs=cleanup_finished_jobs,
        )

    @classmethod
    def from_in_cluster(
        cls,
        *,
        namespace: str,
        poll_interval_seconds: float = 0.25,
        cleanup_finished_jobs: bool = True,
    ) -> KubernetesJobRunner:
        config.load_incluster_config()
        return cls(
            namespace=namespace,
            poll_interval_seconds=poll_interval_seconds,
            cleanup_finished_jobs=cleanup_finished_jobs,
        )

    async def run(self, request: RunnerRequest) -> RunnerResult:
        validate_runner_request(self.capabilities, request)
        started_at = perf_counter()

        active = _ActiveJob(
            name=_job_name(request.attempt_id),
            fencing_token=request.fencing_token,
        )
        async with self._lock:
            if request.attempt_id in self._active:
                raise RuntimeError(f"attempt {request.attempt_id!r} is already running")
            self._active[request.attempt_id] = active

        try:
            while True:
                try:
                    await self._create_or_reconcile_job(active.name, request)
                    result = await self._wait_for_result(active, request)
                    return result.model_copy(
                        update={
                            "metrics": RunnerMetrics(duration_seconds=perf_counter() - started_at)
                        }
                    )
                except ApiException as exc:
                    if exc.status != 401:
                        raise
                    await asyncio.sleep(self._poll_interval_seconds)
        finally:
            if self._cleanup_finished_jobs:
                await self._delete_job(active.name)
            async with self._lock:
                current = self._active.get(request.attempt_id)
                if current is active:
                    del self._active[request.attempt_id]

    async def cancel(self, attempt_id: str, fencing_token: int) -> None:
        async with self._lock:
            active = self._active.get(attempt_id)
            if active is None or active.fencing_token != fencing_token:
                raise StaleRunnerAttemptError(
                    f"attempt {attempt_id!r} is inactive or fenced by a newer token"
                )
            active.cancel_requested = True
        await self._delete_job(active.name)

    async def reconcile(
        self,
        active_attempts: Mapping[str, int],
    ) -> RunnerReconciliationResult:
        jobs = await self._batch.list_namespaced_job(
            self._namespace,
            label_selector="app.kubernetes.io/name=amesh-task",
        )
        cleaned: list[str] = []
        retained: list[str] = []
        for job in jobs.items or []:
            labels = job.metadata.labels or {}
            attempt_id = labels.get("amesh.io/attempt")
            fence = labels.get("amesh.io/fence")
            if attempt_id is None or fence is None:
                continue
            if active_attempts.get(attempt_id) == int(fence):
                retained.append(attempt_id)
                continue
            await self._delete_job(str(job.metadata.name))
            cleaned.append(attempt_id)
        return RunnerReconciliationResult(
            runner=RunnerId.KUBERNETES,
            cleanedAttempts=tuple(sorted(cleaned)),
            retainedAttempts=tuple(sorted(retained)),
        )

    async def close(self) -> None:
        await self._api_client.close()

    async def _create_or_reconcile_job(
        self,
        name: str,
        request: RunnerRequest,
    ) -> None:
        body = _job_body(name, request)
        try:
            await self._batch.create_namespaced_job(self._namespace, body)
        except ApiException as exc:
            if exc.status != 409:
                raise
            existing = await self._batch.read_namespaced_job(name, self._namespace)
            labels = existing.metadata.labels or {}
            if labels.get("amesh.io/attempt") != request.attempt_id or labels.get(
                "amesh.io/fence"
            ) != str(request.fencing_token):
                raise RuntimeError(f"existing Job {name!r} belongs to another attempt") from exc

    async def _wait_for_result(
        self,
        active: _ActiveJob,
        request: RunnerRequest,
    ) -> RunnerResult:
        while True:
            if active.cancel_requested:
                return RunnerResult(
                    runner=RunnerId.KUBERNETES,
                    exit_code=None,
                    status=RunnerStatus.CANCELLED,
                    diagnostics=RunnerDiagnostics(
                        runner=RunnerId.KUBERNETES,
                        externalId=active.name,
                    ),
                )
            try:
                job = await self._batch.read_namespaced_job(active.name, self._namespace)
            except ApiException as exc:
                if exc.status == 404 and active.cancel_requested:
                    continue
                raise

            if job.status.succeeded:
                return await self._pod_result(active.name, RunnerStatus.SUCCESS)
            failure = _job_failure(job)
            if failure is not None:
                reason, message = failure
                status = (
                    RunnerStatus.TIMED_OUT if reason == "DeadlineExceeded" else RunnerStatus.FAILED
                )
                return await self._pod_result(
                    active.name,
                    status,
                    reason=reason,
                    message=message,
                )
            await asyncio.sleep(self._poll_interval_seconds)

    async def _pod_result(
        self,
        job_name: str,
        status: RunnerStatus,
        *,
        reason: str | None = None,
        message: str | None = None,
    ) -> RunnerResult:
        pod_list = await self._core.list_namespaced_pod(
            self._namespace,
            label_selector=f"job-name={job_name}",
        )
        pods = list(pod_list.items or [])
        pods.sort(key=lambda pod: pod.metadata.creation_timestamp)
        pod = next(
            (candidate for candidate in reversed(pods) if candidate.status.phase == "Succeeded"),
            pods[-1] if pods else None,
        )
        if pod is None:
            return RunnerResult(
                runner=RunnerId.KUBERNETES,
                exit_code=None,
                status=status,
                diagnostics=RunnerDiagnostics(
                    runner=RunnerId.KUBERNETES,
                    externalId=job_name,
                    reason=reason,
                    message=message,
                ),
            )

        pod_name = str(pod.metadata.name)
        log = await self._core.read_namespaced_pod_log(
            pod_name,
            self._namespace,
            container="task",
        )
        exit_code = _pod_exit_code(pod)
        return RunnerResult(
            runner=RunnerId.KUBERNETES,
            exit_code=exit_code,
            status=status,
            logs=(RunnerLog(sequence=0, stream=RunnerLogStream.STDOUT, message=log),),
            outputs={"stdout": log, "stderr": ""},
            diagnostics=RunnerDiagnostics(
                runner=RunnerId.KUBERNETES,
                externalId=job_name,
                reason=reason,
                message=message,
                details={"podName": pod_name},
            ),
        )

    async def _delete_job(self, name: str) -> None:
        try:
            await self._batch.delete_namespaced_job(
                name,
                self._namespace,
                body=client.V1DeleteOptions(propagation_policy="Foreground"),
            )
        except ApiException as exc:
            if exc.status not in {401, 404}:
                raise


def _job_name(attempt_id: str) -> str:
    digest = hashlib.sha256(attempt_id.encode("utf-8")).hexdigest()[:32]
    return f"amesh-{digest}"


def _job_body(name: str, request: RunnerRequest) -> dict[str, Any]:
    extension = (
        request.extension
        if isinstance(request.extension, KubernetesJobRunnerExtension)
        else KubernetesJobRunnerExtension(type=RunnerId.KUBERNETES)
    )
    labels = {
        "app.kubernetes.io/name": "amesh-task",
        "amesh.io/attempt": request.attempt_id,
        "amesh.io/fence": str(request.fencing_token),
        **extension.labels,
    }
    environment = dict(request.environment)
    environment.update(
        {
            credential.environment_variable: credential.value.get_secret_value()
            for credential in request.credentials
        }
    )
    container: dict[str, Any] = {
        "name": "task",
        "image": request.image,
        "command": request.command,
        "env": [{"name": key, "value": value} for key, value in sorted(environment.items())],
        "resources": {
            "requests": request.resource_limits,
            "limits": request.resource_limits,
        },
    }
    container["securityContext"] = {
        "privileged": request.security_policy.privileged,
        "readOnlyRootFilesystem": request.security_policy.read_only_root_filesystem,
        "allowPrivilegeEscalation": not request.security_policy.no_new_privileges,
        "capabilities": {
            "add": list(request.security_policy.capability_add),
            "drop": list(request.security_policy.capability_drop),
        },
        **(
            {"runAsUser": request.security_policy.run_as_user}
            if request.security_policy.run_as_user is not None
            else {}
        ),
    }
    pod_spec: dict[str, Any] = {
        "restartPolicy": "Never",
        "terminationGracePeriodSeconds": math.ceil(request.cancel_grace_seconds),
        "containers": [container],
    }
    if extension.service_account_name is not None:
        pod_spec["serviceAccountName"] = extension.service_account_name
    if extension.node_selector:
        pod_spec["nodeSelector"] = extension.node_selector
    job_spec: dict[str, Any] = {
        "backoffLimit": 1,
        "template": {
            "metadata": {"labels": labels},
            "spec": pod_spec,
        },
    }
    if request.timeout_seconds is not None:
        job_spec["activeDeadlineSeconds"] = math.ceil(request.timeout_seconds)
    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": name, "labels": labels},
        "spec": job_spec,
    }


def _job_failure(job: Any) -> tuple[str | None, str | None] | None:
    for condition in job.status.conditions or []:
        if condition.type == "Failed" and condition.status == "True":
            return condition.reason, condition.message
    return None


def _pod_exit_code(pod: Any) -> int | None:
    for container_status in pod.status.container_statuses or []:
        terminated = container_status.state.terminated
        if terminated is not None:
            return int(terminated.exit_code)
    return None
