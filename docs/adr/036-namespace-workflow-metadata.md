# ADR-036 — Namespace workflow metadata and resolved defaults

- **Status:** Accepted
- **Date:** 2026-08-22
- **Epic:** EPIC-206

## Context

Workflow labels must be searchable across runtime resources, while plugin defaults must inherit
through namespace ancestry without hiding the value that an execution actually used. Flow revisions
also need to remain reproducible after namespace policy changes.

## Decision

AMESH stores tenant-scoped namespace workflow metadata in PostgreSQL. Each namespace may define
exact plugin-type defaults and a label/default policy. Flow application walks the namespace lineage
from parent to child, validates user labels, applies policy normalization and resolves defaults into
the immutable flow revision. Non-forced values use broad-to-specific precedence: parent namespace,
child namespace, flow and task. Forced values reverse that privilege so the broadest forced
namespace value wins. Nested mappings merge recursively; arrays and scalar values replace.

The revision's `pluginResolution.defaults` projection records every task's effective values and the
source, namespace and forced state for each inherited property. Executions remain pinned to that
revision. User labels reject the protected `amesh.` and `system.` prefixes; AMESH adds protected flow,
execution, task-run, asset and backfill labels at their persistence boundary. PostgreSQL JSONB GIN
indexes support dotted collection filters such as `metadata.labels.team=platform`.

The precedence behavior follows the public Kestra v1.3.30 plugin-default and label contracts, while
the storage model remains AMESH-native.

## Alternatives considered

### Resolve namespace defaults at task dispatch

This would see the newest policy but make retries and historical revisions non-reproducible.

### Flatten all defaults into flow YAML

This is explicit but loses centralized policy and forces authors to copy operator-owned settings.

### Give task values priority over every forced value

That would make an operator's forced namespace policy advisory rather than enforceable.

## Consequences

- Migration 0038 adds namespace metadata, task-run and asset labels, and label indexes.
- Namespace metadata changes use optimistic resource versions and namespace authorization.
- Flow detail exposes labels, effective defaults and provenance from the pinned revision.
- Updating namespace metadata affects newly applied revisions, not already-pinned executions.
