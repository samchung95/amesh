# ToolProvider contract reference

The `amesh.tool-provider/v1` contract gives MCP servers and isolated plugins one
provider-neutral boundary for tool discovery and invocation. A provider is
identified by `(kind, key, revision)`; each discovered tool carries input and
optional output JSON Schema, impact, secret scopes, egress destinations and
filesystem roots. The callable schema digest is pinned as `schemaDigest`.

## Provider kinds

`mcp` adapts the existing governed MCP connection without changing its endpoint
or wire behavior. `plugin` refers to an isolated JSON-RPC plugin process. Plugin
code never runs in the AMESH control-plane process.

## Shared enforcement

Use `GovernedToolInvoker` for both kinds. It checks the exact provider identity,
tool allowlist, high-impact approval, delegated secrets/egress/filesystem roots,
input schema, timeout and output schema before recording a completed result.
Every result carries provider identity, tool name, schema digest, request hash,
policy digest and invocation state. A journal record left `STARTED` is treated as
an ambiguous external outcome and is not repeated after restart.

The neutral certification fixture is `example.echo`; it accepts `{ "value": ... }`
and returns the same value without side effects. See
`tests/domain/test_tool_provider.py` for the provider-neutral conformance cases.

## Compatibility migration

Existing MCP-only agent tool references remain valid through `connectionKey`,
`connectionRevision`, `toolName` and `schemaDigest`. New definitions may also
pin `providerKind`, `providerKey` and `providerRevision`; MCP references use
`providerKind: mcp` and retain their existing connection fields. A plugin pin is
resolved by the plugin provider registry and must not be silently substituted
for another provider revision.

Operational migration, journal recovery and certification instructions are in
the [tool provider operations runbook](../operations/tool-providers.md).
