# ADR-022: Versioned Pebble compatibility adapter

- Status: Accepted
- Date: 2026-08-22
- Scope: EPIC-005

## Context

AMESH already uses Jinja2's sandboxed native environment for scalar, collection and object rendering.
Kestra 1.3.30 documents Pebble delimiters, attribute/subscript access, control flow, null coalescing,
filters, functions and execution contexts. Pebble itself is a Java engine; no maintained Python Pebble
implementation with a compatible sandbox and native-value contract was identified.

Running a JVM sidecar for every expression would add a second runtime, serialization boundary and
failure mode to the core. Silently treating similar Jinja syntax as complete Pebble parity would be
incorrect.

## Decision

1. Define an `ExpressionEngine` protocol independent of flow persistence. The native implementation is
   versioned `amesh.expression/v1`; its compatibility facade declares
   `kestra-pebble/1.3.30-subset-1`.
2. Use Jinja2's immutable sandboxed native environment as the evaluator. Translate only declared,
   fixture-proven syntax differences: Pebble `elseif` and the selected null-coalescing `??` form.
3. The selected subset covers scalar/list/object rendering; dot and subscript access; arithmetic,
   comparisons, logic and `~` concatenation; `if`/`elseif`/`else` and bounded `for`; documented string,
   collection, JSON, YAML and date filters; and `min`, `max`, `render`, `secret` and `kv` functions.
4. Expose flow, execution, task, task-run, trigger, inputs, outputs, variables, labels and namespace
   mappings through `ExpressionContext`. Secret and key-value lookup use explicit context-backed
   functions rather than global process access.
5. Separate `ExpressionCompileError` from `ExpressionRenderError`. Compilation validates translated
   syntax and AST size before runtime values are available.
6. Apply configurable limits to template length, AST nodes, context bytes, collection cardinality,
   nesting, recursive rendering, rendered bytes and elapsed render time. Intercept potentially
   amplifying arithmetic in addition to using the immutable sandbox.
7. Track secret-derived values during a render. Runtime rendering may return the value to the selected
   task, while previews and error messages replace every tracked value with `[REDACTED]`.
8. Functions requiring external effects or unfinished platform owners—HTTP, storage reads, subflows,
   execution queries and assets—remain unsupported and fail explicitly until their owning epics add
   capability-scoped adapters and conformance evidence.

## Consequences

- No new runtime dependency is required; Jinja2 remains the internal implementation detail.
- Compatibility claims are limited to the checked-in versioned fixture corpus, not all Pebble or all
  Kestra functions.
- Expression limits are deterministic application guards. Deployment CPU/memory limits remain an
  additional boundary, as recommended by the Jinja sandbox documentation.
- Secret and key-value persistence remains owned by EPIC-207/506; this epic defines and verifies the
  expression-facing adapter contract.

## Sources

- [Kestra expression context and Pebble syntax](https://kestra.io/docs/expressions)
- [Pebble template syntax](https://pebbletemplates.io/wiki/guide/basic-usage/)
- [Jinja sandbox guidance](https://jinja.palletsprojects.com/en/stable/sandbox/)
- [Jinja native values](https://jinja.palletsprojects.com/en/stable/nativetypes/)
