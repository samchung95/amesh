# AMESH architecture

AMESH is a Python 3.12 asyncio control plane whose correctness comes from a pure reducer, PostgreSQL transactions, idempotent messages, expiring leases and fencing tokens. PostgreSQL is authoritative; notifications, workers and external model providers are replaceable edges.

```text
YAML / CLI / REST / webhooks
            |
            v
    validation + expressions
            |
            v
 command handler -> PostgreSQL <- scheduler / reconciler
       |          events, queue,         |
       |          inbox, outbox          |
       +----------------+----------------+
                        |
                  fenced claims
                        v
        local worker / Kubernetes Job worker
                        |
          process, HTTP, LLM and MCP tasks
                        |
                 logs + task results
```

## Component boundaries

- `domain` contains immutable execution and task state plus pure transition functions; it has no framework or database imports.
- `domain.identity` and `domain.resources` own canonical natural-key validation, UUIDv7 runtime identity, managed-resource metadata, lifecycle transitions, concurrency tags and canonical hashing. Every API, repository and future UI/auth module consumes these contracts rather than defining local variants.
- `domain.authorization` owns actors, permissions, roles, scoped bindings, namespace boundaries and deterministic deny-overrides evaluation. PostgreSQL policy rows and a monotonic policy version are authoritative; REST, CLI and non-human callers consume one authorization service rather than embedding local permission checks.
- `domain.authentication` owns local credential and browser-session contracts without making authorization decisions. A provider-neutral authentication port resolves an external identity to an existing user principal; the local adapter verifies Argon2id password hashes, while later OIDC, SAML and LDAP adapters remain replaceable edges.
- `dsl` parses and validates the MVP YAML model and native expression references.
- `ports` defines transport, runner and plugin contracts.
- `adapters` implements PostgreSQL, process, Kubernetes and external-provider boundaries.
- `api` and `cli` translate user requests into application commands and return persisted state.
- PostgreSQL owns accepted commands, executions, events, task attempts, schedules, inbox/outbox messages and durable work claims.

## Data and failure flow

Execution transitions append their events in the same database transaction. The transport adapter provides separately verified transactional outbox publication, durable inbox deduplication and fenced queue claims. The MVP recovery worker scans persisted running executions and reconciles their deterministic Kubernetes Jobs; task and execution results commit only while the persisted attempt and execution epoch still match. Duplicate commands and messages return the previously persisted logical result. When PostgreSQL is unavailable, AMESH acknowledges no state-changing request. OpenRouter and MCP failures remain task failures or retries and never mutate orchestration state directly.

Interactive login follows the same PostgreSQL-authoritative boundary. The browser submits a provider, user handle and secret to the authentication service; successful local verification returns a random opaque session whose keyed digest, CSRF digest, principal credential epoch, idle deadline, absolute deadline and revocation state are stored in PostgreSQL. The browser receives only a same-site HTTP-only session cookie and a separate CSRF value. Every authenticated unsafe request must match the CSRF cookie and header before authorization runs. Password rotation, user disablement, logout and global revocation fence existing sessions through the persisted principal epoch or session state. Invalid, locked, expired and unknown identities return the same public failure while bounded metrics and secret-free audit evidence retain the internal reason.

## Bounded model and MCP primitive boundary

`agent.chat`, `agent.embedding`, `agent.structured` and `agent.toolCall` resolve an explicit provider,
credential scope, model, budget, timeout, retry and data-handling policy before calling a replaceable
model adapter. Every attempt opens a PostgreSQL invocation record before provider I/O and stores the
validated result plus redacted provenance before the executor commits the task result. A completed
attempt is reusable after restart; an in-flight attempt is reported as an ambiguous external outcome
rather than silently repeated. Model output is always labelled nondeterministic.

`agent.mcp` resolves a tenant-and-namespace-scoped connection revision. The worker authenticates with
a runtime-only secret, discovers the live tool schema, verifies it against the revision pin, enforces
the tool allowlist and impact policy, then journals the call. The model and MCP transports never write
execution state. AMESH's own authenticated MCP server exposes only authorization-checked application
operations; its first surface is read-only workflow and execution inspection.

## Versioned agent resource boundary

Prompts, skills, model policies and agent definitions share one tenant-and-namespace-scoped immutable
revision ledger. Each revision is validated by a kind-specific domain contract before persistence;
plaintext credentials and executable skill payloads are not valid resource fields. Agent definitions
refer to exact prompt, skill and model-policy revisions plus exact MCP connection revisions.

One resolver loads those revisions in a single PostgreSQL transaction, verifies authorization and
cross-resource invariants, intersects requested tools/skills with the declared permission boundary,
and persists a content-addressed capability-envelope pin. Future agent sessions consume only that
pin. Provider fallback order is data inside the pinned model policy; changing provider/model policy
creates a new revision and an explicit nondeterminism/migration diagnostic rather than silently
changing durable workflow semantics.

## Durable bounded agent-session boundary

`agent.session` is a recoverable task inside the existing execution state machine, not a second
workflow engine. Before its first turn it resolves an exact agent revision into the immutable
capability pin. A PostgreSQL session row stores the latest checkpoint and cumulative budgets, while
an idempotent ordered event journal projects model turns, tool proposals/results, policy decisions,
approval observations and schema decisions into ordinary execution evidence.

