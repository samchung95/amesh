# ADR-060: Content-addressed document extractor task contract

- **Status:** Accepted
- **Date:** 2026-08-26

## Context

Workflows need to ingest PDFs without exposing object-store credentials or creating a document-specific
filesystem. Parsers must be replaceable while downstream nodes receive one stable, source-locatable
shape. The existing namespace-file store, task plugin runtime, bounded working directory and execution
artifact/evidence path already own those responsibilities.

For the embedded PDF implementation, the evaluated choices were a custom parser, `pdfminer.six` and
`pypdf`. A custom parser would duplicate a mature security-sensitive format implementation.
`pdfminer.six` is capable but brings a broader extraction stack than this page/text/metadata reference
needs. `pypdf` is pure Python, supports the required PDF operations and publishes clear package and
license metadata.

## Decision

Project stored files as immutable tenant-scoped `amesh.artifact-ref/v1` values containing an opaque
exact reference, content address, media type, size, SHA-256 digest, provenance and retention state.
Resolve the opaque reference inside AMESH and pass only a bounded materialized file to tasks.

Define `amesh.document-extractor/v1` as a specialization of the existing plugin `task` contract. Pin
the embedded reference implementation to `pypdf==6.16.1` and record its wheel SHA-256
`63fec31c4092ae50b6729beedcb469055b60d20c834bde1c402df241f371f644` in every result. The package
declares `BSD-3-Clause`; the lock retains the exact source and wheel hashes. See the official
[PyPI package record](https://pypi.org/project/pypdf/) and
[license](https://github.com/py-pdf/pypdf/blob/main/LICENSE).

Run the parser in a killable child process and enforce task/workspace output limits plus explicit byte,
page, token and wall-time limits. Persist successful JSON through the ordinary execution artifact and
lineage path. External task plugins may advertise the same output schema and replace the embedded
implementation under normal resolution and policy.

## Consequences

- Upload, retention, authorization, tenant fencing and evidence remain owned by existing platform
  services.
- Structured results retain exact source, page/offset and parser provenance for downstream nodes.
- Storage URIs, credentials and host paths do not enter the public artifact or extractor contracts.
- Scanned-image OCR and other formats require separate plugins; they do not expand the core contract.
