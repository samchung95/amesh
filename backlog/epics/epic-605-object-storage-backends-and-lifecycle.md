# EPIC-605 — Object storage backends and lifecycle

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `storage`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Operate internal storage reliably across local and cloud object stores.

## In scope

- [x] **URS-F-0622** — The system shall support S3-compatible, Azure Blob and Google Cloud Storage backends.
- [x] **URS-F-0623** — The system shall use tenant-aware prefixes or containers and configurable encryption keys.
- [x] **URS-F-0624** — The system shall support proxy, private endpoint, custom certificate authority and workload identity configurations.
- [x] **URS-F-0625** — The system shall verify read-after-write assumptions and compensate for backend-specific consistency behavior.
- [x] **URS-F-0626** — The system shall apply retention, lifecycle, legal hold and deletion markers without orphaning referenced artifacts.
- [x] **URS-F-0627** — The system shall support migration between storage backends with checksum verification and resumability.
- [x] **URS-F-0628** — The system shall publish storage usage, request, latency, error and corruption metrics.
- [x] **URS-F-0629** — The system shall include storage data in backup, restore and disaster-recovery validation.

## Implementation completion evidence

- 2026-08-22 — EPIC-605 portable storage scope is complete. The execution path selects S3-compatible, Azure Blob or Google Cloud Storage adapters through one tenant-scoped streaming contract. Workload identity, static credentials, private endpoints, proxy/custom CA and provider encryption-key settings are exposed through typed configuration and Helm values. Verified reads spool in bounded memory and reject checksum corruption before yielding data; read-after-write retries compensate for delayed visibility. Lifecycle decisions block referenced, retained or held objects; migration is checksum-verified, deterministic and resumable through an atomically persisted CLI checkpoint. Backend-bounded Prometheus metrics cover usage, requests, latency, errors and corruption. Provider-fake conformance passed for all three adapters, real versioned MinIO passed multipart/inventory/lifecycle behavior, and the 10 GiB logical transfer stayed below the 256 MiB target. Managed Azure/GCP environment certification remains EPIC-706 qualification. Coordinated backup/restore use of the verified inventory is intentionally completed next under EPIC-609, so URS-F-0629 remains In Progress until that exercise passes. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`object-storage.md`](../../docs/operations/object-storage.md), [`test_service.py`](../../tests/storage/test_service.py), [`test_provider_adapters.py`](../../tests/storage/test_provider_adapters.py), and [`test_minio_integration.py`](../../tests/storage/test_minio_integration.py).
- 2026-08-22 — URS-F-0629 is now Verified by EPIC-609. The recovery manifest captures exact provider versions and checksums for every tenant object, and the isolated PostgreSQL 17 + versioned-MinIO exercise verified every recorded object before completing a real restore. Evidence: [`disaster-recovery.md`](../../docs/operations/disaster-recovery.md) and [`test_disaster_recovery.py`](../../tests/adapters/postgres/test_disaster_recovery.py).

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-006** — All stored artifacts and imported bundles shall be protected by cryptographic checksums and corruption detection. Target: Every stored object has a verified checksum; corruption drills are detected before consumption.
- [ ] **URS-NFR-PERFORMANCE-008** — Large artifact transfer shall use streaming and bounded memory. Target: A 10 GiB artifact transfers with less than 256 MiB process-memory growth per stream.
- [ ] **URS-NFR-SECURITY-001** — No API, event, cache, log, metric, search, storage or plugin path shall expose one tenant's protected data to another. Target: Zero cross-tenant findings in adversarial isolation test suite and pre-GA penetration test.
- [ ] **URS-NFR-SECURITY-005** — The platform shall support encrypted metadata, object storage and secret-provider configurations. Target: Documented reference configurations use provider-managed or customer-managed encryption keys.

## Dependencies

- EPIC-010

## Architecture impact

- Primary bounded area: `storage`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Repository or storage adapter contract and fault-injection tests.
- Storage adapter conformance and corruption-injection tests.
- Storage adapter performance and memory profiling.
- Automated negative tests, database checks and independent penetration testing.
- Configuration audit and restore test.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0622, URS-F-0623, URS-F-0624, URS-F-0625, URS-F-0626, URS-F-0627, URS-F-0628, URS-F-0629
- Non-functional requirements: URS-NFR-RELIABILITY-006, URS-NFR-PERFORMANCE-008, URS-NFR-SECURITY-001, URS-NFR-SECURITY-005
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
