# EPIC-838 re-verification baseline

- **Source:** GitHub issue #42
- **Verified revision:** `5bfd9110aecbc4a27ad9c6f17f8aaf867949db19`
- **Recorded:** 2026-09-03
- **Execution boundary:** child issues #43 through #53

## Disposition rule

A moved file is not a resolved responsibility. A finding is accepted as landed only when the cited
behavior or boundary exists on the verified revision. A valid residual is assigned to exactly one
qualified child unless two milestones own distinct parts. Claims with no demonstrated failure are
explicitly deferred rather than represented as fixed.

## Original 16-finding scorecard

| # | Re-verified disposition | Accepted action |
|---:|---|---|
| 1 | Partial: one repository family uses RLS; remaining administrative families rely on a bypass role. | #47 qualifies fail-closed role and tenant visibility; #50 adopts shared repository responsibilities. |
| 2 | Relocated: the API implementation remains a 16,687-line mixed responsibility with import-time construction. | #48 extracts bootstrap, dependencies and feature routers with an import-side-effect regression. |
| 3 | Partial: the worker crash guard landed, but the executor remains a God class. | Retain the guard; #49 owns measured executor decomposition. |
| 4 | Partial: domain imports are lighter, but the replacement execution trace hook has no production caller. | Retain the import probes; #45 owns trace propagation or consistent removal. |
| 5 | Not addressed behaviorally: repository support types exist but almost no repository adopts them. | #50 owns distinct persistence responsibilities and support-service adoption. |
| 6 | Resolved: shared application composition is used by API, worker and CLI supported paths. | Accept as landed; #48 must preserve its public compatibility surfaces. |
| 7 | Resolved: all production adapters declare ports and application/domain annotations no longer name PostgreSQL implementations. | Accept as landed; #50 must preserve port behavior while splitting implementations. |
| 8 | Relocated: specification literals moved, but schemas still self-compare and `agent.llm` remains drifted. | #51 makes handler contracts authoritative and restores DSL parity. |
| 9 | Partial: a pure session reducer exists, but callers choose targets and progress append replays history. | #45 owns typed computed transitions and incremental progress state. |
| 10 | Partial: one managed-process boundary landed; the default Pi command now starts from an invalid cwd. | Retain the shared boundary; #44 fixes the demonstrated startup regression. Unproven helper-duplication and blocking-call cleanup is deferred. |
| 11 | Partial: some feature packages landed, but package/name/test structure drift remains. | #52 owns the measured repository and test structure boundary. |
| 12 | Partial: five cited failure/loop rows landed; accepted recovery, deferral, search and cancellation regressions remain. | #44 owns the demonstrated regressions. Unchanged low-risk plugin-hook/check/catalog rows without a new failure are deferred. |
| 13 | Resolved only structurally: escape hatches are gone, but the coverage pass skips PostgreSQL and its floor was lowered. | #46 makes the Docker gate complete and honest. |
| 14 | Partial: shared disposable PostgreSQL fixtures landed, but many supported tests still hand-roll setup and assertions weakened. | #46 restores gate assertions; #52 owns remaining supported-path fixture disposition. |
| 15 | Partial: root Compose/progress clutter improved, while settings, docs navigation and screenshots remain unreconciled. | #52 owns settings, Compose, documentation and asset structure. |
| 16 | Partial: generated OpenAPI types and split clients landed, but compatibility wrappers and calls bypass generated paths. | #53 makes generated schema/path types authoritative and groups the frontend by feature. |

## Atomic regression and gate claims

The issue contains 22 independently testable bullets. Their frozen disposition is:

| Claim | Verdict | Owner / evidence boundary |
|---|---|---|
| Default Pi worker command starts in a temporary cwd | Valid | #44: spawn the repository-relative default through the managed-process path. |
| Transient recovery errors terminally fail executions | Valid | #44: DB/OS transients propagate without `fail_execution`. |
| Permanent recovery reasons persist unredacted text | Valid | #44: secret-bearing failure text is absent from durable/API evidence. |
| Cache abandonment can turn deferral into failure | Valid | #44: abandonment failure still durably defers with a resume token. |
| Terminal Kubernetes log 503 can fail a successful Job | Valid | #44: a succeeded Job remains successful with incomplete transient logs. |
| Missing tenant-admin grant silently runs under the login role | Valid | #47: transaction entry fails closed and rolling-upgrade behavior is explicit. |
| Lifecycle version conflict returns HTTP 500 | Valid | #44: a stale policy write returns 409. |
| Search failure recording aborts the remaining tenant cycle | Valid | #44: a later tenant is still processed. |
| Cancellation during timeout cleanup becomes timeout | Valid | #44: outer cancellation remains `CancelledError`. |
| Semantic debug booleans/lists become `[REDACTED]` | Valid | #45: declared shapes survive while actual secrets remain redacted. |
| Execution trace attachment has no production caller | Valid | #45: production submission persists current trace context or removes the claim consistently. |
| Progress append replays/scans complete history | Valid | #45: bounded query/work regression proves incremental append. |
| Determinism repeatedly serializes complete subtrees | Valid | #45: accepted workload scaling is linear. |
| Simulator and executor consume different task views | Valid | #45 and #51: datetime and explicit-null parity use the handler view. |
| Lazy DSL package attributes regressed | Partly valid | #51: preserve the supported validator attribute; no unsupported eager-import expansion. |
| Worker runner defaults duplicate the shared factory | Partly valid | #52: reconcile the supported composition path; no current missing setting is claimed. |
| `amesh.app` replaces `sys.modules` under module execution | Partly valid but non-failing | Explicitly deferred; #48 must preserve and test the supported `python -m amesh.app` entry point. |
| Four structural-field sets can drift | Partly valid | #51: all consumers import one authoritative set. |
| HTTP readiness assertion was weakened | Partly valid | #46: assert status and degraded dependency payload. |
| Histogram assertion can pass without an observation | Valid | #46: require the observed `_count` sample. |
| Frontend `Omit` keys and narrowed fields evade drift checks | Valid | #53: validate every key and preserve generated optionality/nullability. |
| Migration isolation test removes an unused environment variable | Stale | No code change: `migration_directory()` reads `AMESH_MIGRATIONS_PATH` on the verified revision. |

## Ordered qualification

1. #43 — canonical active/archive catalog and this frozen disposition.
2. #44 — release-blocking runtime regressions.
3. #45 — state, trace, redaction and determinism regressions.
4. #46 — complete PostgreSQL Docker gate and restored evidence assertions.
5. #47 — fail-closed PostgreSQL role boundaries.
6. #48 — API bootstrap, dependencies and routers.
7. #49 — executor responsibilities.
8. #50 — PostgreSQL persistence responsibilities and support adoption.
9. #51 — handler-authoritative DSL.
10. #52 — repository, settings, Compose, test and documentation structure.
11. #53 — generated frontend path authority and feature grouping.

Each child requires focused regressions plus the complete Docker-local gate before merge. No child
may add GitHub Actions, fix an unrelated finding, or use relocation alone as completion evidence.
