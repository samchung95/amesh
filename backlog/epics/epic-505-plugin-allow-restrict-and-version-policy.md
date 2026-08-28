# EPIC-505 — Plugin allow, restrict and version policy

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Administrator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Control which plugin capabilities and versions may be authored or executed in each scope.

## In scope

- [x] **URS-F-0534** — The system shall allow or deny plugin packages, types, versions, vendors and capabilities at instance, tenant and namespace scopes.
- [x] **URS-F-0535** — The system shall distinguish authoring, validation, execution and administration permissions for plugins.
- [x] **URS-F-0536** — The system shall freeze approved plugin versions and prevent unreviewed automatic upgrades.
- [x] **URS-F-0537** — The system shall evaluate policy when saving a flow and again when starting an execution.
- [x] **URS-F-0538** — The system shall quarantine vulnerable, revoked or compromised plugin versions while preserving historical metadata.
- [x] **URS-F-0539** — The system shall show the effective policy and source of every decision.
- [x] **URS-F-0540** — The system shall support emergency disable with an impact preview of affected flows and running executions.
- [x] **URS-F-0541** — The system shall record policy changes and violations in audit history.

## Implementation completion evidence

- 2026-08-23 — EPIC-505 is complete. PostgreSQL migration 0047 stores scoped allow/deny rules, quarantines and attributable decisions. The policy engine evaluates package, type, semantic version, vendor and capability selectors independently for authoring, validation, execution and administration, preserves exact revision pins, fails closed for unreviewed third-party plugins and re-evaluates frozen resolutions at execution start. Authorized APIs and the Plugins UI explain effective sources, manage rules, preview emergency-disable impact and preserve quarantine history; flow save/start and offline bundle installation enforce the same policy, while changes and violations enter audit history. Evidence: [`plugin-governance.md`](../../docs/api/plugin-governance.md), [`0047_plugin_governance.sql`](../../migrations/0047_plugin_governance.sql), [`test_plugin_policy.py`](../../tests/plugins/test_plugin_policy.py), [`test_plugin_policy_repository.py`](../../tests/adapters/postgres/test_plugin_policy_repository.py), [`test_plugin_policy_api.py`](../../tests/api/test_plugin_policy_api.py), and [`shell.spec.ts`](../../frontend/e2e/shell.spec.ts). Shared URS-NFR-SECURITY-010 remains In Progress until the other owning epics and the production security baseline scan complete.

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

- Functional requirements: URS-F-0534, URS-F-0535, URS-F-0536, URS-F-0537, URS-F-0538, URS-F-0539, URS-F-0540, URS-F-0541
- Non-functional requirements: URS-NFR-SECURITY-010
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
