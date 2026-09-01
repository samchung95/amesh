# EPIC-827 — Agent Session Orchestrator administration and portability

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** Session platform administrator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Give administrators a separately managed session-orchestration control plane for fleet visibility, lifecycle governance and portable migration while reusing AMESH's canonical execution, session, evidence and storage authorities.

## In scope

- [x] The application session data plane, administrative session control plane and reused AMESH runtime authorities are separate versioned interfaces with no second executor, queue, transcript database or evidence ledger.
- [x] Session-specific permissions distinguish create, own-view, fleet-view, lifecycle-control, policy-management, migration and instance administration without weakening tenant, namespace or owner isolation.
- [x] Tenant and instance administrators can inspect cursor-paginated session fleets with filters, operational aggregates, bounded usage and cost, dependency provenance and explicit audited tenant drill-down.
- [x] A dedicated administration workbench exposes session fleet status, trace drill-down, dependency and capacity posture, individual controls and guarded bulk lifecycle actions with responsive accessible behavior.
- [x] Versioned session policies govern admission, concurrency, token, cost, duration, retention and allowed provider, harness and tool dependencies with optimistic concurrency and immutable audit evidence.
- [x] A digest-protected portable profile bundle exports and imports exact agent, prompt, skill, model-policy, schema and MCP tool references without secret plaintext and reports destination compatibility before mutation.
- [x] Session transfer accepts only terminal sessions or sessions paused at a clean checkpoint with no ambiguous external invocation; import is idempotent and preserves public identity, immutable pins, event cursors, evidence and artifact integrity.
- [x] Whole-cluster migration coordinates admission drain, PostgreSQL and object-storage recovery points, secret rebinding, compatibility verification, cutover and rollback without treating Kubernetes process state as authoritative.
- [x] The public application session API and OpenAI-compatible surface remain backward compatible; administrators use a distinct API and UI surface rather than elevated application parameters.
- [x] Docker-local tests cover authorization, filtering, controls, migration integrity, restart, duplicate import, tenant isolation, accessibility and generated contract drift; live OpenRouter Luna evidence remains an explicit opt-in qualification.

## Implementation completion evidence

- 2026-08-30 — M1 complete: ADR-067 separates the application session data plane, session administration plane and canonical runtime authorities. Migration 0069 and the authorization domain add session-client, session-operator and session-admin with product-specific create, own-view, fleet-list, lifecycle, policy and migration grants. Data-plane routes enforce those grants with a bounded legacy execution-permission upgrade bridge that never overrides an explicit session deny. Focused authorization/API/manifest tests and an isolated PostgreSQL migration test passed; evidence is recorded in TESTLOG.md.
- 2026-08-30 — M2 complete: the dedicated administration API projects tenant-isolated session fleets from canonical executions and latest session attempts with fixed keyset pagination; tenant-bound cursors; state, namespace, agent, owner, harness and time filters; bounded usage, cost and dependency posture; and safe instance-level tenant aggregates. Both administration and fleet-list grants are mandatory with no legacy fallback. Eight API/PostgreSQL tests passed against an isolated database, including cross-tenant isolation and cursor traversal; OpenAPI and all four generated SDKs are current.
- 2026-08-30 — M3 complete: the dedicated Session Orchestrator workbench exposes typed fleet filters, bounded aggregates, dependency/capacity posture, immutable agent/harness provenance and canonical trace drill-down. Individually fenced controls and exact-confirmation bulk actions for at most 25 sessions reuse the canonical execution command path and return independent item outcomes. Five focused API tests, 32 frontend assertions, changed-file lint, the production build and responsive Playwright/axe cases passed.
- 2026-08-30 — M4 complete: immutable tenant/namespace/application policies cumulatively enforce admission, concurrency, token, cost, duration, retention and provider/harness/tool allowlists while persisting exact actor/revision/digest provenance. Application scope is bound to authenticated identity. Terminal-session expiry reuses the canonical previewed, legal-hold-aware lifecycle purge authority, and the separately gated workbench exposes effective policy provenance plus optimistic mutation. Fifty-four backend/API/PostgreSQL tests, 35 frontend assertions, lint/type/build checks and responsive Playwright/axe journeys passed.
- 2026-08-30 — M5 complete: digest-protected profile bundles and terminal/clean-checkpoint session bundles now plan and import through strict migration RBAC without secret values or ambiguous effects. Canonical records import transactionally with deterministic tenant-local mappings, exact pins, contiguous cursors, artifact/evidence integrity and idempotent receipts. The plan-first file-upload workbench, OpenAPI and four SDKs are current; 20 backend/API/PostgreSQL tests, 36 frontend assertions, lint/type/build/contract checks and responsive Playwright/axe journeys passed.
- 2026-08-30 — M6 and EPIC complete: loopback-only Docker Compose and Helm session-orchestrator profiles run the webserver, executor and scheduler over external PostgreSQL and S3-compatible storage with file-backed or existing-secret credentials, hardened preflight and role-aware readiness, while mounting no Docker socket and receiving no broker or model-provider credentials. Selective migration uses the plan-first portability workbench; the whole-cluster runbook coordinates admission drain, database/object recovery points, secret rebinding, compatibility checks, cutover and rollback. A fresh-image isolated smoke applied all 71 migrations and reported the API, executor, scheduler, database and object store ready. The complete Docker-local push gate passed 786 backend tests, 109 frontend tests, two Chromium journeys, the 23-case Pi conformance kit twice, contract/backlog/license/review gates, production image probing and release packaging; the opt-in openai/gpt-5.6-luna session smoke also passed. Multi-region, arbitrary external-dependency and production-HA qualification remain explicit non-claims.

