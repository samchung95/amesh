from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .identity import NaturalId, TenantSlug


class FederationProtocol(StrEnum):
    OIDC = "oidc"
    SAML = "saml"


class FederatedClaims(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider_id: NaturalId
    subject: str = Field(min_length=1, max_length=2048)
    email: str = Field(min_length=3, max_length=320)
    display: str = Field(min_length=1, max_length=255)
    groups: tuple[str, ...] = ()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized.count("@") != 1 or any(char.isspace() for char in normalized):
            raise ValueError("identity provider email claim is invalid")
        return normalized


class FederationState(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider_id: NaturalId
    protocol: FederationProtocol
    request_id: str | None = None
    nonce: str | None = None
    code_verifier: str | None = None
    tenant_slug: TenantSlug | None = None
    return_to: str
    expires_at: datetime


class ScimResourceRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider_id: NaturalId
    resource_type: str
    principal_id: UUID
    external_id: str | None = None
    resource_name: str
    handle: str
    display_name: str
    enabled: bool
    version: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime
    member_ids: tuple[UUID, ...] = ()
