# Backend language evaluation

## Status

**Decision:** Accepted on 2026-08-16 — Q-006  
**Selected architecture:** Java 25 for the modular durable control plane

The recommendation is not based on Java being fashionable or universally superior. It follows from AMESH’s unusual combination of requirements:

1. exact Kestra-facing compatibility, including Pebble expression behavior;
2. a long-running transactional control plane built around PostgreSQL;
3. durable scheduling, retries, leases, fencing and crash recovery;
4. on-premises Kubernetes operation;
5. a language-neutral plugin boundary;
6. implementation and review performed mostly by AI engineering agents.

The existing Python code remains an executable specification. It is not a commitment to Python for the production engine.

## The main reason: compatibility costs more than raw execution speed

AMESH does not merely need to run DAGs. It must reproduce version-pinned YAML, Pebble, API, CLI, import/export and execution behavior.

Pebble is a Java templating engine. A Java core can use the same public engine and extension model directly for parser, escaping, filter, function, error and null-behavior conformance. A Go, Rust, Python or TypeScript core would need either:

- a clean-room reimplementation of Pebble semantics;
- a permanent JVM compatibility sidecar; or
- a deliberate compatibility gap.

The third option is incompatible with the accepted parity promise. The first is expensive and fragile. The second is viable, but it creates a polyglot distributed dependency in the most frequently exercised compatibility path.

Java also leaves open a transitional JVM bridge if plugin-configuration migration proves more difficult than expected. AMESH still defaults to isolated language-neutral plugins; Java is not permission to run arbitrary third-party JARs inside the control plane.

## Why Java fits the durable control plane

### Transactional and operational maturity

The control plane is primarily an I/O-heavy state machine. It repeatedly performs PostgreSQL transactions, row claims, lease renewal, HTTP calls, object-storage operations, log writes and worker communication. Java has mature libraries and operational practice for JDBC, connection pools, migrations, gRPC, OpenTelemetry, metrics, TLS, structured logging and long-lived services.

This does not automatically make Java code correct. AMESH still requires explicit transaction boundaries, fencing tokens, idempotency, property tests, failure injection and database-backed integration tests.

### Concurrency without forcing a reactive architecture

Modern Java virtual threads allow a straightforward thread-per-operation programming style for large numbers of I/O-bound tasks. They increase throughput by allowing blocked operations to release their carrier threads; they do not make CPU work intrinsically faster.

That model suits AMESH because most control-plane operations wait on PostgreSQL, storage, workers or external services. CPU-intensive user tasks remain outside the control plane behind local, Docker or Kubernetes runners.

### Strong feedback for AI engineering agents

Java is widely represented in public training material, has stable conventions, and gives immediate compiler and static-analysis feedback. That matters when many AI implementation agents work in parallel. The language’s verbosity is a cost, but explicit types and uniform patterns make independent review and generated-code verification easier than in a highly dynamic core.

Java is not selected because an AI model “knows Java best.” It is selected because mistakes become visible earlier through compilation, architecture tests and typed contracts.

### On-premises supportability

An on-premises operator benefits from mature JVM diagnostics such as thread dumps, Java Flight Recorder, heap diagnostics and established support across Linux distributions and Kubernetes platforms. AMESH should baseline on JDK 25 using a maintained OpenJDK distribution and avoid preview features in durable public contracts.

## Costs and disadvantages of Java

Java has material drawbacks that the architecture must accept rather than hide:

- higher idle memory than a comparable Go service;
- larger runtime images unless custom runtime images are built;
- slower cold start and build cycles than Go;
- garbage-collection and allocation behavior that still require profiling;
- risk of accidental framework complexity, reflection and hidden lifecycle behavior;
- JVM and dependency patching obligations for on-premises users;
- more verbose implementation than Kotlin, Python or TypeScript;
- temptation to load plugins in-process because they are also JVM-based.

Mitigations include modular boundaries, small runtime images, explicit dependency injection, immutable records, sealed domain hierarchies, architecture tests, bounded allocation, JFR-based profiling and an out-of-process plugin default.

## Comparison