## Explicit non-goals

- Creating another workflow engine, executor, queue, transcript store or evidence database
- Exporting provider, MCP, platform or application secret values
- Hot-swapping immutable agent, model, prompt, skill, tool, schema or harness pins inside an active session
- Migrating a session while an external model or tool invocation has an ambiguous outcome
- Implementing proprietary ChatGPT account, mutable thread or hidden-reasoning protocols
- Adding client-domain prompts, skills, tools, workflows, adapters or migration policy
- Claiming multi-region, arbitrary external-dependency or production-HA qualification without measured evidence

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-105
- EPIC-403
- EPIC-500
- EPIC-501
- EPIC-503
- EPIC-504
- EPIC-601
- EPIC-609
- EPIC-610
- EPIC-812
- EPIC-816
- EPIC-826

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization unit and PostgreSQL tests for every session-specific permission, scope and compatibility transition.
- PostgreSQL query and API contract tests for cursor pagination, filters, aggregates and cross-tenant redaction.
- React unit and Playwright tests for the administration workbench, guarded controls, responsive states and accessibility.
- Policy versioning, admission, quota, audit and dependency-provenance tests.
- Deterministic profile export/import round trips with digest, schema, secret-exclusion and compatibility failures.
- Terminal and clean-checkpoint session transfer tests covering restart, duplicate import, ambiguous invocation rejection, cursor continuity and tenant isolation.
- Coordinated database/object-storage migration rehearsal with drain, restore, cutover and rollback evidence.
- OpenAPI and generated SDK drift checks plus the complete Docker-local verification aggregate.
- Opt-in live OpenRouter openai/gpt-5.6-luna smoke after the offline migration and session-control gates pass.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] The session-orchestration administration plane has dedicated contracts, permissions and UI while canonical execution and session records remain the only runtime authority.
- [x] Authorized administrators can understand and safely manage all sessions in their permitted scope through scalable fleet projections and audited lifecycle controls.
- [x] Portable profiles and supported session states migrate through versioned, digest-protected, idempotent workflows without exporting credentials or replaying ambiguous effects.
- [x] Self-hosted deployment and whole-cluster migration documentation matches verified Docker-local and Helm behavior and states all remaining HA or external-dependency non-claims.
- [x] Focused backend, PostgreSQL, frontend, Playwright, migration, generated-contract and Docker-local aggregate gates pass with linked evidence.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A session-specific copy of execution state would split authority and make lifecycle controls or migration unsafe.
- Cross-tenant fleet queries can disclose protected metadata unless aggregates and drill-down authorization are independently enforced.
- Moving a session during an unresolved provider or tool call can duplicate an external effect or lose an accepted result.
- Portable bundles can become secret exfiltration paths unless they contain references and compatibility requirements only.
- Fleet cardinality and bulk controls can overload PostgreSQL or create unsafe fan-out unless pagination, bounded batches and explicit approvals are enforced.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
