from __future__ import annotations

import asyncio
import hashlib
import ipaddress
import math
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any

from kubernetes import client as sync_client  # type: ignore[import-untyped]
from kubernetes import config as sync_config
from kubernetes.aio import client, config  # type: ignore[import-untyped]
from kubernetes.aio.client.exceptions import ApiException  # type: ignore[import-untyped]

from amesh.ports import (
    KubernetesJobRunnerExtension,
    KubernetesJobTemplate,
    KubernetesRunnerProfile,
    RunnerCapabilities,
    RunnerDiagnostics,
    RunnerId,
    RunnerLog,
    RunnerLogStream,
    RunnerMetrics,
    RunnerNetworkAccess,
    RunnerPolicyViolation,
    RunnerReconciliationResult,
    RunnerRequest,
    RunnerResult,
    RunnerStatus,
    StaleRunnerAttemptError,
    TaskRunner,
    UnsupportedRunnerRequest,
    validate_runner_request,
)

from .workspace import download_workspace, release_transfer_sidecar, upload_workspace

_FINALIZER = "amesh.io/task-cleanup"
_OWNER_SELECTOR = "app.kubernetes.io/name=amesh-task"
_TRANSIENT_API_STATUSES = {401, 408, 429, 500, 502, 503, 504}
_WORKSPACE = "/workspace"

_CAPABILITIES = RunnerCapabilities(
    runner=RunnerId.KUBERNETES,
    acceptsCommand=True,
    requiresCommand=True,
    acceptsImage=True,
    requiresImage=True,
    supportsFiles=True,
    supportsWorkingDirectory=True,
    supportsResources=True,
    networkAccess=(
        RunnerNetworkAccess.INHERIT,
        RunnerNetworkAccess.NONE,
        RunnerNetworkAccess.RESTRICTED,
    ),
    supportsSecurityPolicy=True,
    supportsScopedCredentials=True,
    supportsReconciliation=True,
    extensionType=RunnerId.KUBERNETES,
    cancellationEscalation=("delete", "finalizer-cleanup", "foreground-propagation"),
    platforms=("kubernetes", "kind"),
    features=(
        "typed-job-template",
        "profile-placement-policy",
        "api-log-reconnect",
        "controlled-sidecar-workspace-transfer",
        "network-policy",
        "workload-identity",
        "owned-resource-finalizers",
        "failure-classification",
    ),
)

KubernetesRunnerLogSink = Callable[[RunnerLog], Awaitable[None]]


@dataclass
class _ActiveJob:
    name: str
    fencing_token: int
    cancel_requested: bool = False
    workspace_uploaded_pods: set[str] = field(default_factory=set)
    workspace_collected_pods: set[str] = field(default_factory=set)
    log_lengths: dict[str, int] = field(default_factory=dict)
    logs: list[RunnerLog] = field(default_factory=list)


