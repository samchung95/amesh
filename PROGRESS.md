# Progress Log

## Current state

- What works: the original five requested post-MVP areas plus durable cache, triggers, execution evidence and SLA/check policies are implemented, evidence-linked and deployed through migration 0031.
- What's in flight: the 50-epic local completion program is tracked on Agent Hotel cards `c37`–`c86`; EPIC-000 on card `c37` has passed its final gates and EPIC-003 on card `c38` is next. The local Docker Compose deployment remains available at `http://localhost:8000`.
- Known broken / TODO: 20 external-cloud, SaaS, hosted-release, independent-certification, multi-region or long-duration epics are deferred. Cards `c15` and `c29` preserve unrelated test failures and are not blockers for the local program.
- How to run/test: use `uv run --extra runtime --extra dev pytest`; set `AMESH_TEST_DATABASE_URL` for PostgreSQL integration tests and `OPENROUTER_API_KEY` for live LLM tests.

## Session log

### 2026-08-22 (50-epic local completion program, EPIC-000 completion)

- Did: completed EPIC-000 with a generated 837-item compatibility inventory, machine-readable public-source provenance and strict clean-room role handoffs, pinned-target validation, release-blocking REUSE 6.2.0 licensing, isolated one-way token-shingle similarity scanning, trademark/contribution policy and a repeatable target-rebase guide. Linked URS-F-0001 through URS-F-0007 to evidence.
- Verification: 272 tests collected against an isolated PostgreSQL database; 264 passed, six environment/profile tests skipped and the two pre-existing card `c15`/`c29` assertions were explicitly deselected. A fresh database applied all 31 migrations. REUSE, Ruff, strict mypy, workflow YAML, package-script syntax, clean-room, planning regeneration, backlog and diff gates passed.
- Deviations from plan: no runtime or LLM change was needed. The first shared-database run was invalid because deployed services consumed test work; the isolated rerun passed without code changes. The configured OpenRouter `openai/gpt-5.6-luna` default is unchanged.
- Next step when resuming: close and commit card `c37`, then select EPIC-003 on card `c38` and implement the typed configuration/feature-flag system.

### 2026-08-21

- Did: fast-forwarded the accepted Python MVP rescope onto `main`; implemented and verified the PostgreSQL durable queue, transactional outbox publisher and consumer inbox; added a live OpenRouter contract test with GPT-5.6 Luna as the default model; established the root architecture and cold-resume tracker; closed W1; implemented persisted execution/task/attempt state and restartable DAG scheduling; closed W2; implemented the runner port, local-process adapter, persisted retry scheduling, timeout/cancellation escalation and stale-attempt fencing; closed W3; implemented timezone-aware cron calculation, transactional occurrence deduplication, sandboxed native expressions, output interpolation and `runIf`; closed W4; implemented the Kubernetes Job adapter and verified pod-deletion reconciliation on kind; closed W5; implemented `core.http`, OpenAI-compatible `agent.llm`, official-SDK `agent.mcp`, authenticated REST and matching CLI surfaces; ran the checked-in Luna → Kubernetes shell → HTTP demo through the API; closed W6; added the uv-locked non-root image, external-PostgreSQL Helm migration hook, server/recovery-worker deployments, RBAC, JSON logs and Prometheus endpoint; installed on a fresh kind cluster and ran the demo through the installed Service; closed W7; reconciled evidence-linked progress into all affected epic files through the canonical planning generator.
- W8 checkpoint: candidate `amesh:mvp-w8f` passed 47 tests at 80.47% branch coverage plus artifact, Helm, policy and exact-image cron/log checks. The owner-accepted soak reached cycle 270 with 270 independently re-read, unique single-attempt successes after 270 task-pod kills, 27 server-pod kills and 13 worker-pod kills; both replacement Deployments were Ready with zero restarts. The two-second soak-only recovery grace intentionally produced fenced losing contenders while preserving exactly-once persisted completion.
- Deviations from plan: on 2026-08-21 the product owner deferred the remaining uninterrupted 24-hour soak and authorized release progression. The full-duration criterion is preserved under EPIC-611 and no broader production-readiness claim is made. The W7 worker remains a deliberately single-tenant delayed recovery loop; general distributed dispatch and HA remain deferred.
- Next step when resuming: continue the dependency-ordered backlog; run EPIC-611's uninterrupted 86,400-second qualification before making broader availability, scale or production-readiness claims. The path-back audit left all 900 broad roadmap requirements `Proposed` because the MVP slices do not satisfy their complete acceptance criteria.

