from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx
import yaml

from amesh import __version__
from amesh.config import Settings
from amesh.dsl import FlowDocumentError, validate_flow_document
from amesh.ports import StorageMigrationCheckpoint
from amesh.storage.factory import build_object_store


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="amesh")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--api-url",
        default=os.getenv("AMESH_API_URL", "http://127.0.0.1:8000"),
    )
    parser.add_argument("--token", default=os.getenv("AMESH_ADMIN_TOKEN"))
    parser.add_argument("--tenant", default=os.getenv("AMESH_TENANT", "default"))
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate = subcommands.add_parser("validate", help="Validate a flow YAML or JSON file")
    validate.add_argument("path", type=Path)
    validate.add_argument("--json", action="store_true", dest="as_json")

    apply = subcommands.add_parser("apply", help="Apply a validated flow through the API")
    apply.add_argument("path", type=Path)

    subcommands.add_parser("flows", help="List applied flows")

    executions = subcommands.add_parser("executions", help="List executions")
    executions.add_argument("--limit", type=int, default=100)

    run = subcommands.add_parser("run", help="Run an applied flow and wait for completion")
    run.add_argument("namespace")
    run.add_argument("flow_id")
    run.add_argument("--runner", choices=("local", "kubernetes"), default="local")
    run.add_argument("--input", action="append", default=[])
    run.add_argument("--idempotency-key")

    execution = subcommands.add_parser("execution", help="Get one execution")
    execution.add_argument("execution_id")

    logs = subcommands.add_parser("logs", help="Get task outputs for one execution")
    logs.add_argument("execution_id")

    webhook = subcommands.add_parser("webhook", help="Trigger an applied webhook flow")
    webhook.add_argument("namespace")
    webhook.add_argument("flow_id")
    webhook.add_argument("trigger_id")
    webhook.add_argument("--runner", choices=("local", "kubernetes"), default="local")
    webhook.add_argument("--input", action="append", default=[])

    storage = subcommands.add_parser("storage", help="Validate or migrate object storage")
    storage_commands = storage.add_subparsers(dest="storage_command", required=True)
    storage_validate = storage_commands.add_parser(
        "validate", help="Verify the configured tenant storage inventory"
    )
    storage_validate.add_argument("--metadata-only", action="store_true")
    storage_migrate = storage_commands.add_parser(
        "migrate", help="Copy the configured tenant storage to another backend"
    )
    storage_migrate.add_argument("destination_config", type=Path)
    storage_migrate.add_argument("--checkpoint", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        path: Path = args.path
        try:
            result = validate_flow_document(path.read_bytes())
        except (OSError, FlowDocumentError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if args.as_json:
            print(result.model_dump_json(indent=2, by_alias=True))
        elif result.valid:
            print(f"valid: {path} ({result.semantic_hash})")
        else:
            for issue in result.issues:
                print(f"{issue.severity}: {issue.path}: {issue.code}: {issue.message}")
        return 0 if result.valid else 1
    if args.command == "storage":
        try:
            if args.storage_command == "validate":
                report = asyncio.run(
                    build_object_store(Settings()).validate_inventory(
                        args.tenant,
                        verify_content=not args.metadata_only,
                    )
                )
                print(report.model_dump_json(indent=2))
                return 0 if not report.corrupt else 1
            destination_settings = Settings.model_validate(
                json.loads(args.destination_config.read_text(encoding="utf-8"))
            )
            checkpoint = _load_storage_checkpoint(args.checkpoint)
            migration_checkpoint = asyncio.run(
                build_object_store(Settings()).migrate_to(
                    build_object_store(destination_settings),
                    args.tenant,
                    checkpoint=checkpoint,
                    write_checkpoint=lambda value: _write_storage_checkpoint(
                        args.checkpoint, value
                    ),
                )
            )
            print(migration_checkpoint.model_dump_json(indent=2))
            return 0
        except (OSError, ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
    try:
        with httpx.Client(
            base_url=args.api_url,
            headers=_request_headers(args.token, args.tenant),
            timeout=120,
        ) as client:
            if args.command == "apply":
                response = client.put(
                    "/api/v1/flows",
                    content=args.path.read_bytes(),
                    headers={"content-type": "application/yaml"},
                )
            elif args.command == "flows":
                response = client.get("/api/v1/flows")
            elif args.command == "executions":
                response = client.get("/api/v1/executions", params={"limit": args.limit})
            elif args.command == "run":
                response = client.post(
                    "/api/v1/executions",
                    json={
                        "namespace": args.namespace,
                        "flowId": args.flow_id,
                        "inputs": _parse_inputs(args.input),
                        "runner": args.runner,
                        "idempotencyKey": args.idempotency_key,
                    },
                )
            elif args.command == "execution":
                response = client.get(f"/api/v1/executions/{args.execution_id}")
            elif args.command == "logs":
                response = client.get(f"/api/v1/executions/{args.execution_id}/logs")
            elif args.command == "webhook":
                response = client.post(
                    f"/api/v1/webhooks/{args.namespace}/{args.flow_id}/{args.trigger_id}",
                    params={"runner": args.runner},
                    json=_parse_inputs(args.input),
                )
            else:
                return 2
        if response.is_error:
            print(f"API error {response.status_code}: {response.text}", file=sys.stderr)
            return 2
        print(json.dumps(response.json(), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, httpx.HTTPError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


def _request_headers(token: str | None, tenant: str) -> dict[str, str]:
    headers = {"x-amesh-tenant": tenant}
    if token:
        headers["authorization"] = f"Bearer {token}"
    return headers


def _parse_inputs(values: Sequence[str]) -> dict[str, Any]:
    inputs: dict[str, Any] = {}
    for value in values:
        key, separator, encoded = value.partition("=")
        if not separator or not key:
            raise ValueError(f"input {value!r} must use key=value")
        inputs[key] = yaml.safe_load(encoded)
    return inputs


def _load_storage_checkpoint(path: Path) -> StorageMigrationCheckpoint | None:
    if not path.exists():
        return None
    return StorageMigrationCheckpoint.model_validate_json(path.read_text(encoding="utf-8"))


async def _write_storage_checkpoint(
    path: Path,
    checkpoint: StorageMigrationCheckpoint,
) -> None:
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(checkpoint.model_dump_json(indent=2), encoding="utf-8")
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())
