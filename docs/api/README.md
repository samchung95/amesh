# API contracts

- `openapi.json` is generated from the foundation FastAPI application.
- Public API compatibility is validated against the checked-in document in CI once the regeneration
  script is added in EPIC-400.
- The current endpoints cover health, flow validation and management, execution control, webhook triggers, logs, authorization administration, decision explanation, service-account API tokens and workload credential exchange.
- Flow validation accepts YAML or JSON and returns the versioned `amesh.flow/v1` canonical form. Blocking issues include stable codes, data paths, source ranges and remediation hints; see the [flow DSL contract](../architecture/flow-dsl.md).
- Resource-bearing operations authenticate and authorize server-side. The development bootstrap token is unavailable outside development mode; durable service/workload credentials work in every mode, and interactive users use revocable PostgreSQL-backed browser sessions with CSRF protection.
- They are not the complete compatibility API; gaps remain explicit until the version-pinned ADR-009 façade epics are verified.

Future generated SDKs must consume the supported API contract, not internal Python classes.
