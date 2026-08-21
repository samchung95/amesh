from __future__ import annotations

import asyncio
import os
import socket
from contextlib import suppress
from typing import Any

from sqlalchemy.exc import DBAPIError

from amesh import __version__
from amesh.config import Settings
from amesh.domain import (
    ServiceInstance,
    ServiceRegistration,
    ServiceRole,
    ServiceState,
    new_runtime_id,
)
from amesh.ports import ServiceFenceError, ServiceRegistryRepository


def service_instance_name(settings: Settings) -> str:
    return settings.service_instance_name or os.getenv("HOSTNAME") or socket.gethostname()


class RegisteredService:
    def __init__(
        self,
        repository: ServiceRegistryRepository,
        settings: Settings,
        role: ServiceRole,
    ) -> None:
        self._repository = repository
        self._settings = settings
        self._registration = ServiceRegistration(
            id=new_runtime_id(),
            role=role,
            instanceName=service_instance_name(settings),
            version=__version__,
            failureZone=settings.service_failure_zone,
            labels={"coordination": "postgresql"},
        )
        self._instance: ServiceInstance | None = None

    @property
    def instance(self) -> ServiceInstance:
        if self._instance is None:
            raise RuntimeError("service has not registered")
        return self._instance

    async def register(self) -> ServiceInstance:
        self._instance = await self._repository.register(self._registration)
        return self._instance

    async def heartbeat(
        self,
        *,
        ownership: dict[str, Any] | None = None,
        partitions: dict[str, Any] | None = None,
        dependencies: dict[str, str] | None = None,
    ) -> ServiceInstance:
        current = self.instance
        self._instance = await self._repository.heartbeat(
            current.instance_id,
            current.generation,
            ownership=ownership,
            partitions=partitions,
            dependencies=dependencies,
        )
        return self._instance

    async def stop(self) -> None:
        if self._instance is None or self._instance.state is ServiceState.STOPPED:
            return
        try:
            self._instance = await self._repository.stop(
                self._instance.instance_id,
                self._instance.generation,
            )
        except ServiceFenceError:
            self._instance = None

    async def heartbeat_server_until_draining(self, stop: asyncio.Event) -> None:
        while not stop.is_set():
            try:
                current = await self.heartbeat(
                    ownership={"http": "serving"},
                    partitions={"strategy": "stateless-load-balancing"},
                    dependencies={"postgresql": "READY"},
                )
            except (DBAPIError, OSError):
                current = None
            except ServiceFenceError:
                stop.set()
                return
            if current is not None and current.state is ServiceState.DRAINING:
                stop.set()
                return
            with suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), self._settings.service_heartbeat_seconds)
