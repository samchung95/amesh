# Project governance

## Current model

The initial repository uses a benevolent-maintainer model while architecture and scope are being formed.
The repository owner is the provisional lead maintainer. This file must be replaced with a multi-maintainer
model before GA.

## Roles

- **Contributor:** submits issues, research, code, tests or documentation.
- **Reviewer:** reviews within a bounded area and verifies requirement evidence.
- **Maintainer:** merges changes, releases artifacts and manages roadmap or security processes.
- **Technical steering group:** future group that accepts major ADRs, compatibility promises and LTS policy.

## Decisions

Routine changes may merge after deterministic gates and an independent agent-review quorum. Cross-cutting or public-contract decisions require an ADR.
Licence, trademark, compatibility promise, governance, security-policy and destructive migration changes require named human approval until a steering group exists.

## Releases

A release requires traceability, the documented Docker-local qualification gate, security scans,
migration classification, known limitations and signed artifacts. Publication, signing and provenance
attestation are explicit operator actions, not hidden side effects of local verification. Every stable
or security release requires named human approval. No implementer, agent or maintainer may be the sole
approver of its own security-sensitive release content.

## Funding and commercial services

Sponsors and hosted-service providers do not receive hidden software capabilities. Funding, employment
and vendor conflicts relevant to a decision must be disclosed.
