from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Any, Literal
from urllib.parse import urlsplit
from uuid import UUID

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

from .agent_primitives import McpConnectionRevision, McpToolImpact, ModelProviderSpec
from .identity import NamespaceId, NaturalId, new_runtime_id
from .resources import canonical_hash


class AgentResourceKind(StrEnum):
    PROMPT = "PROMPT"
    SKILL = "SKILL"
    MODEL_POLICY = "MODEL_POLICY"
    AGENT = "AGENT"


class AgentMemoryScope(StrEnum):
    NONE = "NONE"
    EXECUTION = "EXECUTION"
    PRIVATE = "PRIVATE"
    SHARED = "SHARED"


class ModelFallbackMode(StrEnum):
    DISABLED = "DISABLED"
    ORDERED = "ORDERED"


class AgentResourceRef(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: NaturalId
    revision: int = Field(ge=1)


class OrderedPromptRef(AgentResourceRef):
    order: int = Field(ge=0, le=10_000)


class PromptSpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: Literal[AgentResourceKind.PROMPT] = AgentResourceKind.PROMPT
    key: NaturalId
    namespace: NamespaceId
    title: str = Field(min_length=1, max_length=256)
    content: str = Field(min_length=1, max_length=131_072)
    variables: dict[NaturalId, str] = Field(default_factory=dict)


class SkillSpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: Literal[AgentResourceKind.SKILL] = AgentResourceKind.SKILL
    key: NaturalId
    namespace: NamespaceId
    title: str = Field(min_length=1, max_length=256)
    description: str = Field(default="", max_length=4096)
    instructions: str = Field(min_length=1, max_length=131_072)
    requested_capabilities: tuple[NaturalId, ...] = Field(
        default=(),
        alias="requestedCapabilities",
    )

    @field_validator("requested_capabilities")
    @classmethod
    def validate_unique_capabilities(cls, value: tuple[NaturalId, ...]) -> tuple[NaturalId, ...]:
        if len(set(value)) != len(value):
            raise ValueError("skill requestedCapabilities must be unique")
        return value


class ModelRoute(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    route_id: NaturalId = Field(alias="routeId")
    provider: ModelProviderSpec
    model: str = Field(min_length=1, max_length=512)
    required_features: tuple[NaturalId, ...] = Field(default=(), alias="requiredFeatures")
    parameters: dict[str, Any] = Field(default_factory=dict)


class ModelPolicySpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: Literal[AgentResourceKind.MODEL_POLICY] = AgentResourceKind.MODEL_POLICY
    key: NaturalId
    namespace: NamespaceId
    title: str = Field(min_length=1, max_length=256)
    routes: tuple[ModelRoute, ...] = Field(min_length=1)
    fallback_mode: ModelFallbackMode = Field(
        default=ModelFallbackMode.DISABLED,
        alias="fallbackMode",
    )
    output_nondeterminism_disclosure: str = Field(
        alias="outputNondeterminismDisclosure",
        min_length=1,
        max_length=4096,
    )

    @model_validator(mode="after")
    def validate_routes(self) -> ModelPolicySpec:
        route_ids = tuple(route.route_id for route in self.routes)
        if len(set(route_ids)) != len(route_ids):
            raise ValueError("model-policy routeId values must be unique")
        if self.fallback_mode is ModelFallbackMode.DISABLED and len(self.routes) != 1:
            raise ValueError("fallbackMode DISABLED requires exactly one route")
        return self


class AgentToolRef(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    connection_key: NaturalId = Field(alias="connectionKey")
    connection_revision: int = Field(alias="connectionRevision", ge=1)
    tool_name: NaturalId = Field(alias="toolName")
    schema_digest: str = Field(alias="schemaDigest", pattern=r"^sha256:[0-9a-f]{64}$")


class AgentMemoryPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    scope: AgentMemoryScope = AgentMemoryScope.NONE
    max_bytes: int = Field(default=0, alias="maxBytes", ge=0, le=100_000_000)
    retention_seconds: int = Field(
        default=0,
        alias="retentionSeconds",
        ge=0,
        le=31_536_000,
    )
    redact: bool = True

    @model_validator(mode="after")
    def validate_disabled_memory(self) -> AgentMemoryPolicy:
        if self.scope is AgentMemoryScope.NONE and (self.max_bytes or self.retention_seconds):
            raise ValueError("memory scope NONE requires zero size and retention")
        if self.scope is not AgentMemoryScope.NONE and self.max_bytes == 0:
            raise ValueError("enabled memory requires maxBytes")
        return self


class AgentPermissions(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    delegated_capabilities: tuple[NaturalId, ...] = Field(
        default=(),
        alias="delegatedCapabilities",
    )
    tool_allowlist: tuple[NaturalId, ...] = Field(default=(), alias="toolAllowlist")
    secret_scopes: tuple[NaturalId, ...] = Field(default=(), alias="secretScopes")
    network_hosts: tuple[str, ...] = Field(default=(), alias="networkHosts")
    filesystem_read_roots: tuple[str, ...] = Field(
        default=(),
        alias="filesystemReadRoots",
    )
    filesystem_write_roots: tuple[str, ...] = Field(
        default=(),
        alias="filesystemWriteRoots",
    )
    allow_high_impact_tools: bool = Field(default=False, alias="allowHighImpactTools")

    @field_validator(
        "delegated_capabilities",
        "tool_allowlist",
        "secret_scopes",
        "network_hosts",
        "filesystem_read_roots",
        "filesystem_write_roots",
    )
    @classmethod
    def validate_unique_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("capability boundary values must be unique")
        return value

    @field_validator("network_hosts")
    @classmethod
    def validate_network_hosts(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for host in value:
            parsed = urlsplit(host if "://" in host else f"https://{host}")
            if not parsed.hostname or parsed.username or parsed.password or parsed.path not in {"", "/"}:
                raise ValueError("networkHosts must contain credential-free hosts, not URLs or paths")
        return value


class AgentHardLimits(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    max_total_tokens: int = Field(alias="maxTotalTokens", ge=1)
    max_cost_usd: Decimal = Field(alias="maxCostUsd", ge=0)
    max_duration_seconds: int = Field(alias="maxDurationSeconds", ge=1, le=86_400)
    max_tool_calls: int = Field(alias="maxToolCalls", ge=0, le=10_000)
    max_turns: int = Field(alias="maxTurns", ge=1, le=10_000)
    max_loop_iterations: int = Field(alias="maxLoopIterations", ge=0, le=10_000)
    max_recursion_depth: int = Field(alias="maxRecursionDepth", ge=0, le=100)
    max_concurrency: int = Field(alias="maxConcurrency", ge=1, le=1_000)


class AgentEvaluationPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    required_evaluations: tuple[NaturalId, ...] = Field(
        default=(),
        alias="requiredEvaluations",
    )
    require_human_release: bool = Field(default=False, alias="requireHumanRelease")


def _validate_json_schema(value: dict[str, Any]) -> dict[str, Any]:
    try:
        Draft202012Validator.check_schema(value)
    except SchemaError as exc:
        raise ValueError(f"invalid Draft 2020-12 schema: {exc.message}") from exc
    return value


class AgentDefinitionSpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: Literal[AgentResourceKind.AGENT] = AgentResourceKind.AGENT
    key: NaturalId
    namespace: NamespaceId
    title: str = Field(min_length=1, max_length=256)
    description: str = Field(default="", max_length=4096)
    instructions: str = Field(min_length=1, max_length=131_072)
    input_schema: dict[str, Any] = Field(alias="inputSchema")
    output_schema: dict[str, Any] = Field(alias="outputSchema")
    model_policy: AgentResourceRef = Field(alias="modelPolicy")
    prompts: tuple[OrderedPromptRef, ...] = ()
    skills: tuple[AgentResourceRef, ...] = ()
    tools: tuple[AgentToolRef, ...] = ()
    memory_policy: AgentMemoryPolicy = Field(alias="memoryPolicy")
    permissions: AgentPermissions
    hard_limits: AgentHardLimits = Field(alias="hardLimits")
    evaluation_policy: AgentEvaluationPolicy = Field(alias="evaluationPolicy")

    @field_validator("input_schema", "output_schema")
    @classmethod
    def validate_schema(cls, value: dict[str, Any]) -> dict[str, Any]:
        return _validate_json_schema(value)

    @model_validator(mode="after")
    def validate_references(self) -> AgentDefinitionSpec:
        prompt_keys = tuple((ref.key, ref.revision) for ref in self.prompts)
        skill_keys = tuple((ref.key, ref.revision) for ref in self.skills)
        orders = tuple(ref.order for ref in self.prompts)
        tools = tuple((ref.connection_key, ref.connection_revision, ref.tool_name) for ref in self.tools)
        if len(set(prompt_keys)) != len(prompt_keys):
            raise ValueError("prompt revision references must be unique")
        if len(set(skill_keys)) != len(skill_keys):
            raise ValueError("skill revision references must be unique")
        if len(set(orders)) != len(orders):
            raise ValueError("prompt composition order values must be unique")
        if len(set(tools)) != len(tools):
            raise ValueError("agent tool revision references must be unique")
        if set(self.permissions.tool_allowlist) != {tool.tool_name for tool in self.tools}:
            raise ValueError("permissions.toolAllowlist must exactly match declared tools")
        return self


AgentResourceSpec = Annotated[
    PromptSpec | SkillSpec | ModelPolicySpec | AgentDefinitionSpec,
    Field(discriminator="kind"),
]
AGENT_RESOURCE_ADAPTER: TypeAdapter[AgentResourceSpec] = TypeAdapter(AgentResourceSpec)


class AgentResourceRevision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    resource_id: UUID = Field(default_factory=new_runtime_id, alias="resourceId")
    tenant_id: str = Field(alias="tenantId")
    namespace: NamespaceId
    kind: AgentResourceKind
    key: NaturalId
    revision: int = Field(ge=1)
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    spec: AgentResourceSpec
    created_by: str = Field(alias="createdBy", min_length=1, max_length=255)
    created_at: datetime = Field(alias="createdAt")

    @model_validator(mode="after")
    def validate_kind(self) -> AgentResourceRevision:
        if self.kind is not self.spec.kind:
            raise ValueError("resource revision kind must match its spec kind")
        if self.namespace != self.spec.namespace or self.key != self.spec.key:
            raise ValueError("resource revision identity must match its spec")
        return self


class ResolvedResourcePin(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    resource_id: UUID = Field(alias="resourceId")
    kind: AgentResourceKind
    key: NaturalId
    revision: int = Field(ge=1)
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class ResolvedToolPin(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    connection_id: UUID = Field(alias="connectionId")
    connection_key: NaturalId = Field(alias="connectionKey")
    connection_revision: int = Field(alias="connectionRevision", ge=1)
    connection_digest: str = Field(alias="connectionDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    tool_name: NaturalId = Field(alias="toolName")
    schema_digest: str = Field(alias="schemaDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    impact: McpToolImpact


class InstructionFragment(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    source_kind: str = Field(alias="sourceKind")
    source_key: str = Field(alias="sourceKey")
    order: int
    content: str


class EffectiveCapabilityEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: Literal["amesh.agent-envelope/v1"] = Field(
        default="amesh.agent-envelope/v1",
        alias="schemaVersion",
    )
    agent: ResolvedResourcePin
    resources: tuple[ResolvedResourcePin, ...]
    instructions: tuple[InstructionFragment, ...]
    prompt_variables: dict[str, str] = Field(alias="promptVariables")
    model_routes: tuple[ModelRoute, ...] = Field(alias="modelRoutes")
    fallback_mode: ModelFallbackMode = Field(alias="fallbackMode")
    output_nondeterminism_disclosure: str = Field(alias="outputNondeterminismDisclosure")
    tools: tuple[ResolvedToolPin, ...]
    input_schema: dict[str, Any] = Field(alias="inputSchema")
    output_schema: dict[str, Any] = Field(alias="outputSchema")
    memory_policy: AgentMemoryPolicy = Field(alias="memoryPolicy")
    permissions: AgentPermissions
    hard_limits: AgentHardLimits = Field(alias="hardLimits")
    evaluation_policy: AgentEvaluationPolicy = Field(alias="evaluationPolicy")

    @property
    def digest(self) -> str:
        return "sha256:" + canonical_hash(self)


class AgentResolutionRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    agent_revision: int = Field(alias="agentRevision", ge=1)
    subject_ref: str = Field(alias="subjectRef", min_length=1, max_length=512)


class AgentCapabilityPin(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    pin_id: UUID = Field(default_factory=new_runtime_id, alias="pinId")
    tenant_id: str = Field(alias="tenantId")
    namespace: NamespaceId
    subject_ref: str = Field(alias="subjectRef")
    envelope_digest: str = Field(alias="envelopeDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    envelope: EffectiveCapabilityEnvelope
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(alias="createdAt")


class AgentRevisionComparison(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    from_revision: int = Field(alias="fromRevision")
    to_revision: int = Field(alias="toRevision")
    same_input_schema: bool = Field(alias="sameInputSchema")
    same_output_schema: bool = Field(alias="sameOutputSchema")
    added_prompts: tuple[str, ...] = Field(alias="addedPrompts")
    removed_prompts: tuple[str, ...] = Field(alias="removedPrompts")
    added_skills: tuple[str, ...] = Field(alias="addedSkills")
    removed_skills: tuple[str, ...] = Field(alias="removedSkills")
    added_tools: tuple[str, ...] = Field(alias="addedTools")
    removed_tools: tuple[str, ...] = Field(alias="removedTools")
    model_policy_changed: bool = Field(alias="modelPolicyChanged")
    nondeterminism_disclosure: str = Field(alias="nondeterminismDisclosure")


class ProviderMigrationDiagnostic(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    state_schema_changed: bool = Field(default=False, alias="stateSchemaChanged")
    provider_routes_changed: bool = Field(alias="providerRoutesChanged")
    removed_routes: tuple[str, ...] = Field(alias="removedRoutes")
    added_routes: tuple[str, ...] = Field(alias="addedRoutes")
    output_nondeterministic: bool = Field(default=True, alias="outputNondeterministic")
    disclosure: str

    @model_validator(mode="after")
    def validate_portability_boundary(self) -> ProviderMigrationDiagnostic:
        if self.state_schema_changed:
            raise ValueError("provider migration cannot change the durable state schema")
        if not self.output_nondeterministic:
            raise ValueError("provider migration must disclose output nondeterminism")
        return self


def agent_resource_digest(spec: AgentResourceSpec) -> str:
    return "sha256:" + canonical_hash(spec)


def resolved_resource_pin(revision: AgentResourceRevision) -> ResolvedResourcePin:
    return ResolvedResourcePin(
        resourceId=revision.resource_id,
        kind=revision.kind,
        key=revision.key,
        revision=revision.revision,
        digest=revision.digest,
    )


def resolve_capability_envelope(
    agent: AgentResourceRevision,
    model_policy: AgentResourceRevision,
    prompts: tuple[AgentResourceRevision, ...],
    skills: tuple[AgentResourceRevision, ...],
    connections: tuple[McpConnectionRevision, ...],
) -> EffectiveCapabilityEnvelope:
    if not isinstance(agent.spec, AgentDefinitionSpec):
        raise ValueError("agent resource must contain an AGENT definition")
    definition = agent.spec
    if not isinstance(model_policy.spec, ModelPolicySpec):
        raise ValueError("model-policy reference did not resolve to MODEL_POLICY")
    if (model_policy.key, model_policy.revision) != (
        definition.model_policy.key,
        definition.model_policy.revision,
    ):
        raise ValueError("resolved model-policy revision does not match the agent reference")
    prompt_by_ref = {(item.key, item.revision): item for item in prompts}
    skill_by_ref = {(item.key, item.revision): item for item in skills}
    connection_by_ref = {(item.spec.key, item.revision): item for item in connections}
    if set(prompt_by_ref) != {(ref.key, ref.revision) for ref in definition.prompts}:
        raise LookupError("one or more exact prompt revisions are unavailable")
    if set(skill_by_ref) != {(ref.key, ref.revision) for ref in definition.skills}:
        raise LookupError("one or more exact skill revisions are unavailable")

    allowed_secrets = set(definition.permissions.secret_scopes)
    allowed_hosts = set(definition.permissions.network_hosts)
    for route in model_policy.spec.routes:
        if route.provider.credential_ref not in allowed_secrets:
            raise PermissionError(
                f"model route {route.route_id!r} credential is outside secretScopes"
            )
        route_host = urlsplit(route.provider.endpoint).hostname
        if route_host not in allowed_hosts:
            raise PermissionError(
                f"model route {route.route_id!r} endpoint is outside networkHosts"
            )

    fragments = [InstructionFragment(sourceKind="AGENT", sourceKey=agent.key, order=-1, content=definition.instructions)]
    variables: dict[str, str] = {}
    for prompt_ref in sorted(definition.prompts, key=lambda item: (item.order, item.key)):
        revision = prompt_by_ref[(prompt_ref.key, prompt_ref.revision)]
        if not isinstance(revision.spec, PromptSpec):
            raise ValueError(f"prompt reference {prompt_ref.key!r} resolved to the wrong kind")
        for name, value in revision.spec.variables.items():
            if name in variables and variables[name] != value:
                raise ValueError(f"prompt variable {name!r} has conflicting values")
            variables[name] = value
        fragments.append(
            InstructionFragment(
                sourceKind="PROMPT",
                sourceKey=prompt_ref.key,
                order=prompt_ref.order,
                content=revision.spec.content,
            )
        )

    delegated = set(definition.permissions.delegated_capabilities)
    skill_offset = 20_000
    for index, skill_ref in enumerate(
        sorted(definition.skills, key=lambda item: (item.key, item.revision))
    ):
        revision = skill_by_ref[(skill_ref.key, skill_ref.revision)]
        if not isinstance(revision.spec, SkillSpec):
            raise ValueError(f"skill reference {skill_ref.key!r} resolved to the wrong kind")
        missing = set(revision.spec.requested_capabilities) - delegated
        if missing:
            raise PermissionError(
                f"skill {skill_ref.key!r} requests undelegated capabilities: "
                f"{', '.join(sorted(missing))}"
            )
        fragments.append(
            InstructionFragment(
                sourceKind="SKILL",
                sourceKey=skill_ref.key,
                order=skill_offset + index,
                content=revision.spec.instructions,
            )
        )

    resolved_tools: list[ResolvedToolPin] = []
    for reference in definition.tools:
        connection = connection_by_ref.get((reference.connection_key, reference.connection_revision))
        if connection is None:
            raise LookupError(
                f"MCP connection {reference.connection_key}@{reference.connection_revision} unavailable"
            )
        if connection.spec.credential_ref not in definition.permissions.secret_scopes:
            raise PermissionError(
                f"connection {reference.connection_key!r} credential is outside secretScopes"
            )
        connection_host = urlsplit(connection.spec.endpoint).hostname
        if connection_host not in allowed_hosts:
            raise PermissionError(
                f"connection {reference.connection_key!r} endpoint is outside networkHosts"
            )
        tool = connection.spec.pinned_tool(reference.tool_name)
        if tool.schema_digest != reference.schema_digest:
            raise ValueError(f"tool schema pin changed for {reference.tool_name!r}")
        if tool.impact is McpToolImpact.HIGH_IMPACT and not definition.permissions.allow_high_impact_tools:
            raise PermissionError(f"high-impact tool {reference.tool_name!r} is not delegated")
        resolved_tools.append(
            ResolvedToolPin(
                connectionId=connection.connection_id,
                connectionKey=connection.spec.key,
                connectionRevision=connection.revision,
                connectionDigest=connection.digest,
                toolName=tool.name,
                schemaDigest=tool.schema_digest,
                impact=tool.impact,
            )
        )

    ordered_resources = (
        model_policy,
        *(prompt_by_ref[(ref.key, ref.revision)] for ref in definition.prompts),
        *(skill_by_ref[(ref.key, ref.revision)] for ref in definition.skills),
    )
    return EffectiveCapabilityEnvelope(
        agent=resolved_resource_pin(agent),
        resources=tuple(resolved_resource_pin(item) for item in ordered_resources),
        instructions=tuple(fragments),
        promptVariables=variables,
        modelRoutes=model_policy.spec.routes,
        fallbackMode=model_policy.spec.fallback_mode,
        outputNondeterminismDisclosure=model_policy.spec.output_nondeterminism_disclosure,
        tools=tuple(resolved_tools),
        inputSchema=definition.input_schema,
        outputSchema=definition.output_schema,
        memoryPolicy=definition.memory_policy,
        permissions=definition.permissions,
        hardLimits=definition.hard_limits,
        evaluationPolicy=definition.evaluation_policy,
    )


def compare_agent_revisions(
    previous: AgentResourceRevision,
    current: AgentResourceRevision,
) -> AgentRevisionComparison:
    if not isinstance(previous.spec, AgentDefinitionSpec) or not isinstance(current.spec, AgentDefinitionSpec):
        raise ValueError("agent comparison requires two AGENT revisions")
    old_prompts = {f"{item.key}@{item.revision}" for item in previous.spec.prompts}
    new_prompts = {f"{item.key}@{item.revision}" for item in current.spec.prompts}
    old_skills = {f"{item.key}@{item.revision}" for item in previous.spec.skills}
    new_skills = {f"{item.key}@{item.revision}" for item in current.spec.skills}
    old_tools = {f"{item.connection_key}@{item.connection_revision}:{item.tool_name}" for item in previous.spec.tools}
    new_tools = {f"{item.connection_key}@{item.connection_revision}:{item.tool_name}" for item in current.spec.tools}
    return AgentRevisionComparison(
        fromRevision=previous.revision,
        toRevision=current.revision,
        sameInputSchema=previous.spec.input_schema == current.spec.input_schema,
        sameOutputSchema=previous.spec.output_schema == current.spec.output_schema,
        addedPrompts=tuple(sorted(new_prompts - old_prompts)),
        removedPrompts=tuple(sorted(old_prompts - new_prompts)),
        addedSkills=tuple(sorted(new_skills - old_skills)),
        removedSkills=tuple(sorted(old_skills - new_skills)),
        addedTools=tuple(sorted(new_tools - old_tools)),
        removedTools=tuple(sorted(old_tools - new_tools)),
        modelPolicyChanged=previous.spec.model_policy != current.spec.model_policy,
        nondeterminismDisclosure=(
            "Model output is nondeterministic. Re-resolution never rewrites an existing pin."
        ),
    )


def provider_migration_diagnostic(
    previous: ModelPolicySpec,
    current: ModelPolicySpec,
) -> ProviderMigrationDiagnostic:
    old_routes = {f"{route.route_id}:{route.provider.adapter}:{route.model}" for route in previous.routes}
    new_routes = {f"{route.route_id}:{route.provider.adapter}:{route.model}" for route in current.routes}
    return ProviderMigrationDiagnostic(
        providerRoutesChanged=old_routes != new_routes,
        removedRoutes=tuple(sorted(old_routes - new_routes)),
        addedRoutes=tuple(sorted(new_routes - old_routes)),
        disclosure=current.output_nondeterminism_disclosure,
    )
