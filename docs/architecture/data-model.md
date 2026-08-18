# Data model

The schema is normalized for authoritative state and append-only evidence. Large payloads are referenced
by object-storage URI.

## Principal aggregates

| Aggregate | Natural key | Runtime key | Notes |
|---|---|---|---|
| Tenant | tenant slug | tenant UUID | Mandatory outside explicit single-tenant mode |
| Namespace | tenant + dotted namespace | namespace UUID | Hierarchical permissions and inheritance |
| Flow | tenant + namespace + flow ID | flow UUID | Stable identity |
| Flow revision | flow + revision number/hash | revision UUID | Immutable canonical definition |
| Execution | execution ID | sortable UUID | Pinned revision and plugin resolution |
| Task run | execution + task path + iteration | task-run UUID | Logical task across attempts |
| Task attempt | task run + attempt number | attempt UUID | Fenced worker ownership |
| Trigger | flow revision + trigger ID | trigger UUID | Definition |
| Trigger instance | trigger + service shard | instance UUID | Checkpoint and operational state |
| Worker | worker identity | worker UUID | Capabilities, labels and heartbeat |
| Backfill | backfill ID | UUID | Generates occurrence set |
| Plugin package | name + version + digest | package UUID | Immutable artifact |
| Asset | provider + external key | asset UUID | Catalog and lineage |
| App/approval | tenant-scoped key | UUID | Human interaction resources |

## Core tables

```text
tenants, namespaces
flows, flow_revisions, flow_revision_plugins
executions, execution_events
task_runs, task_attempts, task_run_events
commands_inbox, messages_outbox, consumed_messages
dispatches, leases, resource_reservations
trigger_definitions, trigger_instances, trigger_occurrences
workers, service_instances
backfills, backfill_occurrences
namespace_files, kv_entries, secret_metadata
artifacts, artifact_references, cache_entries
logs, metrics, execution_outputs
plugin_packages, plugin_types, plugin_policies
users, groups, roles, bindings, service_accounts, api_tokens
audit_events, policy_decisions
assets, lineage_edges
retention_jobs, reconciliation_jobs
```

## Event storage

Events are append-only and include aggregate ID, aggregate version, event type, schema version, tenant,
correlation, causation, actor, event time and payload. The current snapshot is optimized state, not a
replacement for transition evidence.

The first implementation is not a universal event-sourcing framework: resource CRUD that does not need
replay may use ordinary revision history plus audit events. Execution and task state must be replayable.

## Tenant isolation

Every tenant-owned row contains `tenant_id`; every unique constraint and index includes it where
appropriate. Repositories require tenant context. PostgreSQL row-level security is evaluated as defense
in depth, not the sole authorization layer.

## Storage boundaries

- Metadata database: identifiers, state, structured small outputs and object references.
- Object storage: files, artifacts, large outputs, import/export bundles and plugin packages.
- Event bus: bounded messages and references, never large files.
- Search: denormalized authorized projections that can be deleted and rebuilt.
