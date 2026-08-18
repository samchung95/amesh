# ADR-014: SOC 2 and ISO/IEC 27001 readiness

- **Status:** Accepted
- **Decision question:** Q-018
- **Date:** 2026-08-15

## Context

Platform engineers and enterprise operators require evidence-backed security and governance. Certification depends on an operating organisation and cannot be provided solely by application code.

## Decision

Design AMESH architecture, procedures and evidence for **SOC 2 and ISO/IEC 27001 readiness** before GA.

Maintain a versioned control crosswalk linking applicable controls to owners, requirements, implementation, tests, evidence sources, cadence and gaps. Provide permission-scoped evidence export.

Do not represent readiness as certification. Formal certification is not a v1 release gate unless a later decision changes scope.

## Consequences

- Audit, access review, change management, vulnerability, backup, incident and release evidence must be structured and exportable.
- Evidence export requires authorization, redaction, integrity protection and audit of the export itself.
- Applicable controls and gaps become release-visible rather than informal documents.
- Independent compliance or security review is required for the readiness package.

## Traceability

See `docs/governance/compliance-readiness.md`, `URS-NFR-COMPLIANCE-001`, `URS-F-0834`, `URS-F-0835`, `EPIC-504`, `EPIC-612` and `EPIC-805`.