class KubernetesJobRunner(TaskRunner):
    """Runs one fenced task attempt as one policy-bound Kubernetes Job."""

    CAPABILITIES = _CAPABILITIES

    def __init__(
        self,
        *,
        namespace: str,
        api_client: client.ApiClient | None = None,
        sync_api_client: sync_client.ApiClient | None = None,
        profile: KubernetesRunnerProfile | None = None,
        poll_interval_seconds: float = 0.25,
        cleanup_finished_jobs: bool = True,
        log_sink: KubernetesRunnerLogSink | None = None,
    ) -> None:
        self._namespace = namespace
        self._api_client = api_client or client.ApiClient()
        self._sync_api_client = sync_api_client
        self._batch = client.BatchV1Api(self._api_client)
        self._core = client.CoreV1Api(self._api_client)
        self._networking = client.NetworkingV1Api(self._api_client)
        self._sync_core = (
            sync_client.CoreV1Api(sync_api_client) if sync_api_client is not None else None
        )
        self._profile = profile
        self._poll_interval_seconds = poll_interval_seconds
        self._cleanup_finished_jobs = cleanup_finished_jobs
        self._log_sink = log_sink
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
        profile: KubernetesRunnerProfile | None = None,
        poll_interval_seconds: float = 0.25,
        cleanup_finished_jobs: bool = True,
        log_sink: KubernetesRunnerLogSink | None = None,
    ) -> KubernetesJobRunner:
        async_configuration = client.Configuration()
        await config.load_kube_config(
            context=context,
            client_configuration=async_configuration,
        )
        sync_configuration = sync_client.Configuration()
        await asyncio.to_thread(
            sync_config.load_kube_config,
            context=context,
            client_configuration=sync_configuration,
        )
        return cls(
            namespace=namespace,
            api_client=client.ApiClient(async_configuration),
            sync_api_client=sync_client.ApiClient(sync_configuration),
            profile=profile,
            poll_interval_seconds=poll_interval_seconds,
            cleanup_finished_jobs=cleanup_finished_jobs,
            log_sink=log_sink,
        )

    @classmethod
    def from_in_cluster(
        cls,
        *,
        namespace: str,
        profile: KubernetesRunnerProfile | None = None,
        poll_interval_seconds: float = 0.25,
        cleanup_finished_jobs: bool = True,
        log_sink: KubernetesRunnerLogSink | None = None,
    ) -> KubernetesJobRunner:
        async_configuration = client.Configuration()
        config.load_incluster_config(client_configuration=async_configuration)
        sync_configuration = sync_client.Configuration()
        sync_config.load_incluster_config(client_configuration=sync_configuration)
        return cls(
            namespace=namespace,
            api_client=client.ApiClient(async_configuration),
            sync_api_client=sync_client.ApiClient(sync_configuration),
            profile=profile,
            poll_interval_seconds=poll_interval_seconds,
            cleanup_finished_jobs=cleanup_finished_jobs,
            log_sink=log_sink,
        )

    async def run(self, request: RunnerRequest) -> RunnerResult:
        validate_runner_request(self.capabilities, request)
        _effective_extension(request, self._profile)
        if request.working_directory is not None and self._sync_core is None:
            raise UnsupportedRunnerRequest(
                RunnerId.KUBERNETES,
                ("workspace transfer requires a Kubernetes exec API client",),
            )
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
                    await self._create_or_reconcile_network_policy(active.name, request)
                    result = await self._wait_for_result(active, request)
                    return result.model_copy(
                        update={
                            "metrics": RunnerMetrics(duration_seconds=perf_counter() - started_at)
                        }
                    )
                except ApiException as exc:
                    if exc.status not in _TRANSIENT_API_STATUSES:
                        raise
                    await asyncio.sleep(self._poll_interval_seconds)
        finally:
            if self._cleanup_finished_jobs:
                cleanup = asyncio.create_task(self._delete_owned_resources(active.name))
                try:
                    await asyncio.shield(cleanup)
                except asyncio.CancelledError:
                    await cleanup
                    raise
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
        await self._delete_owned_resources(active.name)

    async def reconcile(
        self,
        active_attempts: Mapping[str, int],
    ) -> RunnerReconciliationResult:
        selector = _profile_selector(self._profile)
        jobs = await self._batch.list_namespaced_job(
            self._namespace,
            label_selector=selector,
        )
        cleaned: set[str] = set()
        retained: set[str] = set()
        for job in jobs.items or []:
            labels = job.metadata.labels or {}
            attempt_id = labels.get("amesh.io/attempt")
            fence = labels.get("amesh.io/fence")
            if attempt_id is None or fence is None:
                continue
            if str(active_attempts.get(attempt_id)) == fence:
                retained.add(attempt_id)
                continue
            await self._delete_owned_resources(str(job.metadata.name))
            cleaned.add(attempt_id)
        policies = await self._networking.list_namespaced_network_policy(
            self._namespace,
            label_selector=selector,
        )
        for policy in policies.items or []:
            labels = policy.metadata.labels or {}
            attempt_id = labels.get("amesh.io/attempt")
            fence = labels.get("amesh.io/fence")
            if attempt_id is not None and str(active_attempts.get(attempt_id)) == fence:
                continue
            await self._delete_network_policy(str(policy.metadata.name))
            if attempt_id is not None:
                cleaned.add(attempt_id)
        return RunnerReconciliationResult(
            runner=RunnerId.KUBERNETES,
            cleanedAttempts=tuple(sorted(cleaned)),
            retainedAttempts=tuple(sorted(retained)),
        )

    async def close(self) -> None:
        await self._api_client.close()
        if self._sync_api_client is not None:
            await asyncio.to_thread(self._sync_api_client.close)

    async def _create_or_reconcile_job(self, name: str, request: RunnerRequest) -> None:
        body = _job_body(name, request, self._profile)
        try:
            await self._batch.create_namespaced_job(self._namespace, body)
        except ApiException as exc:
            if exc.status != 409:
                raise
            existing = await self._batch.read_namespaced_job(name, self._namespace)
            _assert_owned(existing, request, "Job", name)

    async def _create_or_reconcile_network_policy(
        self,
        name: str,
        request: RunnerRequest,
    ) -> None:
        body = _network_policy_body(name, request, self._profile)
        if body is None:
            return
        try:
            await self._networking.create_namespaced_network_policy(self._namespace, body)
        except ApiException as exc:
            if exc.status != 409:
                raise
            existing = await self._networking.read_namespaced_network_policy(
                name,
                self._namespace,
            )
            _assert_owned(existing, request, "NetworkPolicy", name)

    async def _wait_for_result(
        self,
        active: _ActiveJob,
        request: RunnerRequest,
    ) -> RunnerResult:
        while True:
            if active.cancel_requested:
                return _empty_result(active.name, RunnerStatus.CANCELLED)
            try:
                job = await self._read_job(active.name)
            except ApiException as exc:
                if exc.status == 404 and active.cancel_requested:
                    return _empty_result(active.name, RunnerStatus.CANCELLED)
                raise
            pods = await self._pods(active.name)
            pod = _preferred_pod(pods)
            if pod is not None:
                await self._capture_log(active, pod)
                is_terminating = pod.metadata.deletion_timestamp is not None
                if request.working_directory is not None and not is_terminating:
                    await self._transfer_workspace(active, request, pod)
                terminated = _task_termination(pod)
                if terminated is not None:
                    exit_code, reason, message = terminated
                    if exit_code == 0:
                        return await self._pod_result(
                            active,
                            pod,
                            RunnerStatus.SUCCESS,
                            exit_code=exit_code,
                        )
                    if _job_failure(job) is not None:
                        return await self._pod_result(
                            active,
                            pod,
                            RunnerStatus.FAILED,
                            exit_code=exit_code,
                            reason=reason,
                            message=message,
                        )
                diagnosis = _pod_diagnosis(pod)
                if diagnosis is not None:
                    reason, message = diagnosis
                    if reason in {"SCHEDULING_ERROR", "IMAGE_ERROR"} or _job_failure(job):
                        return await self._pod_result(
                            active,
                            pod,
                            RunnerStatus.FAILED,
                            reason=reason,
                            message=message,
                        )
            if job.status.succeeded:
                if pod is None:
                    return _empty_result(active.name, RunnerStatus.SUCCESS)
                return await self._pod_result(active, pod, RunnerStatus.SUCCESS, exit_code=0)
            failure = _job_failure(job)
            if failure is not None:
                reason, message = failure
                status = (
                    RunnerStatus.TIMED_OUT if reason == "DeadlineExceeded" else RunnerStatus.FAILED
                )
                diagnostic_reason = "TIMEOUT" if status is RunnerStatus.TIMED_OUT else reason
                if pod is None:
                    return _empty_result(
                        active.name,
                        status,
                        reason=diagnostic_reason,
                        message=message,
                    )
                return await self._pod_result(
                    active,
                    pod,
                    status,
                    reason=diagnostic_reason,
                    message=message,
                )
            await asyncio.sleep(self._poll_interval_seconds)

    async def _read_job(self, name: str) -> Any:
        return await self._batch.read_namespaced_job(name, self._namespace)

    async def _pods(self, job_name: str) -> list[Any]:
        pod_list = await self._core.list_namespaced_pod(
            self._namespace,
            label_selector=f"job-name={job_name}",
        )
        return list(pod_list.items or [])

    async def _capture_log(self, active: _ActiveJob, pod: Any) -> None:
        pod_name = str(pod.metadata.name)
        try:
            value = await self._core.read_namespaced_pod_log(
                pod_name,
                self._namespace,
                container="task",
            )
        except ApiException as exc:
            if exc.status in {400, 404} or exc.status in _TRANSIENT_API_STATUSES:
                return
            raise
        log = str(value or "")
        previous = active.log_lengths.get(pod_name, 0)
        if len(log) <= previous:
            return
        entry = RunnerLog(
            sequence=len(active.logs),
            stream=RunnerLogStream.STDOUT,
            message=log[previous:],
        )
        active.log_lengths[pod_name] = len(log)
        active.logs.append(entry)
        if self._log_sink is not None:
            await self._log_sink(entry)

    async def _transfer_workspace(
        self,
        active: _ActiveJob,
        request: RunnerRequest,
        pod: Any,
    ) -> None:
        assert request.working_directory is not None
        assert self._sync_core is not None
        pod_name = str(pod.metadata.name)
        states = _container_states(pod)
        init_state = states.get("workspace-init")
        task_state = states.get("task")
        transfer_state = states.get("workspace-transfer")
        if pod_name not in active.workspace_uploaded_pods and init_state == "running":
            await asyncio.to_thread(
                upload_workspace,
                self._sync_core,
                namespace=self._namespace,
                pod_name=pod_name,
                root=Path(request.working_directory),
            )
            active.workspace_uploaded_pods.add(pod_name)
        elif init_state == "terminated" or task_state in {"running", "terminated"}:
            active.workspace_uploaded_pods.add(pod_name)
        if (
            task_state == "terminated"
            and transfer_state == "running"
            and pod_name not in active.workspace_collected_pods
        ):
            await asyncio.to_thread(
                download_workspace,
                self._sync_core,
                namespace=self._namespace,
                pod_name=pod_name,
                root=Path(request.working_directory),
            )
            await asyncio.to_thread(
                release_transfer_sidecar,
                self._sync_core,
                namespace=self._namespace,
                pod_name=pod_name,
            )
            active.workspace_collected_pods.add(pod_name)

    async def _pod_result(
        self,
        active: _ActiveJob,
        pod: Any,
        status: RunnerStatus,
        *,
        exit_code: int | None = None,
        reason: str | None = None,
        message: str | None = None,
    ) -> RunnerResult:
        await self._capture_log(active, pod)
        pod_name = str(pod.metadata.name)
        stdout = "".join(entry.message for entry in active.logs)
        return RunnerResult(
            runner=RunnerId.KUBERNETES,
            exit_code=exit_code if exit_code is not None else _pod_exit_code(pod),
            status=status,
            logs=tuple(active.logs),
            outputs={"stdout": stdout, "stderr": ""},
            diagnostics=RunnerDiagnostics(
                runner=RunnerId.KUBERNETES,
                externalId=active.name,
                reason=reason,
                message=message,
                details={
                    "podName": pod_name,
                    "namespace": self._namespace,
                    "profile": self._profile.name if self._profile is not None else None,
                },
            ),
        )

    async def _delete_owned_resources(self, name: str) -> None:
        await self._delete_network_policy(name)
        try:
            job = await self._batch.read_namespaced_job(name, self._namespace)
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        labels = job.metadata.labels or {}
        if labels.get("app.kubernetes.io/name") != "amesh-task":
            raise RuntimeError(f"refusing to delete unowned Job {name!r}")
        if _FINALIZER in (job.metadata.finalizers or []):
            await self._batch.patch_namespaced_job(
                name,
                self._namespace,
                {"metadata": {"finalizers": None}},
            )
        try:
            await self._batch.delete_namespaced_job(
                name,
                self._namespace,
                body=client.V1DeleteOptions(propagation_policy="Foreground"),
            )
        except ApiException as exc:
            if exc.status != 404:
                raise

    async def _delete_network_policy(self, name: str) -> None:
        try:
            await self._networking.delete_namespaced_network_policy(name, self._namespace)
        except ApiException as exc:
            if exc.status != 404:
                raise


