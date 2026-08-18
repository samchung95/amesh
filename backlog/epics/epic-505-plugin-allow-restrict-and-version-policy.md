# EPIC-505 — Plugin allow, restrict and version policy

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Administrator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Control which plugin capabilities and versions may be authored or executed in each scope.

## In scope

- [ ] **URS-F-0534** — The system shall allow or deny plugin packages, types, versions, vendors and capabilities at instance, tenant and namespace scopes.
- [ ] **URS-F-0535** — The system shall distinguish authoring, validation, execution and administration permissions for plugins.
- [ ] **URS-F-0536** — The system shall freeze approved plugin versions and prevent unreviewed automatic upgrades.
- [ ] **URS-F-0537** — The system shall evaluate policy when saving a flow and again when starting an execution.
- [ ] **URS-F-0538** — The system shall quarantine vulnerable, revoked or compromised plugin versions while preserving historical metadata.
- [ ] **URS-F-0539** — The system shall show the effective policy and source of every decision.
- [ ] **URS-F-0540** — The system shall support emergency disable with an impact preview of affected flows and running executions.
- [ ] **URS-F-0541** — The system shall record policy changes and violations in audit history.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-010** — Fresh production-oriented configurations shall fail closed for authentication, plugin trust, network exposure and secrets. Target: Security baseline scanner reports no critical unsafe defaults.

## Dependencies

- EPIC-301
- EPIC-500

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization, audit and administrative end-to-end tests.
- Configuration conformance and container scan.
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

- Functional requirements: URS-F-0534, URS-F-0535, URS-F-0536, URS-F-0537, URS-F-0538, URS-F-0539, URS-F-0540, URS-F-0541
- Non-functional requirements: URS-NFR-SECURITY-010
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
