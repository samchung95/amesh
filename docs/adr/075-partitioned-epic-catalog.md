# ADR-075: Partition the canonical epic catalog by lifecycle state

- **Status:** Accepted
- **Date:** 2026-09-03
- **Epic:** EPIC-838

## Context

`backlog/epics.json` has grown to about 1.1 MB and 134 records. Of those records, 115 are
completed, and each embeds the same body that already exists as a Markdown file. The active
planning surface therefore carries mostly historical data, but backlog generation, validation and
GitHub bootstrap tooling still require a complete catalog.

Removing embedded bodies would be a separate compatibility change because existing scripts and
tests consume the current record shape. Archiving only the Markdown bodies would not materially
reduce the JSON manifest, and fixed ID-range archives would make reopening an epic awkward.

## Decision

Keep `backlog/epics.json` as the active canonical manifest and move records whose state is `done`
to `backlog/archive/epics.done.json`. The active manifest declares its archive files and records
active, archived and total counts in metadata.

A shared standard-library loader reads the active manifest and every declared archive, rejects
unsafe or missing paths, duplicate epic IDs and records in the wrong lifecycle partition, then
returns one deterministic catalog sorted by wave and epic ID. A shared writer applies the same
state-based partition, preserves the full epic record shape and writes stable two-space-indented
JSON with a trailing newline. Publication uses atomic per-file replacement and stages a superset
before either partition removes a record. An interrupted cross-file transition can therefore leave
a marked staged duplicate for regeneration to reconcile, but cannot silently lose the moving epic.

Planning regeneration, validation and GitHub backlog bootstrap must consume the combined catalog.
Generated Markdown and traceability artifacts continue to include active and archived epics, so
existing epic links and historical evidence remain valid. Completing or reopening an epic moves
the record automatically on the next regeneration rather than requiring manual archive edits.

## Consequences

- The frequently edited active manifest becomes small while completed history remains checked in.
- Consumers must use the shared catalog loader instead of reading `backlog/epics.json` directly.
- Archive corruption, undeclared paths and duplicate records fail planning validation rather than
  producing partial output.
- Full record bodies remain duplicated for compatibility; removing that duplication can be a
  separately versioned change if it later becomes worthwhile.

## Rejected alternatives

- Remove embedded bodies now: it changes the established planning-tool contract and is unnecessary
  to make the active file manageable.
- Archive only Markdown files: the large JSON records would remain in the active manifest.
- Partition by epic number or milestone: lifecycle state, not identifier range, determines whether
  a record belongs in the active planning surface.
