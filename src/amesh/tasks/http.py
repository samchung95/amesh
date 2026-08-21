from __future__ import annotations

from typing import Any

import httpx

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext, TaskHandler


def core_http_handler(client: httpx.AsyncClient | None = None) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
        del context
        extra = task.model_extra or {}
        url = extra.get("url")
        if not isinstance(url, str) or not url:
            raise ValueError(f"task {task.id!r} requires url")
        method = str(extra.get("method", "GET")).upper()
        headers = extra.get("headers", {})
        if not isinstance(headers, dict):
            raise ValueError(f"task {task.id!r} headers must be an object")
        body = extra.get("body")
        timeout = task.timeout_seconds or 30

        async def request(active_client: httpx.AsyncClient) -> dict[str, Any]:
            response = await active_client.request(
                method,
                url,
                headers={str(key): str(value) for key, value in headers.items()},
                json=body,
                timeout=timeout,
            )
            response.raise_for_status()
            result: dict[str, Any] = {
                "statusCode": response.status_code,
                "body": response.text,
                "headers": dict(response.headers),
            }
            if response.headers.get("content-type", "").startswith("application/json"):
                result["json"] = response.json()
            return result

        if client is not None:
            return await request(client)
        async with httpx.AsyncClient() as active_client:
            return await request(active_client)

    return run
