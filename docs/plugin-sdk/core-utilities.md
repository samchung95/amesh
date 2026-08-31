# Core utility plugin pack

AMESH ships the EPIC-306 utilities as built-in, versioned resource-catalog entries. They use the
same task execution, retry, output, log, artifact and authorization paths as plugin tasks, while
remaining available without installing an external package.

## Tasks

| Area | Resource types | Contract |
| --- | --- | --- |
| HTTP | `core.http`, `core.download` | Bearer, basic and API-key auth; the shared task retry policy; bounded pagination, redirects and response bytes. Downloads write only to the assigned workspace. |
| Files | `core.files.compress`, `extract`, `checksum`, `copy`, `move`, `delete` | Relative POSIX paths inside the isolated task or shared working-directory scope. ZIP extraction rejects traversal, symlinks, excessive entries, excessive expansion and compression-ratio bombs. |
| Data | `core.data.json`, `yaml`, `csv`, `xml`, `text` | Deterministic parse/serialize or text transformations with bounded input and output. XML document type and entity declarations are rejected. |
| Control | `core.sleep`, `fail`, `log`, `return`, `debug`, `assert` | Bounded cancellation-aware sleep, intentional user-code failure, durable logging/native returns, redacted context inspection and boolean assertions. |
| Notifications | `core.notify.email`, `core.notify.webhook` | Bounded SMTP text delivery and the same protected HTTP contract used by `core.http`. |

The core distribution also declares `core.manual`, `core.webhook`, `core.cron`, `core.interval` and
`core.flow` triggers. Manual execution uses the authorized execution API and UI; the remaining
triggers use the durable occurrence runtime.

## HTTP security policy

HTTP and webhook tasks accept only `http` or `https` URLs without embedded credentials. Local,
loopback, link-local, private and otherwise non-global IP addresses are denied after hostname
resolution and each redirect is revalidated. Operators can explicitly allow named private hosts for
known internal services with `CORE_HTTP_ALLOWED_PRIVATE_HOSTS`; workflow authors cannot expand that
allowlist. `CORE_HTTP_MAX_RESPONSE_BYTES`, `CORE_HTTP_MAX_PAGES` and
`CORE_HTTP_MAX_REDIRECTS` are deployment ceilings. A task may choose a lower response or page limit.

HTTP authentication material is request-only and is not copied into task output. Use rendered
secrets for token, password and API-key values.

## Workspace and payload boundaries

File tasks prepare inputs through the existing object-store-backed working-directory manager. A
standalone task uploads only its declared `outputFiles`; tasks nested under `core.workingDirectory`
share the parent scope. Absolute paths, Windows paths, parent traversal and symlinks are rejected.

The shipped ceiling is 10 MiB for data transformations, 10 MiB for HTTP responses by default and
100 MiB or 10,000 entries for archive expansion. Deployment HTTP ceilings can be lowered through
configuration. The task contract's output and workspace quotas still apply after these utility-level
checks.

## Example

```yaml
id: core_utilities
namespace: examples.plugins
labels:
  team: platform
tasks:
  - id: parse
    type: core.data.json
    operation: parse
    input: '{"ready":true,"name":"amesh"}'
  - id: normalize
    type: core.data.text
    dependsOn: [parse]
    operation: upper
    input: "{{ outputs.parse.value.name }}"
  - id: assert_ready
    type: core.assert
    dependsOn: [parse]
    value: "{{ outputs.parse.value.ready }}"
  - id: done
    type: core.return
    dependsOn: [normalize, assert_ready]
    value: "{{ outputs.normalize.value }}"
```

The checked-in
[`core-utilities.yaml`](https://github.com/samchung95/amesh/blob/main/examples/core-utilities.yaml)
example can be applied and
run through the same flow and execution APIs as other workflows.

`tests/tasks/test_core_utilities.py` provides deterministic HTTP, download, archive, format,
control, notification and rejection fixtures. The PostgreSQL executor fixture additionally proves
that rendered results remain observable in durable task-run output.
