# Priority personas and accepted initial integration pack

## Priority personas

### AI workflow developer

Needs durable model calls, structured outputs, MCP tools, agent hand-offs, budgets, evaluation, replay metadata and safe human/policy gates.

### Software engineer

Needs Git-backed workflow definitions, local debugging, APIs/SDKs, CI integration, code and container execution, tests, secrets and predictable promotion between environments.

### Platform engineer

Needs multi-tenancy, RBAC, SSO, audit, on-premises Kubernetes deployment, worker isolation, policy-as-code, observability, backup/restore, capacity controls and offline installation.

## Accepted first ten integrations

1. **HTTP/REST** task and polling trigger.
2. **Webhook** ingress and callback task.
3. **Git** repository operations.
4. **GitHub** issues, pull requests, checks, releases and webhooks.
5. **PostgreSQL** query, transaction and CDC/polling primitives.
6. **S3-compatible object storage**, including MinIO.
7. **Docker/OCI** image build/run and registry operations.
8. **Kubernetes** jobs, resources, watch triggers and logs.
9. **OpenAI-compatible model API** for chat, embeddings, structured output and tool calling without coupling the core to one provider.
10. **MCP** client and server capabilities with scoped tool allowlists.

These ten are release-scope decisions, not merely examples. Each integration still needs its own requirements, plugin contract, security model, conformance fixtures and operational documentation.

## Core runtime capabilities that are not counted as integrations

- local shell/process execution;
- Python and Node.js scripts;
- cron/schedule triggers;
- flow/subflow invocation;
- filesystem, JSON, YAML and archive utilities;
- human approval nodes;
- email/notification interfaces supplied by later plugin packs.

## Integration acceptance baseline

Each initial integration must provide, as applicable:

- typed configuration schema and generated documentation;
- secret references rather than embedded credentials;
- timeout, retry, backoff and cancellation behavior;
- idempotency or explicit duplicate-side-effect guidance;
- pagination, rate-limit and reconnect handling;
- tenant and authorization enforcement;
- redacted logs and audit events;
- local or recorded-response fixtures;
- failure classification and operator diagnostics;
- compatibility and upgrade policy;
- offline-installable plugin packaging for the on-premises reference release.
