# ADR-034 — Durable error and terminal hooks

- **Status:** Accepted
- **Date:** 2026-08-22
- **Epic:** EPIC-204

## Context

AMESH already parses flow-level `errors` and `finally` blocks, but those tasks are not materialized or
executed. EPIC-204 also requires local flowable handlers, selector conditions, post-terminal
`afterExecution` tasks, primary-failure preservation, bounded recursion and graph visibility. A
transient executor callback cannot survive restart or prove that the execution reached a terminal
state before post-execution work began.

The pinned public behavior distinguishes three lifecycle moments:

1. `errors` handles a failure at flow or local flowable scope;
2. `finally` performs cleanup before normal success/failure terminalization; and
3. `afterExecution` reacts after the execution state is terminal and cannot replace that state.

## Decision

Lifecycle tasks are compiled into the same deterministic execution plan as ordinary tasks and are
created as ordinary durable task runs. Each task run records one phase: `MAIN`, `ERROR`, `FINALLY` or
`AFTER_EXECUTION`. The executor reduces the main graph first, then runs selected error handlers,
always runs finally tasks, persists the primary terminal state, and only then runs after-execution
tasks.

Execution lifecycle evidence records the primary outcome and per-phase status/failures through the
existing execution event/outbox boundary. Handler and cleanup failures are structured evidence and
never replace the primary failure. A terminal execution with incomplete lifecycle evidence remains
recoverable by the executor service.

Flowable tasks may define local `errors`. Error tasks may define an `errorSelector` containing states,
failure categories, task IDs and a safe expression. The existing `runIf` condition remains available
for final selection. Nested error handlers inside lifecycle blocks are rejected, so handler recursion
is statically bounded; ordinary task retry limits continue to bound cleanup attempts.

The execution graph exposes lifecycle phase and handler owner. Local handler edges connect the owning
flowable to its handler tasks, while flow-owned error, finally and after-execution nodes are explicitly
labelled.

## Alternatives considered

### Executor-only callbacks

This has the smallest implementation diff, but loses work on process failure, cannot prove ordering
around terminal persistence and produces no task-level graph or attempt evidence.

### External system flows or completion triggers

These are useful notification and compensation targets, but cannot implement local flowable ownership
or pre-terminal finally ordering. They remain valid tasks invoked from a durable handler.

### Separate lifecycle workflow executions

Child executions provide isolation but complicate primary-state ownership, authorization, graph
correlation and output visibility. The existing task-run aggregate already supplies the required
durability and fencing boundary.

## Consequences

- Migration 0036 adds task-run lifecycle phase and execution lifecycle evidence.
- Cancellation preserves not-yet-started finally/after-execution task runs for lifecycle recovery.
- `afterExecution` can observe the terminal execution state; its failures remain diagnostic only.
- Handler outputs can use existing notification, subflow/compensation and artifact-capable task
  contracts without a new runtime or dependency.
