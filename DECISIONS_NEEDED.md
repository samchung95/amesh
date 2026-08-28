# Decision status — no blocking questions

All foundational product-owner questions `Q-001` through `Q-022` are accepted and recorded in [`docs/product/decision-register.md`](docs/product/decision-register.md). Q-006 was amended on **2026-08-19**; everything else stands as accepted on **2026-08-16**.

**No product-owner decision blocks implementation.**

## Final foundational decision — Q-006 (amended 2026-08-19)

AMESH will use:

- **Python 3.12 asyncio** for the durable control plane — the checked-in foundation is the production core seed ([ADR-016](docs/adr/016-python-production-core.md), superseding ADR-010's Java 25 selection before any Java implementation began);
- **React and TypeScript** for the web client;
- a language-neutral Protobuf/gRPC and OCI boundary for plugins and runners;
- Java, Python and TypeScript as the first plugin SDKs;
- Go or Rust components only after profiling demonstrates a concrete operational or safety benefit.

The rationale is in:

- [`docs/adr/016-python-production-core.md`](docs/adr/016-python-production-core.md)
- [`docs/adr/010-production-core-language.md`](docs/adr/010-production-core-language.md) (superseded) and [`docs/architecture/backend-language-evaluation.md`](docs/architecture/backend-language-evaluation.md) (historical evaluation)

## What may still be decided during implementation

Implementation ADRs may select libraries, module boundaries, build plugins, test harnesses and deployment details without reopening the product architecture. They require product-owner input only when they change compatibility promises, licence policy, security boundaries, release gates, migration guarantees, supported deployment profiles or other accepted requirements.

Begin with [`docs/product/implementation-kickoff.md`](docs/product/implementation-kickoff.md).
