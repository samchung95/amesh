# PostgreSQL migrations

The MVP image applies the exact order declared in `manifest.json` through `python -m amesh.entrypoints.migrations`. The runner validates contiguous filenames, transaction wrappers, migration mode, online-compatibility classification and rollback guidance before connecting. It then checks PostgreSQL 15+, uses a serializable transaction and advisory lock, records each filename and SHA-256 checksum in `amesh_schema_migrations`, skips already-applied files, and rejects checksum drift or database migrations absent from the manifest. The Helm chart runs it as a pre-install/pre-upgrade hook before server or worker rollout. Operators and LTS fixtures can stop at an exact declared boundary with `python -m amesh.entrypoints.migrations --target 0032_configuration_feature_flags.sql`; an unknown boundary or a database already beyond it is rejected.

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
security-definer function owned by a `NOLOGIN BYPASSRLS` resolver. At this migration boundary,
tenant-runtime logins need only membership in `amesh_runtime`; they do not need table ownership,
superuser or direct tenant-table access before entering the restricted role. Current shipped service
lifecycle membership is described by migration `0009` below.
Migration `0009_tenant_administration_role.sql` adds a narrow `NOLOGIN` tenant-administration role
for lifecycle/export operations and a security-definer worker-group selector. Shipped server and
worker lifecycles require a `NOINHERIT` login with membership in both `amesh_runtime` and
`amesh_tenant_admin`. Tenant-scoped transactions explicitly use `SET LOCAL ROLE amesh_runtime`;
notification waits use session-scoped `SET ROLE amesh_runtime` and reset it before pool release.
Lifecycle and instance-wide work uses `SET LOCAL ROLE amesh_tenant_admin`.

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

Migration `0014_executor_dispatch.sql` makes an eligible `TaskRunStarted` event an explicit
`task-dispatch` outbox command while condition-skipped task starts remain ordinary task-run events. The
event and dispatch are committed atomically by the existing task-run event trigger.

Migration `0015_scheduler_state.sql` adds tenant-isolated next-fire cursors, database-time leases,
monotonic fencing tokens and latest schedule-decision evidence. It is additive; pause scheduler
replicas and forward-fix on failure without discarding cursor state.

Migration `0016_worker_protocol.sql` adds versioned worker registration fields, advertised runner
types and capacity, worker/task heartbeat evidence, cancellation acknowledgement and the queue-to-task
attempt identity used by atomic fenced dispatch. It is additive; pause worker claimers and forward-fix
on failure while retaining task attempts, queue rows and their fencing evidence.

Migration `0017_execution_interventions.sql` adds execution timeout and cancellation deadlines plus
attempt cancellation-request and normalized failure-category evidence. Partial indexes select due
execution timeouts and cancellation escalations without making node wall clocks authoritative. It is
additive; pause intervention writers and forward-fix on failure while retaining execution, task and
attempt history.

Migration `0018_subflow_relationships.sql` adds the tenant-isolated parent/child execution relation,
including invocation identity, parent attempt, pinned child revision, mode, nesting depth, propagation
policy, output mapping and actor evidence. Unique tenant-scoped invocation and child constraints make
recovery idempotent. It is additive; pause subflow launchers and forward-fix on failure while retaining
both executions and their task/event history.

Migration `0027_interactive_authentication.sql` adds local Argon2id credential state, opaque browser
session digests, CSRF digests, inactivity and absolute deadlines, rotation overlap, revocation evidence
and source-fingerprint rate windows. Passwords, session tokens and CSRF tokens are never schema fields.

Migration `0028_execution_evidence.sql` adds contextual log and metric fields, separate output and
artifact-reference projections, and one tenant-isolated monotonic evidence stream. State and task
evidence triggers write reconnectable events in the originating transaction; task-attempt evidence
remains the immutable recovery source.

Migration `0029_task_cache.sql` adds tenant-isolated task-result entries and an immutable cache
decision ledger. Leased population ownership, expiry, soft invalidation and provenance survive
executor restarts without making cached state authoritative over ordinary task and execution events.

Migration `0030_trigger_occurrence_runtime.sql` adds tenant-isolated trigger revision state, durable
checkpoints, a deduplicated occurrence queue and immutable occurrence events. Database-time leased
claims, retry/dead-letter state, replay lineage and flow-revision activation survive scheduler or
connector restart. It is additive; pause trigger consumers and forward-fix on failure while retaining
occurrence evidence.

