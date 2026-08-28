# AMESH plugin workspace

Native plugin SDK and registry work begins in M3. Third-party plugins target the isolated, language-neutral protocol by default; selected trusted in-process extensions are a separately governed tier.

Initial supported SDK languages are planned to be:

- Java, for compatibility-heavy plugins and transitional migration tooling;
- Python, for AI/model integrations and data workflows;
- TypeScript, for software automation and broad SDK reach.

Kestra plugin configuration should be mechanically translated where practical. Unchanged JAR compatibility is not a baseline promise; a transitional JVM bridge is permitted only when measured migration overhead justifies its security and lifecycle cost.

See `docs/architecture/plugins.md`, `proto/plugin/v1/plugin.proto`, EPIC-300 through EPIC-313 and EPIC-704.
