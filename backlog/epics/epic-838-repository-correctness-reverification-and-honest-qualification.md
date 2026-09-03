# EPIC-838 — Repository correctness re-verification and honest qualification

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `reliability`
- **Primary persona:** AMESH maintainer and platform operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Re-verify GitHub issue #42 against merged main, correct every confirmed regression, finish the structural boundaries that were previously only relocated, and make the Docker-local gate report the PostgreSQL evidence it actually runs.

## In scope

- [x] Partition the canonical epic catalog into an active manifest and declared completed archive without changing the aggregate planning, validation or bootstrap contract
- [x] Correct the confirmed release-blocking process, recovery, deferral, Kubernetes result, lifecycle conflict, indexing and cancellation regressions
- [x] Correct confirmed state-reducer, trace-context, redaction, progress and determinism defects
- [x] Make the complete Docker-local verification gate run and report the PostgreSQL suite honestly
- [x] Make administrative PostgreSQL role assumptions fail closed and qualify restricted-login tenant paths
- [x] Split API bootstrap, dependencies and routers into explicit responsibilities without import side effects or public OpenAPI drift
- [x] Decompose execution and PostgreSQL repository responsibilities behind their existing ports without changing transaction, fencing or idempotency behavior
- [x] Make built-in task specifications authoritative for handler schemas and align simulator and executor configuration semantics
- [x] Reconcile repository/settings/Compose/documentation structure and generated frontend path authority through independently qualified child changes
- [x] Give every atomic claim in issue #42 an implemented, accepted-as-landed, stale or explicit deferred disposition with linked evidence

## Implementation completion evidence

