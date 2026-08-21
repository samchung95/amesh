# Execution semantics

## Guarantee vocabulary

The platform uses precise guarantees:

- **Durable acceptance:** after a state-changing API call succeeds, its command is recoverable.
- **At-least-once delivery:** messages and task results may be delivered more than once.
- **Idempotent logical effect:** repeated delivery with the same identity changes logical state once.
- **Fenced ownership:** a former owner cannot commit after a newer ownership epoch exists.
- **No generic exactly-once external effects:** external systems need idempotency keys, transactions or
  compensating workflows.

## Command processing

Every command has:

```text
command_id
idempotency_key
command_type + schema_version
tenant_id
target resource and expected version
actor and delegated identity
correlation_id + causation_id
trace context
submitted_at
payload
```

The command handler:

1. authenticates and authorizes;
2. validates payload and expected resource version;
3. checks the durable command inbox/idempotency table;
4. locks or compare-and-swaps the target aggregate;
5. invokes the pure reducer;
6. persists new snapshot, immutable events and outbox records;
7. commits;
8. returns the persisted result.

A retry of the same idempotency key returns the original committed result when request semantics match.
Reuse of a key with a different payload is rejected.

## Authoritative event contract

`amesh.domain` owns immutable execution and task-run command, event, snapshot, transition and
rejection models. The reducer is a pure transition-table lookup: it performs no database, web,
queue, search or object-storage I/O. Execution events use schema version 2; task-run events use
schema version 1. The execution upcaster accepts the historical version-1 shape, derives its stable
idempotency key from `event_id`, promotes a payload reason into the event header and rejects unknown
versions.

The persisted execution lifecycle is:

```text
CREATED -> QUEUED -> RUNNING -> SUCCESS | FAILED | WARNING
                       |  |
                       |  +-> PAUSED -> RUNNING
                       +----> CANCELLING -> CANCELLED
FAILED | WARNING | CANCELLED -> RESTARTING -> RUNNING  (new epoch)
```

The persisted task-run lifecycle is:

```text
WAITING -> RUNNING -> SUCCESS | FAILED
             |
             +-> RETRY_DELAY -> RUNNING
WAITING | RUNNING | RETRY_DELAY -> CANCELLED
```

Every accepted event retains an event identity, stable idempotency key, schema version, actor,
optional reason, correlation/causation identities, occurrence time and typed payload. Replaying the
same ordered history from the same initial snapshot produces the same canonical snapshot. Repeated
event IDs or idempotency keys are no-ops; an illegal or stale command returns immutable rejection
evidence without changing the snapshot.

PostgreSQL stores execution history in `execution_events`, task history in `task_run_events`, and
durable rejected decisions in `transition_rejections`. Row-level security applies to all three.
An `AFTER INSERT` trigger writes the corresponding versioned envelope to `messages_outbox` in the
same database transaction as each event. The publisher can observe it only after commit; rollback
removes the state change, event and outbox row together.

Each execution records one launch source: `manual`, `api`, `scheduled`, `event` or `subflow`.
Source-specific context is stored beside that value, and an idempotency key owns duplicate launch
suppression for schedules, events and subflow callers.

## Execution graph

A flow revision compiles into a canonical graph. Dynamic constructs create graph fragments through
versioned expansion events. The executor never mutates an execution by scanning files or interpreting UI
state.

A task becomes runnable only when:

- its parent flowable has expanded it;
- declared dependencies are terminal in acceptable states;
- its condition evaluates true;
- admission and concurrency policy grants capacity;
- the execution is not paused, cancelling or terminal;
- the task and plugin remain permitted.

`reduce_orchestration()` derives runnable task IDs, retry waiting, success or an unsatisfiable-graph
failure from the committed flow revision and task-run snapshot. The decision is pure and preserves
canonical flow order, so parallel executor instances reach the same branch decision. PostgreSQL then
compare-and-swaps a task from `WAITING` or eligible `RETRY_DELAY` to `RUNNING`; a losing executor does
not reuse the winner's running attempt. A false `runIf` condition is persisted as a skipped success
without emitting a dispatch command.

An eligible `TaskRunStarted` event produces a `DispatchTaskRun` envelope on `task-dispatch` in the same
transaction as the task state and immutable event. Task completion and terminal execution envelopes
remain on the task-run and execution event subjects for downstream event/subflow consumers. If a
restarted executor sees failed prerequisites or another graph state with no legal progress, it commits
`ExecutionFailed` with deterministic `failed` and `blocked` diagnostics.

### Nested flowables

