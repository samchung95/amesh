# EPIC-500 — Users, groups, roles, bindings and authorization

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Administrator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Enforce fine-grained least-privilege access consistently across every platform resource and action.

## In scope

- [ ] **URS-F-0494** — The system shall define permissions by resource type and action including view, create, update, delete, execute, manage and use.
- [ ] **URS-F-0495** — The system shall bind roles to users, groups and service accounts at instance, tenant and namespace scopes.
- [ ] **URS-F-0496** — The system shall inherit namespace permissions predictably with explicit deny or boundary behavior.
- [ ] **URS-F-0497** — The system shall evaluate authorization server-side for REST, realtime, CLI, UI, worker and plugin-originated requests.
- [ ] **URS-F-0498** — The system shall cache decisions safely without retaining access after binding or group revocation.
- [ ] **URS-F-0499** — The system shall explain authorization decisions to administrators without revealing inaccessible resource details.
- [ ] **URS-F-0500** — The system shall provide built-in least-privilege roles and prevent accidental removal of all administrators.
- [ ] **URS-F-0501** — The system shall test every public endpoint and event stream for tenant and permission isolation.

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-002** — State, admission, retry, cache, policy and authorization decisions shall expose human-readable evidence to authorized users. Target: Decision evidence is present in all catalogued decision scenarios.

## Dependencies

- EPIC-002

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization, audit and administrative end-to-end tests.
- Scenario-based UI and API acceptance tests.
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

- Functional requirements: URS-F-0494, URS-F-0495, URS-F-0496, URS-F-0497, URS-F-0498, URS-F-0499, URS-F-0500, URS-F-0501
- Non-functional requirements: URS-NFR-USABILITY-002
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