def _job_name(attempt_id: str) -> str:
    digest = hashlib.sha256(attempt_id.encode("utf-8")).hexdigest()[:32]
    return f"amesh-{digest}"


def _job_body(
    name: str,
    request: RunnerRequest,
    profile: KubernetesRunnerProfile | None = None,
) -> dict[str, Any]:
    extension = _effective_extension(request, profile)
    template = profile.template if profile is not None else KubernetesJobTemplate()
    labels = _owner_labels(request, profile)
    labels.update(template.labels)
    labels.update(extension.labels)
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
        "resources": _resource_requirements(request.resource_limits),
        "securityContext": _task_security_context(request),
    }
    workspace_enabled = request.working_directory is not None
    if workspace_enabled:
        container["workingDir"] = _WORKSPACE
        container["volumeMounts"] = [{"name": "workspace", "mountPath": _WORKSPACE}]
    pod_spec: dict[str, Any] = {
        "restartPolicy": "Never",
        "terminationGracePeriodSeconds": math.ceil(request.cancel_grace_seconds),
        "automountServiceAccountToken": bool(profile and profile.workload_identity),
        "containers": [container],
        "securityContext": {"seccompProfile": {"type": "RuntimeDefault"}},
    }
    if workspace_enabled:
        storage_limit = _ephemeral_storage_limit(request.resource_limits)
        workspace_volume: dict[str, Any] = {"name": "workspace", "emptyDir": {}}
        if storage_limit is not None:
            workspace_volume["emptyDir"]["sizeLimit"] = storage_limit
        pod_spec.update(
            {
                "securityContext": {
                    "seccompProfile": {"type": "RuntimeDefault"},
                    "fsGroup": 65534,
                    "fsGroupChangePolicy": "OnRootMismatch",
                },
                "volumes": [workspace_volume, {"name": "control", "emptyDir": {}}],
                "initContainers": [_workspace_init_container(template.transfer_image)],
                "containers": [container, _workspace_transfer_container(template.transfer_image)],
            }
        )
    service_account = extension.service_account_name
    node_selector = extension.node_selector
    runtime_class = extension.runtime_class_name
    if profile is not None:
        service_account = profile.service_account_name
        node_selector = profile.node_selector
        runtime_class = profile.runtime_class_name
    if service_account is not None:
        pod_spec["serviceAccountName"] = service_account
        if profile is None:
            pod_spec["automountServiceAccountToken"] = True
    if node_selector:
        pod_spec["nodeSelector"] = node_selector
    if runtime_class is not None:
        pod_spec["runtimeClassName"] = runtime_class
    if template.image_pull_secrets:
        pod_spec["imagePullSecrets"] = [{"name": value} for value in template.image_pull_secrets]
    if template.priority_class_name is not None:
        pod_spec["priorityClassName"] = template.priority_class_name
    if template.scheduler_name is not None:
        pod_spec["schedulerName"] = template.scheduler_name
    if template.tolerations:
        pod_spec["tolerations"] = list(template.tolerations)
    if template.affinity:
        pod_spec["affinity"] = template.affinity
    job_spec: dict[str, Any] = {
        "backoffLimit": template.backoff_limit,
        "template": {
            "metadata": {"labels": labels, "annotations": template.annotations},
            "spec": pod_spec,
        },
    }
    if template.ttl_seconds_after_finished is not None:
        job_spec["ttlSecondsAfterFinished"] = template.ttl_seconds_after_finished
    if request.timeout_seconds is not None:
        job_spec["activeDeadlineSeconds"] = math.ceil(request.timeout_seconds)
    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": name,
            "labels": labels,
            "annotations": template.annotations,
            "finalizers": [_FINALIZER],
        },
        "spec": job_spec,
    }


