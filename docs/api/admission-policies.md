# Admission policy API

AMESH evaluates immutable `amesh.policy/v1` rules at workflow validation, save, promotion, launch and
task dispatch. The graphical editor runs the validation boundary before saving; active revisions and
recent evidence are available under **Plugins → Workflow admission policies**.

## Rule document

Create a tenant policy with `POST /api/v1/policies` or a new immutable revision with
`PUT /api/v1/policies/{policyKey}`:

```json
{
  "schemaVersion": "amesh.policy/v1",
  "policyKey": "security.local",
  "name": "Local runner policy",
  "description": "Require review before Docker launches.",
  "scope": "TENANT",
  "criticality": "ENFORCING",
  "evaluationTimeoutMs": 100,
  "enabled": true,
  "rules": [
    {
      "id": "review-docker",
      "stages": ["LAUNCH", "DISPATCH"],
      "conditions": [
        {"path": "runner.requested", "operator": "EQUALS", "value": "DOCKER"}
      ],
      "outcome": "REQUIRE_APPROVAL",
      "reason": "Docker workload execution requires security approval.",
      "mutations": {}
    }
  ]
}
```

Scopes are `INSTANCE`, `TENANT` and `NAMESPACE`; namespace scope requires `namespace`. Rule conditions
are an all-of set. Operators are `EQUALS`, `NOT_EQUALS`, `IN`, `CONTAINS`, `EXISTS`, `MATCHES`
(case-sensitive glob), `LESS_THAN`, `LESS_THAN_OR_EQUAL`, `GREATER_THAN` and
`GREATER_THAN_OR_EQUAL`.

Outcomes are:

- `DENY`: block the boundary.
- `WARN`: allow and retain the warning.
- `MUTATE_DEFAULT`: set only absent fields named in `mutations`.
- `REQUIRE_APPROVAL`: block unless the request contains `<policyKey>/<ruleId>` in `approvals`.
- `ALLOW`: record the match without changing the result.

Mutation paths may target nested `flow`, `runner`, `image`, `network` or `resource` fields. Secret and
credential paths are rejected. Conditions may inspect the typed `actor`, `tenant`, `namespace`,
`flow`, `plugin`, `runner`, `image`, `secret.scopes`, `network` and `resource` contexts; secret values
are never supplied.

## Evaluate and test

- `POST /api/v1/policies/flows/validate` accepts a YAML or JSON flow body and returns the `VALIDATE`
  decision used by the editor.
- `POST /api/v1/policies/evaluate` accepts a complete `PolicyEvaluationRequest`; the server replaces
  actor and tenant identity with the authenticated request context.
- `POST /api/v1/policies/{policyKey}/test?revision=N` runs one fixture against an exact revision and
  returns expected-versus-actual failures plus the complete explanation.
- `GET /api/v1/policies?namespace=default` returns effective active revisions.
- `GET /api/v1/policies/{policyKey}?revision=N` retrieves an exact historical revision.
- `GET /api/v1/policies/decisions?limit=100` returns recent tenant decision evidence.

Every decision includes `engineVersion`, outcome, `allowed`, exact policy revision/digest pins,
matched reasons and condition evidence, default mutations, approval keys, input hash and elapsed
evaluation time. Enforcing timeouts deny; advisory timeouts warn. The internal mutated input is never
returned or stored in the decision payload.

Ordinary flow save, promote, restore, launch and dispatch operations call the same evaluator. A
blocked operation returns the lifecycle API's conflict/error result, while its denied decision is
still retained in policy and audit history.
