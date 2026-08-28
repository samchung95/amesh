# Tool provider operations

MCP servers and isolated plugins share the `amesh.tool-provider/v1` discovery,
policy, invocation and evidence contract. Bind every call through
`GovernedToolInvoker`; direct plugin callbacks and direct MCP transport calls
are not supported operational paths.

## Database migration

Apply migration `0062_tool_provider_invocations.sql` after the evidence
migration `0061_canonical_evidence_bundles.sql`. The migration creates the
tenant-RLS `tool_invocations` journal. It is additive and has no rollback that
preserves invocation evidence; use a forward migration for corrections. Verify
that the migration manifest contains 0062 in numeric order before restarting
workers.

## Recovery and duplicates

The journal uniqueness boundary is tenant, task run, attempt, provider kind,
provider key/revision and tool. Replaying an identical request returns the
existing evidence. A changed request hash is rejected. A record left `STARTED`
after a worker or provider restart is ambiguous and must be reviewed or
reconciled; it is never silently invoked again. Failed records remain evidence
and are not retried under the same invocation key.

## Certification

Validate a provider-neutral descriptor before installing or promoting a
provider:

```console
uv run amesh plugins certify-provider examples/plugin-sdk/neutral-tool-provider.json
```

The alias `certify-tool-provider` is also accepted. The command validates the
provider revision, canonical discovery digest and shared policy authorization;
it does not execute external tool code.

## Tenant and redaction checks

Provider revisions must match the agent tenant and namespace. Keep credentials
in secret references; invocation metadata stores request hashes and redacted
arguments, never plaintext secret values. Inspect journal rows through the
tenant-scoped repository and verify RLS when qualifying a deployment.
