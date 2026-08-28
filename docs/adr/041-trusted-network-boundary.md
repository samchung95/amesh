# ADR-041: Trusted network boundary and explicit egress policy

- Status: Accepted
- Date: 2026-08-23
- Scope: EPIC-613

## Decision

AMESH owns the application network trust boundary even when a reverse proxy terminates TLS. The
server disables Uvicorn's implicit proxy-header rewriting, accepts forwarded origin data only from
configured IP or CIDR ranges, and rejects untrusted forwarding attempts before route handling.

Direct TLS uses Python's server TLS context with TLS 1.2 as the minimum, an operator-selected modern
cipher expression, and optional or required client-certificate authentication. Mounted certificate,
key and CA files are deployment inputs rather than image contents. Multi-replica rolling replacement
with `maxUnavailable: 0` is the reference certificate-rotation mechanism.

Outbound HTTP and download tasks share one policy: explicit HTTP/HTTPS proxies and no-proxy matches,
custom CA and client-certificate material, a host/CIDR egress allowlist, DNS resolution before the
request, private-address rejection, bounded redirects and revalidation after every redirect. Plugin
manifests retain their separately granted egress declarations and Kubernetes runners translate
approved CIDRs into NetworkPolicy rules.

The operations API exposes only redacted posture: whether proxies are configured, destination host
and scheme, certificate fingerprints and readability, DNS results, topology and policy. It never
returns proxy credentials, private-key content or secret-backed configuration values.

## Consequences

- Operators must configure the actual socket-peer proxy ranges, not client address ranges.
- Direct required mTLS applies to the complete listener; selected internal audiences should use a
  dedicated private listener or release boundary.
- Kubernetes NetworkPolicy accepts CIDRs, while hostname policy remains enforced by the application.
- Certificate rotation is outage-free only for a deployment with at least two ready server replicas.
