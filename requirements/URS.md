# User Requirements Specification (URS)

**Product:** AMESH — Agent Mesh
**Baseline:** Kestra 1.3.30 / `db49f3b2c2af60d61df10adb6f9fc34e4776b65b`
**Status:** Architecture-locked, implementation-ready backlog scaffold
**Generated:** 2026-08-29
**Functional requirements:** 837
**Non-functional requirements:** 63
**Total:** 900

## 1. Purpose

This URS defines the observable outcomes, quality attributes and verification expectations for AMESH: a clean-room, fully open-source, Kestra-compatible durable workflow and agent orchestration platform. It is an implementation baseline, not a claim that all requirements already exist.

## 2. Requirement language

- **Shall** is mandatory for the selected release scope.
- **Must/Should/Could** are MoSCoW priorities.
- **Verified** requires linked evidence; code completion alone is not verification.
- Compatibility is version-pinned and may be claimed only for surfaces with passing differential evidence.

## 3. Binding product decisions

- Product name: **AMESH (Agent Mesh)**.
- Licence grant: **AGPL-3.0-only**.
- Implementation model: strict clean room based on public specifications, observable behavior and independently authored tests.
- Scope: Kestra OSS parity, independently implemented advanced capabilities, and AMESH-specific agent-mesh differentiation in one open distribution.
- Compatibility surfaces: Kestra YAML, Pebble expressions, REST API, CLI, execution semantics and documented import/export formats.
- Reference persistence and durable internal transport: PostgreSQL only; LISTEN/NOTIFY is an optimization, never delivery truth.
- Production durable control plane: Python 3.12 asyncio (ADR-016); the checked-in foundation is the production engine seed.
- Web client: React and TypeScript.
- First runners: local process, Docker/OCI and Kubernetes.
- Production reference: on-premises Kubernetes/Helm with external PostgreSQL and S3-compatible object storage; Docker Compose is the development profile.
- Plugin direction: isolated language-neutral runtime with Java, Python and TypeScript SDKs; migration tools preferred over unchanged JAR loading.
- Priority users: AI workflow developers, software engineers and platform engineers.
- Accepted first integrations: HTTP/REST, webhooks, Git, GitHub, PostgreSQL, S3/MinIO, Docker/OCI, Kubernetes, OpenAI-compatible model APIs and MCP.
- Scale profile M: 100,000 executions/day, 1,000 active task runs, 50 task starts/second and 10 million retained execution records.
- Availability and recovery: 99.9% monthly control-plane target; v1 RPO <= 48 hours and RTO <= 8 hours.
- Migration: full side-by-side resources, identity/governance, historical executions, logs, artifacts and audit evidence.
- Compliance: SOC 2 and ISO/IEC 27001 readiness without a certification claim.
- Engineering authority: independent agent quorum for normal merges; named human approval for defined high-risk changes and stable releases.

All foundational product decisions required to begin M0 are accepted. The decision record is maintained in [`docs/product/decision-register.md`](../docs/product/decision-register.md); [`DECISIONS_NEEDED.md`](../DECISIONS_NEEDED.md) records whether any new product-owner blocker exists.

## 4. Functional requirements

### M0 — Foundation and clean-room baseline

Exit condition: Repository, legal boundary, parity inventory, DSL and state foundations are accepted.

#### EPIC-000 — Clean-room governance and parity baseline

Establish a defensible, repeatable method for reproducing observable capabilities without copying protected expression.

**URS-F-0001 — Must**

The system shall maintain a version-pinned parity inventory against Kestra v1.3.30 and its documented public behavior.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0002 — Must**

The system shall record source provenance for every compatibility requirement and prohibit copying source code, UI assets, trademarks, or documentation prose.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0003 — Must**

The system shall separate reference researchers from implementers when a strict clean-room mode is selected.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0004 — Must**

The system shall run automated similarity and license scans before every release.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0005 — Must**

The system shall document trademark-safe naming, attribution, notices, and contribution provenance.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0006 — Must**

The system shall track parity gaps, intentional differences, deferred features, and evidence in a machine-readable matrix.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0007 — Must**

The system shall provide a repeatable procedure for rebasing the parity target to a later upstream release.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-001 — Repository engineering, CI and release foundation

Create a contributor-friendly monorepo with deterministic builds, quality gates and release automation.

**URS-F-0008 — Must**

The system shall provide documented local development commands for backend, frontend, workers, plugins and documentation.

_Verification:_ Repository validation and CI tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0009 — Must**

The system shall enforce formatting, linting, typing, tests, dependency review and secret scanning in continuous integration.

_Verification:_ Repository validation and CI tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0010 — Must**

The system shall build reproducible source archives, containers, software bills of materials and signed release provenance.

_Verification:_ Repository validation and CI tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0011 — Must**

The system shall apply semantic versioning and publish migration notes for every incompatible change.

_Verification:_ Repository validation and CI tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0012 — Must**

The system shall support conventional commits, pull request templates, issue forms and ownership rules.

_Verification:_ Repository validation and CI tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0013 — Must**

The system shall validate repository structure, generated files, requirement traceability and architectural decision status.

_Verification:_ Repository validation and CI tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0014 — Must**

The system shall provide development containers and a Docker Compose reference environment.

_Verification:_ Repository validation and CI tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-002 — Canonical resource model and identifiers

Define stable resource identities and lifecycle conventions used across APIs, storage, events and permissions.

**URS-F-0015 — Must**

The system shall define canonical identifiers for tenants, namespaces, flows, revisions, executions, task runs, triggers, workers, plugins and assets.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0016 — Must**

The system shall validate identifier syntax, reserved words, length limits and case behavior consistently across all interfaces.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0017 — Must**

The system shall use sortable globally unique identifiers for mutable runtime records while preserving user-facing natural keys.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0018 — Must**

The system shall represent labels, annotations, timestamps, actor identity and resource version on every managed resource.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0019 — Must**

The system shall support optimistic concurrency through entity versions or entity tags.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0020 — Must**

The system shall define deletion, archival, tombstone and restoration semantics for each resource type.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0021 — Must**

The system shall serialize resources deterministically for hashing, diffing, signing and cache keys.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-003 — Configuration and feature flag system

Offer typed, layered and auditable configuration for standalone and distributed deployments.

**URS-F-0022 — Must**

The system shall load configuration from files, environment variables, command-line flags and secret references with a documented precedence order.

_Verification:_ Configuration and service integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0023 — Must**

The system shall validate all configuration at startup and reject unsafe or contradictory combinations.

_Verification:_ Configuration and service integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0024 — Must**

The system shall redact secrets from diagnostics, API responses, logs and crash reports.

_Verification:_ Configuration and service integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0025 — Must**

The system shall support dynamic reload only for explicitly reloadable settings.

_Verification:_ Configuration and service integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0026 — Must**

The system shall expose effective non-secret configuration and provenance to authorized administrators.

_Verification:_ Configuration and service integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0027 — Must**

The system shall provide feature flags with tenant, namespace and instance scopes.

_Verification:_ Configuration and service integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0028 — Must**

The system shall support deprecation warnings and automated migration of renamed settings.

_Verification:_ Configuration and service integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-004 — Flow DSL, YAML model and schema

Define a declarative workflow language capable of representing the full target feature set.

**URS-F-0029 — Must**

The system shall parse YAML and JSON flow definitions into a versioned canonical intermediate representation.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0030 — Must**

The system shall validate required fields, types, uniqueness, references, cycles and plugin-specific properties.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0031 — Must**

The system shall preserve comments and stable formatting where practical during visual or programmatic edits.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0032 — Must**

The system shall generate JSON Schema and editor metadata for every core and plugin-defined resource.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0033 — Must**

The system shall support namespaces, flow identifiers, descriptions, labels, inputs, variables, tasks, triggers, errors, finally blocks and outputs.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0034 — Must**

The system shall return machine-readable validation errors with source ranges and remediation hints.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0035 — Must**

The system shall support forward-compatible extension fields while rejecting unknown core fields by policy.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0036 — Must**

The system shall calculate deterministic semantic hashes that ignore non-semantic formatting.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-005 — Expression and templating engine

Provide deterministic runtime rendering for dynamic workflow values without granting arbitrary code execution.

**URS-F-0037 — Must**

The system shall render scalar, collection and object values against a documented execution context.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0038 — Must**

The system shall support conditions, filters, functions, date operations, collection operations, JSON and YAML conversion and safe string handling.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0039 — Must**

The system shall expose flow, execution, task-run, trigger, input, output, variable, label, namespace, secret and key-value contexts.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0040 — Must**

The system shall distinguish compile-time validation from runtime rendering failures.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0041 — Must**

The system shall sandbox expression evaluation with bounded time, memory, recursion and output size.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0042 — Must**

The system shall redact secret-derived values from previews, errors and logs.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0043 — Must**

The system shall provide compatibility tests for the selected Kestra Pebble expression subset.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0044 — Must**

The system shall allow future expression engines through a stable adapter without changing flow storage.

_Verification:_ Parser, schema, rendering and compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-006 — Flow revisions, change history and promotion

Make workflow definitions immutable by revision and safely promotable across environments.

**URS-F-0045 — Must**

The system shall create a new immutable revision for each semantic flow change.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0046 — Must**

The system shall show human-readable and machine-readable diffs between revisions.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0047 — Must**

The system shall pin every execution to the exact flow revision and plugin resolution set used at launch.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0048 — Must**

The system shall restore or clone an earlier revision without rewriting history.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0049 — Must**

The system shall support draft, active, disabled and archived lifecycle states.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0050 — Must**

The system shall attach actor, source, commit, environment and deployment metadata to revisions.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0051 — Must**

The system shall prevent incompatible revision deletion while executions or audit records reference it.

_Verification:_ Domain model unit and serialization compatibility tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-007 — Execution event model and state machine

Define the authoritative deterministic state transitions for workflows, tasks, triggers and service components.

**URS-F-0052 — Must**

The system shall represent all commands, decisions and state changes as typed versioned events.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0053 — Must**

The system shall enforce legal execution and task-run state transitions through a pure deterministic reducer.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0054 — Must**

The system shall retain immutable transition history with actor, reason, correlation and causation identifiers.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0055 — Must**

The system shall make duplicate commands and events idempotent by stable idempotency keys.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0056 — Must**

The system shall support replay from event history to rebuild current execution state.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0057 — Must**

The system shall record rejected transitions and invariant violations without corrupting state.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0058 — Must**

The system shall version the event schema and provide upcasters for supported historical versions.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0059 — Must**

The system shall publish committed events only after the corresponding state transaction succeeds.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-008 — Metadata persistence and migrations

Persist platform metadata transactionally with clear repository boundaries and safe schema evolution.

**URS-F-0060 — Must**

The system shall provide repository interfaces for flows, revisions, executions, task runs, triggers, workers, logs, metrics, assets and governance resources.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0061 — Must**

The system shall implement PostgreSQL as the reference transactional backend.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0062 — Must**

The system shall use explicit transactions and isolation levels for scheduling, claiming, state transitions and outbox publication.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0063 — Must**

The system shall apply ordered forward migrations with preflight checks and rollback guidance.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0064 — Must**

The system shall support online-compatible migrations for rolling upgrades whenever feasible.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0065 — Must**

The system shall protect invariants with database constraints in addition to application validation.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0066 — Must**

The system shall expose health, pool saturation, slow query and migration status metrics.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0067 — Must**

The system shall provide deterministic seed data and ephemeral test database support.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-009 — PostgreSQL transport, inbox and transactional outbox

Provide durable PostgreSQL-backed work delivery while preserving transactional correctness, idempotency and replayability.

**URS-F-0068 — Must**

The system shall define versioned message envelopes with identity, type, tenant, correlation, causation, timestamp and trace context.

_Verification:_ Delivery, ordering, duplicate and outage conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0069 — Must**

The system shall write outbound messages to a transactional outbox in the same transaction as state changes.

_Verification:_ Delivery, ordering, duplicate and outage conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0070 — Must**

The system shall deduplicate inbound messages through a durable inbox before applying side effects.

_Verification:_ Delivery, ordering, duplicate and outage conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0071 — Must**

The system shall support ordered processing by execution or trigger partition key.

_Verification:_ Delivery, ordering, duplicate and outage conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0072 — Must**

The system shall retry transient publication and consumption failures with bounded backoff and dead-letter handling.

_Verification:_ Delivery, ordering, duplicate and outage conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0073 — Must**

The system shall expose lag, redelivery, poison-message and dead-letter diagnostics.

_Verification:_ Delivery, ordering, duplicate and outage conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0074 — Must**

The system shall provide a PostgreSQL-backed durable queue adapter with transactional outbox, inbox, claim, retry and dead-letter semantics.

_Verification:_ Delivery, ordering, duplicate and outage conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0075 — Must**

The system shall document at-least-once delivery and external side-effect idempotency responsibilities.

_Verification:_ Delivery, ordering, duplicate and outage conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-010 — Internal object storage and artifact addressing

Store workflow files and artifacts independently from orchestration metadata.

**URS-F-0076 — Must**

The system shall address stored objects through opaque tenant-scoped URIs rather than local filesystem paths.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0077 — Must**

The system shall support local development storage and S3-compatible production storage through one interface.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0078 — Must**

The system shall stream uploads and downloads without loading large objects fully into process memory.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0079 — Must**

The system shall record size, content type, checksum, encryption metadata, creator, retention and lineage.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0080 — Must**

The system shall prevent cross-tenant access and path traversal at every storage boundary.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0081 — Must**

The system shall support multipart upload, ranged download and resumable transfer where the backend permits.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0082 — Must**

The system shall garbage-collect unreferenced objects only after a configurable safety window.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0083 — Must**

The system shall verify object integrity on write and optionally on read.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-011 — AI-native engineering factory and autonomous contribution controls

Make elastic AI engineering teams productive while preserving independent review, clean-room provenance, isolation and deterministic release evidence.

**URS-F-0798 — Must**

The system shall represent every implementation assignment as a requirement-linked machine-readable work item with scope, dependencies, allowed files and acceptance evidence.

_Verification:_ AI engineering workflow, isolation and evidence-gate tests.
_Source scope:_ AMESH engineering differentiator; not a Kestra-parity claim.

**URS-F-0799 — Must**

The system shall assign architect, implementer, test engineer, reviewer and verifier roles using independent task contexts.

_Verification:_ AI engineering workflow, isolation and evidence-gate tests.
_Source scope:_ AMESH engineering differentiator; not a Kestra-parity claim.

**URS-F-0800 — Must**

The system shall confine AI changes to isolated branches or worktrees and prevent direct writes to protected release branches.

_Verification:_ AI engineering workflow, isolation and evidence-gate tests.
_Source scope:_ AMESH engineering differentiator; not a Kestra-parity claim.

**URS-F-0801 — Must**

The system shall require every AI-authored pull request to record changed requirement IDs, implementation plan, risk, provenance and test evidence.

_Verification:_ AI engineering workflow, isolation and evidence-gate tests.
_Source scope:_ AMESH engineering differentiator; not a Kestra-parity claim.

**URS-F-0802 — Must**

The system shall prohibit an implementation agent from approving or being the sole verifier of its own change.

_Verification:_ AI engineering workflow, isolation and evidence-gate tests.
_Source scope:_ AMESH engineering differentiator; not a Kestra-parity claim.

**URS-F-0803 — Must**

The system shall execute AI-generated builds and tests in ephemeral least-privilege environments without production credentials.

_Verification:_ AI engineering workflow, isolation and evidence-gate tests.
_Source scope:_ AMESH engineering differentiator; not a Kestra-parity claim.

**URS-F-0804 — Must**

The system shall apply explicit token, cost, retry and elapsed-time budgets to engineering agents and escalate exhausted work with evidence.

_Verification:_ AI engineering workflow, isolation and evidence-gate tests.
_Source scope:_ AMESH engineering differentiator; not a Kestra-parity claim.

**URS-F-0805 — Must**

The system shall generate a signed evidence bundle containing reviews, test results, compatibility results, schemas, SBOM and traceability before release.

_Verification:_ AI engineering workflow, isolation and evidence-gate tests.
_Source scope:_ AMESH engineering differentiator; not a Kestra-parity claim.

**URS-F-0836 — Must**

The system shall allow a normal protected-branch change to merge only after deterministic gates pass and a configured quorum of independent review and verification agents approves it.

_Verification:_ AI merge-policy, quorum and evidence-replay tests.
_Source scope:_ AMESH engineering-governance decision; not a Kestra-parity claim.

**URS-F-0837 — Must**

The system shall require named human approval for security-sensitive changes, licensing or governance changes, destructive production migrations and every stable release.

_Verification:_ Protected-branch and release-authority policy tests.
_Source scope:_ AMESH engineering-governance decision; not a Kestra-parity claim.

### M1 — Single-node durable engine

Exit condition: A PostgreSQL-backed standalone server survives process failure and runs scheduled workflows.

#### EPIC-100 — Executor and orchestration reducer

Drive executions from committed state and events without executing untrusted task code in the control plane.

**URS-F-0084 — Must**

The system shall create executions from manual, API, scheduled, event and subflow launches.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0085 — Must**

The system shall expand runnable tasks only when dependencies and conditions are satisfied.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0086 — Must**

The system shall apply task-run results to the workflow state through the deterministic reducer.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0087 — Must**

The system shall coordinate sequential, parallel and dependency-driven branches without race-dependent outcomes.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0088 — Must**

The system shall emit dispatch commands, downstream trigger events and terminal execution events transactionally.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0089 — Must**

The system shall resume orchestration after executor restart without losing or duplicating logical progress.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0090 — Must**

