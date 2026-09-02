# ADR-021: Round-trip YAML and resource schema registry

- Status: Accepted
- Date: 2026-08-21
- Scope: EPIC-004

## Context

AMESH currently parses YAML through PyYAML and validates the common flow shape with Pydantic. That is
enough for execution, but it discards comments, cannot support stable programmatic edits and has no
installed-resource registry for task-, trigger- or input-specific JSON Schemas and editor hints.

Building a YAML concrete-syntax tree or a JSON Schema evaluator in AMESH would duplicate mature,
security-sensitive parser work. PyYAML exposes source marks but does not provide the required comment
round trip. `ruamel.yaml` provides a safe-derived round-trip loader, YAML 1.2 behavior and preserved
comments. Python `jsonschema` provides a version-pinned Draft 2020-12 validator.

## Decision

1. Parse editable YAML with `ruamel.yaml` in round-trip mode, disallow duplicate mapping keys and retain
   the source tree only for rendering and location lookup. JSON remains a first-class accepted syntax.
2. Keep `FlowDefinition` as the typed canonical intermediate representation. Validation results expose
   the explicit IR identifier `amesh.flow/v1`; semantic hashes cover only the canonical data, not source
   formatting or comments.
3. Map parser, Pydantic, reference, cycle and resource-schema failures to one validation issue contract
   containing a stable code, data path, source range and remediation hint.
4. Allow forward-compatible fields only when their names start with `x-`. Unknown unprefixed core fields
   remain errors.
5. Validate installed task, trigger and input configurations through an AMESH-owned resource registry.
   Each descriptor contains a Draft 2020-12 JSON Schema plus editor metadata. Core descriptors ship in
   the default registry; plugin descriptors use the same registration API.
6. Generate the aggregate flow schema and resource catalog deterministically for API/UI consumers.
   Plugin runtime discovery may populate the registry later without changing the DSL contract.
7. Define each built-in task schema and editor contract once as a frozen, feature-adjacent task
   specification. Derive the default registry from those specifications and expose parsed task
   configuration through an immutable, kind-bound view shared by validation and execution.

## Consequences

- `ruamel.yaml` and `jsonschema` become runtime dependencies and are managed through `uv`.
- Editable source and canonical execution data stay separate, so comment preservation cannot affect
  execution identity or replay determinism.
- A flow referencing an unregistered resource type fails validation with an installation/remediation
  hint instead of silently accepting unvalidated configuration; direct execution fails closed at the
  same registry boundary.
- JSON Schema Draft 2020-12 is the versioned plugin configuration contract for this IR generation.

## Sources

- [`ruamel.yaml` round-trip API](https://yaml.dev/doc/ruamel.yaml/api/)
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [Python `jsonschema` versioned validators](https://github.com/python-jsonschema/jsonschema/blob/main/docs/validate.rst)
