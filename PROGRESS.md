# Progress Log

## Current state

- What works: the locally qualified MVP foundation is deployed through migration 59. Guided creation supports a traceable first workflow run; EPIC-312 supplies bounded Luna/OpenRouter and MCP primitives; EPIC-807 supplies immutable capability envelopes; EPIC-808 runs recoverable bounded sessions; and EPIC-809 adds isolated exact-key memory, deterministic-first evaluations, optional pinned judges and ordinary human release gates in the same execution trace.
- What's in flight: `c100`, `c106`, `c107` and EPIC-809 on `c108` are complete. EPIC-806 remains To-Do on `c109` and must be selected next.
- Known broken / TODO: production determinism qualification remains on `c101`; multi-agent topology, typed hand-offs and explainable routing remain on `c109`. Existing deferred baseline and external-qualification cards remain unchanged.
- How to run/test: frontend checks run from `frontend/` with `npm test`, `npm run build` and `npm run test:e2e`; backend checks use `uv run --extra runtime --extra dev pytest`. The local Compose product is served at `http://localhost:8000`.

## Session log

### 2026-08-25 (EPIC-809 complete)

- Did: completed tenant-, namespace- and agent-revision-isolated memory with bounded private/shared scopes, retention, redaction, size limits, metadata-only discovery and audited deletion; exact immutable evaluation fixtures, assertions, weighted rubrics and optional pinned judges; deterministic-first acceptance; direct human release authority; side-effect-free preview; durable memory/evaluation/release events; guided Agents controls; readable trace annotations; migration 0059; ADR-054; API/how-to documentation; an example; and regenerated API/resource/SDK projections.
- Verification: 14 affected Python tests, three real-PostgreSQL integration tests and seven frontend assertions pass; Ruff, strict mypy over 233 source files, the production build and diff gate pass. Rebuilt Compose is ready at 59/59. OpenRouter Luna cold execution `01a03728-0034-7730-82f9-fce320a344fc` and recall execution `01a03728-fc13-70cc-b592-df2fabca6c88` both completed successfully with exact evaluation revision 1, judge/model/cost/token provenance, ordered session events and private-memory write/recall/replacement evidence.
- Deviations from plan: the distributed Compose executor needed the same agent resource/session/memory repositories as the monolithic worker, and its five-second recovery grace raced healthy bounded model calls; the direct deployment blockers were corrected and regression-tested. A live judge rejection at 0.68 against the 0.70 gate was retained as adversarial evidence rather than weakening the gate. Shared agent NFRs remain In Progress for EPIC-806 multi-agent qualification.
- Next step when resuming: close and publish `c108`, then select `c109` / EPIC-806 for multi-agent topology, typed hand-offs and explainable routing.

### 2026-08-25 (EPIC-809 start)

- Did: closed and published EPIC-808 as `15a5e46`; selected `c108`; reconciled agent resources, session checkpoints, flow tests, simulation and durable approvals; and accepted ADR-054 for explicit tenant-RLS memory scopes plus exact evaluation revisions, deterministic-first gates, optional pinned judge evidence and ordinary `core.approval` release authority.
- Deviations from plan: no vector database, separate promotion engine or new dependency is required. Memory recall is exact-key and treated as untrusted user data; semantic retrieval remains outside this epic.
- Next step when resuming: implement migration 0059, immutable evaluation resources, the memory journal and session evaluation/release integration before extending the authorized API and trace.

### 2026-08-25 (EPIC-808 complete)

