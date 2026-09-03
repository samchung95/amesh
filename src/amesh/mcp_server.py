from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit
from uuid import UUID

from mcp.server import MCPServer
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import AnyHttpUrl
from starlette.applications import Starlette

from amesh.authorization import AuthorizationService
from amesh.domain import (
    ActorContext,
    AgentDefinitionSpec,
    AgentResourceKind,
    AuthorizationRequest,
    PermissionAction,
    PrincipalType,
)
from amesh.identity import CredentialService, InvalidCredential
from amesh.ports import AgentResourceRepository, CredentialRateLimitExceeded, ExecutionRepository


class AmeshMcpTokenVerifier:
    """Adapt AMESH workload credentials to the MCP SDK bearer contract."""

    def __init__(self, credentials: CredentialService) -> None:
        self._credentials = credentials

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            actor = await self._credentials.authenticate_bearer(
                f"Bearer {token}",
                audience="amesh-mcp",
            )
        except (CredentialRateLimitExceeded, InvalidCredential):
            return None
        return AccessToken(
            token="[REDACTED]",
            client_id=str(actor.credential_id or actor.principal_id),
            scopes=list(actor.credential_scopes),
            subject=str(actor.principal_id),
            claims={
                "principalType": actor.principal_type.value,
                "display": actor.display,
                "bootstrapAdmin": actor.bootstrap_admin,
                "credentialId": str(actor.credential_id) if actor.credential_id else None,
                "credentialScopes": list(actor.credential_scopes),
                "credentialAudience": actor.credential_audience,
            },
        )


class AmeshMcpReadGateway:
    """Authorization-checked read projections exposed to MCP clients."""

    def __init__(
        self,
        executions: ExecutionRepository,
        agent_resources: AgentResourceRepository,
        authorization: AuthorizationService,
    ) -> None:
        self._executions = executions
        self._agent_resources = agent_resources
        self._authorization = authorization

    async def list_workflows(
        self,
        tenant: str,
        namespace: str,
        limit: int = 100,
    ) -> dict[str, Any]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        actor = _authenticated_actor()
        await self._authorization.require(
            AuthorizationRequest(
                actor=actor,
                tenant_id=tenant,
                namespace=namespace,
                resource_type="flow",
                action=PermissionAction.LIST,
                audience="amesh-mcp",
            )
        )
        flows = [
            flow
            for flow in await self._executions.list_flows(tenant_id=tenant)
            if flow.namespace == namespace
        ][:limit]
        return {
            "tenant": tenant,
            "namespace": namespace,
            "workflows": [
                {
                    "id": flow.flow_id,
                    "revision": flow.revision,
                    "lifecycle": flow.lifecycle.value,
                    "semanticHash": flow.semantic_hash,
                    "etag": flow.etag,
                }
                for flow in flows
            ],
        }

    async def inspect_execution(
        self,
        tenant: str,
        execution_id: str,
    ) -> dict[str, Any]:
        try:
            identifier = UUID(execution_id)
        except ValueError as exc:
            raise ValueError("execution_id must be a UUID") from exc
        try:
            execution = await self._executions.get_execution(identifier, tenant_id=tenant)
        except LookupError as exc:
            raise LookupError("execution unavailable") from exc
        actor = _authenticated_actor()
        await self._authorization.require(
            AuthorizationRequest(
                actor=actor,
                tenant_id=tenant,
                namespace=execution.namespace,
                resource_type="execution",
                action=PermissionAction.VIEW,
                audience="amesh-mcp",
            )
        )
        task_runs = await self._executions.list_task_runs(identifier, tenant_id=tenant)
        return {
            "executionId": str(execution.execution_id),
            "tenant": tenant,
            "namespace": execution.namespace,
            "workflowId": execution.flow_id,
            "workflowRevision": execution.flow_revision,
            "state": execution.state.value,
            "createdAt": execution.created_at.isoformat(),
            "updatedAt": execution.updated_at.isoformat(),
            "taskRuns": [
                {
                    "taskRunId": str(task.task_run_id),
                    "taskId": task.task_id,
                    "state": task.state.value,
                    "attempt": task.current_attempt,
                }
                for task in task_runs
            ],
        }

    async def list_agents(
        self,
        tenant: str,
        namespace: str,
        limit: int = 100,
    ) -> dict[str, Any]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        actor = _authenticated_actor()
        await self._authorization.require(
            AuthorizationRequest(
                actor=actor,
                tenant_id=tenant,
                namespace=namespace,
                resource_type="agent",
                action=PermissionAction.LIST,
                audience="amesh-mcp",
            )
        )
        resources = await self._agent_resources.list_resources(
            tenant,
            namespace,
            kind=AgentResourceKind.AGENT,
        )
        return {
            "tenant": tenant,
            "namespace": namespace,
            "agents": [
                {
                    "key": item.key,
                    "revision": item.revision,
                    "digest": item.digest,
                    "title": item.spec.title,
                }
                for item in resources[:limit]
                if isinstance(item.spec, AgentDefinitionSpec)
            ],
        }

    async def inspect_agent(
        self,
        tenant: str,
        namespace: str,
        key: str,
        revision: int,
    ) -> dict[str, Any]:
        actor = _authenticated_actor()
        await self._authorization.require(
            AuthorizationRequest(
                actor=actor,
                tenant_id=tenant,
                namespace=namespace,
                resource_type="agent",
                action=PermissionAction.VIEW,
                audience="amesh-mcp",
            )
        )
        try:
            resource = await self._agent_resources.get_resource(
                tenant,
                namespace,
                AgentResourceKind.AGENT,
                key,
                revision=revision,
            )
        except LookupError as exc:
            raise LookupError("agent definition unavailable") from exc
        if not isinstance(resource.spec, AgentDefinitionSpec):
            raise LookupError("agent definition unavailable")
        return {
            "tenant": tenant,
            "namespace": namespace,
            "key": resource.key,
            "revision": resource.revision,
            "digest": resource.digest,
            "definition": resource.spec.model_dump(mode="json", by_alias=True),
        }


