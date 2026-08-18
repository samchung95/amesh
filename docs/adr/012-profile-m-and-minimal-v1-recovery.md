# ADR-012: Profile M scale and minimal v1 recovery gate

- **Status:** Accepted
- **Decision questions:** Q-015, Q-016
- **Date:** 2026-08-15

## Context

AMESH needs measurable release targets. Unbounded “enterprise scale” language is not a useful acceptance criterion, while overly aggressive recovery goals would delay the first stable release without evidence of user need.

## Decision

Qualify the v1 distributed reference deployment at **profile M**:

- 100,000 executions per day;
- 1,000 active task runs;
- 50 sustained task starts per second;
- 10 million retained execution records.

Maintain a 99.9% monthly control-plane availability objective, excluding declared maintenance.

Use the following first-stable-release disaster-recovery gate:

- RPO no more than 48 hours;
- RTO no more than 8 hours.

Track a post-GA hardened reference target of RPO no more than 4 hours and RTO no more than 4 hours, but do not make it a v1 blocker.

## Consequences

- Profile M must be demonstrated on a published fixed bill of materials.
- The minimal RPO/RTO must be clearly labelled as unsuitable for workloads requiring tighter recovery.
- Backup and restore tests are release gates even though the initial targets are lenient.
- Claims above profile M require separate evidence.
- Failure injection occurs during qualification, not only in an idle environment.

## Traceability

See `URS-NFR-PERFORMANCE-010`, `URS-NFR-AVAILABILITY-003`, `EPIC-609`, `EPIC-611` and `EPIC-805`.
