# EPIC-402 — CLI and generated client SDKs

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `api`
- **Primary persona:** Developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Make all common platform operations scriptable and suitable for CI/CD.

## In scope

- [x] **URS-F-0414** — The system shall provide a cross-platform CLI for authentication, configuration, flows, executions, namespaces, files, plugins and administration.
- [x] **URS-F-0415** — The system shall support human-readable, JSON and quiet output modes with stable exit codes.
- [x] **URS-F-0416** — The system shall support declarative apply, diff, delete and export workflows from files or standard input.
- [x] **URS-F-0417** — The system shall generate typed Python, JavaScript or TypeScript, Java and Go clients from the supported API contract.
- [x] **URS-F-0418** — The system shall publish clients with version compatibility metadata and retry or pagination helpers.
- [x] **URS-F-0419** — The system shall store credentials using operating-system secure storage when available.
- [x] **URS-F-0420** — The system shall support non-interactive service-account authentication in CI.
- [x] **URS-F-0421** — The system shall provide shell completion and command documentation generated from the command model.

## MVP implementation progress

- 2026-08-21 — W6 verified CLI commands for flow validation/apply/list, execution create/get/list/logs and webhook invocation against the MVP REST contract. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`test_cli.py`](../../tests/test_cli.py), and [`cli.py`](../../src/amesh/cli.py). Generated SDKs and the broader CLI surface remain open.

## Implementation completion evidence

- 2026-08-23 — Completed the cross-platform CLI command model with named profiles, human/JSON/quiet output, stable exit codes, declarative flow apply/diff/export/delete, administration commands and explicit destructive previews.
- 2026-08-23 — Added operating-system keyring credential storage, non-interactive AMESH_SERVICE_ACCOUNT_TOKEN authentication, generated shell completions and generated command reference documentation.
- 2026-08-23 — Generated and compiled pinned OpenAPI Python, TypeScript, Java and Go clients with compatibility metadata, pagination helpers, deterministic release archives and Docker-local freshness checks. Fresh 41-migration focused and full regression suites, static checks and deployment smoke evidence are recorded in TESTLOG.md. Shared usability and generated-artifact NFRs remain open for their other owning epics.

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-005** — Destructive UI and CLI operations shall present impact, scope and recovery consequences before execution. Target: All destructive-action catalog entries have preview or explicit force semantics.
- [ ] **URS-NFR-MAINTAINABILITY-005** — Generated schemas, SDKs, documentation, traceability files and issue bodies shall be reproducible and checked for drift. Target: Repository validation produces no uncommitted generated changes.

## Dependencies

- EPIC-400

## Architecture impact

- Primary bounded area: `api`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- tests/test_cli.py and tests/test_cli_epic402.py::test_urs_f_0414_0415_0419_0420_profiles_secure_tokens_and_output_modes plus test_urs_f_0414_0416_declarative_stdin_diff_export_delete_and_admin.
- tests/test_cli_epic402.py::test_urs_f_0414_0415_0419_0420_profiles_secure_tokens_and_output_modes.
- tests/test_cli_epic402.py::test_urs_f_0414_0416_declarative_stdin_diff_export_delete_and_admin.
- tests/test_sdk_contracts.py::test_urs_f_0417_0418_generated_sdk_manifest_matches_supported_contract and generated Python, TypeScript, Java and Go build checks.
- tests/test_sdk_contracts.py::test_urs_f_0417_0418_generated_sdk_manifest_matches_supported_contract and test_urs_f_0418_sdk_release_archives_are_reproducible.
- tests/test_cli_epic402.py::test_urs_f_0414_0415_0419_0420_profiles_secure_tokens_and_output_modes and deployed AMESH_SERVICE_ACCOUNT_TOKEN CLI smoke.
- tests/test_cli_epic402.py::test_urs_f_0421_completion_and_docs_are_generated_from_parser and docs/cli/reference.md freshness check.
- Interaction and CLI contract tests.
- CI regeneration and clean-tree check.
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

- Functional requirements: URS-F-0414, URS-F-0415, URS-F-0416, URS-F-0417, URS-F-0418, URS-F-0419, URS-F-0420, URS-F-0421
- Non-functional requirements: URS-NFR-USABILITY-005, URS-NFR-MAINTAINABILITY-005
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
