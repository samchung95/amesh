# Execution files and working directories

Use `inputFiles` to materialize internal object-storage or `nsfile:///` references before a local
shell task starts. Keys are relative POSIX paths inside the attempt directory. Use `outputFiles` for
exact paths or globs, or `outputManifest` for a JSON array of additional relative paths.

```yaml
tasks:
  - id: transform
    type: core.shell
    inputFiles:
      data/input.csv: "{{ inputs.file }}"
    outputFiles:
      - "reports/*.json"
    outputManifest: generated-files.json
    workspaceQuotaBytes: 104857600
    retainDiagnosticsOnFailure: true
    command: [python, transform.py]
```

Each attempt has a different directory and receives `WORKING_DIR` and `OUTPUT_DIR`. Input content is
checked against object size and SHA-256 metadata. Output collection rejects traversal and symlinks,
streams each file to object storage, rolls back an incomplete multi-file upload, persists lineage and
removes local data. The quota covers all user files present in the workspace.

Use `core.workingDirectory` when child Process tasks must share local files. Children are always
sequential; `maxConcurrency`, when supplied, must be `1`. Parent inputs are installed once and parent
outputs are collected when the group terminates.

```yaml
tasks:
  - id: workspace
    type: core.workingDirectory
    inputFiles:
      source.txt: nsfile:///source.txt
    outputFiles: [result.txt]
    maxConcurrency: 1
    tasks:
      - id: prepare
        type: core.shell
        command: [python, -c, "open('intermediate.txt','w').write(open('source.txt').read())"]
      - id: finish
        type: core.shell
        command: [python, -c, "open('result.txt','w').write(open('intermediate.txt').read())"]
```

List and download committed files with:

```text
GET /api/v1/executions/{executionId}/files
GET /api/v1/executions/{executionId}/files/{artifactId}
```

Both routes require execution view permission and preserve tenant isolation. Artifact rows expose
metadata and lineage; payload bytes stream from object storage. The local and Docker/OCI profiles are
qualified here. Docker transfers the bounded workspace through the Engine archive API and an owned
named volume; it does not expose the control-plane host filesystem to the task. Kubernetes workspace
transfer remains with its runner epic.

`core.document.extract` uses this same workspace boundary. Its exact namespace artifact is
materialized as an input, and a successful run commits `document-result.json` with execution,
task-attempt and logical-path lineage. The typed task output and committed JSON both use
`amesh.document-extractor/v1`; a failed or over-limit extraction commits no result artifact.
