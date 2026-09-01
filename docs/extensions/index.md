# Extend AMESH

Extensions add capabilities without giving workflow YAML or an agent unrestricted access to the host.
Choose the narrowest contract that matches what you are adding.

| Extension | Adds | Start here |
| --- | --- | --- |
| Plugin | Versioned resources and process entry points | [Plugin architecture](../architecture/plugins.md) |
| Workflow task/tool provider | A typed, policy-governed action | [Implement a ToolProvider](../how-to/implement-tool-provider.md) |
| MCP connection | Imported MCP tools pinned into an agent envelope | [Register MCP](../how-to/register-mcp-connection.md) |
| Model-provider adapter | A model route with normalized usage, errors and continuation | [Add a model provider](../how-to/add-model-provider.md) |
| Session harness | The bounded multi-turn agent loop behind the stable AMESH port | [Harness contract](../plugin-sdk/agent-session-harness.md) |

## Plugin path

1. Define the [manifest](../plugin-sdk/manifest.md) and exact compatibility ranges.
2. Use [discovery and resolution](../plugin-sdk/discovery-and-resolution.md) to produce the effective
   catalog.
3. Implement the supported [extension contracts](../plugin-sdk/extension-contracts.md).
4. Run the [plugin test kit](../plugin-sdk/testing.md) and isolation checks.
5. Deploy through the appropriate [isolated runtime](../plugin-sdk/isolated-runtime.md) or explicitly
   trusted in-process boundary.

Plugin descriptions are discoverability metadata, not authority. AMESH still resolves tenant policy,
permissions, credentials, network policy, approvals and exact version pins before dispatch.

## Tool and MCP responsibility

AMESH stores the high-level callable schema, description, pin and policy decision. A remote MCP server
or client-side extension owns its concrete privileged implementation—for example, browser automation.
It should expose only safe high-level operations, validate arguments locally and return a bounded
result. Registering the tool does not transfer browser credentials or raw automation commands into
AMESH.

Read [Extension concepts](../concepts/extensions.md) for the boundaries between prompts, skills,
plugins, tools, MCP and harnesses.
