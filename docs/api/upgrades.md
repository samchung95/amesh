# Upgrade API

All upgrade endpoints require instance `manage` authorization. They are native AMESH v1 operations;
they do not imply compatibility with another product's upgrade mechanism.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/upgrades/policy` | Return supported LTS releases, paths, component minimums and rollback policy. |
| `POST` | `/api/v1/upgrades/preflight` | Evaluate an upgrade before rollout. |
| `POST` | `/api/v1/upgrades/postflight` | Verify the target schema and runtime after rollout. |
| `GET` | `/api/v1/upgrades/events/upcast` | Preview historical execution events eligible for schema upcast. |
| `POST` | `/api/v1/upgrades/events/upcast` | Apply one confirmed bounded event batch and return audit evidence. |
| `POST` | `/api/v1/upgrades/configuration/migrate` | Canonicalize one flow or plugin document for a target release. |

Preflight and postflight accept:

```json
{"fromVersion":"0.1.0","toVersion":"0.2.0"}
```

The response contains `safeToProceed`, `rollingCompatible`, categorized checks with remediation,
warnings, the ordered rolling plan, restoration guidance and a reproducible `reportFingerprint`.
Unsupported versions or paths return `422`.

Event upcast preview returns an exact `confirmationPhrase`. Send that phrase unchanged with an
operator reason and a batch size from 1 through 10,000:

```json
{"confirmation":"UPCAST 12","reason":"CHG-123 supported LTS upgrade","batchSize":1000}
```

A stale or altered phrase returns `409`; preview again instead of guessing. A successful response
reports migrated and remaining rows plus `evidenceEventId`.

Configuration migration accepts `kind` as `flow` or `plugin`, a declared `targetVersion` and a JSON
`document`. It returns a canonical document without publishing it. Invalid source documents or plugin
platform ranges that exclude the target return `422`.
