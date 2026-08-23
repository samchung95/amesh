from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from amesh.domain import OperationalBoundary, OperationalControlDecision


class OperationalControlEvaluator(Protocol):
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
    ) -> OperationalControlDecision: ...
