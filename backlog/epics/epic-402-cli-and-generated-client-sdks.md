# EPIC-402 — CLI and generated client SDKs

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `api`
- **Primary persona:** Developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Make all common platform operations scriptable and suitable for CI/CD.

## In scope

- [ ] **URS-F-0414** — The system shall provide a cross-platform CLI for authentication, configuration, flows, executions, namespaces, files, plugins and administration.
- [ ] **URS-F-0415** — The system shall support human-readable, JSON and quiet output modes with stable exit codes.
- [ ] **URS-F-0416** — The system shall support declarative apply, diff, delete and export workflows from files or standard input.
- [ ] **URS-F-0417** — The system shall generate typed Python, JavaScript or TypeScript, Java and Go clients from the supported API contract.
- [ ] **URS-F-0418** — The system shall publish clients with version compatibility metadata and retry or pagination helpers.
- [ ] **URS-F-0419** — The system shall store credentials using operating-system secure storage when available.
- [ ] **URS-F-0420** — The system shall support non-interactive service-account authentication in CI.
- [ ] **URS-F-0421** — The system shall provide shell completion and command documentation generated from the command model.

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-005** — Destructive UI and CLI operations shall present impact, scope and recovery consequences before execution. Target: All destructive-action catalog entries have preview or explicit force semantics.
- [ ] **URS-NFR-MAINTAINABILITY-005** — Generated schemas, SDKs, documentation, traceability files and issue bodies shall be reproducible and checked for drift. Target: Repository validation produces no uncommitted generated changes.

## Dependencies

- EPIC-400

## Architecture impact

- Primary bounded area: `api`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- OpenAPI contract and authenticated end-to-end API tests.
- Interaction and CLI contract tests.
- CI regeneration and clean-tree check.
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

- Functional requirements: URS-F-0414, URS-F-0415, URS-F-0416, URS-F-0417, URS-F-0418, URS-F-0419, URS-F-0420, URS-F-0421
- Non-functional requirements: URS-NFR-USABILITY-005, URS-NFR-MAINTAINABILITY-005
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
