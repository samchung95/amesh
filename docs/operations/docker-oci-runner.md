# Docker and OCI runner

Use the Docker runner for isolated shell tasks on a local, rootless or remote Docker-compatible
Engine. The runner is disabled by default. Enable it with `DOCKER_RUNNER_ENABLED=true` and allow
`docker` in the matching runner policy.

## Task contract

```yaml
tasks:
  - id: transform
    type: core.shell
    image: alpine:3.21
    command: [sh, -c, "tr a-z A-Z < input.txt > output.txt"]
    inputFiles: {input.txt: nsfile:///input.txt}
    outputFiles: [output.txt]
    taskRunner:
      type: docker
      pullPolicy: IF_NOT_PRESENT
      platform: linux/amd64
    resources:
      cpus: 0.5
      memoryBytes: 33554432
      processes: 32
      openFiles: 128
    networkPolicy: {access: none}
    securityPolicy:
      readOnlyRootFilesystem: true
      runAsUser: 1000
      capabilityDrop: [ALL]
      noNewPrivileges: true
```

The runner resolves every accepted image to a repository digest before container creation. Tags are
rejected unless `docker_image_policy.allowTags` is true. `pullPolicy` is `NEVER`,
`IF_NOT_PRESENT` or `ALWAYS`.

Input and output workspaces cross the Engine API as validated tar archives backed by an owned named
volume. The task receives only `/workspace`; AMESH does not bind-mount its host workspace or Docker
socket into the task. Links, devices and paths that escape the workspace are rejected.

Stdout and stderr stream separately with ordered AMESH log sequence values. Results include exit
status, signal, duration, CPU, peak memory, resolved image digest, OOM status and runtime errors.
Cancellation stops the container for the configured grace period and then kills it. Containers and
workspace volumes carry AMESH ownership and fencing labels; normal cleanup and reconciliation are
idempotent.

## Engine and image policy

The default image policy accepts only `docker.io` digests and rejects tags. Configure it with JSON:

```text
DOCKER_IMAGE_POLICY={"allowedRegistries":["registry.internal.example"],"allowTags":false,"requireSignature":true,"requireVulnerabilityScan":true}
DOCKER_SIGNATURE_VERIFICATION_COMMAND=["cosign","verify","{image}"]
DOCKER_VULNERABILITY_VERIFICATION_COMMAND=["trivy","image","--exit-code","1","{image}"]
```

Verifier settings are argv arrays, not shell strings. `{image}` is replaced with the resolved digest.
A required verifier that is absent or exits nonzero rejects the attempt before a container is
created.

Set `DOCKER_RUNNER_ENDPOINT` to an Engine SDK endpoint such as a rootless Unix socket, TCP endpoint or
SSH endpoint. When it is omitted, the Docker SDK uses the standard `DOCKER_HOST` environment and local
client configuration. TLS and SSH credentials belong to the trusted AMESH runner process, not the task
environment.

Private-registry credentials are attempt-scoped runner credentials. Declare their scopes in the task
contract, map them through `runnerCredentials`, and name the mapped environment variables with
`registryUsernameVariable` and `registryPasswordVariable`. Those two values are passed only to image
pull and are removed from the task environment.

## Compose development profile

The development Compose profile mounts `/var/run/docker.sock` only into the trusted AMESH API and
executor containers so they can operate the Engine. It never forwards that socket to task containers.
On Linux set `DOCKER_GID` to the socket group ID before startup when it is not group `0`:

```bash
export DOCKER_GID="$(stat -c '%g' /var/run/docker.sock)"
docker compose up -d --build api executor scheduler
```

Treat direct Docker socket access as host-equivalent authority. For stronger separation, point AMESH
at a dedicated rootless or remote Engine and omit the Compose socket mount.

The disposable Engine qualification sets `AMESH_TEST_DOCKER=1` and exercises real container output
limits, archive security, logs, cancellation and reconciliation. It remains outside the socket-free
aggregate; its accountable repository role and next review date are recorded in the
[specialist qualification register](../how-to/run-local-verification.md#focused-gates-and-specialist-qualification).
