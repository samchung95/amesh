# How to promote, roll back, or stop a release

Use the release-gate API to preview a tenant's exact policy evidence before applying a promotion.
AMESH never selects thresholds or performs a client's production cutover.

## Use the web console

Open `/releases`, choose the target type and stable target key, then select **Inspect target**.
Enter the immutable policy ID and preview its evidence before applying it. Operators with
`releases.manage` can promote a passing gate, roll back to an exact revision from history, or
activate the kill switch; `releases.view` users remain preview-only.

## Use the client-neutral API

Send the authenticated tenant context on every request. The main sequence is:

1. `POST /api/v1/releases/policies/{policy-id}/preview`
2. `POST /api/v1/releases/policies/{policy-id}/apply` with `expectedVersion` and `reason`
3. `GET /api/v1/releases/{kind}/{target-key}` and
   `GET /api/v1/releases/{kind}/{target-key}/history`

Recovery uses `POST /api/v1/releases/{kind}/{target-key}/rollback` or
`POST /api/v1/releases/{kind}/{target-key}/kill-switch`, also with the target's current
`expectedVersion` and an operator reason.

## Verify a gate

Create immutable evidence with the target `configurationDigest`, then create a policy that lists
the exact evidence digests. Preview is side-effect free and requires the preview authorization.

```bash
uv run amesh --tenant <tenant> releases preview <policy-id>
```

The preview must report `passed: true`. Stale, expired, failed, tenant-mismatched, or differently
pinned evidence is rejected.

## Apply a promotion

Supply the target's current `expectedVersion` and a reason. Preview and apply use separate
authorization actions; apply writes an immutable history event and an outbox message in the same
PostgreSQL transaction.

```bash
uv run amesh --tenant <tenant> releases apply <policy-id> \
  --expected-version 0 \
  --reason "qualified release"
```

Retry with the returned version if the command reports an optimistic-concurrency conflict. Do not
retry with a different policy or evidence under the same request identity.

## Roll back or stop immediately

Rollback names an exact revision already present in release history. The kill switch changes the
target to `KILLED` immediately while retaining its exact active revision and complete history.

```bash
uv run amesh --tenant <tenant> releases rollback <kind> <target-key> \
  --to-revision <revision> --expected-version <version> \
  --reason "revert failed release"

uv run amesh --tenant <tenant> releases kill-switch <kind> <target-key> \
  --expected-version <version> --reason "stop release"
```

Inspect `GET /api/v1/releases/{kind}/{target-key}/history` after either action. The response is
the durable recovery record; restart does not clear the target, events, or outbox entries.
