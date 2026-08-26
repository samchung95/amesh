# Agent-session harness workers

This directory contains language-specific workers behind AMESH's internal
`AgentSessionHarness` port. They are subordinate execution libraries, not workflow engines:
PostgreSQL and the AMESH model/tool gateways remain authoritative for durable state, credentials,
policy, effects, budgets and evidence.

- [`pi/`](pi/) — the required production worker, locked to Pi 0.84.3.

The adapter contract, authority boundary, conformance command and provenance rules are documented in
[`docs/plugin-sdk/agent-session-harness.md`](../docs/plugin-sdk/agent-session-harness.md). The
provider-free production-image probe is runnable with:

```powershell
docker build -t amesh:harness-conformance .
docker run --rm --entrypoint python amesh:harness-conformance -m amesh.harness_probe
```
