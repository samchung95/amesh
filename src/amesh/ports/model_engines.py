"""Provider-neutral contracts for subscription-backed model engines."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator


class ProviderError(RuntimeError):
    """Provider-neutral failure raised at a model-engine boundary."""


class ProviderProcessError(ProviderError):
    """A model-engine child process could not be started or completed."""


class ProviderProtocolError(ProviderError):
    """A model engine violated its bounded transport or message contract."""


class ProviderTimeoutError(ProviderError, TimeoutError):
    """A bounded model-engine operation exceeded its deadline."""


class ModelEngineAccess(BaseModel):
    """Private access selector; exactly one engine reference or secret is permitted."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    engine_ref: str | None = Field(default=None, alias="engineRef", min_length=1, max_length=512)
    credential: SecretStr | None = Field(default=None, exclude=True, repr=False)

    @model_validator(mode="after")
    def validate_exclusive_access(self) -> ModelEngineAccess:
        if (self.engine_ref is None) == (self.credential is None):
            raise ValueError("model engine access requires exactly one engineRef or credential")
        return self

    def get_secret_value(self) -> str:
        """Compatibility accessor for legacy provider fakes; engine refs are never secrets."""
        if self.credential is None:
            raise ValueError("model engine access does not contain a credential")
        return self.credential.get_secret_value()


class EngineAccountStatus(BaseModel):
    """Safe account projection shared by subscription engine adapters."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    authenticated: bool | None
    auth_mode: str | None = Field(default=None, alias="authMode")
    plan_type: str | None = Field(default=None, alias="planType")
    requires_openai_auth: bool | None = Field(default=None, alias="requiresOpenaiAuth")
    rate_limits: dict[str, Any] | None = Field(default=None, alias="rateLimits")
    usage: dict[str, Any] | None = None
    action_required: bool = Field(default=False, alias="actionRequired")


class EngineLoginStart(BaseModel):
    """Safe, provider-neutral user-action projection for an interactive login."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: str = Field(min_length=1, max_length=64)
    login_id: str = Field(alias="loginId", min_length=1, max_length=255)
    auth_url: str | None = Field(default=None, alias="authUrl")
    verification_url: str | None = Field(default=None, alias="verificationUrl")
    user_code: str | None = Field(default=None, alias="userCode")
    expires_at: int | None = Field(default=None, alias="expiresAt", ge=0)
    action_required: bool = Field(default=True, alias="actionRequired")


class ModelEngineAccountManager(Protocol):
    """Account lifecycle port implemented by Codex and other process engines."""

    async def status(
        self,
        tenant_id: str,
        *,
        refresh_token: bool = False,
        include_rate_limits: bool = False,
        include_usage: bool = False,
    ) -> EngineAccountStatus: ...

    async def login_start(self, tenant_id: str, *, mode: str = "browser") -> EngineLoginStart: ...

    async def logout(self, tenant_id: str) -> None: ...


__all__ = [
    "EngineAccountStatus",
    "EngineLoginStart",
    "ModelEngineAccess",
    "ModelEngineAccountManager",
    "ProviderError",
    "ProviderProcessError",
    "ProviderProtocolError",
    "ProviderTimeoutError",
]
