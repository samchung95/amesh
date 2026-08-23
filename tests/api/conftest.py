from __future__ import annotations

from collections.abc import Iterator, Sequence

import pytest

from amesh.app import app, get_flow_test_repository, get_operational_control_repository
from amesh.domain import (
    OperationalBoundary,
    OperationalControlDecision,
    RunningWorkPolicy,
)


class _NoOperationalControls:
    async def evaluate(
        self,
        boundary: OperationalBoundary,
        *,
        tenant_id: str,
        namespace: str | None = None,
        flow_id: str | None = None,
        plugin_ids: Sequence[str] = (),
        runner_ids: Sequence[str] = (),
        component_id: str | None = None,
        component_role: str | None = None,
    ) -> OperationalControlDecision:
        del tenant_id, namespace, flow_id, plugin_ids, runner_ids, component_id, component_role
        return OperationalControlDecision(
            blocked=False,
            boundary=boundary,
            runningWorkPolicy=RunningWorkPolicy.CONTINUE,
        )


class _NoFlowTestGate:
    async def get_gate(self, namespace: str, *, tenant_id: str) -> None:
        del namespace, tenant_id
        return None


@pytest.fixture(autouse=True)
def disable_operational_controls_by_default() -> None:
    repository = _NoOperationalControls()

    def override() -> _NoOperationalControls:
        return repository

    app.dependency_overrides[get_operational_control_repository] = override
    yield
    if app.dependency_overrides.get(get_operational_control_repository) is override:
        app.dependency_overrides.pop(get_operational_control_repository, None)


@pytest.fixture(autouse=True)
def disable_flow_test_gate_by_default() -> Iterator[None]:
    repository = _NoFlowTestGate()

    def override() -> _NoFlowTestGate:
        return repository

    app.dependency_overrides[get_flow_test_repository] = override
    yield
    if app.dependency_overrides.get(get_flow_test_repository) is override:
        app.dependency_overrides.pop(get_flow_test_repository, None)
