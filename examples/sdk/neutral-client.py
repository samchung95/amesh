"""Launch and inspect an AMESH workflow through the client-neutral contract."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.request import Request, urlopen
from uuid import uuid4

from amesh_client.execution import ExecutionClient


def _get_json(endpoint: str, path: str, token: str, tenant: str) -> dict[str, Any]:
    request = Request(
        endpoint.rstrip("/") + path,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "X-Amesh-Tenant": tenant,
        },
    )
    with urlopen(request, timeout=30) as response:
        value = json.load(response)
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} did not return a JSON object")
    return value


def main() -> None:
    endpoint = os.environ["AMESH_ENDPOINT"].rstrip("/")
    token = os.environ["AMESH_TOKEN"]
    tenant = os.getenv("AMESH_TENANT", "default")
    namespace = os.getenv("AMESH_NAMESPACE", "examples.getting_started")
    flow_id = os.getenv("AMESH_FLOW", "hello_world")
    correlation_id = os.getenv("AMESH_CORRELATION_ID", f"neutral-client-{uuid4()}")
    idempotency_key = os.getenv("AMESH_IDEMPOTENCY_KEY", f"neutral-launch-{uuid4()}")

    profile = _get_json(endpoint, "/api/v1/orchestration/profile", token, tenant)
    if profile.get("schemaVersion") != "amesh.external-orchestration/v1":
        raise RuntimeError("live deployment does not publish the expected orchestration profile")
    openapi = _get_json(endpoint, "/openapi.json", token, tenant)
    paths = openapi.get("paths")
    if not isinstance(paths, dict):
        raise RuntimeError("live OpenAPI document has no paths map")
    for operation in profile.get("operations", []):
        if not isinstance(operation, dict):
            raise RuntimeError("live orchestration profile contains an invalid operation")
        path = str(operation["path"]).split("?", maxsplit=1)[0]
        published = paths.get(path)
        method = str(operation["method"]).lower()
        if not isinstance(published, dict) or method not in published:
            raise RuntimeError(f"profile operation {operation['name']} is absent from OpenAPI")

    client = ExecutionClient(endpoint, token, tenant)
    launched = client.launch(
        namespace,
        flow_id,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
    )
    execution_id = str(launched.execution.execution_id)
    repeated = client.launch(
        namespace,
        flow_id,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
    )
    if repeated.execution.execution_id != launched.execution.execution_id:
        raise RuntimeError("repeated idempotent launch created a second logical execution")
    completed = client.wait(execution_id, timeout_seconds=300, poll_seconds=1)
    print(
        json.dumps(
            {
                "executionId": execution_id,
                "state": completed.execution.state.value,
                "correlationId": correlation_id,
                "idempotencyKey": idempotency_key,
                "profileVersion": profile["schemaVersion"],
                "operationsVerified": len(profile["operations"]),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