Each model response can propose one pinned MCP tool or a final structured result. AMESH validates
the proposal, enforces the pinned tool and authority boundary, and dispatches one operation at a
time through the existing model and MCP invocation journal. Stable session operation keys let a
restarted task reuse accepted calls; an unfinished external call is surfaced as an ambiguous outcome
and is never silently repeated. Hard turns, loops, tool calls, tokens, cost and duration are checked
between calls, independently of model compliance. High-impact tools require an approved direct task
dependency, and success requires the pinned output schema plus configured deterministic assertions.

## Agent memory, evaluation and release boundary

Agent memory and evaluation remain subordinate to `agent.session`. Exact evaluation revisions are
part of the immutable capability pin, while tenant-RLS memory entries carry an explicit execution,
private-agent or named shared scope plus expiry, redaction and provenance. Recalled content is
untrusted user data, never system instruction. Deterministic assertions gate optional judge evidence,
and an ordinary durable approval task remains the human release authority. See
[ADR-054](docs/adr/054-agent-memory-evaluation-and-release-evidence.md).

## Agent mesh boundary

`agent.mesh` is a static flowable over the existing durable task graph. Its declared supervisor,
router, peer-to-peer, hierarchical or swarm members map one-to-one to exact `agent.session` children;
ordinary dependencies and conditions define execution order. Parent and member reservations compose
with pinned agent limits, so the tighter token, cost, duration and tool ceiling always wins.

`agent.route` gates exact candidates by capability, policy and availability before deterministic
evaluation/cost/latency ordering. `agent.handoff` validates and redacts selected context between an
exact completed source and directly dependent destination. Both publish ordinary task results and
the mesh parent aggregates their provenance and session usage. Models cannot mutate the task graph,
route policy or budgets. See
[ADR-055](docs/adr/055-static-agent-mesh-on-durable-task-graph.md).

## Guided workflow authoring boundary

Guided creation, the visual editor and the code editor are projections over one canonical YAML
document. The guide applies narrow round-trip edits to that document and derives its displayed state
from the document whenever the user changes modes; it never persists a second workflow definition.
Catalog-backed controls expose installed task and trigger schemas, while unsupported or code-only
fields remain intact and are identified as advanced content rather than discarded.

The authoring readiness path composes existing boundaries: schema validation, policy admission,
side-effect-free simulation and isolated flow tests run before an explicit execution launch. Saving
creates the ordinary immutable revision. “Run now” launches that saved revision and navigates to its
persisted execution trace, so the guided path cannot bypass revision, authorization, policy or
execution evidence contracts.

## MVP executor boundary

The executor derives runnable tasks from the validated top-level DAG and persisted task-run states; it does not keep authoritative progress in memory. The execution repository creates one stable task-run identity per execution/task path, records every attempt separately and stores task results before dependants become eligible. In-process MVP handlers prove orchestration with `core.return` and `core.log`; W3 replaces the handler edge with fenced runner dispatch without changing DAG readiness or persisted state. Dropping an executor process loses no scheduler state: a replacement reloads successful task runs, skips them and continues the remaining graph.

Retry eligibility is persisted as `task_runs.retry_at`; backoff is never an in-memory timer of record. Each attempt number is its fencing token for the MVP. The local-process runner owns subprocess creation, output capture, timeout and cancellation, while the execution repository accepts a result only when the task run is still running at that exact attempt. A timed-out, cancelled or superseded process may exit later, but its stale result cannot change task state.

W4 keeps expression evaluation deterministic and side-effect free: the native Jinja sandbox receives only `inputs`, successful task `outputs` and flow `vars`, and renders a task immediately before its attempt handler runs. Cron calculation is stateless; durable uniqueness comes from a stable execution idempotency key derived from the tenant, flow revision, trigger and scheduled UTC instant. The execution row, initial events and task runs are created in one PostgreSQL transaction, so concurrent or restarted scheduler instances converge on one execution per occurrence without introducing a second scheduler database.

W6 exposes this executor through the authenticated MVP REST and CLI surfaces and supplies trusted in-process HTTP, OpenAI-compatible LLM and MCP handlers. W7 packages one uv-locked image into three Helm roles: an idempotent migration hook, an API server and a delayed recovery worker. Both runtime roles use PostgreSQL as authority and reconcile Kubernetes task Jobs through namespace-scoped RBAC. The server publishes Prometheus metrics and both processes emit JSON log records; PostgreSQL remains an external chart dependency.

W5 implements the same `TaskRunner` port with Kubernetes Jobs. A stable attempt identity maps to one deterministic owned Job name; recreating a runner reads that Job instead of duplicating it. The Job controller replaces a deleted pod, while the runner reconciles Job status, captures the terminal pod log and exit code, and performs idempotent foreground deletion after success, failure, timeout or fenced cancellation. PostgreSQL still decides whether the attempt result is current—the Kubernetes API never becomes orchestration state.

Detailed decisions remain in `docs/architecture/` and `docs/adr/`; this page is the cold-start system map.
