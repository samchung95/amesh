# Flow DSL and validation

AMESH accepts YAML 1.2 and JSON flow documents and normalizes both into the versioned
`amesh.flow/v1` canonical intermediate representation. `apiVersion` may be written explicitly; when it
is absent, the v1 default is included in canonical output and its semantic hash.

The core flow shape contains:

- `id`, `namespace`, `description`, `revision`, `disabled`, labels and annotations;
- inputs, variables, tasks, triggers and outputs;
- error tasks, `finally` tasks and post-terminal `afterExecution` tasks;
- `x-` extension fields at flow and resource levels.

Unknown unprefixed flow fields fail validation. Task, trigger and input configuration is checked against
the descriptor for its registered type. An unregistered type also fails rather than bypassing schema
validation.

## Validation contract

`POST /api/v1/flows/validate` returns a `FlowValidationResult`. Valid documents include `irVersion`, a
canonical JSON-compatible object and a SHA-256 semantic hash. Invalid documents include issues with:

- a stable `code` and data `path`;
- a human-readable `message` and remediation `hint`;
- a one-based `sourceRange` with line, column and byte/character offset positions;
- `severity`, currently `error` for blocking issues.

Required fields, types, duplicate identifiers, missing task references, dependency cycles, duplicate
YAML keys and resource-specific properties all use this contract. The semantic hash sorts canonical
mapping keys and therefore ignores comments, key order and YAML layout while retaining semantic
extensions.

## Conditional flowables

`core.if` requires a boolean `condition` and non-empty `then` tasks. Ordered `elseIf` entries each
declare an `id`, boolean `condition` and tasks; `else` is optional. `core.switch` renders Kestra-shaped
`value`, normalizes null and boolean selectors, trims scalar strings and uses stable compact JSON for
structured selectors. It checks named `cases` for an exact normalized match, checks ordered
`predicateCases`, then uses the optional `default` case. No match without a default selects no branch.
Every branch task ID remains unique across the complete flow.

`conditionErrorPolicy` is `FAIL` by default. `FALSE` treats a failing boolean expression as false and
a failing switch selector as null, so an exact `null` case may match. `FALLBACK` immediately selects
the logical `else` or `default` branch. Runnable `runIf` and retry `condition` fields support `FAIL`
and `FALSE`. Static validation rejects repeated predicates and branches following a condition that is
literally unconditional.

See
[`conditional-flowables.yaml`](https://github.com/samchung95/amesh/blob/main/examples/conditional-flowables.yaml)
for the complete shape.

## Error and terminal hooks

A flowable may own a local `errors` task list, and the flow may own global `errors`, `finally` and
`afterExecution` lists. Each list is ordered. An error task may declare `errorSelector` with any
combination of `states` (`FAILED` or `CANCELLED`), normalized failure `categories`, `taskIds` in its
owner's scope and a safe boolean `condition`. The ordinary `runIf` condition may further restrict the
handler.

Lifecycle tasks use the same runnable task contract as primary tasks. They can therefore invoke
notification or compensation task types and return structured diagnostic outputs or artifact
references. Nested `errors` blocks inside any lifecycle block are rejected, and ordinary retry limits
remain bounded. A handler that does not match is committed as a zero-attempt skipped task.

`finally` runs after error handling on success, failure or cancellation. `afterExecution` starts only
after the primary terminal state is durable. See
[`lifecycle-hooks.yaml`](https://github.com/samchung95/amesh/blob/main/examples/lifecycle-hooks.yaml)
for the complete shape and
[execution semantics](execution-semantics.md#error-finally-and-after-execution-lifecycle) for ordering.

## Programmatic edits

`parse_editable_flow_document` returns an `EditableFlowDocument` backed by the YAML round-trip tree.
`set_value(("tasks", 0, "value"), replacement)` changes one value; `render()` retains surrounding
comments, mapping order, quotes and established indentation where practical. JSON input renders as
stable indented JSON.

Editable source is deliberately separate from canonical execution data. Comments and presentation
never affect execution identity.

## Resource schemas and editor metadata

`ResourceSchemaRegistry` registers task, trigger and input descriptors. Every descriptor includes:

- resource type and kind;
- a JSON Schema Draft 2020-12 configuration schema;
- title, description, category and property ordering for editors.

The default registry contains the currently executable core, agent, trigger and input types. Plugin
discovery can register descriptors through the same API. Duplicate types and invalid JSON Schemas are
rejected at registration.

Each built-in task kind has one frozen `TaskSpecification` bound to an independently checked runtime
configuration contract. Model-task schemas are generated from the Pydantic models used by their
handlers; non-model schemas are checked against handler-owned contract digests before registration.
The specification records whether the kind is owned by an ordinary handler, the executor or a
flowable controller, and the application refuses ambiguous ownership. The default registry and
generated catalog are derived from these specifications rather than a second schema list.

A parsed `TaskDefinition` exposes schema fields through an immutable, kind-bound `TaskConfiguration`
while retaining the raw handler values needed for exact runtime types. The DSL validator and trusted
and isolated plugin runtimes import the same structural-field set, so task metadata cannot leak into
handler configuration. A null property that is not declared by the resource schema is treated as
unset; declared nullable properties remain values. `contract_view()` normalizes YAML date and
datetime values to ISO strings for the schema boundary, while `handler_view()` preserves the raw
runtime values. Both document validation and execution fail with stable diagnostics when a task kind
is not registered. Plugin task descriptors continue to use
`ResourceSchemaRegistry.register` and therefore cross the same validation boundary before execution.

Public model-task configuration covers exact provider routing and revision, model parameters, bounded
or provider-bounded token controls, data handling, timeout controls and protected continuation
references. `maxCompletionTokens` applies only to completion-producing tasks and cannot conflict with
a declared budget; `agent.embedding` does not advertise it. `agent.llm` rejects tool and structured
output fields, which belong to `agent.toolCall` and `agent.structured`. Runtime-derived
`invocationKey` and `progressContext` values remain internal and are not authorable catalogue fields.

Run `uv run python scripts/generate_contracts.py` after a contract change. It deterministically writes:

- [`flow.schema.json`](https://github.com/samchung95/amesh/blob/main/schemas/flow.schema.json), the aggregate canonical flow schema;
- [`resource-catalog.json`](https://github.com/samchung95/amesh/blob/main/schemas/resource-catalog.json), core resource schemas and editor hints;
- the execution schemas and OpenAPI contract.

Generated-artifact tests fail when checked-in output drifts from implementation types. ADR-021 records
the parser and registry decision; the version-pinned Kestra import/conformance façade remains assigned
to EPIC-704.
