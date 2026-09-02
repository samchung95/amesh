# EPIC-837 — Repository structural reliability roadmap

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `reliability`
- **Primary persona:** AMESH maintainer and platform operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Re-baseline the 2026-09-02 repository structural review against merged main and deliver its valid correctness and maintainability work as independently qualified, low-risk phases.

## In scope

- [x] Every finding in GitHub issue #19 is re-verified against the merged codebase before implementation or deferral.
- [x] The eight identified PostgreSQL repositories use explicit tenant or instance database-role boundaries and pass a non-superuser restricted-login qualification.
- [x] Remaining valid findings are split into bounded child issues with evidence, dependencies and independent definitions of done before implementation.
- [x] Each phase preserves public contracts unless its child issue explicitly versions a contract change.
- [x] Every implemented phase passes focused tests and the complete Docker-local quality gate without adding GitHub Actions.
- [x] Architecture and operations documentation remains aligned with the verified implementation boundary.

## Implementation completion evidence

- 2026-09-02 — Milestone 1 was completed by GitHub issue #20 and pull request #21: eight PostgreSQL repository families now use explicit restricted transaction roles and pass non-superuser Docker-local qualification.
- 2026-09-02 — Milestone 2 was completed by GitHub issue #22 and pull request #32: the authoritative Docker-local aggregate now enforces formatting, frontend lint, generated-SDK integrity, a nonzero coverage floor and every formerly deselected test without GitHub Actions.
- 2026-09-02 — Milestone 3 was completed by GitHub issue #23 and pull request #33: shared fixtures now create one migrated disposable PostgreSQL database per test, migrated test families no longer touch the configured Compose application database, and the complete Docker-local gate passed.
- 2026-09-02 — Milestone 4 was completed by GitHub issue #24 and pull request #34: per-execution worker composition is isolated, cited asynchronous failures are explicit, blocking filesystem work is offloaded, and persistent retry loops use configured bounded backoff; independent Luna review and the complete Docker-local gate passed.
- 2026-09-02 — Milestone 5 was completed by GitHub issue #25 and pull request #35: Codex App Server, Copilot CLI and Pi now share one allowlisted, frame-bounded, timeout-aware managed-process lifecycle; the Pi Node bridge enforces the configured streaming limit; typed Settings own child-process environment and direct OpenRouter fallback configuration; provider-specific compatibility is retained beneath a provider-neutral error hierarchy; independent Luna review and the complete Docker-local gate passed.
- 2026-09-02 — Milestone 6 was completed by GitHub issue #26 and pull request #36: the domain execution contracts no longer read ambient observability state, the broad domain compatibility API lazy-loads YAML/Pillow-backed features, clean imports exclude every cited heavyweight dependency, and typed agent-session lifecycle events now pass through an exhaustive pure state/phase reducer before persistence; independent Luna review and the complete Docker-local gate passed.
- 2026-09-02 — Milestone 7 was completed by GitHub issue #27 and pull request #37: `amesh.app` is now a compatibility surface over the API implementation, execution launch is framework-neutral, and API, worker, CLI and service-role entry points use shared authentication, outbound-policy, runner, handler and executor composition. API and worker recovery profiles remain intentionally distinct, partial runtime construction closes owned runners, the OpenAPI document is byte-identical to the pre-refactor baseline, and the complete Docker-local gate passed.
- 2026-09-02 — Milestone 8 was completed by GitHub issue #28 and pull request #38: every production PostgreSQL repository now declares a checked port, application and domain services depend on ports, common persistence and provider error families cross adapter boundaries, the agent-session-policy repository uses injected transaction/audit/JSON/clock services, and execution persistence exposes separate flow-registry, admission, lifecycle, task-run and control responsibilities while preserving the aggregate API. Focused conformance tests, restricted-role qualification and the complete Docker-local gate passed.
- 2026-09-02 — Milestone 9 was completed by GitHub issue #29 and pull request #39: 50 frozen, feature-adjacent task specifications now authoritatively generate every built-in task descriptor; parsed tasks expose exact immutable kind-bound configuration; runtime handlers no longer consume mutable extra bags; and both DSL validation and execution reject unregistered kinds through stable registry diagnostics. Canonical YAML, the generated flow schema and the 79-entry resource catalog remain unchanged, and the complete Docker-local gate passed.
- 2026-09-02 — Milestone 10 was completed by GitHub issue #30 and pull request #40: Kestra compatibility and executable process roots now have explicit feature packages with module-identity aliases for every historical import and `python -m` path; dependency-neutral DSL, migration, authorization, HTTP-policy and MCP-client boundaries remove the verified production import cycles; non-default Compose profiles and auxiliary Dockerfiles live under `docker/`; and historical verification/progress records live under `docs/reviews/`. Strict mypy, fresh-process imports, compatibility regressions, independent Luna review and the complete Docker-local gate passed.
- 2026-09-03 — Milestone 11 was completed by GitHub issue #31 and pull request #41: frontend wire contracts are now generated deterministically from the canonical OpenAPI document by an isolated, version-pinned toolchain; Docker-local verification rejects drift; stable UI-facing compatibility types remain anchored to generated schemas; and the 192-method API facade now composes eight cohesive resource clients without visual or runtime contract changes. Frontend lint, measured coverage, unit tests, production build, Playwright, independent Luna review and the complete Docker-local gate passed.

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

- [x] Every still-valid #19 finding is either resolved by a qualified child pull request or explicitly deferred with current evidence and impact.
- [x] Critical correctness findings are completed before structural refactors begin.
- [x] Each child phase has focused regression coverage and Docker-local verification evidence.
- [x] The repository board, GitHub tracker and canonical backlog agree with merged reality.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- The review was produced against an older working tree, so stale findings must not create unnecessary changes.
- Large structural cuts can hide behavior changes, so phases must remain signature-preserving and independently reversible.
- Database-role hardening can break supported legacy upgrade preflight unless rollout boundaries remain explicit.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
