"""Flow quality HTTP routes."""

from __future__ import annotations

import hashlib
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)

from amesh.admission_policy import AdmissionPolicyService, policy_input_from_flow
from amesh.api.dependencies import (
    ActorDependency,
    AdmissionPolicyServiceDependency,
    AuthorizationServiceDependency,
    FlowTestRepositoryDependency,
    PluginCatalogDependency,
    PluginPolicyServiceDependency,
    ReadRepositoryDependency,
    RepositoryDependency,
    SettingsDependency,
    TenantDependency,
    authorize_request,
    require_namespace_permission,
)
from amesh.config import (
    Settings,
)
from amesh.determinism import DeterminismPolicyPin
from amesh.domain import (
    ActorContext,
    FlowRevisionDiff,
    FlowTestDefinition,
    FlowTestDefinitionCreateRequest,
    FlowTestQualityGate,
    FlowTestQualityGateUpdate,
    FlowTestRunRequest,
    FlowTestRunResult,
    PermissionAction,
    PluginPolicyDecision,
    PluginPolicyStage,
    PolicyDecision,
    PolicyEvaluationRequest,
    PolicyStage,
    PrincipalType,
)
from amesh.domain.flow_revisions import compare_flow_revisions
from amesh.dsl import (
    FlowDefinition,
    FlowDocumentError,
    validate_flow_document,
)
from amesh.platform import FlowTestService
from amesh.ports import (
    FlowTestVersionConflict,
)
from amesh.simulation import (
    SimulationComparison,
    SimulationPlan,
    SimulationPolicyDecision,
    SimulationRequest,
    compare_simulation_plans,
    simulate_flow,
)

router_1 = APIRouter()


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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow_test", PermissionAction.VIEW))
    ],
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
) -> list[FlowTestDefinition]:
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow_test", PermissionAction.UPDATE))
    ],
    tenant_id: TenantDependency,
    expected_version: Annotated[int, Query(alias="expectedVersion", ge=1)],
) -> Response:
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow_test", PermissionAction.EXECUTE))
    ],
    tenant_id: TenantDependency,
    revision: Annotated[int, Query(ge=1)],
) -> FlowTestRunResult:
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow_test", PermissionAction.VIEW))
    ],
    tenant_id: TenantDependency,
    revision: Annotated[int | None, Query(ge=1)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[FlowTestRunResult]:
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow_test", PermissionAction.VIEW))
    ],
    tenant_id: TenantDependency,
) -> FlowTestQualityGate | None:
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow_test", PermissionAction.UPDATE))
    ],
    tenant_id: TenantDependency,
) -> FlowTestQualityGate:
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow", PermissionAction.VIEW))
    ],
    tenant_id: TenantDependency,
    from_revision: Annotated[int, Query(alias="from", ge=1)],
    to_revision: Annotated[int, Query(alias="to", ge=1)],
) -> FlowRevisionDiff:
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow", PermissionAction.VIEW))
    ],
    tenant_id: TenantDependency,
) -> FlowRevisionDiff:
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
        persisted_revision = await repository.get_flow_revision(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    before = persisted_revision.document()
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow", PermissionAction.VIEW))
    ],
    tenant_id: TenantDependency,
) -> SimulationPlan:
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
    actor: Annotated[
        ActorContext, Depends(require_namespace_permission("flow", PermissionAction.VIEW))
    ],
    tenant_id: TenantDependency,
    from_revision: Annotated[int, Query(alias="from", ge=1)],
    to_revision: Annotated[int, Query(alias="to", ge=1)],
) -> SimulationComparison:
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
