# Deterministic simulation API

Simulation compiles one stored flow revision without creating an execution or invoking a runner.
Open a flow in the web UI and choose **Preview plan**, or call:

```http
POST /api/v1/flows/team.data/forecast/revisions/4/simulate
Content-Type: application/json
X-Amesh-Tenant: default

{
  "inputs": {"customer": "acme"},
  "triggerContext": {"kind": "primary"},
  "fixtures": {
    "lookup": {
      "source": "RECORDED",
      "output": {"status": "approved"},
      "failuresBeforeSuccess": 1,
      "recordedAt": "2026-08-23T00:00:00Z"
    }
  },
  "estimateModels": {
    "vendor.lookup": {
      "durationSeconds": 0.5,
      "apiCalls": 1,
      "costUsd": 0.02
    }
  }
}
```

Fixture sources are `MOCK`, `RECORDED` and `SCHEMA_ONLY`. Schema-only fixtures declare
`outputSchema`; AMESH builds typed zero-value placeholders and labels them as schema-only rather
than observed output. Any reached external task without one of these substitutions becomes
`UNKNOWN`. Unknown expressions, concurrency keys, dynamic iteration counts and absent estimate
models are returned in `unknowns` with a stable code and path.

The plan includes the expanded task graph, condition/branch state, retry attempts, resolved
concurrency buckets, side-effect substitution, plugin-policy preview, runner demand and modeled
estimates. `sideEffectsSuppressed` is always true. The server signs canonical plans with
domain-separated HMAC-SHA256 evidence; `semanticHash`, `pluginSetHash`, `inputHash`, simulator,
reducer and expression versions make stale evidence detectable.

Compare two stored revisions and their frozen plugin sets with:

```http
POST /api/v1/flows/team.data/forecast/simulations/compare?from=3&to=4
```

The response includes both signed plans plus added, removed and changed tasks, estimate deltas and
new/resolved unknowns.

## CLI

```console
amesh flow simulate team.data forecast --revision 4 \
  --input customer=acme \
  --trigger kind=primary \
  --fixture 'lookup={source: MOCK, output: {status: approved}}' \
  --estimate-model 'vendor.lookup={durationSeconds: 0.5, apiCalls: 1}'

amesh flow simulation-diff team.data forecast \
  --from-revision 3 --to-revision 4 \
  --fixture 'lookup={source: MOCK, output: {status: approved}}'
```

JSON output is the stable automation format. `--unsigned` is available for local exploratory
previews, but unsigned evidence must not satisfy a promotion gate.
