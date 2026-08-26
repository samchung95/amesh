from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import cast
from uuid import uuid4

import pytest
from pydantic import SecretStr, ValidationError

from amesh.adapters.kubernetes.job_runner import _job_body
from amesh.adapters.local import LocalProcessRunner
from amesh.domain.runner import (
    KubernetesJobRunnerExtension,
    RunnerId,
    RunnerNetworkAccess,
    RunnerNetworkPolicy,
    RunnerPolicy,
    RunnerPolicySet,
    RunnerPolicyViolation,
    RunnerSecurityPolicy,
)
from amesh.dsl import validate_flow_document
from amesh.dsl.models import TaskDefinition
from amesh.executor import (
    TaskCancellationChannel,
    TaskExecutionContext,
    TaskExecutionFailure,
    local_process_handler,
)
from amesh.ports import (
    RunnerLogStream,
    RunnerRequest,
    RunnerStatus,
    ScopedRunnerCredential,
    UnsupportedRunnerRequest,
    validate_runner_request,
)


def _request(*command: str, **updates: object) -> RunnerRequest:
    values: dict[str, object] = {
        "tenant_id": "default",
        "namespace": "company.platform",
        "execution_id": "execution-1",
        "task_run_id": "task-1",
        "attempt_id": "attempt-1",
        "fencing_token": 1,
        "command": list(command),
    }
    values.update(updates)
    return RunnerRequest.model_validate(values)


def test_urs_f_0250_0251_local_capabilities_reject_before_dispatch(tmp_path: Path) -> None:
    marker = tmp_path / "must-not-exist"
    runner = LocalProcessRunner()
    request = _request(
        sys.executable,
        "-c",
        f"from pathlib import Path; Path({str(marker)!r}).touch()",
        image="busybox:1.37",
    )

    with pytest.raises(UnsupportedRunnerRequest, match="image"):
        asyncio.run(runner.run(request))

    assert runner.capabilities.runner is RunnerId.LOCAL
    assert runner.capabilities.contract_versions == ("1.0",)
    assert not marker.exists()


def test_urs_f_0252_result_is_normalized() -> None:
    async def scenario() -> None:
        result = await LocalProcessRunner().run(
            _request(sys.executable, "-c", "print('normalized')")
        )

        assert result.runner is RunnerId.LOCAL
        assert result.status is RunnerStatus.SUCCESS
        assert result.exit_code == 0
        assert result.logs[0].stream is RunnerLogStream.STDOUT
        assert result.logs[0].message.strip() == "normalized"
        assert result.metrics.duration_seconds > 0
        assert result.diagnostics.runner is RunnerId.LOCAL

    asyncio.run(scenario())


def test_urs_f_0253_handler_propagates_cancellation_to_runner() -> None:
    class DelayedCancellation:
        async def wait(self, *, poll_interval: float = 0.05) -> None:
            del poll_interval
            await asyncio.sleep(0.05)

    async def scenario() -> None:
        task = TaskDefinition(
            id="cancelled",
            type="core.shell",
            command=[sys.executable, "-c", "import time; time.sleep(30)"],
        )
        context = TaskExecutionContext(
            tenant_id="default",
            execution_id=uuid4(),
            task_run_id=uuid4(),
            attempt=1,
            attempt_id=uuid4(),
            inputs={},
            outputs={},
            variables={},
            cancellation=cast(TaskCancellationChannel, DelayedCancellation()),
        )

        with pytest.raises(TaskExecutionFailure, match="CANCELLED"):
            await local_process_handler(LocalProcessRunner(), namespace="tests.runner")(
                task,
                context,
            )

    asyncio.run(scenario())


def test_urs_f_0254_0255_typed_extension_and_attempt_scoped_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AMESH_PARENT_SECRET", "must-not-leak")
    credential = ScopedRunnerCredential(
        scope="scoped_token",
        environmentVariable="SCOPED_TOKEN",
        value=SecretStr("attempt-only"),
    )
    request = _request(
        sys.executable,
        "-c",
        (
            "import os; "
            "print(os.getenv('SCOPED_TOKEN')); "
            "print(os.getenv('AMESH_PARENT_SECRET', 'isolated'))"
        ),
        credentials=(credential,),
    )

    result = asyncio.run(LocalProcessRunner().run(request))

    assert result.outputs["stdout"].splitlines() == ["[REDACTED]", "isolated"]
    assert "attempt-only" not in repr(request)
    assert request.model_dump(mode="json")["credentials"][0]["value"] == "**********"

    task = TaskDefinition(
        id="typed",
        type="core.shell",
        command=["true"],
        taskRunner={"type": "kubernetes", "serviceAccountName": "amesh-task"},
        runnerCredentials={"SCOPED_TOKEN": "scoped_token"},
        contract={"secretScopes": ["scoped_token"]},
    )
    assert isinstance(task.task_runner, KubernetesJobRunnerExtension)

    with pytest.raises(ValidationError, match="undeclared contract secretScopes"):
        TaskDefinition(
            id="invalid",
            type="core.shell",
            command=["true"],
            runnerCredentials={"SCOPED_TOKEN": "scoped_token"},
        )