Migration `0031_execution_checks.sql` adds reusable namespace/plugin policies, immutable effective
flow-revision definitions, database-time deadlines, independent evaluation evidence and a fenced,
retry-bounded violation-action queue. It is additive; pause deadline/action consumers and forward-fix
while retaining compliance evidence if application fails.

Migration `0032_configuration_feature_flags.sql` adds versioned instance, tenant and namespace
boolean flags. The scope shape is constrained in PostgreSQL, tenant runtime reads are RLS-filtered and
all administrative writes use the existing tenant-administration boundary and audit ledger.

Migration `0033_flow_revisions.sql` adds immutable revision provenance, lifecycle constraints and a
tenant-isolated flow revision event ledger with transactional outbox publication. A database trigger
protects selected revisions and revisions referenced by executions or direct audit evidence.

Migration `0034_flow_revision_event_retention.sql` makes revision events subordinate to explicit flow
purge while preserving them for the entire lifetime of their owning flow.

Migration `0054_retention_lifecycle.sql` adds instance/tenant/namespace/label workflow-data policies,
workflow legal holds, previewed and scheduled bounded purge jobs, durable external-object decisions and
transactional lifecycle events. Audit retention remains governed by its independent ledger policy.

Migration `0055_admission_policy.sql` adds immutable instance, tenant and namespace admission-policy
revisions plus tenant-isolated decision history. Policy revisions and every evaluation are also
written to the existing audit ledger by the application repository.

Migration `0035_conditional_task_control.sql` adds task-run-owned terminal results and control
evidence for durable conditional decisions and zero-attempt skips. Ordinary runnable results remain
authoritative on immutable task attempts.

Migration `0036_execution_lifecycle_hooks.sql` tags durable task runs as main, error, finally or
after-execution work and adds structured execution lifecycle evidence. A partial index supports
recovery of incomplete terminal hooks without changing primary execution-event authority.

Migration `0037_execution_data_contracts.sql` adds terminal flow outputs to the execution aggregate.
Inputs are validated before execution rows exist, while successful terminalization stores the bounded,
typed output rendering in the same transaction as the terminal event.

Migration `0038_workflow_metadata.sql` adds tenant-isolated namespace plugin defaults and metadata
policy, task-run and asset labels, and JSONB label indexes across flows, executions, task runs, assets
and backfills. Effective defaults remain pinned in immutable flow revisions.

Migration `0039_namespace_shared_resources.sql` adds tenant-isolated versioned namespace files,
strongly typed key-values with TTL/CAS/change cursors, and environment-provider secret references.
It also separates list, read, write and use authorization actions; secret values remain outside the
database, resource bundles and audit events.

Migration `0040_execution_file_lineage.sql` adds the bounded logical workspace path and ordered
source/transformation lineage to each execution artifact. Existing artifact references remain valid
with an empty lineage array.

Migration `0042_execution_debug_evidence.sql` replaces the state-evidence projection triggers so
future execution and task transitions include actor, causation, correlation and reason context in
their immutable evidence payload. It does not rewrite historical evidence. The migration is additive;
pause evidence consumers and forward-fix on failure while retaining the authoritative execution and
task event streams.

Migration `0043_dashboards.sql` adds tenant-isolated custom dashboard definitions, independent
viewer/editor ACLs and immutable definition events. Every create, update or delete publishes through
the transactional outbox. Built-in dashboards remain code-defined; the database stores only custom
API/GitOps definitions and their optimistic-concurrency version.

Migration `0044_search_projection.sql` adds the disposable tenant-hash-partitioned search document
projection, generated PostgreSQL full-text vectors, trigram/JSON/structured indexes, per-tenant
projection state and immutable rebuild/failure events with transactional outbox publication. It is
additive; stop optional projection cycles and forward-fix or rebuild these rows while authoritative
resources and orchestration continue.

Migration `0045_identity_federation.sql` adds immutable provider-subject identity links, one-time
OIDC/SAML state and replay fences, provider-owned group memberships, and tenant-bound SCIM resource
ownership. It is additive; disable the affected identity provider during a forward fix while existing
local authentication and previously provisioned principals remain available.

