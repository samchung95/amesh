# EPIC-606 — Containers, Kubernetes and Helm deployment

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `operations`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Provide secure, portable and air-gapped-capable deployment artifacts for the on-premises Kubernetes reference environment.

## In scope

- [ ] **URS-F-0630** — The system shall publish minimal multi-architecture container images with non-root defaults and immutable tags.
- [ ] **URS-F-0631** — The system shall provide a Helm chart for standalone and distributed role topologies.
- [ ] **URS-F-0632** — The system shall configure probes, disruption budgets, autoscaling, affinity, topology spread, resources and security contexts.
- [ ] **URS-F-0633** — The system shall support external PostgreSQL, object storage, ingress, identity, secret and certificate integrations required by the selected deployment profile.
- [ ] **URS-F-0634** — The system shall avoid embedding default production secrets and support external secret injection.
- [ ] **URS-F-0635** — The system shall validate chart installation, upgrade and failure recovery against the documented on-premises Kubernetes reference topology and at least one additional portable Kubernetes distribution in CI or scheduled qualification.
- [ ] **URS-F-0636** — The system shall provide network-policy examples that separate control plane, workers and user infrastructure.
- [ ] **URS-F-0637** — The system shall publish values schema, migration notes and generated reference documentation.
- [ ] **URS-F-0826** — The system shall provide an on-premises Kubernetes reference deployment with no mandatory public-cloud control plane, managed database, managed object store, hosted telemetry service or license server.
- [ ] **URS-F-0827** — The system shall support disconnected installation and upgrade from a signed offline bundle containing images, Helm charts, custom-resource definitions, migrations, SBOMs, provenance and operator documentation.
- [ ] **URS-F-0828** — The system shall validate the reference Helm deployment against upstream Kubernetes and at least one common on-premises distribution using external PostgreSQL and S3-compatible storage.

## MVP implementation progress

- 2026-08-21 — W7 verified the accepted deployment slice on a fresh kind v0.32.0 / Kubernetes v1.36.1 cluster: a uv-locked numeric non-root image installed through Helm as an external-PostgreSQL migration hook plus server and recovery-worker Deployments, namespace-scoped task-Job RBAC, external Secret references and health probes. The installed Service completed the checked-in Luna → Kubernetes Job → HTTP flow. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`Dockerfile`](../../Dockerfile), and [`charts/amesh`](../../charts/amesh). Multi-architecture, ingress, air-gap, upgrade and broader qualification requirements remain open.
- 2026-08-21 — W8 exercised the exact release-candidate image for 270 successful task-pod deletion/reconciliation cycles with 27 server and 13 worker replacements; the API and replacement roles stayed healthy, and the clean-cluster quickstart was reproduced. The product owner accepted this MVP evidence and deferred the uninterrupted 24-hour qualification to EPIC-611. Evidence: [`TESTLOG.md`](../../TESTLOG.md) and [`scripts/soak_mvp.py`](../../scripts/soak_mvp.py).

## Non-functional requirements

- [ ] **URS-NFR-OPERABILITY-001** — Each service shall expose distinct liveness, readiness and detailed dependency health. Target: Reference orchestrator removes unready instances without restarting healthy but degraded processes unnecessarily.
- [ ] **URS-NFR-PORTABILITY-002** — Official containers shall support linux/amd64 and linux/arm64. Target: Both architectures pass smoke and conformance tests for every stable release.

## Dependencies

- EPIC-600
- EPIC-601
- EPIC-612

## Architecture impact

- Primary bounded area: `operations`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Reference deployment, upgrade and failure-recovery tests.
- On-premises Kubernetes installation, upgrade and failure-recovery tests.
- Air-gapped bundle installation and upgrade tests.
- Cross-distribution Kubernetes conformance and upgrade tests.
- Kubernetes and Compose health tests.
- Multi-architecture release CI.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [ ] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [ ] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [ ] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [ ] Security, tenant isolation, redaction and audit behavior are reviewed.
- [ ] Documentation, examples, migration notes and operational runbooks are updated.
- [ ] Performance and recovery budgets are measured when this epic is on a critical path.
- [ ] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Kubernetes distribution differences can affect storage, ingress, security policy and upgrade behavior.
- Offline bundles increase release size and require strict provenance and patch procedures.

## Traceability

- Functional requirements: URS-F-0630, URS-F-0631, URS-F-0632, URS-F-0633, URS-F-0634, URS-F-0635, URS-F-0636, URS-F-0637, URS-F-0826, URS-F-0827, URS-F-0828
- Non-functional requirements: URS-NFR-OPERABILITY-001, URS-NFR-PORTABILITY-002
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
