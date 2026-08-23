from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from typing import Any

from amesh.operator.client import AmeshApiClient
from amesh.operator.kubernetes import KubernetesGateway, WatchEvent
from amesh.operator.model import RESOURCE_DESCRIPTORS, OperatorSettings, ResourceDescriptor
from amesh.operator.reconciler import AmeshResourceReconciler

LOGGER = logging.getLogger("amesh.operator")


class OperatorRuntime:
    def __init__(
        self,
        settings: OperatorSettings,
        kubernetes: KubernetesGateway,
        api: AmeshApiClient,
    ) -> None:
        self._settings = settings
        self._kubernetes = kubernetes
        self._api = api
        self._reconciler = AmeshResourceReconciler(settings, kubernetes, api)

    async def run_once(self) -> int:
        resources = 0
        for descriptor in RESOURCE_DESCRIPTORS:
            for namespace in self._settings.watch_namespaces:
                items = await self._kubernetes.list_resources(
                    descriptor,
                    namespace,
                    self._settings.label_selector,
                )
                resources += len(items)
                for resource in items:
                    await self._reconcile_and_requeue(descriptor, resource)
        return resources

    async def run_forever(self, stop_event: asyncio.Event | None = None) -> None:
        stop = stop_event or asyncio.Event()
        await self.run_once()
        watchers = [
            asyncio.create_task(self._watch(descriptor, namespace, stop))
            for descriptor in RESOURCE_DESCRIPTORS
            for namespace in self._settings.watch_namespaces
        ]
        resync = asyncio.create_task(self._resync(stop))
        try:
            await stop.wait()
        finally:
            for task in (*watchers, resync):
                task.cancel()
            for task in (*watchers, resync):
                with suppress(asyncio.CancelledError):
                    await task

    async def close(self) -> None:
        await self._api.close()

    async def _watch(
        self,
        descriptor: ResourceDescriptor,
        namespace: str,
        stop: asyncio.Event,
    ) -> None:
        while not stop.is_set():
            try:
                events = await self._kubernetes.watch_batch(
                    descriptor,
                    namespace,
                    self._settings.label_selector,
                    self._settings.watch_timeout_seconds,
                )
                for event in events:
                    if _requires_reconcile(event):
                        await self._reconcile_and_requeue(descriptor, event.resource)
            except asyncio.CancelledError:
                raise
            except Exception:
                LOGGER.exception(
                    "operator watch failed",
                    extra={"kind": descriptor.kind, "namespace": namespace},
                )
                await _wait_or_stop(stop, self._settings.retry_initial_seconds)

    async def _resync(self, stop: asyncio.Event) -> None:
        while not stop.is_set():
            await _wait_or_stop(stop, self._settings.resync_seconds)
            if stop.is_set():
                return
            try:
                await self.run_once()
            except Exception:
                LOGGER.exception("operator periodic resync failed")

    async def _reconcile_and_requeue(
        self,
        descriptor: ResourceDescriptor,
        resource: dict[str, Any],
    ) -> None:
        result = await self._reconciler.reconcile(descriptor, resource)
        if result.requeue_after_seconds is not None:
            await asyncio.sleep(result.requeue_after_seconds)
            await self._reconciler.reconcile(descriptor, resource)


async def _wait_or_stop(stop: asyncio.Event, seconds: float) -> None:
    try:
        await asyncio.wait_for(stop.wait(), timeout=seconds)
    except TimeoutError:
        return


def _requires_reconcile(event: WatchEvent) -> bool:
    if event.type in {"ADDED", "DELETED"}:
        return True
    metadata = event.resource.get("metadata")
    status = event.resource.get("status")
    if not isinstance(metadata, dict) or not isinstance(status, dict):
        return True
    if metadata.get("deletionTimestamp"):
        return True
    return metadata.get("generation") != status.get("observedGeneration")
