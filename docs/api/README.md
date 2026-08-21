# API contracts

- `openapi.json` is generated from the foundation FastAPI application.
- Public API compatibility is validated against the checked-in document in CI once the regeneration
  script is added in EPIC-400.
- The current endpoints cover health, flow validation and management, execution control, webhook triggers, logs, authorization administration and decision explanation.
- Resource-bearing operations authenticate and authorize server-side. The development bootstrap token is unavailable outside development mode; durable login and credential entry points remain under EPIC-403/EPIC-501.
- They are not the complete compatibility API; gaps remain explicit until the version-pinned ADR-009 façade epics are verified.

Future generated SDKs must consume the supported API contract, not internal Python classes.
