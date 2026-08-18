# EPIC-509 — Announcements, maintenance mode and kill switch

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Administrator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Control instance-wide operational posture during incidents and planned maintenance.

## In scope

- [ ] **URS-F-0566** — The system shall publish scheduled and immediate announcements with severity, audience and expiry.
- [ ] **URS-F-0567** — The system shall enter maintenance modes that separately control authoring, new executions, triggers, API writes and worker dispatch.
- [ ] **URS-F-0568** — The system shall activate tenant, namespace, flow, plugin, runner or instance kill switches.
- [ ] **URS-F-0569** — The system shall define behavior for already-running work when a switch is activated.
- [ ] **URS-F-0570** — The system shall require reason, actor, expiry or review for emergency controls.
- [ ] **URS-F-0571** — The system shall propagate control changes rapidly to all components and expose acknowledgement status.
- [ ] **URS-F-0572** — The system shall automatically expire temporary controls where configured.
- [ ] **URS-F-0573** — The system shall audit activation, extension, bypass and deactivation events.

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

- Functional requirements: URS-F-0566, URS-F-0567, URS-F-0568, URS-F-0569, URS-F-0570, URS-F-0571, URS-F-0572, URS-F-0573
- Non-functional requirements: URS-NFR-AVAILABILITY-004
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