The system shall detect deadlocked or unsatisfiable execution graphs and terminate them with actionable diagnostics.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0091 — Must**

The system shall support horizontally scaled executor instances through partitioning, leases or optimistic coordination.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-101 — Worker protocol, leases and heartbeats

Safely assign runnable work to workers and recover ownership after failure.

**URS-F-0092 — Must**

The system shall register workers with stable identity, version, capabilities, labels, runner types and capacity.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0093 — Must**

The system shall lease task runs atomically to one eligible worker using expiring ownership and fencing tokens.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0094 — Must**

The system shall renew leases through heartbeats that include progress, resource use and cancellation acknowledgement.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0095 — Must**

The system shall reject stale completion or mutation attempts from a worker holding an obsolete fencing token.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0096 — Must**

The system shall requeue or fail task runs according to policy when a worker or lease disappears.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0097 — Must**

The system shall drain workers without assigning new work while allowing in-flight work to finish.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0098 — Must**

The system shall expose worker inventory, liveness, utilization, claimed work and compatibility status.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0099 — Must**

The system shall support pull-based and PostgreSQL-notification-assisted dispatch through one versioned worker protocol.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-102 — Scheduler and temporal correctness

Create due executions exactly according to declared temporal semantics despite restarts and multiple scheduler replicas.

**URS-F-0100 — Must**

The system shall evaluate cron and interval schedules in explicit IANA time zones.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0101 — Must**

The system shall define deterministic behavior for daylight-saving gaps, overlaps and historical timezone changes.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0102 — Must**

The system shall persist next-fire state and acquire scheduler leases using fencing to prevent competing owners.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0103 — Must**

The system shall recover missed schedules according to catch-up, skip, coalesce or backfill policy.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0104 — Must**

The system shall apply start, end, disabled, paused and condition constraints before launch.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0105 — Must**

The system shall deduplicate schedule launches with a stable trigger occurrence identity.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0106 — Must**

The system shall preview future occurrences and explain why a schedule did or did not fire.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0107 — Must**

The system shall operate safely with multiple scheduler replicas and PostgreSQL failover or connection interruption.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-103 — Trigger runtime and occurrence lifecycle

Unify schedule, polling, webhook, realtime, flow and programmatic triggers under one occurrence model.

**URS-F-0108 — Must**

The system shall define trigger identities, revisions, state, conditions, inputs and occurrence metadata.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0109 — Must**

The system shall activate and deactivate trigger instances when flow revisions change.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0110 — Must**

The system shall persist trigger checkpoints and cursors before acknowledging external events where possible.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0111 — Must**

The system shall deduplicate repeated source events using connector-provided or derived occurrence keys.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0112 — Must**

The system shall support trigger backpressure, pause, retry, dead-letter and manual replay.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0113 — Must**

The system shall expose trigger health, last evaluation, next evaluation, lag and recent occurrences.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0114 — Must**

The system shall route flow-completion events to dependent flows without relying on polling.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0115 — Must**

The system shall allow plugins to implement polling and realtime trigger adapters through stable interfaces.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-104 — Retries, timeout, pause, cancellation, kill and restart

Give users predictable control over failure recovery and execution interruption.

**URS-F-0116 — Must**

The system shall apply configurable retry attempts, delays, exponential backoff, maximum interval and jitter.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0117 — Must**

The system shall classify errors as retryable, non-retryable, cancelled, timed out or infrastructure failures.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0118 — Must**

The system shall enforce task and execution timeouts using monotonic deadlines where possible.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0119 — Must**

The system shall pause and resume workflows without losing completed work or admitting new runnable tasks.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0120 — Must**

The system shall request graceful cancellation before escalating to force termination after a deadline.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0121 — Must**

The system shall restart an execution, task run or subflow from supported checkpoints with explicit state reset rules.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0122 — Must**

The system shall invalidate stale worker results after cancellation, retry or restart through fencing.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0123 — Must**

The system shall surface a complete intervention history and predicted consequences before destructive actions.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-105 — Concurrency, admission control and fairness

Protect shared capacity while offering predictable fairness across tenants, namespaces, flows and task types.

**URS-F-0124 — Must**

The system shall enforce execution and task concurrency limits at global, tenant, namespace, flow, worker-group and key scopes.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0125 — Must**

The system shall support queue, cancel, fail, replace and skip behaviors when a limit is reached.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0126 — Must**

The system shall evaluate dynamic concurrency keys from safe expressions.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0127 — Must**

The system shall reserve scarce resources atomically before dispatch and release them idempotently.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0128 — Must**

The system shall prioritize admitted work without starving lower-priority tenants or queues.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0129 — Must**

The system shall apply per-tenant quotas for active executions, queued work, storage, logs and API usage.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0130 — Must**

The system shall explain admission decisions and expose queued position, age and limiting policy.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0131 — Must**

The system shall recover leaked reservations after crashes through lease expiry and reconciliation.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-106 — Backfill, replay and historical reprocessing

Run historical workload ranges safely and observably without confusing them with live trigger traffic.

**URS-F-0132 — Must**

The system shall create backfills over explicit time ranges, partitions or selected trigger occurrences.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0133 — Must**

The system shall preview the number of executions and estimated impact before submitting a backfill.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0134 — Must**

The system shall apply concurrency, rate, priority, labels, inputs and revision pinning to a backfill.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0135 — Must**

The system shall pause, resume, cancel and monitor a backfill as a first-class resource.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0136 — Must**

The system shall replay one or more prior executions while preserving source lineage.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0137 — Must**

The system shall prevent accidental duplicate external effects through dry-run and idempotency guidance.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0138 — Must**

The system shall track generated executions and aggregate success, failure, duration and cost.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0139 — Must**

The system shall resume incomplete backfills after service restart without regenerating completed occurrences.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-107 — Subflows, dependencies and system flows

Compose workflows while preserving parent-child state, outputs, cancellation and authorization.

**URS-F-0140 — Must**

The system shall invoke another flow by tenant, namespace, identifier and selected or current revision.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0141 — Must**

The system shall pass typed inputs, labels, correlation and trace context from parent to child.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0142 — Must**

The system shall choose synchronous wait, asynchronous launch or detached invocation semantics.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0143 — Must**

The system shall propagate success, failure, cancellation, pause and restart according to explicit policy.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0144 — Must**

The system shall map child outputs and artifacts back to the parent with schema validation.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0145 — Must**

The system shall prevent recursive invocation beyond configured depth and detect dependency cycles.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0146 — Must**

The system shall support privileged system flows for notifications, governance and operational automation.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0147 — Must**

The system shall authorize parent and child resources independently and record cross-namespace access.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-108 — Recovery, reconciliation and invariant repair

Continuously detect and safely repair drift caused by process, PostgreSQL, worker, runner or object-storage failure.

**URS-F-0148 — Must**

The system shall scan for expired leases, orphan task runs, stuck executions, missing dispatches and unprojected events.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0149 — Must**

The system shall rebuild disposable projections from authoritative state and event records.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0150 — Must**

The system shall apply only idempotent, version-checked repairs and record every repair as an auditable event.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0151 — Must**

The system shall quarantine ambiguous cases for operator review instead of guessing.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0152 — Must**

The system shall provide targeted reconciliation by execution, trigger, worker, tenant or time range.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0153 — Must**

The system shall rate-limit repair work so recovery cannot overwhelm the primary workload.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0154 — Must**

The system shall publish repair metrics, unresolved invariant counts and runbook links.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0155 — Must**

The system shall prove recovery scenarios through fault-injection and crash-consistency tests.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-109 — Task and execution cache

Reuse deterministic task results without hiding provenance or serving stale data unexpectedly.

**URS-F-0156 — Must**

The system shall derive cache keys from declared inputs, code or plugin version, flow revision and selected contextual values.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0157 — Must**

The system shall support explicit cache time-to-live, namespace, scope and invalidation policy.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0158 — Must**

The system shall store outputs, metrics and artifact references with the cached result.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0159 — Must**

The system shall prevent reuse across tenants or security contexts unless explicitly permitted.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0160 — Must**

The system shall explain cache hit, miss, bypass and invalidation reasons in execution details.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0161 — Must**

The system shall allow users to disable, refresh or purge caches by key prefix and resource scope.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0162 — Must**

The system shall handle concurrent cache population with single-flight or safe duplicate computation.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0163 — Must**

The system shall include cache provenance in lineage and audit records.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-110 — SLA, checks and execution policy evaluation

Evaluate operational expectations during and after executions and make violations actionable.

**URS-F-0164 — Must**

The system shall define duration, start-delay, freshness, completion-window, output and custom expression checks.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0165 — Must**

The system shall evaluate checks at deterministic lifecycle points and on periodic deadlines.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0166 — Must**

The system shall record pass, warn, fail and error outcomes separately from task execution state.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0167 — Must**

The system shall trigger notifications, system flows or policy actions from check and SLA outcomes.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0168 — Must**

The system shall aggregate compliance by tenant, namespace, flow, label and time period.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0169 — Must**

The system shall allow check definitions to be reused through namespace policy or plugin defaults.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0170 — Must**

The system shall prevent policy loops and bound the work caused by violation handlers.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0171 — Must**

The system shall expose evidence used for each evaluation.

_Verification:_ Automated unit, integration, crash-recovery and conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-111 — Logs, metrics, outputs and artifact events

Capture task-produced evidence as structured, searchable and streamable execution data.

**URS-F-0172 — Must**

The system shall ingest structured and unstructured logs with execution, task-run, worker, tenant and trace context.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0173 — Must**

The system shall preserve event time, ingest time, severity, logger, attempt and source stream.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0174 — Must**

The system shall accept typed counters, gauges, timers and custom metrics from tasks and plugins.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0175 — Must**

The system shall persist task and flow outputs separately from logs with size and sensitivity controls.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0176 — Must**

The system shall link artifact metadata to internal storage without embedding large payloads in metadata records.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0177 — Must**

The system shall stream new logs and state updates to authorized clients with reconnect cursors.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0178 — Must**

The system shall apply redaction, retention, sampling and export policies before external shipment.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0179 — Must**

The system shall continue execution when optional telemetry sinks are temporarily unavailable.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

### M2 — Workflow semantics and core runners

Exit condition: Core flow control, files, errors, retries and process/container execution pass conformance tests.

#### EPIC-200 — Runnable task contract

Define the lifecycle contract for units of executable work.

**URS-F-0180 — Must**

The system shall validate task configuration against plugin-provided schemas before an execution starts.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0181 — Must**

The system shall create one task-run identity per logical attempt and preserve attempt history.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0182 — Must**

The system shall supply a typed execution context, scoped secrets, files, variables and cancellation channel.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0183 — Must**

The system shall capture structured outputs, metrics, logs, artifacts and exit metadata.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0184 — Must**

The system shall distinguish user-code failure, configuration failure, infrastructure failure and platform failure.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0185 — Must**

The system shall support synchronous completion and asynchronous deferral with a durable resume token.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0186 — Must**

The system shall bound task resource use and enforce output, log and artifact limits.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0187 — Must**

The system shall make task completion idempotent and reject stale attempt results.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-201 — Sequential, parallel and DAG flowables

Express common dependency and parallelism patterns as first-class flowable tasks.

**URS-F-0188 — Must**

The system shall execute child tasks sequentially in declared order.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0189 — Must**

The system shall execute independent child tasks in parallel up to declared and platform concurrency limits.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0190 — Must**

The system shall execute directed acyclic graphs from explicit dependency edges.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0191 — Must**

The system shall validate DAG references and cycles at flow revision creation time.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0192 — Must**

The system shall aggregate child states, outputs and errors using documented deterministic rules.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0193 — Must**

The system shall support fail-fast, continue-on-error and collect-all policies.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0194 — Must**

The system shall render child task contexts without leaking sibling-private values.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0195 — Must**

The system shall visualize expanded dependency graphs before and during execution.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-202 — Conditional branching and switch semantics

Choose workflow branches from safe expressions with explainable decisions.

**URS-F-0196 — Must**

The system shall execute if, else-if and else branches from boolean conditions.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0197 — Must**

The system shall select switch cases by exact value, ordered predicate or default branch.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0198 — Must**

The system shall record rendered condition inputs, redacted evaluation result and selected branch.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0199 — Must**

The system shall treat expression errors according to explicit fail, false or fallback policy.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0200 — Must**

The system shall skip non-selected branches without creating misleading runnable attempts.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0201 — Must**

The system shall support conditions on tasks, triggers, retries, errors and outputs.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0202 — Must**

The system shall validate unreachable or duplicate cases where static analysis permits.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-203 — Loops, foreach, while and until

Repeat work over data or conditions while maintaining bounded, resumable state.

**URS-F-0203 — Must**

The system shall iterate over arrays, maps, ranges, batches and streamed item manifests.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0204 — Must**

The system shall expose stable iteration index, key, value and parent context to each child run.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0205 — Must**

The system shall apply per-loop parallelism and preserve deterministic output ordering.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0206 — Must**

The system shall evaluate while and until conditions at documented checkpoints.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0207 — Must**

The system shall enforce maximum iterations, duration and generated task-run limits.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0208 — Must**

The system shall resume loops after restart without repeating acknowledged iterations.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0209 — Must**

The system shall support break, continue and failure aggregation policies.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0210 — Must**

The system shall store large iteration payloads in object storage rather than execution metadata.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-204 — Errors, finally and after-execution hooks

Run recovery and cleanup logic predictably for task, branch and execution outcomes.

**URS-F-0211 — Must**

The system shall attach error handlers at task-group, flowable and flow scopes.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0212 — Must**

The system shall select handlers by state, error category, task identity or safe expression.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0213 — Must**

The system shall execute finally tasks after success, failure or cancellation under documented rules.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0214 — Must**

The system shall execute after-execution tasks after terminal state persistence and expose the terminal context.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0215 — Must**

The system shall preserve the primary failure while recording cleanup failures separately.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0216 — Must**

The system shall prevent cleanup retries or recursive handlers from creating unbounded loops.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0217 — Must**

The system shall allow handlers to emit notifications, compensation commands and diagnostic artifacts.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0218 — Must**

The system shall visualize handler execution and its relationship to the primary task graph.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-205 — Inputs, outputs and variables

Provide typed data contracts at flow and task boundaries.

**URS-F-0219 — Must**

The system shall declare string, number, boolean, datetime, duration, enum, array, object, file and secret input types.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0220 — Must**

The system shall apply required, default, validation, display, prefill and sensitivity metadata.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0221 — Must**

The system shall validate manual, API, trigger and subflow inputs before creating runnable work.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0222 — Must**

The system shall declare flow outputs rendered from completed execution context.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0223 — Must**

The system shall keep static variables separate from execution inputs and mutable key-value data.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0224 — Must**

The system shall enforce payload size limits and move large file values into internal storage.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0225 — Must**

The system shall generate UI forms and API schemas from the same input definitions.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0226 — Must**

The system shall redact sensitive inputs and outputs according to schema metadata and policy.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-206 — Labels, metadata and plugin defaults

Apply searchable metadata and inherited defaults without hidden ambiguity.

**URS-F-0227 — Must**

The system shall attach user and system labels to flows, executions, task runs, assets and backfills.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0228 — Must**

The system shall reserve protected system label prefixes and prevent user spoofing.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0229 — Must**

The system shall support namespace-scoped plugin defaults with exact type and property matching.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0230 — Must**

The system shall define deterministic inheritance, merge and override precedence.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0231 — Must**

The system shall show the effective configuration and origin of every inherited value.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0232 — Must**

The system shall allow policy to require, deny or normalize selected labels and defaults.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0233 — Must**

The system shall index labels for filtering, dashboards, quotas, routing and retention.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-207 — Namespace files, key-value store and secrets

Offer namespace-scoped shared resources with inheritance and fine-grained access control.

**URS-F-0234 — Must**

The system shall upload, list, download, move, version and delete namespace files through API, UI and CLI.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0235 — Must**

The system shall resolve inherited namespace files from parent namespaces with explicit precedence.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0236 — Must**

The system shall create typed key-value entries with optional expiry, metadata and atomic compare-and-set.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0237 — Must**

The system shall watch or poll key-value changes for supported automation use cases.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0238 — Must**

The system shall resolve secrets only at execution time and never persist plaintext in flow revisions.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0239 — Must**

The system shall apply independent read, write, list and use permissions to files, key-values and secrets.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0240 — Must**

The system shall record access and mutation audit events without revealing protected values.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0241 — Must**

The system shall support import, export and environment promotion without exporting secret plaintext.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-208 — Working directories and execution files

Move files safely between tasks, runners and object storage.

**URS-F-0242 — Must**

The system shall create a unique disposable working directory for each task attempt.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0243 — Must**

The system shall materialize declared input files from internal storage with checksum verification.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0244 — Must**

The system shall collect declared output files by path, glob or manifest and upload them atomically.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0245 — Must**

The system shall prevent path traversal, symlink escape and cross-task filesystem access.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0246 — Must**

The system shall support a shared working-directory flowable with explicit lifetime and concurrency rules.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0247 — Must**

The system shall clean local working data after upload while retaining diagnostics on configured failures.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0248 — Must**

The system shall stream large files and enforce per-task storage quotas.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0249 — Must**

The system shall record file lineage from source artifact through transformations and outputs.

_Verification:_ DSL validation plus end-to-end workflow conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-209 — Task runner interface and capability model

Separate task semantics from the environment that executes user code.

**URS-F-0250 — Must**

The system shall define a runner-neutral request containing image or command, files, environment, resources, network and security policy.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0251 — Must**

The system shall advertise runner capabilities and reject unsupported requests before dispatch.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0252 — Must**

The system shall return normalized process status, logs, metrics, outputs and infrastructure diagnostics.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0253 — Must**

