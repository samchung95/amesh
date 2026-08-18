# Definition of done

An epic or requirement is complete only when the relevant items below are evidenced.

## Product

- Observable behavior and failure semantics are documented.
- Requirement and acceptance criteria are approved.
- Intentional differences and compatibility level are explicit.
- User-facing terminology does not imply unsupported guarantees.

## Engineering

- Implementation follows module boundaries and accepted ADRs.
- State changes are idempotent, versioned and recoverable.
- Duplicate, restart, timeout, cancellation and stale-owner cases are covered where relevant.
- Schema, API, event, DSL and plugin contracts have compatibility tests.
- Migrations have preflight, upgrade and recovery guidance.

## Security and tenancy

- Authentication and authorization paths are tested.
- Cross-tenant and negative-access tests exist.
- Secret, PII and log redaction are validated.
- Threat model and dependency review are updated.
- Untrusted code stays behind approved isolation.

## Operations

- Health, metrics, logs, traces and alerts exist.
- Resource limits and overload behavior are documented.
- Backup, restore, purge and reconciliation consequences are addressed.
- Performance budgets are measured for critical paths.

## Documentation and release

- Public docs, examples, runbooks and migration notes are updated.
- URS-to-epic-to-test evidence is linked.
- Clean-room and license declarations pass.
- `make validate` and release gates pass.
