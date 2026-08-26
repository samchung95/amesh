# AMESH agent-session adapter template

Copy this directory when evaluating a different harness. Keep the adapter isolated from the durable
engine and implement only the `AgentSessionHarness` port.

```python
from amesh.ports import (
    AgentSessionHarnessRequest,
    AgentSessionHarnessResult,
    AgentSessionModelGateway,
)


class ExampleAgentSessionHarness:
    async def next_action(
        self,
        request: AgentSessionHarnessRequest,
        *,
        model_gateway: AgentSessionModelGateway,
    ) -> AgentSessionHarnessResult:
        # Pass request.model_call unchanged to model_gateway.invoke(...).
        # Return the model output and exact adapter provenance.
        raise NotImplementedError
```

An implementation must not receive provider credential values, call a provider or MCP server
directly, execute tools, write workflow/session state or choose a different route, model, budget,
continuation or invocation key. AMESH performs those operations and remains authoritative.

After registering the adapter and wiring it into the conformance runner, run the same provider-free
kit (replace `pi` with the registered adapter key):

```powershell
uv run python scripts/run_agent_harness_conformance.py --adapter pi --output .artifacts/harness-report.json
```

Add a registry entry only after the kit and failure-injection checks pass. Unknown or unavailable
adapters must fail closed. Keep the adapter's exact package lock, integrity and license evidence with
the implementation. Do not add DSH or Goose as production dependencies as part of this template.
