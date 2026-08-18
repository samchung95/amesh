# Implementation status

AMESH currently contains an architecture-locked, implementation-ready planning baseline plus a small executable specification. It does **not** yet implement full workflow orchestration or claim Kestra compatibility.

## Implemented foundation

- Python package and CLI named `amesh`.
- Pydantic models for a deliberately small canonical flow subset.
- YAML/JSON validation for identifiers, duplicate task IDs, sibling dependencies and DAG cycles.
- Deterministic semantic hashing for the supported flow subset.
- Immutable execution-state reducer with duplicate-event idempotency, legal-transition enforcement and restart epochs.
- Foundation REST endpoints for health, flow validation and reducer demonstration.
- Port contracts for durable transport, object storage, task runners and isolated plugin invocation.
- Provisional PostgreSQL schema for resources, execution state, events, inbox/outbox, task attempts, workers and fenced leases.
- Provisional worker and isolated-plugin Protocol Buffer contracts.
- PostgreSQL and MinIO Docker Compose development services.
- Generated OpenAPI and JSON Schema contracts.
- Deterministic URS, traceability, parity, roadmap and GitHub-issue regeneration.
- Backlog validation and clean-room lexical checks.

## Decision and specification baseline

- Product name: AMESH — Agent Mesh.
- Strict clean-room implementation.
- Confirmed `AGPL-3.0-only` licence direction.
- Full pinned compatibility target across YAML, Pebble, REST, CLI, execution behavior and import/export.
- PostgreSQL-only authoritative database and internal durable transport.
- Python 3.12 asyncio confirmed as the production durable control plane (ADR-016; the earlier Java 25 selection was superseded before implementation began).
- React/TypeScript frontend.
- Local, Docker/OCI and Kubernetes runners first.
- On-premises Kubernetes/Helm as the first production and release-qualification topology.
- Isolated language-neutral plugins, with migration tooling preferred over unchanged JAR execution.
- Accepted first integration pack: HTTP/REST, webhooks, Git, GitHub, PostgreSQL, S3/MinIO, Docker/OCI, Kubernetes, OpenAI-compatible model APIs and MCP.
- AI workflow developer, software engineer and platform engineer as priority personas.
- First-class agent-mesh runtime and AI-native engineering governance added to scope.
- 99.9% monthly control-plane availability target.
- Profile M release qualification: 100,000 executions/day, 1,000 active task runs, 50 task starts/s and 10 million retained records.
- First stable release recovery gate: RPO <= 48 hours and RTO <= 8 hours.
- Full side-by-side migration of resources, governance, history, logs, artifacts and audit evidence.
- SOC 2 and ISO/IEC 27001 readiness architecture and evidence requirements.
- Independent agent quorum for ordinary merges; named human approval for high-risk changes and stable releases.

## Specified, not implemented

- Source-preserving Kestra YAML and Pebble compatibility.
- Durable PostgreSQL repositories, queue claimers, schedulers, executors, trigger services and reconcilers.
- Local, Docker/OCI and Kubernetes runner implementations.
- On-premises Helm chart, offline installation bundle and cross-distribution qualification.
- Plugin packaging, registry, sandbox hosts and multi-language SDKs.
- Full authentication, RBAC, SSO, multi-tenancy, audit, secrets and policy enforcement.
- React authoring, monitoring, administration and visual workflow UI.
- PostgreSQL search, logs, analytics projections and dashboards.
- High availability, backup/restore, rolling upgrades, profile M qualification and chaos evidence.
- Initial integration packs and the Kestra compatibility importer/conformance suite.
- Full historical and governance migration tooling.
- SOC 2/ISO control crosswalk and compliance evidence export.
- Agent merge-quorum enforcement and human approval binding.
- Agent mesh runtime, deterministic simulation, policy-as-code and agentic assistance.
- All remaining capabilities in the 103-epic backlog.

## Planning proof level

The planning baseline contains:

- 103 epics;
- 837 functional requirements;
- 63 non-functional requirements;
- 900 total requirements;
- 992 requirement-to-epic traceability links.

Passing current tests proves only the limited foundation behavior those tests cover. All 900 requirements remain `Proposed`; none is marked `Verified`.

The checked-in Python code is the seed of the production engine (ADR-016): the two-month MVP scope in `docs/product/mvp-scope.md` extends it into a running orchestrator, and its tests are tests of production behavior.
