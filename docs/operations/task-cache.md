# Task cache operations

AMESH reuses a runnable task result only when its flow opts in and the tenant, security context,
revision, code version, task configuration and selected contextual values produce the same key.
Every execution still records a normal task attempt and durable cache decision.

## Configure a task

```yaml
tasks:
  - id: calculate
    type: core.return
    value: "{{ inputs.value }}"
    taskCache:
      enabled: true
      ttl: PT1H
      namespace: calculations
      scope: TASK
      invalidationPolicy: TTL_AND_REVISION
      keyContext: [inputs, variables, labels, trigger, iteration]
      codeVersion: calculation-v1
```

`enabled` and `ttl` match the pinned Kestra task-cache spelling. `ttl` must be a positive ISO-8601
duration. `namespace` defaults to `default`; `scope` controls the administrative prefix (`TASK`,
`FLOW` or `NAMESPACE`). `codeVersion` defaults to the running AMESH version and task type. Set it for
independently versioned plugin or user code.

## Run, bypass or refresh

`POST /api/v1/executions` accepts `cacheMode`:

- `USE` is the default and reuses an eligible entry.
- `BYPASS` runs the handler and leaves the reusable entry unchanged.
- `REFRESH` runs the handler and replaces the matching entry.

The execution detail page shows `HIT`, `MISS`, `MISS_EXPIRED`, `MISS_INVALIDATED`,
`MISS_CONCURRENT`, `BYPASS` or `REFRESH`, its human-readable reason and source execution on a hit.
The same decision is stored under each task run's `evidence.cache` field and as a system log event.

## Inspect and purge

List entries with optional `keyPrefix`, `namespace`, `flowId` and `taskId` filters:

```text
GET /api/v1/task-cache?namespace=demo.cache
```

Purge by at least one prefix or resource scope:

```http
POST /api/v1/task-cache/purge
Content-Type: application/json

{
  "namespace": "demo.cache",
  "flowId": "cached-result",
  "reason": "input contract changed"
}
```

Purge requires `manage` authorization on `task_cache`. It marks matching entries `INVALIDATED`,
writes a cache event for every entry and writes a tenant audit event. The next matching execution
reports `MISS_INVALIDATED` with the supplied reason and repopulates the entry.

## Failure and recovery behavior

- A cache lookup and ownership decision is one PostgreSQL transaction guarded by a per-key advisory
  lock.
- A concurrent non-owner computes normally but cannot replace the owner's entry.
- A failed or deferred owner abandons population. An interrupted owner can be replaced after its
  lease expires.
- Cache publication happens after the task result commits. Publication failure does not reverse the
  successful task; the incomplete population is abandoned for a later retry.
- Cache tables are covered by the same PostgreSQL backup and tenant-RLS controls as execution state.
