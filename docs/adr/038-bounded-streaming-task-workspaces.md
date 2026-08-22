# ADR-038: Bounded streaming task workspaces

- Status: Accepted
- Date: 2026-08-22
- Owner: EPIC-208

## Context

Runnable tasks need filesystem paths without making worker-local storage durable or allowing one
attempt to inspect another. The compatibility target places declared input files in a temporary task
directory, uploads declared output paths/globs, and provides a sequential WorkingDirectory flowable
for children that intentionally share files. The published Kestra behavior is documented in its
[input/output file guide](https://kestra.io/docs/scripts/input-output-files),
[Process runner guide](https://kestra.io/docs/task-runners/types/process-task-runner) and
[WorkingDirectory guide](https://kestra.io/docs/scripts/working-directory).

## Decision

AMESH creates one opaque local directory for every task attempt. The workspace service streams
declared internal-object URIs into bounded relative POSIX paths, verifies size and SHA-256 metadata,
runs the local process with that directory as `cwd`, and uploads declared paths, globs or a JSON path
manifest. A multi-file collection is published only after every upload succeeds; an incomplete batch
is deleted.

`core.workingDirectory` is a durable flowable whose children are always sequential and share one
execution-scoped local directory until the parent reaches a terminal state. Parent `inputFiles` are
materialized once, parent `outputFiles` are collected when the group completes, and the directory is
then removed. The local profile sets `WORKING_DIR` and `OUTPUT_DIR` to the assigned root.

Every collected file becomes an ordinary task artifact with its logical path, checksum and ordered
lineage from source object URI through execution, task attempt and workspace path. Migration 0040
adds those bounded fields to the existing transactional evidence projection. Authorized clients list
and stream files through `/api/v1/executions/{executionId}/files`.

## Security and failure rules

- absolute paths, drives, parent segments and backslash syntax are rejected;
- existing symlinks and symlink parents fail collection or materialization;
- workspace roots contain hashes of tenant/execution/task identities, never caller paths;
- streamed input and complete workspace bytes must remain within `workspaceQuotaBytes`;
- successful and ordinary failed attempts remove local data after upload;
- `retainDiagnosticsOnFailure` uploads a bounded diagnostic manifest before cleanup;
- retries receive a different attempt directory, while fencing still owns result commitment.

## Consequences

Local Process tasks and the control-plane API satisfy the EPIC-208 local profile without a new
dependency. Container and Kubernetes sidecar/volume transfer remain with EPIC-221/222; those runners
fail explicitly if this file-transfer surface is requested before their capability is installed.
