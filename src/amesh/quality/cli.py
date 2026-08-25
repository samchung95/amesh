"""Provider-neutral CLI composition helpers for differential REST operations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
import yaml

from .differential import ComparisonReport, DifferentialSpec

EXIT_SUCCESS = 0
EXIT_DIFFERENCE = 1
EXIT_ERROR = 2


def add_differential_commands(subcommands: Any) -> None:
    """Add ``differential run`` and ``differential report`` to an existing CLI parser."""

    differential = subcommands.add_parser(
        "differential", help="Compare exact configurations in shadow mode"
    )
    commands = differential.add_subparsers(dest="differential_command", required=True)
    run = commands.add_parser("run", help="Run a frozen differential specification")
    run.add_argument("path", type=Path, help="JSON or YAML differential specification")
    report = commands.add_parser("report", help="Retrieve one differential report")
    report.add_argument("namespace")
    report.add_argument("idempotency_key")


def differential_request(
    client: httpx.Client,
    args: argparse.Namespace,
    *,
    tenant_id: str,
) -> httpx.Response:
    """Issue one authenticated, tenant-bound differential REST operation."""

    if args.differential_command == "run":
        spec = load_differential_spec(args.path)
        if spec.tenant_id != tenant_id:
            raise ValueError("differential specification tenant does not match CLI tenant")
        return client.post(
            f"/api/v1/namespaces/{quote(spec.namespace, safe='')}/differentials",
            headers={
                "X-Amesh-Tenant": tenant_id,
                "Idempotency-Key": spec.idempotency_key,
            },
            json=spec.model_dump(mode="json", by_alias=True),
        )
    if args.differential_command == "report":
        return client.get(
            f"/api/v1/namespaces/{quote(args.namespace, safe='')}/differentials/"
            f"{quote(args.idempotency_key, safe='')}",
            headers={"X-Amesh-Tenant": tenant_id},
        )
    raise ValueError(f"unsupported differential command: {args.differential_command!r}")


def load_differential_spec(path: Path) -> DifferentialSpec:
    """Load and validate one exact JSON/YAML differential specification."""

    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"unable to read differential specification: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("differential specification must be a JSON/YAML object")
    return DifferentialSpec.model_validate(value)


def differential_result(response: httpx.Response) -> tuple[int, dict[str, Any] | str]:
    """Convert an API response to the CLI's difference/error exit convention."""

    if response.is_error:
        try:
            body: dict[str, Any] | str = response.json()
        except json.JSONDecodeError:
            body = response.text
        return EXIT_ERROR, body
    try:
        body = response.json()
    except json.JSONDecodeError as exc:
        raise ValueError("differential API returned a non-JSON response") from exc
    if not isinstance(body, dict):
        raise ValueError("differential API returned a non-object response")
    report = ComparisonReport.model_validate(body)
    return (EXIT_SUCCESS if report.passed else EXIT_DIFFERENCE), body


__all__ = [
    "EXIT_DIFFERENCE",
    "EXIT_ERROR",
    "EXIT_SUCCESS",
    "add_differential_commands",
    "differential_request",
    "differential_result",
    "load_differential_spec",
]