- Did: completed the recoverable `agent.session` task against one exact capability pin; added migration 0058 with tenant-isolated checkpoints and idempotent session events; mediated stable model and MCP operation identities; enforced cumulative turns, loops, tools, tokens, cost and duration; required direct approval for high-impact tools or sensitive egress; gated final results through the pinned schema plus deterministic business assertions; projected agent events into ordinary execution evidence; exposed an authorized session API and readable trace annotations; and regenerated the API, SDK, backlog and traceability projections.
- Verification: 12 affected-path Python tests plus two real-PostgreSQL migration/repository tests pass; Ruff lint and strict mypy over all 229 source files pass; 26 focused frontend assertions and the production build pass; deterministic contract/planning/SDK checks match 2,355 generated files; Python, TypeScript, Java and containerized Go SDK checks pass. Rebuilt Compose reports migration 58/58 ready. Live OpenRouter execution `01a036f3-eda7-77d1-838d-a46727e3aa8e` used `openai/gpt-5.6-luna`, passed the pinned output schema and one business assertion, and persisted a successful one-turn session with 379 tokens and `$0.0002178` cost.
- Deviations from plan: OpenRouter's strict schema subset required tool arguments to cross the provider boundary as a JSON string while final output uses the pinned object schema; AMESH decodes and validates both before dispatch or acceptance. The repository-wide Ruff format baseline still reports 75 pre-existing files outside this epic; they were not changed. Memory, learned evaluation, human release promotion and multi-agent topology remain with EPIC-809/806.
- Next step when resuming: close and publish `c107`, then select `c108` / EPIC-809 and implement isolated memory plus evaluation/release gates.

### 2026-08-25 (EPIC-808 start)

- Did: selected `c107`; reconciled the existing execution, capability-pin, model/MCP invocation and human-approval boundaries; compared graph expansion, an external agent runtime and a recoverable ordinary task; and accepted ADR-053 for a PostgreSQL checkpoint/event journal with stable per-operation invocation keys.
- Deviations from plan: no dependency or second execution engine is required. Memory, learned evaluation, release promotion and multi-agent topology remain with EPIC-809/806.
- Next step when resuming: implement migration 0058, the session domain/repository, and the bounded handler before wiring execution-trace visibility and deployed acceptance.

### 2026-08-25 (EPIC-807 complete)

- Did: completed versioned prompt, declarative skill, provider-neutral model-policy and agent resources; exact prompt/skill/model/MCP-tool references; deterministic instruction composition; typed input/output schemas; isolated memory declarations; delegated capability, secret, network and filesystem boundaries; hard budget/turn/tool/loop/recursion/concurrency limits; evaluation policy; atomic content-addressed subject pins; revision comparison; provider migration diagnostics; guided Agents UI; REST/CLI operations; MCP tool catalog plus authenticated `list_agents` and `inspect_agent`; migration 0057; ADR-052; API/how-to documentation; and regenerated four-language SDKs.
- Verification: 19 focused domain, PostgreSQL repository, API, MCP, CLI and generated-contract tests pass; the PostgreSQL test proves restart-idempotent pins, conflicting-envelope rejection, tenant isolation and secret-free audit evidence. Ruff passes and strict mypy passes all 225 source files. Two focused frontend unit assertions, changed-file ESLint, the production build and the focused Chromium agent-composition acceptance pass. Deterministic SDK generation matches 2,335 files; Python/TypeScript/Java/Go clients compile or test successfully. Rebuilt Compose is healthy at migration 57/57, and live HTTP acceptance created Luna policy/prompt/agent revision 1 and returned the same persisted pin on retry for envelope `sha256:668c8e99814b8444bd95ca16ba97bbe72f4d84568bf648c5c6b62a4a77609f2b`.
- Deviations from plan: the generated Go tree, including pre-existing files, is reported by `gofmt`; its containerized `go test ./...` gate passes and generator formatting was not changed under this epic. Durable model turns, tool mediation and checkpoint resume intentionally remain EPIC-808 consumers of the EPIC-807 pin. Model output is explicitly nondeterministic.
- Next step when resuming: close and publish `c106`, select `c107` / EPIC-808, and implement bounded durable single-agent sessions against the exact capability pin.

### 2026-08-25 (EPIC-807 start)

- Did: closed and published guided-creation card `c100` as `8aae515`; selected `c106` / EPIC-807; compared workflow embedding, per-kind tables and a typed shared revision ledger; and accepted ADR-052 for exact immutable resource references plus one transactionally persisted capability-envelope pin.
- Deviations from plan: none. This epic defines and resolves agents but does not run an autonomous loop, execute skill code or persist ambient credentials.
- Next step when resuming: implement typed prompt, skill, model-policy, agent and envelope contracts, then add migration 0057 and the transactional resolver repository.

