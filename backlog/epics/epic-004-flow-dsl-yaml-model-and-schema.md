# EPIC-004 — Flow DSL, YAML model and schema

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `dsl`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Define a declarative workflow language capable of representing the full target feature set.

## In scope

- [x] **URS-F-0029** — The system shall parse YAML and JSON flow definitions into a versioned canonical intermediate representation.
- [x] **URS-F-0030** — The system shall validate required fields, types, uniqueness, references, cycles and plugin-specific properties.
- [x] **URS-F-0031** — The system shall preserve comments and stable formatting where practical during visual or programmatic edits.
- [x] **URS-F-0032** — The system shall generate JSON Schema and editor metadata for every core and plugin-defined resource.
- [x] **URS-F-0033** — The system shall support namespaces, flow identifiers, descriptions, labels, inputs, variables, tasks, triggers, errors, finally blocks and outputs.
- [x] **URS-F-0034** — The system shall return machine-readable validation errors with source ranges and remediation hints.
- [x] **URS-F-0035** — The system shall support forward-compatible extension fields while rejecting unknown core fields by policy.
- [x] **URS-F-0036** — The system shall calculate deterministic semantic hashes that ignore non-semantic formatting.

## Implementation completion evidence

- 2026-08-22 — EPIC-004 is complete. AMESH now parses YAML 1.2 and JSON into the explicit `amesh.flow/v1` canonical IR; validates common shape, identifiers, references, cycles and installed resource configuration; preserves comments and stable layout for programmatic edits; emits source-ranged issues with remediation hints; permits only `x-` forward extensions; generates aggregate flow and resource/editor schemas; and hashes semantic content independently of formatting. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`flow-dsl.md`](../../docs/architecture/flow-dsl.md), [`source.py`](../../src/amesh/dsl/source.py), [`registry.py`](../../src/amesh/dsl/registry.py), [`test_dsl_contract.py`](../../tests/test_dsl_contract.py), [`flow.schema.json`](../../schemas/flow.schema.json), and [`resource-catalog.json`](../../schemas/resource-catalog.json). Shared URS-NFR-USABILITY-001 and URS-NFR-MAINTAINABILITY-002 remain In Progress until their UI, plugin, API and upgrade owners complete.

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-001** — Flow validation shall return actionable errors tied to source locations. Target: p95 validation response below 1 second for a 5,000-line flow; every error includes code and location.
- [ ] **URS-NFR-MAINTAINABILITY-002** — Public DSL, API, event and plugin contracts shall follow documented semantic-versioning and deprecation rules. Target: No breaking contract change enters a minor or patch release without an approved exception.

## Dependencies

- EPIC-002

## Architecture impact

- Primary bounded area: `dsl`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Parser, schema, rendering and compatibility tests.
- Editor benchmark and validation contract tests.
- Automated schema and API compatibility checks.
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

- Functional requirements: URS-F-0029, URS-F-0030, URS-F-0031, URS-F-0032, URS-F-0033, URS-F-0034, URS-F-0035, URS-F-0036
- Non-functional requirements: URS-NFR-USABILITY-001, URS-NFR-MAINTAINABILITY-002
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
