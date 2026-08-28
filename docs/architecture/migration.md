# Full side-by-side migration architecture

## Accepted scope

Q-017 selected migration option C. AMESH migration therefore covers more than flow YAML.

The supported migration set includes:

- flows, revisions, namespace files, key-values, labels, dashboards, apps, tests and policies;
- users, groups, roles, bindings, service accounts, tenants and namespace configuration;
- plugin inventory, plugin configuration and compatibility diagnostics;
- historical executions, task runs, state events, logs, metrics and outputs;
- artifacts and their metadata;
- audit events and evidence packages;
- secret references and provider metadata, never secret plaintext.

## Reference strategy

Migration is an export/import and side-by-side verification process. Direct in-place mutation of a Kestra database is not the reference method.

```text
Source system
    |
Read-only public APIs / documented exports / approved black-box extraction
    |
Versioned source bundle + manifest + checksums
    |
AMESH migration planner
- parse
- inventory
- classify
- map IDs
- report unsupported items
- calculate storage and duration estimates
    |
Dry run / transformed staging bundle
    |
Resumable AMESH importer
    |
Target AMESH instance with triggers and side effects disabled
    |
Reconciliation and differential verification
    |
Explicit cutover decision or rollback
```

## Migration phases

### 1. Discovery

The discovery phase inventories source versions, namespaces, resources, users, permissions, plugins, history volume, artifact size, retention, external secret references and unsupported features.

It produces:

- source-system fingerprint;
- compatibility target and importer version;
- item counts and size estimates;
- exact, adapted, blocked and unknown classifications;
- permissions required for extraction;
- required target plugins and secret providers;
- cutover risks and expected downtime.

### 2. Export

Exports are versioned, chunked and checksummed. Every record includes source identity, tenant or namespace, revision, source timestamp, extraction timestamp and provenance.

Sensitive fields are redacted according to schema. Secret values are never exported. The bundle contains only secret references, provider identifiers and unresolved-binding diagnostics.

### 3. Plan and transform

The planner validates schemas, computes source-to-target identifiers, resolves configuration mappings and creates source-located patches where user input is required.

Mappings are classified as:

- **exact:** no semantic change;
- **compatibility-adapted:** AMESH stores a native representation but reproduces declared behavior through its compatibility façade;
- **blocked:** no safe mapping exists;
- **unknown:** insufficient evidence exists and cutover is blocked for Must scope.

Approximate or silently defaulted mappings cannot satisfy a full migration claim.

### 4. Dry run

A dry run validates the complete bundle without committing durable target resources. It checks:

- schema and referential integrity;
- identifier collisions;
- plugin and runner availability;
- secret-reference resolution;
- storage capacity;
- permission and tenancy mapping;
- history chronology;
- artifact checksums;
- expected target counts;
- cutover and rollback preconditions.

### 5. Staged import

Import is resumable and idempotent. Each chunk has a stable identity, checksum, checkpoint and result. Retrying an acknowledged chunk cannot create duplicate logical records.

Triggers, schedulers, webhooks and external side effects remain disabled during historical import unless a specific replay mode is explicitly selected.

### 6. Reconciliation

Reconciliation compares source and target by resource counts, semantic hashes, identifier maps, revision history, execution state, log and artifact counts, timestamps, checksums, permissions and audit continuity.

Differences are machine-readable and classified as accepted, blocked or unresolved. A Must mismatch blocks cutover.

### 7. Shadow validation

Where safe, AMESH can run selected workflows in shadow mode with external effects mocked, suppressed or made idempotent. Results compare validation, graph expansion, state transitions, outputs, error classes and timing windows against the pinned source behavior.

### 8. Cutover

Cutover is an explicit operation with a named authority. A typical sequence is:

1. freeze source mutations or record a final delta boundary;
2. export and import the final delta;
3. rerun reconciliation;
4. verify secret references and external endpoints;
5. enable AMESH workers;
6. enable schedulers and triggers in controlled order;
7. monitor duplicate or missed occurrence guards;
8. preserve the source system read-only for the agreed rollback window.

### 9. Rollback

Rollback guidance states which target-side effects may already have occurred. AMESH cannot promise generic exactly-once behavior across arbitrary external systems.

A rollback report includes imported items, enabled triggers, launched executions, external actions, unresolved ambiguity and the source checkpoint needed to resume or revert.

## Identifier policy

AMESH maintains a source-to-target identifier map for every migrated object. The map records source system, source type, source identifier, target type, target identifier, collision strategy and mapping version.

Referential-integrity checks cover resources, revisions, parent/subflow relationships, executions, task runs, logs, artifacts, users, roles, audit actors and correlation identifiers.

Source identifiers may be preserved when valid and collision-free. Otherwise, the target identifier changes and the mapping remains durable and exportable.

## Historical execution semantics

Historical records are imported as history, not re-executed work. Their imported state is marked with source provenance and importer version.

AMESH does not fabricate missing events to imply stronger evidence than the source provided. When the source exposes only snapshots, the importer records that limitation rather than inventing an event history.

## Logs, metrics and artifacts

Large data is streamed in bounded memory and imported in chunks. Artifacts use cryptographic checksums and object-store addressing. Logs preserve timestamp, level, source execution/task identity and redaction state where available.

Metrics that cannot be represented losslessly may be retained as an attached source dataset rather than rewritten into native metrics.

## Governance and audit data

Identity and permission migration requires explicit mapping rules and negative authorization tests. Imported audit events remain distinguishable from native AMESH audit events while preserving chronology and actor provenance.

An imported event cannot claim AMESH cryptographic chaining or transactionality that did not exist in the source. AMESH can sign the import package and subsequent storage without rewriting historical truth.

## Failure and recovery

The importer tolerates interruption through checkpoints and idempotent chunk commits. It must handle:

- network interruption;
- expired credentials;
- target restart;
- duplicate bundle delivery;
- partial object upload;
- checksum failure;
- insufficient storage;
- missing plugin or secret provider;
- source changes after discovery;
- operator cancellation.

No failed or cancelled migration silently enables triggers or deletes source data.

## Implemented local tooling

The `amesh.kestra-migration/v1` models and CLI implement the bundle, stable identifier, dry-run,
secret-reference, checkpoint, idempotency and reconciliation contracts described above. The
[operator runbook](../operations/kestra-migration.md) gives the supported commands. Extraction from
an external Kestra instance remains source-side work; AMESH consumes a versioned bundle and never
requires direct access to the source database.
