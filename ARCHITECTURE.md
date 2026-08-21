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
- `dsl` parses and validates the MVP YAML model and native expression references.
- `ports` defines transport, runner and plugin contracts.
- `adapters` implements PostgreSQL, process, Kubernetes and external-provider boundaries.
- `api` and `cli` translate user requests into application commands and return persisted state.
- PostgreSQL owns accepted commands, executions, events, task attempts, schedules, inbox/outbox messages and durable work claims.

## Data and failure flow

Execution transitions append their events in the same database transaction. The transport adapter provides separately verified transactional outbox publication, durable inbox deduplication and fenced queue claims. The MVP recovery worker scans persisted running executions and reconciles their deterministic Kubernetes Jobs; task and execution results commit only while the persisted attempt and execution epoch still match. Duplicate commands and messages return the previously persisted logical result. When PostgreSQL is unavailable, AMESH acknowledges no state-changing request. OpenRouter and MCP failures remain task failures or retries and never mutate orchestration state directly.

## MVP executor boundary

The executor derives runnable tasks from the validated top-level DAG and persisted task-run states; it does not keep authoritative progress in memory. The execution repository creates one stable task-run identity per execution/task path, records every attempt separately and stores task results before dependants become eligible. In-process MVP handlers prove orchestration with `core.return` and `core.log`; W3 replaces the handler edge with fenced runner dispatch without changing DAG readiness or persisted state. Dropping an executor process loses no scheduler state: a replacement reloads successful task runs, skips them and continues the remaining graph.

Retry eligibility is persisted as `task_runs.retry_at`; backoff is never an in-memory timer of record. Each attempt number is its fencing token for the MVP. The local-process runner owns subprocess creation, output capture, timeout and cancellation, while the execution repository accepts a result only when the task run is still running at that exact attempt. A timed-out, cancelled or superseded process may exit later, but its stale result cannot change task state.

W4 keeps expression evaluation deterministic and side-effect free: the native Jinja sandbox receives only `inputs`, successful task `outputs` and flow `vars`, and renders a task immediately before its attempt handler runs. Cron calculation is stateless; durable uniqueness comes from a stable execution idempotency key derived from the tenant, flow revision, trigger and scheduled UTC instant. The execution row, initial events and task runs are created in one PostgreSQL transaction, so concurrent or restarted scheduler instances converge on one execution per occurrence without introducing a second scheduler database.

W6 exposes this executor through the authenticated MVP REST and CLI surfaces and supplies trusted in-process HTTP, OpenAI-compatible LLM and MCP handlers. W7 packages one uv-locked image into three Helm roles: an idempotent migration hook, an API server and a delayed recovery worker. Both runtime roles use PostgreSQL as authority and reconcile Kubernetes task Jobs through namespace-scoped RBAC. The server publishes Prometheus metrics and both processes emit JSON log records; PostgreSQL remains an external chart dependency.

W5 implements the same `TaskRunner` port with Kubernetes Jobs. A stable attempt identity maps to one deterministic owned Job name; recreating a runner reads that Job instead of duplicating it. The Job controller replaces a deleted pod, while the runner reconciles Job status, captures the terminal pod log and exit code, and performs idempotent foreground deletion after success, failure, timeout or fenced cancellation. PostgreSQL still decides whether the attempt result is current—the Kubernetes API never becomes orchestration state.

Detailed decisions remain in `docs/architecture/` and `docs/adr/`; this page is the cold-start system map.