### 2026-08-21 (post-MVP roadmap session 1)

- Did: accepted the five requested roadmap areas; registered the repository with the Agent Hotel daemon; made its board the primary execution tracker; selected dependency-free EPIC-002 as the first card; verified the existing tests; mapped direct dependency chains; researched UUIDv7 and canonical serialization choices.
- Deviations from plan: the finished MVP plan was superseded by the requested roadmap-completion goal. No product code has changed yet.
- Next step when resuming: implement and verify EPIC-002 against card `c1`, update its canonical backlog evidence, and only then select the next dependency-ready epic.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-002 completion)

- Did: added canonical natural-key models; adopted UUIDv7 through the uv-locked `uuid6` package; switched new execution, task-run, attempt, revision, event and worker IDs to UUIDv7; added shared metadata, lifecycle, canonical hash and ETag contracts; persisted managed-resource metadata through migration 0003; exposed flow ETags and REST `If-Match`; regenerated contracts; linked all seven EPIC-002 requirements to evidence.
- Verification: 53 tests passed with real PostgreSQL at 76.11% branch coverage; clean-database migrations 0001–0003 passed; focused ETag and UUIDv7 persistence tests passed; Ruff and strict mypy passed.
- Deviations from plan: the existing Compose database required its already-applied 0001/0002 checksums registered before migration 0003; no schema or product data was reset. The worker software-version column required the new concurrency field to be named `resource_version`.
- Next step when resuming: select EPIC-500 as the next dependency-ready requested epic and begin its architecture-first RBAC design.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-500 completion)

- Did: closed EPIC-002 on card `c1` and committed it as `b9c7eb5`; selected and completed EPIC-500 on card `c2`; accepted ADR-018; added PostgreSQL-authoritative principals, groups, roles, permissions, scoped bindings and namespace boundaries; implemented deny-overrides evaluation, policy-version cache invalidation, group and binding revocation, administrator explanations, built-in roles and effective last-admin protection; applied server-side authorization to every resource API; added tenant-aware CLI requests, shared non-human actor contracts, audit writes, migration 0004 and the administration runbook; linked all eight functional requirements to evidence.
- Verification: 68 tests passed with real PostgreSQL at 78.54% branch coverage; clean-database migrations 0001–0004 passed; every current endpoint has public-or-protected acceptance evidence; Ruff, strict mypy, lock, generated contract/planning, backlog, clean-room, compile, build, Compose, Helm and diff gates passed. The pure evaluator measured 1.64 microseconds per decision over 100,000 local calls without making a distributed throughput claim.
- Deviations from plan: no authorization dependency was added because the evaluated libraries do not replace AMESH-specific persistence, evidence, invalidation and administrator-safety rules; Oso Cloud would also introduce a second external authority. Shared `URS-NFR-USABILITY-002` is `In Progress`: EPIC-500's authorization evidence is complete, while its admission/cache/UI owners remain open.
- Next step when resuming: close board card `c2`, commit EPIC-500, select dependency-ready EPIC-501 and implement durable service-account/API-token credentials before the login/session epic.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-501 start)

- Did: closed and committed EPIC-500 as `8a4b227`; selected EPIC-501 on card `c3`; reviewed Python `secrets`/HMAC, RFC 6750 bearer-token guidance and self-contained token tradeoffs; accepted ADR-019 for 256-bit opaque bearer tokens whose HMAC digests, revocation state, scopes, audiences, expiry, usage and quotas remain PostgreSQL-authoritative.
- Deviations from plan: no credential dependency was added. Self-contained JWT/PASETO tokens would still require authoritative revocation, quota and last-used state, while password hashing is unnecessary for server-generated 256-bit secrets.
- Next step when resuming: implement token/scope domain contracts, migration 0005, the credential repository/service and durable bearer authentication entry point.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-501 completion)

- Did: completed EPIC-501 with PostgreSQL-authoritative service/workload credentials; one-time 256-bit opaque token disclosure; keyed digests; scope/audience/expiry/last-use metadata; independent quotas; bounded rotation overlap; current/previous pepper rollout; immediate token, derived-child and principal-epoch revocation; worker/plugin exchange; production durable bearer authentication; failure/success auditing without plaintext; migration 0005; Helm Secret wiring; ADR-019; API contract and runbook updates; and evidence links for URS-F-0502 through URS-F-0509.
- Verification: 76 tests passed with real PostgreSQL at 79.14% branch coverage; a clean database applied migrations 0001–0005; Ruff, strict mypy, lock, generated OpenAPI/planning, backlog, clean-room, compile, Compose and Helm gates passed. Shared `URS-NFR-SECURITY-002` and `URS-NFR-SECURITY-006` are `In Progress` because their other owning epics remain open.
- Next step when resuming: close board card `c3`, commit EPIC-501, and select the next dependency-ready requested epic.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-503 start)

