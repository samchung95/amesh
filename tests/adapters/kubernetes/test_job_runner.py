from __future__ import annotations

import asyncio
import os
from contextlib import suppress
from pathlib import Path
from uuid import UUID, uuid4, uuid5

import pytest
from kubernetes.aio import client, config
from kubernetes.client.exceptions import ApiException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.kubernetes import KubernetesJobRunner
from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.domain import ExecutionState
from amesh.domain.runner import KubernetesJobTemplate, KubernetesRunnerProfile
from amesh.dsl.models import FlowDefinition, TaskDefinition
from amesh.executor import InProcessExecutor, TaskExecutionContext, kubernetes_job_handler
from amesh.ports import RunnerNetworkAccess, RunnerNetworkPolicy, RunnerRequest, RunnerStatus

KIND_CONTEXT = os.getenv("AMESH_KIND_CONTEXT")

pytestmark = pytest.mark.skipif(
    KIND_CONTEXT is None,
    reason="AMESH_KIND_CONTEXT is required",
)


async def cleanup_execution(engine: AsyncEngine, execution_id: UUID) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM messages_outbox WHERE partition_key = :partition_key"),
            {"partition_key": f"execution:{execution_id}"},
        )
        await connection.execute(
            text(
                "DELETE FROM transition_rejections WHERE "
                "(aggregate_type = 'execution' AND aggregate_id = :execution_id) OR "
                "(aggregate_type = 'task_run' AND aggregate_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = :execution_id))"
            ),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM task_run_events WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM execution_logs WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text(
                "DELETE FROM task_attempts WHERE task_run_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = :execution_id)"
            ),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM task_runs WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM execution_events WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM executions WHERE id = :execution_id"),
            {"execution_id": execution_id},
        )


async def wait_for_running_pod(core: client.CoreV1Api, namespace: str) -> str:
    for _ in range(240):
        pod_list = await core.list_namespaced_pod(
            namespace,
            label_selector="app.kubernetes.io/name=amesh-task",
        )
        for pod in pod_list.items:
            if pod.status.phase == "Running":
                return str(pod.metadata.name)
        await asyncio.sleep(0.25)
    raise TimeoutError("Kubernetes Job did not create a running pod")


def test_executor_job_survives_pod_deletion_on_kind(migrated_test_database_url: str) -> None:
    async def scenario() -> None:
        if KIND_CONTEXT is None:
            raise RuntimeError("kind settings are required")
        namespace = f"amesh-test-{uuid4().hex[:10]}"
        await config.load_kube_config(context=KIND_CONTEXT)
        observer_client = client.ApiClient()
        observer = client.CoreV1Api(observer_client)
        await observer.create_namespace({"metadata": {"name": namespace}})

        runner = await KubernetesJobRunner.from_kube_config(
            namespace=namespace,
            context=KIND_CONTEXT,
            poll_interval_seconds=0.2,
        )
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(
            repository,
            handlers={"core.shell": kubernetes_job_handler(runner)},
        )
        flow = FlowDefinition(
            id="kind_job",
            namespace=f"tests.kubernetes.{uuid4().hex}",
            tasks=[
                TaskDefinition(
                    id="shell",
                    type="core.shell",
                    image="busybox:1.37.0",
                    command=["sh", "-c", "echo started; sleep 5; echo completed"],
                    resources={"cpu": "10m", "memory": "16Mi"},
                    timeout_seconds=60,
                )
            ],
        )
        execution_id = await executor.create_execution(flow, tenant_id="default")
        execution_task = asyncio.create_task(
            executor.run_to_completion(flow, execution_id, tenant_id="default")
        )
        try:
            deleted_pod = await wait_for_running_pod(observer, namespace)
            await observer.delete_namespaced_pod(
                deleted_pod,
                namespace,
                body=client.V1DeleteOptions(
                    grace_period_seconds=0,
                    propagation_policy="Foreground",
                ),
            )
            completed = await asyncio.wait_for(execution_task, timeout=90)

            assert completed.state is ExecutionState.SUCCESS
            result = completed.task_runs[0].result
            assert result is not None
            assert result["exitCode"] == 0
            assert "completed" in result["stdout"]
            assert result["diagnostics"]["podName"] != deleted_pod
        finally:
            if not execution_task.done():
                execution_task.cancel()
                with suppress(asyncio.CancelledError):
                    await execution_task
            await cleanup_execution(engine, execution_id)
            await engine.dispose()
            await runner.close()
            try:
                await observer.delete_namespace(namespace)
            except ApiException as exc:
                if exc.status != 404:
                    raise
            await observer_client.close()

    asyncio.run(scenario())


