from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresCredentialRepository,
)
from amesh.app import (
    app,
    get_authorization_repository,
    get_authorization_service,
    get_credential_repository,
    get_credential_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.credentials import CredentialService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_api_token_is_shown_once_and_authenticates_outside_development() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        authorization_repository = PostgresAuthorizationRepository(engine)
        credential_repository = PostgresCredentialRepository(engine)
        credential_service = CredentialService(
            credential_repository,
            token_pepper=SecretStr("api-integration-pepper"),
        )
        authorization_service = AuthorizationService(authorization_repository)
        suffix = uuid4().hex[:12]
        active_settings = [
            Settings(
                _env_file=None,
                database_url=TEST_DATABASE_URL,
                app_env="development",
                auth_mode="development",
                amesh_admin_token="bootstrap-test-token",
            )
        ]
        app.dependency_overrides[get_settings] = lambda: active_settings[0]
        app.dependency_overrides[get_authorization_repository] = lambda: authorization_repository
        app.dependency_overrides[get_authorization_service] = lambda: authorization_service
        app.dependency_overrides[get_credential_repository] = lambda: credential_repository
        app.dependency_overrides[get_credential_service] = lambda: credential_service
        bootstrap_headers = {"authorization": "Bearer bootstrap-test-token"}
        principal_id: UUID | None = None
        token_ids: list[UUID] = []
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="https://amesh.test",
            ) as client:
                principal_response = await client.post(
                    "/api/v1/admin/principals",
                    headers=bootstrap_headers,
                    json={
                        "principal_type": "SERVICE_ACCOUNT",
                        "handle": f"api-service-{suffix}",
                        "display_name": "API service account",
                    },
                )
                assert principal_response.status_code == 201
                principal_id = UUID(principal_response.json()["id"])
                binding = await client.post(
                    "/api/v1/admin/bindings",
                    headers=bootstrap_headers,
                    json={
                        "principal_id": str(principal_id),
                        "principal_type": "SERVICE_ACCOUNT",
                        "role_name": "instance-admin",
                        "scope_type": "INSTANCE",
                    },
                )
                assert binding.status_code == 201

                issued_response = await client.post(
                    f"/api/v1/admin/principals/{principal_id}/credentials",
                    headers=bootstrap_headers,
                    json={
                        "name": "control-plane",
                        "scopes": ["*:*"],
                        "audience": "amesh-api",
                        "expiresAt": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
                        "rateLimitPerMinute": 100,
                    },
                )
                assert issued_response.status_code == 201
                issued_body = issued_response.json()
                token = issued_body["token"]
                first_token_id = UUID(issued_body["metadata"]["id"])
                token_ids.append(first_token_id)
                assert token.startswith(f"amesh_v1_{first_token_id.hex}.")

                listed = await client.get(
                    f"/api/v1/admin/principals/{principal_id}/credentials",
                    headers=bootstrap_headers,
                )
                assert listed.status_code == 200
                assert listed.json()[0]["id"] == str(first_token_id)
                assert "token" not in listed.json()[0]
                assert "token_hash" not in listed.json()[0]
                assert token not in listed.text

                active_settings[0] = Settings(
                    _env_file=None,
                    database_url=TEST_DATABASE_URL,
                    app_env="production",
                    auth_mode="credentials",
                    amesh_admin_token="bootstrap-test-token",
                    amesh_token_pepper="api-integration-pepper",
                    object_storage_workload_identity=True,
                )
                durable_headers = {"authorization": f"Bearer {token}"}
                assert (
                    await client.get("/api/v1/admin/roles", headers=durable_headers)
                ).status_code == 200
                assert (
                    await client.get("/api/v1/admin/roles", headers=bootstrap_headers)
                ).status_code == 401
                assert "/api/v1/auth/login" in app.openapi()["paths"]

                rotated = await client.post(
                    f"/api/v1/admin/credentials/{first_token_id}/rotate",
                    headers=durable_headers,
                    json={"overlapSeconds": 300},
                )
                assert rotated.status_code == 201
                replacement = rotated.json()["token"]
                replacement_id = UUID(rotated.json()["metadata"]["id"])
                token_ids.append(replacement_id)
                replacement_headers = {"authorization": f"Bearer {replacement}"}
                assert (
                    await client.get("/api/v1/admin/roles", headers=durable_headers)
                ).status_code == 200
                assert (
                    await client.get("/api/v1/admin/roles", headers=replacement_headers)
                ).status_code == 200

                revoked_old = await client.delete(
                    f"/api/v1/admin/credentials/{first_token_id}",
                    headers=replacement_headers,
                )
                assert revoked_old.status_code == 200
                assert revoked_old.json()["revokedCount"] == 1
                assert (
                    await client.get("/api/v1/admin/roles", headers=durable_headers)
                ).status_code == 401

                revoked_all = await client.delete(
                    f"/api/v1/admin/principals/{principal_id}/credentials",
                    headers=replacement_headers,
                )
                assert revoked_all.status_code == 200
                assert revoked_all.json()["revokedCount"] == 1
                assert (
                    await client.get("/api/v1/admin/roles", headers=replacement_headers)
                ).status_code == 401
        finally:
            app.dependency_overrides.clear()
            async with engine.begin() as connection:
                if principal_id is not None:
                    await connection.execute(
                        text("DELETE FROM auth_principals WHERE id = :principal_id"),
                        {"principal_id": principal_id},
                    )
                await connection.execute(
                    text(
                        """
                        DELETE FROM audit_events
                        WHERE actor_id IN (
                            '00000000-0000-7000-8000-000000000001',
                            :principal_id
                        )
                           OR resource_id = ANY(CAST(:token_ids AS text[]))
                        """
                    ),
                    {
                        "principal_id": str(principal_id),
                        "token_ids": [str(value) for value in token_ids],
                    },
                )
            await engine.dispose()

    asyncio.run(scenario())
