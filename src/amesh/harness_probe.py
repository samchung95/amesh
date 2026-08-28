"""Run a secret-free Pi harness smoke test from a built AMESH image.

The probe uses the production Python adapter and a deterministic in-process model
gateway. It never contacts a provider, persists session state, or prints model
payloads. This keeps the image check useful in CI without requiring credentials.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

from amesh.adapters.agent_session_registry import create_agent_session_harness
from amesh.ports import AgentSessionHarnessRequest, AgentSessionModelCall

_PI_VERSION = "0.84.3"
_PI_PACKAGES = ("@earendil-works/pi-agent-core", "@earendil-works/pi-ai")


class _ProbeGateway:
    async def invoke(self, call: AgentSessionModelCall) -> dict[str, Any]:
        return {
            "structuredOutput": {
                "action": "final",
                "tool": "none",
                "arguments": None,
                "output": {"answer": "production-image-probe"},
                "rationale": "Deterministic image smoke.",
            },
            "model": call.model,
            "usageNormalized": {
                "state": "unpriced",
                "inputTokens": 1,
                "outputTokens": 1,
                "totalTokens": 2,
            },
        }


def _root() -> Path:
    candidates = (Path.cwd(), Path("/app"), Path(__file__).resolve().parents[2])
    for candidate in candidates:
        if (candidate / "harnesses" / "pi").is_dir():
            return candidate
    raise RuntimeError("AMESH application root with the Pi worker was not found")


def _package_versions(root: Path) -> dict[str, str]:
    versions: dict[str, str] = {}
    for package in _PI_PACKAGES:
        package_json = root / "harnesses" / "pi" / "node_modules" / Path(package) / "package.json"
        payload = json.loads(package_json.read_text(encoding="utf-8"))
        version = payload.get("version")
        if version != _PI_VERSION:
            raise RuntimeError(f"{package} version is not pinned to {_PI_VERSION}")
        versions[package] = version
    return versions


async def _run(worker: Path) -> dict[str, Any]:
    call = AgentSessionModelCall(
        routeId="image-probe",
        provider={"adapter": "probe"},
        model="amesh/image-probe",
        messages=({"role": "user", "content": "Run the image probe."},),
        outputSchema={"type": "object"},
        maxTotalTokens=100,
        maxCompletionTokens=50,
        maxCostUsd=Decimal("0"),
        timeoutSeconds=10,
        invocationKey="harness-probe:image:1",
    )
    request = AgentSessionHarnessRequest(
        sessionId=uuid4(),
        turn=1,
        envelopeDigest="sha256:" + "0" * 64,
        modelCall=call,
    )
    adapter = create_agent_session_harness("pi", ("node", str(worker)))
    result = await adapter.next_action(request, model_gateway=_ProbeGateway())
    if result.adapter_version != _PI_VERSION:
        raise RuntimeError("Pi adapter version does not match the pinned worker")
    if result.model_output.get("structuredOutput", {}).get("output", {}).get("answer") != (
        "production-image-probe"
    ):
        raise RuntimeError("Pi worker did not return the deterministic probe result")
    return {
        "adapter": result.adapter,
        "adapterVersion": result.adapter_version,
        "workerProtocol": result.metadata.get("workerProtocol"),
        "modelGateway": result.metadata.get("modelGateway"),
    }


async def _probe(worker: Path) -> dict[str, Any]:
    package_versions = _package_versions(_root())
    result = await _run(worker)
    return {"passed": True, "packages": package_versions, **result}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe the Pi harness in the AMESH production image"
    )
    parser.add_argument(
        "--worker",
        type=Path,
        default=_root() / "harnesses" / "pi" / "src" / "worker.mjs",
        help="path to the installed Pi worker",
    )
    arguments = parser.parse_args()
    try:
        report = asyncio.run(_probe(arguments.worker))
    except Exception as exc:  # pragma: no cover - exercised by image failures
        report = {"passed": False, "error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(report, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
