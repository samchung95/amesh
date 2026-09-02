# EPIC-301 — Plugin discovery, resolution and dependency isolation

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Resolve a deterministic plugin set for each flow revision without classpath or dependency ambiguity.

## In scope

- [x] **URS-F-0297** — The system shall discover installed plugins from configured directories, registries and embedded distributions.
- [x] **URS-F-0298** — The system shall resolve plugin type references to an exact package version and content digest.
- [x] **URS-F-0299** — The system shall detect duplicate types, incompatible SDK ranges and dependency conflicts before activation.
- [x] **URS-F-0300** — The system shall pin the resolved plugin set into each flow revision and execution.
- [x] **URS-F-0301** — The system shall isolate plugin dependencies from the control plane and from other plugin versions.
- [x] **URS-F-0302** — The system shall refresh plugin catalogs without interrupting executions already pinned to older versions.
- [x] **URS-F-0303** — The system shall expose installed, active, deprecated, incompatible and quarantined plugin status.
- [x] **URS-F-0304** — The system shall support offline installation from verified bundles.

## Implementation completion evidence

- 2026-08-23 — EPIC-301 is complete. AMESH now discovers embedded, configured-directory and verified local/HTTP registry bundles; classifies installed, active, deprecated, incompatible and quarantined versions; resolves resource types through deterministic SemVer backtracking to exact content digests; and persists the immutable resolution into flow revisions inherited by executions. Content-addressed roots and dependency maps keep plugin versions outside the control-plane import path, catalog refreshes preserve existing pins, and authorized API/CLI operations expose, refresh and install SHA-256-verified offline bundles. Docker Compose persists the installation root in `plugin-data`. Evidence: [`test_discovery.py`](../../tests/plugin_sdk/test_discovery.py), generated catalog/registry/resolution schemas and OpenAPI, [`discovery-and-resolution.md`](../../docs/plugin-sdk/discovery-and-resolution.md) and [`TESTLOG.md`](../../docs/reviews/TESTLOG.md). Trusted and isolated callback execution remains with EPIC-302/303; signing, SBOM and provenance enforcement remains with EPIC-305.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-300

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Plugin SDK contract, sandbox and integration tests.
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

- Functional requirements: URS-F-0297, URS-F-0298, URS-F-0299, URS-F-0300, URS-F-0301, URS-F-0302, URS-F-0303, URS-F-0304
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
