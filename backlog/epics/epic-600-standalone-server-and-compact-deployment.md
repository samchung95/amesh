# EPIC-600 — Standalone server and compact deployment

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Run the complete platform on one host or small cluster with minimal dependencies.

## In scope

- [x] **URS-F-0582** — The system shall start webserver, executor, scheduler, worker and maintenance roles in one process or one deployment.
- [x] **URS-F-0583** — The system shall use PostgreSQL for authoritative state and compact queueing in the reference mode.
- [x] **URS-F-0584** — The system shall use local or S3-compatible object storage through configuration.
- [x] **URS-F-0585** — The system shall provide Docker, Docker Compose and native binary or package installation paths.
- [x] **URS-F-0586** — The system shall perform startup preflight checks for database, storage, configuration, migrations and required credentials.
- [x] **URS-F-0587** — The system shall expose readiness separately from liveness and include degraded dependency states.
- [x] **URS-F-0588** — The system shall support graceful shutdown that stops admission, drains work and checkpoints owned triggers.
- [x] **URS-F-0589** — The system shall document minimum and recommended resources for development and production.

## Implementation completion evidence

- 2026-08-23 — EPIC-600 is complete for the local reference profile. The `amesh-compact` supervisor runs webserver, executor, scheduler, worker, indexer and maintenance in one process over PostgreSQL-backed authoritative state and durable queueing, while the distributed Compose profile runs the same six roles independently. Configuration now selects immutable tenant-scoped local filesystem or S3-compatible object storage. Startup preflight fails closed on configuration, credentials, database, migration or storage failures; `/health` remains liveness-only and `/ready` reports required, degraded and unavailable dependency states. Docker Compose and native `uv tool install` paths include all 51 migrations plus `amesh`, `amesh-compact`, `amesh-migrate` and `amesh-preflight` commands. Live compact and distributed deployments were healthy at 51/51 with all six roles live, ready and AVAILABLE; the sample hello-world flow succeeded, compact restart retained it, and SIGTERM drained all six roles to STOPPED in 1.46 seconds. Focused Python, strict typing, packaging, Compose, generated-contract, frontend unit and production-build checks passed. The external 99.9% monthly SLO qualification and quarterly first-run usability study remain open under their shared NFRs and are not claimed. No LLM behavior was involved, so no OpenRouter call was required. Evidence: [`compact-deployment.md`](../../docs/operations/compact-deployment.md), [`test_compact.py`](../../tests/test_compact.py), [`test_preflight.py`](../../tests/test_preflight.py), [`test_local_object_store.py`](../../tests/storage/test_local_object_store.py), and [`TESTLOG.md`](../../TESTLOG.md).

## Non-functional requirements

- [ ] **URS-NFR-AVAILABILITY-001** — A production compact deployment shall support a documented high-availability topology. Target: At least 99.9% monthly control-plane availability excluding declared maintenance.
- [ ] **URS-NFR-USABILITY-003** — A new contributor shall be able to start the reference stack and run a sample flow from documented steps. Target: Median completion below 20 minutes on a clean supported workstation, excluding image download time.
- [ ] **URS-NFR-OPERABILITY-001** — Each service shall expose distinct liveness, readiness and detailed dependency health. Target: Reference orchestrator removes unready instances without restarting healthy but degraded processes unnecessarily.

## Dependencies

- EPIC-008
- EPIC-009
- EPIC-010

## Architecture impact

- Primary bounded area: `operations`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Reference deployment, upgrade and failure-recovery tests.
- Reference topology soak test and SLO calculation.
- Quarterly external documentation usability test.
- Kubernetes and Compose health tests.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- The 99.9% monthly compact availability target requires an external production-profile soak and SLO calculation.
- The below-20-minute first-run target requires the scheduled external contributor usability study.

## Traceability

- Functional requirements: URS-F-0582, URS-F-0583, URS-F-0584, URS-F-0585, URS-F-0586, URS-F-0587, URS-F-0588, URS-F-0589
- Non-functional requirements: URS-NFR-AVAILABILITY-001, URS-NFR-USABILITY-003, URS-NFR-OPERABILITY-001
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
