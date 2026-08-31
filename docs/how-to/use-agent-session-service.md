# Start and inspect an agent session

Use this guide to launch a durable agent session from an exact agent revision, follow its safe event
trace and retrieve its structured result.

## Configure the CLI

Create an agent revision first with
[Define and pin an agent capability envelope](define-agent-capability-envelope.md). Then configure a
CLI profile and store a scoped API token in the operating-system credential store:

```powershell
uv run amesh config set local --api-url http://127.0.0.1:8000 --tenant default
uv run amesh config use local
$env:AMESH_SERVICE_ACCOUNT_TOKEN = '<scoped-token>'
```

The token needs execution permission for the agent namespace. The profile stores no credential.

## Create the session

Save the agent input as `session-input.json`:

```json
{
  "incident": "API latency exceeded the objective for eight minutes."
}
```

Launch the exact agent revision with one stable idempotency key:

```powershell
uv run amesh session create agents.demo incident-helper `
  --agent-revision 1 `
  --input-file session-input.json `
  --idempotency-key incident-2026-08-29-001 `
  --prefer-async
```

Use `--input-json '{"incident":"..."}'` when the input is short. Both input forms require a JSON
object. The JSON output includes `sessionId` and `location`; save the stable public `sessionId`.
Repeating the command as the same actor with the same tenant, namespace and idempotency key resolves
to the same logical session. Another actor using the same key receives a distinct session identity.

The CLI intentionally has no harness selector. Pi is the current server default, and AMESH records
its exact adapter and protocol pin. A future conformant harness can replace the server default for new
sessions without changing this command or an existing session.

To continue the same canonical session after it succeeds, post another input with a new stable key:

```powershell
$headers = @{
  Authorization = "Bearer $env:AMESH_SERVICE_ACCOUNT_TOKEN"
  "X-Amesh-Tenant" = "default"
  "Idempotency-Key" = "incident-2026-08-29-002"
}
$body = @{ input = @{ question = "What changed since the first result?" } } |
  ConvertTo-Json -Depth 8
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/agent-sessions/<session-id>/messages `
  -Headers $headers -ContentType application/json -Body $body
```

AMESH preserves the public session ID, resumes the last successful checkpoint with its exact pins and
returns the next structured result. Reusing the same key returns that same durable turn. Governed
`image_ref` input is accepted for an image-capable pinned route when the caller can read the exact
namespace artifact.

## Use an OpenAI-compatible client

Point a client at the AMESH base URL and use an exact agent reference as `model`. The agent input
schema must accept `{"messages": [...]}`:

```powershell
$headers = @{
  Authorization = "Bearer $env:AMESH_SERVICE_ACCOUNT_TOKEN"
  "X-Amesh-Tenant" = "default"
  "Idempotency-Key" = "incident-2026-08-29-chat-001"
}
$body = @{
  model = "agents.demo/incident-helper@1"
  messages = @(@{ role = "user"; content = "Summarize the incident." })
} | ConvertTo-Json -Depth 8
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/chat/completions `
  -Headers $headers -ContentType application/json -Body $body
```

For an image-capable pinned agent, replace the user content string with ordered `text` and
`image_url` parts. The supported compatibility subset accepts a base64 data URL only; AMESH stages
it as a governed artifact before the run and does not persist the data URL:

```powershell
$encoded = [Convert]::ToBase64String([IO.File]::ReadAllBytes('.\chart.png'))
$body = @{
  model = "agents.demo/incident-helper@1"
  messages = @(@{
    role = "user"
    content = @(
      @{ type = "text"; text = "Explain this chart." }
      @{ type = "image_url"; image_url = @{ url = "data:image/png;base64,$encoded" } }
    )
  })
} | ConvertTo-Json -Depth 12
```

The pinned agent revision owns model tuning, token and cost ceilings, tools, skills, system prompts
and structured-output schema. Compatibility streaming is buffered until the canonical run completes.
The OpenAI-compatible routes remain request-scoped: continue there by sending another request with
the full desired message history and a new idempotency key. Use the canonical `/messages` route above
when the client needs AMESH to resume the stored checkpoint under the same public session ID.

## Follow progress and read the result

Read the current summary and the first canonical progress page, or watch it live:

```powershell
uv run amesh session get <session-id>
uv run amesh session progress <session-id> --limit 100
uv run amesh session watch <session-id>
```

`progress` returns an opaque `nextCursor`. Pass it back with `--after` only after handling the
preceding page. `watch` consumes bounded NDJSON incrementally and reconnects safely when invoked
again with its last displayed cursor. A previous attempt's terminal event does not hide a later
retry attempt.

The legacy latest-attempt event projection remains available when needed:

```powershell
uv run amesh session events <session-id> --after-event-index 0 --limit 100
```

When the event response contains `nextEventIndex`, pass that value to the next `events` command. The
progress trace exposes safe model, tool, approval, validation, artifact and terminal observations.
It does not
expose prompts, credentials, private checkpoint data or hidden reasoning.

Retrieve the structured terminal output:

```powershell
uv run amesh session result <session-id>
```

The response contains `result` after success or a redacted `error` after failure. Schema validation
makes the result structurally reliable; it does not make LLM text deterministic.

## Pause, resume, cancel or retry

Each control requires an operator reason:

```powershell
uv run amesh session pause <session-id> --reason 'Waiting for operator review'
uv run amesh session resume <session-id> --reason 'Review completed'
uv run amesh session cancel <session-id> --reason 'Request withdrawn'
uv run amesh session retry <session-id> --reason 'Retry approved after provider failure'
```

The server applies the current execution fence by default. For compare-and-set automation, also pass
`--expected-version` and `--expected-epoch` from an immediately preceding execution read. A stale
value fails without applying the control.

## Verify the CLI locally

Run the focused unit suite with locked `uv` dependencies:

```powershell
uv run pytest -q tests/test_agent_session_cli.py
```

Run the supported Docker-local backend gate before pushing:

```powershell
.\scripts\verify-local.ps1 -Suite backend
```

The complete local push gate is documented in [Run local verification](run-local-verification.md).
