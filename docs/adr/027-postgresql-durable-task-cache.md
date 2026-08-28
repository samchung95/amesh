# ADR 027: PostgreSQL durable task-result cache

- Status: Accepted
- Date: 2026-08-22
- Scope: EPIC-109

## Context

AMESH needs deterministic task-result reuse with tenant and security-context isolation, expiry,
administrative invalidation, restart recovery, concurrent population safety and visible provenance.
The result envelope includes outputs, metrics and artifact references, so a cache hit is an execution
decision rather than a transparent process-local optimization.

## Decision

Use tenant-RLS-protected PostgreSQL tables for cache entries and an immutable decision ledger. A
transaction-scoped advisory lock serializes one key decision. The first miss owns a leased
`POPULATING` entry; concurrent executions may compute a safe duplicate but cannot overwrite the
owner's result. Successful publication changes the entry to `READY`. Failure or deferral abandons the
lease, while expiry, refresh and administrative purge make an entry non-reusable before a new owner
publishes.

Keys use a canonical SHA-256 digest of the tenant, flow revision, rendered task configuration,
declared input values, selected context, task/plugin code version and a one-way security-context
fingerprint. Raw secret values are not stored. The human-readable prefix is administrative metadata,
not the equality key.

The public DSL preserves Kestra's `taskCache.enabled` and ISO-8601 `taskCache.ttl` spellings. AMESH
adds namespace, scope, invalidation policy, selected key context and explicit code version. Execution
launches add `cacheMode` with `USE`, `BYPASS` and `REFRESH` values.

## Alternatives considered

- A process-local mapping was rejected because it cannot survive restart, coordinate replicas or
  preserve tenant-scoped audit evidence.
- Redis or Memcached through dogpile.cache was rejected for this profile because it adds another
  required service while still requiring PostgreSQL provenance and purge records. The library's
  distributed locks are backend-specific; PostgreSQL already provides transaction-scoped advisory
  locks alongside AMESH's authoritative execution state.
- Caching a whole execution was rejected because the epic's deterministic unit is a runnable task;
  task-level reuse preserves normal orchestration, state and lineage for every execution.

## Consequences

- Cache availability follows the existing PostgreSQL dependency and backup boundary.
- Cache hits still create ordinary task attempts, outputs, metrics, artifact projections and task-run
  evidence in the current execution.
- Purge is a soft invalidation, preserving the decision and audit history.
- Result reuse is opt-in and limited to runnable tasks. Flowables continue to reduce their current
  child executions.

## References

- [Kestra task cache documentation](https://kestra.io/docs/workflow-components/tasks#task-cache)
- [PostgreSQL advisory lock functions](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS)
- [dogpile.cache usage guide](https://dogpilecache.sqlalchemy.org/en/latest/usage.html)