def _network_policy_body(
    name: str,
    request: RunnerRequest,
    profile: KubernetesRunnerProfile | None = None,
) -> dict[str, Any] | None:
    if request.network_policy.access is RunnerNetworkAccess.INHERIT:
        return None
    egress: list[dict[str, Any]] = []
    if request.network_policy.access is RunnerNetworkAccess.RESTRICTED:
        for value in request.network_policy.allowed_egress:
            try:
                cidr = str(ipaddress.ip_network(value, strict=False))
            except ValueError as exc:
                raise RunnerPolicyViolation(
                    f"Kubernetes restricted egress requires a CIDR, got {value!r}"
                ) from exc
            egress.append({"to": [{"ipBlock": {"cidr": cidr}}]})
    labels = _owner_labels(request, profile)
    return {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {"name": name, "labels": labels},
        "spec": {
            "podSelector": {
                "matchLabels": {
                    "amesh.io/attempt": request.attempt_id,
                    "amesh.io/fence": str(request.fencing_token),
                }
            },
            "policyTypes": ["Egress"],
            "egress": egress,
        },
    }


def _effective_extension(
    request: RunnerRequest,
    profile: KubernetesRunnerProfile | None,
) -> KubernetesJobRunnerExtension:
    extension = (
        request.extension
        if isinstance(request.extension, KubernetesJobRunnerExtension)
        else KubernetesJobRunnerExtension(type=RunnerId.KUBERNETES)
    )
    if profile is None:
        return extension
    conflicts = {
        "serviceAccountName": (extension.service_account_name, profile.service_account_name),
        "nodeSelector": (extension.node_selector or None, profile.node_selector or None),
        "runtimeClassName": (extension.runtime_class_name, profile.runtime_class_name),
    }
    escaped = [
        key
        for key, (requested, allowed) in conflicts.items()
        if requested is not None and requested != allowed
    ]
    if escaped:
        raise RunnerPolicyViolation(
            "task runner settings cannot override Kubernetes profile policy: " + ", ".join(escaped)
        )
    return extension


