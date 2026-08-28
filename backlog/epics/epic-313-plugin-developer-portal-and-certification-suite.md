# EPIC-313 — Plugin developer portal and certification suite

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Plugin developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Reduce plugin development friction and define transparent quality levels.

## In scope

- [x] **URS-F-0391** — The system shall provide generated SDK documentation, starter templates and local sandbox tooling.
- [x] **URS-F-0392** — The system shall run manifest, schema, contract, security, license and compatibility checks in one command.
- [x] **URS-F-0393** — The system shall publish reference fixtures for retries, cancellation, large files, secret redaction and worker restart.
- [x] **URS-F-0394** — The system shall generate human-readable documentation and sample configuration from plugin metadata.
- [x] **URS-F-0395** — The system shall define community, verified and certified quality levels with objective criteria.
- [x] **URS-F-0396** — The system shall allow maintainers to reproduce certification results from public CI evidence.
- [x] **URS-F-0397** — The system shall track compatibility across supported platform releases.

## Implementation completion evidence

- 2026-08-23 — EPIC-313 is complete. The local-first `uv run amesh plugins` portal now scaffolds versioned Python SDK starters, validates manifest-driven configuration in a local sandbox, generates human-readable reference documentation and sample YAML, and runs manifest, schema, contract, security, license and release-compatibility checks in one command. Community, Verified and Certified levels have machine-readable objective criteria; five published retry, cancellation, large-file, secret-redaction and worker-restart fixtures require passing evidence; compatibility matrices test supported AMESH releases; and immutable-commit/public-HTTPS CI evidence plus a deterministic input digest make certification reproducible. Evidence: [`test_certification.py`](../../tests/plugin_sdk/test_certification.py), [`certification.py`](../../src/amesh/plugin_sdk/certification.py), [`plugin-certification.schema.json`](../../schemas/plugin-certification.schema.json), [`certification.md`](../../docs/plugin-sdk/certification.md), [`certification-fixtures.json`](../../examples/plugin-sdk/certification-fixtures.json) and [`TESTLOG.md`](../../TESTLOG.md).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-300
- EPIC-305

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

- Functional requirements: URS-F-0391, URS-F-0392, URS-F-0393, URS-F-0394, URS-F-0395, URS-F-0396, URS-F-0397
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
