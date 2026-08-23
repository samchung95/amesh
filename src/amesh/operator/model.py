from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

API_GROUP = "platform.amesh.io"
API_VERSION = "v1alpha1"
FINALIZER = "platform.amesh.io/finalizer"

ReadMode = Literal["direct", "collection", "raw"]
PayloadMode = Literal["json", "flow", "file"]


@dataclass(frozen=True, slots=True)
class SecretReference:
    namespace: str
    name: str
    key: str


@dataclass(frozen=True, slots=True)
class OperatorTarget:
    tenant: str
    endpoint: str
    credential: SecretReference


@dataclass(frozen=True, slots=True)
class OperatorSettings:
    watch_namespaces: tuple[str, ...]
    targets: tuple[OperatorTarget, ...]
    kube_context: str | None = None
    label_selector: str = ""
    resync_seconds: float = 60.0
    watch_timeout_seconds: int = 30
    retry_initial_seconds: float = 2.0
    retry_max_seconds: float = 120.0
    metrics_port: int = 9090

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> OperatorSettings:
        values = environment or os.environ
        raw_namespaces = json.loads(values.get("AMESH_OPERATOR_WATCH_NAMESPACES", "[]"))
        raw_targets = json.loads(values.get("AMESH_OPERATOR_TARGETS", "[]"))
        if not isinstance(raw_namespaces, list) or not raw_namespaces:
            raise ValueError("AMESH_OPERATOR_WATCH_NAMESPACES must be a non-empty JSON array")
        if not isinstance(raw_targets, list) or not raw_targets:
            raise ValueError("AMESH_OPERATOR_TARGETS must be a non-empty JSON array")
        namespaces = tuple(_required_string(item, "watch namespace") for item in raw_namespaces)
        targets = tuple(_target(item) for item in raw_targets)
        if len({target.tenant for target in targets}) != len(targets):
            raise ValueError("AMESH_OPERATOR_TARGETS must contain unique tenant values")
        return cls(
            watch_namespaces=namespaces,
            targets=targets,
            kube_context=values.get("AMESH_OPERATOR_KUBE_CONTEXT") or None,
            label_selector=values.get("AMESH_OPERATOR_LABEL_SELECTOR", ""),
            resync_seconds=_positive_float(values, "AMESH_OPERATOR_RESYNC_SECONDS", 60.0),
            watch_timeout_seconds=_positive_int(values, "AMESH_OPERATOR_WATCH_TIMEOUT_SECONDS", 30),
            retry_initial_seconds=_positive_float(
                values, "AMESH_OPERATOR_RETRY_INITIAL_SECONDS", 2.0
            ),
            retry_max_seconds=_positive_float(values, "AMESH_OPERATOR_RETRY_MAX_SECONDS", 120.0),
            metrics_port=_positive_int(values, "AMESH_OPERATOR_METRICS_PORT", 9090),
        )

    def target(self, tenant: str) -> OperatorTarget:
        for target in self.targets:
            if target.tenant == tenant:
                return target
        raise ValueError(f"tenant {tenant!r} is outside this operator credential scope")


@dataclass(frozen=True, slots=True)
class ResourceDescriptor:
    kind: str
    plural: str
    platform_kind: str
    namespaced: bool
    create_method: str
    create_path: str
    update_method: str
    update_path: str
    read_path: str
    delete_method: str = ""
    delete_path: str = ""
    read_mode: ReadMode = "direct"
    read_collection_field: str = ""
    read_match_field: str = ""
    read_document_field: str = ""
    server_id_field: str = ""
    revision_field: str = ""
    revision_header: str = ""
    payload_mode: PayloadMode = "json"
    replace_on_change: bool = False
    server_managed_defaults: tuple[str, ...] = ()
    comparison_defaults: tuple[tuple[str, object], ...] = ()

    @property
    def supports_delete(self) -> bool:
        return bool(self.delete_method and self.delete_path)


