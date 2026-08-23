from __future__ import annotations

from collections.abc import Sequence

import pytest

from amesh.app import app, get_operational_control_repository
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


@pytest.fixture(autouse=True)
def disable_operational_controls_by_default() -> None:
    repository = _NoOperationalControls()

    def override() -> _NoOperationalControls:
        return repository

    app.dependency_overrides[get_operational_control_repository] = override
    yield
    if app.dependency_overrides.get(get_operational_control_repository) is override:
        app.dependency_overrides.pop(get_operational_control_repository, None)
