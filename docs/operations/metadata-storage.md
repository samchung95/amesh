# Metadata storage operations

AMESH uses PostgreSQL as the reference transactional metadata backend. Domain-facing ports remain
separate from SQLAlchemy adapters so persistence mechanics do not leak into orchestration logic.

## Repository ownership

| Resource | Port and PostgreSQL owner |
| --- | --- |
| Flows and immutable revisions | `ExecutionRepository` / `PostgresExecutionRepository` |
| Executions and task runs | `ExecutionRepository` / `PostgresExecutionRepository` |
| Trigger definitions, workers, execution logs and metrics, assets | `MetadataRepository` / `PostgresMetadataRepository` |
| Tenants and tenant policy | `TenantRepository` / `PostgresTenantRepository` |
| Principals, groups, roles and bindings | `AuthorizationRepository` / `PostgresAuthorizationRepository` |
| Service credentials and usage windows | `CredentialRepository` / `PostgresCredentialRepository` |
| Command inbox, work queue and outbox | `DurableTransport` / `PostgresDurableTransport` |

Flow writes materialize trigger definitions in the same transaction as their immutable revision.
Execution logs and metrics have tenant-safe foreign keys to their execution and optional task run.
Worker heartbeat and asset updates use resource versions so stale writers cannot overwrite newer
metadata.

Tenant quota usage is stored transactionally beside metadata. Log insertion reserves the UTF-8 message
and structured-field byte count before the row is written; a rejected insert rolls back both changes.
Storage adapters reserve and release bytes through `TenantRepository`, and tenant-scoped API requests
consume a database-time, one-minute window. The applicable limits are `max_log_bytes`,
`max_storage_bytes` and `max_api_requests_per_minute` in `TenantPolicy`.

## Transaction and migration contract

Tenant repository operations explicitly use PostgreSQL `READ COMMITTED` transactions after selecting
the restricted runtime or tenant-administration role and setting the transaction-local tenant ID.
Scheduling claims, state changes, event insertion and outbox publication therefore share an explicit
transaction boundary. Event-to-outbox triggers run inside the state transaction, so rollback removes
both records. Migration application uses `SERIALIZABLE` plus a transaction-scoped advisory lock.

`migrations/manifest.json` is the canonical order and classifies every migration as `bootstrap`,
`expand` or `exclusive`, records whether mixed-version rollout is supported, and gives operator
rollback or forward-fix guidance. Applied files are immutable; create another numbered migration for
corrections. Readiness is false when database connectivity fails or the applied migration count does
not exactly match the checked-in manifest.

## Operational signals

`GET /health` is process liveness. `GET /ready` reports configuration, credential, PostgreSQL,
exact-migration, object-storage and service-registry conditions as `READY`, `DEGRADED` or
`UNAVAILABLE`; required failures return HTTP 503. Reference deployments enable the storage probe
with `READINESS_CHECK_STORAGE=true`. `GET /metrics` exposes:

- `amesh_database_health`;
- `amesh_database_pool_size` and `amesh_database_pool_checked_out`;
- `amesh_database_query_duration_seconds` and `amesh_database_slow_queries_total`;
- `amesh_database_migrations_applied` and `amesh_database_migrations_expected`.

Set `DATABASE_SLOW_QUERY_SECONDS` to the desired positive threshold; the default is 0.5 seconds.
These metrics have no tenant, SQL text or identifier labels, avoiding unbounded cardinality and data
leakage.

Pool budgets, optional stale-read replica routing, TLS modes, compatibility qualification and
backup-consistent WAL/object checkpoints are defined in the [PostgreSQL operations guide](postgresql.md).

## Metadata data inventory

| Data | Persisted fields | Purpose | Sensitivity | Retention owner |
| --- | --- | --- | --- | --- |
| Trigger definitions | tenant, revision, key, type, canonical definition, enabled flag, creator, timestamp | Rebuild and schedule the exact flow revision | Internal; definition may contain operator configuration | Flow revision lifecycle; EPIC-608 defines purge enforcement |
| Worker registration | tenant, group, instance, version, capabilities, labels, state, heartbeat, version/audit/lifecycle timestamps | Claim routing, fencing and worker health | Internal infrastructure metadata | Worker lifecycle; EPIC-608 defines stale-record purge |
| Execution logs | tenant, execution/task identity, level, logger, message, structured fields, redaction flag, timestamp | Execution diagnosis and audit evidence | Potentially sensitive; callers must redact secret-derived values before persistence | Tenant retention policy; EPIC-608 defines purge enforcement |
| Execution metrics | tenant, execution/task identity, name, kind, numeric value, unit, labels, timestamp | Execution performance and outcome analysis | Internal operational metadata | Tenant retention policy; EPIC-608 defines purge enforcement |
| Assets | tenant, provider key, type, display name, metadata, resource version, actor/timestamps | Catalog identity and current metadata | Classification is provider-defined and may be sensitive | Asset lifecycle; EPIC-507/608 define lineage and purge |
| Audit evidence | tenant, actor/delegated actor, resource/action/outcome/reason, source, correlation/trace, event time, retention time and hash chain | Security investigation, change accountability and compliance evidence | Security-sensitive metadata; protected values are recursively redacted | Independent tenant audit policy and legal holds; enforced by EPIC-504 purge |
| Lifecycle policies | policy and optional tenant identity, resource type, scope selector, retention days, batch/schedule controls, enabled state, reason, actor/timestamps and version | Resolve and schedule bounded workflow-data retention | Internal policy metadata; reasons may contain operational context | Retained while active and through dependent job evidence; disabled policies are removed only by administrative lifecycle |
| Lifecycle legal holds | hold and tenant identity, type/resource/namespace/label/time selectors, active/release state, reasons, actors and timestamps | Prevent eligible workflow data from entering purge selection | Compliance-sensitive investigation metadata | Independent of ordinary workflow retention; retained after release as hold evidence |
| Lifecycle jobs and items | job/policy/tenant identity, trigger/state/cutoff, policy snapshot, record/byte estimates and progress, cursor, retries/errors, actor/reason/timestamps, per-resource decision, object URI and size | Resume bounded purges, retry external deletes and prove authoritative deletion order | Operationally sensitive; object URIs and errors may expose resource names but never object content | Job evidence is not governed by the job's target policy; retained under operator/compliance evidence policy |
| Lifecycle events | tenant/policy/job/event identity, type, actor, reason, payload and timestamp | Immutable policy, preview, confirmation, batch, retry and completion evidence with transactional outbox publication | Audit-adjacent operational metadata; payload contains counts and IDs, not retained content | Retained independently from target workflow data and exported through ordinary event transport policy |
| Compliance evidence | tenant, category, title, source, event/creation time, redacted payload and checksum | Package access-review, change, backup/restore, vulnerability, incident and provenance evidence | Operator-supplied evidence; protected values are recursively redacted | Evidence-period policy and tenant legal process |

Tenant ID is present on every tenant-owned metadata row; forced row-level security also permits
read-only inheritance of instance lifecycle policies. The database stores no raw service credential
in these resources. EPIC-608 lifecycle jobs now enforce workflow-data retention while audit evidence
continues under its independent policy and legal holds.

## Repeatable ephemeral databases

Tests may call `create_ephemeral_database(base_url)`, apply `migration_directory()` with
`apply_migrations()`, compare `schema_fingerprint()` and `seed_fingerprint()`, then call
`drop_ephemeral_database(base_url, database.name)` in `finally`. The drop helper accepts only generated
`amesh_test_<16 lowercase hex>` names. The database role needs `CREATEDB`; production runtime roles
must not receive that privilege.
