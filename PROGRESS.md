# Progress Log

## Current state

- What works: the tagged `v0.2.0-mvp` foundation plus EPIC-002, EPIC-500, EPIC-501 and EPIC-503 are implemented; PostgreSQL RLS now enforces explicit tenant execution and transport boundaries, with tenant lifecycle/policy APIs and tenant-aware workers.
- What's in flight: EPIC-503 has passed all gates and is ready for card closure/commit; the next requested dependency-ready epic will be selected immediately afterward.
- Known broken / TODO: the five requested post-MVP product areas remain open. The uninterrupted 86,400-second qualification remains under EPIC-611 and still gates production-readiness claims.
- How to run/test: use `uv run --extra runtime --extra dev pytest`; set `AMESH_TEST_DATABASE_URL` for PostgreSQL integration tests and `OPENROUTER_API_KEY` for live LLM tests.

## Session log

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