- Did: closed EPIC-501 as `df29a1a`; selected dependency-ready EPIC-503 on card `c4`; compared application filters, shared-schema PostgreSQL RLS and database-per-tenant approaches; accepted ADR-020 for explicit request context plus transaction-local `amesh_runtime` RLS enforcement.
- Deviations from plan: no tenancy dependency was added. The required lifecycle, policy and repository contracts are AMESH-specific, while PostgreSQL already provides the database isolation primitive.
- Next step when resuming: implement tenant domain contracts, migration 0006, the tenant administration repository/API and tenant-scoped runtime transactions.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-503 completion)

- Did: completed EPIC-503 with explicit multi-tenant request context; tenant lifecycle, policy, export and administration APIs; PostgreSQL forced RLS through non-bypass runtime/administration roles and restricted resolver functions; tenant-scoped execution and durable transport; tenant-specific queue notifications; execution/plugin/feature quotas; worker-group routing; immutable storage prefixes; separately audited super-administration; Helm settings; ADR-020; migrations 0006–0009; and the multi-tenancy runbook. Linked URS-F-0518 through URS-F-0525 to automated evidence.
- Verification: 82 tests passed with real PostgreSQL at 79.65% branch coverage; a clean database applied migrations 0001–0009 and exposed 18 tenant-isolation policies; a non-superuser/non-owner tenant-repository login test passed; Ruff, strict mypy, lock, generated contract/planning, backlog, clean-room, compile, build, Compose and Helm gates passed.
- Deviations from plan: shared URS-NFR-SECURITY-001 remains In Progress because EPIC-604/605 and the independent pre-GA penetration test remain open. No tenancy dependency was added; PostgreSQL RLS and typed AMESH contracts provide the required boundary.
- Next step when resuming: close and commit card `c4`, then select the next dependency-ready epic from the remaining requested frontend, compatibility, login, orchestration-control and HA/DR areas.

### 2026-08-21 (post-MVP roadmap session 1, EPIC-004 start)

- Did: closed EPIC-503 on card `c4` and committed it as `1b35594`; selected dependency-ready EPIC-004 on card `c5`; compared PyYAML source-mark patching, a new parser and `ruamel.yaml` round-trip parsing; accepted ADR-021 for a versioned Pydantic canonical IR, round-trip YAML source tree and Draft 2020-12 resource-schema registry.
- Deviations from plan: this epic adds `ruamel.yaml` and `jsonschema` because comment-preserving edits and standards-complete plugin schema validation are established library responsibilities.
- Next step when resuming: implement the editable document, source-range mapper, resource registry and versioned validation result before extending generated contracts.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-004 completion)

- Did: completed EPIC-004 with YAML 1.2/JSON parsing into `amesh.flow/v1`; comment-preserving programmatic edits; common, reference, cycle and installed-resource validation; source ranges and remediation hints; `x-` extension policy; deterministic semantic hashes; Draft 2020-12 resource schemas/editor metadata; generated contract artifacts; ADR-021 and the flow DSL guide. Linked URS-F-0029 through URS-F-0036 to evidence.
- Verification: 91 tests passed with real PostgreSQL at 80.29% branch coverage; generated flow/resource/OpenAPI contracts matched; a 5,003-line flow measured 0.598 seconds p95 over 10 uninstrumented runs; Ruff, strict mypy and focused API/DSL checks passed.
- Deviations from plan: shared URS-NFR-USABILITY-001 remains In Progress for EPIC-405 editor integration, and URS-NFR-MAINTAINABILITY-002 remains In Progress for EPIC-300/400/610. `ruamel.yaml`, `jsonschema` and the latter's type stubs were added through `uv` after the build-vs-buy review.
- Next step when resuming: close and commit card `c5`, then select dependency-ready EPIC-005 to complete the requested Pebble-compatible expression layer.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-005 start)

- Did: closed EPIC-004 on card `c5` and committed it as `0f6e2f2`; selected dependency-ready EPIC-005 on card `c6`; compared a JVM Pebble boundary, an unavailable maintained Python Pebble port and a versioned compatibility facade over the existing Jinja sandbox; accepted ADR-022 for the explicit `kestra-pebble/1.3.30-subset-1` adapter.
- Deviations from plan: no expression dependency was added. The existing Jinja native sandbox supplies the maintained parser/evaluator primitive; AMESH owns only the bounded compatibility, context and redaction contracts.
- Next step when resuming: implement the engine protocol, typed contexts, selected filters/functions, compile/runtime errors and resource limits before wiring the executor context.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-005 completion)

