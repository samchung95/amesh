# EPIC-705 — Documentation, examples and community governance

- **Milestone:** M7 — Compatibility, infrastructure as code and ecosystem
- **Priority:** Must
- **Domain:** `community`
- **Primary persona:** Contributor
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Make the platform understandable, supportable and governable as a durable open-source project.

## In scope

- [ ] **URS-F-0734** — The system shall publish conceptual, tutorial, how-to, reference and operations documentation from versioned source.
- [ ] **URS-F-0735** — The system shall document every public API, CLI command, configuration field, DSL construct and plugin interface.
- [ ] **URS-F-0736** — The system shall provide runnable examples for data, infrastructure, software, approval and AI workflows.
- [ ] **URS-F-0737** — The system shall maintain contribution, review, release, security, code-of-conduct and governance policies.
- [ ] **URS-F-0738** — The system shall define maintainer roles, decision process, roadmap process and conflict resolution.
- [ ] **URS-F-0739** — The system shall publish compatibility, support, deprecation and LTS matrices.
- [ ] **URS-F-0740** — The system shall test documentation code samples and links in CI.
- [ ] **URS-F-0741** — The system shall provide issue triage, discussion and plugin contribution templates.

## Non-functional requirements

- [ ] **URS-NFR-MAINTAINABILITY-005** — Generated schemas, SDKs, documentation, traceability files and issue bodies shall be reproducible and checked for drift. Target: Repository validation produces no uncommitted generated changes.
- [ ] **URS-NFR-OPERABILITY-003** — Reference alerts shall include symptom, likely causes, impact and runbook link. Target: All GA SLO alerts pass alert-quality review and simulated firing tests.

## Dependencies

- EPIC-001

## Architecture impact

- Primary bounded area: `community`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Documentation build and external contributor usability test.
- CI regeneration and clean-tree check.
- Alert fixture and runbook audit.
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

- Functional requirements: URS-F-0734, URS-F-0735, URS-F-0736, URS-F-0737, URS-F-0738, URS-F-0739, URS-F-0740, URS-F-0741
- Non-functional requirements: URS-NFR-MAINTAINABILITY-005, URS-NFR-OPERABILITY-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
