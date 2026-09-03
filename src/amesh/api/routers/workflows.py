"""Cohesive workflows API definitions extracted from the composition root."""

from __future__ import annotations

import hashlib
import json
from collections.abc import AsyncIterator, Mapping
from typing import Annotated
from uuid import UUID

import yaml
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi import Path as PathParameter
from starlette.responses import StreamingResponse

from amesh.adapters.postgres.human_task_repository import (
    HumanTaskConflict,
    WorkflowAppVersionConflict,
)
from amesh.admission_policy import AdmissionPolicyService, policy_input_from_flow
from amesh.api.contracts import (
    CollectionQuery,
    collection_response,
)
from amesh.api.dependencies import (
    ActorDependency,
    AdmissionPolicyServiceDependency,
    AuthorizationServiceDependency,
    FlowTestRepositoryDependency,
    HumanTaskRepositoryDependency,
    HumanTaskServiceDependency,
    NamespaceResourceServiceDependency,
    OperationalControlRepositoryDependency,
    PluginCatalogDependency,
    PluginPolicyServiceDependency,
    ReadRepositoryDependency,
    RepositoryDependency,
    SettingsDependency,
    SharedResourceRepositoryDependency,
    TaskCacheRepositoryDependency,
    TenantDependency,
    authorize_request,
)
from amesh.api.models import (
    BlueprintDraftResponse,
    CreateExecutionRequest,
    ExecutionDetail,
    ExpressionPreviewRequest,
    ExpressionPreviewResponse,
    FlowDataContract,
    FlowDocumentExport,
    FlowEditorSchemaResponse,
    FlowFormatResponse,
    FlowGraph,
    FlowMetadataResponse,
    FlowRevisionLifecycleRequest,
    FlowRevisionRestoreRequest,
    KestraExecutionRequest,
    NamespaceFileMoveRequest,
    NamespaceResourceImportResult,
    PlaygroundSafety,
    PlaygroundSimulationRequest,
    PlaygroundSimulationResponse,
    PlaygroundStep,
)
from amesh.api.route_support import (
    _build_flow_graph,
    _execute_flow,
)
from amesh.api.routers.executions import (
    create_execution,
)
from amesh.compatibility.kestra import (
    KestraFlowImport,
    compatibility_manifest,
    import_kestra_flow,
)
from amesh.config import (
    Settings,
)
from amesh.determinism import DeterminismPolicyPin
from amesh.domain import (
    ActorContext,
    ArtifactRef,
    AuthorizationRequest,
    BlueprintCatalogSource,
    BlueprintDefinition,
    BlueprintInstantiationRequest,
    BlueprintSummary,
    FlowLifecycle,
    FlowRevisionDiff,
    FlowRevisionRecord,
    FlowRevisionSource,
    FlowTestDefinition,
    FlowTestDefinitionCreateRequest,
    FlowTestQualityGate,
    FlowTestQualityGateUpdate,
    FlowTestRunRequest,
    FlowTestRunResult,
    ImageArtifactRef,
    KeyValueChange,
    KeyValueEntry,
    KeyValueWrite,
    NamespaceFile,
    NamespaceFileVersion,
    NamespaceResourceBundle,
    OperationalBoundary,
    PermissionAction,
    PluginPolicyDecision,
    PluginPolicyStage,
    PolicyDecision,
    PolicyEvaluationRequest,
    PolicyStage,
    PrincipalType,
    ResourceVersionConflict,
    SecretBinding,
    SecretBindingWrite,
    ServiceRole,
    canonical_hash,
    get_blueprint,
    instantiate_blueprint,
    list_blueprints,
)
from amesh.domain.flow_revisions import compare_flow_revisions
from amesh.domain.human_tasks import (
    HumanTask,
    HumanTaskActionRequest,
    HumanTaskNotification,
    WorkflowApp,
    WorkflowAppLaunchRequest,
    WorkflowAppSpec,
    WorkflowAppUpsertRequest,
    form_from_flow,
)
from amesh.dsl import (
    FlowDefinition,
    FlowDocumentError,
    FlowValidationResult,
    compile_execution_tasks,
    validate_flow_document,
)
from amesh.expressions import NativeExpressionEngine
from amesh.expressions.contracts import ExpressionError
from amesh.flow_testing import FlowTestService
from amesh.plugin_sdk import (
    PluginContractError,
)
from amesh.ports import (
    ExecutionLaunchSource,
    FlowTestVersionConflict,
    PersistedFlow,
    TaskStateConflictError,
)
from amesh.simulation import (
    SimulationComparison,
    SimulationPlan,
    SimulationPolicyDecision,
    SimulationRequest,
    compare_simulation_plans,
    simulate_flow,
)
from amesh.workflow.data_contracts import (
    DataContractError,
    flow_input_contract,
)
from amesh.workflow.metadata import (
    NamespaceWorkflowMetadata,
    NamespaceWorkflowMetadataUpdate,
    NamespaceWorkflowMetadataView,
)

router_1 = APIRouter()


router_2 = APIRouter()


_EDITOR_CONTEXT_KEYS = frozenset(
    {
        "flow",
        "execution",
        "task",
        "taskrun",
        "trigger",
        "inputs",
        "outputs",
        "vars",
        "labels",
        "namespace",
        "iteration",
        "error",
    }
)


_SENSITIVE_EDITOR_KEY_PARTS = frozenset(
    {"password", "secret", "token", "credential", "api_key", "apikey"}
)


def _redact_editor_context(context: Mapping[str, object]) -> dict[str, object]:
    def sanitize(value: object) -> object:
        if isinstance(value, Mapping):
            return {
                str(key): (
                    "[REDACTED]"
                    if any(
                        part in str(key).lower().replace("-", "_")
                        for part in _SENSITIVE_EDITOR_KEY_PARTS
                    )
                    else sanitize(item)
                )
                for key, item in value.items()
            }
        if isinstance(value, list | tuple):
            return [sanitize(item) for item in value]
        return value

    return {key: sanitize(value) for key, value in context.items() if key in _EDITOR_CONTEXT_KEYS}