- 2026-09-03 — Issue #42 was independently re-baselined against merged revision 5bfd911: all sixteen original findings and 22 atomic regression/gate claims have an accepted, child-owned, stale or explicit deferred disposition in docs/reviews/epic-838-rebaseline.md; GitHub issues #43 through #53 are the dependency-ordered qualification boundaries.
- 2026-09-03 — Milestone 0 / issue #43 partitioned the catalog into 20 active and 115 completed records while preserving 135 unique epics across all generators, validators and exports; 15 focused recovery tests and the Docker-local contracts suite passed.
- 2026-09-03 — Milestone 1 / issue #44 repaired the default Pi worker launch, transient recovery and search isolation, cache-safe task deferral, successful Kubernetes terminal-log handling, lifecycle conflict response and tool-cleanup cancellation semantics. Seventy-one focused Docker tests, an independent Sol/high review and the complete Docker-local aggregate passed.
- 2026-09-03 — Milestone 2 / issue #45 made agent-session transitions reducer-owned and typed, replaced full progress-journal replay with tenant-bound incremental projections and a qualified 0078-to-0079 backfill, preserved semantic redaction shapes, wired production and dynamic-child trace propagation, made determinism analysis linear and aligned simulator handler values with execution. Focused unit and PostgreSQL suites, an independent Sol/high review and the complete Docker-local aggregate passed.
- 2026-09-03 — Milestone 3 / issue #46 made the Docker-local backend gate supply PostgreSQL configuration, fail missing-database fixture skips, enforce 75% coverage, assert degraded readiness and observed histogram samples, discover every PostgreSQL transaction path, and check planning drift without mutation. Every specialist deferral now has an accountable repository role and review date. An independent Sol/high review and the complete Docker-local aggregate passed 1,393 backend tests with 16 documented specialist skips and 81.41% coverage.
- 2026-09-03 — Milestone 4 / issue #47 made missing tenant-administration grants fail closed, predicated tenant-bearing authorization reads, moved quota and resolver paths behind tenant transactions, and made notification waits enter the restricted runtime role. Cancellation-safe cleanup prevents pooled sessions from retaining listeners, tenant context or role state. Pre-0075 preflight behavior, runtime/admin visibility, BYPASSRLS scope and rolling-upgrade operations are explicit and tested. Two independent Sol/high reviews and the complete Docker-local aggregate passed 1,400 backend tests with 16 documented skips and 81.42% coverage.
- 2026-09-03 — Milestone 5 / issue #48 made API import inert, replaced process-global dependency caches with application-owned lazy provider containers, split 331 operations across cohesive feature routers without route-order or OpenAPI drift, and made MCP lifecycle, authentication and cleanup application-owned. Focused compatibility tests, three independent Sol/high reviews and the complete Docker-local aggregate passed 1,409 backend tests with 16 documented skips and the enforced 75% coverage threshold.
- 2026-09-03 — Milestone 6 / issue #49 reduced the executor compatibility facade to 783 lines and split orchestration, attempt, condition, flowable, loop, lifecycle, handler and cache/result responsibilities behind explicit leaf interfaces; every executor implementation file is at most 900 lines and every callable at most 120 lines. Public exports, signatures, persisted schemas and deterministic attempt/cache/retry identities remained compatible. Two independent Sol/high reviews and the complete Docker-local aggregate passed 1,435 backend tests with 16 documented skips and 81.59% coverage, 124 frontend tests and build, all 10 Playwright journeys, 11 Pi worker tests, all 27 harness conformance cases, and the remaining planning, backlog, generated-contract, SDK, image and package gates.
- 2026-09-03 — Milestone 7 / issue #50 made the five execution repository ports pairwise-distinct over one transaction-owned aggregate, adopted shared transaction, audit, JSON and clock services across all 41 engine-owning PostgreSQL repository source files, centralized tenant resolution and execution row mapping, and routed not-found and version conflicts through the port vocabulary. Concurrency, rollback, restricted-role and static adoption tests, two independent Sol/high reviews and the complete Docker-local aggregate passed 1,471 backend tests with 16 documented skips and the enforced 75% coverage threshold, 124 frontend tests and build, all 10 Playwright journeys, 11 Pi worker tests, all 27 harness conformance cases, and the remaining planning, backlog, generated-contract, SDK, image and package gates.
- 2026-09-04 — Milestone 8 / issue #51 made built-in task schemas handler-authoritative through independently checked runtime contracts, explicit task-kind ownership, one structural-field authority and stable registry diagnostics. Public model controls now match model handlers, persisted canonical definitions and semantic hashes remain immutable repository-row data, and flow tests share executor switch normalization and inline foreach ordering, batching and iteration values. Focused contract, model, simulator and row tests plus an independent Sol/high review passed. The complete Docker-local aggregate also passed with 81.56% backend coverage, 124 frontend tests and build, all 10 Playwright journeys, 11 Pi worker tests, all 27 deterministic harness conformance cases, generated-contract and SDK integrity checks, strict documentation, image probes, and repository plus four-SDK packaging.
- 2026-09-04 — Milestone 9 / issue #52 established canonical identity, lifecycle and platform feature packages while preserving legacy public symbol identity; made shared PostgreSQL test lifecycle, Settings-derived environment examples and local Compose templates authoritative; completed ADR and screenshot evidence navigation; and aligned worker runner construction, test naming and current progress evidence. Focused suites and an independent Sol/high review passed. The complete Docker-local aggregate passed 1,516 backend tests with 20 documented skips and 81.62% coverage, 124 frontend tests and build, all 10 Playwright journeys, 11 Pi worker tests, all 27 deterministic harness conformance cases, generated-contract and SDK integrity checks, strict documentation, production and model-engine image probes, and repository plus four-SDK packaging.
- 2026-09-04 — Milestone 10 / issue #53 bound all 187 frontend network calls to generated OpenAPI path and method descriptors with generated request-body and success-response types; replaced hand-maintained compatibility mirrors with exact generated aliases and compile-time drift guards; and regrouped 84 flat page and component files into feature-owned modules while preserving all 23 route contracts and visual styling. Nine focused Python contract and boundary tests, 136 frontend tests at 78.37% branch coverage, three affected workflow Playwright journeys and independent Sol/high reviews passed. The complete Docker-local aggregate passed 1,523 backend tests with 20 documented skips and 81.62% coverage, 136 frontend tests and build, two application and eight documentation Playwright journeys, 11 Pi worker tests, all 27 deterministic harness conformance cases, generated-contract and SDK integrity checks, strict documentation, production and model-engine image probes, and repository plus four-SDK packaging.
- 2026-09-04 — Parent issue #42 closed after dependency-ordered child issues #43 through #53 were closed by pull requests #54 through #64. The frozen claim dispositions, child evidence, Docker-local qualification, compatibility checks and repository trackers were reconciled with no release-blocking EPIC-838 claim remaining.

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

- [x] Child issues #43 through #53 are merged in dependency order with their own definitions of done satisfied.
- [x] Every valid or partially valid issue #42 claim is resolved or explicitly deferred with current evidence and impact; stale claims are documented without code churn.
- [x] PostgreSQL-dependent tests cannot be silently skipped by the complete Docker-local gate.
- [x] Public API, DSL, execution and generated frontend contracts pass their compatibility checks.
- [x] The repository board, GitHub tracker and canonical backlog agree with merged reality.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Structural movement can disguise unchanged responsibilities, so acceptance tests must measure boundaries rather than filenames alone.
- Database-role corrections can expose unsupported deployment assumptions and must fail closed.
- Large-file splits can create import cycles or hidden composition side effects unless performed in dependency order.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