The system shall propagate cancellation and timeout with a documented escalation sequence.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0254 — Must**

The system shall support runner-specific configuration through typed extension fields.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0255 — Must**

The system shall isolate credentials so a runner receives only the scoped capability required for one attempt.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0256 — Must**

The system shall clean up orphan runtime resources through idempotent reconciliation.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0257 — Must**

The system shall allow namespace and worker-group policy to select or prohibit runners.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-220 — Local process task runner

Run trusted scripts and commands directly on a worker for local development and controlled environments.

**URS-F-0258 — Must**

The system shall execute argv-based commands without implicit shell parsing unless explicitly requested.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0259 — Must**

The system shall set working directory, environment, standard input, user and resource limits.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0260 — Must**

The system shall stream stdout and stderr while preserving ordering metadata and severity mapping.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0261 — Must**

The system shall terminate process groups reliably on cancellation or timeout.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0262 — Must**

The system shall support Linux and macOS development with documented Windows constraints.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0263 — Must**

The system shall disable the runner by default in untrusted multi-tenant deployments.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0264 — Must**

The system shall capture exit code, signal, duration and peak resource use.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-221 — Docker and OCI task runner

Execute isolated task containers with governed images, mounts, networking and cleanup.

**URS-F-0265 — Must**

The system shall pull images by immutable digest or resolve tags under explicit policy.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0266 — Must**

The system shall create containers with declared CPU, memory, user, capabilities, filesystem and network restrictions.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0267 — Must**

The system shall transfer input and output files without exposing the host control plane filesystem.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0268 — Must**

The system shall stream container logs and collect exit, OOM and runtime diagnostics.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0269 — Must**

The system shall support rootless engines and remote OCI runtimes where practical.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0270 — Must**

The system shall enforce image registry allowlists, signature verification and vulnerability policy.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0271 — Must**

The system shall remove containers, volumes and temporary credentials idempotently after completion.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0272 — Must**

The system shall avoid mounting the host Docker socket into untrusted task containers.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-222 — Kubernetes task runner

Run task attempts as isolated Kubernetes resources across configured clusters.

**URS-F-0273 — Must**

The system shall create Jobs or Pods from a typed runner request and configurable templates.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0274 — Must**

The system shall select cluster, namespace, service account, node placement and runtime class through policy.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0275 — Must**

The system shall apply resource requests, limits, security context, network policy and ephemeral storage limits.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0276 — Must**

The system shall stream logs and status despite API reconnects or worker restarts.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0277 — Must**

The system shall collect outputs through object storage or a controlled sidecar mechanism.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0278 — Must**

The system shall propagate cancellation and delete owned resources using finalizers and idempotent cleanup.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0279 — Must**

The system shall distinguish scheduling, image, infrastructure, eviction and user-process failures.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0280 — Must**

The system shall support workload identity without long-lived cloud credentials.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-223 — Cloud batch, VM and serverless runners

Offload task execution to managed cloud compute through interchangeable adapters.

**URS-F-0281 — Should**

The system shall define adapter contracts for batch jobs, temporary virtual machines and serverless job services.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0282 — Should**

The system shall submit jobs with deterministic external identifiers and idempotency tokens.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0283 — Should**

The system shall poll or subscribe to state while tolerating eventual consistency and API throttling.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0284 — Should**

The system shall stream or collect logs and outputs through cloud-native storage integrations.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0285 — Should**

The system shall cancel and reconcile externally running jobs after control-plane failure.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0286 — Should**

The system shall map provider failure states into normalized runner failure categories.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0287 — Should**

The system shall estimate and record provider resource usage and cost metadata.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0288 — Should**

The system shall ship reference adapters for at least one AWS, Azure and Google Cloud service before GA.

_Verification:_ Runner contract tests against disposable execution environments.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

### M3 — Plugin platform and integration packs

Exit condition: Third parties can build, test, publish and safely execute versioned plugins.

#### EPIC-300 — Plugin SDK and manifest contract

Let independent developers extend tasks, triggers, conditions, runners, storage and secrets through stable contracts.

**URS-F-0289 — Must**

The system shall define a versioned plugin manifest with identity, version, vendor, license, entry points, dependencies and compatibility range.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0290 — Must**

The system shall provide typed SDK interfaces for task, trigger, condition, runner, storage, secret, expression and notification extensions.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0291 — Must**

The system shall generate configuration schema, documentation metadata and UI controls from plugin declarations.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0292 — Must**

The system shall provide local test harnesses, fixtures and contract tests for each extension type.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0293 — Must**

The system shall separate platform API stability from implementation language and transport.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0294 — Must**

The system shall allow plugins to declare required capabilities, network access, filesystem access and secret scopes.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0295 — Must**

The system shall return structured user-facing configuration and runtime errors.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0296 — Must**

The system shall publish a compatibility policy and deprecation lifecycle for SDK changes.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-301 — Plugin discovery, resolution and dependency isolation

Resolve a deterministic plugin set for each flow revision without classpath or dependency ambiguity.

**URS-F-0297 — Must**

The system shall discover installed plugins from configured directories, registries and embedded distributions.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0298 — Must**

The system shall resolve plugin type references to an exact package version and content digest.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0299 — Must**

The system shall detect duplicate types, incompatible SDK ranges and dependency conflicts before activation.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0300 — Must**

The system shall pin the resolved plugin set into each flow revision and execution.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0301 — Must**

The system shall isolate plugin dependencies from the control plane and from other plugin versions.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0302 — Must**

The system shall refresh plugin catalogs without interrupting executions already pinned to older versions.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0303 — Must**

The system shall expose installed, active, deprecated, incompatible and quarantined plugin status.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0304 — Must**

The system shall support offline installation from verified bundles.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-302 — Trusted in-process plugin runtime

Run selected high-trust plugins with low overhead while containing dependency and lifecycle failures.

**URS-F-0305 — Must**

The system shall load only administrator-approved in-process plugins.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0306 — Must**

The system shall initialize and stop plugin components through bounded lifecycle hooks.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0307 — Must**

The system shall isolate plugin namespaces or classloaders where the implementation language supports it.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0308 — Must**

The system shall apply timeouts and circuit breakers to plugin callbacks invoked by control-plane services.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0309 — Must**

The system shall prevent one plugin from registering or overriding another plugin's identities.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0310 — Must**

The system shall report plugin memory, error and latency telemetry.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0311 — Must**

The system shall quarantine a plugin version that repeatedly violates runtime invariants.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0312 — Must**

The system shall document that in-process plugins share the host security boundary.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-303 — Isolated language-neutral plugin runtime

Execute third-party plugins out of process or in OCI sandboxes through a language-neutral protocol.

**URS-F-0313 — Must**

The system shall define an RPC protocol for schema discovery, validation, execution, cancellation, heartbeats, logs, metrics and artifacts.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0314 — Must**

The system shall launch plugin services as managed local processes, containers or remote endpoints.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0315 — Must**

The system shall authenticate every plugin session with short-lived workload identity.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0316 — Must**

The system shall grant per-call capabilities for secrets, files, network destinations and platform APIs.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0317 — Must**

The system shall enforce CPU, memory, wall-time, output and concurrency limits.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0318 — Must**

The system shall restart crashed plugin services without losing durable task ownership semantics.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0319 — Must**

The system shall support SDKs for at least Python, Java, JavaScript or TypeScript and Go before GA.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0320 — Must**

The system shall version the wire protocol and negotiate compatible features.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-304 — Trigger, condition and notification extension contracts

Make non-task workflow extensions first-class and durable.

**URS-F-0321 — Must**

The system shall support polling triggers with durable checkpoints and normalized occurrence identities.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0322 — Must**

The system shall support realtime triggers with connection lifecycle, backpressure and acknowledgement hooks.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0323 — Must**

The system shall support conditions that return boolean results and explainable evaluation evidence.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0324 — Must**

The system shall support notification plugins that receive typed lifecycle events and delivery policy.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0325 — Must**

The system shall apply retry, timeout, cancellation and secret-scope behavior consistently across extension types.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0326 — Must**

The system shall validate trigger and condition configuration without opening external connections.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0327 — Must**

The system shall provide emulator and fault-injection fixtures for connector developers.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-305 — Plugin registry, signing, SBOM and marketplace metadata

Distribute plugins with verifiable provenance and enough metadata for safe adoption.

**URS-F-0328 — Must**

The system shall publish immutable plugin bundles by name, semantic version and digest.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0329 — Must**

The system shall store license, source, documentation, supported platform range, SDK range and changelog metadata.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0330 — Must**

The system shall attach software bills of materials, vulnerability reports and provenance attestations.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0331 — Must**

The system shall sign registry metadata and plugin artifacts and verify signatures before installation.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0332 — Must**

The system shall support allowlisted registries, mirrors, proxies and offline export or import.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0333 — Must**

The system shall display popularity, maintenance, certification and security status without treating them as trust guarantees.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0334 — Must**

The system shall yank compromised versions without deleting historical metadata needed by pinned executions.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0335 — Must**

The system shall provide an OSS registry API and a self-hosted registry implementation.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-306 — Core utility plugin pack

Ship dependable generic building blocks for control flow, HTTP, files, data conversion and diagnostics.

**URS-F-0336 — Must**

The system shall provide HTTP request and download tasks with authentication, retry, pagination and response limits.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0337 — Must**

The system shall provide file compression, archive extraction, checksum, copy, move and delete tasks.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0338 — Must**

The system shall provide JSON, YAML, CSV, XML and text parsing or transformation tasks.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0339 — Must**

The system shall provide sleep, fail, log, return, debug and assertion tasks.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0340 — Must**

The system shall provide webhook, schedule, flow and manual trigger implementations in the core distribution.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0341 — Must**

The system shall provide notification primitives for email and generic webhooks.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0342 — Must**

The system shall apply SSRF, decompression bomb, path traversal and payload size protections.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0343 — Must**

The system shall cover all core utilities with deterministic integration fixtures.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-307 — Multi-language script plugin pack

Run scripts in common languages with consistent dependency, file, log, metric and output behavior.

**URS-F-0344 — Must**

The system shall support shell, Python, Node.js, Java, R and PowerShell execution through task runners.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0345 — Must**

The system shall support inline scripts, namespace files, repository files and packaged source artifacts.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0346 — Must**

The system shall allow runtime dependency installation only under explicit network and supply-chain policy.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0347 — Must**

The system shall offer documented helpers for outputs, metrics, logs and file manifests.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0348 — Must**

The system shall select default images by immutable release and permit organization-approved overrides.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0349 — Must**

The system shall capture interpreter and package metadata for reproducibility.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0350 — Must**

The system shall prevent interpolation injection by separating script content, arguments and environment values.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0351 — Must**

The system shall provide sample flows and contract tests for each supported language.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-308 — Database, analytics and storage plugin pack

Connect workflows to widely used databases, warehouses and object stores.

**URS-F-0352 — Must**

The system shall provide JDBC or native SQL task patterns for queries, scripts, batch operations and streaming result export.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0353 — Must**

The system shall support PostgreSQL, MySQL-compatible, SQL Server and SQLite reference connectors.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0354 — Must**

The system shall support at least two major cloud data warehouses before GA.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0355 — Must**

The system shall support S3-compatible, Azure Blob and Google Cloud Storage operations.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0356 — Must**

The system shall handle credentials, TLS, proxies, pagination, transactions and large-result streaming consistently.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0357 — Must**

The system shall emit lineage metadata for read and written datasets when identifiable.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0358 — Must**

The system shall classify transient, constraint, authentication and query failures for retry policy.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0359 — Must**

The system shall ship containerized integration tests against supported open-source services.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-309 — Cloud and infrastructure plugin pack

Automate cloud and infrastructure services with scoped identity and normalized behavior.

**URS-F-0360 — Must**

The system shall provide credential-chain and workload-identity support for AWS, Azure and Google Cloud.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0361 — Must**

The system shall provide common compute, storage, serverless, batch and infrastructure automation tasks.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0362 — Must**

The system shall support Terraform, OpenTofu, Ansible, Kubernetes and Git command workflows.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0363 — Must**

The system shall record external resource identifiers, regions, accounts and change summaries.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0364 — Must**

The system shall apply provider rate-limit handling, idempotency tokens and retry classification.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0365 — Must**

The system shall support plan or preview modes before mutating infrastructure where the underlying tool permits.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0366 — Must**

The system shall isolate cloud credentials per task attempt and redact them from subprocess environments after use.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0367 — Must**

The system shall maintain tested examples for multi-account and private-network deployments.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-310 — Messaging and event-stream plugin pack

Publish, consume and trigger workflows from common messaging systems.

**URS-F-0368 — Must**

The system shall support Kafka-compatible, NATS, AMQP and cloud queue or pub-sub systems.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0369 — Must**

The system shall provide batch and streaming consumption with durable checkpoints and acknowledgement policy.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0370 — Must**

The system shall derive deterministic occurrence identities from topic, partition, offset or source message identity.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0371 — Must**

The system shall support schema registry, headers, keys, compression and common serialization formats.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0372 — Must**

The system shall control concurrency, prefetch, backpressure, poison-message and dead-letter behavior.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0373 — Must**

The system shall avoid acknowledging source messages before the platform durably records the trigger occurrence.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0374 — Must**

The system shall support transactional or effectively-once patterns when the source and destination permit.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0375 — Must**

The system shall publish lag, throughput, redelivery and checkpoint metrics.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-311 — Notification and collaboration plugin pack

Deliver human and machine notifications through common communication platforms.

**URS-F-0376 — Must**

The system shall support email, generic webhook, Slack-compatible, Microsoft Teams-compatible and incident-management endpoints.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0377 — Must**

The system shall render templated messages with redacted execution context and links.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0378 — Must**

The system shall support thread, update, resolve and deduplication semantics where the destination permits.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0379 — Must**

The system shall apply per-destination rate limits, retries, circuit breakers and dead-letter storage.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0380 — Must**

The system shall record delivery attempt evidence without storing sensitive message content unnecessarily.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0381 — Must**

The system shall allow namespace policy to restrict destinations and templates.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0382 — Must**

The system shall provide notification system-flow examples for failure, SLA, approval and recovery events.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-312 — Provider-neutral model, structured-output and MCP primitives

Provide bounded provider-neutral model and MCP task primitives with structured results, explicit policy, complete provenance and no autonomous session state.

**URS-F-0383 — Must**

The system shall provide provider-neutral chat, embedding, structured-output and tool-call tasks.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0384 — Must**

The system shall support model endpoint, credential, budget, timeout, retry and data-handling policy.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0385 — Must**

The system shall expose workflows and approved operations through an authenticated MCP server.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0386 — Must**

The system shall invoke external MCP tools through scoped allowlists and auditable tool calls.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0387 — Must**

The system shall store prompts, model parameters, usage, cost and response provenance subject to redaction policy.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0388 — Must**

The system shall validate structured outputs against JSON Schema before downstream use.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0389 — Must**

The system shall require approval or policy checks for high-impact tools and sensitive data movement.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0390 — Must**

The system shall support replay with pinned model and prompt metadata while acknowledging provider nondeterminism.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-313 — Plugin developer portal and certification suite

Reduce plugin development friction and define transparent quality levels.

**URS-F-0391 — Must**

The system shall provide generated SDK documentation, starter templates and local sandbox tooling.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0392 — Must**

The system shall run manifest, schema, contract, security, license and compatibility checks in one command.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0393 — Must**

The system shall publish reference fixtures for retries, cancellation, large files, secret redaction and worker restart.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0394 — Must**

The system shall generate human-readable documentation and sample configuration from plugin metadata.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0395 — Must**

The system shall define community, verified and certified quality levels with objective criteria.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0396 — Must**

The system shall allow maintainers to reproduce certification results from public CI evidence.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0397 — Must**

The system shall track compatibility across supported platform releases.

_Verification:_ Plugin SDK contract, sandbox and integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

### M4 — API, UI and self-service

Exit condition: Users can author, launch, observe, debug and administer workflows without direct database access.

#### EPIC-400 — Versioned REST API and OpenAPI contract

Expose the complete supported control plane through a stable, documented and automatable API.

**URS-F-0398 — Must**

The system shall provide CRUD and lifecycle endpoints for flows, revisions, executions, task runs, triggers, backfills, namespaces, files, key-values, plugins and governance resources.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0399 — Must**

The system shall use consistent pagination, filtering, sorting, field selection, error envelopes and idempotency headers.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0400 — Must**

The system shall generate an OpenAPI document from implementation types and validate backward compatibility in CI.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0401 — Must**

The system shall support optimistic concurrency and conditional requests for mutable resources.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0402 — Must**

The system shall accept bulk operations with per-item results and bounded transactional scope.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0403 — Must**

The system shall stream large imports, exports, logs and artifacts rather than buffering them.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0404 — Must**

The system shall version incompatible contracts and publish a deprecation schedule.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0405 — Must**

The system shall enforce authorization and tenant scope before resource existence is disclosed.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-401 — Realtime API, webhooks and event subscriptions

Deliver state, log and audit changes to clients without fragile polling.

**URS-F-0406 — Must**

The system shall provide reconnectable server-sent event or WebSocket streams with cursor-based resume.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0407 — Must**

The system shall filter subscriptions by authorized tenant, namespace, flow, execution, event type and severity.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0408 — Must**

The system shall bound per-client buffers and apply backpressure or disconnect policy.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0409 — Must**

The system shall provide signed outbound webhooks with retries, rotation, replay protection and delivery history.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0410 — Must**

The system shall let consumers test webhook endpoints and replay selected deliveries.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0411 — Must**

The system shall redact event payloads according to field sensitivity and caller permissions.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0412 — Must**

