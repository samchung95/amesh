# Local process runner

Use the local runner for trusted development commands or controlled workers. User code shares the
worker host, filesystem permissions and network namespace; use the OCI or Kubernetes runner for an
untrusted tenant.

## Task contract

Argv is the default and is not parsed by a shell:

```yaml
tasks:
  - id: inspect
    type: core.shell
    command: [python, -c, "import os,sys; print(os.getcwd(), sys.stdin.read())"]
    stdin: hello
    environment: {MODE: development}
    resources:
      cpuSeconds: 10
      memoryBytes: 268435456
      fileSizeBytes: 10485760
      openFiles: 128
      processes: 32
    securityPolicy: {runAsUser: 1000}
    taskRunner: {type: local}
```

Use the native platform shell only when its parsing is intentional. Shell mode requires one command
string so the trust boundary remains visible in the flow:

```yaml
taskRunner: {type: local, shell: true}
command: ["printf 'hello\\n' | grep hello"]
```

The result contains `exitCode`, `signal`, `stdout`, `stderr` and `metrics` with `duration_seconds`,
`cpu_seconds` and `peak_memory_bytes`. Stdout entries map to `INFO`; stderr entries map to `ERROR`.
Each entry has a single observed `sequence` and UTC `occurredAt` value.

## Host environment

The runner inherits only the platform path, locale and temporary-directory variables by default.
Add named variables with `allowedHostEnvironment`, or use `inheritHostEnvironment: true` only on a
dedicated trusted worker. `runnerCredentials` remain attempt-scoped and are never added to task output.

## Platform behavior

- Linux and macOS use a new process group. Cancellation and timeout send `SIGTERM`, wait for the
  configured grace period, then send `SIGKILL`. Numeric UID and POSIX resource limits are supported;
  changing UID requires root unless the requested UID already matches the worker.
- Windows uses a new process group plus recursive process-tree termination. Argv, explicit shell,
  stdin, working directory, environment, output streaming and resource measurement are supported.
  POSIX UID and resource-limit requests are rejected before process creation.

The runner is enabled by default only in single-tenant mode. In multi-tenant mode an operator must set
`LOCAL_PROCESS_RUNNER_ENABLED=true` and still allow `local` through the matching runner policy.
