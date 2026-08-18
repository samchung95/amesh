# API contracts

- `openapi.json` is generated from the foundation FastAPI application.
- Public API compatibility is validated against the checked-in document in CI once the regeneration
  script is added in EPIC-400.
- The current endpoints demonstrate health, flow validation and deterministic execution reduction only.
- They are not the complete product API and may change before ADR-009 is accepted.

Future generated SDKs must consume the supported API contract, not internal Python classes.
