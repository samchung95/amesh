# Trusted in-process plugin runtime

The trusted runtime is the low-overhead execution tier for small Python plugins that have been
reviewed and explicitly approved by an AMESH administrator. Third-party plugins are not eligible by
default; use the isolated runtime for code that should not share the control-plane process.

## Approve an exact package

`TRUSTED_PLUGIN_APPROVALS` is a JSON array. Every approval includes the immutable package name,
semantic version and discovered SHA-256 content digest:

```json
[
  {
    "name": "acme.reviewed",
    "version": "1.2.0",
    "contentDigest": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
  }
]
```

All three values must match an `active` or `installed` catalog record. A name-only or version-only
approval is invalid. Changing package content changes its digest and therefore requires a new
approval. Duplicate exact approvals fail configuration loading.

The API and executor must see the same package files and approval configuration. Docker Compose
mounts the persistent `plugin-data` volume at `/var/lib/amesh/plugins` in both services.

## Python package contract

An in-process entry point uses this target convention:

```json
{
  "target": "python:plugin.py:execute",
  "transport": "stdio"
}
```

The target path is relative to the package content root, must end in `.py`, and cannot escape that
root. The named callback must be asynchronous and accept one `PluginRequest`; it returns a
`PluginResponse`.

A package may expose these optional hooks from one of its target modules:

```python
async def plugin_start(context): ...
async def plugin_stop(context): ...
def plugin_memory_bytes() -> int: ...
```

The lifecycle context contains the exact name, version, digest and private namespace. Start and stop
hooks are bounded by `TRUSTED_PLUGIN_LIFECYCLE_TIMEOUT_SECONDS`. Callback execution is bounded by
`TRUSTED_PLUGIN_CALLBACK_TIMEOUT_SECONDS`.

## Dispatch and failure containment

The API and executor dispatch task callbacks through the exact package pin stored on the flow
revision inherited by the execution. Installing or activating a newer package version cannot change
an existing execution's callback target.

Each package is imported under a digest-derived `_amesh_trusted_...` namespace. AMESH does not add
the package directory to `sys.path`, and it removes namespace modules when the runtime stops. The
runtime rejects a second package that attempts to own an already registered task identity.

Runtime failures increment a per-package circuit breaker. The relevant controls are:

- `TRUSTED_PLUGIN_FAILURE_THRESHOLD` — consecutive runtime failures before opening the circuit;
- `TRUSTED_PLUGIN_RESET_SECONDS` — delay before one half-open probe is allowed;
- `TRUSTED_PLUGIN_QUARANTINE_THRESHOLD` — repeated timeout, unhandled-exception or invocation-fence
  violations before the exact package version is quarantined.

Configuration, compatibility and capability errors are returned as structured errors but do not
trip the runtime circuit. A quarantine remains in effect for the lifetime of that service process;
an operator must correct or replace the package and restart with an exact approved digest.

## Observe the runtime

`GET /api/v1/plugins/trusted-runtime` requires plugin view permission and reports each approved
package's lifecycle state, circuit state, callback/error counts, invariant violations, mean latency,
last error code, plugin-reported memory and host-process resident memory.

Prometheus exports:

- `amesh_plugin_callbacks_total` and `amesh_plugin_callback_duration_seconds`;
- `amesh_plugin_callback_errors_total`;
- `amesh_plugin_memory_bytes` for `plugin-owned` and `host-process` measurements;
- `amesh_plugin_circuit_open` and `amesh_plugin_quarantines_total`.

## Security boundary

In-process namespace isolation is dependency and registration containment, not a security sandbox.
The plugin shares the host process, memory, interpreter, environment, filesystem permissions,
network access and credentials available to that service. A malicious or compromised in-process
plugin can bypass Python-level conventions, mutate global process state or terminate the service.

Only reviewed first-party or equivalently trusted code should be approved for this tier. Timeouts,
circuit breakers and quarantine limit availability failures; they do not create process, kernel or
credential isolation. Run untrusted or broadly distributed plugins through the isolated
language-neutral runtime instead.
