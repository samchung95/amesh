from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
import yaml
from pydantic import SecretStr

from amesh import __version__
from amesh.adapters.postgres import (
    PostgresAuthenticationRepository,
    PostgresExecutionRepository,
    PostgresTenantRepository,
)
from amesh.authentication import AuthenticationService
from amesh.config import Settings
from amesh.database import create_database_engine
from amesh.dsl import FlowDocumentError, validate_flow_document
from amesh.ports import StorageMigrationCheckpoint
from amesh.recovery import RecoveryService
from amesh.storage.factory import build_object_store
from amesh.tenancy import TenantService
from amesh.tenant_transfer import TenantTransferBundle, TenantTransferService


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

    plugins = subcommands.add_parser("plugins", help="Inspect and manage plugin packages")
    plugin_commands = plugins.add_subparsers(dest="plugin_command", required=True)
    plugin_commands.add_parser("list", help="List the active plugin catalog")
    plugin_commands.add_parser("refresh", help="Refresh configured plugin sources")
    plugin_install = plugin_commands.add_parser(
        "install", help="Install a verified offline plugin bundle"
    )
    plugin_install.add_argument("path", type=Path)
    plugin_install.add_argument("--sha256", required=True)

    namespace = subcommands.add_parser("namespace", help="Manage namespace resources")
    namespace_commands = namespace.add_subparsers(dest="namespace_command", required=True)
    files = namespace_commands.add_parser("files", help="Manage namespace files")
    file_commands = files.add_subparsers(dest="file_command", required=True)
    files_list = file_commands.add_parser("list", help="List namespace files")
    files_list.add_argument("namespace")
    files_list.add_argument("--local-only", action="store_true")
    files_upload = file_commands.add_parser("upload", help="Upload a namespace file")
    files_upload.add_argument("namespace")
    files_upload.add_argument("remote_path")
    files_upload.add_argument("local_path", type=Path)
    files_upload.add_argument("--content-type", default="application/octet-stream")
    files_upload.add_argument("--expected-version", type=int)
    files_download = file_commands.add_parser("download", help="Download a namespace file")
    files_download.add_argument("namespace")
    files_download.add_argument("remote_path")
    files_download.add_argument("local_path", type=Path)
    files_download.add_argument("--version", type=int)
    files_move = file_commands.add_parser("move", help="Move a namespace file")
    files_move.add_argument("namespace")
    files_move.add_argument("remote_path")
    files_move.add_argument("destination_path")
    files_move.add_argument("--expected-version", type=int)
    files_versions = file_commands.add_parser("versions", help="List file versions")
    files_versions.add_argument("namespace")
    files_versions.add_argument("remote_path")
    files_delete = file_commands.add_parser("delete", help="Delete a namespace file")
    files_delete.add_argument("namespace")
    files_delete.add_argument("remote_path")
    files_delete.add_argument("--expected-version", type=int)

    key_values = namespace_commands.add_parser("kv", help="Manage typed key-values")
    key_value_commands = key_values.add_subparsers(dest="kv_command", required=True)
    kv_list = key_value_commands.add_parser("list", help="List key-values")
    kv_list.add_argument("namespace")
    kv_get = key_value_commands.add_parser("get", help="Read one key-value")
    kv_get.add_argument("namespace")
    kv_get.add_argument("key")
    kv_set = key_value_commands.add_parser("set", help="Set one typed key-value")
    kv_set.add_argument("namespace")
    kv_set.add_argument("key")
    kv_set.add_argument(
        "--type",
        required=True,
        choices=("STRING", "NUMBER", "BOOLEAN", "DATETIME", "DATE", "DURATION", "JSON"),
    )
    kv_set.add_argument("--value", required=True)
    kv_set.add_argument("--expires-at")
    kv_set.add_argument("--expected-version", type=int)
    kv_delete = key_value_commands.add_parser("delete", help="Delete one key-value")
    kv_delete.add_argument("namespace")
    kv_delete.add_argument("key")
    kv_delete.add_argument("--expected-version", type=int)
    kv_changes = key_value_commands.add_parser("changes", help="Poll key-value changes")
    kv_changes.add_argument("namespace")
    kv_changes.add_argument("--after", type=int, default=0)
    kv_changes.add_argument("--limit", type=int, default=100)

    secret_bindings = namespace_commands.add_parser(
        "secrets", help="Manage runtime secret references"
    )
    secret_commands = secret_bindings.add_subparsers(dest="secret_command", required=True)
    secrets_list = secret_commands.add_parser("list", help="List secret references")
    secrets_list.add_argument("namespace")
    secrets_list.add_argument("--local-only", action="store_true")
    secrets_bind = secret_commands.add_parser("bind", help="Bind a key to an environment name")
    secrets_bind.add_argument("namespace")
    secrets_bind.add_argument("key")
    secrets_bind.add_argument("environment_name")
    secrets_bind.add_argument("--expected-version", type=int)
    secrets_delete = secret_commands.add_parser("delete", help="Delete a secret reference")
    secrets_delete.add_argument("namespace")
    secrets_delete.add_argument("key")
    secrets_delete.add_argument("--expected-version", type=int)

    resources = namespace_commands.add_parser("resources", help="Promote namespace resources")
    resource_commands = resources.add_subparsers(dest="resource_command", required=True)
    resources_export = resource_commands.add_parser("export", help="Export a resource bundle")
    resources_export.add_argument("namespace")
    resources_export.add_argument("path", type=Path)
    resources_import = resource_commands.add_parser("import", help="Import a resource bundle")
    resources_import.add_argument("namespace")
    resources_import.add_argument("path", type=Path)

    auth = subcommands.add_parser("auth", help="Manage interactive authentication")
    auth_commands = auth.add_subparsers(dest="auth_command", required=True)
    bootstrap_admin = auth_commands.add_parser(
        "bootstrap-admin",
        help="Create the first local administrator without a default credential",
    )
    bootstrap_admin.add_argument("--handle", required=True)
    bootstrap_admin.add_argument("--display-name", required=True)
    bootstrap_admin.add_argument(
        "--password-stdin",
        action="store_true",
        help="Read the password from one stdin line instead of an interactive prompt",
    )

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

    recovery = subcommands.add_parser(
        "recovery", help="Create and qualify coordinated recovery points"
    )
    recovery_commands = recovery.add_subparsers(dest="recovery_command", required=True)
    recovery_create = recovery_commands.add_parser("create", help="Create a coordinated backup")
    recovery_create.add_argument("--actor", default="operator:recovery-cli")
    recovery_verify = recovery_commands.add_parser(
        "verify-latest", help="Restore and verify the latest backup in an isolated database"
    )
    recovery_verify.add_argument("--actor", default="operator:recovery-cli")
    recovery_verify.add_argument("--profile", default="v1")
    recovery_verify.add_argument("--scheduled", action="store_true")
    recovery_exercise = recovery_commands.add_parser(
        "exercise", help="Create a backup and immediately run an isolated restore exercise"
    )
    recovery_exercise.add_argument("--actor", default="operator:recovery-cli")
    recovery_exercise.add_argument("--profile", default="v1")
    recovery_exercise.add_argument("--scheduled", action="store_true")

    transfer = subcommands.add_parser(
        "tenant-transfer", help="Export or import a checksum-protected tenant bundle"
    )
    transfer_commands = transfer.add_subparsers(dest="transfer_command", required=True)
    transfer_export = transfer_commands.add_parser("export", help="Export one tenant")
    transfer_export.add_argument("tenant_slug")
    transfer_export.add_argument("path", type=Path)
    transfer_export.add_argument("--actor", default="operator:tenant-transfer")
    transfer_import = transfer_commands.add_parser("import", help="Import into a new tenant slug")
    transfer_import.add_argument("path", type=Path)
    transfer_import.add_argument("target_slug")
    transfer_import.add_argument("--actor", default="operator:tenant-transfer")
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
    if args.command == "auth":
        try:
            password = _read_bootstrap_password(args.password_stdin)
            principal = asyncio.run(
                _bootstrap_local_admin(
                    Settings(),
                    handle=args.handle,
                    display_name=args.display_name,
                    password=password,
                )
            )
            print(
                json.dumps(
                    {
                        "principalId": str(principal.id),
                        "handle": principal.handle,
                        "displayName": principal.display_name,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        except (EOFError, LookupError, ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
    if args.command == "recovery":
        try:
            result = asyncio.run(_run_recovery(args, Settings()))
            print(result.model_dump_json(indent=2))
            state = getattr(result, "state", "PASSED")
            return 0 if state == "PASSED" else 1
        except (OSError, LookupError, ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
    if args.command == "tenant-transfer":
        try:
            result = asyncio.run(_run_tenant_transfer(args, Settings()))
            print(result.model_dump_json(indent=2))
            return 0
        except (OSError, LookupError, ValueError, RuntimeError) as exc:
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
            elif args.command == "plugins":
                if args.plugin_command == "list":
                    response = client.get("/api/v1/plugins")
                elif args.plugin_command == "refresh":
                    response = client.post("/api/v1/plugins/refresh")
                else:
                    digest = args.sha256
                    if not digest.startswith("sha256:"):
                        digest = f"sha256:{digest}"
                    response = client.post(
                        "/api/v1/plugins/install",
                        params={"contentDigest": digest},
                        content=args.path.read_bytes(),
                        headers={"content-type": "application/vnd.amesh.plugin+zip"},
                    )
            elif args.command == "namespace":
                response = _namespace_request(client, args)
            else:
                return 2
        if response.is_error:
            print(f"API error {response.status_code}: {response.text}", file=sys.stderr)
            return 2
        if args.command == "namespace" and _write_namespace_response(response, args):
            return 0
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


def _read_bootstrap_password(from_stdin: bool) -> SecretStr:
    if from_stdin:
        value = sys.stdin.readline().rstrip("\r\n")
        if not value:
            raise ValueError("bootstrap password stdin was empty")
        return SecretStr(value)
    value = getpass.getpass("New local administrator password: ")
    repeated = getpass.getpass("Repeat password: ")
    if value != repeated:
        raise ValueError("passwords do not match")
    return SecretStr(value)


def _parse_inputs(values: Sequence[str]) -> dict[str, Any]:
    inputs: dict[str, Any] = {}
    for value in values:
        key, separator, encoded = value.partition("=")
        if not separator or not key:
            raise ValueError(f"input {value!r} must use key=value")
        inputs[key] = yaml.safe_load(encoded)
    return inputs


def _resource_path(namespace: str, resource: str) -> str:
    return f"/api/v1/namespaces/{quote(namespace, safe='')}/{resource}"


def _namespace_request(client: httpx.Client, args: argparse.Namespace) -> httpx.Response:
    if args.namespace_command == "files":
        root = _resource_path(args.namespace, "files")
        if args.file_command == "list":
            return client.get(root, params={"inherited": not args.local_only})
        path = f"{root}/{quote(args.remote_path, safe='/')}"
        if args.file_command == "upload":
            params = (
                {"expectedVersion": args.expected_version}
                if args.expected_version is not None
                else None
            )
            return client.put(
                path,
                params=params,
                content=args.local_path.read_bytes(),
                headers={"content-type": args.content_type},
            )
        if args.file_command == "download":
            params = {"version": args.version} if args.version is not None else None
            return client.get(path, params=params)
        if args.file_command == "versions":
            return client.get(f"{path}/versions")
        if args.file_command == "move":
            return client.post(
                f"{path}/move",
                json={
                    "destinationPath": args.destination_path,
                    "expectedVersion": args.expected_version,
                },
            )
        params = (
            {"expectedVersion": args.expected_version}
            if args.expected_version is not None
            else None
        )
        return client.delete(path, params=params)
    if args.namespace_command == "kv":
        root = _resource_path(args.namespace, "key-values")
        if args.kv_command == "list":
            return client.get(root)
        if args.kv_command == "changes":
            return client.get(
                f"{root}/changes", params={"after": args.after, "limit": args.limit}
            )
        path = f"{root}/{quote(args.key, safe='')}"
        if args.kv_command == "get":
            return client.get(path)
        if args.kv_command == "set":
            return client.put(
                path,
                json={
                    "type": args.type,
                    "value": yaml.safe_load(args.value),
                    "expiresAt": args.expires_at,
                    "expectedVersion": args.expected_version,
                },
            )
        params = (
            {"expectedVersion": args.expected_version}
            if args.expected_version is not None
            else None
        )
        return client.delete(path, params=params)
    if args.namespace_command == "secrets":
        root = _resource_path(args.namespace, "secret-bindings")
        if args.secret_command == "list":
            return client.get(root, params={"inherited": not args.local_only})
        path = f"{root}/{quote(args.key, safe='')}"
        if args.secret_command == "bind":
            return client.put(
                path,
                json={
                    "provider": "env",
                    "providerReference": args.environment_name,
                    "expectedVersion": args.expected_version,
                },
            )
        params = (
            {"expectedVersion": args.expected_version}
            if args.expected_version is not None
            else None
        )
        return client.delete(path, params=params)
    root = _resource_path(args.namespace, "resource-bundle")
    if args.resource_command == "export":
        return client.get(root)
    return client.post(root, json=json.loads(args.path.read_text(encoding="utf-8")))


def _write_namespace_response(response: httpx.Response, args: argparse.Namespace) -> bool:
    if args.namespace_command == "files" and args.file_command == "download":
        args.local_path.write_bytes(response.content)
        print(f"downloaded {len(response.content)} bytes to {args.local_path}")
        return True
    if args.namespace_command == "resources" and args.resource_command == "export":
        args.path.write_text(json.dumps(response.json(), indent=2), encoding="utf-8")
        print(f"exported namespace resources to {args.path}")
        return True
    return False


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


async def _run_recovery(args: argparse.Namespace, settings: Settings) -> Any:
    service = RecoveryService(settings, build_object_store(settings))
    if args.recovery_command == "create":
        return await service.create_backup(actor_id=args.actor)
    if args.recovery_command == "verify-latest":
        return await service.verify_latest(
            actor_id=args.actor,
            profile=args.profile,
            scheduled=args.scheduled,
        )
    return await service.exercise(
        actor_id=args.actor,
        profile=args.profile,
        scheduled=args.scheduled,
    )


async def _run_tenant_transfer(args: argparse.Namespace, settings: Settings) -> Any:
    engine = create_database_engine(settings)
    try:
        service = TenantTransferService(
            TenantService(PostgresTenantRepository(engine)),
            PostgresExecutionRepository(engine),
            build_object_store(settings),
        )
        if args.transfer_command == "export":
            bundle = await service.export(args.tenant_slug, actor_id=args.actor)
            temporary = args.path.with_suffix(f"{args.path.suffix}.tmp")
            temporary.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
            temporary.replace(args.path)
            return bundle
        bundle = TenantTransferBundle.model_validate_json(args.path.read_text(encoding="utf-8"))
        return await service.import_bundle(
            bundle,
            target_slug=args.target_slug,
            actor_id=args.actor,
        )
    finally:
        await engine.dispose()


async def _bootstrap_local_admin(
    settings: Settings,
    *,
    handle: str,
    display_name: str,
    password: SecretStr,
) -> Any:
    engine = create_database_engine(settings)
    try:
        service = AuthenticationService(
            PostgresAuthenticationRepository(engine),
            token_pepper=settings.amesh_token_pepper,
            policy=settings.auth_policy,
            session_idle_seconds=settings.auth_session_idle_seconds,
            session_absolute_seconds=settings.auth_session_absolute_seconds,
            session_rotation_seconds=settings.auth_session_rotation_seconds,
            session_overlap_seconds=settings.auth_session_overlap_seconds,
            login_rate_limit_per_minute=settings.auth_login_rate_limit_per_minute,
            login_max_failures=settings.auth_login_max_failures,
            login_lock_seconds=settings.auth_login_lock_seconds,
        )
        return await service.bootstrap_local_admin(
            handle=handle,
            display_name=display_name,
            password=password,
        )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
