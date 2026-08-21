# PostgreSQL migrations

The MVP image applies the exact order declared in `manifest.json` through `python -m amesh.migrations`. The runner validates contiguous filenames, transaction wrappers, migration mode, online-compatibility classification and rollback guidance before connecting. It then checks PostgreSQL 15+, uses a serializable transaction and advisory lock, records each filename and SHA-256 checksum in `amesh_schema_migrations`, skips already-applied files, and rejects checksum drift or database migrations absent from the manifest. The Helm chart runs it as a pre-install/pre-upgrade hook before server or worker rollout.

It establishes the first explicit persistence concepts for:

- tenants, namespaces, flows and immutable flow revisions;
- executions and immutable execution events;
- command inbox and transactional outbox records;
- a PostgreSQL durable work queue with claims, lease expiry and fencing tokens;
- worker registrations, task runs and task attempts;
- generic fenced leases and audit events.
- canonical labels, annotations, actor, lifecycle, tombstone and resource-version metadata for managed tenant, namespace, flow, execution and worker records.
- PostgreSQL-authoritative principals, group memberships, roles, permissions, scoped bindings, namespace authorization boundaries and revocation versions.
- HMAC-digested API and derived workload credentials, principal revocation epochs and per-token usage windows.

Migration `0003_canonical_resource_metadata.sql` is the EPIC-002 forward migration. It preserves existing UUID records while new application-created runtime records use UUIDv7.

Migration `0004_authorization.sql` is the EPIC-500 forward migration. It seeds immutable built-in role definitions and attaches statement-level policy-version triggers to every authorization policy table. The migration is forward-only; restore or upgrade qualification remains governed by the later HA/DR epics.

Migration `0005_service_credentials.sql` is the EPIC-501 forward migration. It adds principal
credential epochs plus credential lifecycle and independent fixed-window quota tables. Only keyed
digests and non-secret metadata are persisted; token material is not a schema field.

Migration `0006_multi_tenancy.sql` is the EPIC-503 forward migration. It adds tenant policy,
storage-prefix and export state, makes worker and audit tenant ownership explicit, creates the
`amesh_runtime` role and forces tenant-ID RLS across runtime tables. Migration
`0007_tenant_queue_notifications.sql` replaces the shared queue wake-up channel with a channel derived
from the tenant UUID so one tenant's enqueue does not wake another tenant's waiter.
Migration `0008_restricted_tenant_resolution.sql` moves active-tenant lookup behind a minimal
security-definer function owned by a `NOLOGIN BYPASSRLS` resolver. Application database logins need
only membership in `amesh_runtime`; they do not need table ownership, superuser or direct tenant-table
access before entering the restricted role.
Migration `0009_tenant_administration_role.sql` adds a narrow `NOLOGIN` tenant-administration role
for lifecycle/export operations and a security-definer worker-group selector. Server logins that
perform tenant administration need membership in both `amesh_runtime` and `amesh_tenant_admin`;
worker-only logins need only `amesh_runtime`.

Migration `0010_execution_trigger_context.sql` persists the immutable trigger metadata supplied when an
execution is created, allowing the expression engine to restore cron and webhook context after process
or executor restarts.

Migration `0011_execution_event_model.sql` upgrades execution events to schema version 2 with stable
idempotency keys and reasons, versions command-inbox records, adds immutable task-run history and
transition-rejection evidence, and attaches tenant-isolated event-to-outbox triggers. Because the
trigger and event insert share the state transaction, uncommitted events cannot escape through the
outbox publisher.

Migration `0012_metadata_repository.sql` adds tenant-isolated trigger definitions, execution logs,
execution metrics and asset metadata; constrains execution, task-attempt, task-run and worker states;
and adds the composite identities required for tenant-safe foreign keys. It is an additive `expand`
migration. Stop new metadata writers and forward-fix if it fails; do not discard retained execution
evidence as a rollback shortcut.

Migration `0013_transport_dead_letters.sql` adds bounded outbox retry state, JSON envelope
constraints, partition-order support and tenant-isolated payload-safe dead-letter evidence. It is an
additive `expand` migration; stop publishers/consumers and forward-fix on failure while retaining queue,
outbox and quarantine rows.

## Migration modes

- `bootstrap` creates the initial schema and is only safe for an empty database.
- `expand` is additive and may run before all application instances are upgraded. The manifest checker
  rejects common contract DDL when such a migration is marked online-compatible.
- `exclusive` requires a controlled maintenance window because its data or privilege transition is
  not safe under mixed application versions.

Applied SQL is immutable. Correct an applied migration with a new forward migration. The exact
operator response for each migration is its `rollbackGuidance` entry in `manifest.json`.

For integration tests, `amesh.migrations.create_ephemeral_database()` creates a guarded
`amesh_test_<random>` database and `drop_ephemeral_database()` refuses any other name. Applying the
manifest twice must produce no second changes; `schema_fingerprint()` and `seed_fingerprint()` provide
canonical repeatability evidence across fresh databases.