### 2026-08-25 (guided workflow creation complete)

- Did: completed board card `c100` with six intent starters; a numbered guided authoring rail; namespace, task/plugin, trigger, upstream-output, runner, model and secret selectors; one round-trip YAML source shared with visual/code editing; inline validation and policy explanations; dynamic-bound simulation; revision-pinned isolated smoke tests; permission states; and a save-to-run path that lands on the simple execution trace. Accepted ADR-051 and exported responsive visual evidence.
- Verification: six focused model/editor tests and the production frontend build pass; the full suite passes all 62 functional unit assertions while retaining the pre-existing `c94` branch/function coverage-threshold exit; all 23 applicable Playwright tests pass with 27 intentional project/environment skips. The first-run browser acceptance creates and runs a two-step workflow without opening YAML and reports zero critical/serious axe findings. Rebuilt Compose is ready at migration 56, and an authenticated live test saved, policy-checked, simulated with two tasks and zero unknowns, isolated-tested with zero production executions, launched and opened the persisted trace in 7.2 seconds.
- Deviations from plan: no dependency, backend format or parallel execution path was added. The existing unrelated ESLint findings in `ExecutionEvidenceTimeline.tsx` and deferred global coverage threshold remain on their existing owners and were not changed.
- Next step when resuming: close `c100`, commit and publish it, then select `c106` / EPIC-807.

### 2026-08-25 (EPIC-312 complete)

- Did: completed and documented provider-neutral chat, embedding, structured-output and proposed tool-call tasks; explicit model budgets/data policy; a redacted invocation journal; tenant-scoped MCP discovery, immutable schema pins and allowlists; impact/approval gates; authenticated connection APIs; and authorization-checked read-only AMESH MCP tools. Updated URS-F-0383 through URS-F-0390 and regenerated the canonical epic projections.
- Verification: Ruff, strict mypy, lock/diff/compilation gates and 26 affected-path tests passed; the separate live OpenRouter test passed against `openai/gpt-5.6-luna`. Distributed Compose is healthy at migration 56, anonymous `/mcp` returns 401, and a live structured Luna flow completed with validated downstream output, usage, cost, redacted provenance and a durable successful invocation row.
- Deviations from plan: none. The deployed smoke required the existing namespace `team: platform` label and OpenAI-compatible structured schemas to declare a type alongside enum; the checked-in example now reflects both requirements. No durable agent-session, memory or multi-agent scope was absorbed.
- Next step when resuming: select `c106` / EPIC-807 before implementing versioned agent definitions and capability envelopes.

### 2026-08-25 (EPIC-312 connection and MCP-server checkpoint)

- Did: added authenticated discovery and immutable connection-revision REST APIs; resolved credentials only through tenant-scoped secret bindings; verified live tool schemas before save and call; added an audience-bound workload-token verifier; and exposed read-only `list_workflows` and `inspect_execution` MCP tools with per-call authorization and no execution payload/state mutation.
- Verification: API denial/outage/tenant tests, protocol-level anonymous/authenticated MCP tests, schema-drift/dedup/restart/redaction task tests, a fresh migration-56 PostgreSQL repository test and generated-contract tests pass. A live bounded OpenRouter call passed against `openai/gpt-5.6-luna` with token/cost budget evidence.
- Next step when resuming: finish the how-to/reference docs and backlog evidence, run the complete affected-path gates, rebuild Compose and close `c105` only if the deployed smoke tests pass.

### 2026-08-25 (EPIC-312 bounded task checkpoint)

