# ADR-032: Content-addressed flow revisions and pointer-based promotion

- Status: Accepted
- Date: 2026-08-22
- Owners: EPIC-006

## Context

AMESH already stores canonical flow definitions in PostgreSQL revision rows and pins executions to
those rows with a foreign key. EPIC-006 requires automatic immutable history, revision diffs,
promotion metadata, safe restore, lifecycle control and reference-aware deletion.

Python's standard `difflib` produces established unified text diffs. RFC 6902 defines a compact JSON
Patch representation for machine consumers. A third-party diff package would not supply AMESH's
revision allocation, PostgreSQL transaction, authorization, audit or lifecycle rules.

## Decision

1. Hash the canonical semantic definition without its author-supplied revision number. Reapplying the
   same revision and semantics is idempotent; an unused forward revision is preserved, while changed
   content that collides with an existing revision receives the next integer revision.
2. Keep every revision definition immutable. Promotion, disablement, archiving and restore update the
   flow's selected-revision pointer and lifecycle only; restore never edits or duplicates history.
3. Store actor, source, source commit, environment, deployment metadata and a versioned resource
   catalog resolution with each new revision. An execution's existing revision foreign key therefore
   pins both definition and resolution evidence.
4. Return a unified JSON diff for people and deterministic RFC 6902 `add`, `remove` and `replace`
   operations for machines. Lists are replaced atomically when their value changes.
5. Emit every revision state change to a tenant-isolated event ledger and transactional outbox, plus
   an audit record. Selected revisions and revisions referenced by executions or direct audit evidence
   cannot be deleted.

## Consequences

- No dependency is added; `difflib` and AMESH's small JSON Patch encoder cover the required contract.
- Installed third-party package resolution can extend the stored resolution object without changing
  the execution-to-revision pin.
- Draft, disabled and archived flows retain readable history but cannot launch new executions until
  promoted to active.
