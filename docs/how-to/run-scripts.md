# Run scripts through task runners

AMESH provides first-party `script.shell`, `script.python`, `script.node`, `script.java`,
`script.r` and `script.powershell` tasks. They use the same local, Docker and Kubernetes
runner contract as `core.shell`, including cancellation, resource limits, credentials,
working-directory files, logs, metrics and artifacts.

## Choose a source

Use an inline source when the code belongs in the flow:

```yaml
type: script.python
source:
  type: inline
  content: |
    import sys
    print(sys.argv[1])
args: [hello]
```

Namespace and repository sources are staged through `inputFiles`. Repository automation uploads
the revision-pinned file to object storage before applying the flow, so the execution receives an
immutable URI instead of reading a mutable checkout:

```yaml
type: script.python
source: {type: repository, path: src/job.py}
inputFiles:
  src/job.py: s3://amesh/default/repositories/example/7ac1d4/job.py
args: [hello]
```

For namespace files, use an `nsfile:///` reference. For packaged sources, set the source type to
`package` and point `path` at the entry point already staged or extracted in a
`core.workingDirectory` task.

## Read execution evidence

The runner captures stdout and stderr as ordered task logs and publishes duration, CPU time and
peak memory in `output.metrics`. The task also publishes `output.runtime` with the language,
interpreter command, immutable image, source origin and dependency name/version/digest records.

Scripts receive these helper environment variables:

- `AMESH_OUTPUTS_FILE=.amesh-outputs.json`
- `AMESH_METRICS_FILE=.amesh-metrics.json`
- `AMESH_FILES_MANIFEST=.amesh-files.json`
- `AMESH_LOG_FORMAT=jsonl`

Declare helper files in `outputFiles`, or set `outputManifest`, when they must be retained as
artifacts. Standard output and standard error need no manifest.

## Control images and dependencies

Default images are pinned by SHA-256 digest in `SCRIPT_TASK_POLICY`. A flow may set `image` only
when that exact digest appears under the language's operator-owned `approvedImages` list.

Runtime installation is denied by default. To permit it, operators set
`dependencyInstallationEnabled` and `dependencyAllowedEgress` in `SCRIPT_TASK_POLICY`. The task
must also declare immutable dependency name/version/digest records, a `dependencyCommand`, and a
`networkPolicy` with `access: restricted` whose egress entries are all organization-approved.

Script content is delivered by standard input or a staged file. `args` remain runner argv entries,
and `environment` remains a separate map; AMESH does not splice either into the script text.

See the six runnable examples in [`examples/scripts`](../../examples/scripts).
