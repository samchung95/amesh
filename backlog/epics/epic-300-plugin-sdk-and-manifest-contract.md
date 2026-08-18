# EPIC-300 — Plugin SDK and manifest contract

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Plugin developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Let independent developers extend tasks, triggers, conditions, runners, storage and secrets through stable contracts.

## In scope

- [ ] **URS-F-0289** — The system shall define a versioned plugin manifest with identity, version, vendor, license, entry points, dependencies and compatibility range.
- [ ] **URS-F-0290** — The system shall provide typed SDK interfaces for task, trigger, condition, runner, storage, secret, expression and notification extensions.
- [ ] **URS-F-0291** — The system shall generate configuration schema, documentation metadata and UI controls from plugin declarations.
- [ ] **URS-F-0292** — The system shall provide local test harnesses, fixtures and contract tests for each extension type.
- [ ] **URS-F-0293** — The system shall separate platform API stability from implementation language and transport.
- [ ] **URS-F-0294** — The system shall allow plugins to declare required capabilities, network access, filesystem access and secret scopes.
- [ ] **URS-F-0295** — The system shall return structured user-facing configuration and runtime errors.
- [ ] **URS-F-0296** — The system shall publish a compatibility policy and deprecation lifecycle for SDK changes.

## Non-functional requirements

- [ ] **URS-NFR-MAINTAINABILITY-002** — Public DSL, API, event and plugin contracts shall follow documented semantic-versioning and deprecation rules. Target: No breaking contract change enters a minor or patch release without an approved exception.

## Dependencies

- EPIC-004
- EPIC-200

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Plugin SDK contract, sandbox and integration tests.
- Automated schema and API compatibility checks.
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

- Functional requirements: URS-F-0289, URS-F-0290, URS-F-0291, URS-F-0292, URS-F-0293, URS-F-0294, URS-F-0295, URS-F-0296
- Non-functional requirements: URS-NFR-MAINTAINABILITY-002
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
