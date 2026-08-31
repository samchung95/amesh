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

An invocation may additionally pin a versioned `requiredToolPlan`. Admission expands its ordered
steps deterministically from immutable session input and stores an immutable occurrence ledger in the
checkpoint. Dispatch must match the exact next tool name and canonical arguments before approval or
external I/O, and final output is gated until every occurrence succeeds. Safe projections expose
only plan/occurrence digests and bounded completion metadata. The provider and replaceable harness
remain unaware of this runtime governance contract; see
[ADR-069](docs/adr/069-required-agent-tool-plan-governance.md).

Operator inspection is a read-only projection of this same journal. The list surface returns safe
session summaries; the detail surface returns server-redacted canonical events with exclusive,
stable event-index pagination and bounded payloads. It never exposes checkpoint messages, prompts,
continuations or hidden model reasoning. Frozen replay remains part of the existing backfill engine:
source inputs are copied verbatim only after their digest and exact flow, plugin, determinism-envelope
and admission-policy pins match, and an explicit idempotency key prevents duplicate logical replay.

## Agent memory, evaluation and release boundary

Agent memory and evaluation remain subordinate to `agent.session`. Exact evaluation revisions are
part of the immutable capability pin, while tenant-RLS memory entries carry an explicit execution,
private-agent or named shared scope plus expiry, redaction and provenance. Recalled content is
untrusted user data, never system instruction. Deterministic assertions gate optional judge evidence,
and an ordinary durable approval task remains the human release authority. See
[ADR-054](docs/adr/054-agent-memory-evaluation-and-release-evidence.md).

## Pluggable agent-session harness boundary

The transient agent-loop implementation is replaceable behind a typed, one-turn
`AgentSessionHarness` port. AMESH constructs one exact provider route, model, context snapshot,
budget, timeout, continuation handle and stable invocation key, then exposes that immutable call only
through an AMESH model gateway. A harness cannot change the call before provider I/O and receives no
provider credential value, MCP client, approval service or repository.

Pi 0.84.3 is the required production adapter in both API and recovery-executor composition roots;
there is no built-in runtime fallback. It uses its direct `Agent` API through an isolated Node worker
whose allowlisted process environment excludes provider credentials. Pi's model stream must call back
through the AMESH gateway and any tool request must return to the ordinary AMESH policy, approval,
invocation-journal and checkpoint path. PostgreSQL remains the canonical transcript and session store.
Harness context is always a bounded derived projection; it cannot replace or mutate the accepted
transcript. See
[ADR-058](docs/adr/058-pi-behind-amesh-agent-session-harness-port.md).

The canonical session transcript is append-only. Before each model call AMESH derives a bounded
context by retaining pinned instructions and complete recent action/result pairs, never by editing
the transcript. A content-addressed receipt records the source digest, retained indexes, limits and
headroom. Provider prompt-cache reads, writes, hit ratio and signed cost effect are normalized as
model evidence and remain distinct from task-result caching and invocation replay. The harness
conformance kit exercises this contract through the same public port; it cannot register an implicit
fallback or grant a harness provider credentials, native tools or workflow-state access.

## Multi-tenant agent-session service boundary

The agent-session product is an independently consumable facade over `agent.session`, not another
chat engine. A canonical session request authorizes the actor, resolves one immutable agent revision
and admits one ordinary execution/task/session identity through the existing command handler. The
profile pins exact agent, model-policy, prompt, skill, MCP/tool, output-schema, memory, evaluation,
budget and harness revisions. A pre-existing provider-side fine-tuned model identifier is ordinary
model-profile data; training model weights is not a session-plane responsibility.

```text
canonical client / OpenAI-compatible client
                   |
                   v
        stateless webserver replicas
                   |
       auth + profile resolution + admission
                   |
                   v
 PostgreSQL execution / session / event authority
                   |
        fenced execution worker roles
                   |
                   v
 typed harness port -> Pi today / conformant adapter later
                   |
          AMESH model + tool gateways
```

The OpenAI-compatible surface translates onto the canonical API and documents semantic deviations;
it does not emulate proprietary ChatGPT accounts, stored history or hidden protocols. Session API and
event contracts contain no Pi-specific fields. Pi remains the required current production adapter,
while a future adapter registers behind the existing conformance-tested harness port for new
sessions. An active session retains its exact harness and capability pins and cannot be hot-swapped.

Webserver and execution-worker roles remain stateless. PostgreSQL claims, leases, fencing,
checkpoints, invocation identities and the ordered event journal allow another eligible role to
recover accepted work without sticky sessions. Canonical cursor streams are reconnectable durable
event projections. OpenAI-compatible SSE is emitted only after the bounded canonical execution has
completed; it is not a live provider-token stream. User/tenant authorization, quotas, retention,
cost and cache evidence stay with their existing authorities; no surface exposes prompt bodies,
provider or MCP credentials, checkpoint internals or hidden model reasoning.

See [ADR-066](docs/adr/066-session-plane-over-existing-authorities.md).

## Agent Session Orchestrator administration boundary

