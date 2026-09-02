# EPIC-500 — Users, groups, roles, bindings and authorization

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Administrator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Enforce fine-grained least-privilege access consistently across every platform resource and action.

## In scope

- [x] **URS-F-0494** — The system shall define permissions by resource type and action including view, create, update, delete, execute, manage and use.
- [x] **URS-F-0495** — The system shall bind roles to users, groups and service accounts at instance, tenant and namespace scopes.
- [x] **URS-F-0496** — The system shall inherit namespace permissions predictably with explicit deny or boundary behavior.
- [x] **URS-F-0497** — The system shall evaluate authorization server-side for REST, realtime, CLI, UI, worker and plugin-originated requests.
- [x] **URS-F-0498** — The system shall cache decisions safely without retaining access after binding or group revocation.
- [x] **URS-F-0499** — The system shall explain authorization decisions to administrators without revealing inaccessible resource details.
- [x] **URS-F-0500** — The system shall provide built-in least-privilege roles and prevent accidental removal of all administrators.
- [x] **URS-F-0501** — The system shall test every public endpoint and event stream for tenant and permission isolation.

## Implementation completion evidence

- 2026-08-21 — EPIC-500 is complete. AMESH now persists UUIDv7 users, groups and non-human principals; roles, resource/action permissions and instance/tenant/namespace bindings; explicit deny and namespace-boundary semantics; policy-versioned decision caching with immediate binding/group revocation; administrator-only explanations; immutable built-in roles and effective last-administrator protection; audited administration APIs; tenant-aware CLI calls; and shared worker/plugin policy contracts. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`authorization.py`](../../src/amesh/domain/authorization.py), [`authorization_repository.py`](../../src/amesh/adapters/postgres/authorization_repository.py), [`test_authorization_repository.py`](../../tests/adapters/postgres/test_authorization_repository.py), and [`test_authorization_api.py`](../../tests/api/test_authorization_api.py).

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

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0494, URS-F-0495, URS-F-0496, URS-F-0497, URS-F-0498, URS-F-0499, URS-F-0500, URS-F-0501
- Non-functional requirements: URS-NFR-USABILITY-002
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
