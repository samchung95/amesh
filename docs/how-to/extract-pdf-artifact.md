# Extract a PDF as a typed workflow artifact

Use the document pipeline when a workflow needs page-aware PDF text without giving a task object-store
credentials or a host path.

## Guided path

1. Select the target namespace and open **Namespaces**.
2. Under **PDF artifacts**, choose a PDF. The UI creates a safe `documents/...pdf` path and uploads it
   through the existing namespace-file API.
3. Open **Workflows**, create or edit a flow in **Guided** mode, and add **Extract PDF document**.
4. Select the uploaded artifact and set maximum bytes, pages, tokens, chunk size and wall time.
5. Add a downstream step, select the extractor as its dependency, then save, validate and run.
6. Open the execution **Trace**. The document card shows source and parser provenance, page/chunk counts
   and extracted text. `document-result.json` is also available under execution files.

The artifact selector uses the complete immutable object returned by:

```text
GET /api/v1/namespaces/{namespace}/artifacts
```

Its `reference`, version and SHA-256 digest must remain together. Do not replace the reference with an
object-store URI.

## Canonical YAML shape

The guide edits the same YAML used by the API. The abbreviated example below shows the relationship;
copy the complete `artifact` object from the artifact API response.

```yaml
tasks:
  - id: extract
    type: core.document.extract
    artifact:
      schemaVersion: amesh.artifact-ref/v1
      reference: nsfile:///documents/report.pdf?version=1&sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      contentAddress: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      tenantId: default
      namespace: examples
      path: documents/report.pdf
      version: 1
      mediaType: application/pdf
      sizeBytes: 12345
      checksumSha256: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      provenance:
        source: namespace-file
        originNamespace: examples
        createdBy: operator
        createdAt: 2026-08-26T00:00:00Z
        lineage: [namespace-file, examples, documents/report.pdf]
      retention:
        retentionUntil: null
        legalHold: false
    source: document.pdf
    inputFiles:
      document.pdf: nsfile:///documents/report.pdf?version=1&sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    outputFiles: [document-result.json]
    limits:
      maxBytes: 10485760
      maxPages: 100
      maxTokens: 20000
      chunkTokens: 1000
      wallTimeSeconds: 60

  - id: publish
    type: core.return
    dependsOn: [extract]
    value: "{{ outputs.extract }}"
```

The extractor output has contract version `amesh.document-extractor/v1` and contains the immutable
source artifact, extractor/parser pin, metadata, pages, chunks, combined text and token count.

## Expected failures

The task fails explicitly when the artifact is outside the execution tenant/namespace, its content
identity does not match the materialized input, the source name is unsafe, the PDF is unsupported,
encrypted or malformed, or a byte, page, token, output or wall-time limit is exceeded. No partial
`document-result.json` is committed when extraction fails.