`core.sequential`, `core.parallel` and `core.dag` compile into the same durable plan as ordinary tasks.
The flowable parent and every nested child receive task-run identities when the execution is created;
the parent runs as a non-dispatched aggregate while executable leaves retain ordinary attempts and
restart behavior. Sequential flowables inject predecessor edges in declared order. Parallel and DAG
flowables admit ready leaves concurrently, bounded by `maxConcurrency` at every enclosing flowable.

Child completion is reduced in declared order into a parent result containing `childOrder`, each child
state, successful output and normalized error. `FAIL_FAST` fails the parent on the first terminal child
failure, `CONTINUE_ON_ERROR` waits for every child and succeeds with the complete aggregate, and
`COLLECT_ALL` waits for every child before failing when any child failed. A child expression context
contains outputs from transitive dependencies only; independent sibling output is not visible.

`GET /api/v1/flows/{namespace}/{flow_id}/graph` returns the expanded revision before execution.
`GET /api/v1/executions/{execution_id}/graph` returns the pinned revision with current durable task
states and results. The control room renders both contracts on flow and execution detail pages.

## Admission control

Flows and tasks may declare `concurrency` rules with a stable ID, positive limit, scope and limit
behavior. Scopes are `GLOBAL`, `TENANT`, `NAMESPACE`, `FLOW`, `WORKER_GROUP` and `KEY`; a key is
rendered once by the bounded native expression engine and must produce a scalar. Tasks may also set a
bounded `priority` and optional `workerGroup`; workers reject task dispatch outside their explicit
group.

PostgreSQL advisory transaction locks serialize competing reservations for the same evaluated bucket.
One request records the evaluated policy set and decision, while one leased reservation per policy
holds capacity. Completion and retry release all reservations idempotently. Reconciliation expires
lost leases and admits queued requests by priority plus one aging point per minute, so lower-priority
work eventually overtakes continuously arriving higher-priority work. `REPLACE` cancels the oldest
same-tenant holder before admitting its replacement; cross-tenant global replacement is deliberately
rejected by DSL validation.

When capacity is exhausted, `QUEUE` leaves an execution or task pending, `CANCEL` and `FAIL` persist the
corresponding terminal state, `SKIP` persists success without running user code and `REPLACE` fences the
displaced resource. The execution and task admission endpoints expose the outcome, reason, limiting
policy, scope and bucket, active count, configured limit, queue position and queue age. Tenant policy
adds active-execution, queued-execution, storage-byte, log-byte and per-minute API request budgets.

`GET /api/v1/admissions/diagnostics` returns active reservations, queued requests, oldest queue age and
pressure by limiting policy. Tenant administrators can invoke `POST /api/v1/admissions/reconcile`;
ordinary release paths also reconcile queued work immediately.

## Attempts and retries

A logical task run can contain multiple attempts. Each attempt receives a distinct `attempt_id`; retry
does not erase prior evidence. The attempt policy records classification, retry index, planned delay,
actual eligibility time and the triggering failure. Flow YAML accepts `maxAttempts`, `delaySeconds`,
`backoffMultiplier`, `maxIntervalSeconds` and `jitterRatio`; jitter is stable for one task-run attempt
and the final delay never exceeds the configured maximum interval. Failures persist as `RETRYABLE`,
`NON_RETRYABLE`, `CANCELLED`, `TIMED_OUT` or `INFRASTRUCTURE`, and only the configured retryable
categories consume another attempt.

Task handlers run inside `asyncio.timeout()`, whose local deadline is monotonic. An execution's
optional `timeoutSeconds` becomes an absolute PostgreSQL-time deadline when the execution is created.
Executors calculate remaining time from database time, and a due deadline atomically fences active
attempts and persists the execution and affected task outcomes.

## Cancellation

Cancellation is cooperative first:

1. execution records `CANCEL_REQUESTED`;
2. no new ordinary work is admitted;
3. active attempts receive a cancellation command;
4. workers acknowledge and ask runners to stop;
5. after a configured deadline, force termination can occur;
6. stale completion is rejected by attempt state and fencing token;
7. cleanup/finally behavior follows explicit flow policy.

Pause changes only execution admission: completed outputs and in-flight attempts remain committed,
while no new dependency-ready task is started until resume. Cancellation records a database-time grace
deadline and marks live attempts for cooperative cancellation. Confirmation is accepted after live
attempts acknowledge the request; force cancellation is accepted only after the persisted deadline.

Terminal failed, cancelled or warning executions can restart from the whole graph or one named task
checkpoint. The checkpoint and every downstream task return to `WAITING`, successful upstream tasks
remain committed, prior attempts remain immutable history, and the execution epoch advances so an old
worker cannot commit. Every intervention requires the preview's execution version and epoch. The
authorized REST surface exposes preview, apply and immutable intervention history under
`/api/v1/executions/{execution_id}/interventions`.

## Subflows

