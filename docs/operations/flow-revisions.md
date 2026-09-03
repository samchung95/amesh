# Flow revision operations

Flow definitions are immutable after creation. `PUT /api/v1/flows` treats the same revision and
semantic content as an idempotent reapply. It preserves an unused forward revision number and assigns
the next revision automatically when changed content collides with existing history.

Optional request headers record promotion provenance:

- `X-AMESH-Source`
- `X-AMESH-Commit`
- `X-AMESH-Environment`
- `X-AMESH-Deployment`

Authorized workflow authors can use these endpoints:

| Operation | Endpoint |
|---|---|
| List immutable history and resolution metadata | `GET /api/v1/flows/{namespace}/{flow}/revisions` |
| Compare two revisions | `GET .../revisions/diff?from=1&to=2` |
| Select a revision and lifecycle | `PUT .../revisions/{revision}/lifecycle` |
| Restore an earlier revision as active | `POST .../revisions/{revision}/restore` |
| Delete an unselected, unreferenced revision | `DELETE .../revisions/{revision}` |

Lifecycle values are `DRAFT`, `ACTIVE`, `DISABLED` and `ARCHIVED`. Only active flows can launch new
executions. Restore moves the selected pointer to the earlier row; revision definitions, hashes and
history remain unchanged.

The `flow_revisions` row owns the exact canonical definition, semantic hash and plugin resolution for
that revision. Repository reads return an immutable revision snapshot containing those row values;
export, draft diff and execution determinism evidence use the stored document and hash rather than
recomputing them from a parsed model. This preserves historical hashes when newer application defaults
expand the in-memory representation. `get_flow` remains the compatibility projection for callers that
need only the parsed flow.

Deletion returns conflict for the selected revision or a revision referenced by an execution or a
direct `flow_revision` audit record. Flow revision events are committed with their outbox messages;
operators can consume the `flow-revision-events` subject without observing uncommitted state.
