from __future__ import annotations

import asyncio
import os
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresFederationRepository
from amesh.app import app, get_federation_repository, get_settings
from amesh.config import Settings
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_scim_bearer_tenant_isolation_user_group_patch_disable_and_deprovision(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        first_token = tmp_path / "first-scim-token"
        second_token = tmp_path / "second-scim-token"
        first_token.write_text("first-token\n", encoding="utf-8")
        second_token.write_text("second-token\n", encoding="utf-8")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        try:
            await apply_migrations(database.database_url, migration_directory())
            engine = create_async_engine(database.database_url)
            repository = PostgresFederationRepository(
                engine,
                token_pepper=SecretStr("scim-api-test-pepper"),
            )
            settings = Settings(
                _env_file=None,
                database_url=database.database_url,
                scim_providers=(
                    {
                        "id": "tenant-default",
                        "tenant": "default",
                        "role": "viewer",
                        "tokenFile": str(first_token),
                    },
                    {
                        "id": "tenant-isolated",
                        "tenant": "default",
                        "role": "viewer",
                        "tokenFile": str(second_token),
                    },
                ),
            )
            app.dependency_overrides[get_settings] = lambda: settings
            app.dependency_overrides[get_federation_repository] = lambda: repository
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="https://amesh.test") as client:
                unauthenticated = await client.get("/scim/v2/ServiceProviderConfig")
                assert unauthenticated.status_code == 401
                invalid = await client.get(
                    "/scim/v2/ServiceProviderConfig",
                    headers={"Authorization": "Bearer wrong"},
                )
                assert invalid.status_code == 401
                headers = {"Authorization": "Bearer first-token"}
                configuration = await client.get(
                    "/scim/v2/ServiceProviderConfig",
                    headers=headers,
                )
                assert configuration.status_code == 200
                assert configuration.json()["patch"]["supported"] is True
                first_token.write_text("rotated-first-token\n", encoding="utf-8")
                rejected_old_token = await client.get(
                    "/scim/v2/ServiceProviderConfig",
                    headers=headers,
                )
                assert rejected_old_token.status_code == 401
                headers = {"Authorization": "Bearer rotated-first-token"}
                assert (
                    await client.get("/scim/v2/ServiceProviderConfig", headers=headers)
                ).status_code == 200
                created_user = await client.post(
                    "/scim/v2/Users",
                    headers=headers,
                    json={
                        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
                        "externalId": "entra-user-42",
                        "userName": "ada@example.com",
                        "displayName": "Ada Lovelace",
                        "active": True,
                    },
                )
                assert created_user.status_code == 201, created_user.text
                user = created_user.json()
                assert user["userName"] == "ada@example.com"
                user_id = user["id"]
                assert created_user.headers["etag"] == 'W/"1"'
                isolated = await client.get(
                    f"/scim/v2/Users/{user_id}",
                    headers={"Authorization": "Bearer second-token"},
                )
                assert isolated.status_code == 404
                filtered = await client.get(
                    '/scim/v2/Users?filter=userName%20eq%20%22ada%40example.com%22',
                    headers=headers,
                )
                assert filtered.status_code == 200
                assert filtered.json()["totalResults"] == 1
                disabled = await client.patch(
                    f"/scim/v2/Users/{user_id}",
                    headers=headers,
                    json={
                        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                        "Operations": [{"op": "Replace", "path": "active", "value": False}],
                    },
                )
                assert disabled.status_code == 200, disabled.text
                assert disabled.json()["active"] is False
                created_group = await client.post(
                    "/scim/v2/Groups",
                    headers=headers,
                    json={
                        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
                        "externalId": "entra-group-7",
                        "displayName": "Platform team",
                        "members": [],
                    },
                )
                assert created_group.status_code == 201, created_group.text
                group_id = created_group.json()["id"]
                added = await client.patch(
                    f"/scim/v2/Groups/{group_id}",
                    headers=headers,
                    json={
                        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                        "Operations": [
                            {"op": "Add", "path": "members", "value": [{"value": user_id}]}
                        ],
                    },
                )
                assert added.status_code == 400
                reenabled = await client.patch(
                    f"/scim/v2/Users/{user_id}",
                    headers=headers,
                    json={
                        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                        "Operations": [{"op": "Replace", "path": "active", "value": True}],
                    },
                )
                assert reenabled.status_code == 200
                added = await client.patch(
                    f"/scim/v2/Groups/{group_id}",
                    headers=headers,
                    json={
                        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                        "Operations": [
                            {"op": "Add", "path": "members", "value": [{"value": user_id}]}
                        ],
                    },
                )
                assert added.status_code == 200, added.text
                assert added.json()["members"] == [{"value": user_id, "display": None}]
                removed = await client.patch(
                    f"/scim/v2/Groups/{group_id}",
                    headers=headers,
                    json={
                        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                        "Operations": [
                            {
                                "op": "Remove",
                                "path": f'members[value eq "{user_id}"]',
                            }
                        ],
                    },
                )
                assert removed.status_code == 200
                assert removed.json()["members"] == []
                deleted = await client.delete(f"/scim/v2/Users/{user_id}", headers=headers)
                assert deleted.status_code == 204
                missing = await client.get(f"/scim/v2/Users/{user_id}", headers=headers)
                assert missing.status_code == 404
            await engine.dispose()
        finally:
            app.dependency_overrides.clear()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
