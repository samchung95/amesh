# Plugin architecture

## Goals

- Keep third-party code outside trusted control-plane processes by default.
- Support Java, Python and TypeScript SDKs without changing execution truth.
- Preserve exact task/trigger configuration compatibility where declared.
- Make credentials, networking, files, CPU, memory and time explicit capabilities.
- Permit deterministic certification and migration evidence.

## Plugin package

A plugin package contains:

- manifest: identity, semantic version, protocol range and publisher;
- task, trigger, condition, notification and function descriptors;
- JSON Schemas and UI hints;
- required capabilities, runner needs and egress declarations;
- container or executable entry point;
- checksums, signature, SBOM and provenance;
- compatibility mappings and migration transforms;
- conformance fixtures, examples and documentation.

A flow revision pins the resolved package versions and compatibility adapter versions. Resolution never changes silently for an already-created execution.

## Runtime tiers

### First-party trusted modules

Small, reviewed modules may execute in the main runtime only when they require no untrusted dependency graph and pass stricter architecture, licence and security gates. In-process execution is an optimisation, not the general plugin model.

### Isolated native plugins

The default model uses versioned gRPC/Protobuf or equivalent framed RPC over a supervised process or OCI container. The platform grants short-lived capability tokens for specific files, secrets, destinations and result publication.

The plugin cannot write execution state directly. It returns typed results, logs, metrics, artifact references and side-effect evidence to the worker, which commits through fenced platform commands.

### Transitional JVM compatibility bridge

An optional isolated JVM bridge may host supported migrated Java plugins when direct source migration is too costly. It is not loaded into the control plane, must expose the same capability protocol and cannot bypass AMESH authorization or state transitions.

## Initial SDKs

- **Java:** preferred for compatibility-heavy and high-throughput plugins.
- **Python:** preferred for AI/ML, data science and scripting integrations.
- **TypeScript:** preferred for SaaS APIs, web tooling and broad contributor access.

All SDKs generate or consume the same manifest, schemas and conformance contract. SDK convenience must not create different semantics between languages.

The implemented `amesh.plugin/v1` manifest, `amesh.plugin.rpc/v1` request/response envelopes, Python
protocol bindings and local conformance harness are documented in the
[plugin manifest contract](../plugin-sdk/manifest.md), [testing guide](../plugin-sdk/testing.md) and
[compatibility policy](../plugin-sdk/compatibility.md). Deterministic discovery, verified offline
installation, dependency resolution, revision pins and content-root isolation are described in the
[discovery and resolution guide](../plugin-sdk/discovery-and-resolution.md). Trusted/isolated process
supervision and signing remain separate lifecycle layers and do not alter these public documents.

Polling trigger adapters return normalized occurrences plus their next checkpoint. The runtime
persists both before calling the adapter's acknowledgement hook. Realtime trigger adapters expose an
async occurrence stream and are acknowledged only after durable acceptance. Both contracts carry a
source occurrence key and observed timestamp; pause, backpressure, retry, claims and replay remain
platform responsibilities rather than connector-specific behavior.

## Kestra migration path

1. Parse the existing task/trigger configuration through the versioned compatibility model.
2. Produce an exact field mapping, adapter mapping or blocked-gap report.
3. Generate a native SDK project with schemas, examples and fixture tests.
4. Port only the external interaction logic; platform state, retry and logging behavior remains in the AMESH SDK/runtime.
5. Run configuration, behavior, failure and performance conformance.
6. Publish a signed package and migration report.

Migration tooling should make common stateless plugins mechanical. It must never hide unsupported APIs or copy upstream implementation code.

## Capability handshake

1. Supervisor starts a pinned plugin package in a constrained environment.
2. Plugin returns identity, protocol range and descriptor checksum.
3. Supervisor verifies the package, policy and requested capabilities.
4. Worker opens a per-attempt session with short-lived tokens.
5. Plugin streams logs/heartbeats and returns a typed result.
6. Supervisor terminates or reuses the process according to isolation policy.

## Security controls

- non-root execution and read-only root filesystem;
- CPU, memory, process, file and duration limits;
- default-deny network policy and destination allowlists;
- scoped secret resolution without plaintext persistence;
- signed package and provenance verification;
- dependency and vulnerability policy;
- redaction at SDK and platform boundaries;
- deterministic denial when capabilities exceed policy.

## Lifecycle

Plugins may be installed, enabled, restricted, deprecated, quarantined and removed. A version remains resolvable for historical evidence but cannot be selected for new revisions after policy blocks it unless an emergency override is explicitly audited.
