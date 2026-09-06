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

- `domain` contains immutable execution and task state plus pure transition functions. It has no web or database framework imports; Pydantic validates its immutable wire contracts. Runtime shells use `executor.trace_context.attach_current_trace_context` to attach ambient trace context before submitting domain commands.
- `domain.identity` and `domain.resources` own canonical natural-key validation, UUIDv7 runtime identity, managed-resource metadata, lifecycle transitions, concurrency tags and canonical hashing. Every API, repository and future UI/auth module consumes these contracts rather than defining local variants.
- `domain.authorization` owns actors, permissions, roles, scoped bindings, namespace boundaries and deterministic deny-overrides evaluation. PostgreSQL policy rows and a monotonic policy version are authoritative; REST, CLI and non-human callers consume one authorization service rather than embedding local permission checks.
- `domain.authentication` owns local credential and browser-session contracts without making authorization decisions. A provider-neutral authentication port resolves an external identity to an existing user principal; the local adapter verifies Argon2id password hashes, while later OIDC, SAML and LDAP adapters remain replaceable edges.
- `dsl` parses and validates the MVP YAML model and native expression references.
- `ports` defines repository, transaction-support, transport, runner, plugin and provider-error contracts.
- `adapters` implements PostgreSQL, process, Kubernetes and external-provider boundaries.
- `api` and `entrypoints` translate user requests into application commands and run the CLI, service roles, server, compact supervisor, preflight and migration processes.
- `identity`, `lifecycle` and `platform` are the canonical application-service boundaries for credentials and tenants, backfills, and operator dashboards and flow tests. They depend inward on domain and port contracts; API, adapter and entry-point layers do not flow back into them.
- `compatibility.kestra` is the explicit Kestra import, migration, shadow and conformance feature surface.
- PostgreSQL owns accepted commands, executions, events, task attempts, schedules, inbox/outbox messages and durable work claims.

## Source and operational package layout

Executable implementations live under `amesh.entrypoints`; console-script metadata, Docker Compose
and Helm invoke those canonical modules. The former flat modules (`amesh.cli`, `amesh.worker`,
`amesh.role`, `amesh.server`, `amesh.compact`, `amesh.migrations`, `amesh.preflight` and
`amesh.deployment_profile`) remain module-identity aliases so existing imports, monkeypatches and
`python -m` commands continue to work during migration. Kestra compatibility follows the same rule:
new code imports `amesh.compatibility.kestra`, while `amesh.kestra_compatibility` remains an identity
alias.

Feature services use the singular canonical modules `identity.credential`, `identity.tenant`,
`lifecycle.backfill`, `platform.dashboard` and `platform.flow_test`. The former flat plural modules
remain identity-preserving import facades for existing integrations; production code imports only
the canonical packages.

Small dependency-neutral modules hold contracts shared across feature boundaries:
`dsl.descriptors` owns schema/specification value objects, `migration_planning` owns pure migration
metadata, `networking` owns outbound HTTP policy, and `tasks.mcp_client` owns the low-level MCP client.
A fresh-process import regression loads every production module and prevents these boundaries from
forming import cycles again.

The default development `compose.yaml` and production `Dockerfile` remain at the repository root.
Non-default Compose profiles and auxiliary Dockerfiles live under `docker/`; current commands and
package manifests always reference that canonical location. Historical verification and progress
records live under `docs/reviews/`, while the root `PROGRESS.md` is the current handoff only.

## Data and failure flow

Execution transitions append their events in the same database transaction. The transport adapter provides separately verified transactional outbox publication, durable inbox deduplication and fenced queue claims. The MVP recovery worker scans persisted running executions and reconciles their deterministic Kubernetes Jobs; task and execution results commit only while the persisted attempt and execution epoch still match. Duplicate commands and messages return the previously persisted logical result. When PostgreSQL is unavailable, AMESH acknowledges no state-changing request. OpenRouter and MCP failures remain task failures or retries and never mutate orchestration state directly.

Interactive login follows the same PostgreSQL-authoritative boundary. The browser submits a provider, user handle and secret to the authentication service; successful local verification returns a random opaque session whose keyed digest, CSRF digest, principal credential epoch, idle deadline, absolute deadline and revocation state are stored in PostgreSQL. The browser receives only a same-site HTTP-only session cookie and a separate CSRF value. Every authenticated unsafe request must match the CSRF cookie and header before authorization runs. Password rotation, user disablement, logout and global revocation fence existing sessions through the persisted principal epoch or session state. Invalid, locked, expired and unknown identities return the same public failure while bounded metrics and secret-free audit evidence retain the internal reason.

## Bounded model and MCP primitive boundary

The in-progress session interaction refactor is specified in
[ADR-076](docs/adr/076-separated-session-finalization-and-cache-efficient-context.md).
It separates research and finalization without replacing durable session authorities and adds
measured cache-efficient context projection. Only implemented slices are runtime behavior;
the full new interaction protocol remains under qualification.

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

Lifecycle event names are typed at the task boundary. After journal-key deduplication, the session
repository passes each proposed state/phase change through a pure reducer; invalid phase changes and
all new events after terminal completion are rejected before either the journal or snapshot changes.

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
`AgentSessionHarness` port. AMESH constructs one exact provider route, model, canonical transcript,
context budget, output schema, timeout, continuation handle and stable invocation key. The harness
selects only the model-visible messages; the AMESH gateway verifies every other call field and
enforces message, canonical-byte and estimated-token ceilings before provider I/O. A harness receives
no provider credential value, MCP client, approval service or repository.