RESOURCE_DESCRIPTORS: tuple[ResourceDescriptor, ...] = (
    ResourceDescriptor(
        kind="AmeshFlow",
        plural="ameshflows",
        platform_kind="flow",
        namespaced=True,
        create_method="PUT",
        create_path="/api/v1/flows",
        update_method="PUT",
        update_path="/api/v1/flows",
        read_path="/api/v1/flows/{namespace}/{key}/document",
        read_document_field="document",
        delete_method="DELETE",
        delete_path="/api/v1/flows/{namespace}/{key}/revisions/{revision}",
        revision_field="revision",
        payload_mode="flow",
        server_managed_defaults=("revision", "etag", "semanticHash"),
    ),
    ResourceDescriptor(
        kind="AmeshNamespace",
        plural="ameshnamespaces",
        platform_kind="namespace",
        namespaced=True,
        create_method="POST",
        create_path="/api/v1/namespaces/{namespace}/resource-bundle",
        update_method="POST",
        update_path="/api/v1/namespaces/{namespace}/resource-bundle",
        read_path="/api/v1/namespaces/{namespace}/resource-bundle",
        server_managed_defaults=("exportedAt", "checksumSha256"),
    ),
    ResourceDescriptor(
        kind="AmeshFile",
        plural="ameshfiles",
        platform_kind="file",
        namespaced=True,
        create_method="PUT",
        create_path="/api/v1/namespaces/{namespace}/files/{key}",
        update_method="PUT",
        update_path="/api/v1/namespaces/{namespace}/files/{key}",
        read_path="/api/v1/namespaces/{namespace}/files/{key}",
        delete_method="DELETE",
        delete_path="/api/v1/namespaces/{namespace}/files/{key}",
        read_mode="raw",
        revision_header="X-Amesh-File-Version",
        payload_mode="file",
    ),
    ResourceDescriptor(
        kind="AmeshKeyValue",
        plural="ameshkeyvalues",
        platform_kind="key_value",
        namespaced=True,
        create_method="PUT",
        create_path="/api/v1/namespaces/{namespace}/key-values/{key}",
        update_method="PUT",
        update_path="/api/v1/namespaces/{namespace}/key-values/{key}",
        read_path="/api/v1/namespaces/{namespace}/key-values/{key}",
        delete_method="DELETE",
        delete_path="/api/v1/namespaces/{namespace}/key-values/{key}",
        revision_field="resourceVersion",
        server_managed_defaults=(
            "namespace",
            "key",
            "resourceVersion",
            "createdAt",
            "updatedAt",
        ),
        comparison_defaults=(("expiresAt", None), ("metadata", {})),
    ),
    ResourceDescriptor(
        kind="AmeshDashboard",
        plural="ameshdashboards",
        platform_kind="dashboard",
        namespaced=False,
        create_method="PUT",
        create_path="/api/v1/dashboards/{key}",
        update_method="PUT",
        update_path="/api/v1/dashboards/{key}",
        read_path="/api/v1/dashboards/{key}",
        delete_method="DELETE",
        delete_path="/api/v1/dashboards/{key}",
        revision_field="version",
        server_managed_defaults=("id", "version", "createdAt", "updatedAt"),
    ),
    ResourceDescriptor(
        kind="AmeshApp",
        plural="ameshapps",
        platform_kind="app",
        namespaced=True,
        create_method="PUT",
        create_path="/api/v1/apps/{namespace}/{key}",
        update_method="PUT",
        update_path="/api/v1/apps/{namespace}/{key}",
        read_path="/api/v1/apps/{namespace}/{key}",
        revision_field="revision",
        server_managed_defaults=("namespace", "id", "revision", "createdAt", "updatedAt"),
    ),
    ResourceDescriptor(
        kind="AmeshRole",
        plural="ameshroles",
        platform_kind="role",
        namespaced=False,
        create_method="PUT",
        create_path="/api/v1/admin/roles/{key}",
        update_method="PUT",
        update_path="/api/v1/admin/roles/{key}",
        read_path="/api/v1/admin/roles",
        read_mode="collection",
        read_match_field="name",
        server_managed_defaults=("built_in",),
    ),
    ResourceDescriptor(
        kind="AmeshBinding",
        plural="ameshbindings",
        platform_kind="binding",
        namespaced=False,
        create_method="POST",
        create_path="/api/v1/admin/bindings",
        update_method="POST",
        update_path="/api/v1/admin/bindings",
        read_path="/api/v1/admin/bindings",
        delete_method="DELETE",
        delete_path="/api/v1/admin/bindings/{server_id}",
        read_mode="collection",
        read_match_field="id",
        server_id_field="id",
        replace_on_change=True,
    ),
    ResourceDescriptor(
        kind="AmeshPluginPolicy",
        plural="ameshpluginpolicies",
        platform_kind="plugin_policy",
        namespaced=True,
        create_method="POST",
        create_path="/api/v1/plugin-policy/rules",
        update_method="PUT",
        update_path="/api/v1/plugin-policy/rules/{server_id}",
        read_path="/api/v1/plugin-policy/rules/{server_id}",
        delete_method="DELETE",
        delete_path="/api/v1/plugin-policy/rules/{server_id}",
        server_id_field="id",
        server_managed_defaults=(
            "id",
            "tenantId",
            "createdAt",
            "createdBy",
            "updatedAt",
            "updatedBy",
        ),
    ),
)

DESCRIPTORS_BY_KIND = {descriptor.kind: descriptor for descriptor in RESOURCE_DESCRIPTORS}


def _target(value: object) -> OperatorTarget:
    if not isinstance(value, dict):
        raise ValueError("operator target entries must be objects")
    credential = value.get("credentialSecretRef")
    if not isinstance(credential, dict):
        raise ValueError("operator targets require credentialSecretRef")
    endpoint = _required_string(value.get("endpoint"), "target endpoint").rstrip("/")
    if not endpoint.startswith(("http://", "https://")):
        raise ValueError("operator target endpoint must use HTTP or HTTPS")
    return OperatorTarget(
        tenant=_required_string(value.get("tenant"), "target tenant"),
        endpoint=endpoint,
        credential=SecretReference(
            namespace=_required_string(credential.get("namespace"), "credential namespace"),
            name=_required_string(credential.get("name"), "credential Secret name"),
            key=_required_string(credential.get("key"), "credential Secret key"),
        ),
    )


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _positive_float(values: Mapping[str, str], key: str, default: float) -> float:
    value = float(values.get(key, str(default)))
    if value <= 0:
        raise ValueError(f"{key} must be positive")
    return value


def _positive_int(values: Mapping[str, str], key: str, default: int) -> int:
    value = int(values.get(key, str(default)))
    if value <= 0:
        raise ValueError(f"{key} must be positive")
    return value


def object_mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return dict(value)
