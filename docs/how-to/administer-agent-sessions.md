# Administer agent sessions

Open **Session orchestrator** under **Govern** to operate sessions separately from the application
user's **Agent sessions** control room. The workbench shows only the sessions permitted by the
selected tenant and the server-authoritative session-administration permissions.

## Understand the fleet

The summary cards answer how many sessions are active or terminal, how many tokens, turns and tool
calls the filtered fleet consumed, its recorded cost and whether any dependency invocation failed.
Use the state, namespace, agent, owner, harness and creation-time selectors to narrow the fleet.
Pages are newest first; **Load more sessions** follows the opaque server cursor without changing the
filter snapshot.

Select a session ID to open its canonical redacted event trace and current lifecycle projection.
The workbench intentionally omits prompt payloads, tool arguments, credentials, checkpoint content
and hidden reasoning. Use the execution and evidence APIs when a permitted investigation needs the
broader canonical execution record.

Instance administrators can also see metadata-only tenant totals. Tenant administrators do not
request that instance projection. Selecting another tenant changes the normal `X-Amesh-Tenant`
context and causes a fresh authorization decision before any session row is disclosed.

## Control sessions

An authorized session administrator can pause or cancel active work, resume paused work and retry a
terminal unsuccessful attempt. Every action carries the canonical execution version and epoch shown
by the fleet read; a concurrent state change is rejected instead of applying to stale state.

For a bulk action:

1. Select at most 25 visible sessions.
2. Choose the lifecycle action and review the exact affected count.
3. Confirm the action.
4. Inspect the applied and rejected counts, then refresh any rejected rows before deciding whether
   to retry them.

Bulk controls are intentionally bounded and independently fenced. A partial response means earlier
items were applied through their canonical execution controls while rejected items were left
unchanged; it is not an all-or-nothing transaction.

## Govern admission and capacity

The policy panel is visible only with the session-policy view capability. Choose a namespace and,
when relevant, an application to see the exact effective revision chain, digests, provenance,
tightest limits and allowlists. A policy administrator can create or edit tenant, namespace and
application scopes; updates carry the currently displayed revision and stop with a conflict if
another administrator saved first.

Session policies constrain new admissions and immutable dependency pins. They do not rewrite an
active session. Retention starts at terminal completion and is applied through the existing
lifecycle preview/confirmation workflow, so legal holds, bounded purge batches and external artifact
deletion evidence stay intact. A zero-second retention value makes a terminal session immediately
eligible for the next matching lifecycle job; it does not delete an active or paused session.

## Move a profile or session

Use **Portability** in the Session Orchestrator workbench for a selective move. Export the profile
first when the destination does not already contain the exact agent and dependency revisions.
Downloaded bundles are digest-protected JSON files and contain references rather than credential
values.

To import a profile:

1. Choose the source namespace and agent, then download its profile bundle.
2. Switch to the destination deployment and upload that JSON file.
3. Run the compatibility plan and review its exact digest, target namespace, resources to create or
   reuse, MCP references and every reported issue.
4. Import only when the plan is compatible. A repeated import of the same bundle is reported as
   already present rather than creating duplicate revisions.

To move a session, first pause admission to that session and select one supported mode. A terminal
history must be fully complete. A clean checkpoint must have a paused execution, a `RUNNING` session
at `READY`, and no live lease, claim, approval or unresolved external invocation. Download the
bundle, upload it at the destination, acknowledge each displayed stable credential reference, and
run the compatibility plan. Import stays disabled until the exact flow revision, capability pin,
harness, credential references and artifact checks pass.

The workbench preserves artifact URIs by default. Stage every referenced object at the destination
under the same URI, size and checksum before planning. An API client can supply a complete source-to-
destination artifact map during export when the destination keys must differ.

The bundle does not move provider, MCP or platform secret values. Provision those values at the
destination under the same stable references before import. Do not edit the downloaded JSON between
planning and import. Use the
[whole-cluster migration runbook](../operations/session-orchestrator-migration.md) instead when
moving the entire PostgreSQL and object-storage authority.

See the [agent session administration API](../api/agent-session-administration.md) for permissions,
pagination and response boundaries.
