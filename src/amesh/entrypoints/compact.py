from __future__ import annotations

import asyncio
import logging
import signal
import sys
from collections.abc import Callable
from contextlib import suppress
from typing import Any

from amesh.config import Settings, get_settings
from amesh.domain import ServiceRole
from amesh.entrypoints.preflight import PreflightFailed, run_preflight
from amesh.entrypoints.role import request_self_drain, run_role
from amesh.entrypoints.server import run_server
from amesh.observability import configure_observability, shutdown_observability
from amesh.service_runtime import service_instance_name

LOGGER = logging.getLogger("amesh.compact")

_BACKGROUND_ROLES = (
    ServiceRole.EXECUTOR,
    ServiceRole.SCHEDULER,
    ServiceRole.WORKER,
    ServiceRole.INDEXER,
    ServiceRole.MAINTENANCE,
)


async def run_compact(
    settings: Settings,
    *,
    shutdown_event: asyncio.Event | None = None,
) -> None:
    report = await run_preflight(settings, check_storage=True, write_storage_probe=True)
    if not report.ready:
        raise PreflightFailed(report)

    shutdown = shutdown_event or asyncio.Event()
    restore_handlers = (
        _install_shutdown_handlers(asyncio.get_running_loop(), shutdown)
        if shutdown_event is None
        else lambda: None
    )
    stop = asyncio.Event()
    role_settings = _compact_role_settings(settings)
    tasks: dict[ServiceRole, asyncio.Task[None]] = {
        ServiceRole.WEBSERVER: asyncio.create_task(
            run_server(role_settings[ServiceRole.WEBSERVER], stop_event=stop),
            name="amesh-compact-webserver",
        )
    }
    tasks.update(
        {
            role: asyncio.create_task(
                run_role(role_settings[role], stop_event=stop),
                name=f"amesh-compact-{role.value}",
            )
            for role in _BACKGROUND_ROLES
        }
    )
    shutdown_wait = asyncio.create_task(shutdown.wait(), name="amesh-compact-shutdown")
    failure: BaseException | None = None
    try:
        done, _ = await asyncio.wait(
            {*tasks.values(), shutdown_wait},
            return_when=asyncio.FIRST_COMPLETED,
        )
        if shutdown_wait not in done:
            for task in done:
                if task.cancelled():
                    continue
                failure = task.exception()
                if failure is not None:
                    break
            shutdown.set()

        try:
            await asyncio.wait_for(
                _request_drains(role_settings),
                timeout=min(settings.compact_shutdown_grace_seconds / 2, 10),
            )
        except (TimeoutError, OSError):
            LOGGER.exception("compact role drain request did not complete")
        stop.set()
        completed, pending = await asyncio.wait(
            tasks.values(),
            timeout=settings.compact_shutdown_grace_seconds,
        )
        del completed
        for task in pending:
            task.cancel()
        await asyncio.gather(*tasks.values(), return_exceptions=True)
    finally:
        stop.set()
        shutdown_wait.cancel()
        with suppress(asyncio.CancelledError):
            await shutdown_wait
        for task in tasks.values():
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks.values(), return_exceptions=True)
        restore_handlers()
    if failure is not None:
        raise failure


def _compact_role_settings(settings: Settings) -> dict[ServiceRole, Settings]:
    base_name = service_instance_name(settings)
    selected = {
        ServiceRole.WEBSERVER: settings.model_copy(
            update={
                "service_role": ServiceRole.WEBSERVER.value,
                "service_instance_name": base_name,
            }
        )
    }
    selected.update(
        {
            role: settings.model_copy(
                update={
                    "service_role": role.value,
                    "service_instance_name": f"{base_name}-{role.value}",
                }
            )
            for role in _BACKGROUND_ROLES
        }
    )
    return selected


async def _request_drains(role_settings: dict[ServiceRole, Settings]) -> None:
    await asyncio.gather(
        *(request_self_drain(settings) for settings in role_settings.values()),
        return_exceptions=True,
    )


def _install_shutdown_handlers(
    loop: asyncio.AbstractEventLoop,
    shutdown: asyncio.Event,
) -> Callable[[], None]:
    previous: dict[signal.Signals, Any] = {}

    def request_shutdown(_signum: int, _frame: object) -> None:
        loop.call_soon_threadsafe(shutdown.set)

    for selected in (signal.SIGINT, signal.SIGTERM):
        try:
            previous[selected] = signal.getsignal(selected)
            signal.signal(selected, request_shutdown)
        except (OSError, ValueError):
            continue

    def restore() -> None:
        for selected, handler in previous.items():
            signal.signal(selected, handler)

    return restore


def main() -> None:
    settings = get_settings()
    configure_observability(settings.model_copy(update={"service_role": "compact"}))
    try:
        asyncio.run(run_compact(settings))
    except PreflightFailed as exc:
        print(exc.report.model_dump_json(by_alias=True, indent=2), file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        shutdown_observability()


if __name__ == "__main__":
    main()
