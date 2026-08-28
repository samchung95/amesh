# Execution checks

Execution checks record operational compliance without changing execution or task state. The supported
types are `DURATION`, `START_DELAY`, `FRESHNESS`, `COMPLETION_WINDOW`, `OUTPUT` and `EXPRESSION`.

## Define checks on a flow

```yaml
checks:
  - id: duration-budget
    type: DURATION
    threshold: PT5M
  - id: useful-output
    type: OUTPUT
    severity: WARN
    expression: "{{ outputs.result.value == inputs.expected }}"
    actions:
      - type: NOTIFY
        channel: operations
        maxAttempts: 3
```

Threshold checks require a positive ISO-8601 duration. Output/expression checks require a bounded
boolean expression. A false condition becomes the declared `WARN` or `FAIL`; an evaluation exception
becomes `ERROR`. These outcomes never rewrite the execution state.

`START_DELAY` compares the actual start with trigger `scheduledFor` when present. `DURATION` measures
execution elapsed time, `COMPLETION_WINDOW` anchors to `scheduledFor`, and `FRESHNESS` opens a new
database-time window when a revision activates or completes.

## Reuse policies

Create or replace a named namespace policy:

```http
PUT /api/v1/check-policies/team.data/standard-duration
Content-Type: application/json

{
  "source": "NAMESPACE",
  "definition": {
    "id": "standard-duration",
    "type": "DURATION",
    "threshold": "PT10M"
  }
}
```

Select it with `checkPolicies: [standard-duration]`. For an automatic task-type default, use source
`PLUGIN_DEFAULT` and include `taskType`. Effective policies are pinned when the flow revision is first
stored; increment the revision after changing a reusable policy.

## Inspect evidence

- `GET /api/v1/check-policies` lists reusable definitions.
- `GET /api/v1/check-evaluations` lists immutable evidence and accepts namespace, `flowId`,
  `executionId`, outcome and limit filters.
- `GET /api/v1/check-compliance?groupBy=flow` aggregates outcomes. Supported groupings are `tenant`,
  `namespace`, `flow`, `day`, `week`, `month` and `label:<key>`.
- Open `/checks` for the live compliance, evaluation and policy views.

Every evaluation exposes its point, outcome, reason, threshold/expression evidence, labels and time.

## Violation actions and recovery

`NOTIFY` writes an `amesh.check.notification.<channel>` message to the durable outbox. `RUN_FLOW`
creates an ordinary idempotent execution with the evaluation details as inputs. Each action has a
leased claim, maximum attempts and durable terminal evidence. `maxDepth` defaults to four; an action
whose incoming `checkPolicyDepth` reaches that limit is recorded as `SKIPPED` and is not claimed.

Run the scheduler role to evaluate deadlines and actions. On retry, inspect `check_action_queue` state
through PostgreSQL diagnostics and the evaluation reason through the authorized API. Do not delete
evaluation or action rows while investigating an incident.
