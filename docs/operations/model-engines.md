# Operate subscription-backed model engines

This runbook covers deployment and administration of the OpenAI Codex App Server and GitHub
Copilot CLI adapters. Both are optional local processes supervised by AMESH. PostgreSQL remains the
authority for workflows, sessions, invocations, progress, usage and audit events.

## Pin the runtime commands

Configure the command as an argv tuple, not a shell string. The defaults are:

```yaml
model_engine_codex_command: ["codex", "app-server", "--stdio"]
model_engine_copilot_command: ["copilot"]
```

Resolve the first executable through the operating-system `PATH`; AMESH rejects empty or NUL
containing command entries. On Windows, Copilot resolution skips the VS Code extension's
install/update bootstrapper and selects an installed native CLI or npm `copilot.cmd`; if no safe
CLI is available, startup fails without opening an installer prompt. Managed Copilot processes also
receive `COPILOT_AUTO_UPDATE=false`. Pin the installed versions in the deployment image or host and
record them with the qualification evidence. The reference qualification observed `codex-cli
0.151.0` and `GitHub Copilot CLI 1.0.82`; these are examples of pinned versions, not an automatic
upgrade promise. The adapters use Codex JSON-RPC/JSONL and Copilot JSONL programmatic output
contracts.

On Windows, install the CLIs for the same account that runs the AMESH API/worker service and ensure
the executable (`codex`/`copilot`, or the configured command's first entry) is resolvable by that
service's `PATH`. A CLI visible only in an interactive terminal is not sufficient. Do not put
PowerShell metacharacters into command entries; AMESH starts the process directly without a shell.

The default AMESH runtime image does not bundle these optional account CLIs. The checked-in
`runtime-model-engines` target installs the exact versions locked in
`docker/model-engines/package-lock.json`, and the optional Compose overlay assigns that image and one
protected state volume to the API and executor roles:

```bash
docker compose -f compose.yaml -f docker/compose.model-engines.yaml up -d --build
docker compose -f compose.yaml -f docker/compose.model-engines.yaml exec -T api codex --version
docker compose -f compose.yaml -f docker/compose.model-engines.yaml exec -T api copilot --version
```

Use the same overlay on later `up`, `stop`, `logs` and `down` commands. Do not add `-v` to `down`
unless you intend to erase the isolated provider login state along with every other named volume in
the project. The overlay mounts `/var/lib/amesh/model-engines` into both the API role
(login/status/logout and synchronous session work) and the executor role (workflow model work).
Scheduler, indexer, maintenance and lease-worker roles do not receive provider account state.

The pinned packages are the official `@openai/codex` Apache-2.0 distribution and GitHub's
`@github/copilot` distribution, whose separate license terms apply. Updating either version requires
refreshing the lock file and rerunning the provider-free and opt-in live qualification.

The image also includes `/usr/bin/script`, used only to give the official Copilot login prompt a
terminal in a headless container. It does not wrap model invocations or execute workflow-supplied
shell text.

## Isolate state and identities

Set `MODEL_ENGINE_STATE_ROOT` to a server-owned directory writable only by the AMESH service. AMESH
derives a separate state directory from tenant, namespace, adapter and `engineRef`; clients cannot
submit an arbitrary path. Each child process receives only its derived `CODEX_HOME` or
`COPILOT_HOME`, a temporary empty working directory and an allowlisted host environment. The shared
Codex, Copilot and Pi process boundary passes only `COMSPEC`, `LANG`, `LC_ALL`, `PATH`, `PATHEXT`,
`SYSTEMROOT`, `TEMP`, `TMP`, `TMPDIR`, `TZ` and `WINDIR` when present. Operators may override only
that same set through the JSON object in `MODEL_ENGINE_ENVIRONMENT`; unrelated host variables and
provider secrets are never inherited by a child process. Configure a distinct runtime
identity/container per tenant when the host keyring is shared.

Namespace authorization does not turn one binding into separate end-user accounts. Provision a
distinct `engineRef` and corresponding authorization grant for every user identity that must have an
independent subscription login; never share a team binding when individual account isolation is
required.

Copilot CLI prefers the operating-system keyring. Plaintext fallback under `COPILOT_HOME` is
disabled unless `MODEL_ENGINE_COPILOT_ALLOW_PLAINTEXT_TOKEN_STORAGE=true`. The checked-in local
overlay sets that opt-in because its headless containers have no keyring and its shared
model-engine volume is owned by the unprivileged AMESH identity with mode `0700`. Keep the setting
false when a keyring is available. For multi-user deployments, use a dedicated service account,
isolated keyring/container, encrypted or equivalently protected storage and filesystem permissions;
never rely on the host operator's default Copilot login. Codex and Copilot refresh credentials
remain owned by their runtimes and never enter AMESH configuration, logs, flows, checkpoints or API
responses.

For the checked-in local overlay, start each login through the namespace account API after the final
deployment is running. Use device mode for the headless containers, complete the returned provider
approval yourself, and poll the same binding's status until `authenticated: true`. A normal
workstation login is never copied or mounted automatically. For a local administrator-authorized
test bootstrap, an existing CLI credential may instead be imported once into the derived binding
home. Treat that as a credential migration: keep the home owner-only, never print or commit the
credential, and validate the binding with a harmless model invocation afterward.

## Process policy and health

`MODEL_ENGINE_MAX_FRAME_BYTES`, `MODEL_ENGINE_TIMEOUT_SECONDS` and
`MODEL_ENGINE_CANCEL_GRACE_SECONDS` apply through one managed-process lifecycle shared by Codex,
Copilot and Pi. Incoming JSONL frames are rejected while streaming when they exceed the configured
limit, including in the Pi Node bridge. A request without its own timeout uses the configured model
engine timeout for each process I/O operation without imposing a new total request deadline. Normal
completion, cancellation and timeout all close pipes, terminate the child, wait for the configured
grace period and then kill a child that remains alive. AMESH disables
native tools, MCP servers, plugins, web/search integrations and approval escalation in the adapter
invocation; the process can return model content or an AMESH-validated result, but cannot bypass
AMESH tool policy. Keep the service account's OS permissions limited to the derived state root and
temporary working area. The adapter's capability declaration is authoritative for pre-I/O
negotiation.

Direct OpenRouter fallback configuration is loaded through the same typed Settings snapshot as the
model-engine boundary. Configure `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` and, when required, the
chat-completions or embeddings URL. The API key remains in the AMESH process and is not placed in a
Codex, Copilot or Pi child environment.

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
