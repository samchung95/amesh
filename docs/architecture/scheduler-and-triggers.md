# Scheduler and triggers

## Scheduler ownership

Each applied temporal trigger has one PostgreSQL `scheduler_states` row keyed by tenant, flow revision
and trigger. A scheduler replica claims a due row using database time, a bounded lease and a monotonically
increasing fencing token. Completion requires the same live owner and token, so an expired or superseded
replica cannot advance the cursor. A replacement replica resumes from the persisted `next_fire_at`.

Execution creation additionally uses the stable occurrence identity described below. If a connection is
lost after execution creation but before cursor completion, the replacement scheduler receives the same
execution identity and can advance the cursor without launching a duplicate. Worker database cycles
retry after connection-level failures at the configured poll interval, allowing the SQLAlchemy pool to
establish a new PostgreSQL connection after failover.

## Temporal model

`core.cron` evaluates a five-field cron expression as local wall time in its declared IANA timezone.
Timezone data comes from the runtime `zoneinfo` database, including historical offset changes. A local
time skipped by a daylight-saving transition does not fire; an overlapping local time fires once at the
earliest corresponding UTC instant.

`core.interval` accepts an ISO-8601 duration. It is an elapsed-time schedule anchored at the explicit
`start` instant or, when omitted, the Unix epoch; its timezone is retained for trigger context and display.
Both trigger types support aware `start` and `end` bounds, `disabled`, `paused`, a boolean `condition`,
`misfirePolicy`, `misfireGraceSeconds` and `maxCatchUp`.

## Misfire policies

- `SKIP`: move to the next future occurrence.
- `CATCH_UP`: create every missed occurrence subject to admission.
- `COALESCE`: create one occurrence representing a missed range.
- `BACKFILL`: record the missed range as requiring backfill and continue any occurrence still inside the
  grace window. EPIC-106 owns creation and lifecycle of the first-class backfill resource.

Every evaluation persists its decision and missed count. Catch-up work is bounded by `maxCatchUp`; a
remaining backlog is consumed by later evaluations rather than by one unbounded transaction.

## Trigger occurrence protocol

A schedule occurrence identity contains trigger type, namespace, flow ID, immutable flow revision,
trigger ID and scheduled UTC instant. Execution creation treats that identity as an idempotency key.
The scheduler:

1. claims the persisted cursor with a database-time lease and fence;
2. calculates bounded due occurrences and applies flow, trigger, calendar and condition constraints;
3. creates idempotent scheduled executions according to the misfire policy;
4. advances the cursor only while the same fenced ownership remains live;
5. persists an explanation and missed-occurrence count for operators.

`GET /api/v1/flows/{namespace}/{flow_id}/schedules/{trigger_id}/preview` returns the next 1–100
occurrences plus an eligibility explanation. It requires the same tenant and flow-view authorization as
other flow reads and never mutates schedule state.

Webhook triggers use signed or authenticated endpoints, request size limits, replay protection and
idempotency keys. Realtime trigger connectors apply backpressure and cannot retain unbounded memory.