- Did: added the four provider-neutral model operations, explicit provider/budget/data-handling contracts, Draft 2020-12 output/tool validation, Luna/OpenRouter adapter, tenant-scoped MCP connection revisions, live schema pin checks, tool impact controls, redacted invocation provenance and duplicate/restart handling; registered the new task types in the resource catalog and immediate/recovery executors.
- Verification: focused domain, task, DSL and worker tests pass; Ruff and strict mypy pass for the changed task/runtime paths. The unrelated 5,000-line DSL p95 gate remains deferred on board card `c89` and was not changed.
- Next step when resuming: expose authenticated connection discovery/version APIs and mount the authorization-checked read-only AMESH MCP surface.

### 2026-08-25 (EPIC-312 start)

- Did: selected board card `c105`; verified the existing agent handler tests and live `/ready` endpoint; audited the current task, secret-resolution, resource-catalog, executor and MCP seams; recorded the bounded primitive boundary in `ARCHITECTURE.md`; and accepted ADR-050 to reuse locked HTTPX, jsonschema and MCP v2 libraries behind AMESH contracts without adding a dependency.
- Deviations from plan: none. This epic stops at bounded one-shot model/MCP primitives and an authenticated read-only AMESH MCP surface; autonomous sessions, memory and multi-agent routing remain out of scope.
- Next step when resuming: wire provider-neutral model operations and governed MCP calls to the invocation journal, then add connection APIs and the authenticated AMESH MCP server.

### 2026-08-25 (bounded-agent epic decomposition)

- Did: refined EPIC-312 into the bounded provider/model/MCP prerequisite; split the prior broad EPIC-806 requirements into EPIC-807 versioned agent definitions, EPIC-808 durable bounded single-agent sessions, EPIC-809 memory/evaluation/release gates and a narrowed EPIC-806 multi-agent topology layer; recorded ADR-049; regenerated canonical backlog, roadmap, URS, compatibility, traceability and GitHub-issue projections; and created board cards `c105`–`c109` with staged Definitions of Done.
- Verification: `uv run --extra runtime --extra dev python scripts/validate_backlog.py` reports 106 epics, 837 functional requirements, 63 non-functional requirements and 1,000 exact traceability links. The 900-requirement corpus is unchanged; URS-F-0806–0819 and agent NFRs were reassigned across the new durable boundaries.
- Deviations from plan: no runtime, dependency, UI, service or deployment change was made. The roadmap deliberately completes single-agent safety before multi-agent coordination and keeps all agent state inside the existing execution reducer.
- Next step when resuming: select `c105` and complete EPIC-312 before starting EPIC-807.

### 2026-08-24 (Sprint UX-01 complete)

- Did: completed cards `c102`, `c97`, `c98` and `c99` under sprint card `c104`; recorded ADR-048 and the input inventory; replaced constrained text fields with authorized selectors; made Mission Control the operational home; added prioritized Running now/Needs attention views; made the redacted ordered trace the execution default; preserved topology, Gantt, logs, data, history, analytics and YAML; and exported before/after/live visual evidence.
- Verification: 12 focused selector/Mission/trace model tests pass; the production frontend build passes; all 22 applicable Playwright tests pass with 24 intentional project skips; 19 populated after-state captures, five non-happy states and the authenticated live Mission Control/trace report zero critical/serious axe findings, console errors or failed API requests. The live Compose gate proves one running, 94 failed-recently and 105 completed-recently executions, and the rebuilt API is healthy at `http://localhost:8000`.
- Deviations from plan: no dependency or backend service was added. The 58-test complete frontend unit suite passes functionally but the command retains its pre-existing nonzero exit because global branch/function coverage is below 75%, already tracked on deferred card `c94`. Guided creation (`c100`) and production determinism qualification (`c101`) remain separate follow-ons.
- Next step when resuming: start guided workflow creation on `c100`; Sprint UX-01 itself has no remaining work.

### 2026-08-22 (50-epic local completion program, EPIC-220 completion)

