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

## Attempts and retries

A logical task run can contain multiple attempts. Each attempt receives a distinct `attempt_id`; retry
does not erase prior evidence. The attempt policy records classification, retry index, planned delay,
actual eligibility time and the triggering failure.

## Cancellation

Cancellation is cooperative first:

1. execution records `CANCEL_REQUESTED`;
2. no new ordinary work is admitted;
3. active attempts receive a cancellation command;
4. workers acknowledge and ask runners to stop;
5. after a configured deadline, force termination can occur;
6. stale completion is rejected by attempt state and fencing token;
7. cleanup/finally behavior follows explicit flow policy.

## External side effects

Plugin and task authors must choose one:

- use a destination idempotency key derived from task attempt or logical operation;
- execute inside an external transaction coordinated by the plugin;
- probe destination state before retry;
- provide compensation;
- declare the operation unsafe to retry.

The UI and documentation surface the selected side-effect strategy.
