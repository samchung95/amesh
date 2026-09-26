# ADR-081: Focus AMESH on the governed agent-session runtime

Status: accepted by the product owner on 2026-09-26. Amends decision-register entries Q-003, Q-005
and Q-019. It re-orders priorities only; it does not delete code, requirements, inventories or
tests.

Context: the accepted vision covers three products at once: Kestra OSS parity, an enterprise-class
distribution and a governed agent mesh. The 2026-09-26 repository audit (GitHub #108) found that
delivered work and the only real consumer are concentrated on governed agent sessions. GitHub
issues #74–#97 are all session, tool-plan or prompt-cache work for the first external client. Of the
135 catalog epics, 116 are done. The 19 open epics are mainly ecosystem and production gates: plugin
packs, external secrets managers, Git sync, cloud batch runners, multi-region, performance and GA.
The Kestra inventory records 657 verified behaviors, 108 gaps and 72 intentional differences.
Expressions are AMESH-native Jinja, not Pebble. With no explicit focus, effort is spread over a
parity surface that has no consumer, while the differentiator carries the real load.

Decision:

1. **Product identity.** AMESH is a governed agent-session runtime. It provides durable, budgeted
   and auditable agent sessions with pinned capabilities, governed tool calls, checkpoints,
   evidence and restart recovery. Consumers integrate through the session API, MCP and CLI.
2. **Workflow backbone.** The durable workflow engine is the runtime backbone and remains a
   supported surface. It covers DAGs, triggers, retries, runners, PostgreSQL authority, leases and
   the pure reducer. It is maintained and hardened, but not expanded for parity's sake.
3. **Kestra parity becomes a deferred horizon.** No new work starts on the following unless a named
   consumer needs it:
   - Pebble, the Kestra compatibility façade or migration tooling
   - plugin packs EPIC-308 to EPIC-311
   - Git sync EPIC-700 and cloud batch runners EPIC-223
   - multi-region EPIC-803 and enterprise distribution EPIC-804

   Existing compatibility code, the requirement corpus, the parity matrix and their tests are
   retained and must keep passing. The clean-room policy still binds all work.
4. **Priority order for open work:**
   - a. Reliability and security of the session runtime and its deployment: #95, #99–#101, #113,
     #114 and EPIC-612.
   - b. Earned production claims for that runtime: EPIC-611 soak and load, backup/restore, Helm
     defaults in EPIC-606, and #104–#106.
   - c. Session product depth: EPIC-806 multi-agent topology, EPIC-801 agentic authoring and the
     operator UI simplification in #118–#123.
   - d. Everything else.
5. **Positioning.** The README and documentation describe AMESH first as the agent-session runtime.
   Kestra 1.3.30 is described as a pinned compatibility reference, not as the product target.

Alternatives: pursuing a Kestra-compatible orchestrator would need a plugin ecosystem, Pebble, Git
sync and migration tooling, and it has no consumer today. Keeping both targets co-equal would keep
effort spread.

Consequences: backlog records and epic states are unchanged. This ADR and the `PLAN.md` decisions
log carry the new order, and the frozen 900-requirement corpus is not rewritten. Compatibility
claims do not change, because full Kestra compatibility was never claimed. A future consumer need
can reopen any deferred item through a superseding ADR.

Revisit when a consumer requires Kestra-compatible import or plugins, or after the session runtime
passes its production qualification (EPIC-611).
