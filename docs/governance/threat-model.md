# Threat model

## Protected assets

Workflow definitions, secrets, namespace files, execution inputs/outputs, artifacts, logs, identity data,
audit evidence, plugin packages, signing keys, service credentials and user infrastructure.

## Adversaries

- unauthenticated internet attacker;
- authenticated user exceeding permissions;
- malicious tenant;
- compromised browser session or API token;
- malicious workflow author;
- malicious or vulnerable plugin;
- hostile task workload;
- compromised worker or edge node;
- supply-chain attacker;
- operator mistake;
- external service returning malicious content;
- prompt injection through AI-connected workflows.

## Principal threat scenarios

1. Cross-tenant query or object-path leakage.
2. SSRF from HTTP tasks or plugins into metadata/control networks.
3. Secret exfiltration through logs, outputs, errors, metrics, traces or AI prompts.
4. Container escape or host socket abuse.
5. Plugin compromise of scheduler/executor/webserver.
6. Stale worker commits after lease transfer.
7. Trigger replay causing duplicate external effects.
8. Queue poison message blocking a partition.
9. Flow expression denial of service.
10. Archive/path traversal through namespace or task files.
11. Search index returning unauthorized or deleted documents.
12. Compromised release or plugin registry artifact.
13. SSO account-linking or SCIM deprovisioning failure.
14. Audit deletion or tampering.
15. AI assistant taking high-impact actions without approval.

## Required mitigations

Tenant-scoped repositories, capability credentials, egress policy, bounded parsers, isolated runners and
plugins, fencing, idempotency, durable inbox/outbox, secret redaction canaries, signed artifacts, audit
evidence, step-up controls and adversarial testing. Residual external-side-effect ambiguity must be shown
rather than hidden.
