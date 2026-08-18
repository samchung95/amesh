# Changelog

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