Migration `0046_audit_evidence_ledger.sql` adds recursive protected-field redaction, required audit
context, per-tenant SHA-256 chaining, retention anchors, independent retention policies, legal holds,
signed-export receipts and redacted compliance evidence. It backfills existing audit rows and is
additive; stop audit exporters and retention purges during a forward fix while preserving ledger rows.

Migration `0047_plugin_governance.sql` adds scoped plugin allow/deny rules, exact-version
quarantines and durable explained decisions. Instance rules remain visible inside each tenant policy
evaluation, tenant and namespace records are RLS-isolated, and all violations and policy changes use
the audit ledger. The migration is additive; pause policy changes and third-party starts during a
forward fix while preserving immutable flow-revision pins and historical plugin metadata.

Migration `0048_asset_catalog_lineage.sql` extends the existing tenant-scoped asset identity with
account, location, namespace, stewardship, health and materialization metadata. Durable observations
link READ/WRITE evidence to flows, executions, task runs and artifacts; declared, observed and
inferred asset edges retain confidence and provenance. The migration is additive; pause catalog
writes during a forward fix while preserving existing asset and execution history.

Migration `0049_workflow_apps_human_tasks.sql` adds immutable, flow-revision-pinned workflow-app
revisions plus durable participant-scoped approval tasks, actions and redacted notifications. Human
decisions enter a pending-resume state before the existing idempotent task-deferral contract resumes
execution, so worker reconciliation can finish safely after a process interruption.

Migration `0050_operational_controls.sql` adds scheduled announcements and durable instance, tenant,
namespace, flow, plugin and runner controls. Maintenance and kill-switch changes notify every local
component, retain acknowledgement and action history, automatically expire, and are sampled at API,
trigger, execution-admission and worker-dispatch boundaries.

Migration `0051_flow_tests_quality_gates.sql` adds tenant-scoped, revision-pinned flow-test
definitions and immutable result records plus namespace promotion gates. Results retain semantic,
plugin-set and simulator-version pins; definitions, runs and gate changes write audit evidence. The
migration is additive; disable affected gates before a forward fix so lifecycle promotion can resume.

Migration `0052_search_projection_backend.sql` adds the v2 blue-green PostgreSQL search backend.
Tenant generations can rebuild beside the active projection, while durable per-type checkpoints,
checksums, archive rows, versioned components and daily rollups make recovery and drift observable.
The v1 table remains available during rollout, so search can be disabled or forward-fixed without
placing authoritative orchestration state at risk.

Migration `0053_observability_trace_context.sql` adds bounded W3C trace carriers to execution and
task-run events. Tenant transactions set the active carrier and insert triggers capture it without
coupling event commits to an external collector. Empty carriers remain valid when tracing is disabled.

Migrations `0056_agent_primitives.sql` through `0078_projection_rebuild_execution_scope.sql` are the
unreleased current-head expansion after the tagged `0.2.0` boundary at migration 0055. They add the
provider-neutral model/MCP primitive ledger, versioned agent resources, durable sessions and memory,
role-health evidence, canonical evidence bundles, tool-provider invocation receipts, protected model
continuations, promotion/release gates, differential shadow comparisons, explicit evidence-event
kinds, protected trigger payloads, harness provenance pins, session administration and policies,
portable-transfer receipts, progress replay indexing, invocation accounting and explicit persisted
provider-bounded session-policy modes, followed by the restricted database-role grants required by
the audit, identity and instance control-plane repositories. The canonical order, mode, checksum and
rollback guidance for every migration remains `manifest.json`; apply current-head binaries through
migration 0078.

Migration `0069_agent_session_administration.sql` seeds the session-client, session-operator and
session-admin built-in roles, extends flow-author and operator with the session-resource grants, and
adds the fleet keyset and latest-attempt indexes. Session-specific permissions use the existing
canonical actions: `agent_session:create` is create, `agent_session:view` is view-own,
`agent_session:list` is view-all, `agent_session:manage` is control,
`agent_session_policy:manage` is policy-manage, `agent_session_migration:manage` is migrate and
`agent_session_administration:manage` is admin. During the compatibility period, existing clients
with `execution:view`, `execution:execute` or `execution:manage` continue to work through the session
boundary's documented fallback for the operations they already perform; new clients should request
the session-specific grants. An explicit session denial is not overridden by that fallback, and a
future breaking release must announce its removal.

