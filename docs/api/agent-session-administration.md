# Agent session administration API

The agent session administration API is a separate control-plane surface over AMESH's canonical
executions and agent-session attempts. It does not create another scheduler, executor, transcript
store or evidence ledger.

## Tenant fleet

`GET /api/v1/admin/agent-sessions` requires both `agent_session_administration:view` and
`agent_session:list` in the requested tenant. Supply the tenant through `X-Amesh-Tenant`; there is
no elevated query parameter and no compatibility fallback to generic execution permissions.

The response is ordered by canonical execution creation time and execution ID, newest first. Use
the opaque `nextCursor` unchanged for the next page. A cursor is bound to the tenant and the exact
filter set, so reusing it with different filters is rejected. `limit` is bounded to 100. Supported
filters are `state`, `namespace`, `agentRef`, `ownerId`, `harness`, `createdFrom` and `createdTo`.

Each row contains the public session identity, latest attempt identity and state, owner, immutable
agent and harness provenance, canonical execution version/epoch fences, bounded counters,
dependency keys and dependency health. Private
checkpoint state, prompt content, final results, tool arguments, credentials and reasoning are not
part of this projection. The page also returns matched/active/terminal counts, counts by state,
token and cost totals, invocation totals and degraded-dependency counts for the complete filtered
set rather than only the current page.

## Guarded lifecycle controls

`POST /api/v1/admin/agent-sessions/actions` requires both
`agent_session_administration:view` and `agent_session:manage` at tenant scope. It accepts one
action (`cancel`, `pause`, `resume` or `retry`) and no more than 25 unique session items. Every item
must carry the `executionVersion` and `executionEpoch` returned by the fleet read. The request also
includes a reason and the exact phrase `<ACTION> <COUNT> AGENT SESSIONS`; an invalid phrase,
duplicate session or oversized batch is rejected before any mutation.

The response uses HTTP 207 and reports each item as `applied` or `rejected`. Items are independently
fenced canonical execution controls, so a rejected item does not roll back earlier accepted items.
Clients should refresh rejected rows before deciding whether to issue a new action.

## Instance overview and tenant drill-down

`GET /api/v1/admin/agent-sessions/aggregate` is an instance-scoped operation requiring
`agent_session_administration:view` and `agent_session:list`. It accepts no tenant header and
returns only tenant ID, tenant slug and lifecycle counts. It never returns session, owner, agent,
usage, cost or dependency details.

An instance administrator drills into a tenant by selecting its aggregate row and issuing the
tenant fleet request with that tenant's `X-Amesh-Tenant` value. The normal tenant authorization
decision and audit path is therefore applied independently before session metadata is disclosed.

## Versioned session policies

Policy reads require `agent_session_policy:view`; mutation requires
`agent_session_policy:manage`. The administration surface is:

- `GET /api/v1/admin/agent-session-policies` for revision history;
- `GET /api/v1/admin/agent-session-policies/effective` for the exact tenant, namespace and optional
  application policy chain;
- `GET /api/v1/admin/agent-session-policies/{policyId}` for one exact or latest revision; and
- `PUT /api/v1/admin/agent-session-policies` to create the next immutable revision.

Tenant, namespace and application policies are cumulative. Admission is denied if any applied
policy disables it. Concurrency, total-token, cost, duration and retention limits use the tightest
applied value; every non-empty provider, harness or tool allowlist must accept the pinned dependency.
The application scope used for launch is bound to the authenticated principal display identity, so a
client cannot select another application's policy scope. The applied policy IDs, revisions, digests
and effective retention are written into canonical execution provenance.

Send `expectedRevision: 0` when creating a scope and the currently read revision when updating it.
A stale value returns HTTP 409 without mutation. Revision creation and the actor are retained as
immutable audit evidence.

`retentionSeconds` is measured from the canonical terminal timestamp. Existing lifecycle policies,
impact preview/confirmation, bounded jobs, legal holds and artifact deletion decisions remain the
only purge authority. Active and paused sessions are never selected; a session becomes eligible when
its immutable launch-policy retention expires and a matching lifecycle job runs. Non-session
executions continue to use their lifecycle-policy cutoff.

The application-facing session endpoints remain documented in the
[agent session service API](agent-session-service.md).