The system shall emit heartbeats and explicit gap signals when a cursor is no longer available.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0413 — Must**

The system shall continue core orchestration when realtime clients or webhook destinations are unavailable.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-402 — CLI and generated client SDKs

Make all common platform operations scriptable and suitable for CI/CD.

**URS-F-0414 — Must**

The system shall provide a cross-platform CLI for authentication, configuration, flows, executions, namespaces, files, plugins and administration.

_Verification:_ tests/test_cli.py and tests/test_cli_epic402.py::test_urs_f_0414_0415_0419_0420_profiles_secure_tokens_and_output_modes plus test_urs_f_0414_0416_declarative_stdin_diff_export_delete_and_admin.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0415 — Must**

The system shall support human-readable, JSON and quiet output modes with stable exit codes.

_Verification:_ tests/test_cli_epic402.py::test_urs_f_0414_0415_0419_0420_profiles_secure_tokens_and_output_modes.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0416 — Must**

The system shall support declarative apply, diff, delete and export workflows from files or standard input.

_Verification:_ tests/test_cli_epic402.py::test_urs_f_0414_0416_declarative_stdin_diff_export_delete_and_admin.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0417 — Must**

The system shall generate typed Python, JavaScript or TypeScript, Java and Go clients from the supported API contract.

_Verification:_ tests/test_sdk_contracts.py::test_urs_f_0417_0418_generated_sdk_manifest_matches_supported_contract and generated Python, TypeScript, Java and Go build checks.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0418 — Must**

The system shall publish clients with version compatibility metadata and retry or pagination helpers.

_Verification:_ tests/test_sdk_contracts.py::test_urs_f_0417_0418_generated_sdk_manifest_matches_supported_contract and test_urs_f_0418_sdk_release_archives_are_reproducible.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0419 — Must**

The system shall store credentials using operating-system secure storage when available.

_Verification:_ tests/test_cli_epic402.py::test_urs_f_0414_0415_0419_0420_profiles_secure_tokens_and_output_modes.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0420 — Must**

The system shall support non-interactive service-account authentication in CI.

_Verification:_ tests/test_cli_epic402.py::test_urs_f_0414_0415_0419_0420_profiles_secure_tokens_and_output_modes and deployed AMESH_SERVICE_ACCOUNT_TOKEN CLI smoke.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0421 — Must**

The system shall provide shell completion and command documentation generated from the command model.

_Verification:_ tests/test_cli_epic402.py::test_urs_f_0421_completion_and_docs_are_generated_from_parser and docs/cli/reference.md freshness check.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-403 — Authentication session and credential entry points

Provide secure local and federated entry points while keeping authorization separate.

**URS-F-0422 — Must**

The system shall support secure local administrator bootstrap without shipping universal default credentials.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0423 — Must**

The system shall support browser sessions with secure cookies, CSRF protection, rotation, inactivity and absolute expiry.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0424 — Must**

The system shall support bearer tokens for API and CLI clients with explicit audience and expiry.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0425 — Must**

The system shall apply account lockout, rate limiting and anomaly telemetry to authentication attempts.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0426 — Must**

The system shall support logout, global session revocation and credential rotation.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0427 — Must**

The system shall record authentication events without logging passwords, assertions or token material.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0428 — Must**

The system shall expose a provider-neutral authentication interface used by OIDC, SAML, LDAP and local modes.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0429 — Must**

The system shall disable local password authentication when policy requires federated-only access.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-404 — Web UI shell, navigation and accessibility

Provide a responsive, permission-aware and accessible web application for all platform personas.

**URS-F-0430 — Must**

The system shall provide consistent navigation for dashboards, flows, executions, namespaces, assets, apps, plugins and administration.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0431 — Must**

The system shall hide or disable actions based on server-authoritative permissions without relying on UI checks for enforcement.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0432 — Must**

The system shall support deep links, browser history, saved views and tenant or namespace context.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0433 — Must**

The system shall meet WCAG 2.2 AA for keyboard access, focus, semantics, contrast and assistive technology in GA scope.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0434 — Must**

The system shall support responsive desktop and tablet layouts and a documented browser support policy.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0435 — Must**

The system shall provide global search, command palette, notifications and error recovery.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0436 — Must**

The system shall internationalize user-visible strings and locale-sensitive dates, numbers and time zones.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0437 — Must**

The system shall collect opt-in product telemetry only under explicit deployment policy.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-405 — Flow code editor and validation experience

Offer a productive schema-aware editor for the declarative flow language.

**URS-F-0438 — Must**

The system shall edit YAML with syntax highlighting, folding, formatting, search and multi-cursor support.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0439 — Must**

The system shall provide schema-driven completion for core and installed plugin properties.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0440 — Must**

The system shall show validation errors, warnings and documentation at exact source ranges.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0441 — Must**

The system shall preview expression evaluation using a safe redacted sample context.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0442 — Must**

The system shall diff current edits against active and historical revisions.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0443 — Must**

The system shall preserve drafts locally and warn before navigating away from unsaved changes.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0444 — Must**

The system shall validate and save through server APIs so client and server rules cannot diverge.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0445 — Must**

The system shall support import, export, clone, disable and revision restore operations.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-406 — Visual no-code editor and topology model

Author and understand workflows visually without creating a second incompatible representation.

**URS-F-0446 — Must**

The system shall render the canonical flow model as an interactive task and dependency graph.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0447 — Must**

The system shall add, configure, connect, reorder, group and remove supported tasks through schema-generated forms.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0448 — Must**

The system shall round-trip supported visual edits to YAML without changing unrelated semantic content.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0449 — Must**

The system shall fall back to code editing for constructs the visual editor cannot represent.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0450 — Must**

The system shall show conditions, retries, timeouts, concurrency, handlers and subflows in topology.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0451 — Must**

The system shall validate graph cycles, missing references and incompatible connections before save.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0452 — Must**

The system shall support zoom, pan, keyboard navigation, minimap and large-graph performance.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0453 — Must**

The system shall mark generated or lossy transformations before the user accepts them.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-407 — Execution details, Gantt, logs and debugging UI

Help users diagnose execution behavior from one coherent timeline.

**URS-F-0454 — Must**

The system shall show execution identity, revision, inputs, labels, state history, duration, trigger and parent-child relationships.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0455 — Must**

The system shall render task runs as topology and Gantt views with attempts, queues, waits and runner duration.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0456 — Must**

The system shall stream and filter logs by task, attempt, level, worker, time and text.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0457 — Must**

The system shall show rendered inputs, outputs, metrics, artifacts, errors and cache decisions subject to authorization.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0458 — Must**

The system shall offer pause, resume, cancel, kill, restart, replay and backfill actions with impact confirmation.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0459 — Must**

The system shall link each state transition to its causative event and actor where available.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0460 — Must**

The system shall retain the user's filters and selected task in shareable deep links.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0461 — Must**

The system shall remain usable for executions with tens of thousands of task runs through virtualization and aggregation.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-408 — Dashboards, query language and saved views

Create operational and business views from execution, log, metric, SLA and asset data.

**URS-F-0462 — Must**

The system shall provide built-in instance, tenant, namespace, flow, worker and SLA dashboards.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0463 — Must**

The system shall support time series, tables, counters, distributions, status breakdowns and ranked lists.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0464 — Must**

The system shall define dashboard queries through a typed restricted query model rather than arbitrary database SQL.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0465 — Must**

The system shall filter by time, labels, namespace, flow, state, worker group and custom dimensions.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0466 — Must**

The system shall save, share, export and permission dashboards independently from underlying data.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0467 — Must**

The system shall apply query limits, timeouts, sampling and aggregation to protect operational workloads.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0468 — Must**

The system shall show query freshness, partial-result and permission-redaction indicators.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0469 — Must**

The system shall allow custom dashboard definitions to be managed through API and GitOps.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-409 — Search, indexing and retrieval projections

Find flows, executions, logs, assets and governance records quickly without making the search index authoritative.

**URS-F-0470 — Must**

The system shall index authorized metadata and selected log fields into a replaceable search projection.

_Verification:_ Projection rebuild, isolation and query contract tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0471 — Must**

The system shall support full-text, field, range, state, label, namespace and time filters.

_Verification:_ Projection rebuild, isolation and query contract tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0472 — Must**

The system shall return stable pagination and relevance or field sorting.

_Verification:_ Projection rebuild, isolation and query contract tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0473 — Must**

The system shall rebuild indexes from authoritative repositories and event history.

_Verification:_ Projection rebuild, isolation and query contract tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0474 — Must**

The system shall continue writes and orchestration during search backend degradation.

_Verification:_ Projection rebuild, isolation and query contract tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0475 — Must**

The system shall prevent cross-tenant leakage in both indexed documents and query execution.

_Verification:_ Projection rebuild, isolation and query contract tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0476 — Must**

The system shall expose index lag, failures, version and rebuild progress.

_Verification:_ Projection rebuild, isolation and query contract tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0477 — Must**

The system shall provide PostgreSQL full-text, trigram and structured search over rebuildable tenant-scoped projections.

_Verification:_ Projection rebuild, isolation and query contract tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-410 — Namespace, settings and administration UI

Administer resources and platform configuration without direct database or file access.

**URS-F-0478 — Must**

The system shall browse namespace hierarchy, inherited settings, files, key-values, secrets metadata and plugin defaults.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0479 — Must**

The system shall manage users, groups, roles, bindings, service accounts, tokens and identity providers according to permissions.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0480 — Must**

The system shall view workers, services, queues, storage, search, migrations and component health.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0481 — Must**

The system shall manage retention, announcements, maintenance, kill switches and feature flags.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0482 — Must**

The system shall display effective configuration and provenance while redacting secrets.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0483 — Must**

The system shall require reauthentication or step-up approval for high-risk administrative operations.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0484 — Must**

The system shall provide dry-run and impact previews for bulk or destructive changes.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0485 — Must**

The system shall record every successful and rejected administrative action in audit history.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-411 — Blueprints, playground and onboarding

Help users learn and start workflows without weakening production controls.

**URS-F-0486 — Must**

The system shall provide versioned blueprint templates with parameters, documentation, license and provenance.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0487 — Must**

The system shall search and preview built-in, organization and community blueprint catalogs.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0488 — Must**

The system shall instantiate a blueprint into a draft flow without executing it automatically.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0489 — Must**

The system shall provide a playground that validates and simulates supported expressions and flow fragments.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0490 — Must**

The system shall isolate playground execution from production credentials and infrastructure by default.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0491 — Must**

The system shall guide first-time administrators through storage, database, runner and authentication readiness.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0492 — Must**

The system shall provide sample data and local-only examples that run in the reference Compose environment.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0493 — Must**

The system shall track onboarding completion locally without requiring external telemetry.

_Verification:_ Automated browser, accessibility and manual usability tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

### M5 — Open governance and enterprise-class controls

Exit condition: Identity, tenancy, policy, audit, secrets, approvals and lineage are production-ready and fully OSS.

#### EPIC-500 — Users, groups, roles, bindings and authorization

Enforce fine-grained least-privilege access consistently across every platform resource and action.

**URS-F-0494 — Must**

The system shall define permissions by resource type and action including view, create, update, delete, execute, manage and use.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0495 — Must**

The system shall bind roles to users, groups and service accounts at instance, tenant and namespace scopes.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0496 — Must**

The system shall inherit namespace permissions predictably with explicit deny or boundary behavior.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0497 — Must**

The system shall evaluate authorization server-side for REST, realtime, CLI, UI, worker and plugin-originated requests.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0498 — Must**

The system shall cache decisions safely without retaining access after binding or group revocation.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0499 — Must**

The system shall explain authorization decisions to administrators without revealing inaccessible resource details.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0500 — Must**

The system shall provide built-in least-privilege roles and prevent accidental removal of all administrators.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0501 — Must**

The system shall test every public endpoint and event stream for tenant and permission isolation.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-501 — Service accounts, API tokens and credentials

Support non-human automation identities with scoped, rotatable and observable credentials.

**URS-F-0502 — Must**

The system shall create service accounts with roles, groups, tenant and namespace bindings.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0503 — Must**

The system shall issue hashed or asymmetric API tokens with name, scopes, audience, expiry and last-used metadata.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0504 — Must**

The system shall show token material only once and support rotation with an overlap period.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0505 — Must**

The system shall revoke tokens, sessions and derived credentials immediately across components.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0506 — Must**

The system shall support workload identity and short-lived token exchange for workers and plugins.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0507 — Must**

The system shall apply independent quotas and rate limits to automation identities.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0508 — Must**

The system shall record token creation, use, failure, rotation and revocation without storing token plaintext.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0509 — Must**

The system shall prevent service accounts from interactive login unless explicitly supported by policy.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-502 — SSO, OIDC, SAML, LDAP and SCIM

Integrate enterprise identity providers using open standards and auditable mapping.

**URS-F-0510 — Must**

The system shall support OpenID Connect authorization-code flow with PKCE and configurable claims.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0511 — Must**

The system shall support SAML 2.0 service-provider flows with signed assertions and metadata rotation.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0512 — Must**

The system shall support LDAP or Active Directory authentication and group lookup over TLS.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0513 — Must**

The system shall support SCIM 2.0 user and group provisioning, update, disable and deprovision operations.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0514 — Must**

The system shall map identity-provider claims or groups to platform groups and tenant access through explicit rules.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0515 — Must**

The system shall prevent account takeover through ambiguous email, subject or provider linking.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0516 — Must**

The system shall test signing-key rotation, clock skew, replay, logout and provider outage behavior.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0517 — Must**

The system shall allow multiple identity providers with domain or tenant routing policy.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-503 — Multi-tenancy and resource isolation

Host multiple organizations or environments with strong logical isolation and independent administration.

**URS-F-0518 — Must**

The system shall scope every resource, query, message, cache entry, artifact and audit event to an explicit tenant.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0519 — Must**

The system shall require tenant context at service boundaries and reject implicit fallback outside single-tenant mode.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0520 — Must**

The system shall support tenant creation, suspension, deletion, export and restoration workflows.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0521 — Must**

The system shall apply tenant-specific quotas, retention, encryption, identity providers, plugins and feature flags.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0522 — Must**

The system shall prevent identifiers, timing, search, metrics, logs and error messages from leaking cross-tenant information.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0523 — Must**

The system shall support tenant-aware worker groups and storage prefixes or buckets.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0524 — Must**

The system shall let super-administrators operate across tenants with separately audited privileges.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0525 — Must**

The system shall prove isolation with adversarial automated tests and database policy checks.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-504 — Immutable audit log and evidence export

Record security and administrative actions as tamper-evident, queryable evidence.

**URS-F-0526 — Must**

The system shall audit authentication, authorization, resource mutation, execution intervention, secret use, policy decision and administration events.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0527 — Must**

The system shall include actor, delegated identity, tenant, resource, action, outcome, reason, source, timestamp, correlation and trace identifiers.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0528 — Must**

The system shall redact protected values while retaining enough metadata for investigation.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0529 — Must**

The system shall write audit events transactionally with the associated state change where possible.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0530 — Must**

The system shall detect gaps or tampering through append-only storage, hash chaining or signed export batches.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0531 — Must**

The system shall apply independent audit retention and legal-hold policy.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0532 — Must**

The system shall export audit events to files, object storage and external security information systems.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0533 — Must**

The system shall restrict audit access and audit access to the audit log itself.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0835 — Must**

The system shall generate scoped compliance evidence packages containing access reviews, change evidence, audit records, backup and restore evidence, vulnerability results, incident records and provenance without exposing protected values.

_Verification:_ Compliance evidence export, redaction and authorization tests.
_Source scope:_ AMESH compliance-readiness decision; not a certification claim.

#### EPIC-505 — Plugin allow, restrict and version policy

Control which plugin capabilities and versions may be authored or executed in each scope.

**URS-F-0534 — Must**

The system shall allow or deny plugin packages, types, versions, vendors and capabilities at instance, tenant and namespace scopes.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0535 — Must**

The system shall distinguish authoring, validation, execution and administration permissions for plugins.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0536 — Must**

The system shall freeze approved plugin versions and prevent unreviewed automatic upgrades.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0537 — Must**

The system shall evaluate policy when saving a flow and again when starting an execution.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0538 — Must**

The system shall quarantine vulnerable, revoked or compromised plugin versions while preserving historical metadata.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0539 — Must**

The system shall show the effective policy and source of every decision.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0540 — Must**

The system shall support emergency disable with an impact preview of affected flows and running executions.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0541 — Must**

The system shall record policy changes and violations in audit history.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-506 — External secrets managers and secret lifecycle

Resolve secrets from approved stores without making the orchestration database a plaintext vault.

**URS-F-0542 — Must**

The system shall define a provider-neutral secret reference and lookup interface.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0543 — Must**

The system shall support environment or file development secrets and at least three production secret-manager adapters before GA.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0544 — Must**

The system shall resolve secrets just in time for an authorized task, trigger, runner or plugin call.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0545 — Must**

The system shall cache secret values only in protected memory for a bounded duration and support forced invalidation.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0546 — Must**

The system shall support version pinning, rotation, missing-secret behavior and provider failover policy.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0547 — Must**

The system shall prevent secret values from entering events, logs, errors, metrics, outputs, caches or UI previews.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0548 — Must**

The system shall audit secret metadata access and use without recording the value.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0549 — Must**

The system shall apply namespace and tenant permissions independently from provider-side permissions.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-507 — Assets, lineage and catalog

Represent data and infrastructure assets and their relationship to workflows and executions.

**URS-F-0550 — Must**

The system shall register assets from explicit declarations and plugin-emitted read or write events.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0551 — Must**

The system shall identify assets by provider, account, location, type and stable external key.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0552 — Must**

