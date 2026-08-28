from __future__ import annotations

import asyncio
import io
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest
from kubernetes.aio.client.exceptions import ApiException
from pydantic import ValidationError

from amesh.adapters.kubernetes.job_runner import (
    KubernetesJobRunner,
    _ActiveJob,
    _job_body,
    _network_policy_body,
    _pod_diagnosis,
)
from amesh.adapters.kubernetes.workspace import restore_workspace, workspace_archive
from amesh.domain.runner import (
    KubernetesJobRunnerExtension,
    KubernetesJobTemplate,
    KubernetesRunnerProfile,
    KubernetesRunnerProfileSet,
    RunnerId,
    RunnerNetworkAccess,
    RunnerNetworkPolicy,
    RunnerPolicyViolation,
)
from amesh.ports import RunnerRequest, RunnerStatus


def request(**updates: object) -> RunnerRequest:
    values: dict[str, object] = {
        "tenant_id": "default",
        "namespace": "company.analytics",
        "worker_group": "batch",
        "execution_id": "execution-1",
        "task_run_id": "task-1",
        "attempt_id": "attempt-1",
        "fencing_token": 2,
        "command": ["sh", "-c", "echo ok"],
        "image": "busybox:1.37.0",
    }
    values.update(updates)
    return RunnerRequest.model_validate(values)


def test_profile_selection_prefers_worker_and_namespace_specific_scope() -> None:
    default = KubernetesRunnerProfile(name="default")
    namespace = KubernetesRunnerProfile(name="analytics", namespacePrefix="company")
    worker = KubernetesRunnerProfile(
        name="analytics-batch",
        namespacePrefix="company.analytics",
        workerGroup="batch",
    )
    profiles = KubernetesRunnerProfileSet((default, namespace, worker))

    assert profiles.select("company.analytics", "batch") is worker
    assert profiles.select("company.other", None) is namespace
    assert profiles.select("elsewhere", None) is default


def test_workload_identity_requires_operator_service_account() -> None:
    with pytest.raises(ValidationError, match="serviceAccountName"):
        KubernetesRunnerProfile(name="invalid", workloadIdentity=True)


def test_typed_job_template_applies_policy_resources_and_workspace(tmp_path: Path) -> None:
    profile = KubernetesRunnerProfile(
        name="regulated",
        namespace="amesh-regulated",
        serviceAccountName="amesh-workload",
        nodeSelector={"pool": "isolated"},
        runtimeClassName="gvisor",
        workloadIdentity=True,
        template=KubernetesJobTemplate(
            labels={"workload": "regulated"},
            annotations={"example.com/policy": "strict"},
            imagePullSecrets=("registry",),
            priorityClassName="batch",
            schedulerName="default-scheduler",
            tolerations=({"key": "batch", "operator": "Exists"},),
            affinity={"nodeAffinity": {}},
            backoffLimit=3,
            ttlSecondsAfterFinished=600,
        ),
    )
    body = _job_body(
        "amesh-test",
        request(
            working_directory=str(tmp_path),
            resource_limits={
                "requests": {"cpu": "100m", "memory": "64Mi"},
                "limits": {"cpu": "500m", "memory": "128Mi", "ephemeralStorage": "1Gi"},
            },
        ),
        profile,
    )
    pod = body["spec"]["template"]
    spec = pod["spec"]
    task = spec["containers"][0]

    assert body["metadata"]["finalizers"] == ["amesh.io/task-cleanup"]
    assert body["metadata"]["labels"]["amesh.io/profile"] == "regulated"
    assert pod["metadata"]["labels"]["workload"] == "regulated"
    assert spec["serviceAccountName"] == "amesh-workload"
    assert spec["automountServiceAccountToken"] is True
    assert spec["nodeSelector"] == {"pool": "isolated"}
    assert spec["runtimeClassName"] == "gvisor"
    assert spec["imagePullSecrets"] == [{"name": "registry"}]
    assert spec["priorityClassName"] == "batch"
    assert spec["schedulerName"] == "default-scheduler"
    assert spec["tolerations"] == [{"key": "batch", "operator": "Exists"}]
    assert spec["affinity"] == {"nodeAffinity": {}}
    assert body["spec"]["backoffLimit"] == 3
    assert body["spec"]["ttlSecondsAfterFinished"] == 600
    assert task["workingDir"] == "/workspace"
    assert task["resources"]["requests"] == {"cpu": "100m", "memory": "64Mi"}
    assert task["resources"]["limits"]["ephemeral-storage"] == "1Gi"
    assert spec["volumes"][0]["emptyDir"]["sizeLimit"] == "1Gi"
    assert [item["name"] for item in spec["initContainers"]] == ["workspace-init"]
    assert [item["name"] for item in spec["containers"]] == [
        "task",
        "workspace-transfer",
    ]


