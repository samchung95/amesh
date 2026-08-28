# Changelog

## Unreleased

- Replaced executable GitHub Actions with a Docker-local verification and packaging surface for
  backend, frontend, Pi harness, contracts, review regressions, Compose profiles, production-image
  probing and local repository/SDK archives, including a PowerShell entry point.
- Completed the local EPIC-810–825 program: truthful scheduling health, client-neutral orchestration
  and evidence, provider/tool extensibility, hardened local execution, restart/shadow/promotion gates,
  Pi-backed bounded sessions, guided agent authoring and inspection, capability discovery, document
  pipelines, harness portability and deterministic tool bindings.
- Resolved the current merge-path review blockers by preserving one MCP invocation identity across
  retries and charging tenant API quota only after authorization succeeds. The nine environment- or
  optional-capability findings remain explicitly tracked in `c130`–`c132`.
- Resolved MVP review findings 1–8: fresh split-role dispatch, recovered subflows/approvals/isolated plugins, encrypted retryable webhook input, route- and principal-safe frontend state, and bounded Docker output. Kubernetes/Helm/operator findings 9–11 remain explicitly deferred.
- Completed EPIC-002 with canonical resource keys, UUIDv7 runtime identities, shared metadata/lifecycle contracts, deterministic hashes and ETags, persisted flow metadata, conditional REST updates, and the `0003_canonical_resource_metadata.sql` migration.
- Completed EPIC-500 with PostgreSQL-backed principals, groups, roles, permissions and scoped bindings; deny-overrides namespace inheritance; revocation-safe decision caching; administrator explanations; built-in roles and last-admin protection; server-side REST/CLI/non-human policy contracts; audit evidence; and migration `0004_authorization.sql`.

## 0.2.0-mvp — 2026-08-21

- Added the PostgreSQL durable transport adapter with idempotent outbox publication, consumer-inbox deduplication, expiring leases, retries, fencing and lane-specific `LISTEN/NOTIFY` wake-ups; process-crash tests prove redelivery without duplicate-effective work.
- Added a PostgreSQL-backed MVP DAG executor with persisted execution events, task runs and attempts plus epoch-fenced terminal event append; a fresh executor instance resumes `parallel-dag.yaml` without rerunning completed work.
- Added the runner port and local-process adapter with argv execution, captured results, persisted retry scheduling, timeout/cancellation escalation and stale-attempt result fencing.
- Added deployed-worker cron polling with timezone-aware calculation and PostgreSQL execution idempotency across concurrent/restarted schedulers, plus sandboxed AMESH-native Jinja rendering for inputs, outputs, variables and `runIf`.
- Added the Kubernetes Job runner on the shared runner contract with deterministic Job reconciliation, resource/deadline mapping, pod log/exit capture, cancellation cleanup and a real kind pod-deletion recovery test.
- Added structured `core.log`, native `core.return`, HTTP, OpenRouter/OpenAI-compatible LLM and official MCP task handlers; authenticated flow/execution/webhook/log REST endpoints; matching CLI commands including execution listing; and a live API-triggered Luna → Kubernetes shell → HTTP demonstration.
- Added a uv-locked non-root container and minimal Helm chart with external-PostgreSQL migration hook, server and recovery-worker roles, task-Job RBAC, health probes, external Secret references, structured JSON logs and Prometheus `/metrics`; verified on a fresh kind cluster.
- Added opt-in live OpenRouter LLM contract testing with `openai/gpt-5.6-luna` as the default model.
- Confirmed Python 3.12 asyncio as the production durable control plane (ADR-016), superseding the Java 25 selection before any Java implementation began; updated README, decision register, baseline and status documents accordingly.
- Added the two-month MVP scope (`docs/product/mvp-scope.md`): a durable engine slice with local-process and Kubernetes Job runners, cron scheduling, native expressions, agent task types and a minimal Helm chart, plus an explicit deferral register and accepted cons.
- Initialized the git repository with a full baseline commit.
- Fixed the flow DSL silently dropping snake_case `depends_on`/`run_if` spellings; conflicting dual spellings are now rejected; regression tests added.
- Cleaned all ruff lint and formatting findings and fixed pre-existing `mypy --strict` errors in the flow validator.
- Renamed the protobuf packages from `openorchestrator.*` to `amesh.*`.
- Pinned `fastapi`, `pydantic` and `pydantic-settings` exactly to keep the byte-stable generated-contract test deterministic.
- Made generated planning and contract artifacts byte-identical on Windows (`newline="\n"`), so CI drift gates cannot be tripped by the platform.
- Completed the owner-amended W8 release gate: 270 unique single-attempt executions survived 270 task-pod, 27 server-pod and 13 worker-pod deletions with zero lost or duplicated persisted executions; the clean-cluster quickstart and all release gates passed. The remaining uninterrupted 24-hour qualification is explicitly deferred to EPIC-611.

## 0.1.0-dev.1 — 2026-08-16

- Accepted Java 25 as the production language for the modular durable control plane.
- Retained the Python validator and reducer as an independent executable specification until Java differential parity.
- Closed all foundational product-owner decisions and added an implementation kickoff sequence for M0.
- Updated ADR-001 and ADR-010, architecture status, URS metadata and repository baseline accordingly.

## 0.1.0-dev — 2026-08-15

- Named the project **AMESH — Agent Mesh** and adopted a strict clean-room implementation model.
- Confirmed `AGPL-3.0-only` as the licence grant and documented why stricter field-of-use restrictions would conflict with the fully open-source objective.
- Pinned the first compatibility target to Kestra 1.3.30.
- Accepted full compatibility scope for YAML, Pebble expressions, REST API, CLI, execution semantics and documented import/export formats.
- Selected React/TypeScript, PostgreSQL-only authoritative storage and internal transport, isolated language-neutral plugins, and local/Docker/Kubernetes runners.
- Selected on-premises Kubernetes/Helm as the first production and release-qualification topology, including offline installation requirements.
- Confirmed the first integration pack: HTTP/REST, webhooks, Git, GitHub, PostgreSQL, S3/MinIO, Docker/OCI, Kubernetes, OpenAI-compatible model APIs and MCP.
- Accepted profile M: 100,000 executions/day, 1,000 active task runs, 50 task starts/second and 10 million retained execution records.
- Accepted 99.9% monthly control-plane availability and the minimal v1 recovery gate of RPO <= 48 hours and RTO <= 8 hours.
- Selected full side-by-side migration of resources, identity/governance, execution history, logs, artifacts and audit evidence.
- Added SOC 2 and ISO/IEC 27001 readiness requirements without claiming certification.
- Selected independent agent quorum for ordinary merges and named human approval for high-risk changes and stable releases.
- Evaluated Java 25, Go, Kotlin and Python; Java remained pending product-owner acceptance at this snapshot.
- Added 103 implementation epics across nine milestone waves.
- Expanded the baseline to 837 functional and 63 non-functional requirements with 992 traceability links.
- Added first-class agent-mesh runtime and AI-native engineering governance epics.
- Added target architecture, ADRs, threat model, compatibility design, PostgreSQL transport, on-premises Kubernetes, migration, compliance and licence documentation.
- Added a runnable Python flow validator and deterministic execution-reducer specification.
- Added provisional PostgreSQL queue, worker, plugin, Compose and GitHub automation contracts.
- Added deterministic regeneration for URS, traceability, parity, roadmap and GitHub issue artifacts.
