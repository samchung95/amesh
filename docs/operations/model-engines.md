# Operate subscription-backed model engines

This runbook covers deployment and administration of the OpenAI Codex App Server and GitHub
Copilot CLI adapters. Both are optional local processes supervised by AMESH. PostgreSQL remains the
authority for workflows, sessions, invocations, progress, usage and audit events.

## Pin the runtime commands

Configure the command as an argv tuple, not a shell string. The defaults are:

```text
MODEL_ENGINE_CODEX_COMMAND=["codex", "app-server", "--stdio"]
MODEL_ENGINE_COPILOT_COMMAND=["copilot"]
```

Resolve the first executable through the operating-system `PATH`; AMESH rejects empty or NUL
containing command entries. Pin the installed versions in the deployment image or host and record
them with the qualification evidence. The reference qualification observed `codex-cli 0.151.0`
and `GitHub Copilot CLI 1.0.82`; these are examples of pinned versions, not an automatic upgrade
promise. The adapters use Codex JSON-RPC/JSONL and Copilot JSONL programmatic output contracts.

On Windows, install the CLIs for the same account that runs the AMESH API/worker service and ensure
the executable (`codex`/`copilot`, or the configured command's first entry) is resolvable by that
service's `PATH`. A CLI visible only in an interactive terminal is not sufficient. Do not put
PowerShell metacharacters into command entries; AMESH starts the process directly without a shell.

The reference AMESH runtime image does not bundle these optional account CLIs. A container operator
must build a derived image containing the pinned commands and mount one protected persistent
`MODEL_ENGINE_STATE_ROOT` into both the API role (login/status/logout) and every executor role that
can run model work. Keep the same command revisions and state-root mapping across those roles.

## Isolate state and identities

Set `MODEL_ENGINE_STATE_ROOT` to a server-owned directory writable only by the AMESH service. AMESH
derives a separate state directory from tenant, namespace, adapter and `engineRef`; clients cannot
submit an arbitrary path. Each child process receives only its derived `CODEX_HOME` or
`COPILOT_HOME`, a minimal environment and a temporary empty working directory. Configure a distinct
runtime identity/container per tenant when the host keyring is shared.

Namespace authorization does not turn one binding into separate end-user accounts. Provision a
distinct `engineRef` and corresponding authorization grant for every user identity that must have an
independent subscription login; never share a team binding when individual account isolation is
required.

Copilot CLI may store credentials in the operating-system keyring or, when no keyring is available,
in plaintext under `COPILOT_HOME`. `COPILOT_HOME` isolates the directory but does not by itself
isolate a shared OS keyring. For multi-user deployments, use a dedicated service account, isolated
keyring/container and filesystem permissions; never rely on the host operator's default Copilot
login. Codex and Copilot refresh credentials remain owned by their runtimes and never enter AMESH
configuration, logs, flows, checkpoints or API responses.

## Process policy and health

`MODEL_ENGINE_MAX_FRAME_BYTES`, `MODEL_ENGINE_TIMEOUT_SECONDS` and
`MODEL_ENGINE_CANCEL_GRACE_SECONDS` bound process I/O and shutdown. AMESH disables native tools,
MCP servers, plugins, web/search integrations and approval escalation in the adapter invocation;
the process can return model content or an AMESH-validated result, but cannot bypass AMESH tool
policy. Keep the service account's OS permissions limited to the derived state root and temporary
working area. The adapter's capability declaration is authoritative for pre-I/O negotiation.

Use the account API to inspect safe readiness and provider-reported metadata:

```text
GET /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engineRef}/status
```

`authenticated: null` is an honest unknown state when a runtime cannot prove readiness after a
restart. It is not a successful login. Login, status and logout are audited with tenant, namespace,
adapter, binding and outcome only.

## Migration

1. Stop new work that selects the binding and let active external invocations settle.
2. Record the adapter revision, configured command/version, tenant/namespace/`engineRef` bindings,
   and the provider's account/quota status without exporting credentials.
3. Copy only the runtime-owned state through an administrator-controlled protected channel, or
   start a fresh login on the destination. Never copy a default user's home into another tenant.
4. Set the same `MODEL_ENGINE_STATE_ROOT` policy and pinned command on the destination, then run the
   account status and provider-free conformance checks.
5. Complete browser/device approval on the destination if the runtime requires it, and resume new
   work only after `authenticated: true` and the route/capability preflight pass.

AMESH does not promise portable provider refresh tokens or portable OS-keyring entries. A fresh
    destination login is the supported fallback.

## Live qualification without secrets

Live qualification is opt-in and must be run by an operator who owns the provider account. Use a
throwaway tenant/namespace and an isolated state root. Record only adapter/version, model name,
capability result, safe usage/quota fields, terminal status, and evidence IDs. Do not capture login
URLs after use, user codes, tokens, cookies, keyring exports, raw prompts or raw provider output.

The qualification must prove:

- browser/device login requires explicit human approval and status becomes truthful after completion;
- one tenant binding cannot read another binding's state;
- structured output and image references are validated through AMESH;
- progress, usage, timeout, cancellation and restart behavior are recorded;
- native tools, MCP and filesystem access are not delegated;
- unavailable cost/cache/continuation/embedding claims fail or remain explicitly unavailable.

Run the normal Docker-local aggregate after the provider-free checks. A live subscription check is
not a replacement for the deterministic fake-adapter tests or the local gate.
