# Test a plugin contract locally

The Python harness validates identity, protocol compatibility, capability grants and configuration
before calling a transport-neutral async handler. `PluginFixture` provides the same expected-output or
expected-error contract for all eight extension types.

```python
import asyncio

from amesh.plugin_sdk import (
    PluginContractHarness,
    PluginFixture,
    PluginOperation,
    PluginResponse,
)


async def execute(request):
    return PluginResponse(
        invocationId=request.session.invocation_id,
        output={"echo": request.configuration["message"]},
    )


harness = PluginContractHarness(
    manifest,
    {("task.echo", PluginOperation.EXECUTE): execute},
    grant=capability_grant,
)
result = asyncio.run(
    harness.run_fixture(
        PluginFixture(
            name="echo",
            entryPoint="task.echo",
            operation="execute",
            configuration={"message": "hello"},
            expectedOutput={"echo": "hello"},
        )
    )
)
assert result.passed, result.diagnostic
```

Use `validate_configuration` when only schema diagnostics are needed. It returns stable error codes,
phase, JSON path, remediation hint and retryability rather than implementation exception text.
`PluginContractError` lets a handler return the same structured runtime errors deliberately; an
unexpected exception becomes `plugin.runtime.unhandled` with only its exception type in details.

The repository conformance suite runs a fixture for task, trigger, condition, runner, storage, secret,
expression and notification entry points:

```powershell
uv run pytest tests/plugin_sdk/test_contract.py -q
```

Polling/realtime lifecycle, explainable condition results, notification delivery policies and the
connector fault emulators are covered by the
[extension contract guide](extension-contracts.md).

For the one-command release checks, resilience fixtures, quality levels, compatibility matrix and
public CI evidence format, use the [plugin certification guide](certification.md).
