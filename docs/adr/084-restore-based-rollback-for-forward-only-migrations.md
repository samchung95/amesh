# ADR-084: Restore-based rollback for forward-only migrations

Status: accepted.

Context: AMESH migrations are checksum-protected SQL files applied in one forward order by Compose,
Helm and `amesh-migrate`. Existing deployments record each applied filename and checksum, so changing a
historical SQL file would break those deployments. The manifest contains rollback guidance, but the
runtime did not distinguish destructive migrations from ordinary expand-only changes. At least one
migration defines destructive behavior, and operators need an explicit gate before a forward-only
upgrade can remove or irreversibly rewrite retained data.

Decision:

- Keep existing migration SQL immutable. Flag destructive migrations in `migrations/destructive.json`
  with one reason per file instead of editing historical SQL or checksums.
- Migrations remain forward-only. Rollback is restore-based: restore the verified pre-upgrade
  PostgreSQL/object-storage backup, then redeploy the previous AMESH release. AMESH will not maintain
  generic down migrations for historical files.
- The migration runner computes pending migrations before applying SQL. If any pending migration is
  listed as destructive and the database already has applied migrations, the runner refuses to proceed
  unless `MIGRATION_BACKUP_CONFIRMED_AT` is an ISO-8601 UTC timestamp within
  `MIGRATION_BACKUP_MAX_AGE_HOURS` (24 hours by default). Future or unparsable markers are refused.
- Fresh installs do not require the marker because no AMESH data exists yet. Databases with no pending
  destructive migration, including fully migrated databases, also start without it.
- Compose and Helm expose the marker to their migration jobs. A valid marker emits a warning because
  the recovery path is still backup restore plus previous-release redeploy.
- Future migrations should use expand/contract where possible. Contract or retention steps that delete
  rows, truncate, drop table/column/type state or irreversibly overwrite retained values must be added
  to the destructive manifest.

Alternatives: adding down migrations would imply reversible semantics for data deletion and redaction
that AMESH cannot guarantee. Editing existing SQL comments or metadata would break checksum history or
hide the flag inside files that must remain immutable. Warning-only behavior would let unattended
pre-upgrade jobs proceed without verified recovery evidence.

Consequences: Operators must take and verify a backup before destructive upgrades and carry the marker
through Compose or Helm. The default path for fresh installations remains unchanged. Existing
deployments already at the latest manifest have no pending destructive migration and need no marker on
restart. The manifest honesty test keeps obvious destructive SQL from being added without a declared
reason, but human review still owns borderline calls such as irreversible redaction backfills.