The system shall link assets to producing and consuming flows, task runs, executions and artifacts.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0553 — Must**

The system shall display upstream, downstream, last materialization, health and ownership metadata.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0554 — Must**

The system shall support custom metadata, tags, descriptions, contacts and domain grouping.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0555 — Must**

The system shall record lineage confidence and distinguish declared, observed and inferred edges.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0556 — Must**

The system shall apply tenant and namespace permissions to asset visibility and lineage traversal.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0557 — Must**

The system shall export catalog and lineage through API and open interchange formats where practical.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-508 — Apps, forms and human approval tasks

Build governed human-in-the-loop experiences on top of durable workflows.

**URS-F-0558 — Must**

The system shall define versioned apps with forms, validation, display, permissions and flow launch behavior.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0559 — Must**

The system shall generate forms from flow inputs while allowing explicit layout and help text.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0560 — Must**

The system shall create durable approval tasks with assignees, groups, deadlines, escalation and delegation.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0561 — Must**

The system shall support approve, reject, request changes, comment and attach artifact actions.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0562 — Must**

The system shall resume waiting workflows exactly once after an authorized decision.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0563 — Must**

The system shall record decision identity, time, reason and form values in audit and execution history.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0564 — Must**

The system shall notify participants without exposing inaccessible execution data.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0565 — Must**

The system shall provide embeddable or linkable app views protected by the same authorization model.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-509 — Announcements, maintenance mode and kill switch

Control instance-wide operational posture during incidents and planned maintenance.

**URS-F-0566 — Must**

The system shall publish scheduled and immediate announcements with severity, audience and expiry.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0567 — Must**

The system shall enter maintenance modes that separately control authoring, new executions, triggers, API writes and worker dispatch.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0568 — Must**

The system shall activate tenant, namespace, flow, plugin, runner or instance kill switches.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0569 — Must**

The system shall define behavior for already-running work when a switch is activated.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0570 — Must**

The system shall require reason, actor, expiry or review for emergency controls.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0571 — Must**

The system shall propagate control changes rapidly to all components and expose acknowledgement status.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0572 — Must**

The system shall automatically expire temporary controls where configured.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0573 — Must**

The system shall audit activation, extension, bypass and deactivation events.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-510 — Flow unit tests and quality gates

Test workflow behavior deterministically before deployment or promotion.

**URS-F-0574 — Must**

The system shall define tests with a flow revision, inputs, variables, mocked tasks or plugins and expected states or outputs.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0575 — Must**

The system shall simulate expressions, branches, retries, handlers and generated task graphs without external side effects.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0576 — Must**

The system shall run selected tests through API, CLI, UI and CI with machine-readable results.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0577 — Must**

The system shall provide plugin fixtures and recorded responses for external integrations.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0578 — Must**

The system shall measure covered tasks, branches, handlers and conditions without claiming full semantic proof.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0579 — Must**

The system shall require passing tests through namespace promotion or policy gates.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0580 — Must**

The system shall pin test results to flow revision, plugin set and simulator version.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0581 — Must**

The system shall isolate test data, secrets, artifacts and executions from production by default.

_Verification:_ Authorization, audit and administrative end-to-end tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

### M6 — Distributed operations and reliability

Exit condition: The platform scales horizontally, is observable, upgradeable, recoverable and security-hardened.

#### EPIC-600 — Standalone server and compact deployment

Run the complete platform on one host or small cluster with minimal dependencies.

**URS-F-0582 — Must**

The system shall start webserver, executor, scheduler, worker and maintenance roles in one process or one deployment.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0583 — Must**

The system shall use PostgreSQL for authoritative state and compact queueing in the reference mode.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0584 — Must**

The system shall use local or S3-compatible object storage through configuration.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0585 — Must**

The system shall provide Docker, Docker Compose and native binary or package installation paths.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0586 — Must**

The system shall perform startup preflight checks for database, storage, configuration, migrations and required credentials.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0587 — Must**

The system shall expose readiness separately from liveness and include degraded dependency states.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0588 — Must**

The system shall support graceful shutdown that stops admission, drains work and checkpoints owned triggers.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0589 — Must**

The system shall document minimum and recommended resources for development and production.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-601 — Distributed services and high availability

Scale platform roles independently and survive ordinary node or zone failures.

**URS-F-0590 — Must**

The system shall run webserver, executor, scheduler, worker, indexer and maintenance roles as independent scalable services.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0591 — Must**

The system shall assign partitioned work through durable messages, leases and fencing rather than node affinity.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0592 — Must**

The system shall continue orchestration through the loss and replacement of any stateless service instance.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0593 — Must**

The system shall support multiple replicas across failure zones with documented quorum dependencies.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0594 — Must**

The system shall drain, upgrade and replace instances without losing accepted work.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0595 — Must**

The system shall expose service registry, version skew, ownership, partition and failover status.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0596 — Must**

The system shall detect split-brain or stale ownership and reject unfenced mutations.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0597 — Must**

The system shall publish tested reference topologies for small, medium and large deployments.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-602 — PostgreSQL transactional backend

Provide a production-grade PostgreSQL backend for compact and horizontally scaled deployments.

**URS-F-0598 — Must**

The system shall support current supported PostgreSQL major versions under an explicit compatibility matrix.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0599 — Must**

The system shall use connection pools, prepared statements, indexes and partitioning appropriate to execution workloads.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0600 — Must**

The system shall implement queue claims, locks and scheduler ownership without long blocking transactions.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0601 — Must**

The system shall support read replicas only for explicitly stale-tolerant queries.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0602 — Must**

The system shall provide maintenance for table bloat, partitions, statistics and high-volume event retention.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0603 — Must**

The system shall test managed PostgreSQL services and TLS configurations across major cloud providers.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0604 — Must**

The system shall publish query plans and benchmark thresholds for critical operations.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0605 — Must**

The system shall support backup-consistent object-storage metadata and point-in-time recovery procedures.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-603 — PostgreSQL distributed work queue and notifications

Scale durable orchestration using partitioned PostgreSQL queues, notifications, leases and dead-letter workflows without an external broker.

**URS-F-0606 — Must**

The system shall implement the internal messaging abstraction entirely on PostgreSQL using durable queue, outbox, inbox and lease records.

_Verification:_ PostgreSQL delivery, ordering, duplicate, failover and saturation conformance tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0607 — Must**

The system shall shard and claim work by tenant and execution or trigger partition key while preserving required per-partition ordering.

_Verification:_ PostgreSQL delivery, ordering, duplicate, failover and saturation conformance tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0608 — Must**

The system shall support independent consumer lanes, replay, retention, dead-letter and poison-message workflows on PostgreSQL.

_Verification:_ PostgreSQL delivery, ordering, duplicate, failover and saturation conformance tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0609 — Must**

The system shall propagate trace context and message schema version through every durable queue envelope.

_Verification:_ PostgreSQL delivery, ordering, duplicate, failover and saturation conformance tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0610 — Must**

The system shall manage queue schema compatibility and rolling producer or consumer upgrades without losing committed work.

_Verification:_ PostgreSQL delivery, ordering, duplicate, failover and saturation conformance tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0611 — Must**

The system shall surface shard skew, oldest eligible age, lease expiry, redelivery, throughput, transaction latency and PostgreSQL health.

_Verification:_ PostgreSQL delivery, ordering, duplicate, failover and saturation conformance tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0612 — Must**

The system shall recover from PostgreSQL failover or connection loss without losing committed outbox or queue records.

_Verification:_ PostgreSQL delivery, ordering, duplicate, failover and saturation conformance tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0613 — Must**

The system shall document and benchmark semantic and capacity differences between single-host and horizontally scaled PostgreSQL queue profiles.

_Verification:_ PostgreSQL delivery, ordering, duplicate, failover and saturation conformance tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-604 — Search and analytics projection backend

Scale read-heavy UI, log and analytics queries through rebuildable PostgreSQL projections, partitions and rollups.

**URS-F-0614 — Must**

The system shall project committed flow, execution, task-run, log, metric, asset and audit events into tenant-scoped PostgreSQL projection tables.

_Verification:_ PostgreSQL projection rebuild, isolation, retention and query-load tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0615 — Must**

The system shall version projection schemas, indexes, materialized views and rollups to support low-downtime rebuilds.

_Verification:_ PostgreSQL projection rebuild, isolation, retention and query-load tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0616 — Must**

The system shall resume projection from durable event positions after projector failure.

_Verification:_ PostgreSQL projection rebuild, isolation, retention and query-load tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0617 — Must**

The system shall rebuild selected tenants, resource types or time ranges without stopping orchestration.

_Verification:_ PostgreSQL projection rebuild, isolation, retention and query-load tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0618 — Must**

The system shall verify projected row counts, checksums and checkpoints against authoritative repositories.

_Verification:_ PostgreSQL projection rebuild, isolation, retention and query-load tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0619 — Must**

The system shall enforce tenant isolation during projection construction and every search or analytics query.

_Verification:_ PostgreSQL projection rebuild, isolation, retention and query-load tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0620 — Must**

The system shall partition, archive and expire projected data consistently with source retention policy.

_Verification:_ PostgreSQL projection rebuild, isolation, retention and query-load tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

**URS-F-0621 — Must**

The system shall support disabling or rebuilding projections and falling back to bounded authoritative queries where feasible.

_Verification:_ PostgreSQL projection rebuild, isolation, retention and query-load tests.
_Source scope:_ Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation.

#### EPIC-605 — Object storage backends and lifecycle

Operate internal storage reliably across local and cloud object stores.

**URS-F-0622 — Must**

The system shall support S3-compatible, Azure Blob and Google Cloud Storage backends.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0623 — Must**

The system shall use tenant-aware prefixes or containers and configurable encryption keys.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0624 — Must**

The system shall support proxy, private endpoint, custom certificate authority and workload identity configurations.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0625 — Must**

The system shall verify read-after-write assumptions and compensate for backend-specific consistency behavior.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0626 — Must**

The system shall apply retention, lifecycle, legal hold and deletion markers without orphaning referenced artifacts.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0627 — Must**

The system shall support migration between storage backends with checksum verification and resumability.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0628 — Must**

The system shall publish storage usage, request, latency, error and corruption metrics.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0629 — Must**

The system shall include storage data in backup, restore and disaster-recovery validation.

_Verification:_ Repository or storage adapter contract and fault-injection tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-606 — Containers, Kubernetes and Helm deployment

Provide secure, portable and air-gapped-capable deployment artifacts for the on-premises Kubernetes reference environment.

**URS-F-0630 — Must**

The system shall publish minimal multi-architecture container images with non-root defaults and immutable tags.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0631 — Must**

The system shall provide a Helm chart for standalone and distributed role topologies.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0632 — Must**

The system shall configure probes, disruption budgets, autoscaling, affinity, topology spread, resources and security contexts.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0633 — Must**

The system shall support external PostgreSQL, object storage, ingress, identity, secret and certificate integrations required by the selected deployment profile.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0634 — Must**

The system shall avoid embedding default production secrets and support external secret injection.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0635 — Must**

The system shall validate chart installation, upgrade and failure recovery against the documented on-premises Kubernetes reference topology and at least one additional portable Kubernetes distribution in CI or scheduled qualification.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0636 — Must**

The system shall provide network-policy examples that separate control plane, workers and user infrastructure.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0637 — Must**

The system shall publish values schema, migration notes and generated reference documentation.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0826 — Must**

The system shall provide an on-premises Kubernetes reference deployment with no mandatory public-cloud control plane, managed database, managed object store, hosted telemetry service or license server.

_Verification:_ On-premises Kubernetes installation, upgrade and failure-recovery tests.
_Source scope:_ AMESH deployment decision; not a Kestra-parity claim.

**URS-F-0827 — Must**

The system shall support disconnected installation and upgrade from a signed offline bundle containing images, Helm charts, custom-resource definitions, migrations, SBOMs, provenance and operator documentation.

_Verification:_ Air-gapped bundle installation and upgrade tests.
_Source scope:_ AMESH deployment decision; not a Kestra-parity claim.

**URS-F-0828 — Must**

The system shall validate the reference Helm deployment against upstream Kubernetes and at least one common on-premises distribution using external PostgreSQL and S3-compatible storage.

_Verification:_ Cross-distribution Kubernetes conformance and upgrade tests.
_Source scope:_ AMESH deployment decision; not a Kestra-parity claim.

#### EPIC-607 — OpenTelemetry, Prometheus and log shipping

Expose actionable telemetry without coupling the platform to one vendor.

**URS-F-0638 — Must**

The system shall instrument API, scheduler, executor, worker, storage, messaging, plugin and runner operations with OpenTelemetry.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0639 — Must**

The system shall propagate trace context through commands, events, messages, tasks, subflows and outbound plugin calls.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0640 — Must**

The system shall publish Prometheus-compatible metrics with bounded cardinality and documented labels.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0641 — Must**

The system shall emit structured application logs with component, tenant-safe correlation and version metadata.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0642 — Must**

The system shall support configurable log shipping to standard external destinations.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0643 — Must**

The system shall provide default dashboards and alerts for availability, latency, saturation, failures, lag and stuck work.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0644 — Must**

The system shall redact sensitive values before telemetry export.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0645 — Must**

The system shall continue core operation when telemetry collectors or exporters are unavailable.

_Verification:_ Telemetry contract and outage tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-608 — Retention, purge and data lifecycle

Control metadata, logs, metrics, artifacts and audit growth safely.

**URS-F-0646 — Must**

The system shall define retention by resource type at instance, tenant, namespace and label scopes.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0647 — Must**

The system shall preview affected record and byte counts before purge.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0648 — Must**

The system shall purge in bounded resumable batches that do not block active orchestration.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0649 — Must**

The system shall preserve referential integrity across executions, task runs, events, logs, metrics, artifacts, caches and indexes.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0650 — Must**

The system shall honor legal holds and independent audit-retention requirements.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0651 — Must**

The system shall delete object storage and search projections only after authoritative metadata decisions.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0652 — Must**

The system shall record purge job progress, failures, retries and evidence.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0653 — Must**

The system shall support manual purge and scheduled lifecycle policies.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-609 — Backup, restore and disaster recovery

Restore a consistent platform state after data loss or regional failure.

**URS-F-0654 — Must**

The system shall document coordinated backup points for PostgreSQL metadata, queues and projections, object storage and configuration.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0655 — Must**

The system shall automate backup verification through isolated restore tests.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0656 — Must**

The system shall support PostgreSQL point-in-time recovery and object-version-aware restoration.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0657 — Must**

The system shall rebuild disposable search and analytics projections from authoritative sources.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0658 — Must**

The system shall detect and reconcile messages, leases and worker state after restoration.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0659 — Must**

The system shall provide tenant-scoped export and import where isolation permits.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0660 — Must**

The system shall publish reference recovery time and recovery point procedures with measured evidence.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0661 — Must**

The system shall run scheduled disaster-recovery exercises and record unresolved gaps.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-610 — Upgrades, migrations and LTS policy

Upgrade the platform predictably without silently changing workflow behavior.

**URS-F-0662 — Must**

The system shall publish supported upgrade paths, LTS windows and minimum compatible component versions.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0663 — Must**

The system shall run pre-upgrade checks for schema, configuration, plugins, flow syntax, storage and capacity.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0664 — Must**

The system shall support rolling upgrades where message and database compatibility permits.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0665 — Must**

The system shall block unsafe version skew and explain the required remediation.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0666 — Must**

The system shall upcast persisted events and migrate flow or plugin configuration through explicit tools.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0667 — Must**

The system shall retain a rollback window or provide restoration guidance for irreversible migrations.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0668 — Must**

The system shall test upgrades from every supported LTS release with representative workloads.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0669 — Must**

The system shall produce a post-upgrade verification report and unresolved compatibility warnings.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-611 — Performance, scale and chaos qualification

Qualify correctness, performance and recovery under profile M load and adversarial failures on the on-premises Kubernetes reference topology.

**URS-F-0670 — Must**

The system shall maintain reproducible benchmarks for flow creation, execution launch, task dispatch, scheduling, logs, search and UI queries.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0671 — Must**

The system shall measure throughput and latency at small, medium and large reference scales.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0672 — Must**

The system shall publish hardware, topology, dataset and configuration with every benchmark result.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0673 — Must**

The system shall load-test multi-tenant fairness, backfills, large DAGs, high log volume and plugin-heavy workloads.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0674 — Must**

The system shall inject process, node, PostgreSQL, object-storage, network, runner and plugin failures.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0675 — Must**

The system shall assert no accepted command is lost and no stale owner can commit after fencing.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0676 — Must**

The system shall track performance regressions and require explicit approval beyond defined budgets.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0677 — Must**

The system shall provide capacity-planning guidance from benchmark and telemetry evidence.

_Verification:_ Fault-injection, replay and invariant tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-612 — Security hardening and software supply chain

Reduce platform and workload attack surface and produce verifiable release artifacts.

**URS-F-0678 — Must**

The system shall maintain a threat model covering control plane, workers, runners, plugins, storage, identity, UI and supply chain.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0679 — Must**

The system shall run static analysis, dependency scanning, secret scanning, container scanning and dynamic security tests.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0680 — Must**

The system shall generate SBOMs and signed provenance for source, binaries, containers, charts and plugin bundles.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0681 — Must**

The system shall use least-privilege service identities and short-lived credentials between components.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0682 — Must**

The system shall apply secure defaults for headers, cookies, TLS, filesystem permissions, network and deserialization.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0683 — Must**

The system shall provide vulnerability disclosure, security advisory and patch support procedures.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0684 — Must**

The system shall perform independent penetration testing before GA and after material security changes.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0685 — Must**

