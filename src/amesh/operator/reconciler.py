from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from time import perf_counter
from typing import Any, Protocol

from prometheus_client import Counter, Histogram

from amesh.operator.client import (
    AmeshApiClient,
    AmeshApiError,
    RemoteResource,
    ResourceIdentity,
    canonical_digest,
)
from amesh.operator.model import (
    FINALIZER,
    OperatorSettings,
    OperatorTarget,
    ResourceDescriptor,
    object_mapping,
)

OPERATOR_RECONCILIATIONS = Counter(
    "amesh_operator_reconciliations",
    "AMESH Kubernetes operator reconciliation outcomes.",
    ("kind", "outcome"),
)
OPERATOR_RECONCILIATION_DURATION = Histogram(
    "amesh_operator_reconciliation_duration_seconds",
    "AMESH Kubernetes operator reconciliation duration.",
    ("kind",),
)


class KubernetesOperatorPort(Protocol):
    async def patch_finalizers(
        self,
        descriptor: ResourceDescriptor,
        resource: dict[str, Any],
        finalizers: tuple[str, ...],
    ) -> None: ...

    async def patch_status(
        self,
        descriptor: ResourceDescriptor,
        resource: dict[str, Any],
        status: dict[str, Any],
    ) -> None: ...

    async def read_secret(self, namespace: str, name: str, key: str) -> str: ...

    async def emit_event(
        self,
        resource: dict[str, Any],
        *,
        event_type: str,
        reason: str,
        message: str,
    ) -> None: ...