Pi 0.84.3 is the required production adapter in both API and recovery-executor composition roots;
there is no built-in runtime fallback. It uses its direct `Agent` API through an isolated Node worker
whose allowlisted process environment excludes provider credentials. Pi's model stream must call back
through the AMESH gateway and any tool request must return to the ordinary AMESH policy, approval,
invocation-journal and checkpoint path. PostgreSQL remains the canonical transcript and session store.
Harness context is always a bounded derived projection; it cannot replace or mutate the accepted
transcript. See [ADR-058](docs/adr/058-pi-behind-amesh-agent-session-harness-port.md) and
[ADR-070](docs/adr/070-harness-owned-context-projection-under-amesh-budgets.md).

The canonical session transcript is append-only. Before each model call the configured harness uses
its native context hook to retain pinned instructions and complete recent action/result pairs within
an AMESH-calculated input ceiling that reserves completion headroom. A content-addressed receipt
records the harness algorithm, source and selected digests, retained indexes, limits and headroom.
AMESH rejects an overflowing or identity-mutating harness call before provider I/O and records the
accepted receipt without making the harness authoritative for transcript storage. Provider
prompt-cache reads, writes, hit ratio and signed cost effect remain distinct from task-result caching
and invocation replay. The conformance kit exercises this contract without granting a harness
credentials, native tools or workflow-state access.

An agent limit document is explicitly either legacy `BOUNDED` or `PROVIDER_BOUNDED`; omission keeps
the bounded contract. Provider-bounded null ceilings disable only the corresponding AMESH
application stop. Finite mesh and session-policy values still intersect as lower caps, while
concurrency, recursion, retention, cancellation and fencing remain operational controls. Context is
never represented with fake infinity: AMESH resolves the exact model's declared physical context
window and output limit and gives the harness that finite budget, failing preflight if the provider
cannot declare it. An explicit disabled task-timeout mode prevents internal model and MCP handlers
from injecting legacy 60/30-second defaults. See
[ADR-072](docs/adr/072-reliable-agent-attempts-and-provider-bounded-sessions.md).

Each external model invocation checkpoints normalized token, cache and cost accounting before
assistant-content or schema validation. The checkpoint is separate from the successful task result,
is idempotent under the invocation identity and stores no raw provider response or hidden reasoning.
Timeout or cancellation after external work starts settles as `IN_DOUBT`; aggregate evidence labels
known totals as exact, a lower bound or unresolved rather than treating unavailable billing as zero.

## Subscription-backed model-engine boundary

Direct HTTP model routes and subscription-backed process engines share one provider-neutral route
contract. An engine route supplies an adapter and immutable `engineRef`, while `engineScopes` on the
agent and task contract explicitly delegates that binding; endpoint and credential fields are
mutually exclusive with `engineRef`. The application composition root registers the Codex App Server
JSON-RPC/JSONL and GitHub Copilot CLI JSONL adapters at pinned revisions. Their account managers
expose only catalog, safe status, documented browser/device login and logout through the namespace
API.

AMESH derives one `CODEX_HOME`/`COPILOT_HOME` below a server-owned state root for each tenant,
namespace, adapter and engine reference. Child processes receive a minimal environment, bounded
JSONL frames, timeout/cancellation supervision, an empty temporary working directory and no provider
or MCP credential. Native tools and integrations are disabled; AMESH remains authoritative for
tool policy, structured-output validation, durable progress, usage/evidence and execution budgets.
These engines advertise text/image input, structured output, progress, cancellation and usage only
where supported. Subscription quota is not synthesized into API dollar cost, and unsupported
embeddings, opaque provider continuation, engine-native tools, cache guarantees and exact downstream
output ceilings fail capability negotiation or remain explicitly unavailable. Copilot's OS-keyring
fallback requires a dedicated runtime identity or container for tenant isolation. See
[ADR-074](docs/adr/074-isolated-subscription-model-engines.md) and the
[model-engine operations runbook](docs/operations/model-engines.md).

Workflow dependencies expose successful task outputs only to the expression renderer. Dependency
order never appends an upstream output or private session transcript to another agent's context. Each
agent node validates its explicitly rendered input and final structured result against its pinned
schemas; an explicit expression or typed handoff carries that result onward. Transitive output
visibility remains compatible, so strict direct-edge isolation is a workflow-authoring choice rather
than an implicit runtime rewrite.

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

AMESH also owns progress validation, redaction, idempotency and durable acceptance. Every valid
provider or harness frame awaits its individual PostgreSQL journal commit before the producer
continues. The journal is therefore the durable FIFO and database latency supplies backpressure;
there is no acknowledged in-memory tail to lose on process failure. Default rate and session-volume
ceilings do not truncate activity, and AMESH generates no new `TRUNCATED` frames. Historical markers
remain readable. Invalid or oversized frames fail before acceptance, while accepted frames remain
ordered before any later durable lifecycle failure. Hosts own retained duration and storage capacity,
and clients may poll the current projection every 500 milliseconds or consume the reconnectable
stream without changing persistence semantics. See
[ADR-071](docs/adr/071-lossless-progress-ingress.md).

```mermaid
flowchart LR
    P[Provider or harness] -->|await append(valid frame)| S[AMESH progress sink]
    S -->|commit one event before receipt| J[(PostgreSQL session journal)]
    J -->|event id, index, cursor| S
    S -->|durable receipt| P
    J --> C[Current progress projection]
    C -->|poll every 500 ms| CP[Client]
    C -->|reconnectable NDJSON stream| CS[Client]
    P -. caught failure .-> F[Append FAILED closure if DB available]
    F --> J
    R[Session lifecycle and recovery] -. remains authoritative .-> J
```

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