def _playground_flow(fragment: str) -> dict[str, object]:
    try:
        loaded = yaml.safe_load(fragment)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid playground YAML: {exc}") from exc
    if isinstance(loaded, list):
        document: dict[str, object] = {"tasks": loaded}
    elif isinstance(loaded, dict) and "tasks" in loaded:
        document = dict(loaded)
    elif isinstance(loaded, dict) and {"id", "type"} <= loaded.keys():
        document = {"tasks": [loaded]}
    else:
        raise ValueError("flow fragment must be a task, a task list, or a flow with tasks")
    document.setdefault("apiVersion", "amesh.flow/v1")
    document.setdefault("id", "playground_preview")
    document.setdefault("namespace", "playground.local")
    return document


def _playground_steps(document: Mapping[str, object]) -> tuple[PlaygroundStep, ...]:
    tasks = document.get("tasks", [])
    if not isinstance(tasks, list):
        return ()
    deterministic_types = {"core.log", "core.return"}
    return tuple(
        PlaygroundStep(
            taskId=str(task.get("id", "unknown")),
            taskType=str(task.get("type", "unknown")),
            dependencies=tuple(str(value) for value in task.get("dependsOn", [])),
            simulated=task.get("type") in deterministic_types,
            reason=(
                "deterministic local preview"
                if task.get("type") in deterministic_types
                else "validated only; the playground never invokes this resource"
            ),
        )
        for task in tasks
        if isinstance(task, dict)
    )


@router_1.get(
    "/api/v1/blueprints",
    response_model=tuple[BlueprintSummary, ...],
    tags=["blueprints"],
)
async def get_blueprints(
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    q: Annotated[str | None, Query(max_length=200)] = None,
    source: BlueprintCatalogSource | None = None,
) -> tuple[BlueprintSummary, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return list_blueprints(query=q, source=source)


@router_1.get(
    "/api/v1/blueprints/{blueprint_id}/{version}",
    response_model=BlueprintDefinition,
    tags=["blueprints"],
)
async def get_blueprint_version(
    blueprint_id: str,
    version: str,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> BlueprintDefinition:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        return get_blueprint(blueprint_id, version)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.post(
    "/api/v1/blueprints/{blueprint_id}/{version}/instantiate",
    response_model=BlueprintDraftResponse,
    tags=["blueprints"],
)
async def instantiate_blueprint_draft(
    blueprint_id: str,
    version: str,
    request: BlueprintInstantiationRequest,
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> BlueprintDraftResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.CREATE,
        tenant_id=tenant_id,
    )
    try:
        blueprint = get_blueprint(blueprint_id, version)
        document = instantiate_blueprint(blueprint, request)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    source = yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
    validation = validate_flow_document(source, registry=plugin_catalog.resource_registry())
    if not validation.valid:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="the selected blueprint produced an invalid draft",
        )
    return BlueprintDraftResponse(
        blueprint=blueprint,
        document=source,
        validation=validation,
    )


@router_1.post(
    "/api/v1/playground/simulate",
    response_model=PlaygroundSimulationResponse,
    tags=["blueprints"],
)
async def simulate_playground(
    request: PlaygroundSimulationRequest,
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PlaygroundSimulationResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    engine = NativeExpressionEngine()
    context = _redact_editor_context(request.context)
    expression_result: object = None
    if request.expression and request.expression.strip():
        try:
            expression_result = engine.preview_value(request.expression, context)
        except ExpressionError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": exc.code, "message": str(exc)},
            ) from exc
    validation: FlowValidationResult | None = None
    steps: tuple[PlaygroundStep, ...] = ()
    if request.fragment and request.fragment.strip():
        try:
            document = _playground_flow(request.fragment)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        validation = validate_flow_document(
            document,
            registry=plugin_catalog.resource_registry(),
        )
        steps = _playground_steps(document)
    return PlaygroundSimulationResponse(
        expressionResult=expression_result,
        redactedContext=context,
        validation=validation,
        steps=steps,
        safety=PlaygroundSafety(),
        compatibilityVersion=engine.compatibility_version,
    )


@router_1.post(
    "/api/v1/flows/validate",
    response_model=FlowValidationResult,
    tags=["flows"],
)
async def validate_flow(
    request: Request,
    plugin_catalog: PluginCatalogDependency,
) -> FlowValidationResult:
    maximum_bytes = 2 * 1024 * 1024
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            declared_length = int(content_length)
        except ValueError:
            declared_length = None
        if declared_length is not None and declared_length > maximum_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="flow document exceeds the 2 MiB foundation limit",
            )
    chunks: list[bytes] = []
    received_bytes = 0
    async for chunk in request.stream():
        received_bytes += len(chunk)
        if received_bytes > maximum_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="flow document exceeds the 2 MiB foundation limit",
            )
        chunks.append(chunk)
    body = b"".join(chunks)
    try:
        return validate_flow_document(body, registry=plugin_catalog.resource_registry())
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router_1.get(
    "/api/v1/compatibility/kestra/manifest",
    tags=["compatibility"],
)
async def get_kestra_compatibility_manifest() -> dict[str, object]:
    return compatibility_manifest()


