from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sdks" / "api" / "python"))
TEMPLATE = ROOT / "scripts" / "sdk_templates" / "python" / "execution.py"
SPEC = importlib.util.spec_from_file_location("amesh_template_execution", TEMPLATE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load Python SDK template")
TEMPLATE_MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = TEMPLATE_MODULE
SPEC.loader.exec_module(TEMPLATE_MODULE)


class FakeTransport:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.request: dict[str, Any] | None = None

    def send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> Any:
        self.request = {
            "method": method,
            "url": url,
            "headers": headers,
            "body": body,
            "timeout": timeout_seconds,
        }
        return self.response


def test_python_sdk_template_retrieves_and_verifies_bounded_evidence() -> None:
    response = TEMPLATE_MODULE.HttpResponse(
        200,
        {},
        json.dumps(
            {
                "schemaVersion": "1.0",
                "executionId": "execution-1",
                "bundleDigest": "sha256:" + "a" * 64,
                "section": "trace",
                "items": [],
                "nextCursor": "10",
                "limit": 10,
                "total": 20,
            }
        ).encode(),
    )
    transport = FakeTransport(response)
    client = TEMPLATE_MODULE.ExecutionClient("https://amesh.test", "token", transport=transport)

    page = client.evidence("execution-1", cursor="5", limit=10, verify=True)

    assert page["verified"] is True
    assert transport.request is not None
    assert transport.request["method"] == "GET"
    assert "section=trace" in transport.request["url"]
    assert "cursor=5" in transport.request["url"]
    assert "limit=10" in transport.request["url"]
