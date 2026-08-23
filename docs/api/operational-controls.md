# Operational controls API

The operational-controls API lets an instance administrator announce service conditions and apply
durable maintenance or emergency controls without restarting AMESH. Tenant-scoped requests use the
authenticated tenant; instance-scoped records are visible across tenants only to instance admins.

## Announcements

`POST /api/v1/announcements` publishes an announcement with a title, message, `INFO`, `WARNING` or
`CRITICAL` severity, an `INSTANCE`, `TENANT` or `NAMESPACE` audience, a start time and an expiry.
`GET /api/v1/announcements` returns announcements active for the caller and optional namespace.
`DELETE /api/v1/announcements/{id}?expectedVersion={version}` deactivates one announcement with
optimistic concurrency protection.

The web shell polls this collection every ten seconds and renders active announcements until their
expiry. Namespace announcements require a namespace; instance and tenant announcements reject one.

## Maintenance and kill switches

`POST /api/v1/operational-controls` activates a `MAINTENANCE` or `KILL_SWITCH` record. Every request
must provide a name, reason, at least one boundary, a running-work policy, and either an expiry or a
review time. Supported scopes are `INSTANCE`, `TENANT`, `NAMESPACE`, `FLOW`, `PLUGIN` and `RUNNER`.
The corresponding target fields are required only for targeted scopes.

Boundaries are independent:

| Boundary | Effect while controlled |
| --- | --- |
| `AUTHORING` | Rejects flow, app, dashboard, plugin and namespace authoring. |
| `NEW_EXECUTIONS` | Rejects manual, scheduled, trigger and backfill launches. |
| `TRIGGERS` | Stops scheduler and trigger acceptance or claiming. |
| `API_WRITES` | Rejects tenant-mutating API requests with HTTP `423`. |
| `WORKER_DISPATCH` | Applies the selected policy before executor dispatch. |

Already accepted work follows `runningWorkPolicy`: `CONTINUE` permits dispatch, `DRAIN` preserves
the durable work without dispatching it, and `CANCEL` records a force-cancel intervention at the next
recovery or dispatch boundary. Accepted trigger occurrences deferred by a control do not consume a
delivery attempt.

`GET /api/v1/operational-controls` returns effective state, resource version and component
acknowledgements. `POST /api/v1/operational-controls/{id}/actions` performs version-checked
`EXTEND`, `BYPASS` or `DEACTIVATE` actions. A bypass requires `bypassUntil`; extensions require a
new expiry or review time. Expired controls become `EXPIRED` automatically during evaluation or
listing. The administration surface remains exempt from `API_WRITES` controls so an authorized
operator cannot lock out the recovery action.

## Propagation and evidence

PostgreSQL emits `amesh_control_changes` notifications when announcement or control records change.
Service cycles also poll the durable tables, so a missed notification does not lose a control.
Webserver, scheduler, executor and legacy worker cycles persist their control version
acknowledgements, which are included in control responses.

`GET /api/v1/operational-control-events` exposes immutable `ACTIVATE`, `EXTEND`, `BYPASS`,
`DEACTIVATE` and `EXPIRE` evidence with actor, reason and timestamp. Resource versions reject stale
actions with `409`.

## Qualification boundary

Local PostgreSQL integration tests qualify durable trigger deferral, scheduler rejection, worker
drain or cancel decisions, automatic expiry, audit evidence, tenant isolation and component
acknowledgement. Multi-node rolling-upgrade transfer and failure-zone qualification remains governed
by the distributed high-availability conformance program; this API does not by itself certify an
external cluster topology.
