# Product vision

AMESH — Agent Mesh — is a durable workflow and multi-agent orchestration platform that users can operate entirely from public source code. It targets the practical capability surface expected from a Kestra-class orchestrator while making governance, high availability, plugin isolation, compatibility tooling and administration available in one AGPL distribution.

## Product promise

A workflow or agent mesh accepted by AMESH has durable, inspectable and policy-governed state. It survives ordinary component failure, can be controlled through compatible and native interfaces, and executes untrusted work only through explicit isolation boundaries. Operators can understand why work ran, did not run, retried, waited, handed off, exceeded a budget, failed or was denied.

## Priority users

- AI workflow developers building durable multi-agent systems;
- software engineers orchestrating code, services and delivery workflows;
- platform engineers operating secure shared automation infrastructure.

## Non-goals for the initial programme

- Reproducing Kestra branding, visual design, prose or source implementation.
- Claiming exactly-once arbitrary external side effects.
- Treating generated AI code or model output as trusted without independent evidence.
- Shipping hundreds of thin integrations before the engine, runner and SDK contracts are stable.
- Making search, dashboards, notifications or Kubernetes authoritative for workflow state.
- Supporting multiple authoritative relational databases or an alternate internal message broker.
- Loading arbitrary third-party plugin code into the control plane by default.
