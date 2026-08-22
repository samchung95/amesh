# ADR-033: Durable conditional branch decisions and zero-attempt skips

- Status: Accepted
- Date: 2026-08-22
- Owners: EPIC-202

## Context

AMESH already has a bounded native expression engine, a deterministic nested-flowable plan and
PostgreSQL-authoritative task attempts, events and transactional outbox publication. EPIC-202 adds
conditional orchestration whose selected path must remain stable across executor restarts and whose
non-selected runnable tasks must not appear to have run.

Kestra's public flowable contract uses `If` with `condition`, `then` and `else`, and `Switch` with a
rendered `value` and named `cases`. AMESH also requires ordered else-if and predicate cases, explicit
expression-error policies and redacted decision evidence. A rule-engine dependency would duplicate
the existing expression sandbox without supplying AMESH's durable state or evidence contract.

## Decision

1. Add orchestration-only `core.if` and `core.switch` flowables. `core.if` accepts `condition`,
   `then`, ordered `elseIf` branches and `else`; `core.switch` accepts Kestra-compatible `value` and
   `cases`, plus ordered `predicateCases`.
2. Compile every branch into the existing deterministic task plan and tag branch descendants with a
   branch identifier. Exact switch cases are checked before ordered predicates, and the optional
   `default` case is last.
3. Evaluate a conditional parent only after its dependencies succeed. Persist the redacted inputs,
   evaluations, error policy and selected branch on the running parent attempt before making branch
   children runnable. A restarted executor reuses that evidence instead of re-evaluating.
4. Represent non-selected work with a dedicated `TaskRunSkipped` event and a terminal task-run result
   stored without creating a task attempt. The task remains at attempt zero, while existing terminal
   orchestration behavior continues to treat the skipped result as successful control flow.
5. Apply `FAIL`, `FALSE` and `FALLBACK` expression-error policies at conditional parents. Task
   `runIf` and retry conditions support `FAIL` and `FALSE`; `FALLBACK` is valid only where an explicit
   `else` or `default` branch exists.
6. Reject duplicate predicates, duplicate branch identifiers, unconditional branches followed by
   unreachable branches and malformed conditional shapes during flow validation.

## Consequences

- No dependency is added. The existing expression engine and PostgreSQL event/outbox boundary remain
  authoritative.
- A small additive migration stores zero-attempt terminal result/evidence on `task_runs`; ordinary
  runnable results remain authoritative on immutable `task_attempts`.
- Flow error hooks and final flow-output materialization continue to be owned by EPIC-204 and
  EPIC-205. Their task definitions and expressions can use the same condition contract without this
  epic implementing those later lifecycle stages.
