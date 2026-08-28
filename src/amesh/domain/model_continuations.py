from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProtectedModelContinuation(BaseModel):
    """Encrypted provider state stored outside public invocation evidence."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    provider_id: str = Field(alias="providerId", min_length=1, max_length=255)
    provider_revision: str = Field(alias="providerRevision", min_length=1, max_length=255)
    key_id: str = Field(alias="keyId", min_length=1, max_length=255)
    token_digest: str = Field(alias="tokenDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    ciphertext: bytes = Field(min_length=1)

    def public_metadata(self) -> dict[str, str]:
        return {
            "providerId": self.provider_id,
            "providerRevision": self.provider_revision,
            "tokenDigest": self.token_digest,
        }


class ProtectedTriggerPayload(BaseModel):
    """Encrypted trigger input stored outside public occurrence projections."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key_id: str = Field(alias="keyId", min_length=1, max_length=255)
    payload_digest: str = Field(alias="payloadDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    ciphertext: bytes = Field(min_length=1)
