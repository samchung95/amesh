# EPIC-305 — Plugin registry, signing, SBOM and marketplace metadata

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Distribute plugins with verifiable provenance and enough metadata for safe adoption.

## In scope

- [ ] **URS-F-0328** — The system shall publish immutable plugin bundles by name, semantic version and digest.
- [ ] **URS-F-0329** — The system shall store license, source, documentation, supported platform range, SDK range and changelog metadata.
- [ ] **URS-F-0330** — The system shall attach software bills of materials, vulnerability reports and provenance attestations.
- [ ] **URS-F-0331** — The system shall sign registry metadata and plugin artifacts and verify signatures before installation.
- [ ] **URS-F-0332** — The system shall support allowlisted registries, mirrors, proxies and offline export or import.
- [ ] **URS-F-0333** — The system shall display popularity, maintenance, certification and security status without treating them as trust guarantees.
- [ ] **URS-F-0334** — The system shall yank compromised versions without deleting historical metadata needed by pinned executions.
- [ ] **URS-F-0335** — The system shall provide an OSS registry API and a self-hosted registry implementation.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-007** — Official artifacts shall include verifiable source provenance, SBOM and signatures. Target: 100% of official release artifacts have published checksums, SBOMs and signatures.
- [ ] **URS-NFR-PORTABILITY-001** — The self-hosted platform shall not require a proprietary control service or license server for any GA capability. Target: Air-gapped reference deployment passes the full core and governance acceptance suite.

## Dependencies

- EPIC-301
- EPIC-612

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Plugin SDK contract, sandbox and integration tests.
- Release pipeline policy gate.
- Offline installation and test run.
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

- Functional requirements: URS-F-0328, URS-F-0329, URS-F-0330, URS-F-0331, URS-F-0332, URS-F-0333, URS-F-0334, URS-F-0335
- Non-functional requirements: URS-NFR-SECURITY-007, URS-NFR-PORTABILITY-001
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
