# ADR-039: Authoritative resumable retention lifecycle

- Status: Accepted
- Date: 2026-08-23
- Owner: EPIC-608

## Context

Workflow metadata, logs, metrics, artifacts, caches and search projections have different deletion
mechanics but share scope, legal-hold, preview, scheduling and recovery requirements. Deleting whole
execution rows would break retained references from backfills, human tasks and lineage. Deleting an
object before its authoritative metadata decision could leave live metadata pointing at missing bytes;
deleting metadata without durable object work could leak bytes after a provider failure.

Audit data already has an independent tamper-evident retention policy and legal holds. Workflow-data
retention must not weaken or merge that boundary.

## Decision

Use one PostgreSQL lifecycle coordinator for instance, tenant, namespace and label policies over
execution, log, metric, artifact and cache resources. More-specific matching scope owns selection.
Every manual purge begins as a five-minute immutable impact preview with record/byte counts and exact
typed confirmation. Scheduled policies create the same durable job shape without an interactive
confirmation.

Each execution batch selects terminal work only and retains a compact tombstone identity. Payload and
evidence rows are removed or redacted in dependency order while the tombstone preserves foreign-key
integrity. Search projections are removed after the authoritative metadata mutation in the same
transaction.

Artifact URIs are copied into durable job items before artifact metadata deletion. After commit, the
object lifecycle service rechecks provider retention and legal-hold metadata, performs deletion, and
records success or a retryable failure. Policy, hold, preview, confirmation, batch, retry and completion
events publish through the transactional outbox.

## Consequences

- Maintenance cycles remain bounded by policy batch size and never select active orchestration.
- Job IDs, cursors, failures, retry counts and per-object evidence survive process restart.
- Hard-purged data requires a qualified backup restore; the UI and CLI expose this before execution.
- Execution tombstones and lifecycle evidence have an independent retention owner and may outlive the
  payload they describe.
- Audit retention and audit legal holds remain separate and cannot be shortened by workflow policies.