def _owner_labels(
    request: RunnerRequest,
    profile: KubernetesRunnerProfile | None,
) -> dict[str, str]:
    labels = {
        "app.kubernetes.io/name": "amesh-task",
        "amesh.io/attempt": request.attempt_id,
        "amesh.io/fence": str(request.fencing_token),
    }
    if profile is not None:
        labels["amesh.io/profile"] = profile.name
    return labels


def _profile_selector(profile: KubernetesRunnerProfile | None) -> str:
    if profile is None:
        return _OWNER_SELECTOR
    return f"{_OWNER_SELECTOR},amesh.io/profile={profile.name}"


def _resource_requirements(values: dict[str, Any]) -> dict[str, Any]:
    if not values:
        return {"requests": {}, "limits": {}}
    nested = any(key in values for key in {"requests", "limits"})
    if nested:
        if set(values).difference({"requests", "limits"}):
            raise UnsupportedRunnerRequest(
                RunnerId.KUBERNETES,
                ("resources cannot mix requests/limits with flat values",),
            )
        requests = values.get("requests", {})
        limits = values.get("limits", {})
        if not isinstance(requests, dict) or not isinstance(limits, dict):
            raise UnsupportedRunnerRequest(
                RunnerId.KUBERNETES,
                ("resource requests and limits must be maps",),
            )
    else:
        requests = values
        limits = values
    return {
        "requests": {_resource_key(key): value for key, value in requests.items()},
        "limits": {_resource_key(key): value for key, value in limits.items()},
    }


