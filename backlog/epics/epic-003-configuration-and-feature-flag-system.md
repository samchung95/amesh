# EPIC-003 — Configuration and feature flag system

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `platform`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Offer typed, layered and auditable configuration for standalone and distributed deployments.

## In scope

- [x] **URS-F-0022** — The system shall load configuration from files, environment variables, command-line flags and secret references with a documented precedence order.
- [x] **URS-F-0023** — The system shall validate all configuration at startup and reject unsafe or contradictory combinations.
- [x] **URS-F-0024** — The system shall redact secrets from diagnostics, API responses, logs and crash reports.
- [x] **URS-F-0025** — The system shall support dynamic reload only for explicitly reloadable settings.
- [x] **URS-F-0026** — The system shall expose effective non-secret configuration and provenance to authorized administrators.
- [x] **URS-F-0027** — The system shall provide feature flags with tenant, namespace and instance scopes.
- [x] **URS-F-0028** — The system shall support deprecation warnings and automated migration of renamed settings.

## Implementation completion evidence

- 2026-08-22 — EPIC-003 is complete. AMESH now loads one typed process snapshot from ordered YAML/JSON files, environment variables, command-line overrides and secret references with explicit provenance; rejects invalid and unsafe startup combinations; redacts active secrets from API, diagnostic and structured-log output; atomically reloads only declared settings; exposes authorized configuration and tenant-bounded diagnostic APIs; persists audited, versioned instance/tenant/namespace feature flags through migration 0032; and migrates renamed settings with safe deprecation warnings. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`configuration.md`](../../docs/operations/configuration.md), [`config.py`](../../src/amesh/config.py), [`feature_flags.py`](../../src/amesh/adapters/postgres/feature_flags.py), [`test_config.py`](../../tests/test_config.py), [`test_configuration_api.py`](../../tests/api/test_configuration_api.py) and [`test_feature_flag_repository.py`](../../tests/adapters/postgres/test_feature_flag_repository.py). Shared URS-NFR-SECURITY-010, URS-NFR-OPERABILITY-004 and URS-NFR-PRIVACY-001 remain In Progress for their other owning epics and external qualification.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-010** — Fresh production-oriented configurations shall fail closed for authentication, plugin trust, network exposure and secrets. Target: Security baseline scanner reports no critical unsafe defaults.
- [ ] **URS-NFR-OPERABILITY-004** — Administrators shall be able to generate a redacted diagnostic bundle without exposing secrets or unrelated tenant data. Target: Canary-secret and cross-tenant scans pass for generated bundles.
- [ ] **URS-NFR-PRIVACY-001** — Product analytics and update checks shall be disabled by default or require an explicit informed opt-in. Target: No undeclared outbound connection occurs in the offline network test.

## Dependencies

- None

## Architecture impact

- Primary bounded area: `platform`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Configuration and service integration tests.
- Configuration conformance and container scan.
- Security test with seeded sensitive data.
- Network capture in a clean reference deployment.
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

- Functional requirements: URS-F-0022, URS-F-0023, URS-F-0024, URS-F-0025, URS-F-0026, URS-F-0027, URS-F-0028
- Non-functional requirements: URS-NFR-SECURITY-010, URS-NFR-OPERABILITY-004, URS-NFR-PRIVACY-001
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
