# Expression and templating engine

AMESH evaluates dynamic flow values through the versioned `ExpressionEngine` adapter. The current
adapter declares `kestra-pebble/1.3.30-subset-1` and returns native scalar, list and object values. It
uses an immutable Jinja native sandbox internally; that implementation detail is not stored in flow
documents, so a future engine can replace it without a flow-storage migration.

## Documented context

| Name | Available values |
|---|---|
| `flow` | `id`, `namespace`, `revision` |
| `execution` | `id`, `state`, `startDate`, `tenantId` |
| `task` | The current canonical task definition |
| `taskrun` | `id`, `attempt`, `state` |
| `error` | Handler-scoped `state`, primary failed `taskId`, `category`, `message`, all matching `items` and `handlerOwnerId`; otherwise an empty mapping |
| `trigger` | Trigger metadata when an execution was triggered; otherwise an empty mapping |
| `inputs` | Execution inputs |
| `outputs` | Successful upstream task results keyed by task ID |
| `vars` | Flow variables |
| `labels` | Flow labels |
| `namespace` | `id` |
| `secret(name, default?)` | A value supplied by the capability-scoped secret context |
| `kv(name, default?)` | A value supplied by the capability-scoped key-value context |

The executor supplies runtime metadata and data contexts. Secret and key-value providers populate the
two service contexts explicitly; expressions never read process globals or arbitrary external state.
Missing values fail at render time.

## Selected Pebble subset

The checked-in compatibility corpus covers `{{ ... }}` output, `{% if %}` / `elseif` / `else`, bounded
`for` loops, dot and subscript access, native literals, comparisons, boolean and arithmetic operators,
`~` string concatenation and top-level `??` null coalescing.

Supported filters are `abbreviate`, `boolean`, `date`, `dateAdd`, `default`, `first`, `fromJson`,
`fromYaml`, `join`, `json`, `keys`, `last`, `length`, `lower`, `number`, `replace`, `reverse`, `sort`,
`split`, `toJson`, `toYaml`, `trim`, `upper`, `values` and `yaml`. Supported functions are `min`, `max`,
`render`, `secret` and `kv`. Supported tests are `boolean`, `defined`, `empty`, `iterable`, `mapping`,
`null`, `number` and `string`.

This is a version-pinned subset, not a claim of complete Pebble or Kestra function parity. HTTP,
storage, execution-query, subflow and asset functions are intentionally unavailable until their owning
capability supplies a scoped adapter and conformance evidence.

## Failure and resource contract

`compile()` translates the declared syntax and validates it without runtime values. Invalid syntax or
an oversized AST raises `ExpressionCompileError`. Missing values, invalid conversions and sandbox
denials raise `ExpressionRenderError`. Resource violations raise `ExpressionLimitError` with the stable
code `expression_limit_exceeded`.

Default per-render limits are:

| Limit | Default |
|---|---:|
| Template characters | 65,536 |
| AST nodes | 2,048 |
| Context bytes | 1 MiB |
| Items in one collection | 2,000 |
| Value nesting | 32 |
| Recursive `render()` depth | 5 |
| Output bytes | 1 MiB |
| Elapsed render time | 0.5 seconds |

The immutable sandbox blocks unsafe attribute access and mutation. Multiplication and exponentiation
are intercepted before they can exceed output bounds. Deployment CPU and memory controls remain an
additional process boundary.

`secret()` tracks derived string fragments. Tasks receive the runtime value, while previews,
expression errors, representations and `core.log` output replace tracked fragments with
`[REDACTED]`. Call `preview_value()` for any user-facing expression preview.

The selected examples live in
[`kestra-1.3.30-pebble-subset.json`](../../tests/expressions/fixtures/kestra-1.3.30-pebble-subset.json)
and are enforced by `tests/expressions/test_pebble_contract.py`. ADR-022 records the adapter decision.
