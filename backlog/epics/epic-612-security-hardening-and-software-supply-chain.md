# EPIC-612 — Security hardening and software supply chain

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `security`
- **Primary persona:** Security engineer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Reduce platform and workload attack surface and produce verifiable release artifacts.

## In scope

- [ ] **URS-F-0678** — The system shall maintain a threat model covering control plane, workers, runners, plugins, storage, identity, UI and supply chain.
- [ ] **URS-F-0679** — The system shall run static analysis, dependency scanning, secret scanning, container scanning and dynamic security tests.
- [ ] **URS-F-0680** — The system shall generate SBOMs and signed provenance for source, binaries, containers, charts and plugin bundles.
- [ ] **URS-F-0681** — The system shall use least-privilege service identities and short-lived credentials between components.
- [ ] **URS-F-0682** — The system shall apply secure defaults for headers, cookies, TLS, filesystem permissions, network and deserialization.
- [ ] **URS-F-0683** — The system shall provide vulnerability disclosure, security advisory and patch support procedures.
- [ ] **URS-F-0684** — The system shall perform independent penetration testing before GA and after material security changes.
- [ ] **URS-F-0685** — The system shall document residual risks for in-process plugins, local process runners and administrative capabilities.
- [ ] **URS-F-0834** — The system shall maintain a versioned machine-readable crosswalk from applicable SOC 2 Trust Services Criteria and ISO/IEC 27001 controls to owners, requirements, implementations, tests, evidence sources and recorded gaps.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-002** — Components, workers, plugins and runners shall receive only the identities and capabilities required for their role and current operation. Target: Reference deployments pass privilege review with no shared administrator credentials.
- [ ] **URS-NFR-SECURITY-007** — Official artifacts shall include verifiable source provenance, SBOM and signatures. Target: 100% of official release artifacts have published checksums, SBOMs and signatures.
- [ ] **URS-NFR-SECURITY-010** — Fresh production-oriented configurations shall fail closed for authentication, plugin trust, network exposure and secrets. Target: Security baseline scanner reports no critical unsafe defaults.
- [ ] **URS-NFR-MAINTAINABILITY-006** — Runtime dependencies shall have declared owners, update policy and license compatibility. Target: No unknown-license dependency and no unwaived critical known vulnerability in a release.
- [ ] **URS-NFR-OPERABILITY-004** — Administrators shall be able to generate a redacted diagnostic bundle without exposing secrets or unrelated tenant data. Target: Canary-secret and cross-tenant scans pass for generated bundles.
- [ ] **URS-NFR-COMPLIANCE-001** — The architecture, operating procedures and evidence model shall be designed for SOC 2 and ISO/IEC 27001 readiness without representing readiness as certification. Target: Before GA, every applicable control has a versioned mapping to an owner, implementation, evidence source, collection cadence, test and recorded gap; certification itself is outside the v1 release gate.

## Dependencies

- EPIC-001
- EPIC-303
- EPIC-500

## Architecture impact

- Primary bounded area: `security`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Security integration tests and threat-model review.
- Compliance control-crosswalk schema and completeness tests.
- Threat-model review and deployment policy tests.
- Release pipeline policy gate.
- Configuration conformance and container scan.
- Dependency and license scanning.
- Security test with seeded sensitive data.
- Control-crosswalk validation and sample evidence-package review by an independent security or compliance reviewer.
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

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0678, URS-F-0679, URS-F-0680, URS-F-0681, URS-F-0682, URS-F-0683, URS-F-0684, URS-F-0685, URS-F-0834
- Non-functional requirements: URS-NFR-SECURITY-002, URS-NFR-SECURITY-007, URS-NFR-SECURITY-010, URS-NFR-MAINTAINABILITY-006, URS-NFR-OPERABILITY-004, URS-NFR-COMPLIANCE-001
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