The application data plane remains `/api/v1/agent-sessions` plus the documented `/v1/*`
compatibility adapters. A separate administration plane owns fleet queries, session policy,
capacity posture, guarded lifecycle commands and migration coordination. It has session-specific
authorization and UI contracts; it does not accept elevated application-session parameters or use
generic execution management as its permanent public permission model.

```text
application clients                    administrators
        |                                    |
        v                                    v
session data plane                  session administration plane
        |                           fleet / policy / migration
        +-------------------+----------------+
                            v
          canonical execution / session / invocation / event records
                            |
                 PostgreSQL + versioned object storage
                            |
              fenced roles + model/tool/harness gateways
```

Administrative fleet reads are bounded, cursor-paginated projections. Instance-wide views expose
aggregate metadata; protected tenant content requires explicit tenant authorization and audited
drill-down. Lifecycle commands reuse existing execution fencing and audit boundaries. Policies are
versioned inputs to admission rather than mutable fields on an active session.

Profile portability uses content-addressed bundles of exact resource revisions and secret-binding
requirements without resolved credentials. A session is transferable only when terminal or paused
at a clean checkpoint with no ambiguous external invocation. Destination preflight verifies schema,
harness, provider, tool and artifact compatibility before an idempotent import preserves identity,
pins, cursors and evidence. Whole-cluster migration drains admission and moves one coordinated
PostgreSQL/object-storage recovery point; pod or process memory is never migration state.

See [ADR-067](docs/adr/067-separate-session-administration-over-canonical-authorities.md).

## Chronological progress and multimodal input boundary

The agent-session journal is also the ordering authority for live progress. Provider and harness
adapters emit bounded `amesh.agent-progress/v1` frames through an AMESH-owned sink; they cannot write
the journal. Frames contain allowlisted status or provider-declared public-summary detail only. AMESH
commits them beside model, policy, approval, tool, validation, artifact, output and terminal events,
and the accepted journal position—not a provider timestamp—defines chronology. A logical session
cursor includes attempt identity and the attempt-local event index so reconnect traverses retries
without gaps while legacy `afterEventIndex` reads remain compatible. Only adjacent deltas from the
same segment may coalesce in a client projection; any intervening activity closes the segment.

Images are a shared platform value over artifact, workflow, task and plugin contracts. An image
reference wraps a tenant-owned, checksum-pinned namespace `ArtifactRef`; binary content stays in
object storage. Workflow values may propagate that immutable reference through every node input and
output, ordinary expressions, branches, loops and subflows. A consumer resolves bytes only at its
governed invocation boundary and declares image-input capability; model consumers additionally gate
the exact route, provider and harness. OpenRouter is the first qualified model mapping, while the
canonical contract contains no OpenRouter or Pi fields. See
[ADR-068](docs/adr/068-chronological-progress-and-governed-image-inputs.md).

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

Agent authoring extends this same surface with authorized catalog projections for exact agent,
prompt, skill, model-policy, MCP/tool and output-schema revisions. Selectors write canonical
`agent.session` YAML fields, while preview and node testing call the existing resolver, admission,
simulation and flow-test boundaries. The capability catalog and connection wizard aggregate existing
immutable ledgers; they do not create a second registry or persist plaintext secrets. A connection
test is a separate discovery-only projection: it resolves the secret binding at runtime, lists live
tools, compares pinned schema digests, and records only redacted immutable evidence. It never invokes
an MCP tool or expands the connection's effect boundary.

The agent run inspector is a read projection over canonical execution, session, invocation,
approval and evidence records. Realtime updates and contextual pause, cancel, resume, retry and replay
commands use existing APIs. Replay always creates a linked execution with frozen inputs and exact
resource pins; the inspector never infers authority or hidden model rationale from UI state.

## Document and artifact pipeline boundary

Uploaded content enters the existing tenant-scoped object store as a content-addressed typed artifact.
A document extractor is an isolated, version-pinned plugin operation that receives an artifact
reference rather than storage credentials or a host path and returns structured text, metadata and
chunks with exact source locators. Workflow nodes consume that typed result through ordinary task
outputs and evidence. Core owns limits, provenance, retention, tenant isolation and parser policy;
replaceable plugins own format decoding and cannot embed client-domain semantics in the platform.

## External orchestration and qualification boundary

AMESH owns durable schedule evaluation and occurrence launching. A client declares the schedule and
may reference a plugin-provided domain calendar, but it does not own occurrence persistence,
deduplication, retry or scheduler health. Every enabled service role publishes persisted progress
health; a caught background failure can keep a process live while making that role unready. A role
that is intentionally disabled is reported as disabled rather than failed.

External clients use one versioned orchestration profile over the existing REST, realtime, webhook,
CLI and generated-SDK surfaces. Exact workflow revisions, client correlation keys and launch
idempotency keys are durable contract data. The corresponding evidence bundle is a canonical,
bounded projection of pins, state transitions, attempts, sessions, invocations, files, approvals and
usage. Large records are content-addressed outside the response body, cost has explicit billed,
unpriced or unavailable states, and neither credentials nor hidden model rationale are evidence.

