# AMESH MVP scope — two-month vertical slice

**Status:** Proposed re-scope, pending product-owner ratification
**Authored:** 2026-08-19
**Window:** 8 working weeks from kickoff
**Relationship to the roadmap:** a calendar-boxed vertical slice through M0–M2, not a replacement for the dependency-based roadmap. The 103-epic backlog remains canonical; nothing here deletes scope.

## 1. MVP thesis

Prove the one claim the whole product depends on, with the smallest surface that a real user can touch:

> **A YAML-defined workflow of process, container and agent tasks runs durably on Kubernetes: the control plane and workers survive crashes without losing or duplicating work.**

The MVP is Python on the existing foundation. It extends the checked-in validator, reducer, PostgreSQL schema and port contracts into a running engine. It deliberately does **not** attempt Kestra parity, the Java core, or enterprise controls — those are sequenced after the engine exists (section 6).

## 2. In scope

| Area | MVP content | Builds on |
|---|---|---|
| Flow DSL | Existing subset plus `retry` (count/backoff), `timeout`, task inputs/outputs, `runIf` evaluation | `src/amesh/dsl`, EPIC-004 |
| Expressions | Minimal AMESH-native templating (`{{ inputs.x }}`, `{{ outputs.task.y }}`, `{{ vars.z }}`), Jinja2-backed, namespaced as native — explicitly **not** Pebble-compatible | EPIC-005 (native half only) |
| Durable transport | `DurableTransport` implemented on PostgreSQL: `FOR UPDATE SKIP LOCKED` claims, expiring leases, fencing tokens, inbox/outbox, `LISTEN/NOTIFY` wake-ups | `migrations/0001_foundation.sql`, EPIC-009 |
| Executor | Command handler + reducer extended with per-task-run state and attempts; epoch/fencing guards on event append; crash recovery reconciler | `src/amesh/domain`, EPIC-100, EPIC-108 |
| Scheduler | Cron triggers with restart-safe occurrence dedup; manual + webhook execution triggers | EPIC-102, EPIC-103 |
| Runners | **Local process** (dev loop) and **Kubernetes Jobs** (production path): image/cmd/env/resources, log capture, cancellation, fenced completion | EPIC-220, EPIC-222 |
| Task types (in-process pack) | `core.log`, `core.return`, `core.shell`, `core.http`, `agent.llm` (OpenAI-compatible chat), `agent.mcp` (MCP tool call) | EPIC-306, EPIC-312 (seed) |
| API + CLI | REST: validate/apply/list flows; create/get/list executions; logs; webhook trigger. CLI mirrors it | EPIC-400, EPIC-402 (subset) |
| Deployment | Runs **on** Kubernetes: minimal Helm chart (server, worker, migration job, external PostgreSQL), verified on kind/k3d; Docker Compose remains the dev profile | EPIC-606 (subset) |
| Observability | Structured JSON logs, Prometheus `/metrics`, execution/task states queryable via API | EPIC-111, EPIC-607 (subset) |
| Auth | Single static admin token; single tenant (`default`, already seeded) | EPIC-403 (stopgap) |

Scale target for the MVP demo: ~1,000–5,000 executions/day on a single-node control plane. Profile M (100k/day) is a post-MVP qualification, not an MVP claim.

### The Kubernetes decision

Kubernetes is in the MVP twice — AMESH **runs on** Kubernetes (Helm chart) and **runs tasks as** Kubernetes Jobs. To pay for this inside 8 weeks, the standalone Docker/OCI runner (EPIC-221) is deferred: the K8s Job runner covers container execution and the local process runner covers the laptop loop. Docker-runner work would duplicate ~70% of the Job runner's contract surface for no MVP-visible capability.

A side benefit: K8s Jobs give the MVP pod-level isolation for user task code, which softens the deferral of the isolated plugin runtime (EPIC-303).

## 3. Explicitly deferred — the deferral register

Deferred means **parked, not abandoned**. Every row names the epic(s) where the work resumes and the trigger that un-parks it. The backlog entries themselves are untouched.

| Deferral | Epic(s) | Resumes when |
|---|---|---|
| Java 25 production core | ADR-010, EPIC-001 | Post-MVP checkpoint (section 6) re-affirms or amends ADR-010 with MVP evidence in hand |
| Kestra YAML/Pebble/REST/CLI parity + importer | EPIC-005 (compat half), EPIC-704, parity charter | Engine semantics stable; parity work restarts against the pinned 1.3.30 baseline |
| Docker/OCI standalone runner | EPIC-221 | First post-MVP runner iteration; contract already proven by the K8s runner |
| Isolated language-neutral plugin runtime + SDKs | EPIC-300–305 | Task-type surface stabilises; in-process pack becomes the "trusted" tier (EPIC-302) |
| Multi-tenancy, RBAC, SSO/SAML/SCIM, audit | EPIC-500–506 | First deployment with >1 team of users; schema already carries `tenant_id` everywhere so no data migration is created by waiting |
| Web UI (authoring, topology, Gantt, dashboards) | EPIC-404–411 | Post-MVP; API-first MVP keeps the OpenAPI contract as the UI's foundation |
| HA / distributed control plane, backup/restore drills | EPIC-601, EPIC-609, EPIC-611 | After single-node durability evidence exists (MVP week 8 soak is the input) |
| Subflows, loops/foreach, backfill/replay, caches, SLA | EPIC-104 (partial), 106, 107, 109, 110, 203 | Next engine iteration after MVP; retries/timeouts/cancel land in MVP |
| Object-storage artifact pipeline | EPIC-010, EPIC-605 | Logs/outputs outgrow PostgreSQL rows (bounded in MVP); MinIO stays in the dev stack |
| Search/analytics projections, dashboards | EPIC-408, 409, 604 | UI wave |
| Compliance evidence, migration tooling, marketplace, agent-mesh differentiators beyond `agent.*` tasks | EPIC-504/514+, 700s, 800s | Per the existing roadmap ordering |
| Agent merge-quorum enforcement | EPIC-011 | Team scales beyond a single accountable maintainer |

