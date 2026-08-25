# Roadmap

The roadmap is dependency-oriented rather than calendar-based. AI engineering capacity is elastic, but milestone exits are evidence gates rather than staffing or calendar promises.

## M0 — Foundation and clean-room baseline

**Exit condition:** Repository, legal boundary, parity inventory, DSL and state foundations are accepted.

**Epic count:** 12

- `EPIC-000` Clean-room governance and parity baseline
- `EPIC-001` Repository engineering, CI and release foundation
- `EPIC-002` Canonical resource model and identifiers
- `EPIC-003` Configuration and feature flag system
- `EPIC-004` Flow DSL, YAML model and schema
- `EPIC-005` Expression and templating engine
- `EPIC-006` Flow revisions, change history and promotion
- `EPIC-007` Execution event model and state machine
- `EPIC-008` Metadata persistence and migrations
- `EPIC-009` PostgreSQL transport, inbox and transactional outbox
- `EPIC-010` Internal object storage and artifact addressing
- `EPIC-011` AI-native engineering factory and autonomous contribution controls

## M1 — Single-node durable engine

**Exit condition:** A PostgreSQL-backed standalone server survives process failure and runs scheduled workflows.

**Epic count:** 12

- `EPIC-100` Executor and orchestration reducer
- `EPIC-101` Worker protocol, leases and heartbeats
- `EPIC-102` Scheduler and temporal correctness
- `EPIC-103` Trigger runtime and occurrence lifecycle
- `EPIC-104` Retries, timeout, pause, cancellation, kill and restart
- `EPIC-105` Concurrency, admission control and fairness
- `EPIC-106` Backfill, replay and historical reprocessing
- `EPIC-107` Subflows, dependencies and system flows
- `EPIC-108` Recovery, reconciliation and invariant repair
- `EPIC-109` Task and execution cache
- `EPIC-110` SLA, checks and execution policy evaluation
- `EPIC-111` Logs, metrics, outputs and artifact events

## M2 — Workflow semantics and core runners

**Exit condition:** Core flow control, files, errors, retries and process/container execution pass conformance tests.

**Epic count:** 14

- `EPIC-200` Runnable task contract
- `EPIC-201` Sequential, parallel and DAG flowables
- `EPIC-202` Conditional branching and switch semantics
- `EPIC-203` Loops, foreach, while and until
- `EPIC-204` Errors, finally and after-execution hooks
- `EPIC-205` Inputs, outputs and variables
- `EPIC-206` Labels, metadata and plugin defaults
- `EPIC-207` Namespace files, key-value store and secrets
- `EPIC-208` Working directories and execution files
- `EPIC-209` Task runner interface and capability model
- `EPIC-220` Local process task runner
- `EPIC-221` Docker and OCI task runner
- `EPIC-222` Kubernetes task runner
- `EPIC-223` Cloud batch, VM and serverless runners

## M3 — Plugin platform and integration packs

**Exit condition:** Third parties can build, test, publish and safely execute versioned plugins.

**Epic count:** 14

- `EPIC-300` Plugin SDK and manifest contract
- `EPIC-301` Plugin discovery, resolution and dependency isolation
- `EPIC-302` Trusted in-process plugin runtime
- `EPIC-303` Isolated language-neutral plugin runtime
- `EPIC-304` Trigger, condition and notification extension contracts
- `EPIC-305` Plugin registry, signing, SBOM and marketplace metadata
- `EPIC-306` Core utility plugin pack
- `EPIC-307` Multi-language script plugin pack
- `EPIC-308` Database, analytics and storage plugin pack
- `EPIC-309` Cloud and infrastructure plugin pack
- `EPIC-310` Messaging and event-stream plugin pack
- `EPIC-311` Notification and collaboration plugin pack
- `EPIC-312` Provider-neutral model, structured-output and MCP primitives
- `EPIC-313` Plugin developer portal and certification suite

## M4 — API, UI and self-service

**Exit condition:** Users can author, launch, observe, debug and administer workflows without direct database access.

**Epic count:** 12

