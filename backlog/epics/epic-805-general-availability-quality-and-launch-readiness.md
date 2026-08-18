# EPIC-805 — General availability quality and launch readiness

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `quality`
- **Primary persona:** Maintainer
- **Parity scope:** AMESH differentiator; not a Kestra-parity claim

## Outcome

Define objective evidence required before declaring the first stable release.

## In scope

- [ ] **URS-F-0790** — The system shall close or explicitly waive every Must requirement with named owner and rationale.
- [ ] **URS-F-0791** — The system shall pass security, performance, accessibility, upgrade, backup, restore, chaos and conformance release gates.
- [ ] **URS-F-0792** — The system shall publish support, compatibility, deprecation, LTS and vulnerability response policies.
- [ ] **URS-F-0793** — The system shall complete at least two independent production-like reference deployments.
- [ ] **URS-F-0794** — The system shall prove recovery from worker, executor, scheduler, PostgreSQL queue, projection and object-storage disruptions.
- [ ] **URS-F-0795** — The system shall verify documentation, installation, rollback and disaster-recovery procedures with participants outside the core implementation team.
- [ ] **URS-F-0796** — The system shall publish known limitations and parity gaps without misleading compatibility claims.
- [ ] **URS-F-0797** — The system shall freeze public API, event, DSL and plugin contracts for the supported major release.

## Non-functional requirements

- [ ] **URS-NFR-MAINTAINABILITY-004** — Every epic shall include unit, contract, integration or end-to-end evidence appropriate to its risk. Target: All Must requirements have at least one linked automated or manual verification record before GA.
- [ ] **URS-NFR-COMPLIANCE-001** — The architecture, operating procedures and evidence model shall be designed for SOC 2 and ISO/IEC 27001 readiness without representing readiness as certification. Target: Before GA, every applicable control has a versioned mapping to an owner, implementation, evidence source, collection cadence, test and recorded gap; certification itself is outside the v1 release gate.
- [ ] **URS-NFR-PERFORMANCE-010** — The v1 distributed reference deployment shall qualify against the accepted profile M workload on the documented on-premises Kubernetes topology. Target: 100,000 executions per day, 1,000 active task runs, 50 sustained task starts per second and 10 million retained execution records.
- [ ] **URS-NFR-AVAILABILITY-003** — The first stable release and later hardened profiles shall have documented and tested recovery point and recovery time objectives. Target: First stable release gate: RPO <= 48 hours and RTO <= 8 hours. Post-GA hardened reference target: RPO <= 4 hours and RTO <= 4 hours; the tighter target is not a v1 release blocker.

## Dependencies

- EPIC-611
- EPIC-612
- EPIC-704
- EPIC-705
- EPIC-706

## Architecture impact

- Primary bounded area: `quality`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Release-gate evidence review.
- Traceability validator and release gate.
- Control-crosswalk validation and sample evidence-package review by an independent security or compliance reviewer.
- Published 24-hour mixed-workload, retention-query and failure-recovery benchmark on a fixed bill of materials.
- Isolated restore exercise on the on-premises Kubernetes reference topology, with measured data-loss window and service-restoration time.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [ ] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [ ] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [ ] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [ ] Security, tenant isolation, redaction and audit behavior are reviewed.
- [ ] Documentation, examples, migration notes and operational runbooks are updated.
- [ ] Performance and recovery budgets are measured when this epic is on a critical path.
- [ ] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- The first stable release intentionally uses the minimal RPO/RTO gate; deployments with stricter recovery needs require stronger operator configuration and evidence.
- Profile M qualification must not be generalized to untested hardware or topology.
- SOC 2 and ISO/IEC 27001 readiness does not constitute certification.

## Traceability

- Functional requirements: URS-F-0790, URS-F-0791, URS-F-0792, URS-F-0793, URS-F-0794, URS-F-0795, URS-F-0796, URS-F-0797
- Non-functional requirements: URS-NFR-MAINTAINABILITY-004, URS-NFR-COMPLIANCE-001, URS-NFR-PERFORMANCE-010, URS-NFR-AVAILABILITY-003
- Source scope: AMESH differentiator; not a Kestra-parity claim