def _resource_key(value: str) -> str:
    return "ephemeral-storage" if value == "ephemeralStorage" else value


def _ephemeral_storage_limit(values: dict[str, Any]) -> Any | None:
    normalized = _resource_requirements(values)
    return normalized["limits"].get("ephemeral-storage")


def _task_security_context(request: RunnerRequest) -> dict[str, Any]:
    policy = request.security_policy
    return {
        "privileged": policy.privileged,
        "readOnlyRootFilesystem": policy.read_only_root_filesystem,
        "allowPrivilegeEscalation": not policy.no_new_privileges,
        "capabilities": {
            "add": list(policy.capability_add),
            "drop": list(policy.capability_drop),
        },
        "seccompProfile": {"type": "RuntimeDefault"},
        **({"runAsUser": policy.run_as_user} if policy.run_as_user is not None else {}),
    }


def _workspace_init_container(image: str) -> dict[str, Any]:
    return {
        "name": "workspace-init",
        "image": image,
        "command": [
            "sh",
            "-c",
            "while [ ! -f /control/input-ready ]; do sleep 1; done; "
            "tar -xf /control/input.tar -C /workspace",
        ],
        "volumeMounts": [
            {"name": "workspace", "mountPath": _WORKSPACE},
            {"name": "control", "mountPath": "/control"},
        ],
        "securityContext": _transfer_security_context(),
    }


