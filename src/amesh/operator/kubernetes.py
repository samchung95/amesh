from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from kubernetes import client, config, watch  # type: ignore[import-untyped]
from kubernetes.config.config_exception import ConfigException  # type: ignore[import-untyped]

from amesh.operator.model import API_GROUP, API_VERSION, OperatorSettings, ResourceDescriptor


@dataclass(frozen=True, slots=True)
class WatchEvent:
    type: str
    resource: dict[str, Any]


class KubernetesGateway:
    def __init__(self, custom_objects: Any, core: Any) -> None:
        self._custom_objects = custom_objects
        self._core = core

    @classmethod
    def from_settings(cls, settings: OperatorSettings) -> KubernetesGateway:
        if settings.kube_context:
            config.load_kube_config(context=settings.kube_context)
        else:
            try:
                config.load_incluster_config()
            except ConfigException:
                config.load_kube_config()
        return cls(client.CustomObjectsApi(), client.CoreV1Api())

    async def list_resources(
        self,
        descriptor: ResourceDescriptor,
        namespace: str,
        label_selector: str,
    ) -> tuple[dict[str, Any], ...]:
        response = await asyncio.to_thread(
            self._custom_objects.list_namespaced_custom_object,
            API_GROUP,
            API_VERSION,
            namespace,
            descriptor.plural,
            label_selector=label_selector or None,
        )
        items = response.get("items", []) if isinstance(response, dict) else []
        return tuple(dict(item) for item in items if isinstance(item, dict))

    async def watch_batch(
        self,
        descriptor: ResourceDescriptor,
        namespace: str,
        label_selector: str,
        timeout_seconds: int,
    ) -> tuple[WatchEvent, ...]:
        return await asyncio.to_thread(
            self._watch_batch,
            descriptor,
            namespace,
            label_selector,
            timeout_seconds,
        )

    def _watch_batch(
        self,
        descriptor: ResourceDescriptor,
        namespace: str,
        label_selector: str,
        timeout_seconds: int,
    ) -> tuple[WatchEvent, ...]:
        stream = watch.Watch()
        events: list[WatchEvent] = []
        for event in stream.stream(
            self._custom_objects.list_namespaced_custom_object,
            API_GROUP,
            API_VERSION,
            namespace,
            descriptor.plural,
            label_selector=label_selector or None,
            timeout_seconds=timeout_seconds,
        ):
            if not isinstance(event, dict) or not isinstance(event.get("object"), dict):
                continue
            events.append(
                WatchEvent(type=str(event.get("type", "MODIFIED")), resource=event["object"])
            )
            if len(events) >= 1_000:
                stream.stop()
        return tuple(events)

    async def patch_finalizers(
        self,
        descriptor: ResourceDescriptor,
        resource: dict[str, Any],
        finalizers: tuple[str, ...],
    ) -> None:
        metadata = _metadata(resource)
        await asyncio.to_thread(
            self._custom_objects.patch_namespaced_custom_object,
            API_GROUP,
            API_VERSION,
            str(metadata["namespace"]),
            descriptor.plural,
            str(metadata["name"]),
            {"metadata": {"finalizers": list(finalizers)}},
        )

    async def patch_status(
        self,
        descriptor: ResourceDescriptor,
        resource: dict[str, Any],
        status: dict[str, Any],
    ) -> None:
        metadata = _metadata(resource)
        await asyncio.to_thread(
            self._custom_objects.patch_namespaced_custom_object_status,
            API_GROUP,
            API_VERSION,
            str(metadata["namespace"]),
            descriptor.plural,
            str(metadata["name"]),
            {"status": status},
        )

    async def read_secret(self, namespace: str, name: str, key: str) -> str:
        secret = await asyncio.to_thread(self._core.read_namespaced_secret, name, namespace)
        data = getattr(secret, "data", None)
        if not isinstance(data, dict) or key not in data:
            raise ValueError(f"Secret {namespace}/{name} does not contain key {key}")
        raw = data[key]
        if not isinstance(raw, str):
            raise ValueError(f"Secret {namespace}/{name} key {key} is not encoded text")
        try:
            return base64.b64decode(raw, validate=True).decode()
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError(f"Secret {namespace}/{name} key {key} is not valid UTF-8") from exc

    async def emit_event(
        self,
        resource: dict[str, Any],
        *,
        event_type: str,
        reason: str,
        message: str,
    ) -> None:
        metadata = _metadata(resource)
        namespace = str(metadata["namespace"])
        now = datetime.now(UTC)
        body = client.CoreV1Event(
            metadata=client.V1ObjectMeta(generate_name=f"{metadata['name']}-", namespace=namespace),
            involved_object=client.V1ObjectReference(
                api_version=str(resource.get("apiVersion", f"{API_GROUP}/{API_VERSION}")),
                kind=str(resource.get("kind", "AmeshResource")),
                name=str(metadata["name"]),
                namespace=namespace,
                uid=str(metadata.get("uid", "")),
                resource_version=str(metadata.get("resourceVersion", "")),
            ),
            reason=reason,
            message=message[:1_024],
            type=event_type,
            source=client.V1EventSource(component="amesh-operator"),
            first_timestamp=now,
            last_timestamp=now,
            count=1,
        )
        await asyncio.to_thread(self._core.create_namespaced_event, namespace, body)


def _metadata(resource: dict[str, Any]) -> dict[str, Any]:
    value = resource.get("metadata")
    if not isinstance(value, dict):
        raise ValueError("custom resource metadata is missing")
    if not value.get("name") or not value.get("namespace"):
        raise ValueError("custom resource metadata requires name and namespace")
    return value
