# Compatibility and parity charter

## Pinned target

The initial comparison target is Kestra **1.3.30**, tag `v1.3.30`, commit `db49f3b2c2af60d61df10adb6f9fc34e4776b65b`, released 2026-07-28.

Each requirement and differential fixture is evaluated against a known release. Rebasing requires a reviewed change to `project-baseline.json`, the parity matrix, public compatibility manifest and conformance environments.

## Accepted product promise

AMESH targets all three levels below for the declared Kestra 1.3.30 surface. A level may be claimed only after its complete mapped fixture set passes; unsupported or approximate behavior remains a blocking published gap.

### P0 — Capability parity

AMESH independently provides the same observable user outcome. Internals and native AMESH interfaces may differ.

### P1 — Configuration compatibility

Declared Kestra YAML resources and Pebble expressions load or migrate without silent semantic loss. Unsupported constructs produce precise, versioned diagnostics.

### P2 — Interface compatibility

Declared REST endpoints, CLI commands, execution behavior and import/export formats reproduce the pinned public contract closely enough for drop-in use under the published compatibility manifest.

Full P2 does **not** require unchanged loading of arbitrary Kestra plugin JARs. Native plugins use AMESH’s isolated protocol; configuration and common plugin behavior are migrated through explicit adapters and conformance tests. A transitional isolated JVM bridge remains a measured fallback.

## Required evidence

A parity or compatibility item is complete only when:

1. observable behavior is specified in original neutral language;
2. a requirement and epic own the behavior;
3. independent clean-room implementation exists;
4. positive, negative, failure and recovery fixtures pass;
5. differential results include state, output, error and timing tolerances where relevant;
6. API/CLI/YAML round-trip and golden records are reproducible where applicable;
7. differences and unsupported cases are published;
8. clean-room, licence, provenance and security gates pass.

## Scope labels

- `parity:core` — publicly observable OSS behavior.
- `parity:open-enterprise` — independently implemented equivalent of a publicly documented advanced capability, released in the same AGPL distribution.
- `parity:compatibility` — version-pinned configuration or interface compatibility.
- `difference:intentional` — deliberate AMESH capability or semantic difference.
- `parity:deferred` — known scope not scheduled for the current compatibility release.

## Claim discipline

Release notes and marketing must distinguish:

- equivalent capability;
- configuration compatibility;
- interface compatibility;
- full compatibility for a named target and manifest.

A capability test does not imply drop-in compatibility. A subset passing does not permit a full-version claim. AMESH is independent and does not imply endorsement or certification by Kestra.