- Did: completed EPIC-220 with literal argv and explicit single-string shell modes; working directory, bounded environment and standard input; POSIX UID and typed CPU/memory/file/open-file/process limits; live ordered severity-mapped stdout/stderr; POSIX process-group and Windows process-tree escalation; portable process-tree CPU/peak-memory sampling; signal evidence; and local-runner enablement that defaults off in multi-tenant mode. Linked URS-F-0258 through URS-F-0264 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 40 migrations; 339 tests existed, cards `c15`/`c29` were explicitly deselected, and the remaining 337 produced 329 passes, eight environment/platform skips and zero failures. Ruff and strict mypy passed for 128 source files; focused adapter/API/DSL/generated-contract, backlog, lock, compilation, Compose and diff gates passed. Linux container qualification applied UID 100/open-file limit 32, reported CPU/peak memory, captured SIGTERM 15 and removed a timed-out descendant. The rebuilt services are healthy at 40/40, and deployed execution `01a02a20-5039-71a2-b8f4-282a4cd5499e` completed shell/stdin execution with the enforced open-file limit, stderr and resource metrics.
- Deviations from plan: build-versus-buy selected cross-platform `psutil` 7.2.2 plus its development stubs, added with `uv`; no LLM call was required. One full-suite assertion caught an unnecessary rename of stable escalation labels, so the labels were restored without changing process-group behavior and the clean rerun passed. Deferred cards `c15`, `c29`, `c87` and `c88` remain untouched.
- Next step when resuming: close and commit card `c47`, then select EPIC-221 on card `c48` for the Docker and OCI task runner.

### 2026-08-22 (50-epic local completion program, EPIC-209 completion)

- Did: completed EPIC-209 with a versioned runner-neutral request/result contract; advertised local and Kubernetes capabilities; typed local/Kubernetes extensions; scoped credential, network and security policies; namespace/worker-group runner selection; pre-dispatch compatibility validation; normalized logs, metrics and diagnostics; cancellation/timeout escalation; and idempotent orphan reconciliation. Added the authorized runner-capability API and linked URS-F-0250 through URS-F-0257 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 40 migrations and the isolated complete backend suite collected 327 tests: 321 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff and strict mypy passed for 128 source files; focused runner/API tests, generated contracts/planning, backlog, clean-room, REUSE 6.2.0, uv lock, compilation, Compose and diff gates passed. The rebuilt API/executor/scheduler are healthy at 40/40. Live capability discovery returned both runners, and deployed execution `01a02a08-f238-70f1-972d-59f4a2f5cd53` proved task-level local selection over a Kubernetes execution fallback and completed with `RUNNER_LIVE_OK:66`.
- Deviations from plan: no dependency or LLM call was required. The first live flow exposed that the generated resource catalog did not yet admit the new task-runner fields; the catalog registry was minimally extended and the live rerun passed. Shared security/portability NFRs remain In Progress for their other owning epics, and deferred cards `c15`, `c29`, `c87` and `c88` remain untouched.
- Next step when resuming: close and commit card `c46`, then select EPIC-220 on card `c47` for the local process task runner.

### 2026-08-22 (50-epic local completion program, EPIC-208 completion)

- Did: completed EPIC-208 with unique disposable local directories per task attempt; post-expression internal input resolution with streamed checksum verification; atomic path/glob/JSON-manifest output collection; traversal, drive, symlink and cross-root confinement; a sequential `core.workingDirectory` flowable; guaranteed local cleanup with configured failure-diagnostic retention; total workspace quotas; logical path and ordered transformation lineage; and authorized execution-file list/download APIs. Linked URS-F-0242 through URS-F-0249 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 40 migrations and the isolated complete backend suite collected 320 tests: 312 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff and strict mypy passed for 127 source files; generated API/DSL/planning, backlog, clean-room, lock and diff gates passed. Real MinIO/API acceptance exercised namespace-file materialization, shared child execution, lineage listing and payload download. The rebuilt API/executor/scheduler are healthy at 40/40, and deployed execution `01a029e5-3d9b-75ca-a603-d664617e00a7` completed all three task runs successfully and streamed `result.txt` through the new API.
- Deviations from plan: no dependency or LLM call was required. Docker/OCI and Kubernetes workspace transfer remain with their already selected EPIC-221/222 runner owners; those modes reject this surface explicitly until implemented. The existing deferred cards `c15`, `c29`, `c87` and `c88` remain untouched.
- Next step when resuming: close and commit card `c45`, then select EPIC-209 on card `c46`.

