# Implement an isolated ToolProvider

Implement a provider when a tool must be supplied by MCP or an installable
plugin while keeping policy and recovery identical.

1. Create a `ToolProviderRef` with `kind`, stable `key` and immutable `revision`.
2. Return `ToolDescriptor` values from `discover()`. Keep schemas Draft 2020-12,
   declare the impact and list only the secrets, egress and filesystem roots the
   tool needs.
3. Bind `IsolatedPluginToolProvider` to the existing isolated JSON-RPC runtime.
   Its `invoke` callback must cross the child-process RPC boundary; do not load
   plugin code in-process.
4. Route calls through `GovernedToolInvoker` and a durable
   `ToolInvocationJournal`. Do not call a provider directly from an agent task.
5. Run the provider-neutral tests, including schema rejection, timeout/cancel,
   redaction and restart ambiguity. Pin the resulting provider revision and
   schema digest in the agent definition.
