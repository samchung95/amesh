# ADR-013: Full side-by-side migration

- **Status:** Accepted
- **Decision question:** Q-017
- **Date:** 2026-08-15

## Context

Flow-only import is insufficient for users replacing an established orchestrator. They may need identity, governance, historical execution, logs, artifacts and audit continuity.

Direct in-place conversion of an undocumented or version-sensitive source database creates excessive corruption and clean-room risk.

## Decision

Implement migration option C through versioned export/import bundles and side-by-side verification.

Migration includes resources, revisions, identity and authorization data, system configuration, plugin inventory, historical executions, task runs, state records, logs, artifacts and audit evidence. Secret plaintext is never extracted.

The importer is dry-runnable, resumable, idempotent, checksummed and produces stable identifier maps, reconciliation results, cutover guidance and rollback evidence.

## Consequences

- Migration becomes a substantial M7 programme rather than a YAML converter.
- Historical data may be retained with explicit source-provenance limitations rather than fabricated native semantics.
- Large migrations require throttling, chunking, capacity planning and rehearsed cutover.
- A Must mismatch or unresolved required secret reference blocks cutover.
- Source systems remain read-only during the rollback window where practical.

## Traceability

See `docs/architecture/migration.md`, `EPIC-704` and `URS-F-0829` through `URS-F-0833`.
