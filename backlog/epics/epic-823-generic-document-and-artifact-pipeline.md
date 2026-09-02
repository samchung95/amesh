# EPIC-823 — Generic document and artifact pipeline

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Workflow developer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Let workflows ingest files such as PDFs as typed provenance-preserving artifacts while plugins supply replaceable parsers and extractors.

## In scope

- [x] A tenant-scoped typed artifact contract carries content address, media type, size, digest, provenance and retention without exposing storage credentials or host paths.
- [x] A provider-neutral document-extractor plugin contract accepts exact artifact references and returns versioned structured text, metadata and chunks with source locators.
- [x] Upload, selection and workflow-node paths use existing object storage, artifact events, plugin policy and task execution rather than a parallel file system.
- [x] At least one exactly pinned PDF extractor implementation or conformance fixture proves end-to-end pages, text, metadata and typed downstream consumption.
- [x] Size, page, token and time limits plus unsupported, encrypted, malformed and parser-failure states are explicit and tested with tenant isolation and safe filename handling.
- [x] The UI can select or upload an artifact, configure an extractor from catalog options and inspect provenance and result in the execution trace.

## Implementation completion evidence

- 2026-08-26 — EPIC-823 is complete. Added a tenant-scoped, content-addressed `amesh.artifact-ref/v1` contract and artifact catalog/read APIs; a provider-neutral `amesh.document-extractor/v1` task-plugin contract; and the exactly pinned `pypdf==6.16.1` reference extractor with immutable source, parser and derived-result provenance. The ordinary task/plugin runtime enforces media type, checksum, byte, page, token, wall-time and output limits in a killable child process and returns explicit unsupported, encrypted, malformed and parser failures without committing a result artifact. The namespace UI uploads/selects PDF artifacts, the guided builder emits exact input/output bindings, and the execution Data view renders provenance, parser pin, pages, chunks and extracted text. Twenty-seven consolidated Python contract/API/PostgreSQL/MinIO/integration assertions, Ruff, strict mypy, 41 frontend unit assertions, scoped ESLint, the production build, six responsive Playwright journeys and a live deployed Chromium journey passed. The rebuilt Compose deployment remained ready at migration 66/66; live execution `01a03e31-1a44-70f0-92b9-e1d8095ac1fa` completed `SUCCESS` with downstream typed consumption and persisted `document-result.json`. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`extract-pdf-artifact.md`](../../docs/how-to/extract-pdf-artifact.md), [`namespace-resources.md`](../../docs/operations/namespace-resources.md), [`execution-files.md`](../../docs/operations/execution-files.md), and [`ADR-060`](../../docs/adr/060-content-addressed-document-extractor-contract.md).

## Explicit non-goals

- Embedding domain-specific document semantics in core
- Allowing plugins direct storage credentials or unrestricted host filesystem access

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-010
- EPIC-208
- EPIC-303
- EPIC-507
- EPIC-822

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Artifact contract, content-address and tenant-isolation tests.
- Extractor plugin conformance and dependency-license checks.
- Malformed, encrypted, oversized and timeout PDF tests.
- Workflow typed-output and execution-evidence integration tests.
- Responsive UI and live local PDF workflow journey.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] A user can upload a PDF, run an exactly pinned extractor and pass typed output to a downstream workflow node.
- [x] Every derived document result retains immutable source and parser provenance.
- [x] Parser implementations remain replaceable plugins under ordinary AMESH limits, policy and evidence.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Untrusted parsers and malformed files can exhaust resources or expose host data.
- Derived text can lose page or source provenance and make downstream evidence unverifiable.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