### 2026-08-22 (50-epic local completion program, EPIC-207 completion)

- Did: completed EPIC-207 with inherited and versioned namespace files backed by object storage; child override and tombstone semantics; typed, expiring and compare-and-set key-value data; monotonic value-free change evidence; provider-reference-only secret bindings resolved at task runtime; independent list/read/write/delete/use authorization; value-free audits; checksum-protected import/export bundles; and matching API, CLI and control-room surfaces. Linked URS-F-0234 through URS-F-0241 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 39 migrations and the isolated complete backend suite collected 313 tests: 305 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff and strict mypy passed for 126 source files; 12 frontend unit tests, all eight applicable Playwright cases and the production build passed. The rebuilt API/executor/scheduler are healthy at 39/39. Live acceptance uploaded a file, stored a typed value and secret provider reference, exported a plaintext-free bundle and completed execution `01a029c2-458f-787f-a865-982c4fac3c07` with the value resolved and secret output redacted.
- Deviations from plan: no dependency or LLM call was required. A broad first suite run against the active Compose database was invalid because deployed services consumed shared state; the guarded disposable-database rerun passed without product changes. The existing seven frontend lint findings remain deferred on `c88`.
- Next step when resuming: close and commit card `c44`, then select EPIC-208 on card `c45`.

### 2026-08-22 (50-epic local completion program, EPIC-206 completion)

- Did: completed EPIC-206 with tenant-scoped namespace metadata; protected user/system labels on flows, executions, task runs, assets and backfills; exact plugin-type defaults; recursive forced/non-forced precedence; policy require/deny/normalize controls; immutable revision provenance; JSONB label indexes and dotted filters; authorized metadata APIs; and control-room label/effective-origin panels. Linked URS-F-0227 through URS-F-0233 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 38 migrations and the complete suite passed with 292 tests, six environment/profile skips and cards `c15`/`c29` explicitly deselected. Ruff and strict mypy passed for 123 source files; frontend 11-test coverage and production build passed. The rebuilt API/executor/scheduler are healthy at 38/38. Live acceptance configured parent namespace defaults, applied `metadata-demo`, exposed flow/default provenance and completed execution `01a0299b-bf76-7893-8366-f2920cc5b614` with protected execution/task labels.
- Deviations from plan: no dependency or LLM call was required. The first full run exposed a directly caused cache-key regression because unique system labels were included; cache derivation now uses user labels only and both restart/concurrency cache scenarios pass. The seven existing frontend lint errors remain deferred on `c88`.
- Next step when resuming: close and commit card `c43`, then select EPIC-207 on card `c44` for namespace files, key-value data and secrets.

### 2026-08-22 (50-epic local completion program, EPIC-205 completion)

- Did: completed EPIC-205 with one canonical DSL/API/UI input schema for string, integer/number, boolean, datetime, duration, enum, array, object, file and secret values; required/default/display/prefill/validation metadata; validation before runnable persistence across API, manual, trigger and subflow launches; object-storage file staging; typed terminal outputs; and schema-driven public redaction. Linked URS-F-0219 through URS-F-0226 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 37 migrations and the complete suite passed with 288 tests, six environment/profile skips and cards `c15`/`c29` explicitly deselected. Ruff and strict mypy passed for 122 source files; frontend 11-test coverage and production build passed. The rebuilt API/executor/scheduler are healthy at 37/37. Live API acceptance rejected plaintext secrets without creating rows, completed a valid file-backed execution and redacted sensitive values; headless Chromium rendered five generated input controls and the Run action.
- Deviations from plan: no dependency or LLM call was required. Legacy flows without declarations retain bounded ad-hoc input compatibility, and legacy `INT` normalizes to `integer`. Shared cross-product secret non-disclosure remains In Progress under URS-NFR-SECURITY-003; the existing `c87`/`c88` deferred items remain untouched.
- Next step when resuming: close and commit card `c42`, then select EPIC-206 on card `c43` for labels, metadata and plugin defaults.

