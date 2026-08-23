# Plugin governance API

AMESH evaluates durable plugin policy at flow validation, flow save, execution start and plugin
administration. Rules can match package and vendor globs, semantic-version ranges, resource types and
declared capabilities at instance, tenant or namespace scope. An explicit deny or active quarantine
always overrides an allow.

Production-oriented `signed-only` trust starts fail-closed for unmatched third-party packages.
`amesh.core` remains implicitly allowed unless an explicit rule or quarantine denies it. Set
`PLUGIN_TRUST_MODE=development` only when an intentionally permissive local plugin workspace is
required.

## Inspect and evaluate policy

- `GET /api/v1/plugin-policy/effective?namespace=team.data` returns every effective rule and
  quarantine, its scope and source identifier, plus the unmatched-package default.
- `POST /api/v1/plugin-policy/evaluate?stage=VALIDATION` accepts a YAML or JSON flow document and
  returns one explained decision per exact package pin. The other stages are `AUTHORING`, `EXECUTION`
  and `ADMINISTRATION`.
- `GET /api/v1/plugin-policy/decisions` returns durable recent decisions, including the source of
  each allow or deny.

Create a rule with `POST /api/v1/plugin-policy/rules`:

```json
{
  "scope": "NAMESPACE",
  "namespace": "team.data",
  "effect": "ALLOW",
  "stages": ["AUTHORING", "VALIDATION", "EXECUTION"],
  "selector": {
    "package": "acme.warehouse",
    "versionRange": ">=2.1.0,<3.0.0",
    "vendor": "Acme *",
    "pluginTypes": ["task:acme.query"],
    "capabilities": ["network:restricted", "secret:warehouse"]
  },
  "priority": 100,
  "reason": "Security review SEC-142",
  "enabled": true
}
```

Use `PUT /api/v1/plugin-policy/rules/{id}` to replace a rule and
`DELETE /api/v1/plugin-policy/rules/{id}` to remove it. All rule changes and denied evaluations are
written to the tamper-evident audit ledger.

## Version freeze and execution gates

Flow revisions retain the resolver's exact package version, content digest and resource pins. A
catalog refresh can affect a newly authored revision, but cannot change a stored revision or an
execution that references it. Policy is evaluated against the candidate pins before save and against
the stored pins again before every execution start, including schedules, triggers, backfills and
subflows.

Plugin bundle installation first validates the archive and evaluates its manifest at the
`ADMINISTRATION` stage. A denied bundle is not installed.

## Emergency disable

1. Send the intended exact package/version quarantine to
   `POST /api/v1/plugin-policy/quarantines/preview`.
2. Review `affectedFlows` and `runningExecutions`.
3. Send the same request to `POST /api/v1/plugin-policy/quarantines`.

An active quarantine blocks new starts immediately but does not delete registry data, revision pins,
past decisions or running execution evidence. It also does not kill already-running work. Release a
remediated quarantine with
`POST /api/v1/plugin-policy/quarantines/{id}/release?reason=...`.

The Plugins page exposes the same effective-policy, rule and impact-preview workflow. Server-side
authorization remains authoritative; policy changes require plugin administration permission.
