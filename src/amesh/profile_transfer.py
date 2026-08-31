from __future__ import annotations

import hashlib
import re
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain.agent_primitives import McpConnectionRevision
from amesh.domain.agent_resources import (
    AgentDefinitionSpec,
    AgentEvaluationSpec,
    AgentResourceKind,
    AgentResourceRevision,
    AgentResourceSpec,
    agent_resource_digest,
)
from amesh.domain.resources import canonical_json
from amesh.domain.tool_provider import ToolProviderKind
from amesh.ports.agent_primitives import AgentPrimitiveRepository
from amesh.ports.agent_resources import AgentResourceRepository

if TYPE_CHECKING:
    from amesh.ports.transfer_repository import ProfileTransferImportRepository

_PROFILE_SCHEMA = "amesh.profile/v1"
_EMPTY_DIGEST = "0" * 64
_SECRET_KEYS = frozenset(
    {
        "password",
        "token",
        "secret",
        "secret_value",
        "api_key",
        "apikey",
        "private_key",
        "privatekey",
        "access_token",
        "refresh_token",
        "credential",
        "credentials",
        "credential_value",
    }
)
_SENSITIVE_KEY_PATTERN = re.compile(
    r"(?:^|_)(?:client|access|refresh|bearer|auth)_(?:token|secret)(?:_|$)|"
    r"(?:^|_)(?:api|private)_key(?:_|$)|"
    r"(?:^|_)(?:token|secret|password|credential)(?:_|$)"
)
_REFERENCE_KEYS = frozenset({"credentialref", "credential_ref", "secretscopes", "secret_scopes"})
_RESOURCE_ORDER = {
    AgentResourceKind.PROMPT: 0,
    AgentResourceKind.SKILL: 1,
    AgentResourceKind.MODEL_POLICY: 2,
    AgentResourceKind.EVALUATION: 3,
    AgentResourceKind.AGENT: 4,
}