### 2026-08-22 (50-epic local completion program, EPIC-205 start)

- Did: selected EPIC-205 on card `c42` and accepted a single canonical data-contract boundary over the existing Pydantic DSL, JSON Schema generator, expression engine and object-storage port. The boundary will own typed validation/defaults, form/API schema derivation, file staging, terminal flow-output rendering and schema-driven public redaction for API, manual, trigger and subflow launches.
- Deviations from plan: no dependency or LLM call is required. Secret inputs use durable `secret://` references so plaintext secret material never enters execution metadata or events; the existing static `variables` context remains separate from execution inputs and the mutable key-value service.
- Next step when resuming: implement the typed DSL/data-contract service and migration 0037, then wire every execution launch path and the control-room run form before fresh-database qualification.

### 2026-08-22 (50-epic local completion program, EPIC-204 completion)

- Did: completed EPIC-204 with durable MAIN/ERROR/FINALLY/AFTER_EXECUTION task phases; local and flow error ownership; bounded state/category/task/expression selectors; attempt-zero nonmatches; restart-safe lifecycle evidence; success, failure and cancellation cleanup; primary-failure preservation with separate cleanup failures; post-terminal context; recursive-handler rejection; and graph/control-room lifecycle metadata. Linked URS-F-0211 through URS-F-0218 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 36 migrations and the complete suite collected 291 tests: 283 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff, strict mypy, generated contracts/planning, backlog, clean-room, REUSE 6.2.0, uv lock, compilation, Compose and diff gates passed. Frontend unit tests and production build passed; unrelated lint debt was deferred to `c88`. The rebuilt API/executor/scheduler are healthy and `/ready` reports migration 36/36.
- Deviations from plan: no package or LLM call was required. Shared-database suite contamination from an earlier pre-migration run was isolated by rerunning on a disposable clean database. Fresh Compose initialization mounts and unrelated frontend payload stringification were recorded on `c87`/`c88` and left unchanged.
- Next step when resuming: close and commit card `c41`, then select EPIC-205 on card `c42` for typed inputs, outputs and variables.

### 2026-08-22 (50-epic local completion program, EPIC-204 start)

- Did: closed and committed EPIC-202 as `4b378f6`, selected EPIC-204 on card `c41`, and accepted ADR-034. Public behavior research confirmed that errors are failure-specific and may be flow/local-flowable scoped, finally runs cleanup before ordinary terminalization, and after-execution work observes an already terminal execution without replacing its state.
- Deviations from plan: no dependency is required. Lifecycle tasks will use ordinary durable task runs with phase metadata and structured execution lifecycle evidence; existing task handlers cover notification, compensation/subflow and diagnostic-artifact outputs. Nested lifecycle handlers will be rejected to bound recursion.
- Next step when resuming: extend the DSL/compiler and migration 0036, then implement restartable error/finally/after-execution reduction and graph visibility.

### 2026-08-22 (50-epic local completion program, EPIC-202 completion)

- Did: completed EPIC-202 with Kestra-shaped `core.if`/`core.switch` flowables; ordered else-if and predicate cases; explicit `FAIL`, `FALSE` and `FALLBACK` expression policies; restart-stable redacted decision evidence; attempt-zero non-selected skips; conditional retries; static duplicate/unreachable validation; additive migration 0035; ADR-033; example and operator documentation. Linked URS-F-0196 through URS-F-0202 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 35 migrations and the complete suite collected 288 tests: 280 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff passed for 639 files, strict mypy passed for 120 source files, and generated contracts/planning, backlog, clean-room, REUSE 6.2.0, lock, Compose and diff gates passed. The rebuilt Compose services are healthy at migration 35/35; live HTTP acceptance selected the expected else-if and predicate branches while non-selected descendants remained at attempt zero.
- Deviations from plan: no package or LLM call was required. Exact switch cases retain the Kestra-compatible `value`/`cases` surface; AMESH extensions add ordered `elseIf`/`predicateCases` and the explicit error policies. Error-hook execution and flow-output materialization remain with their queued EPIC-204/205 lifecycle owners.
- Next step when resuming: close and commit card `c40`, move EPIC-204 on card `c41` to Doing and implement errors, finally and after-execution hooks against URS-F-0211 through URS-F-0218.

