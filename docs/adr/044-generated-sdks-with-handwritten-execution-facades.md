# ADR-044: Generated SDKs with handwritten execution facades

- Status: Accepted
- Date: 2026-08-23
- Scope: EPIC-703

## Decision

AMESH publishes Python, TypeScript, Java and Go client archives from the checked-in OpenAPI contract.
The pinned OpenAPI generator owns wire models and endpoint clients. Small, language-native execution
facades own the operations that require coordinated behavior: authenticated launch with a stable
idempotency key, bounded safe retries, terminal waiting, version-bound cancellation, log streaming,
artifact access, normalized errors and webhook verification.

The facades use immutable configuration and accept a caller-provided transport. Python provides sync
and async entry points; TypeScript is async; Java and Go use their standard concurrency models. The
generator copies facade sources from `scripts/sdk_templates`, so regenerating a client cannot silently
discard ergonomic behavior. Release conformance launches the same installed flow through every
language against one live AMESH environment.

SDK major/minor compatibility follows the public API major/minor line. A breaking public API change
requires a new SDK major version. Additive API changes increment the SDK minor version, and fixes that
do not change the public SDK contract increment the patch version.

## Consequences

- Generated models remain reproducible while application code gets a compact stable entry point.
- Retries are limited to reads and launches carrying one stable idempotency key.
- Callers can substitute transports for proxies, tracing, tests or platform-specific networking.
- Registry publication remains a release operation; release archives and checksums are the canonical
  local and GitHub Release artifacts.
