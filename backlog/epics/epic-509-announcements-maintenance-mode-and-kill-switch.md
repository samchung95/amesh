# EPIC-509 — Announcements, maintenance mode and kill switch

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Administrator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Control instance-wide operational posture during incidents and planned maintenance.

## In scope

- [x] **URS-F-0566** — The system shall publish scheduled and immediate announcements with severity, audience and expiry.
- [x] **URS-F-0567** — The system shall enter maintenance modes that separately control authoring, new executions, triggers, API writes and worker dispatch.
- [x] **URS-F-0568** — The system shall activate tenant, namespace, flow, plugin, runner or instance kill switches.
- [x] **URS-F-0569** — The system shall define behavior for already-running work when a switch is activated.
- [x] **URS-F-0570** — The system shall require reason, actor, expiry or review for emergency controls.
- [x] **URS-F-0571** — The system shall propagate control changes rapidly to all components and expose acknowledgement status.
- [x] **URS-F-0572** — The system shall automatically expire temporary controls where configured.
- [x] **URS-F-0573** — The system shall audit activation, extension, bypass and deactivation events.

## Implementation completion evidence

- 2026-08-23 — EPIC-509 is complete for the local reference profile. Migration 0050 adds tenant-isolated scheduled announcements, scoped maintenance and kill-switch records, versioned acknowledgements, automatic expiry and immutable lifecycle evidence. API, scheduler, trigger, backfill and executor boundaries independently enforce authoring, new-execution, trigger, API-write and worker-dispatch controls with CONTINUE, DRAIN or CANCEL running-work policy; accepted trigger work is deferred without consuming an attempt. The Administration UI publishes announcements and activates, extends, bypasses or deactivates controls. Fresh-PostgreSQL, API and Chromium tests passed, generated OpenAPI and four SDKs are current, and a live Compose control returned HTTP 423 then received version-1 acknowledgements from webserver, scheduler, executor and indexer within six seconds before clean deactivation. External multi-node rolling-upgrade transfer qualification remains explicitly deferred under the shared availability NFR. Evidence: [`operational-controls.md`](../../docs/api/operational-controls.md), [`0050_operational_controls.sql`](../../migrations/0050_operational_controls.sql), [`test_operational_controls.py`](../../tests/adapters/postgres/test_operational_controls.py), [`test_operational_controls_api.py`](../../tests/api/test_operational_controls_api.py), [`test_worker.py`](../../tests/test_worker.py), and [`operational-controls.spec.ts`](../../frontend/e2e/operational-controls.spec.ts).

## Non-functional requirements

- [ ] **URS-NFR-AVAILABILITY-004** — Planned maintenance and rolling upgrades shall drain or transfer owned work without silent loss. Target: Zero lost accepted work and no more than one configured scheduling-delay window.

## Dependencies

- EPIC-500
- EPIC-504

## Architecture impact

- Primary bounded area: `operations`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Reference deployment, upgrade and failure-recovery tests.
- Upgrade and drain conformance suite.
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

- External multi-node rolling-upgrade transfer and failure-zone qualification remains deferred to the shared high-availability conformance program; EPIC-509 claims only the verified local PostgreSQL and Compose profile.

## Traceability

- Functional requirements: URS-F-0566, URS-F-0567, URS-F-0568, URS-F-0569, URS-F-0570, URS-F-0571, URS-F-0572, URS-F-0573
- Non-functional requirements: URS-NFR-AVAILABILITY-004
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