The system shall document residual risks for in-process plugins, local process runners and administrative capabilities.

_Verification:_ Security integration tests and threat-model review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0834 — Must**

The system shall maintain a versioned machine-readable crosswalk from applicable SOC 2 Trust Services Criteria and ISO/IEC 27001 controls to owners, requirements, implementations, tests, evidence sources and recorded gaps.

_Verification:_ Compliance control-crosswalk schema and completeness tests.
_Source scope:_ AMESH compliance-readiness decision; not a certification claim.

#### EPIC-613 — TLS, networking, proxy and private connectivity

Operate across enterprise networks without weakening transport or destination controls.

**URS-F-0686 — Must**

The system shall support inbound TLS termination directly or through a trusted reverse proxy.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0687 — Must**

The system shall support mutual TLS between selected internal components and workers.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0688 — Must**

The system shall support custom certificate authorities and certificate rotation without full service outage.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0689 — Must**

The system shall support HTTP or HTTPS proxies and explicit no-proxy destinations.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0690 — Must**

The system shall validate forwarded headers and trusted proxy ranges before constructing external URLs.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0691 — Must**

The system shall provide egress allowlists and DNS or IP protections for plugins and HTTP tasks.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0692 — Must**

The system shall support private endpoints and split control-plane or worker network topologies.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0693 — Must**

The system shall expose connection, certificate, proxy and DNS diagnostics without leaking credentials.

_Verification:_ Reference deployment, upgrade and failure-recovery tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

### M7 — Compatibility, infrastructure as code and ecosystem

Exit condition: Migration tooling, SDKs, GitOps, Terraform, operator and documentation support adoption.

#### EPIC-700 — Git synchronization and CI/CD helpers

Manage workflow resources through source control and automated promotion.

**URS-F-0694 — Must**

The system shall export canonical flows, namespace files, dashboards, apps, tests and policy resources to repository-friendly files.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0695 — Must**

The system shall apply creates, updates, deletes and moves from Git commits with dry-run and conflict detection.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0696 — Must**

The system shall support one-way Git-to-platform synchronization as the safe default.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0697 — Must**

The system shall link deployed revisions to repository, commit, actor, pipeline and environment metadata.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0698 — Must**

The system shall provide CI helpers for validate, test, diff, plan, apply and deployment status.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0699 — Must**

The system shall support GitHub, GitLab, Bitbucket and generic Git providers through adapters.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0700 — Must**

The system shall prevent sync loops and protect UI edits according to declared ownership mode.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0701 — Must**

The system shall sign or verify deployment provenance where the Git provider supports it.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-701 — Terraform and OpenTofu provider

Manage platform configuration declaratively through standard infrastructure-as-code tooling.

**URS-F-0702 — Must**

The system shall provide resources and data sources for flows, namespaces, files, key-values, dashboards, apps, users, groups, roles, bindings, service accounts, tenants, worker groups and plugin policies.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0703 — Must**

The system shall implement import, refresh, plan, apply and drift detection with stable identifiers.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0704 — Must**

The system shall treat secret values as sensitive and avoid returning provider-resolved plaintext.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0705 — Must**

The system shall support YAML file content and semantic diff suppression where safe.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0706 — Must**

The system shall generate provider documentation and examples from schemas.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0707 — Must**

The system shall test provider compatibility against supported platform releases.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0708 — Must**

The system shall publish signed provider binaries for major operating systems and architectures.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0709 — Must**

The system shall define behavior for server-managed defaults and immutable fields.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-702 — Kubernetes operator and declarative resources

Reconcile platform resources from Kubernetes custom resources when Kubernetes is the control environment.

**URS-F-0710 — Must**

The system shall define custom resources for flows, namespaces, files, key-values, dashboards, apps and selected governance resources.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0711 — Must**

The system shall reconcile desired state through server APIs with status conditions and observed generation.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0712 — Must**

The system shall support finalizers, deletion policy, retry, backoff and drift detection.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0713 — Must**

The system shall read credentials from Kubernetes Secrets without copying them into status.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0714 — Must**

The system shall scope watches and server credentials for multi-cluster or multi-tenant operation.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0715 — Must**

The system shall emit Kubernetes events and metrics for reconciliation outcomes.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0716 — Must**

The system shall version custom-resource schemas and provide conversion or migration guidance.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0717 — Must**

The system shall avoid making Kubernetes etcd authoritative for execution runtime state.

_Verification:_ Declarative apply, drift and CI integration tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-703 — Public SDKs and embedded integration libraries

Integrate the orchestrator into applications using supported language libraries.

**URS-F-0718 — Must**

The system shall publish supported SDKs for Python, JavaScript or TypeScript, Java and Go.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0719 — Must**

The system shall provide typed models, authentication, retries, idempotency, pagination, streaming and error helpers.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0720 — Must**

The system shall support execution launch, monitoring, cancellation, logs, artifacts and webhook verification.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0721 — Must**

The system shall maintain semantic-version compatibility aligned with API support policy.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0722 — Must**

The system shall generate most models from OpenAPI while hand-crafting ergonomic high-level operations.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0723 — Must**

The system shall publish examples for web applications, CLIs, CI systems and event consumers.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0724 — Must**

The system shall test SDKs against live conformance environments in the release qualification gate.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0725 — Must**

The system shall document thread safety, async support and transport customization.

_Verification:_ OpenAPI contract and authenticated end-to-end API tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-704 — Kestra migration importer and conformance suite

Provide version-pinned compatibility plus full side-by-side migration of resources, identity and governance configuration, execution history, logs, artifacts and audit evidence.

**URS-F-0726 — Must**

The system shall parse Kestra v1.3.30 flow YAML into a source-preserving compatibility model.

_Verification:_ Black-box differential and migration fixture tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0727 — Must**

The system shall map every declared Kestra core property, expression, flowable, trigger, retry, timeout, concurrency, error and output behavior for the pinned target.

_Verification:_ Black-box differential and migration fixture tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0728 — Must**

The system shall classify mappings as exact, compatibility-adapted or blocked; approximate mappings shall not satisfy a full-compatibility release claim.

_Verification:_ Black-box differential and migration fixture tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0729 — Must**

The system shall generate source-located migration patches or adapters without silently discarding or defaulting configuration.

_Verification:_ Black-box differential and migration fixture tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0730 — Must**

The system shall import and round-trip documented namespace files, key-values, labels, revisions, dashboards and export-bundle resources.

_Verification:_ Black-box differential and migration fixture tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0731 — Must**

The system shall run black-box differential scenarios against the pinned Kestra target and AMESH using non-destructive reference plugins.

_Verification:_ Black-box differential and migration fixture tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0732 — Must**

The system shall compare validation, state transitions, task graph, outputs, API payloads, CLI results, timing windows and failure behavior with explicit tolerances.

_Verification:_ Black-box differential and migration fixture tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0733 — Must**

The system shall support side-by-side shadow execution that suppresses, mocks or idempotently isolates external side effects.

_Verification:_ Black-box differential and migration fixture tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0820 — Must**

The system shall provide a version-pinned REST compatibility façade matching declared paths, methods, schemas, pagination, status codes and error classes.

_Verification:_ Black-box differential API, CLI, expression and import/export conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0821 — Must**

The system shall provide a version-pinned CLI compatibility mode matching declared commands, flags, exit codes and machine-readable output.

_Verification:_ Black-box differential API, CLI, expression and import/export conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0822 — Must**

The system shall match declared Pebble parsing, escaping, functions, filters, null behavior and error behavior through differential expression fixtures.

_Verification:_ Black-box differential API, CLI, expression and import/export conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0823 — Must**

The system shall import and export every documented bundle type in the declared compatibility surface without silent information loss.

_Verification:_ Black-box differential API, CLI, expression and import/export conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0824 — Must**

The system shall publish a machine-readable compatibility manifest naming the target version, tested surfaces, evidence and unresolved gaps.

_Verification:_ Black-box differential API, CLI, expression and import/export conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0825 — Must**

The system shall block a full-compatibility release claim when any Must surface remains approximate, unknown or untested.

_Verification:_ Black-box differential API, CLI, expression and import/export conformance tests.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0829 — Must**

The system shall import and export users, groups, roles, bindings, service accounts, tenants, namespaces, system configuration, plugin inventory and audit configuration through versioned migration bundles.

_Verification:_ Full-fidelity identity and governance migration fixtures.
_Source scope:_ AMESH full-migration decision applied to the pinned compatibility surface.

**URS-F-0830 — Must**

The system shall migrate historical executions, task runs, state events, logs, metrics, artifacts and audit evidence while preserving chronology, provenance and tenant boundaries.

_Verification:_ Historical execution, log, artifact and audit migration fixtures.
_Source scope:_ AMESH full-migration decision applied to the pinned compatibility surface.

**URS-F-0831 — Must**

The system shall generate a stable source-to-target identifier map and validate referential integrity across resources, revisions, executions, task runs, logs, artifacts and audit records.

_Verification:_ Identifier-mapping, collision and referential-integrity tests.
_Source scope:_ AMESH full-migration decision applied to the pinned compatibility surface.

**URS-F-0832 — Must**

The system shall perform migration as a dry-runnable, resumable and idempotent side-by-side process with checkpoints, checksums, reconciliation reports and an explicit cutover or rollback plan.

_Verification:_ Interrupted, repeated and rolled-back migration end-to-end tests.
_Source scope:_ AMESH full-migration decision applied to the pinned compatibility surface.

**URS-F-0833 — Must**

The system shall migrate secret references, provider metadata and required bindings without extracting secret plaintext, and shall block cutover when mandatory references remain unresolved.

_Verification:_ Secret-reference migration, redaction and unresolved-binding tests.
_Source scope:_ AMESH full-migration decision applied to the pinned compatibility surface.

#### EPIC-705 — Documentation, examples and community governance

Make the platform understandable, supportable and governable as a durable open-source project.

**URS-F-0734 — Must**

The system shall publish conceptual, tutorial, how-to, reference and operations documentation from versioned source.

_Verification:_ Documentation build and external contributor usability test.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0735 — Must**

The system shall document every public API, CLI command, configuration field, DSL construct and plugin interface.

_Verification:_ Documentation build and external contributor usability test.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0736 — Must**

The system shall provide runnable examples for data, infrastructure, software, approval and AI workflows.

_Verification:_ Documentation build and external contributor usability test.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0737 — Must**

The system shall maintain contribution, review, release, security, code-of-conduct and governance policies.

_Verification:_ Documentation build and external contributor usability test.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0738 — Must**

The system shall define maintainer roles, decision process, roadmap process and conflict resolution.

_Verification:_ Documentation build and external contributor usability test.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0739 — Must**

The system shall publish compatibility, support, deprecation and LTS matrices.

_Verification:_ Documentation build and external contributor usability test.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0740 — Must**

The system shall test documentation code samples and links in CI.

_Verification:_ Documentation build and external contributor usability test.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0741 — Must**

The system shall provide issue triage, discussion and plugin contribution templates.

_Verification:_ Documentation build and external contributor usability test.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

#### EPIC-706 — Reference integration environments and certification

Continuously test platform and plugin behavior against real services and deployment topologies.

**URS-F-0742 — Must**

The system shall maintain disposable integration environments for databases, queues, object stores, identity providers and Kubernetes.

_Verification:_ Release-gate evidence review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0743 — Must**

The system shall run nightly and release-candidate suites separately from fast pull-request tests.

_Verification:_ Release-gate evidence review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0744 — Must**

The system shall record service versions, configuration, test artifacts and flaky-test ownership.

_Verification:_ Release-gate evidence review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0745 — Must**

The system shall test upgrade, backup, restore, network partition, credential rotation and certificate rotation scenarios.

_Verification:_ Release-gate evidence review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0746 — Must**

The system shall provide public conformance results for certified plugins and reference deployments.

_Verification:_ Release-gate evidence review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0747 — Must**

The system shall protect integration credentials and isolate test tenants and cloud accounts.

_Verification:_ Release-gate evidence review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0748 — Must**

The system shall cap spend and clean up leaked resources automatically.

_Verification:_ Release-gate evidence review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

**URS-F-0749 — Must**

The system shall block GA releases on unresolved critical certification failures.

_Verification:_ Release-gate evidence review.
_Source scope:_ Kestra v1.3.30 public behavior and architecture parity baseline.

### M8 — Differentiation and general availability

Exit condition: Differentiating features and GA quality targets are proven under reference workloads.

#### EPIC-800 — Deterministic simulation and dry-run engine

Preview workflow behavior and policy impact without performing undeclared external side effects.

**URS-F-0750 — Must**

The system shall compile a flow revision into an expanded execution plan using supplied sample inputs and trigger context.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0751 — Must**

The system shall evaluate expressions, conditions, task graph, retries, concurrency keys and policy decisions in simulation mode.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0752 — Must**

The system shall replace external tasks with declared mocks, recorded fixtures or schema-only placeholders.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0753 — Must**

The system shall estimate task count, critical path, runner demand, storage, API calls and cost where models exist.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0754 — Must**

The system shall show unknown or nondeterministic behavior explicitly rather than fabricating results.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0755 — Must**

The system shall compare simulation plans between flow revisions and plugin sets.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0756 — Must**

The system shall sign simulation evidence used by promotion gates.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0757 — Must**

The system shall keep simulator semantics versioned and conformance-tested against the real reducer.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

#### EPIC-801 — Agentic authoring and operational assistant

Use AI to assist authoring and diagnosis while keeping changes reviewable and policy-bound.

**URS-F-0758 — Must**

The system shall generate draft flows from natural-language intent using installed plugin schemas and organization examples.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0759 — Must**

The system shall explain flow behavior, expressions, validation errors and execution failures with cited platform evidence.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0760 — Must**

The system shall propose minimal patches as reviewable diffs rather than silently mutating active flows.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0761 — Must**

The system shall run validation, simulation and unit tests before presenting a proposed change.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0762 — Must**

The system shall respect tenant, namespace, plugin, secret and data-access permissions during retrieval and tool use.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0763 — Must**

The system shall record model, prompt, context sources, tool calls, cost and user acceptance or rejection.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0764 — Must**

The system shall require human or policy approval before deployment or high-impact execution actions.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0765 — Must**

The system shall support provider-neutral models and complete disablement without reducing core platform functionality.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

#### EPIC-802 — Policy as code and admission controller

Evaluate authoring, deployment and execution policy through open, testable rules.

**URS-F-0766 — Must**

The system shall evaluate policies when validating, saving, promoting, launching and dispatching workflows.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0767 — Must**

The system shall provide structured policy input for actor, tenant, namespace, flow, plugin, runner, image, secret, network and resource context.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0768 — Must**

The system shall support deny, warn, mutate-default and require-approval outcomes.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0769 — Must**

The system shall use an open policy engine or documented declarative rule format.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0770 — Must**

The system shall version policies and pin decisions to policy revisions.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0771 — Must**

The system shall test policies with fixtures and explain matched rules and evidence.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0772 — Must**

The system shall bound evaluation time and fail safely according to policy criticality.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0773 — Must**

The system shall record every enforcement decision in audit history and execution metadata.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

#### EPIC-803 — Multi-region and edge worker topology

Place execution near private infrastructure while maintaining centralized governance and durable control.

**URS-F-0774 — Must**

The system shall register regional or edge worker pools with capabilities, trust domain, connectivity and data-residency labels.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0775 — Must**

The system shall route task runs by policy without exposing private service credentials to the central control plane.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0776 — Must**

The system shall tolerate intermittent worker connectivity through durable local queues and bounded offline leases.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0777 — Must**

The system shall prevent stale disconnected workers from committing after ownership has moved.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0778 — Must**

The system shall keep large task data on regional object storage with explicit transfer policy.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0779 — Must**

The system shall replicate only required metadata and redact location-sensitive information.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0780 — Must**

The system shall report regional health, lag, capacity, data transfer and failover state.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0781 — Must**

The system shall document unsupported active-active metadata semantics and consistency tradeoffs.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

#### EPIC-804 — Open enterprise distribution and packaging

Ship every production capability under an OSI-approved license without artificial feature gates.

**URS-F-0782 — Must**

The system shall build one public source tree containing standalone, distributed, governance and administration features.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0783 — Must**

The system shall avoid license-key checks or closed runtime dependencies for core production operation.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0784 — Must**

The system shall publish complete source and reproducible build instructions for official artifacts.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0785 — Must**

The system shall permit commercial support and hosted offerings without restricting self-hosted capability.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0786 — Must**

The system shall document optional trademark, certification or hosted-service boundaries separately from software rights.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0787 — Must**

The system shall make telemetry, update checks and external services opt-in or replaceable.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0788 — Must**

The system shall publish a bill of materials showing the license of every distributed dependency.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0789 — Must**

The system shall maintain a contributor certificate or developer certificate process appropriate to the selected governance model.

_Verification:_ Feature-specific end-to-end and policy tests.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

#### EPIC-805 — General availability quality and launch readiness

Define objective evidence required before declaring the first stable release.

**URS-F-0790 — Must**

The system shall close or explicitly waive every Must requirement with named owner and rationale.

_Verification:_ Release-gate evidence review.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0791 — Must**

The system shall pass security, performance, accessibility, upgrade, backup, restore, chaos and conformance release gates.

_Verification:_ Release-gate evidence review.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0792 — Must**

The system shall publish support, compatibility, deprecation, LTS and vulnerability response policies.

_Verification:_ Release-gate evidence review.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0793 — Must**

The system shall complete at least two independent production-like reference deployments.

_Verification:_ Release-gate evidence review.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0794 — Must**

The system shall prove recovery from worker, executor, scheduler, PostgreSQL queue, projection and object-storage disruptions.

