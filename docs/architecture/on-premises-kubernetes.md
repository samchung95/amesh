# On-premises Kubernetes reference architecture

## Status and objective

On-premises Kubernetes is the first real production environment and the reference packaging target for AMESH. The deployment must not depend on a public-cloud control plane, managed database, managed object store, hosted telemetry platform or licence server.

Docker Compose remains the development profile. A single-host production profile remains supported for small installations, but release qualification is performed against this Kubernetes topology.

## Reference topology

```text
Users / CI / API clients
          |
On-prem load balancer or ingress controller
          |
+-----------------------------------------------------------+
| Kubernetes cluster                                        |
|                                                           |
|  Web/API pods       Executor pods       Scheduler pods     |
|  Trigger pods       Projector pods      Maintenance pods   |
|                                                           |
|  Worker gateway pods / isolated plugin hosts              |
|          |                                                |
|          +--> local-process runner nodes, where allowed    |
|          +--> Docker/OCI runner service                    |
|          +--> Kubernetes Jobs/Pods in execution namespaces|
|                                                           |
|  OpenTelemetry collectors / Prometheus exporters          |
+-----------------------------------------------------------+
          |                         |
          v                         v
External PostgreSQL HA       S3-compatible object storage
(authoritative state,        (artifacts, namespace files,
queues and projections)      large payloads and bundles)
```

## Kubernetes roles

The Helm chart supports a compact deployment and independently scalable roles:

- **web/API:** REST, WebSocket, authentication entry points and UI assets;
- **executor:** deterministic command/event reduction and runnable-work dispatch;
- **scheduler:** time ownership, due-occurrence creation and backfill coordination;
- **trigger:** polling, webhook and event-trigger runtime;
- **projector:** PostgreSQL search, dashboards and analytics projections;
- **maintenance:** retention, purge, reconciliation and repair jobs;
- **worker gateway:** worker registration, leases, heartbeats and task-result ingestion;
- **isolated plugin host:** language-neutral plugin processes with explicit capabilities;
- **Kubernetes runner:** creates and supervises user task Jobs or Pods in controlled namespaces.

Roles communicate through PostgreSQL queues, inbox/outbox records and leases. `LISTEN/NOTIFY` is only a wake-up hint. No pod-to-pod memory or notification is delivery truth.

## Stateful dependencies

### PostgreSQL

PostgreSQL is authoritative for:

- resource definitions and revisions;
- execution snapshots and immutable events;
- queue records, claims, attempts, leases and fencing tokens;
- trigger occurrences and scheduler ownership;
- transactional inbox and outbox records;
- worker identity and liveness;
- audit records;
- rebuildable search and analytics projections.

The reference topology uses an external highly available PostgreSQL service operated by the customer or deployed through a separately managed PostgreSQL operator. AMESH does not make a specific PostgreSQL operator mandatory.

### Object storage

Production requires an S3-compatible interface for artifacts, large logs or payloads, namespace files, migration bundles, backup exports and plugin packages. MinIO is the development and reference self-hosted implementation, but the contract remains provider-neutral.

PostgreSQL and object-storage recovery points must be coordinated. Object references are committed transactionally; object checksums and lifecycle state are recorded in PostgreSQL.

## Network zones

Recommended zones are:

1. **ingress zone:** user and CI access to web/API endpoints;
2. **control-plane zone:** AMESH stateless services and PostgreSQL/object-storage access;
3. **worker zone:** worker gateways and plugin hosts;
4. **execution zone:** untrusted Kubernetes task Jobs/Pods;
5. **management zone:** observability, backup, secret and certificate systems.

Default network policies should deny cross-zone traffic except for documented flows. Execution pods must not reach the Kubernetes API, control-plane database, object-storage administration endpoints or other tenants unless an explicit runner policy grants access.

## Identity and secrets

The chart supports external OIDC/SAML identity, LDAP/SCIM integrations, Kubernetes workload identity where available, and external secret providers. Production values must not contain universal default credentials.

Secrets are injected by reference and resolved only for an authorized task, trigger, runner or plugin. AMESH events, logs and migration bundles must never contain secret plaintext.

## Storage classes and persistent volumes

AMESH stateless pods do not rely on local persistent volumes. Temporary working directories use bounded ephemeral storage unless a task runner explicitly requests a controlled volume.

The chart must document:

- supported `ReadWriteOnce` and `ReadWriteMany` use cases;
- ephemeral-storage requests and limits;
- object-storage endpoint, TLS and credential configuration;
- PostgreSQL connection and TLS configuration;
- backup destinations and retention;
- behavior when a node-local workspace disappears.

## Availability

The accepted control-plane objective is 99.9% monthly availability, excluding declared maintenance.

Reference configuration includes:

- multiple replicas for stateless critical roles;
- PodDisruptionBudgets;
- topology spread or anti-affinity across failure domains;
- readiness separate from liveness;
- graceful shutdown and lease release;
- bounded termination periods for in-flight writes;
- retry and reconnection after PostgreSQL failover;
- leader ownership through fenced leases rather than Kubernetes leader state alone.

Kubernetes etcd is never authoritative for workflow execution state.

## Scale profile M

The v1 qualification topology must demonstrate:

- 100,000 executions over 24 hours;
- 1,000 active task runs;
- 50 sustained task starts per second;
- 10 million retained execution records;
- bounded queue lag and stable PostgreSQL resource consumption;
- rolling restart and selected failure scenarios during the workload.

The benchmark report records Kubernetes version and distribution, node types, CPU, memory, storage, PostgreSQL topology and configuration, object-store topology, AMESH values, dataset, plugin versions and all deviations.

## Minimal v1 disaster recovery

The first stable release gate is:

- **RPO:** no more than 48 hours;
- **RTO:** no more than 8 hours.

This is deliberately a minimal release gate, not a recommendation for every production deployment. A post-GA hardened reference target of RPO no more than 4 hours and RTO no more than 4 hours remains planned.

Backups include PostgreSQL recovery material, object-storage versions or snapshots, configuration, secret references, plugin bundles, release metadata, schema versions and compatibility manifests.

## Offline and air-gapped installation

Every stable release produces a signed offline bundle containing:

- multi-architecture container images or an OCI image layout;
- Helm charts and values schema;
- Kubernetes CRDs and operator artifacts where applicable;
- database migrations;
- plugin and integration bundles in the selected release set;
- SBOMs, signatures, checksums and provenance attestations;
- release notes, upgrade guidance, rollback guidance and runbooks;
- corresponding source and reproducible build instructions required by AGPL distribution policy.

The installation path supports a private registry mirror and performs no mandatory external update check, telemetry call or licence validation.

## Distribution qualification

Release qualification covers upstream Kubernetes and at least one common on-premises distribution. Distribution-specific behavior is isolated in documented values or adapters rather than leaking into workflow semantics.

Qualification covers:

- fresh installation;
- configuration validation;
- external PostgreSQL and S3-compatible storage;
- ingress and TLS;
- OIDC and secret-provider integration;
- upgrade and rollback rehearsal;
- node drain and pod disruption;
- PostgreSQL failover and reconnect;
- object-storage interruption;
- worker loss and lease expiry;
- backup and isolated restore;
- offline installation from the signed bundle.

## Explicit non-goals for v1

- AMESH does not ship its own mandatory Kubernetes distribution.
- AMESH does not require a specific PostgreSQL operator, ingress controller, service mesh or object store.
- Multi-region active-active PostgreSQL is not a v1 release gate.
- The v1 recovery objective does not promise zero data loss.
- Local-process tasks are not enabled on general control-plane nodes by default.