def test_task_cannot_escape_profile_placement_policy() -> None:
    profile = KubernetesRunnerProfile(name="owned", serviceAccountName="operator-owned")
    task_request = request(
        extension=KubernetesJobRunnerExtension(
            type=RunnerId.KUBERNETES,
            serviceAccountName="task-selected",
        )
    )

    with pytest.raises(RunnerPolicyViolation, match="serviceAccountName"):
        _job_body("amesh-test", task_request, profile)


def test_network_policy_maps_none_and_restricted_cidrs() -> None:
    denied = _network_policy_body(
        "amesh-test",
        request(network_policy=RunnerNetworkPolicy(access=RunnerNetworkAccess.NONE)),
    )
    restricted = _network_policy_body(
        "amesh-test",
        request(
            network_policy=RunnerNetworkPolicy(
                access=RunnerNetworkAccess.RESTRICTED,
                allowedEgress=("10.20.0.1/16", "2001:db8::/64"),
            )
        ),
    )

    assert denied is not None and denied["spec"]["egress"] == []
    assert restricted is not None
    assert restricted["spec"]["egress"] == [
        {"to": [{"ipBlock": {"cidr": "10.20.0.0/16"}}]},
        {"to": [{"ipBlock": {"cidr": "2001:db8::/64"}}]},
    ]
    with pytest.raises(RunnerPolicyViolation, match="requires a CIDR"):
        _network_policy_body(
            "amesh-test",
            request(
                network_policy=RunnerNetworkPolicy(
                    access=RunnerNetworkAccess.RESTRICTED,
                    allowedEgress=("example.com",),
                )
            ),
        )


def test_failure_diagnostics_distinguish_scheduling_image_eviction_and_infrastructure() -> None:
    waiting = SimpleNamespace(reason="ImagePullBackOff", message="denied")
    task_status = SimpleNamespace(name="task", state=SimpleNamespace(waiting=waiting))
    image_pod = SimpleNamespace(
        status=SimpleNamespace(
            reason=None,
            message=None,
            phase="Pending",
            conditions=[],
            container_statuses=[task_status],
        )
    )
    scheduling_pod = SimpleNamespace(
        status=SimpleNamespace(
            reason=None,
            message=None,
            phase="Pending",
            conditions=[
                SimpleNamespace(
                    type="PodScheduled",
                    status="False",
                    reason="Unschedulable",
                    message="no matching nodes",
                )
            ],
            container_statuses=[],
        )
    )
    eviction_pod = SimpleNamespace(
        status=SimpleNamespace(
            reason="Evicted",
            message="disk pressure",
            phase="Failed",
            conditions=[],
            container_statuses=[],
        )
    )
    infrastructure_pod = SimpleNamespace(
        status=SimpleNamespace(
            reason="NodeLost",
            message="node unavailable",
            phase="Failed",
            conditions=[],
            container_statuses=[],
        )
    )

    assert _pod_diagnosis(scheduling_pod)[0] == "SCHEDULING_ERROR"  # type: ignore[index]
    assert _pod_diagnosis(image_pod)[0] == "IMAGE_ERROR"  # type: ignore[index]
    assert _pod_diagnosis(eviction_pod)[0] == "EVICTION"  # type: ignore[index]
    assert _pod_diagnosis(infrastructure_pod)[0] == "INFRASTRUCTURE_ERROR"  # type: ignore[index]