_Verification:_ Release-gate evidence review.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0795 — Must**

The system shall verify documentation, installation, rollback and disaster-recovery procedures with participants outside the core implementation team.

_Verification:_ Release-gate evidence review.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0796 — Must**

The system shall publish known limitations and parity gaps without misleading compatibility claims.

_Verification:_ Release-gate evidence review.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

**URS-F-0797 — Must**

The system shall freeze public API, event, DSL and plugin contracts for the supported major release.

_Verification:_ Release-gate evidence review.
_Source scope:_ AMESH differentiator; not a Kestra-parity claim.

#### EPIC-806 — Multi-agent topology, typed hand-offs and routing

Coordinate multiple already-bounded agent sessions through typed hand-offs and explainable routing without creating a second execution engine.

**URS-F-0808 — Must**

The system shall support supervisor, router, peer-to-peer, hierarchical and swarm mesh topologies without creating a second execution engine.

_Verification:_ Multi-agent topology, typed hand-off, routing, budget, provenance and failover end-to-end tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

**URS-F-0810 — Must**

The system shall validate agent-to-agent hand-offs against typed schemas and preserve source, destination, rationale and context provenance.

_Verification:_ Multi-agent topology, typed hand-off, routing, budget, provenance and failover end-to-end tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

**URS-F-0811 — Must**

The system shall route work by declared capability, policy, cost, latency, availability and evaluation score with an explainable decision record.

_Verification:_ Multi-agent topology, typed hand-off, routing, budget, provenance and failover end-to-end tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

#### EPIC-807 — Versioned agent definitions and capability envelopes

Define reusable, versioned agent resources whose model, prompt, skill, tool, permission, environment, budget and output-contract revisions resolve and pin before execution.

**URS-F-0806 — Must**

The system shall define versioned agent resources containing model routing, instructions, tools, skills, memory policy, permissions, budgets and evaluation policy.

_Verification:_ Agent resource schema, resolution, authorization, pinning and provider-adapter contract tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

**URS-F-0807 — Must**

The system shall pin resolved agent, model-policy, tool and prompt revisions to every agent session and workflow execution.

_Verification:_ Agent resource schema, resolution, authorization, pinning and provider-adapter contract tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

**URS-F-0815 — Must**

The system shall provide provider-neutral model adapters, fallback policies and migration diagnostics without changing workflow semantics silently.

_Verification:_ Agent resource schema, resolution, authorization, pinning and provider-adapter contract tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

**URS-F-0818 — Must**

The system shall expose approved workflows, agents and tools through authenticated MCP and other versioned agent-protocol adapters.

_Verification:_ Agent resource schema, resolution, authorization, pinning and provider-adapter contract tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

#### EPIC-808 — Durable bounded single-agent sessions

Run one supervised agent as a durable workflow task whose model turns and tool proposals are mediated by AMESH and cannot succeed until structured-output and policy gates pass.

**URS-F-0809 — Must**

The system shall persist agent sessions, messages, tool calls, checkpoints and approvals as durable execution evidence.

_Verification:_ Single-agent session state, budget, tool mediation, approval, checkpoint and recovery end-to-end tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

**URS-F-0813 — Must**

The system shall enforce loop, recursion, concurrency, token, cost, duration and tool-call limits with circuit breakers.

_Verification:_ Single-agent session state, budget, tool mediation, approval, checkpoint and recovery end-to-end tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

**URS-F-0814 — Must**

The system shall require policy or human approval before agents invoke high-impact tools, move sensitive data or exceed delegated authority.

_Verification:_ Single-agent session state, budget, tool mediation, approval, checkpoint and recovery end-to-end tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

**URS-F-0817 — Must**

The system shall resume an interrupted agent session from a durable checkpoint while disclosing which model outputs cannot be reproduced deterministically.

_Verification:_ Single-agent session state, budget, tool mediation, approval, checkpoint and recovery end-to-end tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

#### EPIC-809 — Agent memory, evaluation and release gates

Make bounded agents safe to adopt through isolated memory, versioned evaluations, human-readable traces and evidence-backed promotion gates in the existing workflow experience.

**URS-F-0812 — Must**

The system shall provide isolated private memory and policy-controlled shared memory with retention, redaction, size and tenant boundaries.

_Verification:_ Agent memory-isolation, evaluation, trace, approval-interleaving and release-gate end-to-end tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

**URS-F-0816 — Must**

The system shall evaluate agent and mesh outcomes against versioned tests, rubrics, judges and business assertions.

_Verification:_ Agent memory-isolation, evaluation, trace, approval-interleaving and release-gate end-to-end tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

**URS-F-0819 — Must**

The system shall interleave agent sessions, ordinary tasks and human approval tasks in one state machine, timeline and audit trail.

_Verification:_ Agent memory-isolation, evaluation, trace, approval-interleaving and release-gate end-to-end tests.
_Source scope:_ AMESH Agent Mesh differentiator; not a Kestra-parity claim.

#### EPIC-810 — Reliable scheduling and truthful role-aware health

Make AMESH the durable owner of generic schedules while every enabled service role reports its real ability to make progress.

#### EPIC-811 — Client-neutral external orchestration contract

Let any external client version workflows, launch idempotent runs, inspect progress and control executions through a stable neutral contract.

#### EPIC-812 — Canonical execution evidence bundle

Export one versioned, bounded and integrity-checkable record of everything a client needs to explain an execution without exposing secrets or hidden model rationale.

#### EPIC-813 — Pluggable model-provider capabilities and conformance

Run bounded agents against replaceable model providers whose capabilities, continuation state, timeouts, usage and cost semantics are negotiated and tested before provider I/O.

#### EPIC-814 — Unified MCP and plugin ToolProvider contract

Let MCP servers and installable plugins supply tools through one pinned policy, schema, invocation and recovery boundary without embedding domain integrations in core.

#### EPIC-815 — Hardened client-driven local deployment profile

Provide a fail-closed local deployment profile that external clients can safely call without Docker authority, public exposure or unrelated domain credentials.

#### EPIC-816 — Restart, idempotency and large-record qualification

Prove on isolated PostgreSQL and object storage that failures around schedules, agents, tools and evidence lose no accepted data and create no duplicate logical outcome.

#### EPIC-817 — Generic differential and shadow execution

Compare two exact workflow or agent configurations on frozen inputs without permitting uncontrolled side effects or pretending nondeterministic outputs must be byte-identical.

#### EPIC-818 — Evidence-backed promotion, rollback and release gates

Promote an exact workflow or agent revision only when its client-defined policy is satisfied by fresh immutable evidence, with auditable rollback and an immediate kill switch.

#### EPIC-819 — Pluggable agent-session harness, bounded context and cache evidence

Run long-lived bounded agents through a replaceable session harness while AMESH remains the sole authority for tools, policy, durability, budgets and evidence.

#### EPIC-820 — Guided agent node builder

Let a workflow author configure a valid agent.session node without knowing internal identifiers or writing JSON.

#### EPIC-821 — Live agent run inspector and replay

Let a user understand and safely control an agent run from trigger through structured result.

#### EPIC-822 — Capability catalog and connection wizard

Let users discover, configure, test and attach prompts, skills, plugins, MCP connections and API-backed tools without manual identifiers.

#### EPIC-823 — Generic document and artifact pipeline

Let workflows ingest files such as PDFs as typed provenance-preserving artifacts while plugins supply replaceable parsers and extractors.

#### EPIC-824 — Agent harness conformance and portability

Make the agent-session harness boundary continuously replaceable without weakening AMESH authority or behavior.

#### EPIC-825 — Generic deterministic agent tool argument bindings

Let an orchestrator deterministically bind selected agent-tool arguments from immutable session input while the model continues to choose the tool and all unbound arguments.

#### EPIC-826 — Multi-tenant agent session service and compatibility gateway

Expose AMESH's governed agent-session runtime as an independently consumable multi-tenant product surface so applications can create, observe and control large numbers of bounded user requests from immutable agent revisions without embedding workflow-specific orchestration.

#### EPIC-827 — Agent Session Orchestrator administration and portability

Give administrators a separately managed session-orchestration control plane for fleet visibility, lifecycle governance and portable migration while reusing AMESH's canonical execution, session, evidence and storage authorities.

#### EPIC-828 — Live multimodal agent runs with chronological progress

Let users watch a running agent as one truthful, reconnectable chronological timeline and make governed image input a shared platform capability for workflows, tasks, plugins and sessions without exposing hidden reasoning or duplicating binary state.

#### EPIC-829 — Comprehensive user documentation site

Give new and experienced users one searchable, task-oriented documentation site that accurately explains how AMESH works, how to start it, and how to build, run, inspect, integrate, extend and operate workflows and agent sessions.

#### EPIC-830 — Prompt-cache hit-rate forensics and optimization

Give operators a reproducible, privacy-safe account of provider prompt-cache behavior, locate the first evidence-backed reuse break, and improve reusable context identity without confusing prompt caching with task-result cache or invocation replay.

#### EPIC-831 — Required agent tool-plan governance

Let an agent/session invocation pin a required ordered tool-call plan, expand bounded runtime candidates deterministically, and gate final acceptance until every exact required occurrence succeeds in a restart-safe ledger.

#### EPIC-832 — Harness-owned context budgets and DeepSeek V4 parity

Keep workflow agent nodes isolated behind explicit schema-validated inputs and final outputs, delegate model-visible context projection to the replaceable session harness under AMESH-enforced context budgets, and qualify DeepSeek V4 Flash Vision through the same provider-neutral contract as Luna.

#### EPIC-833 — Durable nonfatal agent-progress backpressure

Keep chronological agent progress bounded and durable without allowing telemetry overflow to fail an otherwise valid model invocation, agent session or workflow execution, while preserving a clear server-versus-client responsibility boundary.

## 5. Non-functional requirements

### Agent Runtime

**URS-NFR-AGENT-001 — Must — Hard budget enforcement**

Agent and mesh budgets shall be enforced by the platform independently of model compliance.

_Target:_ No test mesh exceeds its configured hard cost, token, duration or tool-call limit beyond one explicitly bounded in-flight operation.
_Verification:_ Adversarial runaway-loop and concurrent tool-call tests.
_Mapped epics:_ `EPIC-806`, `EPIC-808`.

**URS-NFR-AGENT-002 — Must — Complete agent provenance**

Every agent message, routing decision, tool call, hand-off, approval and model response shall be traceable to pinned policy and execution context.

_Target:_ All catalogued mesh scenarios produce a complete provenance graph with no orphan tool effects.
_Verification:_ Provenance graph completeness tests.
_Mapped epics:_ `EPIC-806`, `EPIC-808`, `EPIC-809`.

**URS-NFR-AGENT-003 — Must — Memory and tool isolation**

Agent memory, tools and credentials shall be isolated by tenant, namespace, execution and delegated capability.

_Target:_ Zero cross-boundary disclosure or unauthorised tool invocation in adversarial mesh tests.
_Verification:_ Cross-tenant, prompt-injection and capability-confusion tests.
_Mapped epics:_ `EPIC-806`, `EPIC-807`, `EPIC-808`, `EPIC-809`.

**URS-NFR-AGENT-004 — Must — Provider portability**

Core mesh state and policy shall remain usable when a model provider is disabled or replaced.

_Target:_ Reference meshes migrate between two conforming model adapters with documented output nondeterminism and no state-schema change.
_Verification:_ Provider substitution and outage tests.
_Mapped epics:_ `EPIC-806`, `EPIC-807`, `EPIC-809`.

### Ai Engineering

**URS-NFR-AIENGINEERING-001 — Must — Independent verification**

Every AI-authored production change shall receive review and verification from agents that did not implement the change.

_Target:_ 100% of protected-branch changes contain distinct implementer, reviewer and verifier identities.
_Verification:_ Repository policy and pull-request evidence audit.
_Mapped epics:_ `EPIC-011`.

**URS-NFR-AIENGINEERING-002 — Must — Contribution provenance**

AI contributions shall preserve model, tool, input-source and artifact provenance without storing secrets or prohibited source material.

_Target:_ 100% of AI-authored pull requests and releases have a valid provenance record and pass clean-room scans.
_Verification:_ Provenance-schema, secret-scan and clean-room gate tests.
_Mapped epics:_ `EPIC-011`.

**URS-NFR-AIENGINEERING-003 — Must — Autonomy isolation**

Engineering agents shall operate with least privilege and shall not receive production credentials or unreviewed default-branch write access.

_Target:_ Zero production credentials in agent sandboxes and zero direct protected-branch mutations in policy tests.
_Verification:_ Credential canary and branch-protection integration tests.
_Mapped epics:_ `EPIC-011`.

**URS-NFR-AIENGINEERING-004 — Must — Deterministic release gates**

Merge and release eligibility shall be computed from reproducible policy and evidence rather than model confidence.

_Target:_ Repeated evaluation of the same evidence bundle produces the same eligibility result.
_Verification:_ Golden evidence-bundle and policy replay tests.
_Mapped epics:_ `EPIC-011`.

### Availability

**URS-NFR-AVAILABILITY-001 — Must — Compact availability**

A production compact deployment shall support a documented high-availability topology.

_Target:_ At least 99.9% monthly control-plane availability excluding declared maintenance.
_Verification:_ Reference topology soak test and SLO calculation.
_Mapped epics:_ `EPIC-600`, `EPIC-602`.

**URS-NFR-AVAILABILITY-002 — Must — Distributed availability**

The distributed topology shall tolerate loss of any one stateless service instance without operator intervention.

_Target:_ No accepted work lost; service recovers within 60 seconds of instance loss.
_Verification:_ Multi-replica chaos and zone-spread tests.
_Mapped epics:_ `EPIC-601`, `EPIC-603`.

**URS-NFR-AVAILABILITY-003 — Must — Reference recovery objectives**

The first stable release and later hardened profiles shall have documented and tested recovery point and recovery time objectives.

_Target:_ First stable release gate: RPO <= 48 hours and RTO <= 8 hours. Post-GA hardened reference target: RPO <= 4 hours and RTO <= 4 hours; the tighter target is not a v1 release blocker.
_Verification:_ Isolated restore exercise on the on-premises Kubernetes reference topology, with measured data-loss window and service-restoration time.
_Mapped epics:_ `EPIC-609`, `EPIC-805`.

**URS-NFR-AVAILABILITY-004 — Must — Safe maintenance**

Planned maintenance and rolling upgrades shall drain or transfer owned work without silent loss.

_Target:_ Zero lost accepted work and no more than one configured scheduling-delay window.
_Verification:_ Upgrade and drain conformance suite.
_Mapped epics:_ `EPIC-509`, `EPIC-601`, `EPIC-610`.

### Compliance

**URS-NFR-COMPLIANCE-001 — Must — SOC 2 and ISO 27001 readiness**

The architecture, operating procedures and evidence model shall be designed for SOC 2 and ISO/IEC 27001 readiness without representing readiness as certification.

_Target:_ Before GA, every applicable control has a versioned mapping to an owner, implementation, evidence source, collection cadence, test and recorded gap; certification itself is outside the v1 release gate.
_Verification:_ Control-crosswalk validation and sample evidence-package review by an independent security or compliance reviewer.
_Mapped epics:_ `EPIC-504`, `EPIC-612`, `EPIC-805`.

### Maintainability

**URS-NFR-MAINTAINABILITY-001 — Must — Modular boundaries**

Core domain and reducer logic shall not depend directly on web frameworks, PostgreSQL claim mechanics, search projections or object-storage SDKs.

_Target:_ Architecture dependency tests enforce allowed module directions.
_Verification:_ Static architecture test in CI.
_Mapped epics:_ `EPIC-001`, `EPIC-007`, `EPIC-009`, `EPIC-010`.

**URS-NFR-MAINTAINABILITY-002 — Must — Public contract compatibility**

Public DSL, API, event and plugin contracts shall follow documented semantic-versioning and deprecation rules.

_Target:_ No breaking contract change enters a minor or patch release without an approved exception.
_Verification:_ Automated schema and API compatibility checks.
_Mapped epics:_ `EPIC-004`, `EPIC-300`, `EPIC-400`, `EPIC-610`.

**URS-NFR-MAINTAINABILITY-003 — Must — Migration determinism**

Schema, event and resource migrations shall be repeatable and produce the same canonical result.

_Target:_ Repeated migration fixtures produce identical checksums.
_Verification:_ Migration golden tests.
_Mapped epics:_ `EPIC-008`, `EPIC-610`.

**URS-NFR-MAINTAINABILITY-004 — Must — Test pyramid**

Every epic shall include unit, contract, integration or end-to-end evidence appropriate to its risk.

_Target:_ All Must requirements have at least one linked automated or manual verification record before GA.
_Verification:_ Traceability validator and release gate.
_Mapped epics:_ `EPIC-001`, `EPIC-805`.

**URS-NFR-MAINTAINABILITY-005 — Must — Generated artifact freshness**

Generated schemas, SDKs, documentation, traceability files and issue bodies shall be reproducible and checked for drift.

_Target:_ Repository validation produces no uncommitted generated changes.
_Verification:_ CI regeneration and clean-tree check.
_Mapped epics:_ `EPIC-001`, `EPIC-402`, `EPIC-705`.

**URS-NFR-MAINTAINABILITY-006 — Must — Dependency health**

Runtime dependencies shall have declared owners, update policy and license compatibility.

_Target:_ No unknown-license dependency and no unwaived critical known vulnerability in a release.
_Verification:_ Dependency and license scanning.
_Mapped epics:_ `EPIC-001`, `EPIC-612`.

### Operability

**URS-NFR-OPERABILITY-001 — Must — Health model**

Each service shall expose distinct liveness, readiness and detailed dependency health.

