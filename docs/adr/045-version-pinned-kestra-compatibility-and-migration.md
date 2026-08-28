# ADR-045: Version-pinned Kestra compatibility and side-by-side migration

- Status: Accepted
- Date: 2026-08-23
- Scope: EPIC-704

## Decision

AMESH exposes a bounded clean-room compatibility surface pinned to Kestra 1.3.30. Flow imports retain
the editable source document and classify every encountered source path as exact,
compatibility-adapted or blocked. Adaptations produce source-located patches; blocked or unknown
constructs remain in the candidate document and prevent that document from being accepted.

The public manifest is the authority for declared REST paths, CLI commands, evidence and unresolved
gaps. A passing flow or differential fixture does not permit a full-version claim while the manifest
contains a blocking gap. Execution comparisons use non-destructive suppress, mock or idempotent
side-effect modes and explicit timing tolerances.

Full migration uses checksum-protected, versioned bundles. Stable source-to-target identifiers,
tenant and reference validation, chronology checks, external secret references, resumable
checkpoints, idempotent staging and reconciliation precede an explicit cutover. Migration never
exports secret plaintext, silently enables triggers or mutates the source system in place.

## Consequences

- Core documented types can be migrated to native AMESH definitions without losing the original
  editable YAML.
- Unsupported plugins or fields produce evidence instead of guessed defaults.
- Resource, governance and historical bundle payloads remain exact and source-provenanced.
- The initial REST, CLI and Pebble surfaces are intentionally bounded, so the manifest blocks a full
  Kestra 1.3.30 compatibility claim until their published gaps are closed.
