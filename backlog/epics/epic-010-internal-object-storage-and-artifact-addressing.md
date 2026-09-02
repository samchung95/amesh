# EPIC-010 — Internal object storage and artifact addressing

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `storage`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Store workflow files and artifacts independently from orchestration metadata.

## In scope

- [x] **URS-F-0076** — The system shall address stored objects through opaque tenant-scoped URIs rather than local filesystem paths.
- [x] **URS-F-0077** — The system shall support local development storage and S3-compatible production storage through one interface.
- [x] **URS-F-0078** — The system shall stream uploads and downloads without loading large objects fully into process memory.
- [x] **URS-F-0079** — The system shall record size, content type, checksum, encryption metadata, creator, retention and lineage.
- [x] **URS-F-0080** — The system shall prevent cross-tenant access and path traversal at every storage boundary.
- [x] **URS-F-0081** — The system shall support multipart upload, ranged download and resumable transfer where the backend permits.
- [x] **URS-F-0082** — The system shall garbage-collect unreferenced objects only after a configurable safety window.
- [x] **URS-F-0083** — The system shall verify object integrity on write and optionally on read.

## Implementation completion evidence

- 2026-08-22 — EPIC-010 is complete. AMESH now addresses objects through opaque tenant-scoped provider URIs behind one SDK-independent contract used by local versioned MinIO and the supported S3, Azure Blob and Google Cloud Storage adapters. Uploads are multipart/resumable and downloads are streamed with bounded memory; full reads and migrations verify SHA-256 integrity, while native ranged reads enforce object bounds and returned length. Provider metadata preserves creation time, creator, lineage, content type, size, checksum, encryption, retention, legal hold and version identity. Path traversal and cross-tenant URI access are rejected before provider calls. Bounded garbage-collection passes consult an authoritative reference checker and honor the configurable safety window, retention and holds. Provider-fake conformance, corruption injection, a live MinIO exercise and the 10 GiB logical transfer memory profile passed. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`object-storage.md`](../../docs/operations/object-storage.md), [`object_store.py`](../../src/amesh/ports/object_store.py), [`service.py`](../../src/amesh/storage/service.py), [`test_service.py`](../../tests/storage/test_service.py), [`test_provider_adapters.py`](../../tests/storage/test_provider_adapters.py), and [`test_minio_integration.py`](../../tests/storage/test_minio_integration.py). Shared maintainability and portability NFRs remain In Progress for their other owning epics.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-006** — All stored artifacts and imported bundles shall be protected by cryptographic checksums and corruption detection. Target: Every stored object has a verified checksum; corruption drills are detected before consumption.
- [ ] **URS-NFR-PERFORMANCE-008** — Large artifact transfer shall use streaming and bounded memory. Target: A 10 GiB artifact transfers with less than 256 MiB process-memory growth per stream.
- [ ] **URS-NFR-MAINTAINABILITY-001** — Core domain and reducer logic shall not depend directly on web frameworks, PostgreSQL claim mechanics, search projections or object-storage SDKs. Target: Architecture dependency tests enforce allowed module directions.
- [ ] **URS-NFR-PORTABILITY-003** — Core transport semantics shall be isolated from PostgreSQL claim mechanics, while object storage, secret providers, model providers and task runners shall use documented capability interfaces. Target: PostgreSQL remains the sole supported internal durable transport and metadata database; every backend category explicitly marked extensible passes its conformance suite.

## Dependencies

- EPIC-002

## Architecture impact

- Primary bounded area: `storage`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Repository or storage adapter contract and fault-injection tests.
- Storage adapter conformance and corruption-injection tests.
- Storage adapter performance and memory profiling.
- Static architecture test in CI.
- Static architecture checks plus adapter contract tests for each extensible backend category.
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

- Functional requirements: URS-F-0076, URS-F-0077, URS-F-0078, URS-F-0079, URS-F-0080, URS-F-0081, URS-F-0082, URS-F-0083
- Non-functional requirements: URS-NFR-RELIABILITY-006, URS-NFR-PERFORMANCE-008, URS-NFR-MAINTAINABILITY-001, URS-NFR-PORTABILITY-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
