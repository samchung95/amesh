# Project: AMESH — roadmap completion

## Goal

Complete the 50 currently open epics whose implementation and directly relevant verification can run on the local development environment. Execute one dependency-ready epic at a time, keep the Compose product deployable at epic boundaries, and close an epic only when its acceptance criteria and mapped requirements have verified evidence in the canonical backlog.

## Out of scope

External-cloud, external-SaaS, hosted-release, independent-certification, multi-region and long-duration qualification gates are deferred for EPIC-001, 011, 223, 308–312, 506, 606, 611–612, 700, 705–706, 801 and 803–806. Their smallest locally implementable contract may be added only when it directly blocks one of the 50 selected epics. Opportunistic refactors, adjacent defects, cards `c15`/`c29` and broader production claims remain excluded.

## Open questions

None currently. Expensive framework or identity-provider choices will be surfaced before their implementation epic; reversible implementation details follow existing ADRs and repository conventions.

## Decisions log

- 2026-08-19 — Keep Kubernetes in the MVP twice (runs on K8s via Helm; runs tasks as K8s Jobs); defer the standalone Docker runner (EPIC-221) to pay for it — user requirement; Docker runner duplicates ~70% of the Job runner surface for no MVP-visible capability.
- 2026-08-19 — **Product owner confirmed Python as the production core** ("keep the current architecture — slow but robust"); ADR-016 supersedes ADR-010, the Java port is cancelled, and the post-MVP checkpoint becomes a performance review. Robustness claims rest on the PostgreSQL/fencing/pure-reducer design; throughput claims require measurement.
- 2026-08-19 — Expressions are AMESH-native (Jinja2-backed, namespaced), not Pebble-compatible; parity remains a deferred, pinned workstream.
- 2026-08-19 — Planning corpus (900 requirements) is frozen during the MVP; reconciliation pass updates statuses post-MVP.
- 2026-08-19 — Pinned fastapi/pydantic/pydantic-settings exactly because the generated-contracts test asserts byte-stable output.
- 2026-08-21 — Use OpenRouter for live LLM integration tests with `openai/gpt-5.6-luna` as the base model and an environment-overridable model list — user requirement; the core model contract remains provider-neutral.
- 2026-08-21 — Use Jinja2's sandboxed native environment for the explicitly accepted AMESH-native expression subset and croniter for cron calculation; keep occurrence durability in PostgreSQL execution idempotency rather than introducing a second scheduler datastore.
- 2026-08-21 — Use the official Kubernetes Python client 36 async API for the Job runner; deterministic attempt-derived Job names provide reconciliation while PostgreSQL remains authoritative for fenced completion.
- 2026-08-21 — Product owner deferred the remaining uninterrupted 24-hour W8 soak and authorized release progression after cycle 270. The verified partial run is accepted for `v0.2.0-mvp`; the full 86,400-second qualification remains open in EPIC-611 and gates broader availability, scale and production-readiness claims.
- 2026-08-21 — Use the Agent Hotel daemon board as the live execution tracker and keep `backlog/epics.json` as the canonical product-requirement source; `PLAN.md` records scope and decisions only.
- 2026-08-21 — Execute one dependency-ready epic at a time. Direct prerequisite epics enter scope only when the canonical dependency graph makes them necessary for one of the five requested product areas.
- 2026-08-21 — Start with EPIC-002 because it has no dependencies and its identity/resource contracts directly unlock RBAC, multi-tenancy and the REST/UI chain.
- 2026-08-22 — Break the EPIC-403/EPIC-502 planning cycle: EPIC-403 owns local login, durable browser sessions and the provider-neutral authentication boundary; EPIC-502 consumes that boundary for concrete OIDC, SAML, LDAP and SCIM adapters. Federated providers do not block the requested local multi-user login.
- 2026-08-22 — Complete EPIC-400 against the authoritative v0.2 resource profile and preserve `/api/v1`; add opt-in `Prefer: respond-async` execution launch plus common contract behavior. Per the product owner's prior “defer and move forward” direction, file/KV/secret/plugin lifecycle APIs stay with EPIC-207/506/300/301 instead of receiving placeholder persistence in the API layer.
- 2026-08-22 — Register the 50 locally closeable open epics as Agent Hotel cards `c37`–`c86` and execute them dependency-first. Defer the 20 external qualification epics and unrelated failures; implement only a minimum local prerequisite contract when a selected epic cannot otherwise be completed or verified.