def test_api_log_polling_recovers_and_emits_only_new_suffix() -> None:
    class FakeCore:
        def __init__(self) -> None:
            self.values: list[object] = [ApiException(status=503), "one\n", "one\ntwo\n"]

        async def read_namespaced_pod_log(self, *args: object, **kwargs: object) -> str:
            del args, kwargs
            value = self.values.pop(0)
            if isinstance(value, Exception):
                raise value
            return str(value)

    async def scenario() -> None:
        runner = KubernetesJobRunner(namespace="test")
        runner._core = FakeCore()  # type: ignore[assignment]
        active = _ActiveJob(name="amesh-test", fencing_token=1)
        pod = SimpleNamespace(metadata=SimpleNamespace(name="pod-1"))
        try:
            await runner._capture_log(active, pod)
            await runner._capture_log(active, pod)
            await runner._capture_log(active, pod)
        finally:
            await runner.close()
        assert [item.message for item in active.logs] == ["one\n", "two\n"]

    asyncio.run(scenario())


def test_api_log_polling_redacts_secret_split_across_poll_boundaries() -> None:
    class FakeCore:
        def __init__(self) -> None:
            self.values = [
                "prefix-split",
                "prefix-split-secret-suffix",
                "prefix-split-secret-suffix",
            ]

        async def read_namespaced_pod_log(self, *args: object, **kwargs: object) -> str:
            del args, kwargs
            return self.values.pop(0)

    async def scenario() -> None:
        runner = KubernetesJobRunner(namespace="test")
        runner._core = FakeCore()  # type: ignore[assignment]
        active = _ActiveJob(
            name="amesh-test",
            fencing_token=1,
            secret_values=("split-secret",),
        )
        pod = SimpleNamespace(
            metadata=SimpleNamespace(name="pod-1"),
            status=SimpleNamespace(container_statuses=[]),
        )
        await runner._capture_log(active, pod)
        await runner._capture_log(active, pod)
        result = await runner._pod_result(active, pod, RunnerStatus.SUCCESS, exit_code=0)
        rendered = str(result.outputs["stdout"])
        assert rendered == "prefix-[REDACTED]-suffix"
        assert "split-secret" not in rendered
        await runner.close()

    asyncio.run(scenario())


def test_finalizer_cleanup_is_owned_and_idempotent() -> None:
    class FakeBatch:
        def __init__(self) -> None:
            self.patches: list[object] = []
            self.deleted = 0

        async def read_namespaced_job(self, *args: object) -> object:
            del args
            return SimpleNamespace(
                metadata=SimpleNamespace(
                    labels={"app.kubernetes.io/name": "amesh-task"},
                    finalizers=["amesh.io/task-cleanup"],
                )
            )

        async def patch_namespaced_job(self, *args: object) -> None:
            self.patches.append(args[-1])

        async def delete_namespaced_job(self, *args: object, **kwargs: object) -> None:
            del args, kwargs
            self.deleted += 1

    class FakeNetworking:
        async def delete_namespaced_network_policy(self, *args: object) -> None:
            del args
            raise ApiException(status=404)

    async def scenario() -> None:
        runner = KubernetesJobRunner(namespace="test")
        batch = FakeBatch()
        runner._batch = batch  # type: ignore[assignment]
        runner._networking = FakeNetworking()  # type: ignore[assignment]
        try:
            await runner._delete_owned_resources("amesh-test")
        finally:
            await runner.close()
        assert batch.patches == [{"metadata": {"finalizers": None}}]
        assert batch.deleted == 1

    asyncio.run(scenario())


def test_workspace_archive_round_trip_and_rejects_escaping_members(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    (source / "nested").mkdir()
    (source / "nested" / "value.txt").write_text("portable", encoding="utf-8")

    restore_workspace(target, workspace_archive(source))
    assert (target / "nested" / "value.txt").read_text(encoding="utf-8") == "portable"

    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w") as archive:
        member = tarfile.TarInfo("../escape.txt")
        member.size = 1
        archive.addfile(member, io.BytesIO(b"x"))
    with pytest.raises(ValueError, match="escapes workspace"):
        restore_workspace(target, payload.getvalue())