def create_amesh_mcp_server(
    credentials: CredentialService,
    executions: ExecutionRepository,
    agent_resources: AgentResourceRepository,
    authorization: AuthorizationService,
    *,
    base_url: str,
) -> MCPServer[None]:
    root = base_url.rstrip("/")
    server = MCPServer(
        "amesh",
        description=(
            "Read-only, authorization-checked AMESH workflow, execution, and agent inspection."
        ),
        version="1",
        token_verifier=AmeshMcpTokenVerifier(credentials),
        auth=AuthSettings(
            issuer_url=AnyHttpUrl(root + "/"),
            resource_server_url=AnyHttpUrl(root + "/mcp"),
            required_scopes=[],
        ),
    )
    gateway = AmeshMcpReadGateway(executions, agent_resources, authorization)
    read_only = ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    )

    @server.tool(annotations=read_only, structured_output=True)
    async def list_workflows(
        tenant: str,
        namespace: str,
        limit: int = 100,
    ) -> dict[str, Any]:
        """List authorized workflow revisions in one tenant namespace."""

        return await gateway.list_workflows(tenant, namespace, limit)

    @server.tool(annotations=read_only, structured_output=True)
    async def inspect_execution(tenant: str, execution_id: str) -> dict[str, Any]:
        """Inspect one authorized execution and its task-run states without payload data."""

        return await gateway.inspect_execution(tenant, execution_id)

    @server.tool(annotations=read_only, structured_output=True)
    async def list_agents(
        tenant: str,
        namespace: str,
        limit: int = 100,
    ) -> dict[str, Any]:
        """List authorized latest agent-definition revisions in one namespace."""

        return await gateway.list_agents(tenant, namespace, limit)

    @server.tool(annotations=read_only, structured_output=True)
    async def inspect_agent(
        tenant: str,
        namespace: str,
        key: str,
        revision: int,
    ) -> dict[str, Any]:
        """Inspect one exact authorized agent revision and its pinned references."""

        return await gateway.inspect_agent(tenant, namespace, key, revision)

    return server


def create_amesh_mcp_application(server: MCPServer[None], *, base_url: str) -> Starlette:
    parsed = urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("AMESH MCP base URL must be an absolute HTTP(S) URL")
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return server.streamable_http_app(
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=[parsed.netloc],
            allowed_origins=[origin],
        ),
        host=parsed.hostname or "localhost",
    )


def _authenticated_actor() -> ActorContext:
    access_token = get_access_token()
    if access_token is None or access_token.subject is None or access_token.claims is None:
        raise PermissionError("authenticated AMESH MCP credential required")
    claims = access_token.claims
    credential_id = claims.get("credentialId")
    scopes = claims.get("credentialScopes", ())
    if not isinstance(scopes, list) or not all(isinstance(scope, str) for scope in scopes):
        raise PermissionError("invalid AMESH MCP credential claims")
    return ActorContext(
        principal_id=UUID(access_token.subject),
        principal_type=PrincipalType(str(claims["principalType"])),
        display=str(claims["display"]),
        bootstrap_admin=claims.get("bootstrapAdmin") is True,
        credential_id=UUID(str(credential_id)) if credential_id is not None else None,
        credential_scopes=tuple(scopes),
        credential_audience=str(claims.get("credentialAudience", "amesh-mcp")),
    )
