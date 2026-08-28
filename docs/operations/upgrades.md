# Supported upgrades and LTS operations

AMESH publishes its machine-readable release policy at `GET /api/v1/upgrades/policy`. The checked-in
catalog declares supported LTS windows, minimum component and protocol versions, directed upgrade
paths, message-schema overlap, rollback windows, capacity limits and restoration guidance. A version
is not supported merely because its database schema can be applied.

The current supported path is `0.1.0` to `0.2.0`. Both releases require PostgreSQL 15, Python 3.12,
API v1, message schema 1 and plugin protocol `amesh.plugin.rpc/v1`. Release `0.1.0` ends at migration
`0032_configuration_feature_flags.sql`; release `0.2.0` ends at
`0055_admission_policy.sql`.

The unreleased merge-candidate schema continues through
`0067_protected_trigger_payloads.sql`. That current-head boundary is not a new catalogued release and
does not change the supported `0.1.0` to `0.2.0` upgrade path below. Development deployments must run
the complete manifest before starting current-head binaries.

## Operator sequence

1. Create and verify a coordinated recovery point before changing application or schema state.
2. Run `amesh upgrade preflight --from-version 0.1.0 --to-version 0.2.0`.
3. Resolve every `BLOCKED` check. Review warnings and retain the report fingerprint as change evidence.
4. Apply the target schema boundary with `amesh-migrate --target 0055_admission_policy.sql`.
5. For a rolling-compatible report, replace roles in the reported order and verify each role before
   moving forward. The service registry rejects versions outside the published overlap contract.
6. Preview historical event work with `amesh upgrade events-preview`. After verifying the recovery
   point, run `amesh upgrade events-upcast --reason <change-record> --force` until zero remain.
7. Run the postflight report and retain its checks, warnings, restoration guidance and fingerprint.

The web console exposes the same release catalog, preflight/postflight reports, rolling plan and
bounded event upcast under **Administration → Upgrades**.

## Service-role health schema note

Migration `0060_service_role_health.sql` adds the `DEGRADED` registry state plus nullable last-success
and last-failure timestamps, a bounded redacted failure summary and a consecutive-failure counter.
Apply it before deploying binaries that advertise aggregate role readiness. During a forward fix, keep
liveness probes active, treat `DEGRADED` as not ready and preserve the recorded health evidence; do not
run a binary that expects these columns against an older schema.

## Preflight and postflight gates

The report checks the source and target support windows, schema boundary and immutable migration
checksums, online/expand-only migration compatibility, typed runtime configuration, plugin protocol
compatibility, all stored flow revisions, object-storage metadata inventory, database/queue/execution
capacity, live component skew, persisted event schemas and rollback evidence. Unsafe component skew,
newer unknown event schemas, invalid stored flows, inaccessible storage or schema drift blocks the
operation and includes remediation.

Preflight accepts either the source or already-applied target schema so the same command can be rerun
after an interrupted migration. Postflight requires the target boundary. Reports are snapshots; rerun
the appropriate phase after any remediation.

## Explicit configuration and event migration

Use `amesh upgrade migrate-config flow|plugin <input> --target-version <version> --output <path>` to
produce a canonical document. Flow validation errors and plugin target-range incompatibility stop the
conversion; the tool never silently publishes the result.

Persisted event upcasts are bounded to 10,000 rows per request, default to 1,000, use locked batches,
are resumable and require the exact preview phrase `UPCAST <eligible-count>`. Every accepted batch
writes immutable audit evidence. Do not bypass the preview or `--force` gate.

## Rollback boundary

The `0.1.0` to `0.2.0` path declares a 168-hour rollback window. Restore the coordinated pre-upgrade
PostgreSQL and object-storage recovery point; do not run older binaries against a database beyond
their published schema boundary. Persisted event upcasts and config outputs are forward conversions,
so restoration—not reverse mutation—is the recovery procedure if their validation fails.
