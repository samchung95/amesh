from __future__ import annotations

import hmac
import re
import secrets
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, SecretStr, model_validator

from .authorization import PermissionAction, PrincipalType
from .identity import NaturalId, new_runtime_id

_TOKEN_PATTERN = re.compile(r"^amesh_v1_([0-9a-f]{32})\.([A-Za-z0-9_-]{43})$")


class CredentialKind(StrEnum):
    API_TOKEN = "API_TOKEN"
    DERIVED_TOKEN = "DERIVED_TOKEN"


class CredentialStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    REVOKED = "REVOKED"


def validate_credential_scope(value: str) -> str:
    resource, separator, action = value.partition(":")
    if not separator or not resource or not action or ":" in action:
        raise ValueError("credential scope must use resource:action")
    if resource != "*" and not resource.replace("_", "").replace("-", "").isalnum():
        raise ValueError("credential scope resource is invalid")
    if action != "*" and action not in PermissionAction:
        raise ValueError("credential scope action is invalid")
    return value


CredentialScope = Annotated[
    str,
    Field(min_length=3, max_length=257),
    AfterValidator(validate_credential_scope),
]


class CredentialMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=new_runtime_id)
    principal_id: UUID
    principal_type: PrincipalType
    name: NaturalId
    kind: CredentialKind = CredentialKind.API_TOKEN
    scopes: tuple[CredentialScope, ...] = ("*:*",)
    audience: str = Field(default="amesh-api", min_length=1, max_length=128)
    status: CredentialStatus = CredentialStatus.ACTIVE
    expires_at: datetime
    rate_limit_per_minute: int = Field(default=600, ge=1, le=1_000_000)
    issued_credential_version: int = Field(default=1, ge=1)
    parent_token_id: UUID | None = None
    superseded_by: UUID | None = None
    overlap_expires_at: datetime | None = None
    last_used_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    revoked_at: datetime | None = None

    @model_validator(mode="after")
    def validate_lifecycle(self) -> CredentialMetadata:
        for value in (
            self.expires_at,
            self.created_at,
            self.overlap_expires_at,
            self.last_used_at,
            self.revoked_at,
        ):
            if value is not None and value.tzinfo is None:
                raise ValueError("credential timestamps must be timezone-aware")
        if self.expires_at <= self.created_at:
            raise ValueError("credential expiry must follow creation")
        if not self.scopes:
            raise ValueError("credential requires at least one scope")
        if self.kind is CredentialKind.DERIVED_TOKEN and self.parent_token_id is None:
            raise ValueError("derived credential requires parent_token_id")
        if self.status is CredentialStatus.SUPERSEDED and (
            self.superseded_by is None or self.overlap_expires_at is None
        ):
            raise ValueError("superseded credential requires replacement and overlap deadline")
        if self.status is CredentialStatus.REVOKED and self.revoked_at is None:
            raise ValueError("revoked credential requires revoked_at")
        return self


class StoredCredential(BaseModel):
    model_config = ConfigDict(frozen=True)

    metadata: CredentialMetadata
    token_hash: bytes = Field(repr=False)


class IssuedCredential(BaseModel):
    model_config = ConfigDict(frozen=True)

    metadata: CredentialMetadata
    token: SecretStr = Field(repr=False)


def issue_token_material(token_id: UUID) -> tuple[str, str]:
    secret = secrets.token_urlsafe(32)
    return f"amesh_v1_{token_id.hex}.{secret}", secret


def parse_token_material(token: str) -> tuple[UUID, str]:
    matched = _TOKEN_PATTERN.fullmatch(token)
    if matched is None:
        raise ValueError("invalid AMESH bearer token format")
    return UUID(hex=matched.group(1)), matched.group(2)


def token_digest(secret: str, pepper: SecretStr | str) -> bytes:
    key = pepper.get_secret_value() if isinstance(pepper, SecretStr) else pepper
    if not key:
        raise ValueError("token pepper cannot be empty")
    return hmac.new(key.encode("utf-8"), secret.encode("ascii"), sha256).digest()


def credential_scope_allows(
    scopes: tuple[str, ...],
    resource_type: str,
    action: PermissionAction,
) -> bool:
    return any(
        scope
        in {"*:*", f"*:{action.value}", f"{resource_type}:*", f"{resource_type}:{action.value}"}
        for scope in scopes
    )


def credential_scope_covers(parent_scopes: tuple[str, ...], child_scope: str) -> bool:
    child_resource, child_action = child_scope.split(":", maxsplit=1)
    return any(
        parent_scope == "*:*"
        or (
            (parent_scope.split(":", maxsplit=1)[0] in {"*", child_resource})
            and (parent_scope.split(":", maxsplit=1)[1] in {"*", child_action})
        )
        for parent_scope in parent_scopes
    )
