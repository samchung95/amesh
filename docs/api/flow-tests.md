# Flow tests and promotion gates

Flow tests simulate one immutable flow revision without creating an execution, reading a secret or
writing an artifact. Results are pinned to the flow semantic hash, resolved plugin-set hash and
`amesh.flow-test/v1` simulator version. The simulator models expressions, conditions, branches,
retries, error/finally/after-execution handlers and generated loop tasks. Coverage is observed path
coverage for tasks, branches, handlers and conditions; it is not proof of full workflow semantics.

## Define and run tests

Save a test with `PUT /api/v1/flows/{namespace}/{flow_id}/tests`. `expectedVersion` is required when
updating an existing `testId`; stale updates return `412`. Inputs, variables, expected outputs and
task states are JSON objects. Every external or plugin task reached by a test needs a fixture:

```json
{
  "testId": "recorded-success",
  "name": "Recorded provider response",
  "revision": 4,
  "inputs": {"route": "primary"},
  "variables": {},
  "fixtures": {
    "lookup": {
      "source": "RECORDED",
      "output": {"status": "approved"},
      "failuresBeforeSuccess": 1,
      "recordedAt": "2026-08-23T00:00:00Z"
    }
  },
  "expected": {
    "state": "SUCCESS",
    "outputs": {"status": "approved"},
    "taskStates": {"lookup": "SUCCESS"}
  },
  "tags": ["ci"]
}
```

`INLINE`, `PLUGIN` and `RECORDED` fixture sources share the same deterministic replay boundary.
Plugin fixtures require `pluginId`; recorded fixtures require a timezone-aware `recordedAt`.
`failuresBeforeSuccess` exercises the task's configured retry limit. Loop fixtures can provide an
`iterations` array when the flow does not contain an inline iterable. Secret-like keys such as
`password`, `apiToken` or `credential` are rejected before persistence.

The simulator reads the same raw handler values as execution, including explicit nulls and parsed
YAML timestamp values. Switch cases use the executor's null, boolean, trimmed-string and stable-JSON
normalization. A selector error follows `conditionErrorPolicy`: `FALSE` continues as a null selector,
`FALLBACK` selects the logical default and `FAIL` reports the error. A normal unmatched switch without
a default selects no branch.

Inline `core.foreach` tests share the executor's source expansion: arrays retain order, maps sort by
key, integer ranges keep range order and `batchSize` produces the same batches. Generated children see
the same `iteration.index`, `iteration.key`, `iteration.value` and `iteration.parent` shape; the
simulator uses a deterministic synthetic UUID for the parent task-run identity. A `manifestUri` loop
still requires an explicit `iterations` fixture because a flow test does not read object storage.

Run all tests for a revision with:

```http
POST /api/v1/flows/team.data/daily/tests/runs?revision=4
Content-Type: application/json

{"testIds": [], "failFast": false}
```

Supply `testIds` to select cases. The result schema is `amesh.flow-test-result/v1`; `PASSED`,
`FAILED` and `ERROR` are stable machine outcomes. `productionExecutionsCreated`, `artifactsCreated`
and `secretLookups` remain zero. List definitions and prior results through the adjacent `GET
.../tests` and `GET .../tests/runs` endpoints. The flow detail page exposes the same operations under
**Unit tests**.

## CI

The CLI emits JSON by default and exits `0` only for `PASSED`; valid failed/error results exit `1`:

```console
amesh --output json flow test team.data daily --revision 4 --test-id recorded-success
```

Use a service-account token through `AMESH_SERVICE_ACCOUNT_TOKEN` for non-interactive CI.

## Namespace promotion gate

`PUT /api/v1/namespaces/{namespace}/flow-test-gate` configures an optional minimum observed
coverage and required test IDs. When enabled, promoting a revision to `ACTIVE` returns `409` until a
passing result matches that exact semantic hash, plugin-set hash and simulator version. Results from
another revision or a stale plugin resolution never satisfy the gate. Disabling the gate restores
normal lifecycle promotion.

Definitions, results, gates and their audit records are durable and tenant-scoped. Migration
`0051_flow_tests_quality_gates.sql` adds only expandable tables and role permissions; disable gates
before forward-fixing the migration if promotion must continue during recovery.
