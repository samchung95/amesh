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
from amesh.api.evidence_models import EvidenceBundlePageResponse
from amesh.application import build_authentication_service
from amesh.cli_config import (
    CliProfile,
    KeyringCredentialStore,
    default_cli_config_path,
    load_cli_configuration,
    public_configuration,
    save_cli_configuration,
    validate_profile_name,
)
from amesh.compatibility.kestra import (
    FileMigrationStore,
    MigrationBundle,
    MigrationImporter,
    compatibility_manifest,
    import_kestra_flow,
    plan_migration,
)
from amesh.config import Settings
from amesh.database import create_database_engine
from amesh.domain import AgentProgressEvent, compare_flow_revisions
from amesh.dsl import FlowDocumentError, validate_flow_document
from amesh.identity import TenantService
from amesh.plugin_sdk import (
    certify_plugin,
    certify_tool_provider,
    generate_plugin_documentation,
    quality_level_criteria,
    sandbox_configuration,
    scaffold_plugin,
)
from amesh.ports import StorageMigrationCheckpoint
from amesh.quality import add_differential_commands, differential_request, differential_result
from amesh.recovery import RecoveryService
from amesh.storage.factory import build_object_store
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

    evidence = subcommands.add_parser(
        "evidence", help="Get a bounded canonical evidence-bundle page for one execution"
    )
    evidence.add_argument("execution_id")
    evidence.add_argument("--section", default="trace")
    evidence.add_argument("--cursor")
    evidence.add_argument("--limit", type=int, default=100)
    evidence.add_argument("--verify", action="store_true")

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
    provider_certify = plugin_commands.add_parser(
        "certify-provider",
        aliases=("certify-tool-provider",),
        help="Run provider-neutral ToolProvider certification checks",
    )
    provider_certify.add_argument("path", type=Path)
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

    agents = subcommands.add_parser("agent", help="Manage versioned agent definitions")
    agent_commands = agents.add_subparsers(dest="agent_command", required=True)
    agent_apply = agent_commands.add_parser("apply", help="Create a resource revision")
    agent_apply.add_argument("namespace")
    agent_apply.add_argument("path", type=Path)
    agent_list = agent_commands.add_parser("list", help="List latest resource revisions")
    agent_list.add_argument("namespace")
    agent_list.add_argument(
        "--kind",
        choices=("PROMPT", "SKILL", "MODEL_POLICY", "AGENT"),
    )
    agent_get = agent_commands.add_parser("get", help="Get one exact resource revision")
    agent_get.add_argument("namespace")
    agent_get.add_argument("kind", choices=("PROMPT", "SKILL", "MODEL_POLICY", "AGENT"))
    agent_get.add_argument("key")
    agent_get.add_argument("--revision", type=int)
    agent_resolve = agent_commands.add_parser(
        "resolve",
        help="Resolve and pin an effective capability envelope",
    )
    agent_resolve.add_argument("namespace")
    agent_resolve.add_argument("key")
    agent_resolve.add_argument("--revision", type=int, required=True)
    agent_resolve.add_argument("--subject-ref", required=True)
    agent_compare = agent_commands.add_parser("compare", help="Compare agent revisions")
    agent_compare.add_argument("namespace")
    agent_compare.add_argument("key")
    agent_compare.add_argument("--from-revision", type=int, required=True)
    agent_compare.add_argument("--to-revision", type=int, required=True)
    agent_migration = agent_commands.add_parser(
        "model-migration",
        help="Explain provider-route migration semantics",
    )
    agent_migration.add_argument("namespace")
    agent_migration.add_argument("key")
    agent_migration.add_argument("--from-revision", type=int, required=True)
    agent_migration.add_argument("--to-revision", type=int, required=True)

    sessions = subcommands.add_parser(
        "session",
        help="Run and inspect durable harness-neutral agent sessions",
    )
    session_commands = sessions.add_subparsers(dest="session_command", required=True)
    session_create = session_commands.add_parser(
        "create",
        help="Create one session from an exact agent revision",
    )
    session_create.add_argument("namespace")
    session_create.add_argument("agent")
    session_create.add_argument("--agent-revision", type=int, required=True)
    session_input = session_create.add_mutually_exclusive_group()
    session_input.add_argument(
        "--input-json",
        help="Inline JSON object supplied to the pinned agent input schema",
    )
    session_input.add_argument(
        "--input-file",
        type=Path,
        help="Path to a UTF-8 JSON object supplied to the pinned agent input schema",
    )
    session_create.add_argument(
        "--invalid-output-policy",
        choices=("FAIL", "REPAIR"),
        default="FAIL",
    )
    session_create.add_argument("--max-repair-attempts", type=int, default=0)
    session_create.add_argument("--approval-task")
    session_create.add_argument(
        "--data-handling",
        choices=("DENY_SECRETS", "REDACT_SECRETS", "ALLOW"),
        default="DENY_SECRETS",
    )
    session_create.add_argument("--memory-read-key", action="append", default=[])
    session_create.add_argument("--memory-write-key")
    session_create.add_argument("--timeout-seconds", type=float)
    session_create.add_argument(
        "--runner",
        choices=("local", "docker", "kubernetes"),
        default="local",
    )
    session_create.add_argument("--idempotency-key")
    session_create.add_argument(
        "--prefer-async",
        action="store_true",
        help="Request asynchronous admission and return a polling location",
    )

    session_list = session_commands.add_parser("list", help="List recent tenant sessions")
    session_list.add_argument("--limit", type=int, default=100)
    for action in ("get", "events"):
        session_read = session_commands.add_parser(
            action,
            help=(
                "Get one session and its bounded event page"
                if action == "get"
                else "Get one bounded durable event page"
            ),
        )
        session_read.add_argument("session_id")
        session_read.add_argument("--after-event-index", type=int, default=0)
        session_read.add_argument("--limit", type=int, default=100)
    session_result = session_commands.add_parser(
        "result",
        help="Get the structured terminal result or safe error",
    )
    session_result.add_argument("session_id")
    session_progress = session_commands.add_parser(
        "progress",
        help="Get one bounded page of chronological agent progress",
    )
    session_progress.add_argument("session_id")
    session_progress.add_argument("--after")
    session_progress.add_argument("--limit", type=_progress_limit, default=100)
    session_watch = session_commands.add_parser(
        "watch",
        help="Watch chronological agent progress until terminal completion",
    )
    session_watch.add_argument("session_id")
    session_watch.add_argument("--after")
    for action in ("cancel", "pause", "retry", "resume"):
        session_control = session_commands.add_parser(
            action,
            help=f"{action.capitalize()} one session through governed execution control",
        )
        session_control.add_argument("session_id")
        session_control.add_argument("--expected-version", type=int)
        session_control.add_argument("--expected-epoch", type=int)
        session_control.add_argument("--reason", required=True)
        session_control.add_argument("--grace-seconds", type=float, default=30)

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
    flow_test = flow_commands.add_parser("test", help="Run revision-pinned flow unit tests")
    flow_test.add_argument("namespace")
    flow_test.add_argument("flow_id")
    flow_test.add_argument("--revision", type=int, required=True)
    flow_test.add_argument("--test-id", action="append", default=[])
    flow_test.add_argument("--fail-fast", action="store_true")
    flow_simulate = flow_commands.add_parser(
        "simulate",
        help="Compile a signed side-effect-free simulation plan",
    )
    flow_simulate.add_argument("namespace")
    flow_simulate.add_argument("flow_id")
    flow_simulate.add_argument("--revision", type=int, required=True)
    _add_simulation_arguments(flow_simulate)
    flow_simulation_diff = flow_commands.add_parser(
        "simulation-diff",
        help="Compare deterministic plans for two flow revisions",
    )
    flow_simulation_diff.add_argument("namespace")
    flow_simulation_diff.add_argument("flow_id")
    flow_simulation_diff.add_argument("--from-revision", type=int, required=True)
    flow_simulation_diff.add_argument("--to-revision", type=int, required=True)
    _add_simulation_arguments(flow_simulation_diff)

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

    lifecycle = subcommands.add_parser("lifecycle", help="Manage retention and purge jobs")
    lifecycle_commands = lifecycle.add_subparsers(dest="lifecycle_command", required=True)
    lifecycle_commands.add_parser("policies", help="List effective lifecycle policies")
    lifecycle_policy = lifecycle_commands.add_parser(
        "create-policy", help="Create a scoped lifecycle policy"
    )
    lifecycle_policy.add_argument(
        "--resource-type",
        required=True,
        choices=("EXECUTION", "LOG", "METRIC", "ARTIFACT", "CACHE"),
    )
    lifecycle_policy.add_argument(
        "--scope", required=True, choices=("INSTANCE", "TENANT", "NAMESPACE", "LABEL")
    )
    lifecycle_policy.add_argument("--namespace")
    lifecycle_policy.add_argument("--label", action="append", default=[])
    lifecycle_policy.add_argument("--retention-days", required=True, type=int)
    lifecycle_policy.add_argument("--batch-size", type=int, default=100)
    lifecycle_policy.add_argument("--schedule-minutes", type=int)
    lifecycle_policy.add_argument("--reason", required=True)
    lifecycle_preview = lifecycle_commands.add_parser(
        "preview", help="Preview records and bytes affected by a policy"
    )
    lifecycle_preview.add_argument("policy_id")
    lifecycle_preview.add_argument("--reason", required=True)
    lifecycle_commands.add_parser("jobs", help="List lifecycle job progress and evidence")
    lifecycle_execute = lifecycle_commands.add_parser(
        "execute", help="Execute one previewed purge batch"
    )
    lifecycle_execute.add_argument("job_id")
    lifecycle_execute.add_argument("--force", action="store_true")
    lifecycle_resume = lifecycle_commands.add_parser(
        "resume", help="Resume one bounded purge or external deletion retry"
    )
    lifecycle_resume.add_argument("job_id")
    lifecycle_commands.add_parser("holds", help="List lifecycle legal holds")
    lifecycle_hold = lifecycle_commands.add_parser("hold", help="Create a lifecycle legal hold")
    lifecycle_hold.add_argument("name")
    lifecycle_hold.add_argument("--reason", required=True)
    lifecycle_hold.add_argument(
        "--resource-type", choices=("EXECUTION", "LOG", "METRIC", "ARTIFACT", "CACHE")
    )
    lifecycle_hold.add_argument("--resource-id")
    lifecycle_hold.add_argument("--namespace")
    lifecycle_hold.add_argument("--label", action="append", default=[])
    lifecycle_hold.add_argument("--data-from")
    lifecycle_hold.add_argument("--data-to")
    lifecycle_release = lifecycle_commands.add_parser(
        "release-hold", help="Release a lifecycle legal hold"
    )
    lifecycle_release.add_argument("hold_id")

    releases = subcommands.add_parser(
        "releases", help="Preview and apply evidence-backed release actions"
    )
    release_commands = releases.add_subparsers(dest="release_command", required=True)
    release_preview = release_commands.add_parser("preview", help="Preview one policy gate")
    release_preview.add_argument("policy_id")
    release_apply = release_commands.add_parser("apply", help="Apply one passing policy gate")
    release_apply.add_argument("policy_id")
    release_apply.add_argument("--expected-version", type=int, required=True)
    release_apply.add_argument("--reason", required=True)
    release_rollback = release_commands.add_parser(
        "rollback", help="Rollback to an exact prior revision"
    )
    release_rollback.add_argument("target_kind", choices=("WORKFLOW", "AGENT"))
    release_rollback.add_argument("target_key")
    release_rollback.add_argument("--to-revision", type=int, required=True)
    release_rollback.add_argument("--expected-version", type=int, required=True)
    release_rollback.add_argument("--reason", required=True)
    release_kill = release_commands.add_parser("kill-switch", help="Immediately disable a target")
    release_kill.add_argument("target_kind", choices=("WORKFLOW", "AGENT"))
    release_kill.add_argument("target_key")
    release_kill.add_argument("--expected-version", type=int, required=True)
    release_kill.add_argument("--reason", required=True)
    release_target = release_commands.add_parser("target", help="Read current release state")
    release_target.add_argument("target_kind", choices=("WORKFLOW", "AGENT"))
    release_target.add_argument("target_key")
    release_history = release_commands.add_parser("history", help="Read immutable release history")
    release_history.add_argument("target_kind", choices=("WORKFLOW", "AGENT"))
    release_history.add_argument("target_key")

    add_differential_commands(subcommands)

    upgrade = subcommands.add_parser("upgrade", help="Plan and verify supported upgrades")
    upgrade_commands = upgrade.add_subparsers(dest="upgrade_command", required=True)
    upgrade_commands.add_parser("policy", help="Show supported LTS releases and upgrade paths")
    for command in ("preflight", "postflight"):
        report = upgrade_commands.add_parser(command, help=f"Run the {command} report")
        report.add_argument("--from-version", required=True)
        report.add_argument("--to-version", required=True)
    upgrade_commands.add_parser(
        "events-preview", help="Preview persisted execution events eligible for upcast"
    )
    event_upcast = upgrade_commands.add_parser(
        "events-upcast", help="Upcast one bounded batch of persisted execution events"
    )
    event_upcast.add_argument("--reason", required=True)
    event_upcast.add_argument("--batch-size", type=int, default=1_000)
    event_upcast.add_argument("--force", action="store_true")
    config_migration = upgrade_commands.add_parser(
        "migrate-config", help="Canonicalize one flow or plugin document for a target release"
    )
    config_migration.add_argument("kind", choices=("flow", "plugin"))
    config_migration.add_argument("path", type=Path)
    config_migration.add_argument("--target-version", required=True)
    config_migration.add_argument("--output", type=Path, required=True)

    kestra = subcommands.add_parser(
        "kestra", help="Use the version-pinned Kestra 1.3.30 compatibility surface"
    )
    kestra_commands = kestra.add_subparsers(dest="kestra_command", required=True)
    kestra_flow = kestra_commands.add_parser("flow", help="Validate or migrate Kestra flows")
    kestra_flow_commands = kestra_flow.add_subparsers(dest="kestra_flow_command", required=True)
    kestra_flow_validate = kestra_flow_commands.add_parser(
        "validate", help="Classify a Kestra flow against the declared compatibility surface"
    )
    kestra_flow_validate.add_argument("path", type=Path)
    kestra_flow_migrate = kestra_flow_commands.add_parser(
        "migrate", help="Write an AMESH candidate flow when all mappings are supported"
    )
    kestra_flow_migrate.add_argument("path", type=Path)
    kestra_flow_migrate.add_argument("--output-path", type=Path, required=True)

    kestra_migration = kestra_commands.add_parser(
        "migration", help="Plan or run a checksum-protected side-by-side migration"
    )
    kestra_migration_commands = kestra_migration.add_subparsers(
        dest="kestra_migration_command", required=True
    )
    kestra_migration_plan = kestra_migration_commands.add_parser(
        "plan", help="Dry-run a migration bundle and report cutover blockers"
    )
    kestra_migration_plan.add_argument("bundle", type=Path)
    kestra_migration_plan.add_argument("--secret-binding", action="append", default=[])
    kestra_migration_import = kestra_migration_commands.add_parser(
        "import", help="Resume an idempotent side-by-side migration import"
    )
    kestra_migration_import.add_argument("bundle", type=Path)
    kestra_migration_import.add_argument("--target-dir", type=Path, required=True)
    kestra_migration_import.add_argument("--max-records", type=int)
    kestra_migration_import.add_argument("--secret-binding", action="append", default=[])

    kestra_compatibility = kestra_commands.add_parser(
        "compatibility", help="Inspect the version-pinned compatibility contract"
    )
    kestra_compatibility_commands = kestra_compatibility.add_subparsers(
        dest="kestra_compatibility_command", required=True
    )
    kestra_compatibility_commands.add_parser(
        "manifest", help="Print the machine-readable compatibility manifest"
    )

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
    if args.command == "kestra":
        try:
            return _run_kestra_command(args, output_mode)
        except (OSError, FlowDocumentError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return EXIT_ERROR
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
        "certify-provider",
        "certify-tool-provider",
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
            if args.plugin_command in {"certify-provider", "certify-tool-provider"}:
                provider_report = certify_tool_provider(_load_mapping(args.path))
                _emit(provider_report.model_dump(mode="json", by_alias=True), output_mode)
                return EXIT_SUCCESS if provider_report.passed else EXIT_DIFFERENCE
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
            elif args.command == "evidence":
                evidence_params = {
                    key: value
                    for key, value in {
                        "section": args.section,
                        "cursor": args.cursor,
                        "limit": args.limit,
                    }.items()
                    if value is not None
                }
                response = client.get(
                    f"/api/v1/executions/{args.execution_id}/evidence-bundle",
                    params=evidence_params,
                )
                if args.verify and not response.is_error:
                    verified = EvidenceBundlePageResponse.model_validate(response.json())
                    payload = verified.model_dump(mode="json", by_alias=True)
                    payload["verified"] = True
                    response = httpx.Response(200, json=payload)
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
            elif args.command == "agent":
                response = _agent_request(client, args)
            elif args.command == "session":
                if args.session_command == "watch":
                    return _watch_session_progress(client, args, output_mode)
                response = _session_request(client, args)
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
            elif args.command == "lifecycle":
                lifecycle_result = _lifecycle_request(client, args, output_mode)
                if isinstance(lifecycle_result, int):
                    return lifecycle_result
                response = lifecycle_result
            elif args.command == "upgrade":
                upgrade_result = _upgrade_request(client, args, output_mode)
                if isinstance(upgrade_result, int):
                    return upgrade_result
                response = upgrade_result
            elif args.command == "releases":
                response = _release_request(client, args)
            elif args.command == "differential":
                result_code, result_body = differential_result(
                    differential_request(client, args, tenant_id=args.tenant)
                )
                _emit(result_body, output_mode)
                return result_code
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
        if args.command == "session" and _write_session_response(
            response,
            args,
            output_mode,
        ):
            return EXIT_SUCCESS
        if args.command == "upgrade" and _write_upgrade_response(response, args, output_mode):
            return EXIT_SUCCESS
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
        "evidence",
        "webhook",
        "namespace",
        "agent",
        "session",
        "flow",
        "admin",
        "lifecycle",
        "upgrade",
        "releases",
        "differential",
    }:
        return True
    return args.command == "plugins" and args.plugin_command in {"list", "refresh", "install"}