def test_fresh_executor_reconciles_running_job_after_control_plane_loss(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        if KIND_CONTEXT is None:
            raise RuntimeError("kind settings are required")
        namespace = f"amesh-recovery-{uuid4().hex[:10]}"
        await config.load_kube_config(context=KIND_CONTEXT)
        observer_client = client.ApiClient()
        observer = client.CoreV1Api(observer_client)
        await observer.create_namespace({"metadata": {"name": namespace}})

        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        task = TaskDefinition(
            id="shell",
            type="core.shell",
            image="busybox:1.37.0",
            command=["sh", "-c", "echo started; sleep 5; echo recovered"],
            resources={"cpu": "10m", "memory": "16Mi"},
            timeout_seconds=60,
        )
        flow = FlowDefinition(
            id="control_plane_recovery",
            namespace=f"tests.kubernetes.{uuid4().hex}",
            tasks=[task],
        )
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        task_run = (
            await repository.list_task_runs(
                execution.execution_id,
                tenant_id="default",
            )
        )[0]
        running = await repository.start_task(task_run.task_run_id, tenant_id="default")
        context = TaskExecutionContext(
            tenant_id="default",
            execution_id=execution.execution_id,
            task_run_id=running.task_run_id,
            attempt=running.current_attempt,
            attempt_id=uuid5(running.task_run_id, f"attempt:{running.current_attempt}"),
            inputs={},
            outputs={},
            variables={},
        )
        abandoned_runner = await KubernetesJobRunner.from_kube_config(
            namespace=namespace,
            context=KIND_CONTEXT,
            poll_interval_seconds=0.2,
            cleanup_finished_jobs=False,
        )
        abandoned_call = asyncio.create_task(
            kubernetes_job_handler(abandoned_runner)(task, context)
        )
        resumed_runner: KubernetesJobRunner | None = None
        try:
            original_pod = await wait_for_running_pod(observer, namespace)
            abandoned_call.cancel()
            with suppress(asyncio.CancelledError):
                await abandoned_call
            await abandoned_runner.close()

            resumed_runner = await KubernetesJobRunner.from_kube_config(
                namespace=namespace,
                context=KIND_CONTEXT,
                poll_interval_seconds=0.2,
            )
            resumed_executor = InProcessExecutor(
                repository,
                handlers={"core.shell": kubernetes_job_handler(resumed_runner)},
                recover_running_types=frozenset({"core.shell"}),
            )
            completed = await asyncio.wait_for(
                resumed_executor.run_to_completion(
                    flow,
                    execution.execution_id,
                    tenant_id="default",
                ),
                timeout=90,
            )

            assert completed.state is ExecutionState.SUCCESS
            assert completed.task_runs[0].current_attempt == 1
            result = completed.task_runs[0].result
            assert result is not None
            assert result["exitCode"] == 0
            assert "recovered" in result["stdout"]
            assert result["diagnostics"]["podName"] == original_pod
        finally:
            if not abandoned_call.done():
                abandoned_call.cancel()
                with suppress(asyncio.CancelledError):
                    await abandoned_call
            await cleanup_execution(engine, execution.execution_id)
            await engine.dispose()
            if resumed_runner is not None:
                await resumed_runner.close()
            try:
                await observer.delete_namespace(namespace)
            except ApiException as exc:
                if exc.status != 404:
                    raise
            await observer_client.close()

    asyncio.run(scenario())


def test_profiled_job_transfers_workspace_and_applies_network_policy_on_kind(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        if KIND_CONTEXT is None:
            raise RuntimeError("kind settings are required")
        namespace = f"amesh-profile-{uuid4().hex[:10]}"
        await config.load_kube_config(context=KIND_CONTEXT)
        observer_client = client.ApiClient()
        core = client.CoreV1Api(observer_client)
        batch = client.BatchV1Api(observer_client)
        networking = client.NetworkingV1Api(observer_client)
        await core.create_namespace({"metadata": {"name": namespace}})
        await core.create_namespaced_service_account(
            namespace,
            {"metadata": {"name": "amesh-workload"}},
        )
        profile = KubernetesRunnerProfile(
            name="kind-profile",
            context=KIND_CONTEXT,
            namespace=namespace,
            serviceAccountName="amesh-workload",
            nodeSelector={"kubernetes.io/hostname": "amesh-w7-control-plane"},
            workloadIdentity=True,
            template=KubernetesJobTemplate(
                labels={"qualification": "epic-222"},
                annotations={"amesh.io/qualification": "epic-222"},
            ),
        )
        runner = await KubernetesJobRunner.from_kube_config(
            namespace=namespace,
            context=KIND_CONTEXT,
            profile=profile,
            poll_interval_seconds=0.2,
        )
        (tmp_path / "input.txt").write_text("portable", encoding="utf-8")
        task = asyncio.create_task(
            runner.run(
                RunnerRequest(
                    tenant_id="default",
                    namespace="tests.kubernetes.profile",
                    execution_id="execution-profile",
                    task_run_id="task-profile",
                    attempt_id=f"profile-{uuid4()}",
                    fencing_token=1,
                    command=[
                        "sh",
                        "-c",
                        "cat input.txt > output.txt; echo profile-ready; sleep 2",
                    ],
                    image="busybox:1.37.0",
                    working_directory=str(tmp_path),
                    resource_limits={
                        "requests": {"cpu": "10m", "memory": "16Mi"},
                        "limits": {
                            "cpu": "50m",
                            "memory": "32Mi",
                            "ephemeralStorage": "64Mi",
                        },
                    },
                    network_policy=RunnerNetworkPolicy(access=RunnerNetworkAccess.NONE),
                    timeout_seconds=60,
                )
            )
        )
        try:
            for _ in range(120):
                jobs = await batch.list_namespaced_job(
                    namespace,
                    label_selector="amesh.io/profile=kind-profile",
                )
                policies = await networking.list_namespaced_network_policy(
                    namespace,
                    label_selector="amesh.io/profile=kind-profile",
                )
                if jobs.items and policies.items:
                    break
                await asyncio.sleep(0.1)
            else:
                raise TimeoutError("profiled Job and NetworkPolicy were not created")
            job = jobs.items[0]
            pod_spec = job.spec.template.spec
            assert job.metadata.finalizers == ["amesh.io/task-cleanup"]
            assert job.metadata.annotations["amesh.io/qualification"] == "epic-222"
            assert pod_spec.service_account_name == "amesh-workload"
            assert pod_spec.automount_service_account_token is True
            assert pod_spec.node_selector == {"kubernetes.io/hostname": "amesh-w7-control-plane"}
            assert pod_spec.containers[0].resources.limits["ephemeral-storage"] == "64Mi"
            assert policies.items[0].spec.egress is None

            result = await asyncio.wait_for(task, timeout=90)
            assert result.status is RunnerStatus.SUCCESS
            assert "profile-ready" in result.outputs["stdout"]
            assert (tmp_path / "output.txt").read_text(encoding="utf-8") == "portable"
        finally:
            if not task.done():
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
            await runner.close()
            try:
                await core.delete_namespace(namespace)
            except ApiException as exc:
                if exc.status != 404:
                    raise
            await observer_client.close()

    asyncio.run(scenario())
