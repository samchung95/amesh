# PostgreSQL migrations

`0001_foundation.sql` is a provisional review schema, not a production migration history.

It establishes the first explicit persistence concepts for:

- tenants, namespaces, flows and immutable flow revisions;
- executions and immutable execution events;
- command inbox and transactional outbox records;
- a PostgreSQL durable work queue with claims, lease expiry and fencing tokens;
- worker registrations, task runs and task attempts;
- generic fenced leases and audit events.

Production migration tooling must add transactional migration locking, compatibility windows, online index strategies, rollback/forward-fix policy and upgrade fixtures before this schema is used beyond local development.