- `EPIC-400` Versioned REST API and OpenAPI contract
- `EPIC-401` Realtime API, webhooks and event subscriptions
- `EPIC-402` CLI and generated client SDKs
- `EPIC-403` Authentication session and credential entry points
- `EPIC-404` Web UI shell, navigation and accessibility
- `EPIC-405` Flow code editor and validation experience
- `EPIC-406` Visual no-code editor and topology model
- `EPIC-407` Execution details, Gantt, logs and debugging UI
- `EPIC-408` Dashboards, query language and saved views
- `EPIC-409` Search, indexing and retrieval projections
- `EPIC-410` Namespace, settings and administration UI
- `EPIC-411` Blueprints, playground and onboarding

## M5 — Open governance and enterprise-class controls

**Exit condition:** Identity, tenancy, policy, audit, secrets, approvals and lineage are production-ready and fully OSS.

**Epic count:** 11

- `EPIC-500` Users, groups, roles, bindings and authorization
- `EPIC-501` Service accounts, API tokens and credentials
- `EPIC-502` SSO, OIDC, SAML, LDAP and SCIM
- `EPIC-503` Multi-tenancy and resource isolation
- `EPIC-504` Immutable audit log and evidence export
- `EPIC-505` Plugin allow, restrict and version policy
- `EPIC-506` External secrets managers and secret lifecycle
- `EPIC-507` Assets, lineage and catalog
- `EPIC-508` Apps, forms and human approval tasks
- `EPIC-509` Announcements, maintenance mode and kill switch
- `EPIC-510` Flow unit tests and quality gates

## M6 — Distributed operations and reliability

**Exit condition:** The platform scales horizontally, is observable, upgradeable, recoverable and security-hardened.

**Epic count:** 14

- `EPIC-600` Standalone server and compact deployment
- `EPIC-601` Distributed services and high availability
- `EPIC-602` PostgreSQL transactional backend
- `EPIC-603` PostgreSQL distributed work queue and notifications
- `EPIC-604` Search and analytics projection backend
- `EPIC-605` Object storage backends and lifecycle
- `EPIC-606` Containers, Kubernetes and Helm deployment
- `EPIC-607` OpenTelemetry, Prometheus and log shipping
- `EPIC-608` Retention, purge and data lifecycle
- `EPIC-609` Backup, restore and disaster recovery
- `EPIC-610` Upgrades, migrations and LTS policy
- `EPIC-611` Performance, scale and chaos qualification
- `EPIC-612` Security hardening and software supply chain
- `EPIC-613` TLS, networking, proxy and private connectivity

## M7 — Compatibility, infrastructure as code and ecosystem

**Exit condition:** Migration tooling, SDKs, GitOps, Terraform, operator and documentation support adoption.

**Epic count:** 7

- `EPIC-700` Git synchronization and CI/CD helpers
- `EPIC-701` Terraform and OpenTofu provider
- `EPIC-702` Kubernetes operator and declarative resources
- `EPIC-703` Public SDKs and embedded integration libraries
- `EPIC-704` Kestra migration importer and conformance suite
- `EPIC-705` Documentation, examples and community governance
- `EPIC-706` Reference integration environments and certification

## M8 — Differentiation and general availability

**Exit condition:** Differentiating features and GA quality targets are proven under reference workloads.

**Epic count:** 19

- `EPIC-800` Deterministic simulation and dry-run engine
- `EPIC-801` Agentic authoring and operational assistant
- `EPIC-802` Policy as code and admission controller
- `EPIC-803` Multi-region and edge worker topology
- `EPIC-804` Open enterprise distribution and packaging
- `EPIC-805` General availability quality and launch readiness
- `EPIC-806` Multi-agent topology, typed hand-offs and routing
- `EPIC-807` Versioned agent definitions and capability envelopes
- `EPIC-808` Durable bounded single-agent sessions
- `EPIC-809` Agent memory, evaluation and release gates
- `EPIC-810` Reliable scheduling and truthful role-aware health
- `EPIC-811` Client-neutral external orchestration contract
- `EPIC-812` Canonical execution evidence bundle
- `EPIC-813` Pluggable model-provider capabilities and conformance
- `EPIC-814` Unified MCP and plugin ToolProvider contract
- `EPIC-815` Hardened client-driven local deployment profile
- `EPIC-816` Restart, idempotency and large-record qualification
- `EPIC-817` Generic differential and shadow execution
- `EPIC-818` Evidence-backed promotion, rollback and release gates