class AmeshApiPort(Protocol):
    async def read(
        self,
        descriptor: ResourceDescriptor,
        identity: ResourceIdentity,
        target: OperatorTarget,
        token: str,
    ) -> RemoteResource | None: ...

    async def apply(
        self,
        descriptor: ResourceDescriptor,
        identity: ResourceIdentity,
        desired: object,
        target: OperatorTarget,
        token: str,
        *,
        exists: bool,
        content_type: str | None = None,
    ) -> RemoteResource: ...

    async def delete(
        self,
        descriptor: ResourceDescriptor,
        identity: ResourceIdentity,
        target: OperatorTarget,
        token: str,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class ReconcileResult:
    outcome: str
    requeue_after_seconds: float | None = None


class AmeshResourceReconciler:
    def __init__(
        self,
        settings: OperatorSettings,
        kubernetes: KubernetesOperatorPort,
        api: AmeshApiPort | None = None,
    ) -> None:
        self._settings = settings
        self._kubernetes = kubernetes
        self._api: AmeshApiPort = api or AmeshApiClient()

    async def reconcile(
        self,
        descriptor: ResourceDescriptor,
        resource: dict[str, Any],
    ) -> ReconcileResult:
        started = perf_counter()
        try:
            result = await self._reconcile(descriptor, resource)
        except Exception as exc:
            result = await self._record_failure(descriptor, resource, exc)
        OPERATOR_RECONCILIATIONS.labels(descriptor.platform_kind, result.outcome).inc()
        OPERATOR_RECONCILIATION_DURATION.labels(descriptor.platform_kind).observe(
            perf_counter() - started
        )
        return result

    async def _reconcile(
        self,
        descriptor: ResourceDescriptor,
        resource: dict[str, Any],
    ) -> ReconcileResult:
        metadata = object_mapping(resource.get("metadata"), "metadata")
        spec = object_mapping(resource.get("spec"), "spec")
        status = _status(resource)
        identity = _identity(descriptor, metadata, spec, status)
        target = self._settings.target(identity.tenant)
        deletion_timestamp = metadata.get("deletionTimestamp")
        finalizers = tuple(str(item) for item in metadata.get("finalizers", []) if item)

        if deletion_timestamp:
            if FINALIZER not in finalizers:
                return ReconcileResult("deleted")
            deletion_policy = str(spec.get("deletionPolicy", "Retain"))
            if deletion_policy == "Delete":
                token = await self._credential(
                    target.credential.namespace,
                    target.credential.name,
                    target.credential.key,
                )
                await self._api.delete(descriptor, identity, target, token)
            elif deletion_policy != "Retain":
                raise ValueError("spec.deletionPolicy must be Delete or Retain")
            await self._kubernetes.emit_event(
                resource,
                event_type="Normal",
                reason="RemoteDeleted" if deletion_policy == "Delete" else "RemoteRetained",
                message=f"{descriptor.kind} finalizer completed with {deletion_policy} policy",
            )
            await self._kubernetes.patch_finalizers(
                descriptor,
                resource,
                tuple(item for item in finalizers if item != FINALIZER),
            )
            return ReconcileResult("deleted")

        if FINALIZER not in finalizers:
            await self._kubernetes.patch_finalizers(
                descriptor,
                resource,
                (*finalizers, FINALIZER),
            )

        desired = _desired(descriptor, spec)
        desired_digest = canonical_digest(_comparison_document(descriptor, desired))
        token = await self._credential(
            target.credential.namespace, target.credential.name, target.credential.key
        )
        remote = await self._api.read(descriptor, identity, target, token)
        remote_digest = (
            canonical_digest(_comparison_document(descriptor, remote.document))
            if remote is not None
            else ""
        )
        drifted = remote is not None and remote_digest != desired_digest
        reason = "InSync"
        outcome = "unchanged"

        if remote is None or drifted:
            if remote is not None and descriptor.replace_on_change:
                await self._api.delete(
                    descriptor,
                    _with_remote(identity, remote),
                    target,
                    token,
                )
                remote = None
            applied = await self._api.apply(
                descriptor,
                _with_remote(identity, remote),
                desired,
                target,
                token,
                exists=remote is not None,
                content_type=_optional_string(spec.get("contentType")),
            )
            remote = applied
            remote_digest = desired_digest
            reason = "DriftCorrected" if drifted else "Created"
            outcome = "updated" if drifted else "created"

        generation = _generation(metadata)
        if outcome == "unchanged" and _already_current(
            status,
            generation=generation,
            desired_digest=desired_digest,
            remote_digest=remote_digest,
        ):
            return ReconcileResult(outcome)
        reconciled_status = {
            "observedGeneration": generation,
            "remoteId": remote.server_id if remote is not None else identity.server_id,
            "remoteRevision": remote.revision if remote is not None else identity.revision,
            "appliedDigest": desired_digest,
            "remoteDigest": remote_digest,
            "failureCount": 0,
            "conditions": [
                _condition(
                    "Ready",
                    "True",
                    reason,
                    f"{descriptor.kind} desired state is reconciled through the AMESH API",
                    generation,
                ),
                _condition(
                    "DriftDetected",
                    "False",
                    "Corrected" if drifted else "NoDrift",
                    "Remote state matches the declared custom resource",
                    generation,
                ),
            ],
        }
        await self._kubernetes.patch_status(descriptor, resource, reconciled_status)
        await self._kubernetes.emit_event(
            resource,
            event_type="Normal",
            reason=reason,
            message=f"{descriptor.kind} reconciliation completed with outcome {outcome}",
        )
        return ReconcileResult(outcome)

    async def _record_failure(
        self,
        descriptor: ResourceDescriptor,
        resource: dict[str, Any],
        error: Exception,
    ) -> ReconcileResult:
        metadata = _status_metadata(resource)
        previous = _status(resource)
        failures = _failure_count(previous) + 1
        transient = (
            error.transient
            if isinstance(error, AmeshApiError)
            else not isinstance(error, ValueError)
        )
        delay = _retry_delay(self._settings, failures) if transient else None
        reason = "ReconcileFailed" if transient else "InvalidResource"
        message = _safe_error(error)
        failure_status = {
            **{
                key: previous[key]
                for key in ("remoteId", "remoteRevision", "appliedDigest", "remoteDigest")
                if key in previous
            },
            "observedGeneration": _generation(metadata),
            "failureCount": failures,
            "conditions": [
                _condition(
                    "Ready",
                    "False",
                    reason,
                    message,
                    _generation(metadata),
                )
            ],
        }
        if delay is not None:
            failure_status["retryAfter"] = (
                datetime.now(UTC) + timedelta(seconds=delay)
            ).isoformat()
        await self._kubernetes.patch_status(descriptor, resource, failure_status)
        await self._kubernetes.emit_event(
            resource,
            event_type="Warning",
            reason=reason,
            message=message,
        )
        return ReconcileResult("failed", delay)

    async def _credential(self, namespace: str, name: str, key: str) -> str:
        token = await self._kubernetes.read_secret(namespace, name, key)
        if not token:
            raise ValueError(f"Secret {namespace}/{name} key {key} is empty")
        return token


def _identity(
    descriptor: ResourceDescriptor,
    metadata: Mapping[str, object],
    spec: Mapping[str, object],
    status: Mapping[str, object],
) -> ResourceIdentity:
    tenant = _required_string(spec.get("tenant"), "spec.tenant")
    key = _optional_string(spec.get("key")) or _required_string(
        metadata.get("name"), "metadata.name"
    )
    namespace = _optional_string(spec.get("namespace"))
    if descriptor.kind == "AmeshNamespace":
        namespace = namespace or key
    if descriptor.namespaced and not namespace:
        raise ValueError(f"{descriptor.kind} requires spec.namespace")
    return ResourceIdentity(
        tenant=tenant,
        namespace=namespace or "",
        key=key,
        server_id=_optional_string(status.get("remoteId")) or "",
        revision=_optional_string(status.get("remoteRevision")) or "",
    )


def _desired(descriptor: ResourceDescriptor, spec: Mapping[str, object]) -> object:
    field = "content" if descriptor.payload_mode == "file" else "document"
    value = spec.get(field)
    if descriptor.payload_mode == "file":
        if not isinstance(value, str):
            raise ValueError("AmeshFile requires string spec.content")
        return value
    if not isinstance(value, dict):
        raise ValueError(f"{descriptor.kind} requires object spec.document")
    return dict(value)


def _comparison_document(descriptor: ResourceDescriptor, document: object) -> object:
    if not descriptor.comparison_defaults or not isinstance(document, Mapping):
        return document
    normalized = dict(document)
    for field, default in descriptor.comparison_defaults:
        normalized.setdefault(field, default)
    return normalized


def _with_remote(identity: ResourceIdentity, remote: RemoteResource | None) -> ResourceIdentity:
    if remote is None:
        return identity
    return ResourceIdentity(
        tenant=identity.tenant,
        namespace=identity.namespace,
        key=identity.key,
        server_id=remote.server_id or identity.server_id,
        revision=remote.revision or identity.revision,
    )


def _condition(
    condition_type: str,
    status: str,
    reason: str,
    message: str,
    generation: int,
) -> dict[str, object]:
    return {
        "type": condition_type,
        "status": status,
        "reason": reason,
        "message": message,
        "observedGeneration": generation,
        "lastTransitionTime": datetime.now(UTC).isoformat(),
    }


def _status(resource: Mapping[str, object]) -> dict[str, object]:
    value = resource.get("status")
    return dict(value) if isinstance(value, Mapping) else {}


def _status_metadata(resource: Mapping[str, object]) -> dict[str, object]:
    value = resource.get("metadata")
    return dict(value) if isinstance(value, Mapping) else {}


def _generation(metadata: Mapping[str, object]) -> int:
    value = metadata.get("generation", 0)
    return int(value) if isinstance(value, int | str) and str(value).isdigit() else 0


def _failure_count(status: Mapping[str, object]) -> int:
    value = status.get("failureCount", 0)
    return int(value) if isinstance(value, int | str) and str(value).isdigit() else 0


def _retry_delay(settings: OperatorSettings, failures: int) -> float:
    exponent = max(0, min(failures - 1, 20))
    return min(settings.retry_max_seconds, settings.retry_initial_seconds * math.pow(2, exponent))


def _already_current(
    status: Mapping[str, object],
    *,
    generation: int,
    desired_digest: str,
    remote_digest: str,
) -> bool:
    if (
        status.get("observedGeneration") != generation
        or status.get("appliedDigest") != desired_digest
        or status.get("remoteDigest") != remote_digest
        or _failure_count(status) != 0
    ):
        return False
    conditions = status.get("conditions")
    return isinstance(conditions, list) and any(
        isinstance(condition, Mapping)
        and condition.get("type") == "Ready"
        and condition.get("status") == "True"
        for condition in conditions
    )


def _safe_error(error: Exception) -> str:
    if isinstance(error, (AmeshApiError, ValueError)):
        return str(error)[:1_024]
    return f"{type(error).__name__} during reconciliation"


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _optional_string(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None
