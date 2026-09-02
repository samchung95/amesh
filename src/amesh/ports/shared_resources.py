from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from amesh.domain import (
    KeyValueChange,
    KeyValueEntry,
    KeyValueWrite,
    NamespaceFile,
    NamespaceFileVersion,
    SecretBinding,
    SecretBindingWrite,
)


class SharedResourceRepository(Protocol):
    async def put_file(
        self,
        namespace: str,
        path: str,
        *,
        object_uri: str,
        size_bytes: int,
        checksum_sha256: str,
        content_type: str | None,
        metadata: Mapping[str, Any],
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> NamespaceFile: ...

    async def list_files(
        self,
        namespace: str,
        *,
        tenant_id: str,
        actor_id: str,
        inherited: bool = True,
    ) -> list[NamespaceFile]: ...

    async def get_file_version(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        version: int | None = None,
    ) -> NamespaceFileVersion: ...

    async def list_file_versions(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> list[NamespaceFileVersion]: ...

    async def move_file(
        self,
        namespace: str,
        source_path: str,
        destination_path: str,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> NamespaceFile: ...

    async def delete_file(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> int: ...

    async def put_key_value(
        self,
        namespace: str,
        key: str,
        write: KeyValueWrite,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> KeyValueEntry: ...

    async def list_key_values(
        self, namespace: str, *, tenant_id: str, actor_id: str
    ) -> list[KeyValueEntry]: ...

    async def get_key_value(
        self,
        namespace: str,
        key: str,
        *,
        tenant_id: str,
        actor_id: str,
        audit_action: str = "key_value.read",
    ) -> KeyValueEntry: ...

    async def delete_key_value(
        self,
        namespace: str,
        key: str,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> bool: ...

    async def list_key_value_changes(
        self,
        namespace: str,
        *,
        tenant_id: str,
        actor_id: str,
        after: int = 0,
        limit: int = 100,
    ) -> list[KeyValueChange]: ...

    async def put_secret_binding(
        self,
        namespace: str,
        key: str,
        write: SecretBindingWrite,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> SecretBinding: ...

    async def list_secret_bindings(
        self,
        namespace: str,
        *,
        tenant_id: str,
        actor_id: str,
        inherited: bool = True,
    ) -> list[SecretBinding]: ...

    async def get_secret_binding(
        self, namespace: str, key: str, *, tenant_id: str, actor_id: str
    ) -> SecretBinding: ...

    async def delete_secret_binding(
        self,
        namespace: str,
        key: str,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> bool: ...


__all__ = ["SharedResourceRepository"]
