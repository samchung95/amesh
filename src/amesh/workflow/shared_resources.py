from __future__ import annotations

import base64
import hashlib
import json
import os
from collections.abc import AsyncIterator, Mapping
from datetime import UTC, datetime
from typing import Any

from amesh.adapters.postgres.shared_resources import PostgresSharedResourceRepository
from amesh.domain import (
    ArtifactProvenance,
    ArtifactRef,
    ArtifactRetention,
    KeyValueExport,
    KeyValueWrite,
    NamespaceFile,
    NamespaceFileExport,
    NamespaceFileVersion,
    NamespaceResourceBundle,
    SecretBindingExport,
    SecretBindingWrite,
    build_artifact_reference,
    new_runtime_id,
    normalize_resource_path,
    parse_artifact_reference,
)
from amesh.executor.contracts import TaskContextRequest, TaskContextResources, TaskFileReference
from amesh.storage import VerifiedObjectStore


class NamespaceResourceService:
    def __init__(
        self,
        repository: PostgresSharedResourceRepository,
        object_store: VerifiedObjectStore,
    ) -> None:
        self._repository = repository
        self._object_store = object_store

    async def upload_file(
        self,
        namespace: str,
        path: str,
        content: bytes,
        *,
        tenant_id: str,
        actor_id: str,
        content_type: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        expected_version: int | None = None,
    ) -> NamespaceFile:
        path = normalize_resource_path(path)
        if len(content) > 64 * 1024 * 1024:
            raise ValueError("namespace file cannot exceed 64 MiB")

        async def chunks() -> AsyncIterator[bytes]:
            if content:
                yield content

        key = (
            "namespace-files/"
            f"{hashlib.sha256(namespace.encode()).hexdigest()[:24]}/"
            f"{hashlib.sha256(path.encode()).hexdigest()[:24]}/{new_runtime_id()}"
        )
        stored = await self._object_store.put(
            tenant_id,
            key,
            chunks(),
            content_type=content_type,
            creator=actor_id,
            lineage=("namespace-file", namespace, path),
        )
        return await self._repository.put_file(
            namespace,
            path,
            object_uri=stored.uri,
            size_bytes=stored.size,
            checksum_sha256=stored.checksum_sha256,
            content_type=stored.content_type,
            metadata=metadata or {},
            tenant_id=tenant_id,
            actor_id=actor_id,
            expected_version=expected_version,
        )

    async def download_file(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        version: int | None = None,
    ) -> tuple[NamespaceFileVersion, bytes]:
        selected = await self._repository.get_file_version(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=actor_id,
            version=version,
        )
        chunks = [chunk async for chunk in self._object_store.get(tenant_id, selected.object_uri)]
        content = b"".join(chunks)
        if len(content) != selected.size_bytes:
            raise RuntimeError("namespace file size changed during download")
        return selected, content

    async def list_artifacts(
        self,
        namespace: str,
        *,
        tenant_id: str,
        actor_id: str,
        inherited: bool = True,
    ) -> list[ArtifactRef]:
        files = await self._repository.list_files(
            namespace,
            tenant_id=tenant_id,
            actor_id=actor_id,
            inherited=inherited,
        )
        artifacts = [
            await self._artifact_for_file(
                namespace,
                item.path,
                tenant_id=tenant_id,
                actor_id=actor_id,
                origin_namespace=item.origin_namespace,
            )
            for item in files
        ]
        return sorted(artifacts, key=lambda item: item.path)

    async def get_artifact(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        version: int | None = None,
    ) -> ArtifactRef:
        files = await self._repository.list_files(
            namespace,
            tenant_id=tenant_id,
            actor_id=actor_id,
            inherited=True,
        )
        selected_file = next((item for item in files if item.path == path), None)
        if selected_file is None:
            raise LookupError(f"namespace file {path!r} does not exist")
        return await self._artifact_for_file(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=actor_id,
            version=version,
            origin_namespace=selected_file.origin_namespace,
        )

    async def _artifact_for_file(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        origin_namespace: str,
        version: int | None = None,
    ) -> ArtifactRef:
        selected = await self._repository.get_file_version(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=actor_id,
            version=version,
        )
        stored = await self._object_store.head(tenant_id, selected.object_uri)
        if stored.size != selected.size_bytes or stored.checksum_sha256 != selected.checksum_sha256:
            raise ValueError("namespace file object metadata does not match its recorded version")
        checksum = selected.checksum_sha256
        return ArtifactRef(
            reference=build_artifact_reference(selected.path, selected.version, checksum),
            contentAddress=f"sha256:{checksum}",
            tenantId=tenant_id,
            namespace=namespace,
            path=selected.path,
            version=selected.version,
            mediaType=stored.content_type or selected.content_type,
            sizeBytes=stored.size,
            checksumSha256=checksum,
            provenance=ArtifactProvenance(
                source="namespace-file",
                originNamespace=origin_namespace,
                createdBy=selected.created_by,
                createdAt=selected.created_at,
                lineage=stored.lineage or ("namespace-file", origin_namespace, selected.path),
            ),
            retention=ArtifactRetention(
                retentionUntil=stored.retention_until,
                legalHold=stored.legal_hold,
            ),
        )

    async def export_bundle(
        self,
        namespace: str,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> NamespaceResourceBundle:
        files = await self._repository.list_files(
            namespace,
            tenant_id=tenant_id,
            actor_id=actor_id,
            inherited=False,
        )
        file_exports: list[NamespaceFileExport] = []
        for item in files:
            _, content = await self.download_file(
                namespace,
                item.path,
                tenant_id=tenant_id,
                actor_id=actor_id,
            )
            file_exports.append(
                NamespaceFileExport(
                    path=item.path,
                    contentBase64=base64.b64encode(content).decode(),
                    contentType=item.content_type,
                    metadata=item.metadata,
                )
            )
        key_values = await self._repository.list_key_values(
            namespace, tenant_id=tenant_id, actor_id=actor_id
        )
        secrets = await self._repository.list_secret_bindings(
            namespace,
            tenant_id=tenant_id,
            actor_id=actor_id,
            inherited=False,
        )
        candidate = NamespaceResourceBundle(
            sourceNamespace=namespace,
            exportedAt=datetime.now(UTC),
            files=tuple(file_exports),
            keyValues=tuple(
                KeyValueExport(
                    key=item.key,
                    type=item.value_type,
                    value=item.value,
                    expiresAt=item.expires_at,
                    metadata=item.metadata,
                )
                for item in key_values
            ),
            secrets=tuple(
                SecretBindingExport(
                    key=item.key,
                    provider=item.provider,
                    providerReference=item.provider_reference,
                    metadata=item.metadata,
                )
                for item in secrets
            ),
            checksumSha256="0" * 64,
        )
        return candidate.model_copy(update={"checksum_sha256": _bundle_checksum(candidate)})

    async def import_bundle(
        self,
        namespace: str,
        bundle: NamespaceResourceBundle,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> dict[str, int]:
        if _bundle_checksum(bundle) != bundle.checksum_sha256:
            raise ValueError("namespace resource bundle checksum mismatch")
        for item in bundle.files:
            try:
                content = base64.b64decode(item.content_base64, validate=True)
            except ValueError as exc:
                raise ValueError(f"namespace file {item.path!r} has invalid base64") from exc
            await self.upload_file(
                namespace,
                item.path,
                content,
                tenant_id=tenant_id,
                actor_id=actor_id,
                content_type=item.content_type,
                metadata=item.metadata,
            )
        for key_value in bundle.key_values:
            await self._repository.put_key_value(
                namespace,
                key_value.key,
                KeyValueWrite.model_validate(key_value.model_dump(by_alias=True, exclude={"key"})),
                tenant_id=tenant_id,
                actor_id=actor_id,
            )
        for secret in bundle.secrets:
            await self._repository.put_secret_binding(
                namespace,
                secret.key,
                SecretBindingWrite.model_validate(
                    secret.model_dump(by_alias=True, exclude={"key"})
                ),
                tenant_id=tenant_id,
                actor_id=actor_id,
            )
        return {
            "files": len(bundle.files),
            "keyValues": len(bundle.key_values),
            "secretBindings": len(bundle.secrets),
        }


class SharedResourceContextProvider:
    """Resolve declared shared resources immediately before task rendering and dispatch."""

    def __init__(
        self,
        repository: PostgresSharedResourceRepository,
        *,
        object_store: VerifiedObjectStore | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> None:
        self._repository = repository
        self._object_store = object_store
        self._environment = os.environ if environment is None else environment

    async def resolve(self, request: TaskContextRequest) -> TaskContextResources:
        actor_id = f"execution:{request.execution_id}:task:{request.task_run_id}"
        secrets: dict[str, str] = {}
        for key in request.secret_scopes:
            binding = await self._repository.get_secret_binding(
                request.namespace,
                key,
                tenant_id=request.tenant_id,
                actor_id=actor_id,
            )
            value = self._environment.get(binding.provider_reference)
            if value is None:
                raise RuntimeError(
                    f"secret provider reference for {key!r} is unavailable at execution time"
                )
            secrets[key] = value
        key_values = (
            {
                item.key: item.value
                for item in await self._repository.list_key_values(
                    request.namespace,
                    tenant_id=request.tenant_id,
                    actor_id=actor_id,
                )
            }
            if request.key_values_required
            else {}
        )
        files: dict[str, str] = {}
        file_references: dict[str, TaskFileReference] = {}
        for name, reference in request.declared_files.items():
            prefix = "nsfile:///"
            if not reference.startswith(prefix):
                files[name] = reference
                if self._object_store is not None:
                    selected_object = await self._object_store.head(request.tenant_id, reference)
                    file_references[name] = TaskFileReference(
                        uri=selected_object.uri,
                        sizeBytes=selected_object.size,
                        checksumSha256=selected_object.checksum_sha256,
                    )
                continue
            exact_version: int | None = None
            expected_checksum: str | None = None
            if "?" in reference:
                parsed_path, exact_version, expected_checksum = parse_artifact_reference(reference)
            else:
                parsed_path = reference.removeprefix(prefix)
            selected = await self._repository.get_file_version(
                request.namespace,
                parsed_path,
                tenant_id=request.tenant_id,
                actor_id=actor_id,
                version=exact_version,
            )
            if expected_checksum is not None and selected.checksum_sha256 != expected_checksum:
                raise ValueError(
                    f"artifact reference digest does not match namespace file {parsed_path!r}"
                )
            files[name] = selected.object_uri
            file_references[name] = TaskFileReference(
                uri=selected.object_uri,
                sizeBytes=selected.size_bytes,
                checksumSha256=selected.checksum_sha256,
            )
        return TaskContextResources(
            secrets=secrets,
            files=files,
            keyValues=key_values,
            fileReferences=file_references,
        )


def _bundle_checksum(bundle: NamespaceResourceBundle) -> str:
    payload = bundle.model_dump(
        mode="json",
        by_alias=True,
        exclude={"checksum_sha256"},
        exclude_none=True,
    )
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()
