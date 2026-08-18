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
