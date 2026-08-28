from __future__ import annotations

import argparse
import asyncio
import logging
import signal
from contextlib import suppress

from prometheus_client import start_http_server

from amesh.operator.client import AmeshApiClient
from amesh.operator.kubernetes import KubernetesGateway
from amesh.operator.model import OperatorSettings
from amesh.operator.runtime import OperatorRuntime


async def _run(settings: OperatorSettings, *, once: bool) -> None:
    gateway = KubernetesGateway.from_settings(settings)
    api = AmeshApiClient()
    runtime = OperatorRuntime(settings, gateway, api)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for selected in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(selected, stop.set)
    try:
        if once:
            await runtime.run_once()
        else:
            await runtime.run_forever(stop)
    finally:
        await runtime.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile AMESH Kubernetes custom resources")
    parser.add_argument("--once", action="store_true", help="reconcile the current list and exit")
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="validate operator configuration without contacting Kubernetes",
    )
    args = parser.parse_args()
    settings = OperatorSettings.from_environment()
    if args.check_config:
        return
    logging.basicConfig(level=logging.INFO)
    start_http_server(settings.metrics_port)
    asyncio.run(_run(settings, once=args.once))


if __name__ == "__main__":
    main()
