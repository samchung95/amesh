from __future__ import annotations

import argparse
import asyncio
import json
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any
from uuid import uuid4

import httpx
import yaml
from kubernetes.aio import client, config  # type: ignore[import-untyped]
from kubernetes.aio.client.exceptions import ApiException  # type: ignore[import-untyped]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the AMESH induced-pod-kill MVP soak")
    parser.add_argument("--api-url", default="http://127.0.0.1:18080")
    parser.add_argument("--token", required=True)
    cluster = parser.add_mutually_exclusive_group(required=True)
    cluster.add_argument("--kube-context")
    cluster.add_argument("--in-cluster", action="store_true")
    parser.add_argument("--namespace", default="amesh-system")
    parser.add_argument("--duration-seconds", type=float, default=24 * 60 * 60)
    parser.add_argument("--task-seconds", type=int, default=90)
    parser.add_argument("--server-kill-every", type=int, default=10)
    parser.add_argument("--worker-kill-every", type=int, default=20)
    parser.add_argument("--worker-kill-delay", type=float, default=4)
    parser.add_argument("--between-cycles", type=float, default=2)
    parser.add_argument("--report", type=Path, default=Path("data/mvp-soak-report.json"))
    return parser


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def soak_flow(task_seconds: int, flow_id: str) -> bytes:
    document = {
        "id": flow_id,
        "namespace": "mvp.soak",
        "inputs": [{"id": "cycle", "type": "string", "required": True}],
        "tasks": [
            {
                "id": "shell",
                "type": "core.shell",
                "image": "busybox:1.37.0",
                "command": ["sh", "-c", f'sleep {task_seconds}; printf "%s" "$SOAK_ID"'],
                "environment": {"SOAK_ID": "{{ inputs.cycle }}"},
                "resources": {"cpu": "10m", "memory": "16Mi"},
                "timeoutSeconds": task_seconds * 3,
            }
        ],
    }
    return yaml.safe_dump(document, sort_keys=False).encode()


async def wait_for_api(api: httpx.AsyncClient, timeout_seconds: float = 120) -> None:
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        try:
            if (await api.get("/health", timeout=2)).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        await asyncio.sleep(0.5)
    raise TimeoutError("AMESH API did not become healthy")


async def execution_ids(api: httpx.AsyncClient) -> set[str]:
    response = await api.get("/api/v1/executions", params={"limit": 1000})
    response.raise_for_status()
    return {str(item["execution_id"]) for item in response.json()}


async def wait_for_new_execution(
    api: httpx.AsyncClient,
    before: set[str],
    timeout_seconds: float = 30,
) -> str:
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        with suppress(httpx.HTTPError):
            created = await execution_ids(api) - before
            if len(created) == 1:
                return created.pop()
            if len(created) > 1:
                raise RuntimeError(f"multiple executions appeared in one soak cycle: {created}")
        await asyncio.sleep(0.25)
    raise TimeoutError("soak execution was not persisted")


async def wait_for_task_pod(
    core: client.CoreV1Api,
    namespace: str,
    *,
    excluded_name: str | None = None,
    timeout_seconds: float = 120,
) -> str:
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        pods = await core.list_namespaced_pod(
            namespace,
            label_selector="app.kubernetes.io/name=amesh-task",
        )
        for pod in pods.items:
            name = str(pod.metadata.name)
            if pod.status.phase == "Running" and name != excluded_name:
                return name
        await asyncio.sleep(0.25)
    raise TimeoutError("task Job did not produce a running pod")


async def kill_component_pod(
    core: client.CoreV1Api,
    namespace: str,
    component: str,
) -> str:
    pods = await core.list_namespaced_pod(
        namespace,
        label_selector=f"app.kubernetes.io/component={component}",
    )
    running = [pod for pod in pods.items if pod.status.phase == "Running"]
    if not running:
        raise RuntimeError(f"no running {component} pod exists")
    name = str(running[0].metadata.name)
    await core.delete_namespaced_pod(
        name,
        namespace,
        body=client.V1DeleteOptions(grace_period_seconds=0, propagation_policy="Foreground"),
    )
    return name


async def wait_for_success(
    api: httpx.AsyncClient,
    execution_id: str,
    cycle_id: str,
    timeout_seconds: float,
) -> None:
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        try:
            response = await api.get(f"/api/v1/executions/{execution_id}")
            if response.status_code == 200:
                payload = response.json()
                state = payload["execution"]["state"]
                if state == "SUCCESS":
                    task_runs = payload["taskRuns"]
                    if len(task_runs) != 1:
                        raise RuntimeError(f"execution {execution_id} has duplicate task runs")
                    task_run = task_runs[0]
                    if task_run["current_attempt"] != 1:
                        raise RuntimeError(f"execution {execution_id} created duplicate attempts")
                    if task_run["result"]["stdout"] != cycle_id:
                        raise RuntimeError(f"execution {execution_id} returned unexpected output")
                    return
                if state != "RUNNING":
                    raise RuntimeError(f"execution {execution_id} ended in {state}")
        except httpx.HTTPError:
            pass
        await asyncio.sleep(0.5)
    raise TimeoutError(f"execution {execution_id} did not complete")


