# Compatibility architecture

## Product promise

For every declared compatibility release, AMESH targets the pinned Kestra version across all selected public surfaces: YAML, Pebble expressions, REST API, CLI, execution semantics and documented import/export formats. Compatibility is proven by fixtures and differential evidence, not inferred from similar feature names.

## Source-preserving pipeline

```text
Kestra YAML / API payload / export bundle
        |
        v
Source-preserving compatibility parser
        |
        v
Versioned compatibility AST
        |
        +--> exact canonical mapping
        +--> compatibility adapter
        +--> explicit blocked gap
        |
        v
AMESH canonical flow and resource model
        |
        v
Validation + simulation + differential conformance report
```

The importer never silently drops fields. Every source range has a disposition. A required construct is either exact, implemented through a tested adapter, or recorded as a release-blocking gap.

## Compatibility surfaces

### YAML and flow resources

- Preserve comments, ordering and source locations where round-trip operations promise them.
- Match identifier, defaulting, validation and error-location behavior.
- Version task and trigger schemas against the pinned target.

### Pebble expressions

- Match parsing, escaping, null/error behavior, functions, filters and custom extension semantics.
- Maintain a differential fixture corpus for expressions and rendered values.
- Keep expression evaluation side-effect-free unless a public contract explicitly says otherwise.

### REST API

- Provide compatible paths, methods, request/response schemas, pagination, filtering, status codes and error classes for the declared surface.
- Preserve authentication/authorization semantics where documented while implementing all advanced controls in the open distribution.
- Version native AMESH APIs independently from compatibility APIs.

### CLI

- Match command structure, flags, exit codes, stdout/stderr conventions and machine-readable output for declared commands.
- Do not make shell text parsing the only compatibility evidence; use golden command fixtures.

### Execution semantics

Compare expanded task graphs, state sequences, retries, timeouts, pause/cancel/kill/restart, concurrency, trigger occurrence windows, outputs, labels, logs and artifacts. Timing comparisons use documented tolerances; state meaning may not be approximated silently.

### Import/export

Support documented flow, namespace, file, key-value, revision, dashboard and configuration bundles. The required depth of historical execution migration remains an open product decision.

## Differential conformance

Fixtures launch equivalent non-destructive flows against pinned Kestra and AMESH environments. The harness compares:

- validation acceptance, warning and error class;
- canonical and expanded task graph;
- state sequence and terminal state;
- inputs, outputs, labels, logs and artifacts;
- retry, timeout, concurrency and cancellation behavior;
- schedule and trigger occurrence windows;
- REST payloads and CLI golden outputs;
- import/export round trips;
- explicitly documented timing tolerances.

## Plugin migration

Native plugins use the AMESH manifest and isolated RPC contracts. Unchanged Kestra plugin JAR execution is not assumed. Configuration migration, generated SDK scaffolding and conformance tests minimise porting work. A transitional isolated JVM bridge is a fallback only if representative migration overhead exceeds the accepted guardrail.

## Compatibility release gate

A release cannot claim full compatibility with a target version while a Must surface contains an unknown, approximate or untested mapping. Known gaps remain visible in the machine-readable parity matrix.
