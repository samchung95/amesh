# AMESH decision register

**Product:** AMESH — Agent Mesh  
**Repository:** `amesh`  
**Updated:** 2026-08-16

This register records product-owner decisions and separates them from assumptions that still require confirmation. Accepted decisions are binding until replaced by an ADR.

| ID | Status | Decision |
|---|---|---|
| Q-001 | Accepted | The product name is **AMESH**, meaning **Agent Mesh**. The repository slug, package prefix and CLI name are `amesh`. |
| Q-002 | Accepted | AMESH is a **strict clean-room implementation** based on public documentation, observable behavior and independently written conformance tests. Kestra source code, UI assets and documentation prose are not implementation inputs. |
| Q-003 | Accepted | Scope is **full public Kestra parity plus more**: reproduce the pinned OSS surface, independently implement publicly documented advanced/enterprise-class capabilities, and add AMESH-specific differentiators. Everything ships in one open distribution. |
| Q-004 | Accepted | The project is licensed under **GNU AGPL v3 only**, recorded as `AGPL-3.0-only`. This is the strongest network-copyleft direction selected while preserving open-source status. No field-of-use or non-commercial restriction is added. |
| Q-005 | Accepted | Compatibility is required for **Kestra YAML, Pebble expressions, REST API, CLI, execution semantics and documented import/export formats** for each declared compatibility release. Compatibility is version-pinned and conformance-tested. |
| Q-006 | Accepted, amended 2026-08-19 | Use a **Python 3.12 asyncio durable core** ([ADR-016](../adr/016-python-production-core.md); the original Java 25 selection in ADR-010 was superseded before implementation began), React/TypeScript UI, language-neutral plugin RPC, and Java/Python/TypeScript SDKs. Go or Rust components require measured justification and a separate ADR. |
| Q-007 | Accepted | The primary web frontend uses **React and TypeScript**. AMESH owns its design tokens and accessibility contract rather than cloning Kestra’s visual design. |
| Q-008 | Accepted | AMESH uses **PostgreSQL-backed durable transport only** for its reference architecture. It does not require Kafka, Redpanda, NATS or another internal broker. `LISTEN/NOTIFY` may wake workers but is never delivery truth. |
| Q-009 | Accepted | **PostgreSQL is the only supported authoritative relational database** in the initial and GA reference architecture. MySQL/MariaDB compatibility is out of scope. |
| Q-010 | Accepted with guardrail | Native plugins use an isolated, language-neutral protocol. Existing Kestra plugin configuration should be mechanically migrated where possible; unchanged JAR compatibility is not a baseline promise. A transitional JVM bridge is allowed only if measured migration overhead is unacceptably high. |
| Q-011 | Accepted | First-class runners are **local process, Docker/OCI and Kubernetes**. Cloud batch/VM/serverless runners follow later through the same runner contract. |
| Q-012 | Accepted | The first real production environment and reference packaging target is **on-premises Kubernetes deployed through Helm**. Docker Compose remains the development profile and the single-host profile remains secondary. The on-prem reference must have no mandatory public-cloud or hosted-control-plane dependency. |
| Q-013 | Accepted | Priority personas are **AI workflow developers, software engineers and platform engineers**. |
| Q-014 | Accepted | The first integration pack is **HTTP/REST, webhooks, Git, GitHub, PostgreSQL, S3/MinIO, Docker/OCI, Kubernetes, OpenAI-compatible model APIs and MCP**. Python and Node.js script execution are core runtimes rather than integration slots. |
| Q-015 | Accepted | The v1 distributed qualification target is **profile M**: 100,000 executions/day, 1,000 active task runs, 50 sustained task starts/second and 10 million retained execution records. |
| Q-016 | Accepted | Monthly control-plane availability is **99.9%**. The first stable release uses the **minimal recovery gate: RPO ≤ 48 hours and RTO ≤ 8 hours**. A hardened post-GA reference target of RPO ≤ 4 hours and RTO ≤ 4 hours remains planned but is not a v1 blocker. |
| Q-017 | Accepted | Migration depth is **option C**: versioned side-by-side migration of resources, users, roles, service accounts, configuration, plugin inventory, historical executions, task runs, logs, artifacts and audit evidence. Direct in-place conversion of a Kestra database is not the reference method. |
| Q-018 | Accepted | AMESH is designed for **SOC 2 and ISO/IEC 27001 readiness** before GA. Control mapping and evidence generation are release requirements; formal certification is not itself a v1 release gate. |
| Q-019 | Accepted | All proposed differentiators are in scope: one fully OSS distribution, isolated multi-language plugins, deterministic simulation, policy-as-code and evidence-backed agentic assistance. A first-class agent-mesh runtime is an AMESH-specific capability. |
| Q-020 | Accepted with governance | Engineering is performed by elastic teams of AI engineering agents using widely represented languages and tools. Agents work through isolated branches/worktrees, independent review and deterministic quality gates; no agent may approve its own change. |
| Q-021 | Accepted | **Independent agent quorum** may merge ordinary changes after deterministic gates pass. A named human must approve security-sensitive changes, licence or governance changes, destructive production migrations and every stable release. |
| Q-022 | Accepted | Retain **`AGPL-3.0-only`**. A more restrictive field-of-use or hosted-service prohibition would no longer meet the project’s fully open-source objective. Trademark and official-build policies remain separate from software copyright permissions. |

## Binding architecture consequences

1. The production durable control plane uses Python 3.12 asyncio; the checked-in foundation is the production core seed and its tests are tests of production behavior (ADR-016).
2. PostgreSQL is authoritative for resources, execution state, immutable events, queues, leases, inbox/outbox records and search projections in the reference stack.
3. Full compatibility is a testable product requirement, not a marketing aspiration.
4. Native AMESH contracts may be cleaner internally, but the compatibility façade must preserve required Kestra behavior at the public boundary.
5. Plugin isolation and migration automation take priority over loading arbitrary third-party code into the control plane.
6. The reference production topology is an on-premises Kubernetes cluster using external PostgreSQL and S3-compatible object storage, with an offline installation path.
7. Profile M and the minimal v1 recovery targets are release gates and require reproducible qualification evidence.
8. Full migration includes historical and governance data, uses side-by-side export/import, and must be resumable, idempotent and independently reconciled.
9. SOC 2 and ISO/IEC 27001 readiness requires machine-readable control mappings and evidence provenance but must not be represented as certification.
10. Normal AI-authored changes may be merged autonomously only through independent quorum and deterministic gates; specified high-risk actions retain human accountability.
11. `AGPL-3.0-only` protects network modifications through copyleft while still permitting commercial use, support and hosting under the licence terms.

## Decision closure

All foundational product-owner decisions currently listed in this register are accepted. New implementation choices are handled through ADRs and do not block M0 unless they would alter an accepted requirement or architecture boundary.