def _run_kestra_command(args: argparse.Namespace, output_mode: str) -> int:
    if args.kestra_command == "flow":
        imported = import_kestra_flow(args.path.read_bytes())
        if args.kestra_flow_command == "migrate" and imported.valid:
            args.output_path.parent.mkdir(parents=True, exist_ok=True)
            args.output_path.write_text(
                yaml.safe_dump(imported.candidate_document, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )
        payload = imported.model_dump(mode="json", by_alias=True)
        if args.kestra_flow_command == "migrate":
            payload["outputPath"] = str(args.output_path) if imported.valid else None
        _emit(payload, output_mode)
        return EXIT_SUCCESS if imported.valid else EXIT_DIFFERENCE
    if args.kestra_command == "migration":
        bundle = MigrationBundle.model_validate_json(args.bundle.read_text(encoding="utf-8"))
        bindings = set(args.secret_binding)
        if args.kestra_migration_command == "plan":
            plan = plan_migration(bundle, resolved_secret_bindings=bindings)
            _emit(plan.model_dump(mode="json", by_alias=True), output_mode)
            return EXIT_SUCCESS if plan.cutover_allowed else EXIT_DIFFERENCE
        importer = MigrationImporter(FileMigrationStore(args.target_dir))
        result = importer.import_bundle(
            bundle,
            resolved_secret_bindings=bindings,
            max_records=args.max_records,
        )
        reconciliation = importer.reconcile(bundle) if result.complete else ()
        _emit(
            {
                **result.model_dump(mode="json", by_alias=True),
                "reconciliation": [
                    item.model_dump(mode="json", by_alias=True) for item in reconciliation
                ],
            },
            output_mode,
        )
        return EXIT_SUCCESS if not reconciliation else EXIT_DIFFERENCE
    _emit(compatibility_manifest(), output_mode)
    return EXIT_SUCCESS


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
    if args.flow_command == "test":
        return client.post(
            f"{root}/tests/runs",
            params={"revision": args.revision},
            json={"testIds": args.test_id, "failFast": args.fail_fast},
        )
    if args.flow_command == "simulate":
        return client.post(
            f"{root}/revisions/{args.revision}/simulate",
            json=_simulation_request(args),
        )
    if args.flow_command == "simulation-diff":
        return client.post(
            f"{root}/simulations/compare",
            params={"from": args.from_revision, "to": args.to_revision},
            json=_simulation_request(args),
        )
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
    if args.flow_command == "test":
        payload = response.json()
        _emit(
            payload,
            output_mode,
            human=(
                f"{payload['outcome']}: {len(payload['cases'])} case(s), "
                f"{payload['coverage']['percentage']:.2f}% observed coverage"
            ),
        )
        return EXIT_SUCCESS if payload["outcome"] == "PASSED" else EXIT_DIFFERENCE
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


def _lifecycle_request(
    client: httpx.Client,
    args: argparse.Namespace,
    output_mode: str,
) -> httpx.Response | int:
    root = "/api/v1/lifecycle"
    action = args.lifecycle_command
    if action == "policies":
        return client.get(f"{root}/policies")
    if action == "create-policy":
        return client.post(
            f"{root}/policies",
            json={
                "resourceType": args.resource_type,
                "scope": args.scope,
                "namespace": args.namespace,
                "labelSelector": _parse_inputs(args.label),
                "retentionDays": args.retention_days,
                "batchSize": args.batch_size,
                "scheduleIntervalMinutes": args.schedule_minutes,
                "reason": args.reason,
            },
        )
    if action == "preview":
        return client.post(
            f"{root}/previews",
            json={"policyId": args.policy_id, "reason": args.reason},
        )
    if action == "jobs":
        return client.get(f"{root}/jobs")
    if action == "execute":
        job = client.get(f"{root}/jobs/{quote(args.job_id, safe='')}")
        job.raise_for_status()
        preview = job.json()
        if not args.force:
            _emit(
                {
                    "action": "purge retained lifecycle data",
                    "scope": preview["policySnapshot"],
                    "affectedRecords": preview["estimatedRecords"],
                    "affectedBytes": preview["estimatedBytes"],
                    "protectedRecords": preview["protectedRecords"],
                    "activeRecordsExcluded": preview["activeRecords"],
                    "recovery": "purged data requires a qualified backup restore",
                    "requiredFlag": "--force",
                },
                output_mode,
                human=(
                    f"Would purge {preview['estimatedRecords']} record(s) and "
                    f"{preview['estimatedBytes']} byte(s). Recovery requires a qualified "
                    "backup restore; rerun with --force."
                ),
            )
            return EXIT_CONFIRMATION_REQUIRED
        return client.post(
            f"{root}/jobs/{quote(args.job_id, safe='')}/execute",
            json={"confirmation": preview["confirmationPhrase"]},
        )
    if action == "resume":
        return client.post(f"{root}/jobs/{quote(args.job_id, safe='')}/resume")
    if action == "holds":
        return client.get(f"{root}/legal-holds")
    if action == "hold":
        return client.post(
            f"{root}/legal-holds",
            json={
                "name": args.name,
                "reason": args.reason,
                "resourceType": args.resource_type,
                "resourceId": args.resource_id,
                "namespace": args.namespace,
                "labelSelector": _parse_inputs(args.label),
                "dataFrom": args.data_from,
                "dataTo": args.data_to,
            },
        )
    return client.post(f"{root}/legal-holds/{quote(args.hold_id, safe='')}/release")


def _upgrade_request(
    client: httpx.Client,
    args: argparse.Namespace,
    output_mode: str,
) -> httpx.Response | int:
    root = "/api/v1/upgrades"
    action = args.upgrade_command
    if action == "policy":
        return client.get(f"{root}/policy")
    if action in {"preflight", "postflight"}:
        return client.post(
            f"{root}/{action}",
            json={"fromVersion": args.from_version, "toVersion": args.to_version},
        )
    if action == "events-preview":
        return client.get(f"{root}/events/upcast")
    if action == "events-upcast":
        preview_response = client.get(f"{root}/events/upcast")
        preview_response.raise_for_status()
        preview = preview_response.json()
        if not args.force:
            _emit(
                {
                    "action": "upcast persisted execution events",
                    "eligibleEvents": preview["eligibleEvents"],
                    "recovery": "restore the pre-upgrade recovery point if validation fails",
                    "requiredFlag": "--force",
                },
                output_mode,
                human=(
                    f"Would upcast up to {args.batch_size} of "
                    f"{preview['eligibleEvents']} event(s). Rerun with --force."
                ),
            )
            return EXIT_CONFIRMATION_REQUIRED
        return client.post(
            f"{root}/events/upcast",
            json={
                "confirmation": preview["confirmationPhrase"],
                "reason": args.reason,
                "batchSize": args.batch_size,
            },
        )
    return client.post(
        f"{root}/configuration/migrate",
        json={
            "kind": args.kind,
            "targetVersion": args.target_version,
            "document": _load_mapping(args.path),
        },
    )


def _release_request(client: httpx.Client, args: argparse.Namespace) -> httpx.Response:
    if args.release_command == "preview":
        return client.post(f"/api/v1/releases/policies/{quote(args.policy_id, safe='')}/preview")
    if args.release_command == "apply":
        return client.post(
            f"/api/v1/releases/policies/{quote(args.policy_id, safe='')}/apply",
            json={
                "expectedVersion": args.expected_version,
                "reason": args.reason,
            },
        )
    target = f"{args.target_kind.lower()}/{quote(args.target_key, safe='')}"
    if args.release_command == "rollback":
        return client.post(
            f"/api/v1/releases/{target}/rollback",
            json={
                "toRevision": args.to_revision,
                "expectedVersion": args.expected_version,
                "reason": args.reason,
            },
        )
    if args.release_command == "kill-switch":
        return client.post(
            f"/api/v1/releases/{target}/kill-switch",
            json={"expectedVersion": args.expected_version, "reason": args.reason},
        )
    suffix = "history" if args.release_command == "history" else ""
    path = f"/api/v1/releases/{target}"
    return client.get(f"{path}/{suffix}" if suffix else path)


def _write_upgrade_response(
    response: httpx.Response,
    args: argparse.Namespace,
    output_mode: str,
) -> bool:
    if args.upgrade_command != "migrate-config":
        return False
    payload = response.json()
    target: Path = args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix.lower() == ".json":
        target.write_text(json.dumps(payload["canonical"], indent=2) + "\n", encoding="utf-8")
    else:
        target.write_text(
            yaml.safe_dump(payload["canonical"], sort_keys=False),
            encoding="utf-8",
        )
    _emit(
        {
            "kind": payload["kind"],
            "targetVersion": payload["targetVersion"],
            "changed": payload["changed"],
            "output": str(target),
            "warnings": payload["warnings"],
        },
        output_mode,
        human=f"wrote canonical {payload['kind']} configuration to {target}",
    )
    return True


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


def _progress_limit(value: str) -> int:
    limit = int(value)
    if not 1 <= limit <= 1_000:
        raise argparse.ArgumentTypeError("progress limit must be between 1 and 1000")
    return limit


def _add_simulation_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--variable", action="append", default=[])
    parser.add_argument("--trigger", action="append", default=[])
    parser.add_argument(
        "--fixture",
        action="append",
        default=[],
        help="Task fixture as task_id={JSON or YAML mapping}",
    )
    parser.add_argument(
        "--estimate-model",
        action="append",
        default=[],
        help="Estimate model as task_type={JSON or YAML mapping}",
    )
    parser.add_argument(
        "--default-runner",
        choices=("local", "docker", "kubernetes"),
        default="kubernetes",
    )
    parser.add_argument("--unsigned", action="store_true")


def _simulation_request(args: argparse.Namespace) -> dict[str, Any]:
    fixtures = _parse_inputs(args.fixture)
    estimate_models = _parse_inputs(args.estimate_model)
    if any(not isinstance(value, dict) for value in fixtures.values()):
        raise ValueError("simulation fixtures must be JSON or YAML objects")
    if any(not isinstance(value, dict) for value in estimate_models.values()):
        raise ValueError("simulation estimate models must be JSON or YAML objects")
    return {
        "inputs": _parse_inputs(args.input),
        "variables": _parse_inputs(args.variable),
        "triggerContext": _parse_inputs(args.trigger),
        "fixtures": fixtures,
        "estimateModels": estimate_models,
        "defaultRunner": args.default_runner,
        "signEvidence": not args.unsigned,
    }


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


def _agent_request(client: httpx.Client, args: argparse.Namespace) -> httpx.Response:
    root = _resource_path(args.namespace, "agent")
    if args.agent_command == "apply":
        return client.post(f"{root}/resources", json=_load_mapping(args.path))
    if args.agent_command == "list":
        params = {"kind": args.kind} if args.kind is not None else None
        return client.get(f"{root}/resources", params=params)
    if args.agent_command == "get":
        path = f"{root}/resources/{args.kind}/{quote(args.key, safe='')}"
        params = {"revision": args.revision} if args.revision is not None else None
        return client.get(path, params=params)
    if args.agent_command == "resolve":
        return client.post(
            f"{root}/definitions/{quote(args.key, safe='')}/resolve",
            json={"agentRevision": args.revision, "subjectRef": args.subject_ref},
        )
    params = {
        "fromRevision": args.from_revision,
        "toRevision": args.to_revision,
    }
    if args.agent_command == "compare":
        return client.get(
            f"{root}/definitions/{quote(args.key, safe='')}/compare",
            params=params,
        )
    return client.get(
        f"{root}/model-policies/{quote(args.key, safe='')}/migration",
        params=params,
    )


def _session_input(args: argparse.Namespace) -> dict[str, Any]:
    if args.input_file is not None:
        source = str(args.input_file)
        encoded = args.input_file.read_text(encoding="utf-8")
    elif args.input_json is not None:
        source = "--input-json"
        encoded = args.input_json
    else:
        return {}
    try:
        payload = json.loads(encoded)
    except json.JSONDecodeError as exc:
        raise ValueError(f"session input from {source} is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"session input from {source} must be a JSON object")
    return payload


def _session_request(client: httpx.Client, args: argparse.Namespace) -> httpx.Response:
    root = "/api/v1/agent-sessions"
    action = args.session_command
    if action == "create":
        payload: dict[str, Any] = {
            "namespace": args.namespace,
            "agent": args.agent,
            "agentRevision": args.agent_revision,
            "input": _session_input(args),
            "invalidOutputPolicy": args.invalid_output_policy,
            "maxRepairAttempts": args.max_repair_attempts,
            "dataHandling": args.data_handling,
            "memoryReadKeys": args.memory_read_key,
            "runner": args.runner,
        }
        for key, value in {
            "approvalTask": args.approval_task,
            "memoryWriteKey": args.memory_write_key,
            "timeoutSeconds": args.timeout_seconds,
        }.items():
            if value is not None:
                payload[key] = value
        headers: dict[str, str] = {}
        if args.idempotency_key is not None:
            headers["Idempotency-Key"] = args.idempotency_key
        if args.prefer_async:
            headers["Prefer"] = "respond-async"
        request_arguments: dict[str, Any] = {"json": payload}
        if headers:
            request_arguments["headers"] = headers
        return client.post(root, **request_arguments)
    if action == "list":
        return client.get(root, params={"limit": args.limit})

    session_path = f"{root}/{quote(args.session_id, safe='')}"
    if action in {"get", "events"}:
        suffix = "" if action == "get" else "/events"
        return client.get(
            f"{session_path}{suffix}",
            params={
                "afterEventIndex": args.after_event_index,
                "limit": args.limit,
            },
        )
    if action == "result":
        return client.get(f"{session_path}/result")
    if action == "progress":
        params: dict[str, str | int] = {"limit": args.limit}
        if args.after is not None:
            params["after"] = args.after
        return client.get(f"{session_path}/progress", params=params)

    control: dict[str, Any] = {
        "reason": args.reason,
        "graceSeconds": args.grace_seconds,
    }
    if args.expected_version is not None:
        control["expectedVersion"] = args.expected_version
    if args.expected_epoch is not None:
        control["expectedEpoch"] = args.expected_epoch
    return client.post(
        f"{session_path}/{action}",
        json=control,
    )


def _watch_session_progress(
    client: httpx.Client,
    args: argparse.Namespace,
    output_mode: str,
) -> int:
    path = f"/api/v1/agent-sessions/{quote(args.session_id, safe='')}/progress/stream"
    latest_cursor: str | None = args.after
    terminal = False
    try:
        stream = (
            client.stream("GET", path, params={"after": args.after})
            if args.after is not None
            else client.stream("GET", path)
        )
        with stream as response:
            if response.is_error:
                response.read()
                reconnect = f"; reconnect with --after {latest_cursor}" if latest_cursor else ""
                print(
                    f"API error {response.status_code}: {response.text}{reconnect}",
                    file=sys.stderr,
                )
                return EXIT_ERROR
            for line in response.iter_lines():
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError("agent progress stream returned malformed JSON") from exc
                if not isinstance(payload, dict):
                    raise ValueError("agent progress stream item must be a JSON object")
                if payload.get("type") == "heartbeat":
                    cursor = payload.get("cursor")
                    if not isinstance(cursor, str) or not cursor:
                        raise ValueError("agent progress heartbeat is missing its reconnect cursor")
                    latest_cursor = cursor
                    if output_mode == "json":
                        _emit_progress_stream_json(payload)
                    continue
                event = AgentProgressEvent.model_validate(payload)
                latest_cursor = event.cursor
                if output_mode == "json":
                    _emit_progress_stream_json(payload)
                elif output_mode == "human":
                    print(_human_progress_event(payload), flush=True)
                terminal = event.frame.activity.value == "TERMINAL"
    except (OSError, ValueError, httpx.HTTPError) as exc:
        reconnect = f"; reconnect with --after {latest_cursor}" if latest_cursor else ""
        print(f"{exc}{reconnect}", file=sys.stderr)
        return EXIT_ERROR
    if not terminal:
        reconnect = f"; reconnect with --after {latest_cursor}" if latest_cursor else ""
        print(f"agent progress stream ended before terminal completion{reconnect}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_SUCCESS


def _emit_progress_stream_json(payload: dict[str, Any]) -> None:
    print(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str),
        flush=True,
    )


def _human_progress_event(event: dict[str, Any]) -> str:
    frame = event["frame"]
    detail = frame.get("detail")
    description = ""
    if isinstance(detail, dict):
        if detail.get("kind") == "PUBLIC_SUMMARY":
            description = f": {detail['text']}"
        elif detail.get("kind") == "STATUS":
            description = f": {detail.get('label') or detail['code']}"
    return (
        f"{frame['activity'].lower()} {frame['status'].lower()}{description} "
        f"[cursor {event['cursor']}]"
    )


def _write_session_response(
    response: httpx.Response,
    args: argparse.Namespace,
    output_mode: str,
) -> bool:
    if args.session_command not in {"create", "cancel", "retry", "resume", "pause"}:
        return False
    payload = response.json()
    location = response.headers.get("Location")
    if location is not None:
        payload["location"] = location
    preference_applied = response.headers.get("Preference-Applied")
    if preference_applied is not None:
        payload["preferenceApplied"] = preference_applied
    _emit(
        payload,
        output_mode,
        human=(
            f"session {payload['sessionId']}: {payload['executionState']}"
            + (f" ({location})" if location is not None else "")
        ),
    )
    return True


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
        service = build_authentication_service(
            settings,
            PostgresAuthenticationRepository(engine),
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
