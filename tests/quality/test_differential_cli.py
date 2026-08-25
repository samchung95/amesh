from __future__ import annotations

import argparse
from pathlib import Path

import httpx

from amesh.cli import build_parser
from amesh.quality import (
    ConfigurationPin,
    DifferentialService,
    DifferentialSpec,
    RunObservation,
    ShadowRunContext,
    add_differential_commands,
    differential_request,
    differential_result,
    load_differential_spec,
)


def _spec() -> DifferentialSpec:
    return DifferentialSpec(
        tenantId="tenant-a",
        namespace="quality",
        left={"key": "flow", "revision": 1, "digest": "sha256:" + "1" * 64},
        right={"key": "flow", "revision": 2, "digest": "sha256:" + "2" * 64},
        inputs={"value": 1},
        idempotencyKey="request-1",
    )


def test_cli_parser_loads_spec_and_sends_tenant_idempotency_headers(tmp_path: Path) -> None:
    path = tmp_path / "differential.yaml"
    path.write_text(_spec().model_dump_json(by_alias=True), encoding="utf-8")
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)
    add_differential_commands(subcommands)
    args = parser.parse_args(["differential", "run", str(path)])
    assert load_differential_spec(path).input_digest == _spec().input_digest

    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["tenant"] = request.headers["X-Amesh-Tenant"]
        seen["idempotency"] = request.headers["Idempotency-Key"]
        return httpx.Response(200, json={"ok": True})

    with httpx.Client(
        transport=httpx.MockTransport(handler), base_url="http://amesh.test"
    ) as client:
        response = differential_request(client, args, tenant_id="tenant-a")
    assert response.status_code == 200
    assert seen == {
        "path": "/api/v1/namespaces/quality/differentials",
        "tenant": "tenant-a",
        "idempotency": "request-1",
    }


def test_cli_reports_difference_exit_code_without_promoting_candidate() -> None:
    service = DifferentialService()

    def execute(
        configuration: ConfigurationPin, inputs: object, context: ShadowRunContext
    ) -> RunObservation:
        del inputs, context
        return RunObservation(output={"value": configuration.revision})

    report = service.run(_spec(), execute)
    response = httpx.Response(200, json=report.model_dump(mode="json", by_alias=True))
    exit_code, body = differential_result(response)
    assert exit_code == 1
    assert body["deterministicFailures"]


def test_application_cli_registers_differential_commands() -> None:
    args = build_parser().parse_args(["differential", "report", "quality", "request-1"])
    assert args.command == "differential"
    assert args.differential_command == "report"
