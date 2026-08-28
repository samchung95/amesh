# EPIC-410 — Namespace, settings and administration UI

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** Administrator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Administer resources and platform configuration without direct database or file access.

## In scope

- [x] **URS-F-0478** — The system shall browse namespace hierarchy, inherited settings, files, key-values, secrets metadata and plugin defaults.
- [x] **URS-F-0479** — The system shall manage users, groups, roles, bindings, service accounts, tokens and identity providers according to permissions.
- [x] **URS-F-0480** — The system shall view workers, services, queues, storage, search, migrations and component health.
- [x] **URS-F-0481** — The system shall manage retention, announcements, maintenance, kill switches and feature flags.
- [x] **URS-F-0482** — The system shall display effective configuration and provenance while redacting secrets.
- [x] **URS-F-0483** — The system shall require reauthentication or step-up approval for high-risk administrative operations.
- [x] **URS-F-0484** — The system shall provide dry-run and impact previews for bulk or destructive changes.
- [x] **URS-F-0485** — The system shall record every successful and rejected administrative action in audit history.

## Implementation completion evidence

- 2026-08-23 — EPIC-410 is complete. The permission-gated administration workbench composes namespace hierarchy and inherited metadata, identity and access policy, service-account credentials, provider entry points, component health, effective redacted configuration, feature flags and immutable audit evidence. Retention, announcement, maintenance and execution-kill-switch changes use typed tenant controls with server-generated impact/recovery previews, five-minute actor/tenant/draft-bound HMAC approvals, exact confirmation and optimistic versions. Fresh PostgreSQL integration verified atomic control/audit success, rejected-action evidence and tenant isolation; Chromium verified the complete workflow, redaction and automated accessibility. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`administration.md`](../../docs/api/administration.md), [`AdministrationPage.tsx`](../../frontend/src/pages/AdministrationPage.tsx), [`test_configuration_api.py`](../../tests/api/test_configuration_api.py), and [`administration.py`](../../src/amesh/domain/administration.py).

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-005** — Destructive UI and CLI operations shall present impact, scope and recovery consequences before execution. Target: All destructive-action catalog entries have preview or explicit force semantics.

## Dependencies

- EPIC-404
- EPIC-500
- EPIC-509

## Architecture impact

- Primary bounded area: `ui`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated browser, accessibility and manual usability tests.
- Interaction and CLI contract tests.
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

- Functional requirements: URS-F-0478, URS-F-0479, URS-F-0480, URS-F-0481, URS-F-0482, URS-F-0483, URS-F-0484, URS-F-0485
- Non-functional requirements: URS-NFR-USABILITY-005
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
