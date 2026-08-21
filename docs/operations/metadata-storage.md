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

`GET /health` is process liveness. `GET /ready` verifies PostgreSQL and exact migration parity and
returns HTTP 503 when either fails. `GET /metrics` exposes:

- `amesh_database_health`;
- `amesh_database_pool_size` and `amesh_database_pool_checked_out`;
- `amesh_database_query_duration_seconds` and `amesh_database_slow_queries_total`;
- `amesh_database_migrations_applied` and `amesh_database_migrations_expected`.

Set `DATABASE_SLOW_QUERY_SECONDS` to the desired positive threshold; the default is 0.5 seconds.
These metrics have no tenant, SQL text or identifier labels, avoiding unbounded cardinality and data
leakage.

## Metadata data inventory

| Data | Persisted fields | Purpose | Sensitivity | Retention owner |
| --- | --- | --- | --- | --- |
| Trigger definitions | tenant, revision, key, type, canonical definition, enabled flag, creator, timestamp | Rebuild and schedule the exact flow revision | Internal; definition may contain operator configuration | Flow revision lifecycle; EPIC-608 defines purge enforcement |
| Worker registration | tenant, group, instance, version, capabilities, labels, state, heartbeat, version/audit/lifecycle timestamps | Claim routing, fencing and worker health | Internal infrastructure metadata | Worker lifecycle; EPIC-608 defines stale-record purge |
| Execution logs | tenant, execution/task identity, level, logger, message, structured fields, redaction flag, timestamp | Execution diagnosis and audit evidence | Potentially sensitive; callers must redact secret-derived values before persistence | Tenant retention policy; EPIC-608 defines purge enforcement |
| Execution metrics | tenant, execution/task identity, name, kind, numeric value, unit, labels, timestamp | Execution performance and outcome analysis | Internal operational metadata | Tenant retention policy; EPIC-608 defines purge enforcement |
| Assets | tenant, provider key, type, display name, metadata, resource version, actor/timestamps | Catalog identity and current metadata | Classification is provider-defined and may be sensitive | Asset lifecycle; EPIC-507/608 define lineage and purge |

Tenant ID is present on every metadata row and forced row-level security applies to all four new
tables. The database stores no raw service credential in these resources. Retention execution remains
open under EPIC-608, so the shared privacy requirement remains In Progress.

## Repeatable ephemeral databases

Tests may call `create_ephemeral_database(base_url)`, apply `migration_directory()` with
`apply_migrations()`, compare `schema_fingerprint()` and `seed_fingerprint()`, then call
`drop_ephemeral_database(base_url, database.name)` in `finally`. The drop helper accepts only generated
`amesh_test_<16 lowercase hex>` names. The database role needs `CREATEDB`; production runtime roles
must not receive that privilege.
