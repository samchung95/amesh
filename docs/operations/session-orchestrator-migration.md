# Migrate an Agent Session Orchestrator cluster

This runbook moves a complete self-hosted Agent Session Orchestrator deployment. PostgreSQL and the
versioned object store are the authoritative state. Containers, pods, service registrations, leases,
claims, scheduler ownership and search projections are disposable process state; never copy them as
the migration mechanism.

Use profile or session transfer from the Session Orchestrator workbench when moving selected agents
or eligible sessions. Use this runbook only when moving the whole deployment.

## Preconditions

- Source and destination use the same AMESH release, migration manifest and harness adapter pins.
- The destination has separate PostgreSQL and versioned object-storage authorities and is not
  receiving application traffic.
- Destination auth, encryption, identity-provider, model-provider and MCP credential references are
  provisioned out of band. No secret value is present in a recovery manifest.
- `amesh recovery verify-latest` has passed against an isolated restore target.
- Operators can stop ingress, inspect `/api/v1/operations/topology`, drain each live service with
  `POST /api/v1/operations/services/{id}/drain`, and restore PostgreSQL/object versions.

Do not start a migration while a provider or tool invocation has an ambiguous outcome. Let it finish,
or pause its session at a clean `PAUSED` execution / `READY` session checkpoint first.

## Coordinated migration

1. **Prepare the destination.** Render `docker/compose.session-orchestrator.yaml` or
   `charts/amesh/profiles/session-orchestrator.yaml` with destination-only secret references. Keep
   ingress disabled and do not start schedulers or executors against the source database.
2. **Stop new source admissions.** Remove application traffic at the source proxy or load balancer,
   while retaining an administrator connection. Record the cutover reason and time.
3. **Drain canonical work.** Read the service topology, request a version-fenced drain for every live
   executor and scheduler, and wait until no new ownership is acquired. Confirm each session is
   terminal or at a clean checkpoint and there are no live leases, admission claims, unresolved
   approvals or `STARTED` external invocations.
4. **Create one coordinated recovery point.** Run:

   ```text
   uv run --extra runtime amesh recovery create --actor operator:session-migration
   uv run --extra runtime amesh recovery verify-latest \
     --profile v1 --actor operator:session-migration-verify
   ```

   Use exactly the database LSN, object version IDs, manifest checksum and configuration fingerprint
   from that recovery point. Never combine database and object snapshots from different manifests.
5. **Restore without traffic.** Restore PostgreSQL to the recorded LSN and every object by its exact
   provider version and checksum. Fence restored service registrations, scheduler ownership, leases
   and claims; rebuild disposable search/analytics projections. Apply only forward-compatible schema
   migrations for the selected AMESH release.
6. **Rebind protected configuration.** Mount destination database, object-store, auth, encryption,
   identity, model-provider and MCP references. Compare the redacted configuration fingerprint and
   explicitly approve intentional endpoint differences. Do not copy broker or client-domain
   credentials into the orchestrator profile.
7. **Qualify the destination.** With ingress still disabled, require `/ready` to report the expected
   migration count, verify service topology/version compatibility, reconcile every tenant, inspect
   fleet totals and traces, and run one provider-free terminal session recovery check. Run an opt-in
   `openai/gpt-5.6-luna` smoke only when the destination model credential is intentionally available.
8. **Cut over once.** Fence the source so it cannot resume admissions, enable destination ingress,
   update clients to the destination endpoint and observe session creation, event cursors, evidence
   and artifact reads. Keep the source read-only until the rollback window closes.

## Rollback boundary

Before the destination accepts a write, rollback means disabling destination ingress and reopening the
still-fenced source. After the destination accepts a write, never reopen the old source database: that
would create two authorities and duplicate sessions or external effects. Stop traffic, take a new
coordinated destination recovery point, and restore that point into the rollback environment instead.

Record the source and destination release, migration version, recovery-point ID/checksum, object count,
unresolved gaps, cutover time, first destination write and rollback decision as immutable compliance
evidence.

## Qualification boundary

The Docker-local and Helm profiles prove configuration, role and secret-reference boundaries. The
existing recovery exercise proves a coordinated PostgreSQL/object restore and ownership fencing for
the reference environment. This is not a production multi-region, provider-specific PITR, load,
failover-time or arbitrary external-dependency qualification. Those claims require a rehearsal in the
operator's actual PostgreSQL, object-storage, identity, network and model-provider environment.
