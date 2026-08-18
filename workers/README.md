# AMESH worker workspace

Workers claim durable tasks from PostgreSQL, renew expiring leases, enforce fencing tokens, invoke a selected runner and commit bounded results. Workers do not make workflow-graph decisions.

The first runner implementations are:

1. local process for trusted development and controlled hosts;
2. Docker/OCI for isolated containers;
3. Kubernetes for cluster-scheduled task attempts.

`LISTEN/NOTIFY` may wake an idle worker, but a notification never grants ownership. Ownership exists only after a successful transactional claim of the durable queue row.

See `docs/architecture/workers-and-runners.md`, `docs/architecture/postgresql-transport.md`, `proto/worker/v1/worker.proto`, EPIC-101 and EPIC-209.
