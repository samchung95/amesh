from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from pydantic import SecretStr

from amesh.domain.model_continuations import ProtectedModelContinuation

_CONTRACT_VERSION = "amesh.model-continuation/v1"


class ModelContinuationError(ValueError):
    """Base class for invalid or unavailable protected continuation state."""


class ModelContinuationIntegrityError(ModelContinuationError):
    """Encrypted continuation state failed authentication or binding checks."""


class ModelContinuationProtector:
    """Authenticated encryption with one write key and bounded read-key rotation."""

    def __init__(
        self,
        *,
        primary_key_id: str,
        keys: Mapping[str, SecretStr | str],
    ) -> None:
        if not primary_key_id:
            raise ValueError("a continuation primary key id is required")
        if primary_key_id not in keys:
            raise ValueError("the continuation primary key id is not present in keys")
        if not keys:
            raise ValueError("at least one continuation encryption key is required")
        ordered_ids = (primary_key_id, *(key_id for key_id in keys if key_id != primary_key_id))
        try:
            fernets = tuple(Fernet(_key_bytes(keys[key_id])) for key_id in ordered_ids)
        except (UnicodeEncodeError, ValueError) as exc:
            raise ValueError("continuation keys must be valid URL-safe Fernet keys") from exc
        self._primary_key_id = primary_key_id
        self._fernet = MultiFernet(fernets)

    def protect(
        self,
        *,
        tenant_id: str,
        invocation_id: UUID,
        provider_id: str,
        provider_revision: str,
        token: SecretStr,
    ) -> ProtectedModelContinuation:
        raw_token = token.get_secret_value()
        if not raw_token:
            raise ValueError("continuation token cannot be empty")
        plaintext = json.dumps(
            {
                "contract": _CONTRACT_VERSION,
                "tenantId": tenant_id,
                "invocationId": str(invocation_id),
                "providerId": provider_id,
                "providerRevision": provider_revision,
                "token": raw_token,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return ProtectedModelContinuation(
            providerId=provider_id,
            providerRevision=provider_revision,
            keyId=self._primary_key_id,
            tokenDigest="sha256:" + hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
            ciphertext=self._fernet.encrypt(plaintext),
        )

    def reveal(
        self,
        protected: ProtectedModelContinuation,
        *,
        tenant_id: str,
        invocation_id: UUID,
        provider_id: str,
        provider_revision: str,
    ) -> SecretStr:
        try:
            plaintext = self._fernet.decrypt(protected.ciphertext)
            payload = json.loads(plaintext)
        except (InvalidToken, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ModelContinuationIntegrityError(
                "model continuation failed authenticated decryption"
            ) from exc
        expected = {
            "contract": _CONTRACT_VERSION,
            "tenantId": tenant_id,
            "invocationId": str(invocation_id),
            "providerId": provider_id,
            "providerRevision": provider_revision,
        }
        if not isinstance(payload, dict) or any(
            payload.get(key) != value for key, value in expected.items()
        ):
            raise ModelContinuationIntegrityError(
                "model continuation does not match its tenant, invocation or provider pin"
            )
        token = payload.get("token")
        if not isinstance(token, str) or not token:
            raise ModelContinuationIntegrityError("model continuation token is unavailable")
        digest = "sha256:" + hashlib.sha256(token.encode("utf-8")).hexdigest()
        if digest != protected.token_digest:
            raise ModelContinuationIntegrityError("model continuation digest does not match")
        if (protected.provider_id, protected.provider_revision) != (
            provider_id,
            provider_revision,
        ):
            raise ModelContinuationIntegrityError("model continuation provider pin does not match")
        return SecretStr(token)


def configured_model_continuation_protector(
    *,
    primary_key_id: str,
    primary_key: SecretStr | None,
    previous_key_id: str | None = None,
    previous_key: SecretStr | None = None,
) -> ModelContinuationProtector | None:
    if primary_key is None:
        return None
    keys: dict[str, SecretStr] = {}
    if previous_key_id is not None and previous_key is not None:
        keys[previous_key_id] = previous_key
    keys[primary_key_id] = primary_key
    return ModelContinuationProtector(primary_key_id=primary_key_id, keys=keys)


def _key_bytes(value: SecretStr | str) -> bytes:
    raw = value.get_secret_value() if isinstance(value, SecretStr) else value
    return raw.encode("ascii")
