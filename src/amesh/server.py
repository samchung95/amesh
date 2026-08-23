from __future__ import annotations

import asyncio
from contextlib import suppress

import uvicorn

from amesh.adapters.postgres import (
    PostgresOperationalControlRepository,
    PostgresServiceRegistryRepository,
    PostgresTenantRepository,
)
from amesh.app import get_trusted_plugin_runtime
from amesh.config import get_settings
from amesh.database import create_database_engine
from amesh.domain import ServiceRole
from amesh.observability import configure_structured_logging
from amesh.service_runtime import RegisteredService


async def run_server() -> None:
    settings = get_settings()
    engine = create_database_engine(settings)
    repository = PostgresServiceRegistryRepository(
        engine,
        stale_after_seconds=settings.service_stale_after_seconds,
    )
    service = RegisteredService(repository, settings, ServiceRole.WEBSERVER)
    controls = PostgresOperationalControlRepository(engine)
    tenants = PostgresTenantRepository(engine)
    server = uvicorn.Server(
        uvicorn.Config(
            "amesh.app:app",
            host=settings.app_host,
            port=settings.app_port,
            log_config=None,
            access_log=True,
        )
    )
    stop = asyncio.Event()
    heartbeat_task: asyncio.Task[None] | None = None
    try:
        await service.register()

        async def acknowledge_controls(instance: object) -> None:
            await controls.acknowledge_active(
                tenant_ids=await tenants.list_active_for_worker_group(settings.worker_group),
                component_id=str(service.instance.instance_id),
                component_role=ServiceRole.WEBSERVER.value,
            )

        heartbeat_task = asyncio.create_task(
            service.heartbeat_server_until_draining(stop, acknowledge_controls)
        )
        serve_task = asyncio.create_task(server.serve())
        stop_task = asyncio.create_task(stop.wait())
        done, _pending = await asyncio.wait(
            {serve_task, stop_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        if stop_task in done and not serve_task.done():
            server.should_exit = True
        await serve_task
        stop_task.cancel()
        with suppress(asyncio.CancelledError):
            await stop_task
    finally:
        stop.set()
        if heartbeat_task is not None:
            await heartbeat_task
        await get_trusted_plugin_runtime().stop()
        await service.stop()
        await engine.dispose()


def main() -> None:
    settings = get_settings()
    configure_structured_logging(settings.log_level)
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
