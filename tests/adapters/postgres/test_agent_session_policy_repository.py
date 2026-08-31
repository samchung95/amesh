from __future__ import annotations

import asyncio
import os
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresAgentSessionPolicyRepository
from amesh.domain import AgentSessionPolicy
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
)
from amesh.ports import AgentSessionPolicyVersionConflict

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_session_policy_revisions_are_versioned_audited_and_tenant_scoped() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        repository = PostgresAgentSessionPolicyRepository(engine)
        policy = AgentSessionPolicy(
            admissionEnabled=True,
            maxConcurrency=4,
            maxTotalTokens=50_000,
            maxCostUsd=Decimal("5.00"),
            maxDurationSeconds=1_800,
            retentionSeconds=86_400,
            allowedProviderIds=("openai",),
            allowedHarnessIds=("pi",),
            allowedToolIds=("search",),
        )
        try:
            await apply_migrations(database.database_url, MIGRATIONS)
            first = await repository.save_revision(
                "default",
                policy,
                namespace="research",
                actor_id="policy-admin",
                expected_revision=0,
            )
            second = await repository.save_revision(
                "default",
                policy.model_copy(update={"maxConcurrency": 8}),
                namespace="research",
                actor_id="policy-admin",
                expected_revision=first.revision,
            )
            assert (first.revision, second.revision) == (1, 2)
            assert first.policy_id == second.policy_id
            assert (await repository.get_revision("default", namespace="research")).revision == 2
            assert (
                await repository.get_revision("default", namespace="research", revision=1)
            ).spec.max_concurrency == 4

            with pytest.raises(AgentSessionPolicyVersionConflict):
                await repository.save_revision(
                    "default",
                    policy,
                    namespace="research",
                    actor_id="stale-admin",
                    expected_revision=1,
                )

            tenant_policy = await repository.save_revision(
                "default",
                policy,
                actor_id="policy-admin",
                expected_revision=0,
            )
            effective = await repository.effective_revisions("default", namespace="research")
            assert [item.namespace for item in effective] == [None, "research"]
            assert effective[0].policy_id == tenant_policy.policy_id

            application_policy = await repository.save_revision(
                "default",
                policy,
                namespace="research",
                application_id="billing",
                actor_id="policy-admin",
                expected_revision=0,
            )
            application_effective = await repository.effective_revisions(
                "default", namespace="research", application_id="billing"
            )
            assert [item.application_id for item in application_effective] == [
                None,
                None,
                "billing",
            ]
            assert application_effective[-1].policy_id == application_policy.policy_id

            async with engine.connect() as connection:
                audit_count = await connection.scalar(
                    text(
                        "SELECT count(*) FROM audit_events "
                        "WHERE resource_type = 'agent_session_policy'"
                    )
                )
            assert audit_count == 4
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
