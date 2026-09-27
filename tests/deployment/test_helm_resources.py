from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
CHART = ROOT / "charts" / "amesh"
WORKLOAD_KINDS = {"CronJob", "Deployment", "Job", "StatefulSet"}


def _render_chart(extra_args: list[str]) -> list[dict[str, Any]]:
    if shutil.which("helm") is None:
        pytest.skip("Helm is not installed")
    result = subprocess.run(
        ["helm", "template", "resource-check", str(CHART), *extra_args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return [
        document for document in yaml.safe_load_all(result.stdout) if isinstance(document, dict)
    ]


def _pod_spec(workload: dict[str, Any]) -> dict[str, Any]:
    kind = workload["kind"]
    if kind in {"Deployment", "StatefulSet"}:
        return workload["spec"]["template"]["spec"]
    if kind == "Job":
        return workload["spec"]["template"]["spec"]
    if kind == "CronJob":
        return workload["spec"]["jobTemplate"]["spec"]["template"]["spec"]
    raise AssertionError(f"unsupported workload kind {kind}")


def _containers(workload: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    metadata = workload.get("metadata", {})
    workload_name = metadata.get("name", "<unnamed>")
    pod_spec = _pod_spec(workload)
    containers: list[tuple[str, dict[str, Any]]] = []
    for section in ("initContainers", "containers"):
        for container in pod_spec.get(section, []) or []:
            container_name = container.get("name", "<unnamed>")
            path = f"{workload['kind']}/{workload_name}/{section}/{container_name}"
            containers.append((path, container))
    return containers


@pytest.mark.parametrize(
    ("extra_args", "expected_workload_names"),
    [
        (
            [],
            {
                "resource-check-amesh-executor",
                "resource-check-amesh-indexer",
                "resource-check-amesh-maintenance",
                "resource-check-amesh-migrate",
                "resource-check-amesh-scheduler",
                "resource-check-amesh-server",
                "resource-check-amesh-worker",
            },
        ),
        (
            [
                "--set",
                "worker.enabled=true",
                "--set",
                "serviceRoles.worker.enabled=false",
                "--set",
                "recovery.enabled=true",
                "--set",
                "operator.enabled=true",
            ],
            {
                "resource-check-amesh-executor",
                "resource-check-amesh-indexer",
                "resource-check-amesh-maintenance",
                "resource-check-amesh-migrate",
                "resource-check-amesh-operator",
                "resource-check-amesh-recovery",
                "resource-check-amesh-scheduler",
                "resource-check-amesh-server",
                "resource-check-amesh-worker",
            },
        ),
    ],
)
def test_helm_workload_containers_render_with_requests_and_memory_limits(
    extra_args: list[str],
    expected_workload_names: set[str],
) -> None:
    manifests = _render_chart(extra_args)
    workloads = [manifest for manifest in manifests if manifest.get("kind") in WORKLOAD_KINDS]
    assert workloads
    rendered_workload_names = {workload["metadata"]["name"] for workload in workloads}
    assert expected_workload_names <= rendered_workload_names

    checked_containers: list[str] = []
    for workload in workloads:
        for path, container in _containers(workload):
            checked_containers.append(path)
            resources = container.get("resources") or {}
            requests = resources.get("requests") or {}
            limits = resources.get("limits") or {}
            assert requests.get("cpu"), f"{path} is missing a CPU request"
            assert requests.get("memory"), f"{path} is missing a memory request"
            assert limits.get("memory"), f"{path} is missing a memory limit"

    assert checked_containers
