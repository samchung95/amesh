# EPIC-816 — Restart, idempotency and large-record qualification

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `quality`
- **Primary persona:** Maintainer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Prove on isolated PostgreSQL and object storage that failures around schedules, agents, tools and evidence lose no accepted data and create no duplicate logical outcome.

## In scope

- [x] An isolated PostgreSQL and object-storage qualification harness never uses shared developer data.
- [x] A fault matrix restarts API, scheduler, executor and worker before and after occurrence, model call, tool call, checkpoint and final-output persistence boundaries.
- [x] Stable idempotency keys, accepted-result reuse, fencing and ambiguous-outcome behavior are asserted at every boundary.
- [x] Large payloads externalize with size limits and content-integrity verification.
- [x] Qualification produces zero lost accepted records, zero duplicate logical decisions and consistent evidence digests.
- [x] Commands, environment requirements, supported limits and evidence are reproducible from documentation.

## Implementation completion evidence

- 2026-08-26 — EPIC-816 is complete. The documented uv qualification harness isolates its database and object store, exercises 40 before/after restart boundaries across scheduling, execution, model, tool, checkpoint and evidence persistence, and asserts fencing, stable idempotency, accepted-result reuse and explicit ambiguous outcomes. The machine-readable local report passed with zero lost accepted records, zero duplicate logical decisions and consistent evidence digests; a 1 MiB payload externalized with integrity verification and deliberate corruption was detected. Three focused qualification tests passed. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`run-restart-idempotency-qualification.md`](../../docs/how-to/run-restart-idempotency-qualification.md), [`qualify_restart_idempotency.py`](../../scripts/qualify_restart_idempotency.py), [`restart_qualification.py`](../../src/amesh/restart_qualification.py), and [`test_restart_qualification.py`](../../tests/test_restart_qualification.py).

## Explicit non-goals

- Claiming multi-region high availability
- Using a developer's long-lived database as a destructive fault-test target

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-108
- EPIC-810
- EPIC-812
- EPIC-813
- EPIC-814
- EPIC-815

## Architecture impact

- Primary bounded area: `quality`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Isolated PostgreSQL and object-storage integration harness.
- Parameterized process-restart fault matrix across scheduler, execution, model, tool and evidence boundaries.
- Large-payload externalization and corruption tests.
- Machine-readable qualification report with loss, duplicate and digest assertions.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] The complete fault matrix passes on the documented local profile.
- [x] Every ambiguous external-I/O case has an explicit non-duplication outcome.
- [x] Qualification artifacts and exact rerun commands are linked from TESTLOG.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- In-memory fake repositories can hide transaction and restart failures.
- Large provider outputs can exceed database, API or SDK limits after otherwise successful work.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
