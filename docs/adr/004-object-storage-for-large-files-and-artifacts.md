# ADR-004: Object storage for large files and artifacts

- **Status:** Accepted
- **Decision questions:** Q-008, Q-009, Q-012
- **Date:** 2026-08-15

## Context

AMESH uses PostgreSQL as its sole authoritative relational database and durable internal transport, but large artifacts, namespace files, migration bundles and payloads should not inflate transactional queue and event rows.

The first production environment is on-premises Kubernetes, so the storage contract must work without a public-cloud dependency.

## Decision

Keep large payloads out of PostgreSQL orchestration rows. Store them through an S3-compatible object-storage port using opaque tenant-scoped object identities, checksums, explicit lifecycle state and authorization context.

Use MinIO in development and as the self-hosted reference implementation. Do not require MinIO specifically in production.

## Consequences

- Large data can be streamed in bounded memory.
- PostgreSQL and object-storage backups require coordinated recovery procedures.
- Object references, checksums and lifecycle state remain transactional metadata in PostgreSQL.
- Local filesystem storage is development-only and not a production durability promise.
- The on-premises reference deployment requires an external or independently managed S3-compatible store.

## Revisit triggers

- A conformance, performance or security test invalidates the S3-compatible abstraction.
- Coordinated backup cannot meet the selected recovery objectives.
- A public contract would otherwise be broken.

## Traceability

See `docs/architecture/on-premises-kubernetes.md`, `docs/architecture/ha-and-dr.md`, `EPIC-010`, `EPIC-605` and `EPIC-609`.
