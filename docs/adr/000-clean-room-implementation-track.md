# ADR-000: Strict clean-room implementation track

- **Status:** Accepted
- **Decision question:** Q-002
- **Date:** 2026-08-15

## Context

AMESH must reproduce a broad observable compatibility surface without copying Kestra source code, visual design or protected documentation expression.

## Decision

Use public product documentation, public schemas and APIs, independently observed black-box behavior, and independently written conformance fixtures as specification inputs. Keep research provenance. Do not provide Kestra source code, UI assets or documentation prose to implementation agents.

When ambiguity exists, a reference researcher records an observable behavioral specification and test fixture. An implementation agent receives that specification rather than upstream implementation material.

## Consequences

- Reduces source-contamination and trademark risk.
- Requires more black-box research, differential testing and source-range provenance.
- Exact compatibility claims must be backed by version-pinned evidence.
- Contributions can be rejected when their provenance cannot be established.
- This ADR does not provide legal advice; public release still requires licence and trademark review.

## Revisit triggers

- The product owner explicitly chooses a source-derived implementation.
- Legal counsel changes the required clean-room boundary.
- A compatibility target cannot be specified through observable behavior or public contract material.

## Traceability

See `docs/product/decision-register.md`, `docs/governance/clean-room-policy.md`, `requirements/URS.md` and `EPIC-000`.
