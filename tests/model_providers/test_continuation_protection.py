from __future__ import annotations

from uuid import uuid4

import pytest
from cryptography.fernet import Fernet
from pydantic import SecretStr

from amesh.config import Settings
from amesh.model_continuations import (
    ModelContinuationIntegrityError,
    ModelContinuationProtector,
    configured_model_continuation_protector,
)


def test_continuation_is_encrypted_bound_and_redaction_safe() -> None:
    invocation_id = uuid4()
    key = Fernet.generate_key().decode("ascii")
    protector = ModelContinuationProtector(
        primary_key_id="current",
        keys={"current": SecretStr(key)},
    )

    protected = protector.protect(
        tenant_id="tenant-a",
        invocation_id=invocation_id,
        provider_id="fixture",
        provider_revision="2.0.0",
        token=SecretStr("hidden-provider-state"),
    )

    assert b"hidden-provider-state" not in protected.ciphertext
    assert "hidden-provider-state" not in repr(protected)
    assert "hidden-provider-state" not in protected.model_dump_json()
    assert protected.public_metadata() == {
        "providerId": "fixture",
        "providerRevision": "2.0.0",
        "tokenDigest": protected.token_digest,
    }
    revealed = protector.reveal(
        protected,
        tenant_id="tenant-a",
        invocation_id=invocation_id,
        provider_id="fixture",
        provider_revision="2.0.0",
    )
    assert revealed.get_secret_value() == "hidden-provider-state"

    with pytest.raises(ModelContinuationIntegrityError, match="tenant"):
        protector.reveal(
            protected,
            tenant_id="tenant-b",
            invocation_id=invocation_id,
            provider_id="fixture",
            provider_revision="2.0.0",
        )


def test_continuation_key_rotation_reads_old_and_writes_current() -> None:
    invocation_id = uuid4()
    old_key = Fernet.generate_key().decode("ascii")
    current_key = Fernet.generate_key().decode("ascii")
    old = ModelContinuationProtector(primary_key_id="old", keys={"old": old_key})
    protected = old.protect(
        tenant_id="tenant-a",
        invocation_id=invocation_id,
        provider_id="fixture",
        provider_revision="1.0.0",
        token=SecretStr("resume-me"),
    )

    rotated = ModelContinuationProtector(
        primary_key_id="current",
        keys={"current": current_key, "old": old_key},
    )
    assert (
        rotated.reveal(
            protected,
            tenant_id="tenant-a",
            invocation_id=invocation_id,
            provider_id="fixture",
            provider_revision="1.0.0",
        ).get_secret_value()
        == "resume-me"
    )
    replacement = rotated.protect(
        tenant_id="tenant-a",
        invocation_id=uuid4(),
        provider_id="fixture",
        provider_revision="1.0.0",
        token=SecretStr("new-state"),
    )
    assert replacement.key_id == "current"


def test_continuation_key_configuration_remains_secret() -> None:
    raw_key = Fernet.generate_key().decode("ascii")
    settings = Settings(
        _env_file=None,
        model_continuation_key_id="current",
        model_continuation_encryption_key=raw_key,
    )
    assert raw_key not in repr(settings)
    assert (
        configured_model_continuation_protector(
            primary_key_id=settings.model_continuation_key_id,
            primary_key=settings.model_continuation_encryption_key,
            previous_key_id=settings.model_continuation_previous_key_id,
            previous_key=settings.model_continuation_previous_encryption_key,
        )
        is not None
    )
    with pytest.raises(ValueError, match="must be set together"):
        Settings(
            _env_file=None,
            model_continuation_previous_key_id="previous",
        )
