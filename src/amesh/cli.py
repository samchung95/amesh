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
from amesh.cli_config import (
    CliProfile,
    KeyringCredentialStore,
    default_cli_config_path,
    load_cli_configuration,
    public_configuration,
    save_cli_configuration,
    validate_profile_name,
)
from amesh.config import Settings
from amesh.database import create_database_engine
from amesh.domain import compare_flow_revisions
from amesh.dsl import FlowDocumentError, validate_flow_document
from amesh.plugin_sdk import (
    certify_plugin,
    generate_plugin_documentation,
    quality_level_criteria,
    sandbox_configuration,
    scaffold_plugin,
)
from amesh.ports import StorageMigrationCheckpoint
from amesh.recovery import RecoveryService
from amesh.storage.factory import build_object_store
from amesh.tenancy import TenantService
from amesh.tenant_transfer import TenantTransferBundle, TenantTransferService

EXIT_SUCCESS = 0
EXIT_DIFFERENCE = 1
EXIT_ERROR = 2
EXIT_CONFIRMATION_REQUIRED = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="amesh")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--api-url",
        default=None,
    )
    parser.add_argument("--token", default=None)
    parser.add_argument("--tenant", default=None)
    parser.add_argument("--profile", default=None)
    parser.add_argument("--config-path", type=Path, default=None)
    parser.add_argument(
        "--output",
        dest="output_mode",
        choices=("human", "json", "quiet"),
        default=os.getenv("AMESH_OUTPUT", "json"),
    )
    parser.add_argument("--quiet", action="store_true", help="Alias for --output quiet")
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
    plugin_scaffold = plugin_commands.add_parser(
        "scaffold", help="Create a uv-managed plugin starter"
    )
    plugin_scaffold.add_argument("path", type=Path)
    plugin_scaffold.add_argument("--name", required=True)
    plugin_certify = plugin_commands.add_parser(
        "certify", help="Run all plugin certification checks"
    )
    plugin_certify.add_argument("path", type=Path)
    plugin_certify.add_argument("--platform-version", action="append", default=[])
    plugin_certify.add_argument("--output", type=Path)
    plugin_docs = plugin_commands.add_parser(
        "docs", help="Generate plugin reference and sample configuration"
    )
    plugin_docs.add_argument("path", type=Path)
    plugin_docs.add_argument("--output-dir", type=Path, required=True)
    plugin_sandbox = plugin_commands.add_parser(
        "sandbox", help="Validate one entry-point configuration locally"
    )
    plugin_sandbox.add_argument("path", type=Path)
    plugin_sandbox.add_argument("entry_point")
    plugin_sandbox.add_argument("--configuration", type=Path, required=True)
    plugin_commands.add_parser("criteria", help="Print objective plugin quality-level criteria")

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
    auth_token = auth_commands.add_parser(
        "token", help="Store service-account or API credentials in OS secure storage"
    )
    auth_token_commands = auth_token.add_subparsers(dest="auth_token_command", required=True)
    token_store = auth_token_commands.add_parser("store", help="Store a token for the profile")
    token_store.add_argument(
        "--stdin",
        action="store_true",
        help="Read one token line from stdin instead of a hidden prompt",
    )
    auth_token_commands.add_parser("status", help="Report whether a token is stored")
    auth_token_commands.add_parser("delete", help="Delete the stored token")

    config = subcommands.add_parser("config", help="Manage local CLI profiles")
    config_commands = config.add_subparsers(dest="config_command", required=True)
    config_commands.add_parser("show", help="Show non-secret profile configuration")
    config_set = config_commands.add_parser("set", help="Create or update one profile")
    config_set.add_argument("name")
    config_set.add_argument("--api-url", dest="profile_api_url")
    config_set.add_argument("--tenant", dest="profile_tenant")
    config_use = config_commands.add_parser("use", help="Select the active profile")
    config_use.add_argument("name")
    config_commands.add_parser("profiles", help="List configured profiles")

    flow = subcommands.add_parser("flow", help="Manage declarative flow documents")
    flow_commands = flow.add_subparsers(dest="flow_command", required=True)
    flow_apply = flow_commands.add_parser("apply", help="Apply a file or standard input")
    flow_apply.add_argument("path", nargs="?", default="-")
    flow_diff = flow_commands.add_parser("diff", help="Diff a file or stdin against the server")
    flow_diff.add_argument("path", nargs="?", default="-")
    flow_export = flow_commands.add_parser("export", help="Export one flow document")
    flow_export.add_argument("namespace")
    flow_export.add_argument("flow_id")
    flow_export.add_argument("path", nargs="?", default="-")
    flow_export.add_argument("--revision", type=int)
    flow_delete = flow_commands.add_parser("delete", help="Delete one inactive flow revision")
    flow_delete.add_argument("namespace")
    flow_delete.add_argument("flow_id")
    flow_delete.add_argument("revision", type=int)
    flow_delete.add_argument("--force", action="store_true")

    admin = subcommands.add_parser("admin", help="Perform instance administration")
    admin_commands = admin.add_subparsers(dest="admin_command", required=True)
    admin_configuration = admin_commands.add_parser(
        "configuration", help="Inspect or reload server configuration"
    )
    admin_configuration_commands = admin_configuration.add_subparsers(
        dest="admin_configuration_command", required=True
    )
    admin_configuration_commands.add_parser("show")
    admin_configuration_commands.add_parser("diagnostics")
    admin_configuration_commands.add_parser("reload")
    admin_tenants = admin_commands.add_parser("tenants", help="Manage tenants")
    admin_tenant_commands = admin_tenants.add_subparsers(dest="admin_tenant_command", required=True)
    admin_tenant_commands.add_parser("list")
    admin_tenant_get = admin_tenant_commands.add_parser("get")
    admin_tenant_get.add_argument("slug")
    admin_tenant_create = admin_tenant_commands.add_parser("create")
    admin_tenant_create.add_argument("slug")
    admin_tenant_create.add_argument("--display-name", required=True)
    for action in ("suspend", "restore", "export"):
        action_parser = admin_tenant_commands.add_parser(action)
        action_parser.add_argument("slug")
    admin_tenant_delete = admin_tenant_commands.add_parser("delete")
    admin_tenant_delete.add_argument("slug")
    admin_tenant_delete.add_argument("--force", action="store_true")

    completion = subcommands.add_parser(
        "completion", help="Generate shell completion from the command model"
    )
    completion.add_argument("shell", choices=("bash", "zsh", "fish", "powershell"))
    command_docs = subcommands.add_parser(
        "command-docs", help="Generate Markdown command documentation"
    )
    command_docs.add_argument("path", nargs="?", type=Path)

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
    parser = build_parser()
    args = parser.parse_args(argv)
    output_mode = "quiet" if args.quiet else args.output_mode
    if args.command == "completion":
        _emit(shell_completion(parser, args.shell), "quiet" if output_mode == "quiet" else "human")
        return EXIT_SUCCESS
    if args.command == "command-docs":
        command_reference = command_markdown(parser)
        if args.path is None:
            _emit(command_reference, "quiet" if output_mode == "quiet" else "human")
        else:
            args.path.parent.mkdir(parents=True, exist_ok=True)
            args.path.write_text(command_reference, encoding="utf-8", newline="\n")
            _emit({"documentation": str(args.path)}, output_mode)
        return EXIT_SUCCESS
    try:
        if args.command == "config":
            return _run_config_command(args, output_mode)
        if args.command == "auth" and args.auth_command == "token":
            return _run_token_command(args, output_mode)
        _resolve_cli_context(args, include_token=_uses_api(args))
    except (OSError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_ERROR
    if args.command == "plugins" and args.plugin_command in {
        "scaffold",
        "certify",
        "docs",
        "sandbox",
        "criteria",
    }:
        try:
            if args.plugin_command == "scaffold":
                created = scaffold_plugin(args.path, name=args.name)
                _emit({"created": [str(path) for path in created]}, output_mode)
                return EXIT_SUCCESS
            if args.plugin_command == "certify":
                certification_report = certify_plugin(
                    args.path,
                    platform_versions=tuple(args.platform_version),
                )
                encoded = certification_report.model_dump_json(
                    indent=2, by_alias=True, exclude_none=True
                )
                if args.output is not None:
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    args.output.write_text(encoded + "\n", encoding="utf-8")
                _emit(json.loads(encoded), output_mode)
                return EXIT_SUCCESS if certification_report.passed else EXIT_DIFFERENCE
            if args.plugin_command == "docs":
                documentation_path, sample = generate_plugin_documentation(
                    args.path, args.output_dir
                )
                _emit(
                    {
                        "documentation": str(documentation_path),
                        "sampleConfiguration": str(sample),
                    },
                    output_mode,
                )
                return EXIT_SUCCESS
            if args.plugin_command == "sandbox":
                configuration = _load_mapping(args.configuration)
                sandbox_result = sandbox_configuration(args.path, args.entry_point, configuration)
                _emit(sandbox_result, output_mode)
                return EXIT_SUCCESS if sandbox_result["valid"] else EXIT_DIFFERENCE
            _emit(
                {
                    level.value: list(criteria)
                    for level, criteria in quality_level_criteria().items()
                },
                output_mode,
            )
            return EXIT_SUCCESS
        except (OSError, ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return EXIT_ERROR
    if args.command == "validate":
        path: Path = args.path
        try:
            result = validate_flow_document(path.read_bytes())
        except (OSError, FlowDocumentError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if args.as_json or output_mode == "json":
            _emit(result.model_dump(mode="json", by_alias=True), output_mode)
        elif result.valid:
            _emit(f"valid: {path} ({result.semantic_hash})", output_mode)
        else:
            _emit(
                "\n".join(
                    f"{issue.severity}: {issue.path}: {issue.code}: {issue.message}"
                    for issue in result.issues
                ),
                output_mode,
            )
        return EXIT_SUCCESS if result.valid else EXIT_DIFFERENCE
    if args.command == "storage":
        try:
            if args.storage_command == "validate":
                report = asyncio.run(
                    build_object_store(Settings()).validate_inventory(
                        args.tenant,
                        verify_content=not args.metadata_only,
                    )
                )
                _emit(report.model_dump(mode="json"), output_mode)
                return EXIT_SUCCESS if not report.corrupt else EXIT_DIFFERENCE
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
            _emit(migration_checkpoint.model_dump(mode="json"), output_mode)
            return EXIT_SUCCESS
        except (OSError, ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return EXIT_ERROR
    if args.command == "auth" and args.auth_command == "bootstrap-admin":
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
            _emit(
                {
                    "principalId": str(principal.id),
                    "handle": principal.handle,
                    "displayName": principal.display_name,
                },
                output_mode,
            )
            return EXIT_SUCCESS
        except (EOFError, LookupError, ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return EXIT_ERROR
    if args.command == "recovery":
        try:
            result = asyncio.run(_run_recovery(args, Settings()))
            _emit(result.model_dump(mode="json"), output_mode)
            state = getattr(result, "state", "PASSED")
            return EXIT_SUCCESS if state == "PASSED" else EXIT_DIFFERENCE
        except (OSError, LookupError, ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return EXIT_ERROR
    if args.command == "tenant-transfer":
        try:
            result = asyncio.run(_run_tenant_transfer(args, Settings()))
            _emit(result.model_dump(mode="json"), output_mode)
            return EXIT_SUCCESS
        except (OSError, LookupError, ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return EXIT_ERROR
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
            elif args.command == "flow":
                flow_result = _flow_request(client, args, output_mode)
                if isinstance(flow_result, int):
                    return flow_result
                response = flow_result
            elif args.command == "admin":
                admin_result = _admin_request(client, args, output_mode)
                if isinstance(admin_result, int):
                    return admin_result
                response = admin_result
            else:
                return EXIT_ERROR
        if response.is_error:
            print(f"API error {response.status_code}: {response.text}", file=sys.stderr)
            return EXIT_ERROR
        if args.command == "namespace" and _write_namespace_response(response, args, output_mode):
            return EXIT_SUCCESS
        if args.command == "flow":
            flow_exit = _write_flow_response(response, args, output_mode)
            if flow_exit is not None:
                return flow_exit
        if response.status_code == 204 or not response.content:
            _emit({"status": "ok"}, output_mode)
        else:
            _emit(response.json(), output_mode)
        return EXIT_SUCCESS
    except (OSError, ValueError, httpx.HTTPError) as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_ERROR
    return EXIT_ERROR


def _emit(value: Any, mode: str, *, human: str | None = None) -> None:
    if mode == "quiet":
        return
    if mode == "json":
        print(json.dumps(value, indent=2, sort_keys=True, default=str))
        return
    if human is not None:
        print(human)
        return
    if isinstance(value, str):
        print(value)
        return
    if isinstance(value, dict):
        print(
            "\n".join(
                f"{key}: "
                + (
                    json.dumps(item, sort_keys=True, default=str)
                    if isinstance(item, (dict, list, tuple))
                    else str(item)
                )
                for key, item in value.items()
            )
        )
        return
    if isinstance(value, list):
        print("\n".join(json.dumps(item, sort_keys=True, default=str) for item in value))
        return
    print(value)


def _config_path(args: argparse.Namespace) -> Path:
    return args.config_path or default_cli_config_path()


def _run_config_command(args: argparse.Namespace, output_mode: str) -> int:
    path = _config_path(args)
    configuration = load_cli_configuration(path)
    if args.config_command == "show":
        _emit(public_configuration(configuration), output_mode)
        return EXIT_SUCCESS
    if args.config_command == "profiles":
        _emit(
            {
                "activeProfile": configuration.active_profile,
                "profiles": sorted(configuration.profiles),
            },
            output_mode,
        )
        return EXIT_SUCCESS
    name = validate_profile_name(args.name)
    if args.config_command == "use":
        if name != "default" and name not in configuration.profiles:
            raise ValueError(f"CLI profile {name!r} does not exist")
        configuration.active_profile = name
    else:
        current = configuration.profiles.get(name, CliProfile())
        configuration.profiles[name] = CliProfile(
            apiUrl=args.profile_api_url or current.api_url,
            tenant=args.profile_tenant or current.tenant,
        )
    save_cli_configuration(path, configuration)
    _emit(
        {
            "activeProfile": configuration.active_profile,
            "profile": name,
            "configurationPath": str(path),
        },
        output_mode,
    )
    return EXIT_SUCCESS


def _run_token_command(args: argparse.Namespace, output_mode: str) -> int:
    configuration = load_cli_configuration(_config_path(args))
    profile_name, _profile = configuration.profile(args.profile)
    store = KeyringCredentialStore()
    if args.auth_token_command == "status":
        _emit(
            {"profile": profile_name, "stored": store.get(profile_name) is not None},
            output_mode,
        )
        return EXIT_SUCCESS
    if args.auth_token_command == "delete":
        store.delete(profile_name)
        _emit({"profile": profile_name, "stored": False}, output_mode)
        return EXIT_SUCCESS
    token = (
        sys.stdin.readline().rstrip("\r\n")
        if args.stdin
        else getpass.getpass(f"Token for AMESH profile {profile_name}: ")
    )
    store.set(profile_name, token)
    _emit({"profile": profile_name, "stored": True}, output_mode)
    return EXIT_SUCCESS


def _resolve_cli_context(args: argparse.Namespace, *, include_token: bool) -> str:
    configuration = load_cli_configuration(_config_path(args))
    profile_name, profile = configuration.profile(args.profile)
    args.api_url = args.api_url or os.getenv("AMESH_API_URL") or profile.api_url
    args.tenant = args.tenant or os.getenv("AMESH_TENANT") or profile.tenant
    if include_token:
        args.token = (
            args.token
            or os.getenv("AMESH_SERVICE_ACCOUNT_TOKEN")
            or os.getenv("AMESH_ADMIN_TOKEN")
            or KeyringCredentialStore().get(profile_name)
        )
    return profile_name


def _uses_api(args: argparse.Namespace) -> bool:
    if args.command in {
        "apply",
        "flows",
        "executions",
        "run",
        "execution",
        "logs",
        "webhook",
        "namespace",
        "flow",
        "admin",
    }:
        return True
    return args.command == "plugins" and args.plugin_command in {"list", "refresh", "install"}


def _read_document(path: str) -> bytes:
    if path != "-":
        return Path(path).read_bytes()
    reader = getattr(sys.stdin, "buffer", sys.stdin)
    value = reader.read()
    return value if isinstance(value, bytes) else value.encode()


def _flow_request(
    client: httpx.Client,
    args: argparse.Namespace,
    output_mode: str,
) -> httpx.Response | int:
    if args.flow_command == "apply":
        return client.put(
            "/api/v1/flows",
            content=_read_document(args.path),
            headers={"content-type": "application/yaml"},
        )
    if args.flow_command == "diff":
        validation = validate_flow_document(_read_document(args.path))
        if not validation.valid or validation.canonical is None:
            raise ValueError("local flow document is invalid and cannot be diffed")
        args.local_flow_document = validation.canonical
        return client.get(
            "/api/v1/flows/"
            f"{quote(str(validation.canonical['namespace']), safe='')}/"
            f"{quote(str(validation.canonical['id']), safe='')}/document"
        )
    root = f"/api/v1/flows/{quote(args.namespace, safe='')}/{quote(args.flow_id, safe='')}"
    if args.flow_command == "export":
        params = {"revision": args.revision} if args.revision is not None else None
        return client.get(f"{root}/document", params=params)
    if not args.force:
        _emit(
            {
                "action": "delete flow revision",
                "scope": f"{args.namespace}.{args.flow_id}@{args.revision}",
                "recovery": "restore from a prior export or source-control copy",
                "requiredFlag": "--force",
            },
            output_mode,
            human=(
                f"Would delete {args.namespace}.{args.flow_id}@{args.revision}. "
                "Recovery requires a prior export or source-control copy; rerun with --force."
            ),
        )
        return EXIT_CONFIRMATION_REQUIRED
    return client.delete(f"{root}/revisions/{args.revision}")


def _write_flow_response(
    response: httpx.Response,
    args: argparse.Namespace,
    output_mode: str,
) -> int | None:
    if args.flow_command == "diff":
        remote = response.json()
        difference = compare_flow_revisions(
            remote["document"],
            args.local_flow_document,
            from_revision=remote["revision"],
            to_revision=remote["revision"] + 1,
        )
        _emit(
            {
                "fromRevision": difference.from_revision,
                "toRevision": difference.to_revision,
                "changed": bool(difference.operations),
                "operations": list(difference.operations),
                "human": difference.human,
            },
            output_mode,
            human=difference.human or "No changes.",
        )
        return EXIT_DIFFERENCE if difference.operations else EXIT_SUCCESS
    if args.flow_command != "export":
        return None
    payload = response.json()
    document = payload["document"]
    if args.path == "-":
        if output_mode == "json":
            _emit(document, output_mode)
        elif output_mode == "human":
            print(yaml.safe_dump(document, sort_keys=False), end="")
        return EXIT_SUCCESS
    target = Path(args.path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix.lower() == ".json":
        target.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    else:
        target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    _emit(
        {"exported": str(target), "semanticHash": payload["semanticHash"]},
        output_mode,
    )
    return EXIT_SUCCESS


def _admin_request(
    client: httpx.Client,
    args: argparse.Namespace,
    output_mode: str,
) -> httpx.Response | int:
    if args.admin_command == "configuration":
        action = args.admin_configuration_command
        if action == "show":
            return client.get("/api/v1/configuration")
        if action == "diagnostics":
            return client.get("/api/v1/configuration/diagnostics")
        return client.post("/api/v1/configuration/reload")
    action = args.admin_tenant_command
    root = "/api/v1/admin/tenants"
    if action == "list":
        return client.get(root)
    if action == "create":
        return client.post(root, json={"slug": args.slug, "displayName": args.display_name})
    path = f"{root}/{quote(args.slug, safe='')}"
    if action == "get":
        return client.get(path)
    if action == "delete":
        if not args.force:
            _emit(
                {
                    "action": "delete tenant",
                    "scope": args.slug,
                    "recovery": "restore the soft-deleted tenant before its retention window closes",
                    "requiredFlag": "--force",
                },
                output_mode,
                human=(
                    f"Would soft-delete tenant {args.slug}. It remains recoverable during the "
                    "retention window; rerun with --force."
                ),
            )
            return EXIT_CONFIRMATION_REQUIRED
        return client.delete(path)
    return client.post(f"{path}/{action}s" if action == "export" else f"{path}/{action}")


def _command_paths(parser: argparse.ArgumentParser) -> tuple[str, ...]:
    paths: list[str] = []

    def visit(current: argparse.ArgumentParser, prefix: tuple[str, ...]) -> None:
        for action in current._actions:
            if not isinstance(action, argparse._SubParsersAction):
                continue
            for name, child in sorted(action.choices.items()):
                path = (*prefix, name)
                paths.append(" ".join(path))
                visit(child, path)

    visit(parser, ())
    return tuple(paths)


def shell_completion(parser: argparse.ArgumentParser, shell: str) -> str:
    words = sorted({word for path in _command_paths(parser) for word in path.split()})
    candidates = " ".join(words)
    if shell == "bash":
        return (
            "_amesh_complete() {\n"
            f"  COMPREPLY=( $(compgen -W '{candidates}' -- \"${{COMP_WORDS[COMP_CWORD]}}\") )\n"
            "}\ncomplete -F _amesh_complete amesh\n"
        )
    if shell == "zsh":
        return f"#compdef amesh\n_arguments '*:command:(({candidates}))'\n"
    if shell == "fish":
        return f"complete -c amesh -f -a '{candidates}'\n"
    return (
        "Register-ArgumentCompleter -Native -CommandName amesh -ScriptBlock {\n"
        "  param($wordToComplete)\n"
        f"  '{candidates}'.Split(' ') | Where-Object {{ $_ -like \"$wordToComplete*\" }}\n"
        "}\n"
    )


def command_markdown(parser: argparse.ArgumentParser) -> str:
    lines = ["# AMESH CLI command reference", "", "Generated from `build_parser()`.", ""]

    def visit(current: argparse.ArgumentParser, prefix: tuple[str, ...]) -> None:
        heading = "amesh" + (" " + " ".join(prefix) if prefix else "")
        lines.extend([f"## `{heading}`", "", f"```text\n{current.format_usage().strip()}\n```", ""])
        if current.description:
            lines.extend([current.description, ""])
        for action in current._actions:
            if isinstance(action, argparse._SubParsersAction):
                for name, child in sorted(action.choices.items()):
                    visit(child, (*prefix, name))

    visit(parser, ())
    return "\n".join(lines).rstrip() + "\n"


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


def _load_mapping(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    payload: object = (
        json.loads(content) if path.suffix.lower() == ".json" else yaml.safe_load(content)
    )
    if not isinstance(payload, dict):
        raise ValueError("configuration file root must be an object")
    return payload


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
            return client.get(f"{root}/changes", params={"after": args.after, "limit": args.limit})
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


def _write_namespace_response(
    response: httpx.Response,
    args: argparse.Namespace,
    output_mode: str,
) -> bool:
    if args.namespace_command == "files" and args.file_command == "download":
        args.local_path.write_bytes(response.content)
        _emit(
            {"downloadedBytes": len(response.content), "path": str(args.local_path)},
            output_mode,
            human=f"downloaded {len(response.content)} bytes to {args.local_path}",
        )
        return True
    if args.namespace_command == "resources" and args.resource_command == "export":
        args.path.write_text(json.dumps(response.json(), indent=2), encoding="utf-8")
        _emit(
            {"exported": str(args.path)},
            output_mode,
            human=f"exported namespace resources to {args.path}",
        )
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