async def run_soak(args: argparse.Namespace) -> dict[str, Any]:
    if args.duration_seconds <= 0 or args.task_seconds < 1:
        raise ValueError("duration and task time must be positive")
    if args.in_cluster:
        config.load_incluster_config()
    else:
        await config.load_kube_config(context=args.kube_context)
    api_client = client.ApiClient()
    core = client.CoreV1Api(api_client)
    run_id = uuid4().hex[:12]
    flow_id = f"mvp_soak_{run_id}"
    report: dict[str, Any] = {
        "status": "running",
        "runId": run_id,
        "startedAt": utc_now(),
        "durationSeconds": args.duration_seconds,
        "completedCycles": 0,
        "taskPodKills": 0,
        "serverPodKills": 0,
        "workerPodKills": 0,
        "executionIds": [],
        "failures": [],
    }
    write_report(args.report, report)
    headers = {"authorization": f"Bearer {args.token}"}
    timeout = httpx.Timeout(args.task_seconds * 4 + 120)
    started = monotonic()
    try:
        async with httpx.AsyncClient(
            base_url=args.api_url, headers=headers, timeout=timeout
        ) as api:
            await wait_for_api(api)
            applied = await api.put(
                "/api/v1/flows",
                content=soak_flow(args.task_seconds, flow_id),
                headers={**headers, "content-type": "application/yaml"},
            )
            applied.raise_for_status()
            cycle = 0
            while monotonic() - started < args.duration_seconds:
                cycle += 1
                cycle_id = f"{run_id}-soak-{cycle:05d}"
                before = await execution_ids(api)
                run_request = asyncio.create_task(
                    api.post(
                        "/api/v1/executions",
                        json={
                            "namespace": "mvp.soak",
                            "flowId": flow_id,
                            "runner": "kubernetes",
                            "inputs": {"cycle": cycle_id},
                            "idempotencyKey": cycle_id,
                        },
                    )
                )
                execution_id = await wait_for_new_execution(api, before)
                report["executionIds"].append(execution_id)
                original_task_pod = await wait_for_task_pod(core, args.namespace)
                await core.delete_namespaced_pod(
                    original_task_pod,
                    args.namespace,
                    body=client.V1DeleteOptions(
                        grace_period_seconds=0,
                        propagation_policy="Foreground",
                    ),
                )
                report["taskPodKills"] += 1
                await wait_for_task_pod(
                    core,
                    args.namespace,
                    excluded_name=original_task_pod,
                )

                if args.server_kill_every > 0 and cycle % args.server_kill_every == 0:
                    await kill_component_pod(core, args.namespace, "server")
                    report["serverPodKills"] += 1
                    if args.worker_kill_every > 0 and cycle % args.worker_kill_every == 0:
                        await asyncio.sleep(args.worker_kill_delay)
                        await kill_component_pod(core, args.namespace, "worker")
                        report["workerPodKills"] += 1
                    await wait_for_api(api)

                with suppress(httpx.HTTPError, asyncio.CancelledError):
                    response = await run_request
                    response.raise_for_status()
                await wait_for_success(
                    api,
                    execution_id,
                    cycle_id,
                    timeout_seconds=args.task_seconds * 4 + 120,
                )
                report["completedCycles"] = cycle
                report["lastCompletedAt"] = utc_now()
                write_report(args.report, report)
                print(
                    json.dumps(
                        {
                            "cycle": cycle,
                            "executionId": execution_id,
                            "status": "success",
                            "taskPodKills": report["taskPodKills"],
                            "serverPodKills": report["serverPodKills"],
                            "workerPodKills": report["workerPodKills"],
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
                await asyncio.sleep(args.between_cycles)
        report["status"] = "pass"
        report["finishedAt"] = utc_now()
        report["elapsedSeconds"] = monotonic() - started
        write_report(args.report, report)
        return report
    except Exception as exc:
        report["status"] = "fail"
        report["finishedAt"] = utc_now()
        report["elapsedSeconds"] = monotonic() - started
        report["failures"].append(str(exc))
        write_report(args.report, report)
        raise
    finally:
        await api_client.close()


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = asyncio.run(run_soak(args))
    except (ApiException, httpx.HTTPError, OSError, RuntimeError, TimeoutError, ValueError) as exc:
        print(f"soak failed: {exc}")
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
