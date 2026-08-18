# Decision status — no blocking questions

All foundational product-owner questions `Q-001` through `Q-022` are accepted as of **2026-08-16** and recorded in [`docs/product/decision-register.md`](docs/product/decision-register.md).

**No product-owner decision blocks the start of M0 implementation.**

## Final foundational decision — Q-006

AMESH will use:

- **Java 25** for the modular durable control plane;
- **React and TypeScript** for the web client;
- a language-neutral Protobuf/gRPC and OCI boundary for plugins and runners;
- Java, Python and TypeScript as the first plugin SDKs;
- the existing Python validator and reducer as an independent executable specification until Java passes equivalent golden, property and differential tests;
- Go or Rust components only after profiling demonstrates a concrete operational or safety benefit.

The accepted rationale and transition plan are in:

- [`docs/adr/010-production-core-language.md`](docs/adr/010-production-core-language.md)
- [`docs/architecture/backend-language-evaluation.md`](docs/architecture/backend-language-evaluation.md)

## What may still be decided during implementation

Implementation ADRs may select libraries, module boundaries, build plugins, test harnesses and deployment details without reopening the product architecture. They require product-owner input only when they change compatibility promises, licence policy, security boundaries, release gates, migration guarantees, supported deployment profiles or other accepted requirements.

Begin with [`docs/product/implementation-kickoff.md`](docs/product/implementation-kickoff.md).
