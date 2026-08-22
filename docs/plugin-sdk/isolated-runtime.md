# Isolated plugin runtime

AMESH can execute an exact revision-pinned plugin package in a child process instead of importing
third-party code into the API, scheduler, executor, worker, or database process. The reference
launcher uses JSON-RPC 2.0 newline-delimited frames over stdin/stdout and wire version
`amesh.plugin.wire/v1`.

## Runtime configuration

Set `ISOLATED_PLUGIN_SERVICES` to a JSON array. Every item is an administrator-controlled exact
package identity; flow authors cannot change the command or its limits.

```json
[
  {
    "name": "acme.transform",
    "version": "1.2.3",
    "contentDigest": "sha256:<64 lowercase hex characters>",
    "launcher": "local-process",
    "command": ["python", "service.py"],
    "platformApis": ["artifacts.write"],
    "startupTimeoutSeconds": 10,
    "heartbeatTimeoutSeconds": 5,
    "wallTimeSeconds": 300,
    "cancelGraceSeconds": 1,
    "tokenTtlSeconds": 600,
    "maxOutputBytes": 8388608,
    "memoryBytes": 268435456,
    "cpuSeconds": 120,
    "maxConcurrency": 4
  }
]
```

The package must be present in the configured plugin catalog with the same name, semantic version,
and content digest. A package cannot be configured in both the trusted in-process and isolated
tiers. The local-process launcher requires manifest entry points to use `stdio` transport. Relative
command paths resolve inside the package root; the child receives a minimal environment plus only
the explicitly configured environment values.

## Session and call sequence

One managed process serves one invocation:

1. `amesh.handshake` selects `amesh.plugin.wire/v1`, verifies all required features, and binds a
   random session ID plus short-lived workload token to the exact package digest.
2. `amesh.discover` returns entry-point schemas and identities. AMESH rejects a response that differs
   from the catalog manifest.
3. `amesh.validate` validates the task configuration before execution.
4. `amesh.invoke` runs the handler. The plugin emits authenticated `amesh.heartbeat`, `amesh.log`,
   `amesh.metric`, and `amesh.artifact` notifications before its final response.
5. AMESH sends `amesh.cancel` when the durable execution requests cancellation and
   `amesh.shutdown` during normal teardown.

Every response and notification after the handshake must echo the session ID and workload token.
The token travels through the private stdin/stdout channel, is never placed in the child environment,
and expires at the configured TTL. Protocol and feature negotiation fails closed.

The normative generated schema is `schemas/plugin-wire.schema.json`. Contract surfaces are provided
for Python in `amesh.plugin_sdk` and for TypeScript, Java, and Go under `sdks/plugin-wire/`.

## Python service

```python
import asyncio

from amesh.plugin_sdk import (
    PluginOperation,
    PluginResponse,
    serve_stdio_plugin,
)


async def execute(request, capabilities):
    # Only declared and available secrets/files are present in capabilities.
    return PluginResponse(
        invocationId=request.session.invocation_id,
        output={"accepted": True},
    )


asyncio.run(
    serve_stdio_plugin(
        manifest,
        {("main", PluginOperation.EXECUTE): execute},
    )
)
```

Return `ProcessPluginResult` to attach typed metrics and internal object-storage artifacts. Logs in a
`PluginResponse` are emitted as authenticated log notifications.

## Capability boundary

The invocation envelope contains fresh opaque tokens for the manifest's declared capabilities,
only secret scopes both declared by the manifest and resolved for the current task, files only when
filesystem access is declared, the exact declared egress destinations, and administrator-approved
platform APIs. Undeclared task secrets and files are not serialized into the child request.

This is a capability grant, not an operating-system network sandbox. For adversarial code, run the
same wire service through a separately administered OCI or remote isolation boundary; the current
reference launcher is the managed local-process profile.

## Limits, failure, and recovery

AMESH enforces configured concurrency with a per-package semaphore; wall time with an invocation
deadline; combined stdout/stderr and frame limits while streaming; and child-process-tree CPU and
resident-memory limits. Heartbeat silence, broken pipes, and unexpected EOF are retryable service
crashes. Wall-time and cancellation retain their distinct durable failure categories. CPU, memory,
and output violations are user-code failures.

Each retry starts a fresh authenticated process while the executor retains the existing task run and
increments its durable attempt. Runtime status is available to authorized plugin viewers at
`GET /api/v1/plugins/isolated-runtime`; counters include starts, crash-triggered restarts, crashes,
completed calls, active calls, last PID, and the last stable error code.

## Operational validation

Use the following checks before enabling a package:

```powershell
uv run pytest -q tests/plugins/test_isolated_runtime.py tests/plugins/test_wire_sdks.py
uv run python scripts/generate_contracts.py
uv run pytest -q tests/test_generated_contracts.py
```

Compile the Java contract with JDK 21, the Go module with Go 1.23, and the TypeScript contract in
strict mode with TypeScript 5 or later. Pin commands to immutable package content, keep capability
and network grants narrow, and investigate any `degraded` runtime status before increasing retry
budgets.
