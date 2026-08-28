# ADR-017: UUIDv7 and canonical resource contracts

- **Status:** Accepted
- **Date:** 2026-08-21

## Context

EPIC-002 requires sortable runtime identities and one deterministic metadata/lifecycle contract across Python 3.12, PostgreSQL, REST, CLI and the future web client. Python 3.12 has no standard-library UUIDv7 generator.

## Decision

Use the MIT-licensed, pure-Python `uuid6` package for RFC 9562 UUIDv7 generation and pin it through `uv`. Keep natural-key validation, managed-resource metadata, lifecycle transitions and canonical hashing in AMESH's domain layer. Use compact sorted UTF-8 JSON for the current I-JSON-compatible value domain rather than adding an RFC 8785 package.

## Consequences

Runtime UUIDs sort by creation time without changing PostgreSQL's UUID columns. All interfaces share one validation and concurrency contract. Canonical serialization remains small and domain-controlled; adopting cross-language signing semantics beyond the present value domain requires a later ADR and RFC 8785 conformance suite.

## Revisit triggers

Move to the standard library when AMESH's minimum Python version provides UUIDv7, or adopt RFC 8785 when externally signed resource documents require its number and UTF-16 property-order semantics.

## Sources

- RFC 9562 and the `uuid6` package documentation.
- RFC 8785, JSON Canonicalization Scheme.
