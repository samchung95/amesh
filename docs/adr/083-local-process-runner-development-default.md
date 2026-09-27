# ADR-083: Default local-process execution to single-tenant development only

Status: accepted.

Context: The local-process runner executes workflow commands directly on the worker host. Before
GitHub #112, an unset `LOCAL_PROCESS_RUNNER_ENABLED` value enabled that runner for every
`TENANCY_MODE=single` deployment, including production-like self-hosted profiles. Shell mode also
kept one native shell command string for compatibility, which means expression-rendered values can
become command syntax when operators place untrusted data in the string.

Decision:

- An unset `LOCAL_PROCESS_RUNNER_ENABLED` enables local-process execution only when
  `TENANCY_MODE=single` and `APP_ENV=development`. Multi-tenant and all non-development
  environments default it off.
- Production or staging deployments that intentionally run trusted local-process work must set
  `LOCAL_PROCESS_RUNNER_ENABLED=true` explicitly and still allow `local` in runner policy. Checked-in
  Compose profiles that use `EXECUTION_RUNNER_MODE=local` carry that explicit setting on the roles
  that perform admission or execution.
- Shell mode remains available for trusted compatibility cases, but documentation treats rendering
  untrusted inputs, expression results or task outputs into shell command strings as command injection
  risk and recommends argv mode.

Alternatives: Keeping the single-tenant default would preserve convenience but leave production-like
shared deployments one omitted environment variable away from host execution. Rejecting all
expression output in shell strings would be safer but needs a precise language-level design so it does
not break existing trusted command composition or miss equivalent interpolation paths.

Consequences: Development Compose remains convenient through explicit opt-in, and self-hosted
profiles are auditable about host-process execution. Existing deployments that already set
`LOCAL_PROCESS_RUNNER_ENABLED` keep their behavior. Production single-tenant deployments that relied
on the old implicit default must add `LOCAL_PROCESS_RUNNER_ENABLED=true` or select an isolated runner.
