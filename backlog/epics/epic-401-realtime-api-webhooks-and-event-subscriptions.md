# EPIC-401 — Realtime API, webhooks and event subscriptions

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `api`
- **Primary persona:** API consumer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Deliver state, log and audit changes to clients without fragile polling.

## In scope

- [ ] **URS-F-0406** — The system shall provide reconnectable server-sent event or WebSocket streams with cursor-based resume.
- [ ] **URS-F-0407** — The system shall filter subscriptions by authorized tenant, namespace, flow, execution, event type and severity.
- [ ] **URS-F-0408** — The system shall bound per-client buffers and apply backpressure or disconnect policy.
- [ ] **URS-F-0409** — The system shall provide signed outbound webhooks with retries, rotation, replay protection and delivery history.
- [ ] **URS-F-0410** — The system shall let consumers test webhook endpoints and replay selected deliveries.
- [ ] **URS-F-0411** — The system shall redact event payloads according to field sensitivity and caller permissions.
- [ ] **URS-F-0412** — The system shall emit heartbeats and explicit gap signals when a cursor is no longer available.
- [ ] **URS-F-0413** — The system shall continue core orchestration when realtime clients or webhook destinations are unavailable.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-005** — Core orchestration shall continue when optional search, telemetry, outbound webhook or analytics services are unavailable. Target: New and running executions continue within documented latency budgets during optional-service outage tests.

## Dependencies

- EPIC-009
- EPIC-111
- EPIC-400

## Architecture impact

- Primary bounded area: `api`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- OpenAPI contract and authenticated end-to-end API tests.
- Dependency isolation and outage integration tests.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [ ] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [ ] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [ ] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [ ] Security, tenant isolation, redaction and audit behavior are reviewed.
- [ ] Documentation, examples, migration notes and operational runbooks are updated.
- [ ] Performance and recovery budgets are measured when this epic is on a critical path.
- [ ] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0406, URS-F-0407, URS-F-0408, URS-F-0409, URS-F-0410, URS-F-0411, URS-F-0412, URS-F-0413
- Non-functional requirements: URS-NFR-RELIABILITY-005
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
