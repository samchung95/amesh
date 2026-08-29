# Operate the agent session service

Use this runbook to deploy, observe and recover the provider-neutral session surface while preserving
the existing AMESH execution and evidence authorities.

## Deployment boundary

The session routes run on the stateless `webserver` role. Accepted work uses the ordinary PostgreSQL
execution, task-run, checkpoint, invocation and event paths and the existing executor/worker roles.
Scale webserver replicas for authenticated session API and stream traffic, and scale execution roles
for admitted work. Do not add sticky-session routing or a separate transcript database.

PostgreSQL remains the authority for accepted sessions, leases, fencing, event cursors and results.
Object storage remains the authority for oversized retained artifacts. A webserver or worker restart
must recover from those durable records rather than process memory.

## Harness selection

`AGENT_SESSION_HARNESS=pi` is the current default. Pi `0.84.3` runs behind the typed
`AgentSessionHarness` port and the `amesh.pi-worker/v1` protocol. Inspect safe registered provenance
with:

```text
GET /api/v1/agent-sessions/harnesses
```

An unknown configured adapter fails closed. To introduce a future harness, implement the existing
port, register its factory and public adapter/version/protocol metadata, and pass the provider-free
conformance suite before selecting it for new sessions. Do not pass provider, MCP or platform
credentials to the harness. Do not switch the harness pin of an active session.

Run the current conformance gate locally:

```powershell
uv sync --extra runtime --extra dev --locked
npm ci --prefix harnesses/pi
uv run python scripts/run_agent_harness_conformance.py --adapter pi `
  --output .artifacts/harness-report.json
```

## Readiness and investigation

Use `GET /health` only for process liveness. Use `GET /ready` to check PostgreSQL, migrations,
storage and enabled role progress. Use `GET /metrics`, structured logs and traces for aggregate
operation latency, database pressure, queue age and worker capacity. Session-specific investigation
starts with the tenant-authorized session summary, durable event cursor and execution evidence:

```text
GET /api/v1/agent-sessions/{sessionId}
GET /api/v1/agent-sessions/{sessionId}/events?afterEventIndex=0&limit=100
GET /api/v1/executions/{executionId}/evidence-bundle
```

Alert on increasing queue age, provider failures, exhausted token/cost/turn/tool budgets, repeated
lease recovery and sessions that do not converge. Keep session, execution and tenant identifiers in
logs or traces rather than Prometheus labels.

## Recovery and controls

1. Stop accepting new traffic only when the dependency or execution role is unsafe; a telemetry
   exporter outage alone does not justify stopping sessions.
2. Restore PostgreSQL connectivity and verify migrations before replacing API or worker replicas.
3. Read the session event cursor and execution state. Never infer acceptance from a disconnected HTTP
   client.
4. Let expired claims and leases be reclaimed through the existing fenced recovery path.
5. Use `pause`, `resume`, `cancel` or `retry` with an operator reason. Include execution version and
   epoch only when the caller deliberately wants compare-and-set rejection.
6. Confirm the terminal result and evidence before declaring recovery complete.

AMESH reuses completed primitive invocation identities and fails ambiguous external work closed. An
operator retry is not permission to bypass tool authorization, approval, egress or budget policy.

## Security and retention

Authorize every session by actor, tenant and namespace. The harness must not receive provider or MCP
credentials, execute tools directly, persist an authoritative transcript or write workflow state.
Public events and results exclude hidden reasoning, prompts, provider continuations and private
checkpoints. Fine-tuned model IDs are model-policy configuration; model training is not operated by
this service.

Apply existing execution, audit and artifact retention policies to the canonical records. A session
facade must not delete or retain a parallel copy independently.

## Opt-in local reference qualification

The synthetic local reference profile uses isolated, fully migrated PostgreSQL tables and the real
tenant-scoped session projection and advisory guard. Its defaults are 10,000 durable terminal
sessions, 1,000 concurrent logical event-cursor readers and three stateless projection replicas.
The full profile is intentionally opt-in because it is a local capacity measurement, not a fast
unit-test workload.

Run it through the Docker verification image and retain the machine-readable report on the host:

```powershell
New-Item -ItemType Directory -Force .artifacts | Out-Null
docker compose -f compose.verify.yaml up -d --wait postgres
docker compose -f compose.verify.yaml build verify
docker compose -f compose.verify.yaml run --rm --no-deps `
  --entrypoint uv `
  -e AMESH_TEST_DATABASE_URL=postgresql+asyncpg://amesh:amesh@postgres:5432/amesh `
  -v "${PWD}/.artifacts:/workspace/.artifacts" `
  verify run --frozen --extra runtime --extra dev python `
  scripts/qualify_agent_session_service.py `
  --output .artifacts/agent-session-reference.json
```

For a quick live PostgreSQL smoke, add `--durable-sessions 12
--concurrent-stream-readers 6 --replicas 3`. The utility creates and drops only an
`amesh_test_*` database unless `--retain-database` is supplied.

The report records the available container hardware, PostgreSQL version, seed and cursor latency,
and explicit counts for missing seeded final-result projections, duplicate session-guard claims and
cross-tenant event visibility. Because the utility seeds terminal projections directly, this is not
an accepted-work recovery or loss test. It does not include model/provider latency, remote
load-balancer or socket behavior, or production HA, backup, restore and disaster-recovery
qualification. Do not interpret its local latency as a production SLO.

## Docker-local release gate

Run the complete supported gate before pushing the feature:

```powershell
.\scripts\verify-local.ps1 -Suite all
```

The gate runs backend tests, frontend tests/build, Pi tests and conformance, contract drift checks,
Compose validation, production-image probing and local packaging without GitHub Actions or cloud
credentials. The live OpenRouter Luna smoke is opt-in and is not part of the offline default gate.

See [Agent session service API](../api/agent-session-service.md) for the wire contract and
[High-availability operations](high-availability.md) for role placement and fencing.
