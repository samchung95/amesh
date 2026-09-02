# EPIC-837 — Repository structural reliability roadmap

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `reliability`
- **Primary persona:** AMESH maintainer and platform operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Re-baseline the 2026-09-02 repository structural review against merged main and deliver its valid correctness and maintainability work as independently qualified, low-risk phases.

## In scope

- [ ] Every finding in GitHub issue #19 is re-verified against the merged codebase before implementation or deferral.
- [ ] The eight identified PostgreSQL repositories use explicit tenant or instance database-role boundaries and pass a non-superuser restricted-login qualification.
- [ ] Remaining valid findings are split into bounded child issues with evidence, dependencies and independent definitions of done before implementation.
- [ ] Each phase preserves public contracts unless its child issue explicitly versions a contract change.
- [ ] Every implemented phase passes focused tests and the complete Docker-local quality gate without adding GitHub Actions.
- [ ] Architecture and operations documentation remains aligned with the verified implementation boundary.

## Implementation completion evidence

- 2026-09-02 — Milestone 1 was completed by GitHub issue #20 and pull request #21: eight PostgreSQL repository families now use explicit restricted transaction roles and pass non-superuser Docker-local qualification.
- 2026-09-02 — Findings 2–16 from GitHub issue #19 were re-baselined against merged main and split into bounded child issues #22–#31. Milestone 2 (#22) is making the Docker-local aggregate authoritative by removing test deselections and enforcing formatting, lint, generated-SDK and nonzero coverage gates without adding GitHub Actions.

## Explicit non-goals

- Implementing all structural findings in one pull request
- Changing product behavior while moving code unless a child issue explicitly requires it
- Adding GitHub Actions or hosted CI
- Fixing unrelated defects discovered during a bounded child job

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-503
- EPIC-504
- EPIC-602
- EPIC-610

## Architecture impact

- Primary bounded area: `reliability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Re-run the cited structural measurements against the current merged revision before opening each child job.
- Run restricted-role PostgreSQL tests that cover tenant isolation, instance administration, legacy upgrade preflight and recovery operations.
- Run Ruff, strict mypy, migration and planning validation, strict documentation and the complete Docker-local aggregate for each implementation phase.
- Record child issue and pull-request evidence back on GitHub issue #19 and this epic.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [ ] Every still-valid #19 finding is either resolved by a qualified child pull request or explicitly deferred with current evidence and impact.
- [ ] Critical correctness findings are completed before structural refactors begin.
- [ ] Each child phase has focused regression coverage and Docker-local verification evidence.
- [ ] The repository board, GitHub tracker and canonical backlog agree with merged reality.
- [ ] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [ ] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [ ] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [ ] Security, tenant isolation, redaction and audit behavior are reviewed.
- [ ] Documentation, examples, migration notes and operational runbooks are updated.
- [ ] Performance and recovery budgets are measured when this epic is on a critical path.
- [ ] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- The review was produced against an older working tree, so stale findings must not create unnecessary changes.
- Large structural cuts can hide behavior changes, so phases must remain signature-preserving and independently reversible.
- Database-role hardening can break supported legacy upgrade preflight unless rollout boundaries remain explicit.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