| Option | Main advantages | Main disadvantages | AMESH fit |
|---|---|---|---|
| **Java 25 core** | Direct Pebble integration; mature PostgreSQL and server ecosystem; strong static analysis; virtual threads for I/O-heavy concurrency; large contributor and AI-training corpus; transitional JVM bridge remains possible | Higher memory and image footprint; slower builds; verbosity; GC and JVM patching; framework overengineering risk | **Best balance for exact parity and durable operation** |
| **Kotlin core** | Same JVM ecosystem and Pebble access; concise models; expressive type system | Smaller training and maintainer corpus; mixed Java/Kotlin idioms; coroutine and compiler-plugin complexity; generated code is less uniform | Good alternative when the maintaining team is already Kotlin-heavy |
| **Go core** | Small static binaries; fast builds; low memory; simple deployment; straightforward concurrency; excellent remote-worker fit | Pebble and JVM compatibility require reimplementation or a sidecar; dynamic DSL models are less ergonomic; compatibility split becomes permanent | Best alternative when footprint and operational simplicity outrank single-process compatibility |
| **Rust core** | Memory safety; excellent efficiency; strong type system | Highest implementation and review cost; slower compilation; dynamic schema/plugin work is harder; fewer engineers and examples | Better for a later sandbox, runner or high-risk native component |
| **Python core** | Fastest prototyping; excellent AI/ML ecosystem; flexible schema work | Dynamic runtime; harder concurrency and long-running-service guarantees; packaging and process model complexity; Pebble mismatch | Keep for SDKs, plugins, test generation and executable specifications |
| **TypeScript/Node core** | Shared language with React; strong API productivity; large package and AI corpus | Package churn; runtime memory behavior; CPU-heavy reduction; Pebble mismatch; weaker fit for the state engine | Good for SDKs and integration services, not the preferred durable core |
| **Polyglot services from day one** | Each component can use an individually optimal language | Multiple build systems, deployments, wire protocols, traces and failure modes before semantics stabilize | Avoid until profiling demonstrates a concrete boundary |

## Why not Go as the default?

Go is the strongest alternative. It would likely produce smaller images, faster builds and simpler on-premises operations.

The reason it was not selected is that AMESH has accepted **all compatibility surfaces**, not merely equivalent orchestration capability. With Go, the project must commit immediately to one of two additional programmes:

1. implement Pebble and other JVM-adjacent behavior independently, then maintain differential parity forever; or
2. operate a JVM compatibility service beside the Go core and design its availability, caching, versioning, tracing and failure semantics.

That overhead may still be worthwhile. A future superseding ADR may choose Go only if measured footprint and operational benefits outweigh the permanent compatibility-service or reimplementation cost.

## Why Java rather than Kotlin?

Both run on the JVM and can use Pebble directly. Java was selected for this AI-heavy programme because its style is more uniform, its compiler/build surface is simpler, and there is a larger body of established examples for independent implementation and review.

Kotlin is a valid choice when concise domain modeling is valued more highly and the project is willing to standardize coroutine use, nullability conventions, build plugins and Java interop rules from the beginning.

## Accepted architecture

```text
React + TypeScript UI
          |
REST / WebSocket / generated clients
          |
Java 25 modular durable control plane
- native domain model and state reducer
- Kestra compatibility facade
- source-preserving YAML model
- Pebble compatibility
- API, executor, scheduler and triggers
- PostgreSQL queues, leases and projections
- identity, policy, audit and tenancy
          |
Protobuf/gRPC + OCI capability protocol
          |
Java / Python / TypeScript plugin SDKs
Local / Docker / Kubernetes runners
Optional Go worker or sandbox components after profiling
```

Binding Java constraints:

- use a maintained OpenJDK 25 distribution;
- do not depend on preview language features for persisted or public contracts;
- keep the deterministic reducer independent of web and persistence frameworks;
- use explicit SQL and transaction semantics for correctness-critical paths;
- use virtual threads only for suitable I/O-bound operations and monitor pinning;
- prohibit third-party in-process plugins by default;
- use generated Protobuf/OpenAPI types at process boundaries;
- use Testcontainers or equivalent real-PostgreSQL tests for concurrency behavior;
- retain Python golden fixtures until Java passes equivalent differential tests.

## Implementation transition plan

1. Freeze the Python flow model, validator and reducer as versioned behavioral fixtures.
2. Create a Java 25 modular build and replay all Python golden fixtures against it.
3. Implement the canonical resource model, source-preserving YAML and Pebble compatibility first.
4. Implement PostgreSQL repositories, queues, leases, fencing and transactional outbox.
5. Move the REST/CLI compatibility façade only after domain parity is proven.
6. Implement local, Docker and Kubernetes runners behind the language-neutral runner contract.
7. Retain Python for SDKs, AI integrations, conformance generation and optional plugins.
8. Split out Go or Rust components only after profiling identifies a measurable reason.

## Decision outcome

The product owner accepted the Java 25 option on 2026-08-16. Replacing it requires a superseding ADR with compatibility, migration, operational, performance and AI-maintainability evidence. Go and Rust remain available for isolated components only when profiling or threat analysis demonstrates a concrete benefit.
