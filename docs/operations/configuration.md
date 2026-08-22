# Configuration and feature flags

AMESH validates one typed configuration snapshot before a process starts. Source precedence is fixed,
from lowest to highest:

1. checked-in model defaults;
2. ordered YAML or JSON files from `AMESH_CONFIG_FILES` and repeated `--config` arguments;
3. environment variables;
4. repeated command-line `--set NAME=VALUE` arguments.

Later configuration files override earlier files. Environment and command-line values always override
files. Unknown file or command-line names, missing files, unavailable secrets, invalid types and
contradictory production combinations stop startup with a secret-free error.

For example:

```powershell
$env:AMESH_CONFIG_FILES='C:\amesh\base.yaml;C:\amesh\site.yaml'
$env:AMESH_SECRETS_DIR='C:\amesh\secrets'
uv run --extra runtime python -m amesh.server --set LOG_LEVEL=DEBUG
```

A secret-typed setting may contain `secret://name`. AMESH reads `name` from `AMESH_SECRETS_DIR` only
after source precedence is resolved. The effective-configuration and diagnostic APIs return
`[REDACTED]`; structured messages and exception text pass through the same active-secret redactor.
Do not put secret values in YAML, command history or feature-flag descriptions.

`GET /api/v1/configuration` exposes the effective redacted snapshot, winning source, reloadability,
warnings and fingerprint to an authorized instance administrator. `POST /api/v1/configuration/reload`
fully validates a candidate and atomically accepts only changes to `LOG_LEVEL`,
`PRODUCT_TELEMETRY_ENABLED` and `PRODUCT_UPDATE_CHECKS_ENABLED`. Any restart-required change rejects
the entire reload and writes audit evidence.

Renamed settings are migrated before validation. `ADMIN_TOKEN` migrates to `AMESH_ADMIN_TOKEN`, and
`TELEMETRY_ENABLED` migrates to `PRODUCT_TELEMETRY_ENABLED`; both produce deprecation warnings without
logging their values.

## Runner policy

`runner_policies` is a restart-required ordered set of typed namespace/worker-group rules. The most
specific worker-group and namespace-prefix match wins. For example:

```yaml
runner_policies:
  - namespacePrefix: company
    defaultRunner: kubernetes
    allowedRunners: [local, kubernetes]
  - namespacePrefix: company.regulated
    workerGroup: secure
    defaultRunner: kubernetes
    allowedRunners: [kubernetes]
```

The equivalent environment value is JSON in `RUNNER_POLICIES`. Invalid duplicate scopes, duplicate
runner names, or a default runner outside `allowedRunners` stop startup. Policy is evaluated before
runner dispatch; it may select a default or reject an explicit task/API runner request.

`LOCAL_PROCESS_RUNNER_ENABLED` is restart-required. When omitted it is enabled for `TENANCY_MODE=single`
and disabled for `TENANCY_MODE=multi`. Setting it to `true` in a multi-tenant deployment is an explicit
operator assertion that every tenant allowed to select `local` is trusted to run directly on that
worker. Keep `allowedRunners: [kubernetes]` on untrusted namespace and worker-group rules.

`DOCKER_RUNNER_ENABLED` is restart-required and defaults to `false`. `DOCKER_RUNNER_ENDPOINT` selects
a local, rootless or remote Engine; when omitted, the standard Docker client environment is used.
`DOCKER_IMAGE_POLICY` configures registry allowlists, explicit tag use, signature verification and
vulnerability verification. The two verifier command settings are JSON argv arrays and fail closed
when their corresponding policy switch is enabled. See [the Docker runner guide](docker-oci-runner.md).

`KUBERNETES_RUNNER_PROFILES` is a restart-required JSON array of operator-owned cluster profiles.
Each profile can select a kubeconfig context, namespace, service account, node selector, runtime class,
workload identity and typed Job template. The most-specific namespace-prefix and worker-group match
wins; task settings cannot override profile-owned placement or identity. When omitted, the existing
`KUBERNETES_CONTEXT` and `KUBERNETES_TASK_NAMESPACE` settings provide one default profile. See the
[Kubernetes runner guide](kubernetes-runner.md).

`PLUGIN_DIRECTORIES` and `PLUGIN_REGISTRIES` are restart-required JSON arrays used to construct the
plugin catalog. `PLUGIN_INSTALL_ROOT` stores digest-verified registry and offline bundles;
`PLUGIN_REGISTRY_TIMEOUT_SECONDS` bounds registry reads. See the
[plugin discovery and resolution guide](../plugin-sdk/discovery-and-resolution.md).

## Feature flags

Boolean flags are versioned and audited in PostgreSQL. Resolution order is namespace, tenant,
instance, then the caller-provided default. The API is tenant-bounded:

- `GET /api/v1/feature-flags?namespace=...` lists only instance flags and the selected tenant/context;
- `GET /api/v1/feature-flags/{key}/evaluate` returns the value, matched scope and reason;
- `PUT /api/v1/feature-flags/{key}` creates or updates an `INSTANCE`, `TENANT` or `NAMESPACE` value;
- `GET /api/v1/configuration/diagnostics` generates a redacted bundle for only the selected tenant.

Use `expectedVersion` on updates when the caller must reject concurrent changes.

## Production baseline

Production startup rejects development authentication, the development token pepper, development
object-storage credentials without workload identity, and explicitly public exposure without trusted
TLS termination. Plugin trust defaults to `signed-only`. Product telemetry and update checks are off
by default and perform no outbound connection unless explicitly enabled by a later owning component.
