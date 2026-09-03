# EPIC-838 — Repository correctness re-verification and honest qualification

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `reliability`
- **Primary persona:** AMESH maintainer and platform operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Re-verify GitHub issue #42 against merged main, correct every confirmed regression, finish the structural boundaries that were previously only relocated, and make the Docker-local gate report the PostgreSQL evidence it actually runs.

## In scope

- [ ] Partition the canonical epic catalog into an active manifest and declared completed archive without changing the aggregate planning, validation or bootstrap contract
- [ ] Correct the confirmed release-blocking process, recovery, deferral, Kubernetes result, lifecycle conflict, indexing and cancellation regressions
- [ ] Correct confirmed state-reducer, trace-context, redaction, progress and determinism defects
- [ ] Make the complete Docker-local verification gate run and report the PostgreSQL suite honestly
- [ ] Make administrative PostgreSQL role assumptions fail closed and qualify restricted-login tenant paths
- [ ] Split API bootstrap, dependencies and routers into explicit responsibilities without import side effects or public OpenAPI drift
- [ ] Decompose execution and PostgreSQL repository responsibilities behind their existing ports without changing transaction, fencing or idempotency behavior
- [ ] Make built-in task specifications authoritative for handler schemas and align simulator and executor configuration semantics
- [ ] Reconcile repository/settings/Compose/documentation structure and generated frontend path authority through independently qualified child changes
- [ ] Give every atomic claim in issue #42 an implemented, accepted-as-landed, stale or explicit deferred disposition with linked evidence

## Implementation completion evidence

- 2026-09-03 — Issue #42 was independently re-baselined against merged revision 5bfd911: all sixteen original findings and 22 atomic regression/gate claims have an accepted, child-owned, stale or explicit deferred disposition in docs/reviews/epic-838-rebaseline.md; GitHub issues #43 through #53 are the dependency-ordered qualification boundaries.
- 2026-09-03 — Milestone 0 / issue #43 partitioned the catalog into 20 active and 115 completed records while preserving 135 unique epics across all generators, validators and exports; 15 focused recovery tests and the Docker-local contracts suite passed.

## Explicit non-goals

- Adding GitHub Actions or hosted CI/CD
- Changing public product behavior merely to make files smaller
- Fixing defects not identified by issue #42 or required to validate its child milestones
- Treating renamed or relocated large modules as responsibility decomposition

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-503
- EPIC-504
- EPIC-602
- EPIC-610
- EPIC-837

## Architecture impact

- Primary bounded area: `reliability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Add a focused failing reproduction before correcting each confirmed behavior defect.
- Run the smallest relevant unit, contract, PostgreSQL, Kubernetes or Playwright checks for each child issue.
- Run the complete Docker-local aggregate before merging each child pull request without adding GitHub Actions.
- Record exact child issue, pull-request and Docker evidence in docs/reviews/TESTLOG.md and issue #42.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [ ] Child issues #43 through #53 are merged in dependency order with their own definitions of done satisfied.
- [ ] Every valid or partially valid issue #42 claim is resolved or explicitly deferred with current evidence and impact; stale claims are documented without code churn.
- [ ] PostgreSQL-dependent tests cannot be silently skipped by the complete Docker-local gate.
- [ ] Public API, DSL, execution and generated frontend contracts pass their compatibility checks.
- [ ] The repository board, GitHub tracker and canonical backlog agree with merged reality.
- [ ] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [ ] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [ ] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [ ] Security, tenant isolation, redaction and audit behavior are reviewed.
- [ ] Documentation, examples, migration notes and operational runbooks are updated.
- [ ] Performance and recovery budgets are measured when this epic is on a critical path.
- [ ] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Structural movement can disguise unchanged responsibilities, so acceptance tests must measure boundaries rather than filenames alone.
- Database-role corrections can expose unsupported deployment assumptions and must fail closed.
- Large-file splits can create import cycles or hidden composition side effects unless performed in dependency order.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
