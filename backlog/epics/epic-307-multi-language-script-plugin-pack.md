# EPIC-307 — Multi-language script plugin pack

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Run scripts in common languages with consistent dependency, file, log, metric and output behavior.

## In scope

- [x] **URS-F-0344** — The system shall support shell, Python, Node.js, Java, R and PowerShell execution through task runners.
- [x] **URS-F-0345** — The system shall support inline scripts, namespace files, repository files and packaged source artifacts.
- [x] **URS-F-0346** — The system shall allow runtime dependency installation only under explicit network and supply-chain policy.
- [x] **URS-F-0347** — The system shall offer documented helpers for outputs, metrics, logs and file manifests.
- [x] **URS-F-0348** — The system shall select default images by immutable release and permit organization-approved overrides.
- [x] **URS-F-0349** — The system shall capture interpreter and package metadata for reproducibility.
- [x] **URS-F-0350** — The system shall prevent interpolation injection by separating script content, arguments and environment values.
- [x] **URS-F-0351** — The system shall provide sample flows and contract tests for each supported language.

## Implementation completion evidence

- 2026-08-23 — EPIC-307 is complete. First-party `script.shell`, `script.python`, `script.node`, `script.java`, `script.r` and `script.powershell` tasks compile into the existing local, Docker or Kubernetes runner contract without placing script content or environment values in command arguments. Inline, namespace, repository-artifact and packaged-workspace source contracts share existing verified file staging and manifests. Operator-owned policy supplies digest-pinned default images, restricts overrides to approved digests and denies runtime dependency installation unless immutable dependency records, a dependency command and allowlisted restricted egress are all explicit. Execution output captures runner metrics plus interpreter, image, source-origin and package metadata. Evidence: [`test_scripts.py`](../../tests/tasks/test_scripts.py), [`run-scripts.md`](../../docs/how-to/run-scripts.md), [`examples/scripts`](../../examples/scripts), [`resource-catalog.json`](../../schemas/resource-catalog.json) and [`TESTLOG.md`](../../TESTLOG.md).

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

- Functional requirements: URS-F-0344, URS-F-0345, URS-F-0346, URS-F-0347, URS-F-0348, URS-F-0349, URS-F-0350, URS-F-0351
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