## 4. Cons of this re-scope — accepted knowingly

1. **The two-implementation debt grows.** Every line of Python engine code widens the eventual Java port, and the MVP may produce evidence that overturns ADR-010 entirely (a working Python engine is a strong argument for staying). That is a feature of the experiment, but it must be resolved explicitly at the checkpoint, not by drift.
2. **Compatibility debt.** MVP flows use AMESH-native expressions and DSL fields. If/when Pebble/Kestra parity lands, MVP-era flows may need mechanical migration, and the pinned Kestra 1.3.30 baseline ages in the meantime. Mitigation: expressions are namespaced as native from day one, so parity can be added beside them rather than under them.
3. **Weaker isolation than the target architecture.** In-process task types run inside the worker (mitigated for container tasks by pod isolation). Untrusted third-party plugin code is out of bounds until EPIC-303.
4. **Single tenant, static token.** The MVP must not be exposed to untrusted users. The API auth surface is a stopgap and will be replaced, not extended.
5. **No HA.** A control-plane restart is a brief outage (durability is preserved; availability SLOs are explicitly not claimed).
6. **Planning-corpus drift.** The 900 requirements stay `Proposed` and are not re-edited during the MVP; some epic assumptions (Java-first sequencing) go temporarily stale. A post-MVP reconciliation pass updates statuses and re-sequences waves (section 6).
7. **Performance ceiling.** The Python engine will not reach Profile M; MVP claims stop at demo scale.
8. **Some MVP code is scaffolding.** The expression engine, auth stopgap and log storage are expected to be replaced. They are cheap on purpose.
9. **K8s-in-MVP has a real price.** Roughly +1–1.5 weeks versus a Docker-only MVP: kind/k3d test infrastructure, Job lifecycle edge cases, and Helm packaging. Paid for by deferring EPIC-221 and keeping the UI out of scope.

## 5. Eight-week plan

Each week ends with an objectively checkable exit. Weeks 6–8 carry the schedule buffer.

| Week | Deliverable | Exit check |
|---|---|---|
| 1 | PostgreSQL transport adapter (claim/lease/fence/ack, inbox/outbox) | Kill -9 during claim/ack in tests → no lost or double-effective work |
| 2 | Executor with per-task-run state; DAG execution in-process | `examples/parallel-dag.yaml` runs end-to-end; restart mid-run resumes correctly |
| 3 | Worker protocol + local process runner; retry/timeout/cancel | Worker crash → task re-dispatched; stale worker's late result rejected by fencing |
| 4 | Cron scheduler + expressions + `runIf` | Cron flow fires exactly once per occurrence across restarts; outputs flow between tasks |
| 5 | Kubernetes Job runner | Same flow runs tasks as Jobs on kind; deleting the worker pod mid-task reconciles |
| 6 | `agent.llm` + `agent.mcp` + REST/CLI surface | Demo agent flow (LLM → shell → HTTP) triggered via API runs on K8s |
| 7 | Helm chart + metrics + structured logs | `helm install` on a fresh kind cluster → demo flow green, `/metrics` scraped |
| 8 | Hardening, soak, docs, tag | 24h soak with induced pod kills: zero lost/duplicated executions; quickstart reproduced on a clean machine; `v0.2.0-mvp` tagged |

## 6. Path back to the full roadmap

The MVP is a slice of M0–M2, not a fork. On completion:

1. **Reconciliation pass:** update `requirements/urs.json` statuses for requirements the MVP evidences, regenerate planning artifacts, and record intentional deviations.
2. **ADR-010 checkpoint:** with a working engine and measured load, re-affirm the Java core (MVP becomes the executable specification it was always meant to be, now with far richer fixtures) or amend it (Python stays production; Java effort is re-allocated). Either outcome is legitimate; deciding it with evidence is the point.
3. **Resume the deferral register** in roadmap order: runners (EPIC-221), plugin isolation (EPIC-300s), governance (EPIC-500s), UI (EPIC-400s), HA and qualification (EPIC-600s), parity and migration (EPIC-700s), differentiators (EPIC-800s).

The milestone exit gates in `docs/product/roadmap.md` remain the evidence bar for any compatibility, availability or compliance **claim**. The MVP makes no such claims — it makes the engine real.
