# ADR-015: Agent quorum and human release authority

- **Status:** Accepted
- **Decision question:** Q-021
- **Date:** 2026-08-15

## Context

AMESH is developed primarily by elastic AI engineering teams. Requiring a human for every routine merge would unnecessarily limit throughput, while fully autonomous security, legal and stable-release decisions would assign critical accountability to systems that cannot hold it.

## Decision

Allow ordinary protected-branch changes to merge when deterministic gates pass and a configured quorum of independent review and verification agents approves.

Require named human approval for:

- security-sensitive changes;
- licence or governance changes;
- destructive production migrations;
- changes that waive or weaken Must controls;
- every stable release.

No implementation agent may approve its own work or be the sole verifier.

## Consequences

- Merge eligibility is a reproducible policy result, not model confidence.
- Agent identities, roles, evidence and conflicts must be recorded.
- Security classification must be conservative and auditable.
- Human release authority may delegate preparation but not final accountability.
- Emergency procedures require explicit scope, expiry and retrospective review.

## Traceability

See `docs/governance/ai-engineering-model.md`, `URS-F-0836`, `URS-F-0837`, `URS-NFR-AIENGINEERING-001` and `URS-NFR-AIENGINEERING-004`.
