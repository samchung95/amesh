# Current progress

- Current branch: `fix/epic-838-api-decomposition`.
- Active work: EPIC-838 milestone 5 / GitHub issue #48 is implemented and qualified for
  publication. API import is inert, application instances own independent lazy providers and MCP
  lifecycles, and feature routers are split without route-order or OpenAPI drift.
- Completed immediately before this work: EPIC-838 milestone 4 / GitHub issue #47 and pull request
  #58 made restricted PostgreSQL role assumptions fail closed and qualified tenant paths.
- Next bounded work: EPIC-838 milestone 6 / GitHub issue #49, decomposing executor
  responsibilities without changing durable transaction, fencing, identity or retry behavior.
- Verification command: `make verify-local-all` on POSIX or
  `.\scripts\verify-local.ps1 -Suite all` on PowerShell. The local pre-push hook runs the same
  Docker-local gate.
- Historical development entries are archived in
  [`docs/reviews/progress-archive.md`](docs/reviews/progress-archive.md).
