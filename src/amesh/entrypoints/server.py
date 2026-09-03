from __future__ import annotations

import asyncio
import ssl
from collections.abc import Callable
from contextlib import suppress

import uvicorn

from amesh.adapters.postgres import (
    PostgresOperationalControlRepository,
    PostgresServiceRegistryRepository,
    PostgresTenantRepository,
)
from amesh.config import Settings, get_settings
from amesh.database import create_database_engine
from amesh.domain import ServiceRole
from amesh.observability import configure_observability, shutdown_observability
from amesh.service_runtime import RegisteredService


class _ExternallyStoppedServer(uvicorn.Server):
    def install_signal_handlers(self) -> None:
        pass


def build_uvicorn_config(settings: Settings) -> uvicorn.Config:
    if settings.network_inbound_tls_mode == "direct":
        certificate = settings.network_tls_certificate_file
        private_key = settings.network_tls_private_key_file
        if certificate is None or private_key is None:
            raise ValueError("direct inbound TLS requires a certificate and private key")
        client_auth = {
            "none": ssl.CERT_NONE,
            "optional": ssl.CERT_OPTIONAL,
            "required": ssl.CERT_REQUIRED,
        }[settings.network_tls_client_auth]
        return uvicorn.Config(
            "amesh.app:app",
            host=settings.app_host,
            port=settings.app_port,
            log_config=None,
            access_log=True,
            proxy_headers=False,
            ssl_certfile=certificate,
            ssl_keyfile=private_key,
            ssl_cert_reqs=client_auth,
            ssl_ca_certs=settings.network_tls_client_ca_file,
            ssl_ciphers=settings.network_tls_ciphers,
            ssl_context_factory=_modern_ssl_context(settings.network_tls_minimum_version),
        )
    return uvicorn.Config(
        "amesh.app:app",
        host=settings.app_host,
        port=settings.app_port,
        log_config=None,
        access_log=True,
        proxy_headers=False,
    )


def _modern_ssl_context(
    minimum_version: str,
) -> Callable[[uvicorn.Config, Callable[[], ssl.SSLContext]], ssl.SSLContext]:
    selected = {
        "TLSv1.2": ssl.TLSVersion.TLSv1_2,
        "TLSv1.3": ssl.TLSVersion.TLSv1_3,
    }[minimum_version]

    def configure(
        _config: uvicorn.Config,
        default_factory: Callable[[], ssl.SSLContext],
    ) -> ssl.SSLContext:
        context = default_factory()
        context.minimum_version = selected
        context.options |= ssl.OP_NO_COMPRESSION
        return context

    return configure


async def run_server(
    settings: Settings | None = None,
    *,
    stop_event: asyncio.Event | None = None,
) -> None:
    settings = settings or get_settings()
    engine = create_database_engine(settings)
    repository = PostgresServiceRegistryRepository(
        engine,
        stale_after_seconds=settings.service_stale_after_seconds,
    )
    service = RegisteredService(repository, settings, ServiceRole.WEBSERVER)
    controls = PostgresOperationalControlRepository(engine)
    tenants = PostgresTenantRepository(engine)
    server_type = _ExternallyStoppedServer if stop_event is not None else uvicorn.Server
    server = server_type(build_uvicorn_config(settings))
    stop = stop_event or asyncio.Event()
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
        await service.stop()
        await engine.dispose()


def main() -> None:
    settings = get_settings()
    configure_observability(settings)
    try:
        asyncio.run(run_server())
    finally:
        shutdown_observability()


if __name__ == "__main__":
    main()
