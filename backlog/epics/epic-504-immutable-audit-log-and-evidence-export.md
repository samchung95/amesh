# EPIC-504 — Immutable audit log and evidence export

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Auditor
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Record security and administrative actions as tamper-evident, queryable evidence.

## In scope

- [x] **URS-F-0526** — The system shall audit authentication, authorization, resource mutation, execution intervention, secret use, policy decision and administration events.
- [x] **URS-F-0527** — The system shall include actor, delegated identity, tenant, resource, action, outcome, reason, source, timestamp, correlation and trace identifiers.
- [x] **URS-F-0528** — The system shall redact protected values while retaining enough metadata for investigation.
- [x] **URS-F-0529** — The system shall write audit events transactionally with the associated state change where possible.
- [x] **URS-F-0530** — The system shall detect gaps or tampering through append-only storage, hash chaining or signed export batches.
- [x] **URS-F-0531** — The system shall apply independent audit retention and legal-hold policy.
- [x] **URS-F-0532** — The system shall export audit events to files, object storage and external security information systems.
- [x] **URS-F-0533** — The system shall restrict audit access and audit access to the audit log itself.
- [x] **URS-F-0835** — The system shall generate scoped compliance evidence packages containing access reviews, change evidence, audit records, backup and restore evidence, vulnerability results, incident records and provenance without exposing protected values.

## Implementation completion evidence

- 2026-08-23 — EPIC-504 is complete. PostgreSQL migration 0046 now normalizes/redacts every existing audit producer, fills attributable investigation context, and serializes each tenant into a SHA-256 chain with retention anchors. The authorized audit API queries and verifies the ledger, records audit reads, manages independent retention and legal holds, and produces signed file/object-store exports. Existing signed realtime subscriptions provide the external-SIEM path. Compliance evidence records are recursively redacted and checksummed, and deterministic signed ZIP packages contain access, change, audit, backup/restore, vulnerability, incident and provenance sections without claiming certification. Evidence: [`audit-and-compliance.md`](../../docs/api/audit-and-compliance.md), [`audit-evidence.md`](../../docs/operations/audit-evidence.md), [`0046_audit_evidence_ledger.sql`](../../migrations/0046_audit_evidence_ledger.sql), [`test_audit_repository.py`](../../tests/adapters/postgres/test_audit_repository.py), [`test_audit_api.py`](../../tests/api/test_audit_api.py), and [`test_audit_artifacts.py`](../../tests/test_audit_artifacts.py). Shared security/privacy/compliance NFRs remain In Progress until the full audited-action catalog, whole-platform retention inventory, control crosswalk, independent package review and pre-GA evidence period are complete.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-009** — Security-relevant actions shall generate attributable audit records even when denied. Target: 100% coverage of the audited-action catalog in automated tests.
- [ ] **URS-NFR-PRIVACY-002** — The platform shall retain only data required by configured orchestration, audit and operational policy. Target: Data inventory maps every persisted field to purpose, retention and sensitivity.
- [ ] **URS-NFR-COMPLIANCE-001** — The architecture, operating procedures and evidence model shall be designed for SOC 2 and ISO/IEC 27001 readiness without representing readiness as certification. Target: Before GA, every applicable control has a versioned mapping to an owner, implementation, evidence source, collection cadence, test and recorded gap; certification itself is outside the v1 release gate.

## Dependencies

- EPIC-007
- EPIC-500

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization, audit and administrative end-to-end tests.
- Compliance evidence export, redaction and authorization tests.
- Endpoint-to-audit traceability suite.
- Privacy and schema review.
- Control-crosswalk validation and sample evidence-package review by an independent security or compliance reviewer.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0526, URS-F-0527, URS-F-0528, URS-F-0529, URS-F-0530, URS-F-0531, URS-F-0532, URS-F-0533, URS-F-0835
- Non-functional requirements: URS-NFR-SECURITY-009, URS-NFR-PRIVACY-002, URS-NFR-COMPLIANCE-001
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