def _workspace_transfer_container(image: str) -> dict[str, Any]:
    return {
        "name": "workspace-transfer",
        "image": image,
        "command": [
            "sh",
            "-c",
            "while [ ! -f /control/release ]; do sleep 1; done",
        ],
        "volumeMounts": [
            {"name": "workspace", "mountPath": _WORKSPACE},
            {"name": "control", "mountPath": "/control"},
        ],
        "securityContext": _transfer_security_context(),
    }


def _transfer_security_context() -> dict[str, Any]:
    return {
        "privileged": False,
        "allowPrivilegeEscalation": False,
        "readOnlyRootFilesystem": True,
        "runAsNonRoot": True,
        "runAsUser": 65534,
        "capabilities": {"drop": ["ALL"]},
        "seccompProfile": {"type": "RuntimeDefault"},
    }


def _assert_owned(resource: Any, request: RunnerRequest, kind: str, name: str) -> None:
    labels = resource.metadata.labels or {}
    if labels.get("amesh.io/attempt") != request.attempt_id or labels.get("amesh.io/fence") != str(
        request.fencing_token
    ):
        raise RuntimeError(f"existing {kind} {name!r} belongs to another attempt")


def _preferred_pod(pods: list[Any]) -> Any | None:
    if not pods:
        return None
    pods.sort(key=lambda pod: str(pod.metadata.creation_timestamp or ""))
    return next(
        (candidate for candidate in reversed(pods) if candidate.status.phase == "Succeeded"),
        pods[-1],
    )


def _container_states(pod: Any) -> dict[str, str]:
    states: dict[str, str] = {}
    statuses = list(pod.status.init_container_statuses or []) + list(
        pod.status.container_statuses or []
    )
    for status in statuses:
        state = status.state
        if state.running is not None:
            states[str(status.name)] = "running"
        elif state.terminated is not None:
            states[str(status.name)] = "terminated"
        elif state.waiting is not None:
            states[str(status.name)] = "waiting"
    return states


def _task_termination(pod: Any) -> tuple[int, str | None, str | None] | None:
    for status in pod.status.container_statuses or []:
        if status.name != "task" or status.state.terminated is None:
            continue
        terminated = status.state.terminated
        exit_code = int(terminated.exit_code)
        if exit_code == 0:
            return exit_code, None, None
        message = terminated.message or terminated.reason or f"task exited with code {exit_code}"
        return exit_code, "USER_PROCESS_ERROR", message
    return None


def _pod_diagnosis(pod: Any) -> tuple[str, str] | None:
    if pod.status.reason == "Evicted":
        return "EVICTION", pod.status.message or "task pod was evicted"
    for condition in pod.status.conditions or []:
        if (
            condition.type == "PodScheduled"
            and condition.status == "False"
            and condition.reason == "Unschedulable"
        ):
            return "SCHEDULING_ERROR", condition.message or "task pod is unschedulable"
    image_reasons = {
        "ErrImagePull",
        "ImagePullBackOff",
        "InvalidImageName",
        "RegistryUnavailable",
    }
    for status in pod.status.container_statuses or []:
        waiting = status.state.waiting
        if status.name == "task" and waiting is not None and waiting.reason in image_reasons:
            return "IMAGE_ERROR", waiting.message or waiting.reason
    if pod.status.phase == "Failed":
        return (
            "INFRASTRUCTURE_ERROR",
            pod.status.message or pod.status.reason or "task pod failed",
        )
    return None


def _job_failure(job: Any) -> tuple[str | None, str | None] | None:
    for condition in job.status.conditions or []:
        if condition.type == "Failed" and condition.status == "True":
            return condition.reason, condition.message
    return None


def _pod_exit_code(pod: Any) -> int | None:
    termination = _task_termination(pod)
    return termination[0] if termination is not None else None


def _empty_result(
    job_name: str,
    status: RunnerStatus,
    *,
    reason: str | None = None,
    message: str | None = None,
) -> RunnerResult:
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
