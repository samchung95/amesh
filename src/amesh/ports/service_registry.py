from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from amesh.domain.service_topology import (
    ServiceInstance,
    ServiceRegistration,
    ServiceTopology,
)


class ServiceFenceError(RuntimeError):
    """Raised when a replaced or stale service incarnation attempts a mutation."""


class ServiceVersionSkewError(RuntimeError):
    """Raised before an unsafe service version can join the runtime topology."""


class ServiceRegistryRepository(Protocol):
    async def register(self, registration: ServiceRegistration) -> ServiceInstance: ...

    async def heartbeat(
        self,
        instance_id: UUID,
        generation: int,
        *,
        ownership: dict[str, Any] | None = None,
        partitions: dict[str, Any] | None = None,
        dependencies: dict[str, str] | None = None,
        ready: bool | None = True,
        failure: str | None = None,
    ) -> ServiceInstance: ...

    async def request_drain(
        self,
        instance_id: UUID,
        *,
        expected_version: int,
        actor_id: str,
        reason: str,
    ) -> ServiceInstance: ...

    async def stop(self, instance_id: UUID, generation: int) -> ServiceInstance: ...

    async def get(self, instance_id: UUID) -> ServiceInstance: ...

    async def topology(self) -> ServiceTopology: ...
