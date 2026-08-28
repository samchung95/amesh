# ADR 040: Declarative upgrade compatibility gates

- Status: Accepted
- Date: 2026-08-23

## Context

AMESH already has ordered checksum-protected migrations, runtime service registration, graceful
drain, flow validation and plugin compatibility checks. Upgrade safety was nevertheless distributed
across those components: there was no supported-release authority, no combined pre/post report and
no distinction between rolling-compatible and unsafe service skew.

## Decision

A checked-in `amesh.upgrade-policy/v1` catalog is the release authority. It names every supported LTS
release, support window, schema boundary, minimum component contract and supported directed upgrade
path. Paths classify database/message overlap, rolling eligibility, rollback window and restoration
guidance.

The upgrade service composes existing checks instead of duplicating them:

- migration checksums and expand/exclusive classification come from the migration manifest;
- configuration comes from the typed runtime settings;
- plugin compatibility comes from the immutable plugin catalog snapshot;
- flow syntax comes from the canonical validator;
- storage and bounded capacity checks use the configured object store and authoritative database;
- service skew uses the same catalog before registration and in pre/post reports;
- graceful rollout uses the existing fenced service drain protocol.

Flow prechecks validate one canonical document per persisted semantic hash: revisions with the same
hash are definition-identical. Validation uses one immutable resource registry snapshot and runs off
the API event loop so a large retained revision history cannot stall health or unrelated requests.

Pre-upgrade reports fail closed on blocking findings. Post-upgrade reports retain warnings until old
rolling-compatible instances are drained. Historical execution events can be explicitly previewed
and upcast with an exact confirmation phrase. Flow and plugin documents are migrated offline into a
canonical target document so immutable stored revisions are never rewritten silently.

## Consequences

- A release cannot be supported until its catalog entry, migration boundary and upgrade fixture are
  checked in together.
- Rolling compatibility is an explicit directed path, not any arbitrary SemVer mismatch.
- Unsafe service versions fail registration with remediation instead of joining the topology.
- Reports are reproducible observations rather than a second orchestration state machine.
- Irreversible migrations require restoration guidance; rollback claims are limited to the catalog's
  declared window and verified backup procedure.