class ProfileBundle(BaseModel):
    """Portable, immutable agent profile data with no resolved secret values."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    schema_version: str = Field(default=_PROFILE_SCHEMA, alias="schemaVersion")
    source_tenant_id: str = Field(alias="sourceTenantId", min_length=1, max_length=255)
    namespace: str = Field(min_length=1, max_length=255)
    agent_key: str = Field(alias="agentKey", min_length=1, max_length=255)
    agent_revision: int = Field(alias="agentRevision", ge=1)
    resources: tuple[AgentResourceRevision, ...] = ()
    mcp_connections: tuple[McpConnectionRevision, ...] = Field(default=(), alias="mcpConnections")
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")

    def canonical_bytes(self) -> bytes:
        """Return deterministic JSON bytes suitable for transport or storage."""
        return canonical_json(self.model_dump(mode="json", by_alias=True))

    @property
    def import_id(self) -> str:
        return f"{self.source_tenant_id}:{self.namespace}:{self.agent_key}:{self.agent_revision}"

    def verify(self) -> None:
        if self.schema_version != _PROFILE_SCHEMA:
            raise ValueError(f"unsupported profile bundle schema {self.schema_version!r}")
        if self.checksum_sha256 != _bundle_checksum(self):
            raise ValueError("profile bundle checksum is invalid")


class ProfileCompatibilityState(StrEnum):
    CREATE = "CREATE"
    EXISTING = "EXISTING"


class ProfileCompatibilityReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    compatible: bool
    target_tenant_id: str = Field(alias="targetTenantId")
    target_namespace: str = Field(alias="targetNamespace")
    resources_to_create: int = Field(default=0, alias="resourcesToCreate", ge=0)
    resources_existing: int = Field(default=0, alias="resourcesExisting", ge=0)
    mcp_connections_to_create: int = Field(default=0, alias="mcpConnectionsToCreate", ge=0)
    mcp_connections_existing: int = Field(default=0, alias="mcpConnectionsExisting", ge=0)
    issues: tuple[str, ...] = ()


class ProfileCompatibilityError(ValueError):
    def __init__(self, report: ProfileCompatibilityReport) -> None:
        self.report = report
        message = "profile destination is incompatible"
        if report.issues:
            message += ": " + "; ".join(report.issues)
        super().__init__(message)


class ProfileImportResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    target_tenant_id: str = Field(alias="targetTenantId")
    target_namespace: str = Field(alias="targetNamespace")
    agent_key: str = Field(alias="agentKey")
    agent_revision: int = Field(alias="agentRevision", ge=1)
    resources_imported: int = Field(alias="resourcesImported", ge=0)
    resources_existing: int = Field(alias="resourcesExisting", ge=0)
    mcp_connections_imported: int = Field(alias="mcpConnectionsImported", ge=0)
    mcp_connections_existing: int = Field(alias="mcpConnectionsExisting", ge=0)
    import_id: str = Field(default="", alias="importId")
    bundle_digest: str = Field(default=_EMPTY_DIGEST, alias="bundleDigest")
    already_present: bool = Field(default=False, alias="alreadyPresent")


class ProfileTransferService:
    """Export and import a profile through the existing immutable repositories."""

    def __init__(
        self,
        resources: AgentResourceRepository,
        primitives: AgentPrimitiveRepository,
        imports: ProfileTransferImportRepository | None = None,
    ) -> None:
        self._resources = resources
        self._primitives = primitives
        self._imports = imports

    async def export(
        self,
        tenant_id: str,
        namespace: str,
        agent_key: str,
        *,
        agent_revision: int | None = None,
        actor_id: str | None = None,
    ) -> ProfileBundle:
        del actor_id  # Export authorization/audit belongs to the administrative caller.
        root = await self._resources.get_resource(
            tenant_id,
            namespace,
            AgentResourceKind.AGENT,
            agent_key,
            revision=agent_revision,
        )
        if root.kind is not AgentResourceKind.AGENT or root.key != agent_key:
            raise ValueError("requested resource is not the selected agent")

        resources: dict[tuple[AgentResourceKind, str, int], AgentResourceRevision] = {}
        connections: dict[tuple[str, int], McpConnectionRevision] = {}
        pending: list[tuple[AgentResourceKind, str, int]] = [(root.kind, root.key, root.revision)]
        while pending:
            kind, key, revision = pending.pop()
            if (kind, key, revision) in resources:
                continue
            history = await self._resource_history(tenant_id, namespace, kind, key, revision)
            for item in history:
                _check_resource_tenant(item, tenant_id)
                _check_no_secrets(item.spec)
                resources[(item.kind, item.key, item.revision)] = item
                for ref_kind, ref_key, ref_revision in _resource_references(item.spec):
                    pending.append((ref_kind, ref_key, ref_revision))
                for connection_key, connection_revision in _mcp_references(item.spec):
                    connection_history = await self._mcp_history(
                        tenant_id,
                        namespace,
                        connection_key,
                        connection_revision,
                    )
                    for connection in connection_history:
                        _check_connection_tenant(connection, tenant_id)
                        _check_no_secrets(connection.spec)
                        connections[(connection.spec.key, connection.revision)] = connection

        ordered_resources = tuple(
            sorted(
                resources.values(),
                key=lambda item: (_RESOURCE_ORDER[item.kind], item.key, item.revision),
            )
        )
        ordered_connections = tuple(
            sorted(connections.values(), key=lambda item: (item.spec.key, item.revision))
        )
        unsigned = ProfileBundle(
            sourceTenantId=tenant_id,
            namespace=namespace,
            agentKey=agent_key,
            agentRevision=root.revision,
            resources=ordered_resources,
            mcpConnections=ordered_connections,
            checksumSha256=_EMPTY_DIGEST,
        )
        return unsigned.model_copy(update={"checksum_sha256": _bundle_checksum(unsigned)})

    async def compatibility(
        self,
        bundle: ProfileBundle,
        *,
        target_tenant_id: str,
        target_namespace: str | None = None,
    ) -> ProfileCompatibilityReport:
        bundle.verify()
        _validate_bundle(bundle)
        target_namespace = target_namespace or bundle.namespace
        issues: list[str] = []
        if target_namespace != bundle.namespace:
            issues.append(
                f"namespace mapping is unsupported: bundle={bundle.namespace!r}, "
                f"target={target_namespace!r}"
            )

        resources_to_create = resources_existing = 0
        for resource in bundle.resources:
            state, issue = await self._resource_state(
                target_tenant_id,
                target_namespace,
                resource,
            )
            if state is ProfileCompatibilityState.CREATE:
                resources_to_create += 1
            else:
                resources_existing += 1
            if issue:
                issues.append(issue)

        connections_to_create = connections_existing = 0
        for connection in bundle.mcp_connections:
            state, issue = await self._connection_state(
                target_tenant_id,
                target_namespace,
                connection,
            )
            if state is ProfileCompatibilityState.CREATE:
                connections_to_create += 1
            else:
                connections_existing += 1
            if issue:
                issues.append(issue)

        return ProfileCompatibilityReport(
            compatible=not issues,
            targetTenantId=target_tenant_id,
            targetNamespace=target_namespace,
            resourcesToCreate=resources_to_create,
            resourcesExisting=resources_existing,
            mcpConnectionsToCreate=connections_to_create,
            mcpConnectionsExisting=connections_existing,
            issues=tuple(issues),
        )

    async def import_bundle(
        self,
        bundle: ProfileBundle,
        *,
        target_tenant_id: str,
        actor_id: str,
        target_namespace: str | None = None,
    ) -> ProfileImportResult:
        report = await self.compatibility(
            bundle,
            target_tenant_id=target_tenant_id,
            target_namespace=target_namespace,
        )
        if not report.compatible:
            raise ProfileCompatibilityError(report)

        if self._imports is not None:
            existing = await self._imports.get_profile_import(target_tenant_id, bundle.import_id)
            if existing is not None:
                if existing.bundle_digest != bundle.checksum_sha256:
                    raise ValueError("profile import identity was reused with another bundle")
                return ProfileImportResult(
                    targetTenantId=target_tenant_id,
                    targetNamespace=report.target_namespace,
                    agentKey=bundle.agent_key,
                    agentRevision=bundle.agent_revision,
                    resourcesImported=0,
                    resourcesExisting=len(bundle.resources),
                    mcpConnectionsImported=0,
                    mcpConnectionsExisting=len(bundle.mcp_connections),
                    importId=bundle.import_id,
                    bundleDigest=bundle.checksum_sha256,
                    alreadyPresent=True,
                )

        imported_resources = existing_resources = 0
        imported_connections = existing_connections = 0
        for connection in bundle.mcp_connections:
            if await self._connection_exists(target_tenant_id, report.target_namespace, connection):
                existing_connections += 1
                continue
            saved_connection = await self._primitives.save_mcp_connection(
                target_tenant_id,
                connection.spec,
                actor_id=actor_id,
            )
            if (
                saved_connection.revision != connection.revision
                or saved_connection.digest != connection.digest
            ):
                raise ValueError(
                    f"MCP connection {connection.spec.key}@{connection.revision} "
                    "could not be recreated at its immutable revision"
                )
            imported_connections += 1
        for resource in sorted(
            bundle.resources,
            key=lambda item: (_RESOURCE_ORDER[item.kind], item.key, item.revision),
        ):
            if await self._resource_exists(target_tenant_id, report.target_namespace, resource):
                existing_resources += 1
                continue
            saved_resource = await self._resources.save_resource(
                target_tenant_id,
                resource.spec,
                actor_id=actor_id,
            )
            if (
                saved_resource.revision != resource.revision
                or saved_resource.digest != resource.digest
            ):
                raise ValueError(
                    f"{resource.kind.value} resource {resource.key}@{resource.revision} "
                    "could not be recreated at its immutable revision"
                )
            imported_resources += 1

        result = ProfileImportResult(
            targetTenantId=target_tenant_id,
            targetNamespace=report.target_namespace,
            agentKey=bundle.agent_key,
            agentRevision=bundle.agent_revision,
            resourcesImported=imported_resources,
            resourcesExisting=existing_resources,
            mcpConnectionsImported=imported_connections,
            mcpConnectionsExisting=existing_connections,
            importId=bundle.import_id,
            bundleDigest=bundle.checksum_sha256,
        )
        if self._imports is not None:
            await self._imports.record_profile_import(
                target_tenant_id,
                bundle,
                actor_id=actor_id,
                import_id=bundle.import_id,
            )
        return result

    async def _resource_history(
        self,
        tenant_id: str,
        namespace: str,
        kind: AgentResourceKind,
        key: str,
        revision: int,
    ) -> tuple[AgentResourceRevision, ...]:
        result: list[AgentResourceRevision] = []
        for item_revision in range(1, revision + 1):
            try:
                result.append(
                    await self._resources.get_resource(
                        tenant_id, namespace, kind, key, revision=item_revision
                    )
                )
            except LookupError as exc:
                raise ValueError(
                    f"cannot export {kind.value} resource {namespace}.{key}@{revision}: "
                    f"immutable revision {item_revision} is unavailable"
                ) from exc
        return tuple(result)

    async def _mcp_history(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        revision: int,
    ) -> tuple[McpConnectionRevision, ...]:
        result: list[McpConnectionRevision] = []
        for item_revision in range(1, revision + 1):
            try:
                result.append(
                    await self._primitives.get_mcp_connection(
                        tenant_id, namespace, key, revision=item_revision
                    )
                )
            except LookupError as exc:
                raise ValueError(
                    f"cannot export MCP connection {namespace}.{key}@{revision}: "
                    f"immutable revision {item_revision} is unavailable"
                ) from exc
        return tuple(result)

    async def _resource_state(
        self,
        tenant_id: str,
        namespace: str,
        expected: AgentResourceRevision,
    ) -> tuple[ProfileCompatibilityState, str | None]:
        try:
            current = await self._resources.get_resource(
                tenant_id,
                namespace,
                expected.kind,
                expected.key,
                revision=expected.revision,
            )
        except LookupError:
            latest = await self._latest_resource(tenant_id, namespace, expected)
            if latest is not None and latest.revision >= expected.revision:
                return ProfileCompatibilityState.EXISTING, (
                    f"resource {expected.kind.value}:{expected.key}@{expected.revision} "
                    f"is absent but destination is already at revision {latest.revision}"
                )
            if latest is not None and latest.revision + 1 != expected.revision:
                return ProfileCompatibilityState.EXISTING, (
                    f"resource {expected.kind.value}:{expected.key} has revision gap "
                    f"before {expected.revision}"
                )
            return ProfileCompatibilityState.CREATE, None
        if current.digest != expected.digest or current.spec != expected.spec:
            return ProfileCompatibilityState.EXISTING, (
                f"resource {expected.kind.value}:{expected.key}@{expected.revision} "
                "digest or spec differs"
            )
        if current.tenant_id != tenant_id:
            return ProfileCompatibilityState.EXISTING, (
                f"resource {expected.kind.value}:{expected.key}@{expected.revision} "
                "belongs to another tenant"
            )
        return ProfileCompatibilityState.EXISTING, None

    async def _connection_state(
        self,
        tenant_id: str,
        namespace: str,
        expected: McpConnectionRevision,
    ) -> tuple[ProfileCompatibilityState, str | None]:
        try:
            current = await self._primitives.get_mcp_connection(
                tenant_id,
                namespace,
                expected.spec.key,
                revision=expected.revision,
            )
        except LookupError:
            latest = await self._latest_connection(tenant_id, namespace, expected.spec.key)
            if latest is not None and latest.revision >= expected.revision:
                return ProfileCompatibilityState.EXISTING, (
                    f"MCP connection {expected.spec.key}@{expected.revision} is absent "
                    f"but destination is already at revision {latest.revision}"
                )
            if latest is not None and latest.revision + 1 != expected.revision:
                return ProfileCompatibilityState.EXISTING, (
                    f"MCP connection {expected.spec.key} has revision gap "
                    f"before {expected.revision}"
                )
            return ProfileCompatibilityState.CREATE, None
        if current.digest != expected.digest or current.spec != expected.spec:
            return ProfileCompatibilityState.EXISTING, (
                f"MCP connection {expected.spec.key}@{expected.revision} digest or spec differs"
            )
        if current.tenant_id != tenant_id:
            return ProfileCompatibilityState.EXISTING, (
                f"MCP connection {expected.spec.key}@{expected.revision} "
                "belongs to another tenant"
            )
        return ProfileCompatibilityState.EXISTING, None

    async def _resource_exists(
        self, tenant_id: str, namespace: str, expected: AgentResourceRevision
    ) -> bool:
        state, issue = await self._resource_state(tenant_id, namespace, expected)
        if issue:
            raise ProfileCompatibilityError(
                ProfileCompatibilityReport(
                    compatible=False,
                    targetTenantId=tenant_id,
                    targetNamespace=namespace,
                    issues=(issue,),
                )
            )
        return state is ProfileCompatibilityState.EXISTING

    async def _connection_exists(
        self, tenant_id: str, namespace: str, expected: McpConnectionRevision
    ) -> bool:
        state, issue = await self._connection_state(tenant_id, namespace, expected)
        if issue:
            raise ProfileCompatibilityError(
                ProfileCompatibilityReport(
                    compatible=False,
                    targetTenantId=tenant_id,
                    targetNamespace=namespace,
                    issues=(issue,),
                )
            )
        return state is ProfileCompatibilityState.EXISTING

    async def _latest_resource(
        self, tenant_id: str, namespace: str, expected: AgentResourceRevision
    ) -> AgentResourceRevision | None:
        items = await self._resources.list_resources(tenant_id, namespace, kind=expected.kind)
        return next((item for item in items if item.key == expected.key), None)

    async def _latest_connection(
        self, tenant_id: str, namespace: str, key: str
    ) -> McpConnectionRevision | None:
        items = await self._primitives.list_mcp_connections(tenant_id, namespace)
        return next((item for item in items if item.spec.key == key), None)


def _resource_references(spec: AgentResourceSpec) -> tuple[tuple[AgentResourceKind, str, int], ...]:
    refs: list[tuple[AgentResourceKind, str, int]] = []
    if isinstance(spec, AgentDefinitionSpec):
        refs.append(
            (AgentResourceKind.MODEL_POLICY, spec.model_policy.key, spec.model_policy.revision)
        )
        refs.extend((AgentResourceKind.PROMPT, item.key, item.revision) for item in spec.prompts)
        refs.extend((AgentResourceKind.SKILL, item.key, item.revision) for item in spec.skills)
        refs.extend(
            (AgentResourceKind.EVALUATION, item.key, item.revision)
            for item in spec.evaluation_policy.evaluations
        )
    elif isinstance(spec, AgentEvaluationSpec) and spec.judge is not None:
        refs.append(
            (
                AgentResourceKind.MODEL_POLICY,
                spec.judge.model_policy.key,
                spec.judge.model_policy.revision,
            )
        )
    return tuple(refs)


def _mcp_references(spec: AgentResourceSpec) -> tuple[tuple[str, int], ...]:
    if not isinstance(spec, AgentDefinitionSpec):
        return ()
    return tuple(
        (tool.connection_key, tool.connection_revision)
        for tool in spec.tools
        if tool.provider_kind is ToolProviderKind.MCP
        and tool.connection_key is not None
        and tool.connection_revision is not None
    )


def _validate_bundle(bundle: ProfileBundle) -> None:
    if not bundle.resources:
        raise ValueError("profile bundle has no resources")
    resource_keys: set[tuple[str, AgentResourceKind, str, int]] = set()
    for resource in bundle.resources:
        if resource.namespace != bundle.namespace:
            raise ValueError("profile bundle contains a resource from another namespace")
        resource_identity = (resource.namespace, resource.kind, resource.key, resource.revision)
        if resource_identity in resource_keys:
            raise ValueError(f"profile bundle contains duplicate resource {resource_identity}")
        resource_keys.add(resource_identity)
        if resource.digest != agent_resource_digest(resource.spec):
            raise ValueError(
                f"resource {resource.kind.value}:{resource.key}@{resource.revision} digest is invalid"
            )
        if resource.tenant_id != bundle.source_tenant_id:
            raise ValueError("profile bundle contains a resource from another tenant")
        _check_no_secrets(resource.spec)
    root = (bundle.namespace, AgentResourceKind.AGENT, bundle.agent_key, bundle.agent_revision)
    if root not in resource_keys:
        raise ValueError("profile bundle does not contain its selected agent revision")

    connection_keys: set[tuple[str, str, int]] = set()
    for connection in bundle.mcp_connections:
        if connection.spec.namespace != bundle.namespace:
            raise ValueError("profile bundle contains an MCP connection from another namespace")
        connection_identity = (
            connection.spec.namespace,
            connection.spec.key,
            connection.revision,
        )
        if connection_identity in connection_keys:
            raise ValueError(
                f"profile bundle contains duplicate MCP connection {connection_identity}"
            )
        connection_keys.add(connection_identity)
        if connection.tenant_id != bundle.source_tenant_id:
            raise ValueError("profile bundle contains an MCP connection from another tenant")
        if connection.digest != connection.spec.digest:
            raise ValueError(
                f"MCP connection {connection.spec.key}@{connection.revision} digest is invalid"
            )
        _check_no_secrets(connection.spec)

    for resource in bundle.resources:
        for ref_kind, ref_key, ref_revision in _resource_references(resource.spec):
            if (resource.namespace, ref_kind, ref_key, ref_revision) not in resource_keys:
                raise ValueError(
                    f"profile bundle is missing {ref_kind.value}:{ref_key}@{ref_revision}"
                )
        for ref_key, ref_revision in _mcp_references(resource.spec):
            if (resource.namespace, ref_key, ref_revision) not in connection_keys:
                raise ValueError(
                    f"profile bundle is missing MCP connection {ref_key}@{ref_revision}"
                )


def _check_resource_tenant(resource: AgentResourceRevision, tenant_id: str) -> None:
    if resource.tenant_id != tenant_id:
        raise ValueError("repository returned a resource from another tenant")


def _check_connection_tenant(connection: McpConnectionRevision, tenant_id: str) -> None:
    if connection.tenant_id != tenant_id:
        raise ValueError("repository returned an MCP connection from another tenant")


def _check_no_secrets(value: Any) -> None:
    _walk_for_secrets(
        value.model_dump(mode="json", by_alias=True) if isinstance(value, BaseModel) else value
    )


def _walk_for_secrets(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub(r"(?<!^)(?=[A-Z])", "_", str(key)).replace("-", "_").lower()
            if normalized not in _REFERENCE_KEYS and (
                normalized in _SECRET_KEYS or _SENSITIVE_KEY_PATTERN.search(normalized)
            ):
                raise ValueError(f"profile contains secret-bearing field {key!r}")
            _walk_for_secrets(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _walk_for_secrets(item)


def _bundle_checksum(bundle: ProfileBundle) -> str:
    return hashlib.sha256(
        canonical_json(bundle.model_dump(mode="json", by_alias=True, exclude={"checksum_sha256"}))
    ).hexdigest()


__all__ = [
    "ProfileBundle",
    "ProfileCompatibilityError",
    "ProfileCompatibilityReport",
    "ProfileImportResult",
    "ProfileTransferService",
]
