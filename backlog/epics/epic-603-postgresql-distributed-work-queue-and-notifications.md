# EPIC-603 — PostgreSQL distributed work queue and notifications

- **Milestone:** M6 — Distributed operations and reliability
- **Priority:** Must
- **Domain:** `messaging`
- **Primary persona:** Operator
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Scale durable orchestration using partitioned PostgreSQL queues, notifications, leases and dead-letter workflows without an external broker.

## In scope

- [ ] **URS-F-0606** — The system shall implement the internal messaging abstraction entirely on PostgreSQL using durable queue, outbox, inbox and lease records.
- [ ] **URS-F-0607** — The system shall shard and claim work by tenant and execution or trigger partition key while preserving required per-partition ordering.
- [ ] **URS-F-0608** — The system shall support independent consumer lanes, replay, retention, dead-letter and poison-message workflows on PostgreSQL.
- [ ] **URS-F-0609** — The system shall propagate trace context and message schema version through every durable queue envelope.
- [ ] **URS-F-0610** — The system shall manage queue schema compatibility and rolling producer or consumer upgrades without losing committed work.
- [ ] **URS-F-0611** — The system shall surface shard skew, oldest eligible age, lease expiry, redelivery, throughput, transaction latency and PostgreSQL health.
- [ ] **URS-F-0612** — The system shall recover from PostgreSQL failover or connection loss without losing committed outbox or queue records.
- [ ] **URS-F-0613** — The system shall document and benchmark semantic and capacity differences between single-host and horizontally scaled PostgreSQL queue profiles.

## Non-functional requirements

- [ ] **URS-NFR-AVAILABILITY-002** — The distributed topology shall tolerate loss of any one stateless service instance without operator intervention. Target: No accepted work lost; service recovers within 60 seconds of instance loss.
- [ ] **URS-NFR-PERFORMANCE-004** — The distributed reference profile shall sustain task dispatch and completion processing without unbounded lag. Target: Profile M target: 50 task starts per second sustained for 60 minutes with p95 dispatch latency below 3 seconds and no unbounded queue lag.

## Dependencies

- EPIC-009

## Architecture impact

- Primary bounded area: `messaging`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- PostgreSQL delivery, ordering, duplicate, failover and saturation conformance tests.
- Multi-replica chaos and zone-spread tests.
- Published benchmark on a fixed reference topology.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [ ] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [ ] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [ ] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [ ] Security, tenant isolation, redaction and audit behavior are reviewed.
- [ ] Documentation, examples, migration notes and operational runbooks are updated.
- [ ] Performance and recovery budgets are measured when this epic is on a critical path.
- [ ] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- PostgreSQL saturation becomes the dominant platform scaling boundary
- Hot partitions or long claim transactions can damage fairness and latency
- LISTEN/NOTIFY may be mistaken for durable delivery if tests are incomplete

## Traceability

- Functional requirements: URS-F-0606, URS-F-0607, URS-F-0608, URS-F-0609, URS-F-0610, URS-F-0611, URS-F-0612, URS-F-0613
- Non-functional requirements: URS-NFR-AVAILABILITY-002, URS-NFR-PERFORMANCE-004
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
