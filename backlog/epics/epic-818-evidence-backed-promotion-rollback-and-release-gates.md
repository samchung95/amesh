# EPIC-818 — Evidence-backed promotion, rollback and release gates

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Release manager
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Promote an exact workflow or agent revision only when its client-defined policy is satisfied by fresh immutable evidence, with auditable rollback and an immediate kill switch.

## In scope

- [x] A promotion policy pins exact tests, assertions, differential results, health requirements, budgets and approval rules.
- [x] A tenant-scoped immutable gate binds fresh evidence to exact configuration digests and rejects stale or mismatched evidence.
- [x] Preview and apply are separately authorized, audited and protected by optimistic concurrency.
- [x] Rollback selects an exact prior revision, preserves history and supports an immediate policy kill switch.
- [x] Clients own thresholds and cutover decisions; AMESH supplies neutral evaluation and enforcement contracts.
- [x] API, CLI and UI paths preserve authorization and behavior across restart, and a live local smoke proves promote then rollback.

## Implementation completion evidence

- 2026-08-26 — EPIC-818 is complete. Tenant-scoped immutable policies bind fresh evidence to exact configuration digests and enforce client-defined tests, health, budget and approval requirements; preview and apply use separate authorization, optimistic concurrency and immutable audit/outbox history. API, CLI and the `/releases` console support promotion, exact rollback and the immediate kill switch. Nine focused backend/UI-session tests, 23 frontend client tests, the production build and three Chromium Playwright scenarios passed, including view/manage permissions, accessibility and screenshot export. Live target `epic818-qual-f6003249d4d94572b640672f78112e2e` rejected missing evidence with HTTP 409, promoted revisions 1 then 2, rolled back to the exact revision-1 digest at version 3, and preserved `PROMOTE → PROMOTE → ROLLBACK` history after API restart. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`release-promotion.md`](../../docs/how-to/release-promotion.md), [`ReleaseControlsPage.tsx`](../../frontend/src/pages/ReleaseControlsPage.tsx), [`release-controls.spec.ts`](../../frontend/e2e/release-controls.spec.ts), and [`test_promotion_cli.py`](../../tests/test_promotion_cli.py).

## Explicit non-goals

- Choosing domain-specific acceptance thresholds for clients
- Executing a client's production cutover outside AMESH

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-510
- EPIC-705
- EPIC-809
- EPIC-817

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Promotion policy, evidence freshness and digest-binding unit tests.
- Authorization, tenant-isolation, audit and optimistic-concurrency tests.
- Rollback history, restart and kill-switch integration tests.
- API, CLI, UI and live local promote/rollback smoke test.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] No revision can be promoted with stale, incomplete or differently pinned evidence.
- [x] Promotion, rollback and kill-switch actions produce complete immutable audit evidence.
- [x] Client-neutral release-gate and recovery runbooks are verified end to end.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Stale qualification evidence can be incorrectly applied to a changed configuration.
- Rollback without exact immutable history can create an untraceable mixed release.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