### 2026-08-22 (50-epic local completion program, EPIC-006 completion)

- Did: completed EPIC-006 with immutable semantic revision allocation that preserves explicit forward revisions and auto-advances conflicting changes; authorized history, unified/RFC 6902-compatible diff, lifecycle and restore APIs; actor/source/commit/environment/deployment provenance; pinned resource-catalog resolution; execution foreign-key pinning; reference-aware deletion; and tenant-isolated audit/event/outbox evidence through migrations 0033–0034. Linked URS-F-0045 through URS-F-0051 to automated evidence.
- Verification: a fresh PostgreSQL database applied all 34 migrations and the complete suite collected 282 tests: 274 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Ruff passed for 637 files, strict mypy passed for 120 source files, and generated contract/planning, backlog, clean-room, REUSE 6.2.0, lock, Compose and diff gates passed. The rebuilt Compose API/executor/scheduler are healthy at migration 34/34; live acceptance created revisions 100/101, returned two diff operations, disabled revision 101 and restored revision 100.
- Deviations from plan: no package or LLM call was required. Compatibility tests established that an unused explicit forward revision must be retained, while changed content colliding with existing history receives `max + 1`. Revision-event outbox records now follow explicit flow purge through migration 0034.
- Next step when resuming: EPIC-202 is selected on card `c40`; implement conditional branching and switch semantics against URS-F-0196 through URS-F-0202.

### 2026-08-22 (50-epic local completion program, EPIC-003 start)

- Did: selected EPIC-003 on card `c38`; retained pinned Pydantic Settings and PyYAML after build-versus-buy review; accepted ADR-031; implemented ordered file/environment/CLI loading, `secret://` references, secret-free validation errors and structured-log redaction, explicit reloadable metadata, atomic reload rejection, renamed-setting migration and the namespace-over-tenant-over-instance feature-flag contract. Added additive migration 0032 and the PostgreSQL repository boundary.
- Verification: ten focused configuration and feature-flag domain tests pass; Ruff and strict mypy pass for the new core modules.
- Deviations from plan: no new dependency was added. The OpenFeature provider/evaluation shape informed the decision evidence, but its SDK would not supply AMESH's PostgreSQL scope, authorization or audit semantics.
- Next step when resuming: qualify migration 0032 and tenant RLS, then expose authorized configuration, diagnostic, reload and flag APIs.

### 2026-08-22 (50-epic local completion program, EPIC-003 completion)

- Did: completed EPIC-003 with typed source snapshots and provenance; YAML/JSON, environment, CLI and secret-reference precedence; safe deprecation migration; production configuration gates; active-secret API/log/diagnostic redaction; atomic reload; authorized configuration APIs; and audited versioned PostgreSQL instance/tenant/namespace feature flags through migration 0032. Linked URS-F-0022 through URS-F-0028 to evidence.
- Verification: 281 tests collected; 273 passed, six environment/profile tests skipped and cards `c15`/`c29` were explicitly deselected. Seventeen focused tests, Ruff, strict mypy, generated contracts/planning, migration, backlog and clean-room gates passed. The rebuilt Compose API/executor/scheduler are healthy at migration 32/32, and deployed HTTP acceptance passed configuration, reload, scoped evaluation and diagnostic-bundle checks.
- Deviations from plan: the first full run's two failures were direct migration-version expectations; updating the owning assertion and applying migration 0032 to the deployed database resolved both. No LLM call or new package was required.
- Next step when resuming: close and commit card `c38`, then select EPIC-006 on card `c39` for flow revisions, change history and promotion.

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