- Did: completed EPIC-005 with the storage-independent `ExpressionEngine`; typed execution contexts; versioned `kestra-pebble/1.3.30-subset-1` syntax, filters, functions and fixture corpus; immutable sandbox; separate compile/render failures; deterministic template, AST, context, collection, nesting, recursion, output and elapsed-time limits; and secret-aware previews, errors, representations and core logs. Linked URS-F-0037 through URS-F-0044 to evidence.
- Verification: 104 tests passed with real PostgreSQL at 80.05% branch coverage; the 12-case compatibility corpus and executor context integration passed; a representative render measured 0.2324 ms p95 over 1,000 warmed runs; Ruff, strict mypy, backlog, clean-room, compilation and generated-contract gates passed.
- Deviations from plan: no new expression dependency was needed. Compatibility remains explicitly bounded to the published subset; effectful Kestra functions stay with their owning capability epics.
- Next step when resuming: close and commit card `c6`, then select the next dependency-ready epic from the requested graphical frontend, orchestration control and HA/DR areas.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-404 start)

- Did: closed EPIC-005 as `43f095e`; briefly selected EPIC-400, then returned it to To-Do because its full resource surface depends on unfinished backfill, file, key-value and plugin owners and the user directed work to defer blockers and move forward; selected EPIC-404 on card `c8`. Researched the current React ecosystem and accepted ADR-023 for a Vite React SPA, React Router, TanStack Query, i18next, cmdk, AMESH-owned token CSS, Vitest and Playwright/axe.
- Design: established `frontend/DESIGN.md` with a graphite-control-room direction, offline bundled typography, high-contrast signal palette, 44 px controls, keyboard focus, dense operational data surfaces and desktop/tablet/phone layouts before writing components.
- Direct blocker fixed: fresh Docker Compose databases now apply migration 0010, which the completed trigger-context runtime requires.
- Next step when resuming: scaffold the isolated frontend workspace with exact locked packages, implement the shell and server-authoritative session capability endpoint, then test its loading, error, empty, responsive, keyboard, localization and offline states.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-404 completion)

- Did: completed EPIC-404 with a React/Vite control room; AMESH-owned graphite design system; dashboard, flow, execution and execution-detail views; reserved navigation for later product areas; server-authoritative capability rendering; tenant/namespace context; saved views; deep-link fallback; global live-resource command search; notifications; recovery states; bundled typography; English/Simplified Chinese locale and time-zone formatting; telemetry-off deployment policy; FastAPI static serving; and a Node-to-uv container build. Linked URS-F-0430 through URS-F-0437 to evidence and documented the browser/accessibility qualification boundary.
- Verification: 107 Python tests passed with four environment-gated skips against PostgreSQL; eight frontend unit tests passed at 100% isolated-unit coverage; five desktop/tablet browser acceptance cases passed with axe reporting no critical/serious findings and only the local app origin observed; ESLint, TypeScript/Vite, Ruff, strict mypy, uv lock, generated contracts/planning, backlog, clean-room, compilation, Compose, Docker image and diff gates passed.
- Deviations from plan: EPIC-400 remains To-Do because its full API surface depends on unfinished resource owners, but the existing versioned `/api/v1` flow/execution/authorization slice satisfied EPIC-404. Shared URS-NFR-USABILITY-004 and URS-NFR-PRIVACY-001 remain In Progress for their other owners and the pre-GA cross-browser/screen-reader matrix.
- Next step when resuming: close and commit card `c8`, then select the next dependency-ready epic from the remaining login, orchestration-control and HA/DR areas.

### 2026-08-22 (post-MVP roadmap session 1, EPIC-007 completion)

