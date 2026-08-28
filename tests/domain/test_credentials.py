from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import SecretStr, ValidationError

from amesh.domain import (
    CredentialKind,
    CredentialMetadata,
    IssuedCredential,
    PermissionAction,
    PrincipalType,
    credential_scope_allows,
    credential_scope_covers,
    issue_token_material,
    parse_token_material,
    token_digest,
)


def test_token_material_is_256_bit_urlsafe_and_hash_only_is_repr_safe() -> None:
    token_id = uuid4()
    token, secret = issue_token_material(token_id)

    assert parse_token_material(token) == (token_id, secret)
    assert len(secret) == 43
    assert token_digest(secret, "pepper") == token_digest(secret, SecretStr("pepper"))
    issued = IssuedCredential(
        metadata=CredentialMetadata(
            id=token_id,
            principal_id=uuid4(),
            principal_type=PrincipalType.SERVICE_ACCOUNT,
            name="automation",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        ),
        token=token,
    )
    assert secret not in repr(issued)
    assert issued.token.get_secret_value() == token


def test_token_parser_rejects_noncanonical_material() -> None:
    with pytest.raises(ValueError):
        parse_token_material("not-a-token")


def test_scopes_intersect_resource_and_action() -> None:
    scopes = ("flow:view", "execution:*", "*:use")

    assert credential_scope_allows(scopes, "flow", PermissionAction.VIEW)
    assert credential_scope_allows(scopes, "execution", PermissionAction.MANAGE)
    assert credential_scope_allows(scopes, "secret", PermissionAction.USE)
    assert not credential_scope_allows(scopes, "flow", PermissionAction.UPDATE)


def test_derived_scope_cannot_exceed_parent_wildcards() -> None:
    parent = ("flow:*", "*:use")

    assert credential_scope_covers(parent, "flow:view")
    assert credential_scope_covers(parent, "secret:use")
    assert not credential_scope_covers(parent, "secret:view")


def test_derived_credentials_require_parent_and_valid_scope() -> None:
    with pytest.raises(ValidationError):
        CredentialMetadata(
            principal_id=uuid4(),
            principal_type=PrincipalType.WORKER,
            name="derived",
            kind=CredentialKind.DERIVED_TOKEN,
            scopes=("invalid",),
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
        )