def test_core_shell_resource_catalog_accepts_typed_runner_fields() -> None:
    result = validate_flow_document(
        """
id: runner_catalog
namespace: tests.runner
tasks:
  - id: typed
    type: core.shell
    command: [python, -c, "print('ok')"]
    taskRunner:
      type: local
      inheritHostEnvironment: false
    networkPolicy: {access: inherit}
    securityPolicy: {privileged: false}
"""
    )

    assert result.valid, result.issues


def test_urs_f_0256_local_orphan_reconciliation_is_idempotent() -> None:
    async def scenario() -> None:
        runner = LocalProcessRunner()
        running = asyncio.create_task(
            runner.run(_request(sys.executable, "-c", "import time; time.sleep(30)"))
        )
        for _ in range(100):
            if not running.done() and runner._active:
                break
            await asyncio.sleep(0.01)

        first = await runner.reconcile({})
        result = await running
        second = await runner.reconcile({})

        assert first.cleaned_attempts == ("attempt-1",)
        assert result.status is RunnerStatus.CANCELLED
        assert second.cleaned_attempts == ()

    asyncio.run(scenario())


def test_urs_f_0257_namespace_and_worker_group_policy_selects_and_prohibits() -> None:
    policies = RunnerPolicySet(
        (
            RunnerPolicy(
                namespacePrefix="company",
                defaultRunner=RunnerId.KUBERNETES,
                allowedRunners=(RunnerId.LOCAL, RunnerId.KUBERNETES),
            ),
            RunnerPolicy(
                namespacePrefix="company.platform",
                workerGroup="regulated",
                defaultRunner=RunnerId.KUBERNETES,
                allowedRunners=(RunnerId.KUBERNETES,),
            ),
        )
    )
    available = frozenset(RunnerId)

    assert (
        policies.select(
            namespace="company.platform",
            worker_group=None,
            requested=None,
            fallback=RunnerId.LOCAL,
            available=available,
        )
        is RunnerId.KUBERNETES
    )
    with pytest.raises(RunnerPolicyViolation, match="prohibited"):
        policies.select(
            namespace="company.platform",
            worker_group="regulated",
            requested=RunnerId.LOCAL,
            fallback=RunnerId.LOCAL,
            available=available,
        )


def test_kubernetes_typed_security_and_credentials_map_to_job() -> None:
    request = _request(
        "sh",
        "-c",
        "echo ok",
        image="busybox:1.37",
        credentials=(
            ScopedRunnerCredential(
                scope="token",
                environmentVariable="TOKEN",
                value=SecretStr("scoped"),
            ),
        ),
        security_policy=RunnerSecurityPolicy(
            readOnlyRootFilesystem=True,
            runAsUser=1000,
        ),
        extension=KubernetesJobRunnerExtension(
            type=RunnerId.KUBERNETES,
            serviceAccountName="amesh-task",
            labels={"workload": "batch"},
            nodeSelector={"pool": "jobs"},
        ),
    )

    body = _job_body("amesh-test", request)
    pod = body["spec"]["template"]
    container = pod["spec"]["containers"][0]

    assert pod["metadata"]["labels"]["workload"] == "batch"
    assert pod["spec"]["serviceAccountName"] == "amesh-task"
    assert pod["spec"]["nodeSelector"] == {"pool": "jobs"}
    assert container["securityContext"]["runAsUser"] == 1000
    assert {"name": "TOKEN", "value": "scoped"} in container["env"]


def test_network_policy_is_part_of_request_and_rejected_when_unsupported() -> None:
    request = _request(
        sys.executable,
        "-c",
        "print('no dispatch')",
        network_policy=RunnerNetworkPolicy(access=RunnerNetworkAccess.NONE),
    )

    with pytest.raises(UnsupportedRunnerRequest, match="network access none"):
        validate_runner_request(LocalProcessRunner().capabilities, request)
