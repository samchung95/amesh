from __future__ import annotations

import re
import secrets
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from .authorization import ActorContext
from .identity import NaturalId, new_runtime_id

_SESSION_PATTERN = re.compile(r"^amesh_session_v1_([0-9a-f]{32})\.([A-Za-z0-9_-]{43})$")


class AuthenticationProviderKind(StrEnum):
    LOCAL = "local"
    OIDC = "oidc"
    SAML = "saml"
    LDAP = "ldap"


class AuthenticationProviderDescriptor(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: NaturalId
    kind: AuthenticationProviderKind
    display_name: str = Field(min_length=1, max_length=255)
    interactive: bool = True
    login_mode: str = "password"
    domains: tuple[str, ...] = ()
    tenants: tuple[str, ...] = ()


class AuthenticationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: NaturalId = "local"
    identifier: str = Field(min_length=1, max_length=255)
    secret: SecretStr = Field(repr=False)


class ProviderIdentity(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: NaturalId
    principal_id: UUID
    display: str = Field(min_length=1, max_length=255)
    credential_version: int = Field(ge=1)


class BrowserSession(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=new_runtime_id)
    principal_id: UUID
    issued_credential_version: int = Field(ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    idle_expires_at: datetime
    absolute_expires_at: datetime
    rotated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class IssuedBrowserSession(BaseModel):
    model_config = ConfigDict(frozen=True)

    actor: ActorContext
    session_id: UUID
    session_token: SecretStr = Field(repr=False)
    csrf_token: SecretStr = Field(repr=False)
    idle_expires_at: datetime
    absolute_expires_at: datetime


class AuthenticatedBrowserSession(BaseModel):
    model_config = ConfigDict(frozen=True)

    actor: ActorContext
    session_id: UUID
    rotated_token: SecretStr | None = Field(default=None, repr=False)
    idle_expires_at: datetime
    absolute_expires_at: datetime


def issue_session_material(session_id: UUID) -> tuple[str, str]:
    secret = secrets.token_urlsafe(32)
    return f"amesh_session_v1_{session_id.hex}.{secret}", secret


def parse_session_material(token: str) -> tuple[UUID, str]:
    matched = _SESSION_PATTERN.fullmatch(token)
    if matched is None:
        raise ValueError("invalid AMESH browser session format")
    return UUID(hex=matched.group(1)), matched.group(2)


def issue_csrf_material() -> str:
    return secrets.token_urlsafe(32)