Migration `0070_agent_session_policies.sql` adds tenant- and namespace-scoped, versioned session
policy revisions for admission, concurrency, token, cost, duration and retention limits plus
provider, harness and tool dependency allowlists. Revisions are immutable apart from the active
pointer, updates use an expected revision for optimistic concurrency, and each write records audit
evidence. Policy values and dependency identifiers are validated fail-closed before persistence;
launch enforcement is a later integration step.

Migration `0071_transfer_imports.sql` adds the tenant-isolated immutable import ledger shared by
portable profiles and session transfer records. The ledger binds one stable import identity to one
target tenant and bundle digest, so retries are idempotent and a changed bundle cannot silently
reuse an earlier import. It records metadata only; canonical resources, sessions, events, evidence
and artifacts remain in their existing authoritative tables.

Migration `0072_agent_session_progress.sql` adds a partial tenant/session/event-index lookup for
`progress.frame` replay. It is an online-compatible additive index over the canonical
`agent_session_events` journal and does not introduce a second transcript store or rewrite existing
events. If replay reads must be stopped during a forward fix, retain the journal and resume after the
index is repaired, as specified by the migration manifest.

Migration `0073_agent_invocation_accounting.sql` stores bounded provider-neutral usage and cost
checkpoints on model invocations and adds the explicit `IN_DOUBT` terminal state for ambiguous
external outcomes. Migration `0074_agent_session_policy_ceiling_mode.sql` persists `BOUNDED` versus
`PROVIDER_BOUNDED` and permits null application ceilings only for the latter. Because an older
application cannot reconstruct provider-bounded rows, migration 0074 is an exclusive rollout gate;
legacy bounded rows retain their finite values and default mode.

Migration `0075_restricted_repository_roles.sql` grants the existing `amesh_tenant_admin` role only
the tables and functions used by the global identity, audit and instance control-plane repository
paths. Tenant-scoped operations continue to use `amesh_runtime` with a transaction-local tenant UUID.
The admin role intentionally has `BYPASSRLS` for instance-wide work, so tenant-bearing admin reads use
explicit predicates and the additive grants keep the role's table surface narrow. Current binaries
fail closed when this grant boundary is absent instead of continuing as the owning or superuser login.
Migration `0076_authorization_binding_lock_grant.sql` adds the `UPDATE` privilege PostgreSQL requires
for the authorization repository's `SELECT ... FOR UPDATE` binding-deletion lock.
Migration `0077_restricted_operations_role.sql` adds the restored-state read privileges required by
`UPDATE ... RETURNING` and makes the fixed-name disposable-projection rebuild function execute as its
migration owner with a pinned search path.
Migration `0078_projection_rebuild_execution_scope.sql` revokes the inherited public and runtime
execution rights from that owner-privileged function and leaves only `amesh_tenant_admin` authorized.
Migration `0079_agent_progress_incremental_state.sql` adds tenant-bound progress cursors, per-source
sequence state, closed-segment state and producer timestamps so each accepted progress frame is
validated with bounded point/range reads instead of replaying the complete session journal. The
exclusive migration backfills those projections from the canonical journal, preserves historical
truncation receipts and enforces composite tenant/session and exact event ownership through foreign
keys. The session journal remains the authoritative transcript; the new tables are rebuildable
append-time projections.

## Migration modes

- `bootstrap` creates the initial schema and is only safe for an empty database.
- `expand` is additive and may run before all application instances are upgraded. The manifest checker
  rejects common contract DDL when such a migration is marked online-compatible.
- `exclusive` requires a controlled maintenance window because its data or privilege transition is
  not safe under mixed application versions.

Applied SQL is immutable. Correct an applied migration with a new forward migration. The exact
operator response for each migration is its `rollbackGuidance` entry in `manifest.json`.

For integration tests, `amesh.entrypoints.migrations.create_ephemeral_database()` creates a guarded
`amesh_test_<random>` database and `drop_ephemeral_database()` refuses any other name. Applying the
manifest twice must produce no second changes; `schema_fingerprint()` and `seed_fingerprint()` provide
canonical repeatability evidence across fresh databases.