`core.subflow` resolves a child by tenant, namespace, flow ID and either its active revision or an
explicit revision. Creation of the child execution and its `execution_subflows` relationship is one
transaction. The relationship records the parent execution, task run and attempt, child execution,
invocation identity, target revision, nesting depth, mode, propagation policy, output mapping and
actor. Repeating the same parent task attempt resolves the same child rather than launching a
duplicate.

The three invocation modes are:

- `SYNC`: the task waits for the child, applies the declared failure/cancellation/pause policy and
  maps the child's committed task results into parent outputs and artifact references.
- `ASYNC`: the parent task commits the durable child reference immediately; post-response coordination
  executes the child independently and can resume it from the stored relationship.
- `DETACHED`: launch and execution are independent and all parent-state propagation flags are disabled.

Inputs are rendered in the parent context and checked against the child flow's declared input types.
Labels merge child defaults, parent execution labels and invocation labels. Correlation and trace
context are copied into the immutable child trigger context. `outputMapping` and `artifactMapping` are
rendered only after child completion; optional draft-2020-12 `outputSchema` and `artifactSchema`
documents reject an invalid mapped result before the parent task commits it.

Lineage traversal rejects repeated namespace/flow identities and enforces `maxDepth`. Parent task
replay launches a new child when `propagation.restart` is true and reuses the prior committed child
when it is false. The API independently authorizes the parent and every child namespace. A flow marked
`system: true` additionally requires tenant-management authority both when applied and when invoked.
Authorized callers can inspect both directions of the durable graph at
`/api/v1/executions/{execution_id}/subflows` and
`/api/v1/executions/{execution_id}/parent-subflow`.

## Runnable task contract

Before an executor creates an execution, every installed task type is checked against its registered
JSON Schema. Each live attempt receives a typed context containing tenant and execution identities,
inputs, prior outputs, variables, labels, trigger data, declared secret scopes, resolved files and a
polling cancellation channel. A context provider sees only the scopes and file declarations present in
the flow contract; declaring secrets without a configured provider fails as a configuration error.

A synchronous handler returns either a plain output object or a structured completion containing
output, logs, metrics, artifact references and exit metadata. `contract.resourceLimits` bounds encoded
output and log bytes plus declared artifact bytes before completion is committed. Attempt evidence is
stored separately from the task result, and failures retain stable configuration, user-code,
infrastructure or platform classifications.

An asynchronous handler returns a deferral with a resume token, optional expiry and metadata. Only the
SHA-256 token digest is persisted in the tenant-scoped `task_deferrals` table. The task attempt remains
`RUNNING`, emits `TaskRunDeferred` through the transactional outbox and is not re-invoked after executor
restart. An authorized caller completes it through
`POST /api/v1/executions/{execution_id}/task-runs/{task_run_id}/resume`. The first valid callback wins;
the same token then returns the original completion, while wrong, expired or stale-attempt callbacks
fail without replacing committed evidence. An expired deferral is persisted as expired and fails its
live attempt with the timed-out category instead of leaving an execution permanently running.

## Backfills and replay

A backfill is a tenant-scoped durable resource pinned to one flow revision. Its selector expands to a
bounded, deterministic item set from an explicit time range and interval, partition keys, selected
occurrence timestamps or source execution IDs. `POST /api/v1/backfills/preview` is the dry-run path: it
creates no state and reports execution count, estimated task/cost units, side-effect warnings and an
occurrence-scoped idempotency-key template. Submission uses the same selector through
`POST /api/v1/backfills`.

The worker admits no more than the backfill's concurrent capacity or rolling one-minute rate budget.
Every generated execution uses normal tenant/admission controls, the backfill priority, caller inputs
and labels, a pinned revision and the stable key `backfill:<backfill-id>:<occurrence-key>`. Therefore a
worker crash after execution creation but before item linkage converges on the same execution when the
pending item is pumped again. Pausing stops new generation, resuming continues pending items, and
cancelling marks only not-yet-generated items cancelled; already-created executions retain their
ordinary independent lifecycle and evidence.

Replay is the same controller with source-execution items. All sources must match the selected flow and
revision. Source inputs and labels are retained unless explicitly overridden, while the item row and
execution trigger preserve source-to-replay lineage. Monitoring aggregates pending, running, succeeded,
failed and cancelled items plus actual task-based cost units. Backfill state events enter the
transactional outbox, and completion is recorded only after every generated execution is terminal.

## External side effects

Plugin and task authors must choose one:

- use a destination idempotency key derived from task attempt or logical operation;
- execute inside an external transaction coordinated by the plugin;
- probe destination state before retry;
- provide compensation;
- declare the operation unsafe to retry.

The UI and documentation surface the selected side-effect strategy.
