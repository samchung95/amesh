# Canonical execution evidence bundles

This reference describes the versioned `EvidenceBundle` contract used to explain one execution
without exposing credentials or hidden model reasoning.

## Compatibility

The current schema version is `1.0`, declared by `schemaVersion` and mirrored by
[`schemas/evidence-bundle-v1.json`](../../schemas/evidence-bundle-v1.json). Consumers must accept
unknown fields when reading a future minor version and must reject an unsupported major version.
Writers emit only the fields documented by the selected version. The bundle digest is a
`sha256:<64 lowercase hex>` digest of the canonical UTF-8 JSON projection with `bundleDigest`
excluded; object keys are sorted and records are ordered by sequence, timestamp, kind and ID.

## Contents and safety

The bundle carries exact `pins`, `inputs`, `outputs`, `decisions`, `trace`, task attempts, agent
sessions, external invocations, state transitions, logs, metrics, files, errors, approvals,
interventions and controls. Token usage and cost are separate typed sections. Cost is explicitly
`priced`, `unpriced` or `unavailable`; token and section availability distinguish `absent` from
`unavailable`.

Record payloads redact secret-shaped keys and omit hidden reasoning fields during construction.
`ProtectedContinuation` stores provider continuation material privately; its public form contains
only provider, revision and token digest, while a provider/revision match is required to resume.

## Bounded retrieval and externalization

`EvidenceBundleStore.page` is the shared retrieval boundary for REST, CLI and SDK adapters. It
requires the caller tenant to match the bundle tenant, caps pages at 500 records, and returns a
cursor page. Missing execution evidence raises an absent result; a repository outage raises an
unavailable result. Neither state is represented by an empty successful page.

Payloads larger than the inline limit can be replaced by an `externalRef` containing a content
digest, size and URI. `MemoryEvidenceObjectStore` is the contract-test implementation; production
adapters must verify the digest and byte count on every read. A bundle is immutable: storing the
same execution with a different digest raises `EvidenceConflictError`.

The implementation lives in [`src/amesh/evidence_bundle.py`](../../src/amesh/evidence_bundle.py).

## Durable retrieval

Migration `0061_canonical_evidence_bundles.sql` stores one sealed projection per
`(tenant, execution)` in PostgreSQL and emits an `ExecutionEvidenceBundleStored` outbox message
after commit. `PostgresEvidenceBundleRepository` verifies the stored digest on every read and
rejects a second projection with a different digest. The repository uses the existing tenant
transaction/RLS boundary, so a tenant can receive only its own evidence; an absent bundle is
distinct from an unavailable database or object store.

`GET /api/v1/executions/{execution_id}/evidence-bundle` returns at most 500 records from one
canonical section with a cursor. The `amesh evidence EXECUTION_ID` CLI command and the checked-in
Python SDK template use the same endpoint; `--verify`/`verify=True` checks the schema-shaped page
and digest marker. Set `AMESH_EVIDENCE_OBJECT_ROOT` for the local profile to use the filesystem
content-addressed adapter when a redacted payload exceeds the inline limit. Object bytes are
hashed and size-checked on every read, and the root can be replaced by a provider-neutral object
store in a production deployment.