Model and tool integrations are replaceable provider ports. Capability negotiation happens before
provider I/O and the selected provider revision is pinned. Opaque continuation state may be stored
for provider-supported resumption but is never exposed as chain-of-thought. MCP and isolated plugin
tools share one ToolProvider policy, schema, journal, timeout, cancellation and ambiguous-outcome
contract; core ships no domain connector merely to support a client use case.

Qualification uses an isolated PostgreSQL/object-storage harness. Restart matrices prove stable
occurrence, invocation, checkpoint and final-output identities. Differential runs pin two exact
configurations and frozen inputs, deny uncontrolled effects and compare deterministic structure
separately from declared model nondeterminism. Promotion binds a client-defined policy to fresh,
immutable evidence and an exact configuration digest; AMESH enforces preview, apply, rollback and
kill-switch authority but does not choose the client's thresholds or perform its external cutover.

The hardened client-driven local profile is loopback-only, uses real scoped authentication, has no
Docker socket or Docker runner, and contains no client-domain credentials. It is a specifically
qualified local boundary, not a claim of public-cloud, multi-region or independent production
certification.

## Local execution recovery and protected-trigger boundary

Fresh nonterminal executions are immediately eligible for split-role dispatch unless a persisted
running attempt shows that another executor may still own work; only that running-work case receives
the configured recovery grace and existing fencing checks. The split executor composes the same
subflow, approval and isolated-plugin handlers as the API composition root, while PostgreSQL remains
the only execution authority.

Trigger occurrences keep a redacted payload as their public/audit projection and, only when required
for later execution, a separately encrypted recoverable payload. The trigger runtime decrypts that
payload only at the execution boundary; list, replay and evidence surfaces continue to expose the
redacted projection. Browser route and authentication changes discard route- or principal-scoped
client state, and the Docker task runner enforces the common bounded-output contract. See
[ADR-063](docs/adr/063-local-recovery-and-protected-trigger-payloads.md).

## Local verification boundary

Repository verification is developer-invoked and Docker-local. A dedicated verification image owns
the locked Python, Node, frontend and Pi toolchains and runs core tests, static checks, generated
contract checks and harness qualification against the checked-out source. Separately named Docker
suites own compatibility matrices that need PostgreSQL versions or additional SDK/provider tools.
The production image remains free of development dependencies. Verification never receives GitHub
credentials and never publishes packages, releases or attestations. A tracked native pre-push hook,
enabled explicitly per clone, invokes the same complete aggregate and propagates failure to Git; it
does not create a remote enforcement boundary. See
[ADR-062](docs/adr/062-docker-local-verification-without-github-actions.md) and
[ADR-065](docs/adr/065-native-pre-push-docker-gate.md).

## MVP executor boundary

The executor derives runnable tasks from the validated top-level DAG and persisted task-run states; it does not keep authoritative progress in memory. The execution repository creates one stable task-run identity per execution/task path, records every attempt separately and stores task results before dependants become eligible. In-process MVP handlers prove orchestration with `core.return` and `core.log`; W3 replaces the handler edge with fenced runner dispatch without changing DAG readiness or persisted state. Dropping an executor process loses no scheduler state: a replacement reloads successful task runs, skips them and continues the remaining graph.

Retry eligibility is persisted as `task_runs.retry_at`; backoff is never an in-memory timer of record. Each attempt number is its fencing token for the MVP. The local-process runner owns subprocess creation, output capture, timeout and cancellation, while the execution repository accepts a result only when the task run is still running at that exact attempt. A timed-out, cancelled or superseded process may exit later, but its stale result cannot change task state.

W4 keeps expression evaluation deterministic and side-effect free: the native Jinja sandbox receives only `inputs`, successful task `outputs` and flow `vars`, and renders a task immediately before its attempt handler runs. Cron calculation is stateless; durable uniqueness comes from a stable execution idempotency key derived from the tenant, flow revision, trigger and scheduled UTC instant. The execution row, initial events and task runs are created in one PostgreSQL transaction, so concurrent or restarted scheduler instances converge on one execution per occurrence without introducing a second scheduler database.

W6 exposes this executor through the authenticated MVP REST and CLI surfaces and supplies trusted in-process HTTP, OpenAI-compatible LLM and MCP handlers. W7 packages one uv-locked image into three Helm roles: an idempotent migration hook, an API server and a delayed recovery worker. Both runtime roles use PostgreSQL as authority and reconcile Kubernetes task Jobs through namespace-scoped RBAC. The server publishes Prometheus metrics and both processes emit JSON log records; PostgreSQL remains an external chart dependency.

W5 implements the same `TaskRunner` port with Kubernetes Jobs. A stable attempt identity maps to one deterministic owned Job name; recreating a runner reads that Job instead of duplicating it. The Job controller replaces a deleted pod, while the runner reconciles Job status, captures the terminal pod log and exit code, and performs idempotent foreground deletion after success, failure, timeout or fenced cancellation. PostgreSQL still decides whether the attempt result is current—the Kubernetes API never becomes orchestration state.

Detailed decisions remain in `docs/architecture/` and `docs/adr/`; this page is the cold-start system map.
