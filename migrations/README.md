# PostgreSQL migrations

The MVP image applies the ordered `*.sql` files through `python -m amesh.migrations`. The runner uses a PostgreSQL advisory transaction lock, records each filename and SHA-256 checksum in `amesh_schema_migrations`, skips already-applied files and rejects checksum drift. The Helm chart runs it as a pre-install/pre-upgrade hook before server or worker rollout.

It establishes the first explicit persistence concepts for:

- tenants, namespaces, flows and immutable flow revisions;
- executions and immutable execution events;
- command inbox and transactional outbox records;
- a PostgreSQL durable work queue with claims, lease expiry and fencing tokens;
- worker registrations, task runs and task attempts;
- generic fenced leases and audit events.
- canonical labels, annotations, actor, lifecycle, tombstone and resource-version metadata for managed tenant, namespace, flow, execution and worker records.

Migration `0003_canonical_resource_metadata.sql` is the EPIC-002 forward migration. It preserves existing UUID records while new application-created runtime records use UUIDv7. Compatibility windows, online index strategies, rollback/forward-fix policy and upgrade qualification remain later backlog work.
