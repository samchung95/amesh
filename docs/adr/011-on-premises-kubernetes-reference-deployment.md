# ADR-011: On-premises Kubernetes reference deployment

- **Status:** Accepted
- **Decision question:** Q-012
- **Date:** 2026-08-15

## Context

AMESH needs one concrete production environment for packaging, security, performance and recovery qualification. Supporting every deployment form equally from the first release would make evidence ambiguous.

## Decision

Use **on-premises Kubernetes deployed through Helm** as the first real production environment and reference qualification topology.

The reference topology uses external PostgreSQL and S3-compatible object storage and has no mandatory public-cloud control plane, hosted telemetry service, managed database, managed object store or licence server.

Docker Compose remains the development profile. A single-host deployment remains supported but is secondary.

## Consequences

- Helm, offline bundles, private registry support and distribution portability become release requirements.
- Performance and recovery evidence must name the Kubernetes distribution, topology, hardware and storage configuration.
- Kubernetes etcd remains non-authoritative for execution state.
- The project must test upstream Kubernetes and at least one common on-premises distribution.
- Cloud-specific integrations remain optional adapters rather than platform dependencies.

## Traceability

See `docs/architecture/on-premises-kubernetes.md`, `EPIC-606`, `EPIC-702`, `URS-F-0826`, `URS-F-0827` and `URS-F-0828`.
