# Workflow apps and human tasks

Workflow apps are versioned, permission-scoped entry points to a pinned flow revision. Human tasks
use the existing durable task-deferral contract: the executor stores only a resume-token digest, a
decision first enters durable `PENDING` resume state, and retrying the decision or worker
reconciliation cannot complete the task twice.

## Try the Compose sample

Open `http://localhost:8000`, connect with token `development-token` and tenant `default`, then choose
**Apps**. The deployed `Expense review` sample generates its requester, amount and purpose controls
from the flow inputs. Submit it, return to **Apps & approvals**, enter an accounting code, and approve,
reject or request changes. The linked execution shows the recorded decision in task output and
evidence.

The same authorized app form has stable browser links:

- `/apps/demo.apps/expense-review` — control-room view;
- `/embed/apps/demo.apps/expense-review` — shell-free view suitable for an iframe or portal.

Both routes bootstrap the same authenticated UI session and call the same authorized API. The embed
route is not an authentication bypass.

## App API

- `GET /api/v1/apps` lists visible current revisions.
- `GET /api/v1/apps/{namespace}/{appId}?revision=N` reads the current or an immutable historical
  revision.
- `PUT /api/v1/apps/{namespace}/{appId}` creates a revision. Supply `expectedVersion` for an update;
  stale writes return `412`.
- `POST /api/v1/apps/{namespace}/{appId}/launch` validates form values against the pinned flow input
  contract and creates an execution.

If `form` is omitted, AMESH maps the flow input display name, description, placeholder, default,
allowed values, validation metadata, sensitivity and schema into controls. An explicit form may add
sections, columns and help text, but it cannot introduce an unknown flow input or hide a required
input without a default.

```json
{
  "title": "Expense review",
  "description": "Submit a reimbursement request.",
  "flowId": "expense_review_demo",
  "launchLabel": "Submit for approval"
}
```

## Approval task DSL

`core.approval` pauses its task run without holding a worker. At least one user assignee or group is
required. A deadline changes an open task to `ESCALATED`; escalation participants replace the initial
participants when supplied. Delegation is an explicit durable action.

```yaml
- id: approval
  type: core.approval
  title: Review expense request
  description: Confirm the amount and business purpose.
  assigneeIds:
    - 00000000-0000-7000-8000-000000000001
  groupIds: []
  deadlineSeconds: 86400
  escalationGroupIds: []
  form:
    fields:
      - id: accountingCode
        type: text
        label: Accounting code
        helpText: Enter the cost center used for this expense.
        required: true
    layout:
      - title: Approval details
        fields: [accountingCode]
```

Use `deadlineAt` with a timezone instead of `deadlineSeconds` when a fixed instant is required.

## Participant API and audit behavior

- `GET /api/v1/human-tasks` returns tasks assigned directly to the caller or one of their groups;
  callers with `human_task.manage` can operate the namespace-wide queue.
- `POST /api/v1/human-tasks/{humanTaskId}/actions` accepts `APPROVE`, `REJECT`,
  `REQUEST_CHANGES`, `COMMENT`, `ATTACH` and `DELEGATE`. Every request needs an `idempotencyKey`.
- `GET /api/v1/human-task-notifications` returns participant-safe assignment, escalation, delegation
  and decision notices.

Terminal decisions persist actor, time, reason and form values in the human-task action/audit ledger
and in task completion evidence. Notification payloads intentionally contain only the human-task ID,
title, message and deadline; execution IDs and submitted form values are excluded.

The database tables are tenant-RLS protected. Namespace authorization is applied before app read,
authoring, launch, inbox access or task mutation. Resume tokens are deterministically derived on the
server with the configured token pepper and are never returned by the human-task API.
