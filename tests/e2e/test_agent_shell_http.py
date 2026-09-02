from __future__ import annotations

import asyncio
import json
import os
import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest
from kubernetes.aio import client, config
from kubernetes.client.exceptions import ApiException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.app import app, get_repository
from amesh.config import Settings, get_settings

KIND_CONTEXT = os.getenv("AMESH_KIND_CONTEXT")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    KIND_CONTEXT is None or OPENROUTER_API_KEY is None,
    reason="kind and OpenRouter settings are required",
)


class CallbackHandler(BaseHTTPRequestHandler):
    received: queue.Queue[dict[str, object]] = queue.Queue()

    def do_POST(self) -> None:
        length = int(self.headers.get("content-length", "0"))
        payload = json.loads(self.rfile.read(length))
        self.received.put(payload)
        encoded = json.dumps({"accepted": True}).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        del format, args


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


def test_api_runs_openrouter_shell_http_demo_on_kind(migrated_test_database_url: str) -> None:
    async def scenario(callback_url: str) -> None:
        if KIND_CONTEXT is None:
            raise RuntimeError("kind settings are required")
        task_namespace = f"amesh-demo-{uuid4().hex[:10]}"
        flow_namespace = f"tests.demo.{uuid4().hex}"
        await config.load_kube_config(context=KIND_CONTEXT)
        kubernetes_client = client.ApiClient()
        core = client.CoreV1Api(kubernetes_client)
        await core.create_namespace({"metadata": {"name": task_namespace}})

        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        settings = Settings(
            database_url=migrated_test_database_url,
            amesh_admin_token="test-token",
            kubernetes_context=KIND_CONTEXT,
            kubernetes_task_namespace=task_namespace,
            core_http_allowed_private_hosts=("127.0.0.1",),
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_settings] = lambda: settings
        source = (ROOT / "examples" / "agent-shell-http.yaml").read_text(encoding="utf-8")
        source = source.replace("namespace: examples.mvp", f"namespace: {flow_namespace}")
        execution_id: UUID | None = None
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
                timeout=180,
            ) as api_client:
                applied = await api_client.put(
                    "/api/v1/flows",
                    content=source,
                    headers={
                        "authorization": "Bearer test-token",
                        "content-type": "application/yaml",
                    },
                )
                assert applied.status_code == 200
                executed = await api_client.post(
                    "/api/v1/executions",
                    headers={"authorization": "Bearer test-token"},
                    json={
                        "namespace": flow_namespace,
                        "flowId": "agent_shell_http",
                        "inputs": {
                            "topic": "durable workflow recovery",
                            "callbackUrl": callback_url,
                        },
                        "runner": "kubernetes",
                    },
                )
                assert executed.status_code == 200, executed.text
                payload = executed.json()
                execution_id = UUID(payload["execution"]["execution_id"])
                assert payload["execution"]["state"] == "SUCCESS"
                results = {item["task_id"]: item["result"] for item in payload["taskRuns"]}
                assert results["plan"]["model"]
                assert results["shell"]["exitCode"] == 0
                assert results["publish"]["statusCode"] == 200
                callback = CallbackHandler.received.get(timeout=2)
                assert callback == {"message": results["shell"]["stdout"]}
        finally:
            app.dependency_overrides.clear()
            if execution_id is not None:
                await cleanup_execution(engine, execution_id)
            await engine.dispose()
            try:
                await core.delete_namespace(task_namespace)
            except ApiException as exc:
                if exc.status != 404:
                    raise
            await kubernetes_client.close()

    server = ThreadingHTTPServer(("127.0.0.1", 0), CallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        address, port = server.server_address
        asyncio.run(scenario(f"http://{address}:{port}/callback"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
