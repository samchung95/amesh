from __future__ import annotations

import asyncio
import json
import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresExecutionRepository,
    PostgresPluginPolicyRepository,
)
from amesh.config import Settings
from amesh.domain import FlowLifecycle
from amesh.domain.plugin_policy import (
    PluginPolicyEffect,
    PluginPolicyRuleCreate,
    PluginPolicyScope,
    PluginPolicySelector,
    PluginPolicyStage,
    PluginQuarantineCreate,
)
from amesh.dsl import FlowDefinition
from amesh.plugin_sdk import PluginResolver
from amesh.plugins import (
    PluginPolicyDenied,
    PluginPolicyService,
    PluginResolutionQuarantined,
    build_plugin_catalog,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_plugin_policy_is_durable_explained_audited_and_enforced(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        settings = Settings()
        catalog = build_plugin_catalog(settings)
        policies = PostgresPluginPolicyRepository(engine)
        service = PluginPolicyService(policies, catalog, default_allow=False)
        executions = PostgresExecutionRepository(
            engine,
            plugin_resolution_provider=lambda flow: (
                PluginResolver(catalog.snapshot).resolve_flow(flow).revision_payload()
            ),
            plugin_policy_enforcer=service.enforce_flow,
        )
        flow = FlowDefinition.model_validate(
            {
                "id": "governed_flow",
                "namespace": "governance.tests",
                "tasks": [{"id": "return", "type": "core.return", "value": "ok"}],
            }
        )
        core = next(
            record.manifest
            for record in catalog.snapshot.packages
            if record.manifest is not None and record.manifest.name == "amesh.core"
        )
        try:
            persisted = await executions.apply_flow(
                flow,
                tenant_id="default",
                actor_id="author",
            )
            revisions = await executions.list_flow_revisions(
                flow.namespace,
                flow.id,
                tenant_id="default",
            )
            assert revisions[0].plugin_resolution["packages"][0]["version"] == core.version
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE flow_revisions SET plugin_resolution = "
                        '\'{"catalogVersion":"amesh.resource-catalog/v1",'
                        '"resources":[{"kind":"task",'
                        '"type":"core.return"}]}\'::jsonb '
                        "WHERE id = CAST(:revision_id AS uuid)"
                    ),
                    {"revision_id": revisions[0].resource_id},
                )
            legacy_decision = await service.evaluate_flow(
                flow,
                tenant_id="default",
                stage=PluginPolicyStage.EXECUTION,
                actor_id="system:scheduler",
            )
            assert legacy_decision.allowed
            assert legacy_decision.subjects[0].subject.package == "amesh.core"
            migrated = await policies.frozen_resolution(
                "default",
                flow.namespace,
                flow.id,
                flow.revision,
            )
            assert migrated is not None
            assert migrated["schemaVersion"] == "amesh.plugin-resolution/v1"
            async with engine.connect() as connection:
                assert (
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM audit_events "
                            "WHERE action = 'plugin.resolution.migrate'"
                        )
                    )
                    == 1
                )

            validation_deny = await policies.create_rule(
                "default",
                PluginPolicyRuleCreate(
                    scope=PluginPolicyScope.NAMESPACE,
                    namespace=flow.namespace,
                    effect=PluginPolicyEffect.DENY,
                    stages=(PluginPolicyStage.VALIDATION,),
                    selector=PluginPolicySelector(package="amesh.core"),
                    reason="validation is temporarily restricted",
                ),
                actor_id="operator",
            )
            tenant_rule = await policies.create_rule(
                "default",
                PluginPolicyRuleCreate(
                    scope=PluginPolicyScope.TENANT,
                    effect=PluginPolicyEffect.ALLOW,
                    stages=(PluginPolicyStage.ADMINISTRATION,),
                    selector=PluginPolicySelector(package="vendor.tenant"),
                    reason="tenant administrator approval",
                ),
                actor_id="operator",
            )
            instance_rule = await policies.create_rule(
                "default",
                PluginPolicyRuleCreate(
                    scope=PluginPolicyScope.INSTANCE,
                    effect=PluginPolicyEffect.DENY,
                    stages=(PluginPolicyStage.EXECUTION,),
                    selector=PluginPolicySelector(package="vendor.revoked"),
                    reason="instance security deny",
                ),
                actor_id="operator",
            )
            await service.enforce_manifest_administration(
                core.model_copy(update={"name": "vendor.tenant"}),
                "sha256:" + "1" * 64,
                tenant_id="default",
                actor_id="operator",
            )
            with pytest.raises(PluginPolicyDenied, match="DEFAULT_POLICY"):
                await service.enforce_manifest_administration(
                    core.model_copy(update={"name": "vendor.unreviewed"}),
                    "sha256:" + "2" * 64,
                    tenant_id="default",
                    actor_id="operator",
                )
            validation = await service.evaluate_flow(
                flow,
                tenant_id="default",
                stage=PluginPolicyStage.VALIDATION,
                actor_id="author",
            )
            authoring = await service.evaluate_flow(
                flow,
                tenant_id="default",
                stage=PluginPolicyStage.AUTHORING,
                actor_id="author",
            )
            assert validation.allowed is False
            assert validation.subjects[0].sources[0].source_id == str(validation_deny.rule_id)
            assert authoring.allowed is True
            reloaded_policy = await PostgresPluginPolicyRepository(engine).effective_policy(
                "default",
                namespace=flow.namespace,
                default_allow=False,
            )
            assert {item.rule_id for item in reloaded_policy.rules} == {
                validation_deny.rule_id,
                tenant_rule.rule_id,
                instance_rule.rule_id,
            }

            quarantine_request = PluginQuarantineCreate(
                scope=PluginPolicyScope.INSTANCE,
                package="amesh.core",
                version=core.version,
                reason="emergency security disable",
            )
            preview = await policies.impact_preview("default", quarantine_request)
            assert preview.affected_flows == (
                {
                    "namespace": flow.namespace,
                    "flow_key": flow.id,
                    "revision": persisted.revision,
                    "status": "ACTIVE",
                    "active": True,
                },
            )
            quarantine = await policies.create_quarantine(
                "default",
                quarantine_request,
                actor_id="operator",
            )
            with pytest.raises(ValueError, match="already has an active quarantine"):
                await policies.create_quarantine(
                    "default",
                    quarantine_request,
                    actor_id="operator",
                )
            with pytest.raises(PluginPolicyDenied, match="PLUGIN_QUARANTINED"):
                await executions.create_execution(
                    flow,
                    tenant_id="default",
                    inputs={},
                    actor_id="runner",
                )
            decisions = await policies.list_decisions("default")
            assert decisions[0].allowed is False
            assert decisions[0].stage is PluginPolicyStage.EXECUTION
            async with engine.connect() as connection:
                violations = int(
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM audit_events "
                            "WHERE action = 'plugin.policy.violation'"
                        )
                    )
                    or 0
                )
            assert violations == 3

            await policies.release_quarantine(
                "default",
                quarantine.quarantine_id,
                actor_id="operator",
                reason="incident remediated",
            )
            execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                actor_id="runner",
            )
            assert execution.flow_revision == persisted.revision
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_unresolvable_legacy_resolution_disables_flow_and_audits_once(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        catalog = build_plugin_catalog(Settings())
        policies = PostgresPluginPolicyRepository(engine)
        service = PluginPolicyService(policies, catalog, default_allow=False)
        executions = PostgresExecutionRepository(
            engine,
            plugin_resolution_provider=lambda flow: (
                PluginResolver(catalog.snapshot).resolve_flow(flow).revision_payload()
            ),
            plugin_policy_enforcer=service.enforce_flow,
        )
        namespace = f"governance.quarantine.{uuid4().hex}"
        valid_flow = FlowDefinition.model_validate(
            {
                "id": "legacy_pin",
                "namespace": namespace,
                "tasks": [{"id": "return", "type": "core.return", "value": "ok"}],
            }
        )
        incompatible_flow = FlowDefinition.model_validate(
            {
                "id": valid_flow.id,
                "namespace": namespace,
                "tasks": [{"id": "missing", "type": "vendor.missing", "payload": {}}],
            }
        )
        legacy = {
            "catalogVersion": "amesh.resource-catalog/v1",
            "resources": [{"kind": "task", "type": "vendor.missing"}],
        }
        try:
            persisted = await executions.apply_flow(valid_flow, tenant_id="default")
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE flow_revisions SET plugin_resolution = CAST(:legacy AS jsonb) "
                        "WHERE flow_id = CAST(:flow_id AS uuid) AND revision = 1"
                    ),
                    {"legacy": json.dumps(legacy), "flow_id": persisted.resource_id},
                )

            for _ in range(2):
                with pytest.raises(PluginResolutionQuarantined):
                    await service.evaluate_flow(
                        incompatible_flow,
                        tenant_id="default",
                        stage=PluginPolicyStage.EXECUTION,
                        actor_id="system:scheduler",
                    )

            quarantined = next(
                item
                for item in await executions.list_flows(tenant_id="default")
                if item.namespace == namespace and item.flow_id == valid_flow.id
            )
            assert quarantined.lifecycle is FlowLifecycle.DISABLED
            async with engine.connect() as connection:
                assert (
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM audit_events "
                            "WHERE action = 'plugin.resolution.quarantine'"
                        )
                    )
                    == 1
                )
        finally:
            await engine.dispose()

    asyncio.run(scenario())
