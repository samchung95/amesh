# EPIC-810 — Reliable scheduling and truthful role-aware health

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Make AMESH the durable owner of generic schedules while every enabled service role reports its real ability to make progress.

## In scope

- [x] Duplicate schedule occurrences already in `RETRY_WAIT` converge without an exception loop or a second execution.
- [x] Stale or incompatible plugin-resolution pins are migrated or quarantined through a bounded, auditable path and cannot poison the scheduler loop.
- [x] Every enabled role reports last success, last failure, consecutive failures, liveness and readiness; caught background-loop failures degrade readiness.
- [x] Disabled roles are explicitly reported as disabled and do not make the deployment unhealthy.
- [x] Timezone, start/end bounds, misfire, catch-up, pause/resume, replay and restart semantics remain deterministic and occurrence-idempotent.
- [x] A live Compose restart demonstrates no lost or duplicate scheduled execution and health changes honestly when a required role fails.

## Implementation completion evidence

- 2026-08-25 — EPIC-810 is complete. Temporal `RETRY_WAIT` duplicates now advance the fenced schedule cursor without a second execution, while the trigger worker retries with the same occurrence idempotency key. Legacy plugin pins are conditionally migrated to exact v1 pins with one audit event or the owning flow is disabled with one quarantine audit. Migration 0060 persists DEGRADED role state, last success/failure, bounded redacted failure evidence and consecutive failures; `/ready` aggregates every configured role and distinguishes disabled roles. Sixty-one focused unit, API, Helm, migration and PostgreSQL tests passed. Live Compose produced HTTP 503 while the scheduler was degraded, recovered all six roles to READY in 11 seconds after remediation, and kept exactly one occurrence and execution (`01a03980-1533-7e64-97b7-7d30642bc231`) across scheduler restarts before and after its bounded cron instant. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`scheduler-and-triggers.md`](../../docs/architecture/scheduler-and-triggers.md), [`high-availability.md`](../../docs/operations/high-availability.md), [`test_cron_scheduler.py`](../../tests/scheduler/test_cron_scheduler.py), [`test_service_registry.py`](../../tests/adapters/postgres/test_service_registry.py), and [`test_plugin_policy_repository.py`](../../tests/adapters/postgres/test_plugin_policy_repository.py).

## Explicit non-goals

- Embedding market calendars, news schedules or other domain-specific scheduling rules in core
- Making clients responsible for occurrence durability or deduplication

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-103
- EPIC-303
- EPIC-601

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Scheduler unit tests for retry-wait convergence, temporal boundaries and restart deduplication.
- Plugin-resolution compatibility and quarantine regression tests.
- Role-health unit, API contract and isolated PostgreSQL integration tests.
- Live Compose scheduler restart and required-role failure smoke evidence.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] All EPIC-810 acceptance scenarios pass without recurring scheduler errors.
- [x] Health documentation defines enabled, disabled, live, ready and degraded role semantics.
- [x] The canonical backlog, TESTLOG and progress handoff link the automated and live evidence.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- False-green readiness can send client traffic to a deployment that cannot launch work.
- Historical trigger records can repeatedly fail after a plugin contract evolves.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
