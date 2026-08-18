# EPIC-001 — Repository engineering, CI and release foundation

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `engineering`
- **Primary persona:** Contributor
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Create a contributor-friendly monorepo with deterministic builds, quality gates and release automation.

## In scope

- [ ] **URS-F-0008** — The system shall provide documented local development commands for backend, frontend, workers, plugins and documentation.
- [ ] **URS-F-0009** — The system shall enforce formatting, linting, typing, tests, dependency review and secret scanning in continuous integration.
- [ ] **URS-F-0010** — The system shall build reproducible source archives, containers, software bills of materials and signed release provenance.
- [ ] **URS-F-0011** — The system shall apply semantic versioning and publish migration notes for every incompatible change.
- [ ] **URS-F-0012** — The system shall support conventional commits, pull request templates, issue forms and ownership rules.
- [ ] **URS-F-0013** — The system shall validate repository structure, generated files, requirement traceability and architectural decision status.
- [ ] **URS-F-0014** — The system shall provide development containers and a Docker Compose reference environment.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-007** — Official artifacts shall include verifiable source provenance, SBOM and signatures. Target: 100% of official release artifacts have published checksums, SBOMs and signatures.
- [ ] **URS-NFR-USABILITY-003** — A new contributor shall be able to start the reference stack and run a sample flow from documented steps. Target: Median completion below 20 minutes on a clean supported workstation, excluding image download time.
- [ ] **URS-NFR-MAINTAINABILITY-001** — Core domain and reducer logic shall not depend directly on web frameworks, PostgreSQL claim mechanics, search projections or object-storage SDKs. Target: Architecture dependency tests enforce allowed module directions.
- [ ] **URS-NFR-MAINTAINABILITY-004** — Every epic shall include unit, contract, integration or end-to-end evidence appropriate to its risk. Target: All Must requirements have at least one linked automated or manual verification record before GA.
- [ ] **URS-NFR-MAINTAINABILITY-005** — Generated schemas, SDKs, documentation, traceability files and issue bodies shall be reproducible and checked for drift. Target: Repository validation produces no uncommitted generated changes.
- [ ] **URS-NFR-MAINTAINABILITY-006** — Runtime dependencies shall have declared owners, update policy and license compatibility. Target: No unknown-license dependency and no unwaived critical known vulnerability in a release.

## Dependencies

- None

## Architecture impact

- Primary bounded area: `engineering`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Repository validation and CI tests.
- Release pipeline policy gate.
- Quarterly external documentation usability test.
- Static architecture test in CI.
- Traceability validator and release gate.
- CI regeneration and clean-tree check.
- Dependency and license scanning.
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

- Functional requirements: URS-F-0008, URS-F-0009, URS-F-0010, URS-F-0011, URS-F-0012, URS-F-0013, URS-F-0014
- Non-functional requirements: URS-NFR-SECURITY-007, URS-NFR-USABILITY-003, URS-NFR-MAINTAINABILITY-001, URS-NFR-MAINTAINABILITY-004, URS-NFR-MAINTAINABILITY-005, URS-NFR-MAINTAINABILITY-006
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