- Did: selected dependency-ready EPIC-007 after deferring the EPIC-403/EPIC-502 circular dependency; added immutable typed/versioned execution and task-run command, event, snapshot, transition and rejection contracts; pure lifecycle reducers; stable idempotency; replay and execution-v1 upcasting; PostgreSQL task history and rejection evidence; schema-v2 execution metadata; and same-transaction event-to-outbox triggers. Updated generated schemas, migration documentation, execution semantics and canonical requirement evidence.
- Verified: 118 Python/PostgreSQL tests pass with four environment-gated skips at 80.89% branch coverage; a fresh database applies all 11 migrations and exposes forced RLS plus both outbox triggers; 100 repeated replays are byte-equivalent; duplicate task results have one logical effect; stale execution/task transitions preserve state and record evidence; forced rollback leaves neither event nor outbox row. Ruff, strict mypy, uv lock, planning/contracts, backlog, clean-room, compile, Compose and diff gates pass.
- Deviations from plan: the live OpenRouter smoke remains environment-gated because `OPENROUTER_API_KEY` is absent; its checked-in default remains `openai/gpt-5.6-luna`. Helm was not rerun because the Helm executable is absent and EPIC-007 changes no chart template; the fresh migration and Compose configuration were verified directly. Shared reliability and maintainability NFRs remain In Progress for EPIC-008/009/100/103/108 and distributed failover qualification.
- Next step when resuming: close EPIC-007 and select the next dependency-ready backlog epic in the loops/subflows/backfill/recovery chain.

### 2026-08-22 (post-MVP requested-area completion, EPIC-403)

- Did: completed the last uncovered requested capability with one-time local administrator bootstrap, Argon2id local passwords, a provider-neutral authentication registry, opaque PostgreSQL-authoritative browser sessions, production secure-cookie/CSRF policy, expiry and rotation, lockout/rate limiting, logout/global revocation/password rotation, secret-free audit/metrics, RBAC-protected multi-user administration, federated-only policy and the graphical local-account login gate. Applied migration 0027 to the development database and linked URS-F-0422 through URS-F-0429 to evidence.
- Verification: four authentication API/CLI tests passed against disposable PostgreSQL databases; the compiled React UI completed a real headless-browser login through a live AMESH server; frontend lint, ten unit tests, production build and five applicable Playwright shell cases passed; all non-deferred backend tests passed on a clean 27-migration database; Ruff formatting/lint, strict mypy, uv lock, generated OpenAPI/planning, backlog validation, Compose, Helm production/development profiles and the production Docker image passed.
- Deviations from plan: the EPIC-403/EPIC-502 cycle was corrected so EPIC-403 owns local login plus the provider boundary and EPIC-502 owns concrete federation. The unrelated EPIC-104 deadline timing assertion and metric-registration test-order dependency were not changed and remain recorded on cards `c15` and `c29`.
- Next step when resuming: select a new explicitly requested backlog item; the five areas in this execution goal are complete within their published qualification boundaries.

### 2026-08-22 (local deployment handoff)

- Did: deployed the committed API and compiled control-room frontend through Docker Compose without replacing the PostgreSQL or MinIO volumes; bootstrapped the first local administrator; and fixed the runtime wheel package-data declaration that had omitted `amesh/web` from `site-packages`.
- Verification: Compose reported healthy API/PostgreSQL services; `/ready` reported 27 of 27 migrations; `/` returned the compiled HTML; API and headless-Chromium login reached the expected administrator session and Dashboard; HttpOnly session, CSRF and logout checks passed.
- Next step when resuming: leave the local stack running for user testing at `http://localhost:8000`.

### 2026-08-22 (deployed Flows view repair)

- Did: reproduced the reported recovery view as an HTTP 500 from `/api/v1/flows`; traced it to one valid persisted flow whose concurrent transaction timestamps differed by 536 microseconds; normalized the timestamp at the PostgreSQL adapter boundary without weakening the domain metadata invariant; added a regression test; and rebuilt the running API image.
- Verification: the regression failed on the original Pydantic validation error and passed after the fix; Ruff and strict mypy passed; a fresh Chromium session against Compose signed in, rendered Dashboard metrics, opened the 863-flow catalog, and observed HTTP 200 from both flow and execution queries with no recovery view.
- Next step when resuming: leave the repaired stack running for user testing at `http://localhost:8000`.

### 2026-08-22 (50-epic local completion program start)

- Did: classified all 70 open canonical epics by full Definition of Done; excluded 20 with non-local qualification gates; registered the remaining 50 as authoritative Agent Hotel cards `c37`–`c86`; and selected dependency-free EPIC-000 as the first milestone.
- Deviations from plan: the prior five-area scope is superseded by the product owner's explicit 50-epic local completion goal. External prerequisite epics remain open; only their smallest locally testable contract may be implemented when it directly blocks a selected epic.
- Next step when resuming: complete EPIC-000 requirements URS-F-0001 through URS-F-0007, verify its clean-room governance gates and evidence, deploy any affected service, update the canonical backlog and move card `c37` to Done.
