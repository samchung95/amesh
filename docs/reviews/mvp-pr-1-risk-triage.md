# MVP PR #1 review risk triage

Date: 2026-08-27
Pull request: [samchung95/amesh#1](https://github.com/samchung95/amesh/pull/1)

## Current-head review gate

The latest current-head review contains eleven P1 findings. Product-owner direction places findings
1–8 in local MVP review gate `c134` and explicitly defers findings 9–11 to `c130`.

| # | Finding | Current decision |
| --- | --- | --- |
| 1 | Recovery grace delays fresh automated executions | Implemented: work without a fresh `RUNNING` task is immediately eligible; fresh running work remains grace-protected and fenced. |
| 2 | Split-role recovery omits `core.subflow` | Implemented with the existing durable subflow handler and pending-child coordinator. |
| 3 | Split-role recovery omits human-task persistence | Implemented by composing the PostgreSQL human-task repository into the executor role. |
| 4 | Split-role recovery omits isolated plugins | Implemented with the existing isolated runtime and explicit shutdown lifecycle. |
| 5 | Redacted webhook input cannot reproduce a durable retry | Implemented as redacted occurrence/execution projections plus a tenant/occurrence-bound encrypted recoverable payload. |
| 6 | Reused flow-editor routes retain the previous flow | Implemented by resetting route/principal-scoped editor state before the new document renders. |
| 7 | React Query data survives authentication identity changes | Implemented by clearing protected client state on logout and every session/token identity transition. |
| 8 | Docker log capture ignores `outputLimitBytes` | Implemented with bounded stdout/stderr/log capture, container stop, failed status and preserved secret redaction. |
| 9 | Kubernetes log capture ignores `outputLimitBytes` | Deferred: requires the Kubernetes runner qualification environment. |
| 10 | Helm does not supply `WEBHOOK_SIGNING_KEY` | Deferred: requires the Helm/cluster secret contract and qualification environment. |
| 11 | Kubernetes operator file paths can escape the declared namespace | Deferred: requires operator hardening and cluster-backed tenant-boundary qualification. |

Findings 9–11 are not represented as passing local gates. Their resumption criteria live on board
card `c130`.

## Earlier review corpus and decision rule

The review contains one top-level review, nine inline threads and twelve Codex review comments. The
comments contain 133 finding occurrences; repeated scans report the same issue on successive
commits, so this register tracks deduplicated defects rather than inflating the count.

A finding is fixed in this release only when it is both high impact and on the Docker-local,
authenticated external-agent execution path being qualified now. High-impact findings for an
inactive backend or capability remain visible as P1 deferred work. Obsolete, low-probability and UI
edge cases are P2. This is a release-boundary decision, not a claim that deferred findings are false.

## P0 — implemented for this release

| Finding | Why it is on the active path | Resolution |
| --- | --- | --- |
| Fresh Compose stops at migration 0032 | A clean local deployment cannot become ready or expose current agent APIs | Replaced static PostgreSQL init mounts with a manifest-aware one-shot migration service awaited by every runtime role. Review `3838962175`. |
| Login limiter trusts `User-Agent` | Internet-shaped input can bypass authentication throttling | The source bucket is derived from the peer address only. Duplicate comments include `5398686318`, `5403233285`, `5404122346`, `5405333489`, `5406874929`, `5407120038`, `5426781943`. |
| Execution reads omit namespace authorization | A client could bypass a namespace deny or be denied a namespace-only grant | Detail, logs, graph, evidence and artifact reads authorize the persisted execution namespace. Comments `5404122346`, `5406010902`, `5407120038`. |
| Flow validation buffers an unbounded unauthenticated body | The public validation route can exhaust server memory | Content length is rejected early and streamed input is bounded to 2 MiB. Comments `5403233285`, `5426781943`. |
| Failed runner output can persist secrets | Agent and task failures are ordinary external-client paths | Runner streams and failure persistence use the same secret-aware redaction, including split chunks and compound secret keys. Comments `5393213160`, `5404122346`, `5404462936`, `5406010902`, `5414021499`. |
| Local process isolation/output is not fail-closed | The supported local runner can retain descendants, groups or unbounded output | Bounded capture, process-group cleanup and POSIX privilege-policy enforcement are covered by the local-runner focused patch. Comments `5398686318`, `5403233285`, `5404803287`, `5405333489`, `5414021499`. |
| Local attempt is reserved only after process creation | Concurrent delivery of one attempt can start duplicate processes and external effects before the loser is fenced | The runner now reserves the attempt under its lock before process creation and releases the reservation on creation failure or cancellation. A deterministic concurrent-dispatch regression proves the duplicate never reaches `_create_process`. Comment `5406874929`. |
| Governed MCP approval/retry boundary can repeat or self-approve effects | Client-owned agent tools use this neutral AMESH path | Legacy destination validation, direct approval provenance and retry-stable invocation identity are covered by the governed-MCP focused patch. Comments `5404462936`, `5406010902`. |

## P1 — high impact but outside the enabled local qualification path

These are deferred, not dismissed. Enablement of the named capability must first pull its item into a
focused security/reliability epic.

| Capability | Deduplicated findings | Why deferred from this release |
| --- | --- | --- |
| Docker task runner | `RESTRICTED` networking uses the default network; workspace restore can be buffered without a bound; image-digest fallback can select a mismatched repository digest | Docker output/log bounds are resolved in current-head finding 8; these remaining Docker behaviors are outside this review gate. Comments `5398686318`, `5403233285`, `5404122346`, `5404462936`, `5404803287`, `5406010902`, `5406874929`, `5414021499`, `5407120038`, `5426781943`. |
| Kubernetes task runner | NetworkPolicy is created after the Job and removed first; credentials enter Job/Pod specs; API retry can run forever; output capture is unbounded | Kubernetes is not part of the local Docker DoD. Current-head finding 9 remains explicitly deferred. Comments `5393213160`, `5405333489`, `5406010902`, `5406874929`, `5426781943`, `5407120038`. |
| HTTP task egress | Cross-origin redirects may retain credentials; one-time DNS validation may permit rebinding | Both inline threads (`3838962177`, `3838962178`) are outdated and require current-head reproduction before a patch. The first Vibe flow uses no HTTP task. |
| Expression secrets | String transforms can lose secret taint | The current client flow passes only frozen non-secret domain input. Comment `5406010902`. |
| Webhook occurrence identity | Headerless events can collide | Protected sensitive retry/replay is resolved in current-head finding 5; collision semantics remain deferred. Comments `5404122346`, `5414021499`, `5404462936`. |
| Task cache | Resolved key/value content and object checksums are missing from cache identity | The client flow does not enable task caching. Comment `5407120038`. |
| Local artifacts/object store | `local://` is rejected; bytes/metadata publication is non-atomic; deletion can remove referenced versions | The qualified distributed profile uses S3-compatible storage. Comments `5393213160`, `5404462936`, `5404122346`, `5404803287`, `5406874929`, `5426781943`. |
| Per-tenant storage encryption | `TenantPolicy.encryption_key_ref` is ignored and the object store receives only the global key identifier | Per-tenant storage/KMS qualification is outside the current client flow. Comment `5398686318`. |
| Tenant storage and transfer | Writes do not reserve tenant quota; transfer bundles omit bytes | Tenant export/import and quota qualification are not part of the client run. Comments `5398686318`, `5403233285`, `5405333489`, `5406010902`, `5404803287`. |
| Recovery and backup | Recovery scans a fixed execution page; object inventory is not snapshot-coordinated; exported LSN can be later than the snapshot | Restart/idempotency remains qualified for the existing bounded profile, but backup/restore and large-retention recovery need their own fault environment. Comments `5403233285`, `5414021499`. |
| Audit concurrency | Concurrent tenant inserts can choose the same audit-chain head | The review supplies a credible race, but it needs a PostgreSQL concurrency migration and qualification outside this client slice. Comment `5405333489`. |
| Production plugin trust | A repository-known signing key can be trusted; ZIP expansion is unbounded | No third-party plugin package is installed for the first client flow. Comments `5404803287`, `5405333489`, `5414021499`, `5426781943`. |
| Federation redirect | A backslash in `returnTo` may normalize to an external origin | Federation is disabled in the local profile. Comments `5404803287`, `5405333489`. |
| SMTP notifications | STARTTLS can proceed without verifying the mail server certificate | SMTP is disabled in the qualified local agent path. Inline thread `3838962181`. |
| Runner selection | Fallback runner choice is not persisted through restart | The client pins the local runner and configures no fallback. Comment `5404803287`. |
| Inline scripts | Inline source always uses stdin although Docker/Kubernetes reject stdin | The client flow contains no script task. Comments `5404803287`, `5407120038`. |
| Human approval | Assignment can change between the pre-check and action lock | No human task is used by the first client flow. Comment `5406874929`. |
| Execution idempotency admission | Existing keys are resolved after admission; conflicting reuse is not rejected | The client adapter uses a stable key and same frozen payload. Adversarial conflicting-reuse semantics need repository-focused work. Comments `5405333489`, `5404462936`. |

## P2 — deferred compatibility, cloud and edge findings

| Area | Findings |
| --- | --- |
| Object lifecycle/cloud storage | GCS holds are not cleared; retention/legal-hold metadata is not copied during migration; suspended tenants are absent from recovery inventory; partial tenant imports remain active; blocked prefixes can starve garbage collection; local lifecycle metadata can be overwritten. |
| Network/webhook operations | GCS/webhook clients ignore proxy/CA/mTLS/no-proxy; delivery leases can be shorter than request timeout; stale claims can exceed `maxAttempts`; delete-after-crash not-found handling may not be idempotent (`3838962183`, outdated). |
| Authentication/API semantics | Lock expiry extends on rejected attempts; synchronous failed launch returns 500; tenant policy deletion omits tenant context; SCIM ETags do not enforce `If-Match`. |
| Scheduler/data staging | Fractional interval timestamps are truncated; shared-input markers are written only after the batch. |
| Terraform/Kubernetes packaging | Flow destroy lacks flow-level retirement; provider responses cap at 8 MiB; SCIM uses the wrong token class; unsupported CRD delete policies can retain finalizers (`3838962184`, outdated); Helm lacks the webhook signing key. |
| Frontend | Evidence can remain when navigating execution IDs (`3838962187`). Auth-scoped query caches and flow-editor route reuse are resolved in current-head findings 6–7. |
| Minor API edge | Unicode artifact filenames can fail `Content-Disposition`. Comment `5426781943`. |
| Superseded CI comments | Runtime-extra installation (`3838962171`) and release ordering (`3838962176`) are moot because executable GitHub Actions workflows and automatic GitHub releases were removed. |

## Deferred acceptance rule

A deferred item moves back to P0/P1 implementation only when its capability is enabled for a release
or a focused reproduction proves it affects the supported path. Its acceptance criterion must name a
deterministic regression test and the environment needed to exercise it; a repeated automated review
comment alone is not completion evidence.