_Target:_ Reference orchestrator removes unready instances without restarting healthy but degraded processes unnecessarily.
_Verification:_ Kubernetes and Compose health tests.
_Mapped epics:_ `EPIC-600`, `EPIC-601`, `EPIC-606`.

**URS-NFR-OPERABILITY-002 — Must — Bounded cardinality**

Operational metrics shall avoid unbounded tenant, flow, execution and task identifiers by default.

_Target:_ Metric cardinality remains within published limits under the standard scale test.
_Verification:_ Telemetry cardinality audit.
_Mapped epics:_ `EPIC-607`.

**URS-NFR-OPERABILITY-003 — Must — Actionable alerts**

Reference alerts shall include symptom, likely causes, impact and runbook link.

_Target:_ All GA SLO alerts pass alert-quality review and simulated firing tests.
_Verification:_ Alert fixture and runbook audit.
_Mapped epics:_ `EPIC-607`, `EPIC-705`.

**URS-NFR-OPERABILITY-004 — Must — Support bundle safety**

Administrators shall be able to generate a redacted diagnostic bundle without exposing secrets or unrelated tenant data.

_Target:_ Canary-secret and cross-tenant scans pass for generated bundles.
_Verification:_ Security test with seeded sensitive data.
_Mapped epics:_ `EPIC-003`, `EPIC-607`, `EPIC-612`.

**URS-NFR-OPERABILITY-005 — Must — Capacity visibility**

Operators shall see queue lag, worker capacity, admission pressure, database saturation, storage use and search lag.

_Target:_ All capacity signals are present in the reference dashboard and alert catalog.
_Verification:_ Dashboard and telemetry contract tests.
_Mapped epics:_ `EPIC-105`, `EPIC-601`, `EPIC-607`.

**URS-NFR-OPERABILITY-006 — Must — Safe rollback guidance**

Every release containing irreversible migration or behavior change shall publish recovery and rollback guidance.

_Target:_ Release is blocked when migration classification lacks an operator procedure.
_Verification:_ Release metadata validation.
_Mapped epics:_ `EPIC-610`.

### Performance

**URS-NFR-PERFORMANCE-001 — Must — API latency**

Common authenticated read and write APIs shall remain responsive at the standard reference scale.

_Target:_ Provisional target: p95 below 500 ms and p99 below 1.5 s excluding bulk exports and external dependencies.
_Verification:_ Repeatable load test with 10 million retained execution records and realistic filters.
_Mapped epics:_ `EPIC-400`, `EPIC-409`.

**URS-NFR-PERFORMANCE-002 — Must — Execution launch latency**

Accepted execution launches shall become visible and eligible for orchestration promptly.

_Target:_ Provisional target: p95 below 2 seconds and p99 below 5 seconds in the standard profile.
_Verification:_ End-to-end launch benchmark under mixed workload.
_Mapped epics:_ `EPIC-100`, `EPIC-400`.

**URS-NFR-PERFORMANCE-003 — Must — Schedule accuracy**

Due schedules shall create occurrences within a bounded delay under supported load.

_Target:_ Provisional target: p99 within 5 seconds of due time, excluding declared catch-up throttling.
_Verification:_ Virtual-clock and real-time scheduler benchmark.
_Mapped epics:_ `EPIC-102`.

**URS-NFR-PERFORMANCE-004 — Must — Dispatch throughput**

The distributed reference profile shall sustain task dispatch and completion processing without unbounded lag.

_Target:_ Profile M target: 50 task starts per second sustained for 60 minutes with p95 dispatch latency below 3 seconds and no unbounded queue lag.
_Verification:_ Published benchmark on a fixed reference topology.
_Mapped epics:_ `EPIC-100`, `EPIC-101`, `EPIC-603`.

**URS-NFR-PERFORMANCE-005 — Must — Concurrent workload**

The distributed reference profile shall support large numbers of active executions and task runs.

_Target:_ Profile M target: 1,000 active task runs while accepting at least 100,000 executions over a 24-hour mixed-workload qualification run.
_Verification:_ Soak test with mixed short and long tasks.
_Mapped epics:_ `EPIC-105`, `EPIC-601`, `EPIC-611`.

**URS-NFR-PERFORMANCE-006 — Must — Large workflow usability**

The engine and UI shall handle executions with very large expanded task graphs.

_Target:_ Provisional target: 100,000 task runs per execution with aggregated UI views and bounded memory.
_Verification:_ Synthetic large-DAG and loop benchmark.
_Mapped epics:_ `EPIC-203`, `EPIC-407`.

**URS-NFR-PERFORMANCE-007 — Must — Log ingestion**

Log ingestion shall not block task completion and shall apply explicit overload policy.

_Target:_ Provisional target: 50,000 log records per second per standard cluster with bounded buffers.
_Verification:_ Burst and sustained log-load test with exporter outage.
_Mapped epics:_ `EPIC-111`, `EPIC-607`.

**URS-NFR-PERFORMANCE-008 — Must — Artifact streaming**

Large artifact transfer shall use streaming and bounded memory.

_Target:_ A 10 GiB artifact transfers with less than 256 MiB process-memory growth per stream.
_Verification:_ Storage adapter performance and memory profiling.
_Mapped epics:_ `EPIC-010`, `EPIC-605`.

**URS-NFR-PERFORMANCE-009 — Must — Horizontal scalability**

Adding eligible service replicas shall increase throughput until a documented shared dependency becomes limiting.

_Target:_ At least 70% scaling efficiency from two to four replicas on the reference distributed workload.
_Verification:_ Comparative scale-out benchmark.
_Mapped epics:_ `EPIC-601`, `EPIC-611`.

**URS-NFR-PERFORMANCE-010 — Must — Reference scale profile M**

The v1 distributed reference deployment shall qualify against the accepted profile M workload on the documented on-premises Kubernetes topology.

_Target:_ 100,000 executions per day, 1,000 active task runs, 50 sustained task starts per second and 10 million retained execution records.
_Verification:_ Published 24-hour mixed-workload, retention-query and failure-recovery benchmark on a fixed bill of materials.
_Mapped epics:_ `EPIC-611`, `EPIC-805`.

### Portability

**URS-NFR-PORTABILITY-001 — Must — Open dependencies**

The self-hosted platform shall not require a proprietary control service or license server for any GA capability.

_Target:_ Air-gapped reference deployment passes the full core and governance acceptance suite.
_Verification:_ Offline installation and test run.
_Mapped epics:_ `EPIC-305`, `EPIC-804`.

**URS-NFR-PORTABILITY-002 — Must — Architecture portability**

Official containers shall support linux/amd64 and linux/arm64.

_Target:_ Both architectures pass smoke and conformance tests for every stable release.
_Verification:_ Multi-architecture release CI.
_Mapped epics:_ `EPIC-606`.

**URS-NFR-PORTABILITY-003 — Must — Boundary portability without multi-database promises**

Core transport semantics shall be isolated from PostgreSQL claim mechanics, while object storage, secret providers, model providers and task runners shall use documented capability interfaces.

_Target:_ PostgreSQL remains the sole supported internal durable transport and metadata database; every backend category explicitly marked extensible passes its conformance suite.
_Verification:_ Static architecture checks plus adapter contract tests for each extensible backend category.
_Mapped epics:_ `EPIC-009`, `EPIC-010`, `EPIC-209`, `EPIC-409`, `EPIC-506`.

### Privacy

**URS-NFR-PRIVACY-001 — Must — Telemetry choice**

Product analytics and update checks shall be disabled by default or require an explicit informed opt-in.

_Target:_ No undeclared outbound connection occurs in the offline network test.
_Verification:_ Network capture in a clean reference deployment.
_Mapped epics:_ `EPIC-003`, `EPIC-404`, `EPIC-804`.

**URS-NFR-PRIVACY-002 — Must — Data minimization**

The platform shall retain only data required by configured orchestration, audit and operational policy.

_Target:_ Data inventory maps every persisted field to purpose, retention and sensitivity.
_Verification:_ Privacy and schema review.
_Mapped epics:_ `EPIC-008`, `EPIC-504`, `EPIC-608`.

### Reliability

**URS-NFR-RELIABILITY-001 — Must — Acknowledged-command durability**

The platform shall not lose an accepted state-changing command after the API or durable PostgreSQL transport acknowledges it.

_Target:_ Zero lost acknowledged commands in crash-consistency and failover tests.
_Verification:_ Fault-injection tests that terminate services and PostgreSQL connections at every commit, claim and acknowledgement boundary.
_Mapped epics:_ `EPIC-007`, `EPIC-008`, `EPIC-009`, `EPIC-108`.

**URS-NFR-RELIABILITY-002 — Must — Idempotent redelivery**

The platform shall tolerate duplicate commands, events, trigger occurrences and task results without duplicate logical state transitions.

_Target:_ All conformance duplicate-injection scenarios produce one logical effect.
_Verification:_ Property-based and integration tests with duplicate and reordered delivery.
_Mapped epics:_ `EPIC-007`, `EPIC-009`, `EPIC-100`, `EPIC-103`.

**URS-NFR-RELIABILITY-003 — Must — Stale-owner fencing**

The platform shall prevent an expired scheduler, worker or service owner from committing after ownership transfers.

_Target:_ Zero accepted stale mutations in lease-expiry and partition tests.
_Verification:_ Chaos tests with paused processes, network partitions and delayed completions.
_Mapped epics:_ `EPIC-101`, `EPIC-102`, `EPIC-601`.

**URS-NFR-RELIABILITY-004 — Must — Deterministic replay**

The execution reducer shall produce the same canonical state from the same ordered event stream and reducer version.

_Target:_ Byte-equivalent canonical snapshots across 100 repeated replays and supported platforms.
_Verification:_ Golden event-stream and property-based reducer tests.
_Mapped epics:_ `EPIC-007`, `EPIC-100`.

**URS-NFR-RELIABILITY-005 — Must — Graceful degradation**

Core orchestration shall continue when optional search, telemetry, outbound webhook or analytics services are unavailable.

_Target:_ New and running executions continue within documented latency budgets during optional-service outage tests.
_Verification:_ Dependency isolation and outage integration tests.
_Mapped epics:_ `EPIC-401`, `EPIC-409`, `EPIC-604`, `EPIC-607`.

**URS-NFR-RELIABILITY-006 — Must — Data integrity**

All stored artifacts and imported bundles shall be protected by cryptographic checksums and corruption detection.

_Target:_ Every stored object has a verified checksum; corruption drills are detected before consumption.
_Verification:_ Storage adapter conformance and corruption-injection tests.
_Mapped epics:_ `EPIC-010`, `EPIC-605`, `EPIC-609`.

**URS-NFR-RELIABILITY-007 — Must — Recovery convergence**

Automated reconciliation shall converge recoverable invariant violations without creating new violations.

_Target:_ Reference fault scenarios converge within 10 minutes after dependencies recover.
_Verification:_ End-to-end recovery suite with invariant counters.
_Mapped epics:_ `EPIC-108`, `EPIC-601`.

**URS-NFR-RELIABILITY-008 — Must — Clock robustness**

Temporal decisions shall tolerate bounded clock skew and use monotonic time for local deadlines where possible.

_Target:_ Correct schedule, lease and timeout behavior with plus or minus 30 seconds node skew.
_Verification:_ Virtual-clock and multi-node skew tests.
_Mapped epics:_ `EPIC-102`, `EPIC-104`, `EPIC-601`.

### Security

**URS-NFR-SECURITY-001 — Must — Tenant isolation**

No API, event, cache, log, metric, search, storage or plugin path shall expose one tenant's protected data to another.

_Target:_ Zero cross-tenant findings in adversarial isolation test suite and pre-GA penetration test.
_Verification:_ Automated negative tests, database checks and independent penetration testing.
_Mapped epics:_ `EPIC-503`, `EPIC-604`, `EPIC-605`.

**URS-NFR-SECURITY-002 — Must — Least privilege**

Components, workers, plugins and runners shall receive only the identities and capabilities required for their role and current operation.

_Target:_ Reference deployments pass privilege review with no shared administrator credentials.
_Verification:_ Threat-model review and deployment policy tests.
_Mapped epics:_ `EPIC-303`, `EPIC-501`, `EPIC-612`.

**URS-NFR-SECURITY-003 — Must — Secret non-disclosure**

Secret plaintext shall not appear in persistent metadata, events, logs, metrics, traces, UI payloads or generated support bundles.

_Target:_ Zero seeded canary secrets detected across persisted and exported telemetry in the security suite.
_Verification:_ Canary-secret scanning and redaction tests.
_Mapped epics:_ `EPIC-111`, `EPIC-205`, `EPIC-506`, `EPIC-607`.

**URS-NFR-SECURITY-004 — Must — Encryption in transit**

Production interfaces shall support modern TLS and authenticated internal transport where configured.

_Target:_ TLS 1.2 or newer; weak ciphers disabled in reference configurations.
_Verification:_ Automated protocol scan and reference deployment test.
_Mapped epics:_ `EPIC-613`.

**URS-NFR-SECURITY-005 — Must — Encryption at rest**

The platform shall support encrypted metadata, object storage and secret-provider configurations.

_Target:_ Documented reference configurations use provider-managed or customer-managed encryption keys.
_Verification:_ Configuration audit and restore test.
_Mapped epics:_ `EPIC-602`, `EPIC-605`, `EPIC-506`.

**URS-NFR-SECURITY-006 — Must — Credential rotation**

User, service, component and provider credentials shall be rotatable without rebuilding application images.

_Target:_ Reference rotation procedures complete without losing accepted work.
_Verification:_ Automated token, certificate and external-secret rotation tests.
_Mapped epics:_ `EPIC-501`, `EPIC-502`, `EPIC-506`, `EPIC-613`.

**URS-NFR-SECURITY-007 — Must — Supply-chain provenance**

Official artifacts shall include verifiable source provenance, SBOM and signatures.

_Target:_ 100% of official release artifacts have published checksums, SBOMs and signatures.
_Verification:_ Release pipeline policy gate.
_Mapped epics:_ `EPIC-001`, `EPIC-305`, `EPIC-612`.

**URS-NFR-SECURITY-008 — Must — Untrusted workload isolation**

Untrusted user code and third-party plugins shall not execute inside the webserver, scheduler, executor or metadata database process.

_Target:_ All untrusted reference tasks and plugins run through isolated runners or plugin services.
_Verification:_ Architecture test and runtime process inspection.
_Mapped epics:_ `EPIC-303`, `EPIC-209`, `EPIC-221`, `EPIC-222`.

**URS-NFR-SECURITY-009 — Must — Audit completeness**

Security-relevant actions shall generate attributable audit records even when denied.

_Target:_ 100% coverage of the audited-action catalog in automated tests.
_Verification:_ Endpoint-to-audit traceability suite.
_Mapped epics:_ `EPIC-504`.

**URS-NFR-SECURITY-010 — Must — Secure defaults**

Fresh production-oriented configurations shall fail closed for authentication, plugin trust, network exposure and secrets.

_Target:_ Security baseline scanner reports no critical unsafe defaults.
_Verification:_ Configuration conformance and container scan.
_Mapped epics:_ `EPIC-003`, `EPIC-403`, `EPIC-505`, `EPIC-612`.

### Usability

**URS-NFR-USABILITY-001 — Must — Authoring feedback**

Flow validation shall return actionable errors tied to source locations.

_Target:_ p95 validation response below 1 second for a 5,000-line flow; every error includes code and location.
_Verification:_ Editor benchmark and validation contract tests.
_Mapped epics:_ `EPIC-004`, `EPIC-405`.

**URS-NFR-USABILITY-002 — Must — Operational explainability**

State, admission, retry, cache, policy and authorization decisions shall expose human-readable evidence to authorized users.

_Target:_ Decision evidence is present in all catalogued decision scenarios.
_Verification:_ Scenario-based UI and API acceptance tests.
_Mapped epics:_ `EPIC-105`, `EPIC-109`, `EPIC-500`, `EPIC-802`.

**URS-NFR-USABILITY-003 — Must — First-run success**

A new contributor shall be able to start the reference stack and run a sample flow from documented steps.

_Target:_ Median completion below 20 minutes on a clean supported workstation, excluding image download time.
_Verification:_ Quarterly external documentation usability test.
_Mapped epics:_ `EPIC-001`, `EPIC-411`, `EPIC-600`.

**URS-NFR-USABILITY-004 — Must — Accessibility**

The GA web interface shall conform to WCAG 2.2 AA for supported workflows.

_Target:_ No critical or serious automated findings and manual keyboard and screen-reader acceptance.
_Verification:_ Automated accessibility scan plus manual audit.
_Mapped epics:_ `EPIC-404`, `EPIC-405`, `EPIC-407`.

**URS-NFR-USABILITY-005 — Must — Error safety**

Destructive UI and CLI operations shall present impact, scope and recovery consequences before execution.

_Target:_ All destructive-action catalog entries have preview or explicit force semantics.
_Verification:_ Interaction and CLI contract tests.
_Mapped epics:_ `EPIC-402`, `EPIC-410`, `EPIC-608`.

## 6. Traceability and evidence

- `requirements/urs.json` is the canonical machine-readable requirement set.
- `requirements/traceability.csv` maps every functional and non-functional requirement to one or more epics.
- `requirements/parity-matrix.csv` records the parity or intentional-difference scope of every epic.
- `backlog/epics.json` and `backlog/epics/*.md` contain implementation issue bodies and definitions of done.
- Requirement status remains **Proposed** until the approved evidence model is satisfied.

## 7. Change control

Any change to a Must requirement, compatibility promise, quality target, architecture invariant or licensing decision requires an ADR or product-owner decision, regenerated planning artifacts and updated traceability in the same change set.