@router_1.post(
    "/api/v1/main/flows/validate",
    response_model=KestraFlowImport,
    tags=["compatibility"],
)
async def validate_kestra_flow(request: Request) -> KestraFlowImport:
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="flow document exceeds the 2 MiB compatibility limit",
        )
    try:
        return import_kestra_flow(body)
    except (FlowDocumentError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router_1.get(
    "/api/v1/flows/editor/schema",
    response_model=FlowEditorSchemaResponse,
    tags=["flows"],
)
async def get_flow_editor_schema(
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowEditorSchemaResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return FlowEditorSchemaResponse(
        schemaVersion="amesh.flow-editor/v1",
        flowSchema=FlowDefinition.model_json_schema(by_alias=True),
        resourceCatalog=plugin_catalog.resource_registry().catalog(),
        expressionContext={
            "flow": "Current flow metadata.",
            "execution": "Execution identity, state and timing.",
            "task": "Current task definition.",
            "taskrun": "Current task-run state and attempt.",
            "trigger": "Trigger payload and metadata.",
            "inputs": "Validated flow inputs.",
            "outputs": "Completed task outputs by task ID.",
            "vars": "Flow variables.",
            "labels": "Execution and flow labels.",
            "namespace": "Namespace-scoped public context.",
            "iteration": "Loop iteration context.",
            "error": "Current failure context.",
        },
    )


@router_1.post(
    "/api/v1/flows/format",
    response_model=FlowFormatResponse,
    tags=["flows"],
)
async def format_flow(
    request: Request,
    plugin_catalog: PluginCatalogDependency,
) -> FlowFormatResponse:
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="flow document exceeds the 2 MiB foundation limit",
        )
    try:
        validation = validate_flow_document(
            body,
            registry=plugin_catalog.resource_registry(),
        )
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    document = None
    if validation.valid and validation.canonical is not None:
        document = yaml.safe_dump(
            validation.canonical,
            allow_unicode=True,
            sort_keys=False,
        )
    return FlowFormatResponse(document=document, validation=validation)


@router_1.post(
    "/api/v1/flows/expressions/preview",
    response_model=ExpressionPreviewResponse,
    tags=["flows"],
)
async def preview_flow_expression(
    request: ExpressionPreviewRequest,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ExpressionPreviewResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    context = _redact_editor_context(request.context)
    engine = NativeExpressionEngine()
    try:
        result = engine.preview_value(request.expression, context)
    except ExpressionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    return ExpressionPreviewResponse(
        result=result,
        redactedContext=context,
        compatibilityVersion=engine.compatibility_version,
    )


@router_1.get(
    "/api/v1/apps",
    response_model=list[WorkflowApp],
    tags=["apps"],
)
async def list_workflow_apps(
    repository: HumanTaskRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
) -> list[WorkflowApp]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="app",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(await repository.list_apps(tenant_id=tenant_id, namespace=namespace))


@router_1.get(
    "/api/v1/apps/{namespace}/{app_id}",
    response_model=WorkflowApp,
    tags=["apps"],
)
async def get_workflow_app(
    namespace: str,
    app_id: str,
    repository: HumanTaskRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> WorkflowApp:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="app",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.get_app(
            namespace,
            app_id,
            tenant_id=tenant_id,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.put(
    "/api/v1/apps/{namespace}/{app_id}",
    response_model=WorkflowApp,
    tags=["apps"],
)
async def upsert_workflow_app(
    namespace: str,
    app_id: Annotated[str, PathParameter(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")],
    request: WorkflowAppUpsertRequest,
    repository: HumanTaskRepositoryDependency,
    execution_repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> WorkflowApp:
    try:
        await repository.get_app(namespace, app_id, tenant_id=tenant_id)
    except LookupError:
        action = PermissionAction.CREATE
    else:
        action = PermissionAction.UPDATE
    await authorize_request(
        authorization_service,
        actor,
        resource_type="app",
        action=action,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.USE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await execution_repository.get_flow(
            namespace,
            request.flow_id,
            tenant_id=tenant_id,
            revision=request.flow_revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    form = request.form or form_from_flow(flow)
    flow_input_ids = {definition.id for definition in flow.inputs}
    form_input_ids = {field.id for field in form.fields}
    unknown = sorted(form_input_ids - flow_input_ids)
    required_missing = sorted(
        definition.id
        for definition in flow.inputs
        if definition.required
        and not definition.has_default
        and definition.id not in form_input_ids
    )
    if unknown or required_missing:
        details = []
        if unknown:
            details.append("unknown form fields: " + ", ".join(unknown))
        if required_missing:
            details.append("required flow inputs missing from form: " + ", ".join(required_missing))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="; ".join(details),
        )
    resolved = WorkflowAppSpec.model_validate(
        {
            **request.model_dump(mode="json", by_alias=True, exclude={"expected_version"}),
            "flowRevision": flow.revision,
            "form": form.model_dump(mode="json", by_alias=True),
        }
    )
    try:
        return await repository.upsert_app(
            namespace,
            app_id,
            resolved,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=request.expected_version,
        )
    except WorkflowAppVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc


@router_1.post(
    "/api/v1/apps/{namespace}/{app_id}/launch",
    response_model=ExecutionDetail,
    tags=["apps"],
)
async def launch_workflow_app(
    namespace: str,
    app_id: str,
    request: WorkflowAppLaunchRequest,
    background_tasks: BackgroundTasks,
    repository: HumanTaskRepositoryDependency,
    execution_repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> ExecutionDetail:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="app",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        workflow_app = await repository.get_app(namespace, app_id, tenant_id=tenant_id)
        flow = await execution_repository.get_flow(
            namespace,
            workflow_app.flow_id,
            tenant_id=tenant_id,
            revision=workflow_app.flow_revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    launch_request = CreateExecutionRequest(
        namespace=namespace,
        flowId=workflow_app.flow_id,
        inputs=request.inputs,
        idempotencyKey=request.idempotency_key,
    )
    return await _execute_flow(
        execution_repository,
        task_cache,
        flow,
        launch_request,
        settings,
        operational_controls=operational_controls,
        shared_resources=shared_resources,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        actor=actor,
        authorization_service=authorization_service,
        background_tasks=background_tasks,
        launch_source=ExecutionLaunchSource.API,
        idempotency_key=request.idempotency_key,
        respond_async=True,
    )


@router_1.get(
    "/api/v1/human-tasks",
    response_model=list[HumanTask],
    tags=["human-tasks"],
)
async def list_human_tasks(
    repository: HumanTaskRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    namespace: str | None = None,
    include_closed: Annotated[bool, Query(alias="includeClosed")] = False,
) -> list[HumanTask]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="human_task",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    manage = await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=namespace,
            resource_type="human_task",
            action=PermissionAction.MANAGE,
        )
    )
    return list(
        await repository.list_tasks(
            actor.principal_id,
            tenant_id=tenant_id,
            namespace=namespace,
            include_closed=include_closed,
            include_all=manage.allowed,
        )
    )


@router_1.post(
    "/api/v1/human-tasks/{human_task_id}/actions",
    response_model=HumanTask,
    tags=["human-tasks"],
)
async def act_on_human_task(
    human_task_id: UUID,
    request: HumanTaskActionRequest,
    repository: HumanTaskRepositoryDependency,
    service: HumanTaskServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> HumanTask:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="human_task",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    try:
        task = await repository.get_task(
            human_task_id,
            actor.principal_id,
            tenant_id=tenant_id,
            include_all=True,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await authorize_request(
        authorization_service,
        actor,
        resource_type="human_task",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=task.namespace,
    )
    manage = await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=task.namespace,
            resource_type="human_task",
            action=PermissionAction.MANAGE,
        )
    )
    if not manage.allowed:
        try:
            await repository.get_task(
                human_task_id,
                actor.principal_id,
                tenant_id=tenant_id,
            )
        except LookupError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    try:
        return await service.apply_action(
            human_task_id,
            request,
            tenant_id=tenant_id,
            actor_id=actor.principal_id,
        )
    except (HumanTaskConflict, TaskStateConflictError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_1.get(
    "/api/v1/human-task-notifications",
    response_model=list[HumanTaskNotification],
    tags=["human-tasks"],
)
async def list_human_task_notifications(
    repository: HumanTaskRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[HumanTaskNotification]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="human_task",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return list(
        await repository.list_notifications(
            actor.principal_id,
            tenant_id=tenant_id,
            limit=limit,
        )
    )


@router_1.put(
    "/api/v1/flows",
    response_model=PersistedFlow,
    tags=["flows"],
)
async def apply_flow(
    request: Request,
    response: Response,
    repository: RepositoryDependency,
    plugin_catalog: PluginCatalogDependency,
    operational_controls: OperationalControlRepositoryDependency,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
    revision_source: Annotated[str | None, Header(alias="X-AMESH-Source")] = None,
    source_commit: Annotated[str | None, Header(alias="X-AMESH-Commit")] = None,
    environment: Annotated[str | None, Header(alias="X-AMESH-Environment")] = None,
    deployment: Annotated[str | None, Header(alias="X-AMESH-Deployment")] = None,
) -> PersistedFlow:
    try:
        result = validate_flow_document(
            await request.body(),
            registry=plugin_catalog.resource_registry(),
        )
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if not result.valid or result.canonical is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[issue.model_dump(mode="json", by_alias=True) for issue in result.issues],
        )
    flow = FlowDefinition.model_validate(result.canonical)
    authoring_decision = await operational_controls.evaluate(
        OperationalBoundary.AUTHORING,
        tenant_id=tenant_id,
        namespace=flow.namespace,
        flow_id=flow.id,
        plugin_ids=tuple(node.task.type for node in compile_execution_tasks(flow)),
        component_id="webserver:flow-authoring",
        component_role=ServiceRole.WEBSERVER.value,
    )
    if authoring_decision.blocked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "message": "authoring blocked by operational control",
                "boundary": OperationalBoundary.AUTHORING.value,
                "controlIds": [str(control.control_id) for control in authoring_decision.controls],
            },
        )
    existing_revision: int | None = None
    try:
        existing = await repository.get_flow(flow.namespace, flow.id, tenant_id=tenant_id)
    except LookupError:
        write_action = PermissionAction.CREATE
    else:
        existing_revision = existing.revision
        write_action = PermissionAction.UPDATE
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=write_action,
        tenant_id=tenant_id,
        namespace=flow.namespace,
    )
    if flow.system:
        await authorize_request(
            authorization_service,
            actor,
            resource_type="tenant",
            action=PermissionAction.MANAGE,
            tenant_id=tenant_id,
        )
    try:
        persisted = await repository.apply_flow(
            flow,
            tenant_id=tenant_id,
            expected_etag=if_match,
            actor_id=str(actor.principal_id),
            revision_source=FlowRevisionSource(
                source=revision_source,
                source_commit=source_commit,
                environment=environment,
                deployment={"reference": deployment} if deployment is not None else {},
            ),
        )
        gate = await flow_tests.get_gate(flow.namespace, tenant_id=tenant_id)
        if (
            gate is not None
            and gate.enabled
            and (existing_revision is None or persisted.revision > existing_revision)
        ):
            persisted = await repository.promote_flow_revision(
                flow.namespace,
                flow.id,
                persisted.revision,
                FlowLifecycle.DRAFT,
                tenant_id=tenant_id,
                actor_id=str(actor.principal_id),
                reason="namespace flow-test gate requires passing tests before ACTIVE promotion",
            )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc
    except PluginContractError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[error.model_dump(mode="json") for error in exc.errors],
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    response.headers["ETag"] = persisted.etag
    return persisted


@router_1.get(
    "/api/v1/flows",
    response_model=list[PersistedFlow],
    tags=["flows"],
)
async def list_flows(
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    query: Annotated[CollectionQuery, Depends()],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
    )
    return collection_response(await repository.list_flows(tenant_id=tenant_id), query)


@router_1.get(
    "/api/v1/flows/{namespace}/{flow_id}/document",
    response_model=FlowDocumentExport,
    tags=["flows"],
)
async def export_flow_document(
    namespace: str,
    flow_id: str,
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> FlowDocumentExport:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    document = (
        json.loads(flow._persisted_canonical_definition)
        if flow._persisted_canonical_definition is not None
        else flow.model_dump(mode="json", by_alias=True, exclude_none=True)
    )
    return FlowDocumentExport(
        namespace=flow.namespace,
        flowId=flow.id,
        revision=flow.revision,
        semanticHash=flow._persisted_semantic_hash or canonical_hash(document),
        document=document,
    )


@router_1.put(
    "/api/v1/namespaces/{namespace}/workflow-metadata",
    response_model=NamespaceWorkflowMetadata,
    tags=["namespaces"],
)
async def upsert_namespace_workflow_metadata(
    namespace: str,
    request: NamespaceWorkflowMetadataUpdate,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceWorkflowMetadata:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.upsert_namespace_workflow_metadata(
            namespace,
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/workflow-metadata",
    response_model=NamespaceWorkflowMetadataView,
    tags=["namespaces"],
)
async def get_namespace_workflow_metadata(
    namespace: str,
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceWorkflowMetadataView:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.get_namespace_workflow_metadata(
        namespace,
        tenant_id=tenant_id,
    )


@router_1.get(
    "/api/v1/flows/{namespace}/{flow_id}/metadata",
    response_model=FlowMetadataResponse,
    tags=["flows"],
)
async def get_flow_metadata(
    namespace: str,
    flow_id: str,
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowMetadataResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    persisted = next(
        (
            item
            for item in await repository.list_flows(tenant_id=tenant_id)
            if item.namespace == namespace and item.flow_id == flow_id
        ),
        None,
    )
    if persisted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="flow not found")
    revisions = await repository.list_flow_revisions(
        namespace,
        flow_id,
        tenant_id=tenant_id,
    )
    revision = next(item for item in revisions if item.revision == persisted.revision)
    return FlowMetadataResponse(
        namespace=namespace,
        flowId=flow_id,
        revision=persisted.revision,
        labels=persisted.metadata.labels,
        pluginResolution=revision.plugin_resolution,
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/files",
    response_model=list[NamespaceFile],
    tags=["namespace-resources"],
)
async def list_namespace_files(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    inherited: bool = True,
) -> list[NamespaceFile]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_files(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        inherited=inherited,
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/artifacts",
    response_model=list[ArtifactRef],
    tags=["namespace-resources"],
)
async def list_namespace_artifacts(
    namespace: str,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    inherited: bool = True,
) -> list[ArtifactRef]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await service.list_artifacts(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        inherited=inherited,
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/artifacts/{path:path}",
    response_model=ArtifactRef,
    tags=["namespace-resources"],
)
async def get_namespace_artifact(
    namespace: str,
    path: str,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    version: Annotated[int | None, Query(ge=1)] = None,
) -> ArtifactRef:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.READ,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await service.get_artifact(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            version=version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router_1.put(
    "/api/v1/namespaces/{namespace}/images/{path:path}",
    response_model=ImageArtifactRef,
    tags=["namespace-resources"],
)
async def upload_namespace_image(
    namespace: str,
    path: str,
    request: Request,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=0)] = None,
    alt_text: Annotated[
        str | None,
        Query(alias="altText", min_length=1, max_length=1024),
    ] = None,
) -> ImageArtifactRef:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await service.upload_image(
            namespace,
            path,
            await request.body(),
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            content_type=request.headers.get("content-type"),
            expected_version=expected_version,
            alt_text=alt_text,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/images/{path:path}",
    response_model=ImageArtifactRef,
    tags=["namespace-resources"],
)
async def get_namespace_image(
    namespace: str,
    path: str,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    version: Annotated[int | None, Query(ge=1)] = None,
    alt_text: Annotated[
        str | None,
        Query(alias="altText", min_length=1, max_length=1024),
    ] = None,
) -> ImageArtifactRef:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.READ,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await service.get_image_artifact(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            version=version,
            alt_text=alt_text,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router_1.put(
    "/api/v1/namespaces/{namespace}/files/{path:path}",
    response_model=NamespaceFile,
    tags=["namespace-resources"],
)
async def upload_namespace_file(
    namespace: str,
    path: str,
    request: Request,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=0)] = None,
) -> NamespaceFile:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await service.upload_file(
            namespace,
            path,
            await request.body(),
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            content_type=request.headers.get("content-type"),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/files/{path:path}/versions",
    response_model=list[NamespaceFileVersion],
    tags=["namespace-resources"],
)
async def list_namespace_file_versions(
    namespace: str,
    path: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[NamespaceFileVersion]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_file_versions(
        namespace,
        path,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
    )


@router_1.post(
    "/api/v1/namespaces/{namespace}/files/{path:path}/move",
    response_model=NamespaceFile,
    tags=["namespace-resources"],
)
async def move_namespace_file(
    namespace: str,
    path: str,
    request: NamespaceFileMoveRequest,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceFile:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.move_file(
            namespace,
            path,
            request.destination_path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=request.expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/files/{path:path}",
    response_class=StreamingResponse,
    tags=["namespace-resources"],
)
async def download_namespace_file(
    namespace: str,
    path: str,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    version: Annotated[int | None, Query(ge=1)] = None,
) -> StreamingResponse:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.READ,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        selected, content = await service.download_file(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            version=version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    async def chunks() -> AsyncIterator[bytes]:
        yield content

    return StreamingResponse(
        chunks(),
        media_type=selected.content_type or "application/octet-stream",
        headers={
            "ETag": f'"sha256:{selected.checksum_sha256}"',
            "X-Amesh-File-Version": str(selected.version),
            "X-Content-Type-Options": "nosniff",
        },
    )


@router_1.delete(
    "/api/v1/namespaces/{namespace}/files/{path:path}",
    tags=["namespace-resources"],
)
async def delete_namespace_file(
    namespace: str,
    path: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=0)] = None,
) -> dict[str, int]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="namespace_file",
        action=PermissionAction.DELETE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        version = await repository.delete_file(
            namespace,
            path,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    return {"resourceVersion": version}


@router_1.get(
    "/api/v1/namespaces/{namespace}/key-values",
    response_model=list[KeyValueEntry],
    tags=["namespace-resources"],
)
async def list_namespace_key_values(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[KeyValueEntry]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="key_value",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_key_values(
        namespace, tenant_id=tenant_id, actor_id=str(actor.principal_id)
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/key-values/changes",
    response_model=list[KeyValueChange],
    tags=["namespace-resources"],
)
async def list_namespace_key_value_changes(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    after: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[KeyValueChange]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="key_value",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_key_value_changes(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        after=after,
        limit=limit,
    )


@router_1.put(
    "/api/v1/namespaces/{namespace}/key-values/{key}",
    response_model=KeyValueEntry,
    tags=["namespace-resources"],
)
async def put_namespace_key_value(
    namespace: str,
    key: str,
    write: KeyValueWrite,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> KeyValueEntry:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="key_value",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.put_key_value(
            namespace,
            key,
            write,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc


@router_1.get(
    "/api/v1/namespaces/{namespace}/key-values/{key}",
    response_model=KeyValueEntry,
    tags=["namespace-resources"],
)
async def get_namespace_key_value(
    namespace: str,
    key: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> KeyValueEntry:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="key_value",
        action=PermissionAction.READ,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.get_key_value(
            namespace, key, tenant_id=tenant_id, actor_id=str(actor.principal_id)
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.delete(
    "/api/v1/namespaces/{namespace}/key-values/{key}",
    tags=["namespace-resources"],
)
async def delete_namespace_key_value(
    namespace: str,
    key: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> dict[str, bool]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="key_value",
        action=PermissionAction.DELETE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        deleted = await repository.delete_key_value(
            namespace,
            key,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    return {"deleted": deleted}


@router_1.get(
    "/api/v1/namespaces/{namespace}/secret-bindings",
    response_model=list[SecretBinding],
    tags=["namespace-resources"],
)
async def list_namespace_secret_bindings(
    namespace: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    inherited: bool = True,
) -> list[SecretBinding]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="secret",
        action=PermissionAction.LIST,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_secret_bindings(
        namespace,
        tenant_id=tenant_id,
        actor_id=str(actor.principal_id),
        inherited=inherited,
    )


@router_1.put(
    "/api/v1/namespaces/{namespace}/secret-bindings/{key}",
    response_model=SecretBinding,
    tags=["namespace-resources"],
)
async def put_namespace_secret_binding(
    namespace: str,
    key: str,
    write: SecretBindingWrite,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SecretBinding:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="secret",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.put_secret_binding(
            namespace,
            key,
            write,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc


@router_1.delete(
    "/api/v1/namespaces/{namespace}/secret-bindings/{key}",
    tags=["namespace-resources"],
)
async def delete_namespace_secret_binding(
    namespace: str,
    key: str,
    repository: SharedResourceRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int | None, Query(alias="expectedVersion", ge=1)] = None,
) -> dict[str, bool]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="secret",
        action=PermissionAction.WRITE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        deleted = await repository.delete_secret_binding(
            namespace,
            key,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except ResourceVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    return {"deleted": deleted}


@router_1.get(
    "/api/v1/namespaces/{namespace}/resource-bundle",
    response_model=NamespaceResourceBundle,
    tags=["namespace-resources"],
)
async def export_namespace_resource_bundle(
    namespace: str,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceResourceBundle:
    for resource_type, action in (
        ("namespace_file", PermissionAction.READ),
        ("key_value", PermissionAction.READ),
        ("secret", PermissionAction.LIST),
    ):
        await authorize_request(
            authorization_service,
            actor,
            resource_type=resource_type,
            action=action,
            tenant_id=tenant_id,
            namespace=namespace,
        )
    return await service.export_bundle(
        namespace, tenant_id=tenant_id, actor_id=str(actor.principal_id)
    )


@router_1.post(
    "/api/v1/namespaces/{namespace}/resource-bundle",
    response_model=NamespaceResourceImportResult,
    tags=["namespace-resources"],
)
async def import_namespace_resource_bundle(
    namespace: str,
    bundle: NamespaceResourceBundle,
    service: NamespaceResourceServiceDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> NamespaceResourceImportResult:
    for resource_type in ("namespace_file", "key_value", "secret"):
        await authorize_request(
            authorization_service,
            actor,
            resource_type=resource_type,
            action=PermissionAction.WRITE,
            tenant_id=tenant_id,
            namespace=namespace,
        )
    try:
        result = await service.import_bundle(
            namespace,
            bundle,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return NamespaceResourceImportResult.model_validate(result)


@router_1.get(
    "/api/v1/flows/{namespace}/{flow_id}/revisions",
    response_model=list[FlowRevisionRecord],
    tags=["flows"],
)
async def list_flow_revisions(
    namespace: str,
    flow_id: str,
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> list[FlowRevisionRecord]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await repository.list_flow_revisions(namespace, flow_id, tenant_id=tenant_id)


@router_1.put(
    "/api/v1/flows/{namespace}/{flow_id}/tests",
    response_model=FlowTestDefinition,
    tags=["flow-tests"],
)
async def save_flow_test(
    namespace: str,
    flow_id: str,
    request: FlowTestDefinitionCreateRequest,
    repository: RepositoryDependency,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowTestDefinition:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=(
            PermissionAction.CREATE if request.expected_version is None else PermissionAction.UPDATE
        ),
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await FlowTestService(repository, flow_tests).save_definition(
            namespace,
            flow_id,
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FlowTestVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router_1.get(
    "/api/v1/flows/{namespace}/{flow_id}/tests",
    response_model=list[FlowTestDefinition],
    tags=["flow-tests"],
)
async def list_flow_tests(
    namespace: str,
    flow_id: str,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> list[FlowTestDefinition]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(
        await flow_tests.list_definitions(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
    )


@router_1.delete(
    "/api/v1/flows/{namespace}/{flow_id}/tests/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["flow-tests"],
)
async def delete_flow_test(
    namespace: str,
    flow_id: str,
    test_id: str,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int, Query(alias="expectedVersion", ge=1)],
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        await flow_tests.delete_definition(
            namespace,
            flow_id,
            test_id,
            tenant_id=tenant_id,
            expected_version=expected_version,
            actor_id=str(actor.principal_id),
        )
    except FlowTestVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router_1.post(
    "/api/v1/flows/{namespace}/{flow_id}/tests/runs",
    response_model=FlowTestRunResult,
    tags=["flow-tests"],
)
async def run_flow_tests(
    namespace: str,
    flow_id: str,
    request: FlowTestRunRequest,
    repository: RepositoryDependency,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int, Query(ge=1)],
) -> FlowTestRunResult:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.EXECUTE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await FlowTestService(repository, flow_tests).run(
            namespace,
            flow_id,
            revision,
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.get(
    "/api/v1/flows/{namespace}/{flow_id}/tests/runs",
    response_model=list[FlowTestRunResult],
    tags=["flow-tests"],
)
async def list_flow_test_runs(
    namespace: str,
    flow_id: str,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[FlowTestRunResult]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return list(
        await flow_tests.list_runs(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
            limit=limit,
        )
    )


@router_1.get(
    "/api/v1/namespaces/{namespace}/flow-test-gate",
    response_model=FlowTestQualityGate | None,
    tags=["flow-tests"],
)
async def get_flow_test_gate(
    namespace: str,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowTestQualityGate | None:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    return await flow_tests.get_gate(namespace, tenant_id=tenant_id)


@router_1.put(
    "/api/v1/namespaces/{namespace}/flow-test-gate",
    response_model=FlowTestQualityGate,
    tags=["flow-tests"],
)
async def update_flow_test_gate(
    namespace: str,
    request: FlowTestQualityGateUpdate,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowTestQualityGate:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow_test",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await flow_tests.upsert_gate(
            namespace,
            request,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except FlowTestVersionConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(exc),
        ) from exc


@router_1.get(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/diff",
    response_model=FlowRevisionDiff,
    tags=["flows"],
)
async def diff_flow_revisions(
    namespace: str,
    flow_id: str,
    repository: ReadRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    from_revision: Annotated[int, Query(alias="from", ge=1)],
    to_revision: Annotated[int, Query(alias="to", ge=1)],
) -> FlowRevisionDiff:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.diff_flow_revisions(
            namespace,
            flow_id,
            from_revision,
            to_revision,
            tenant_id=tenant_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.post(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/diff-draft",
    response_model=FlowRevisionDiff,
    tags=["flows"],
)
async def diff_flow_draft(
    namespace: str,
    flow_id: str,
    revision: int,
    request: Request,
    repository: ReadRepositoryDependency,
    plugin_catalog: PluginCatalogDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowRevisionDiff:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="flow document exceeds the 2 MiB foundation limit",
        )
    try:
        validation = validate_flow_document(
            body,
            registry=plugin_catalog.resource_registry(),
        )
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if not validation.valid or validation.canonical is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[issue.model_dump(mode="json", by_alias=True) for issue in validation.issues],
        )
    try:
        stored = await repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    before = (
        json.loads(stored._persisted_canonical_definition)
        if stored._persisted_canonical_definition is not None
        else stored.model_dump(mode="json", by_alias=True, exclude_none=True)
    )
    draft_revision = validation.canonical.get("revision", revision)
    return compare_flow_revisions(
        before,
        validation.canonical,
        from_revision=revision,
        to_revision=(
            draft_revision if isinstance(draft_revision, int) and draft_revision >= 1 else revision
        ),
    )


@router_1.post(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/simulate",
    response_model=SimulationPlan,
    tags=["simulations"],
)
async def simulate_flow_revision(
    namespace: str,
    flow_id: str,
    revision: int,
    request: SimulationRequest,
    repository: ReadRepositoryDependency,
    policy: PluginPolicyServiceDependency,
    admission_policy: AdmissionPolicyServiceDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> SimulationPlan:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
        revisions = await repository.list_flow_revisions(
            namespace,
            flow_id,
            tenant_id=tenant_id,
        )
        record = next(item for item in revisions if item.revision == revision)
        plugin_decision = await policy.preview_flow(
            flow,
            tenant_id=tenant_id,
            stage=PluginPolicyStage.EXECUTION,
            resolution_payload=record.plugin_resolution,
        )
        admission_decision = await _preview_simulation_admission_policy(
            admission_policy,
            flow,
            request,
            actor,
            tenant_id,
        )
    except (LookupError, StopIteration) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return simulate_flow(
        flow,
        request,
        semantic_hash=record.semantic_hash,
        plugin_set=record.plugin_resolution,
        tenant_id=tenant_id,
        policy_decisions=(_simulation_plugin_policy(plugin_decision),),
        determinism_policy_pins=_simulation_admission_policy_pins(admission_decision),
        signing_key=_simulation_signing_key(settings),
        signing_key_id="amesh-server/simulation-v1",
    )


@router_1.post(
    "/api/v1/flows/{namespace}/{flow_id}/simulations/compare",
    response_model=SimulationComparison,
    tags=["simulations"],
)
async def compare_flow_simulations(
    namespace: str,
    flow_id: str,
    request: SimulationRequest,
    repository: ReadRepositoryDependency,
    policy: PluginPolicyServiceDependency,
    admission_policy: AdmissionPolicyServiceDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    from_revision: Annotated[int, Query(alias="from", ge=1)],
    to_revision: Annotated[int, Query(alias="to", ge=1)],
) -> SimulationComparison:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        before_flow = await repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=from_revision,
        )
        after_flow = await repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=to_revision,
        )
        revisions = await repository.list_flow_revisions(
            namespace,
            flow_id,
            tenant_id=tenant_id,
        )
        records = {item.revision: item for item in revisions}
        before_record = records[from_revision]
        after_record = records[to_revision]
        before_policy = await policy.preview_flow(
            before_flow,
            tenant_id=tenant_id,
            stage=PluginPolicyStage.EXECUTION,
            resolution_payload=before_record.plugin_resolution,
        )
        after_policy = await policy.preview_flow(
            after_flow,
            tenant_id=tenant_id,
            stage=PluginPolicyStage.EXECUTION,
            resolution_payload=after_record.plugin_resolution,
        )
        before_admission = await _preview_simulation_admission_policy(
            admission_policy,
            before_flow,
            request,
            actor,
            tenant_id,
        )
        after_admission = await _preview_simulation_admission_policy(
            admission_policy,
            after_flow,
            request,
            actor,
            tenant_id,
        )
    except (KeyError, LookupError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    signing_key = _simulation_signing_key(settings)
    before = simulate_flow(
        before_flow,
        request,
        semantic_hash=before_record.semantic_hash,
        plugin_set=before_record.plugin_resolution,
        tenant_id=tenant_id,
        policy_decisions=(_simulation_plugin_policy(before_policy),),
        determinism_policy_pins=_simulation_admission_policy_pins(before_admission),
        signing_key=signing_key,
        signing_key_id="amesh-server/simulation-v1",
    )
    after = simulate_flow(
        after_flow,
        request,
        semantic_hash=after_record.semantic_hash,
        plugin_set=after_record.plugin_resolution,
        tenant_id=tenant_id,
        policy_decisions=(_simulation_plugin_policy(after_policy),),
        determinism_policy_pins=_simulation_admission_policy_pins(after_admission),
        signing_key=signing_key,
        signing_key_id="amesh-server/simulation-v1",
    )
    return SimulationComparison(
        before=before,
        after=after,
        diff=compare_simulation_plans(before, after),
    )


@router_1.put(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/lifecycle",
    response_model=PersistedFlow,
    tags=["flows"],
)
async def promote_flow_revision(
    namespace: str,
    flow_id: str,
    revision: int,
    request: FlowRevisionLifecycleRequest,
    repository: RepositoryDependency,
    flow_tests: FlowTestRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PersistedFlow:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        if request.lifecycle is FlowLifecycle.ACTIVE:
            decision = await FlowTestService(repository, flow_tests).gate_decision(
                namespace,
                flow_id,
                revision,
                tenant_id=tenant_id,
            )
            if not decision.allowed:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "FLOW_TEST_GATE_FAILED",
                        "reason": decision.reason,
                        "decision": decision.model_dump(mode="json", by_alias=True),
                    },
                )
        return await repository.promote_flow_revision(
            namespace,
            flow_id,
            revision,
            request.lifecycle,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            reason=request.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_1.post(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/restore",
    response_model=PersistedFlow,
    tags=["flows"],
)
async def restore_flow_revision(
    namespace: str,
    flow_id: str,
    revision: int,
    request: FlowRevisionRestoreRequest,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> PersistedFlow:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        return await repository.restore_flow_revision(
            namespace,
            flow_id,
            revision,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            reason=request.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router_1.delete(
    "/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["flows"],
)
async def delete_flow_revision(
    namespace: str,
    flow_id: str,
    revision: int,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> Response:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.UPDATE,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        await repository.delete_flow_revision(
            namespace,
            flow_id,
            revision,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router_1.get(
    "/api/v1/flows/{namespace}/{flow_id}/graph",
    response_model=FlowGraph,
    tags=["flows"],
)
async def get_flow_graph(
    namespace: str,
    flow_id: str,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowGraph:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await repository.get_flow(namespace, flow_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _build_flow_graph(flow)


@router_1.get(
    "/api/v1/flows/{namespace}/{flow_id}/data-contract",
    response_model=FlowDataContract,
    tags=["flows"],
)
async def get_flow_data_contract(
    namespace: str,
    flow_id: str,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> FlowDataContract:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="flow",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    try:
        flow = await repository.get_flow(namespace, flow_id, tenant_id=tenant_id)
        return FlowDataContract(
            namespace=flow.namespace,
            flowId=flow.id,
            revision=flow.revision,
            inputSchema=flow_input_contract(flow),
            outputs=flow.outputs,
            variables=flow.variables,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DataContractError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


def _simulation_signing_key(settings: Settings) -> bytes:
    source = settings.webhook_signing_key.get_secret_value().encode("utf-8")
    return hashlib.sha256(b"amesh-simulation-signing-v1\0" + source).digest()


def _simulation_plugin_policy(decision: PluginPolicyDecision) -> SimulationPolicyDecision:
    return SimulationPolicyDecision(
        category="PLUGIN",
        policyId=str(decision.decision_id),
        allowed=decision.allowed,
        reason=(
            "resolved plugin set is allowed by execution policy"
            if decision.allowed
            else "resolved plugin set is denied by execution policy"
        ),
        details={
            "stage": decision.stage.value,
            "subjects": [item.model_dump(mode="json", by_alias=True) for item in decision.subjects],
        },
    )


async def _preview_simulation_admission_policy(
    service: AdmissionPolicyService,
    flow: FlowDefinition,
    request: SimulationRequest,
    actor: ActorContext,
    tenant_id: str,
) -> PolicyDecision:
    runtime_actor = ActorContext(
        principal_id=actor.principal_id,
        principal_type=PrincipalType.SYSTEM,
        display=str(actor.principal_id),
    )
    return await service.evaluate(
        PolicyEvaluationRequest(
            stage=PolicyStage.LAUNCH,
            input=policy_input_from_flow(
                flow,
                tenant_id=tenant_id,
                actor=runtime_actor,
                inputs=dict(request.inputs),
            ),
        ),
        record=False,
    )


def _simulation_admission_policy_pins(
    decision: PolicyDecision,
) -> tuple[DeterminismPolicyPin, ...]:
    return tuple(
        DeterminismPolicyPin(
            category="ADMISSION",
            key=item.policy_key,
            revision=item.revision,
            digest=item.digest,
        )
        for item in decision.pinned_policies
    )


@router_2.post(
    "/api/v1/executions/{namespace}/{flow_id}",
    response_model=ExecutionDetail,
    responses={
        status.HTTP_202_ACCEPTED: {
            "model": ExecutionDetail,
            "description": "Execution persisted and accepted for asynchronous processing",
        }
    },
    tags=["compatibility"],
)
async def create_kestra_execution(
    namespace: str,
    flow_id: str,
    request: KestraExecutionRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    repository: RepositoryDependency,
    task_cache: TaskCacheRepositoryDependency,
    shared_resources: SharedResourceRepositoryDependency,
    operational_controls: OperationalControlRepositoryDependency,
    settings: SettingsDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    prefer: Annotated[str | None, Header(alias="Prefer")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-ID")] = None,
) -> ExecutionDetail:
    return await create_execution(
        CreateExecutionRequest(
            namespace=namespace,
            flowId=flow_id,
            inputs=request.inputs,
            runner=request.runner,
            idempotencyKey=request.idempotency_key,
        ),
        background_tasks,
        response,
        repository,
        task_cache,
        shared_resources,
        operational_controls,
        settings,
        actor,
        authorization_service,
        tenant_id,
        prefer,
        idempotency_key,
        correlation_id,
    )
