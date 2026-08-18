# EPIC-307 — Multi-language script plugin pack

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Run scripts in common languages with consistent dependency, file, log, metric and output behavior.

## In scope

- [ ] **URS-F-0344** — The system shall support shell, Python, Node.js, Java, R and PowerShell execution through task runners.
- [ ] **URS-F-0345** — The system shall support inline scripts, namespace files, repository files and packaged source artifacts.
- [ ] **URS-F-0346** — The system shall allow runtime dependency installation only under explicit network and supply-chain policy.
- [ ] **URS-F-0347** — The system shall offer documented helpers for outputs, metrics, logs and file manifests.
- [ ] **URS-F-0348** — The system shall select default images by immutable release and permit organization-approved overrides.
- [ ] **URS-F-0349** — The system shall capture interpreter and package metadata for reproducibility.
- [ ] **URS-F-0350** — The system shall prevent interpolation injection by separating script content, arguments and environment values.
- [ ] **URS-F-0351** — The system shall provide sample flows and contract tests for each supported language.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-208
- EPIC-209
- EPIC-306

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Plugin SDK contract, sandbox and integration tests.
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

- Functional requirements: URS-F-0344, URS-F-0345, URS-F-0346, URS-F-0347, URS-F-0348, URS-F-0349, URS-F-0350, URS-F-0351
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
