from __future__ import annotations

from typing import Protocol

from amesh.domain import (
    FlowTestDefinition,
    FlowTestDefinitionCreateRequest,
    FlowTestQualityGate,
    FlowTestQualityGateUpdate,
    FlowTestRunResult,
)


class FlowTestVersionConflict(RuntimeError):
    """Raised when a flow-test or gate update uses a stale resource version."""


class FlowTestRepository(Protocol):
    async def save_definition(
        self,
        namespace: str,
        flow_id: str,
        request: FlowTestDefinitionCreateRequest,
        *,
        tenant_id: str,
        flow_semantic_hash: str,
        plugin_set_hash: str,
        actor_id: str,
    ) -> FlowTestDefinition: ...

    async def list_definitions(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> tuple[FlowTestDefinition, ...]: ...

    async def delete_definition(
        self,
        namespace: str,
        flow_id: str,
        test_id: str,
        *,
        tenant_id: str,
        expected_version: int,
        actor_id: str,
    ) -> None: ...

    async def record_run(self, result: FlowTestRunResult) -> FlowTestRunResult: ...

    async def list_runs(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
        limit: int = 50,
    ) -> tuple[FlowTestRunResult, ...]: ...

    async def get_gate(
        self,
        namespace: str,
        *,
        tenant_id: str,
    ) -> FlowTestQualityGate | None: ...

    async def upsert_gate(
        self,
        namespace: str,
        request: FlowTestQualityGateUpdate,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> FlowTestQualityGate: ...
