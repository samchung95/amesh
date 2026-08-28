# EPIC-208 — Working directories and execution files

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Move files safely between tasks, runners and object storage.

## In scope

- [x] **URS-F-0242** — The system shall create a unique disposable working directory for each task attempt.
- [x] **URS-F-0243** — The system shall materialize declared input files from internal storage with checksum verification.
- [x] **URS-F-0244** — The system shall collect declared output files by path, glob or manifest and upload them atomically.
- [x] **URS-F-0245** — The system shall prevent path traversal, symlink escape and cross-task filesystem access.
- [x] **URS-F-0246** — The system shall support a shared working-directory flowable with explicit lifetime and concurrency rules.
- [x] **URS-F-0247** — The system shall clean local working data after upload while retaining diagnostics on configured failures.
- [x] **URS-F-0248** — The system shall stream large files and enforce per-task storage quotas.
- [x] **URS-F-0249** — The system shall record file lineage from source artifact through transformations and outputs.

## Implementation completion evidence

- 2026-08-22 — EPIC-208 is complete. AMESH now provides unique disposable attempt workspaces; checksum-verified streamed internal inputs; atomic path/glob/manifest output collection; traversal and symlink confinement; sequential shared WorkingDirectory lifetime; configured failure diagnostics; workspace quotas; durable logical-path and transformation lineage; and authorized file list/download APIs. Evidence: [`test_working_directory.py`](../../tests/workflow/test_working_directory.py), [`test_working_directories.py`](../../tests/executor/test_working_directories.py), [`test_namespace_resources_api.py`](../../tests/api/test_namespace_resources_api.py), [`working-directory.yaml`](../../examples/working-directory.yaml), [`execution-files.md`](../../docs/operations/execution-files.md) and [`038-bounded-streaming-task-workspaces.md`](../../docs/adr/038-bounded-streaming-task-workspaces.md).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-010
- EPIC-200

## Architecture impact

- Primary bounded area: `workflow`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- DSL validation plus end-to-end workflow conformance tests.
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

- Functional requirements: URS-F-0242, URS-F-0243, URS-F-0244, URS-F-0245, URS-F-0246, URS-F-0247, URS-F-0248, URS-F-0249
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
