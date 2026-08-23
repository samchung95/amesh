from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .feature_flags import FeatureFlag, FeatureFlagScope


class AdministrationControlKey(StrEnum):
    RETENTION = "RETENTION"
    ANNOUNCEMENT = "ANNOUNCEMENT"
    MAINTENANCE = "MAINTENANCE"
    KILL_SWITCH = "KILL_SWITCH"


CONTROL_FLAG_KEYS = {
    AdministrationControlKey.RETENTION: "admin-retention-executions",
    AdministrationControlKey.ANNOUNCEMENT: "admin-announcement-banner",
    AdministrationControlKey.MAINTENANCE: "admin-maintenance-mode",
    AdministrationControlKey.KILL_SWITCH: "admin-execution-kill-switch",
}


class AdministrationControlDraft(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: AdministrationControlKey
    enabled: bool
    value: int | str | None = None
    reason: str = Field(min_length=3, max_length=500)
    expected_version: int | None = Field(default=None, alias="expectedVersion", ge=1)

    @model_validator(mode="after")
    def validate_value(self) -> AdministrationControlDraft:
        if self.key is AdministrationControlKey.RETENTION:
            if isinstance(self.value, bool) or not isinstance(self.value, int):
                raise ValueError("retention requires an integer day count")
            if not 1 <= self.value <= 3650:
                raise ValueError("retention days must be between 1 and 3650")
        elif self.key is AdministrationControlKey.ANNOUNCEMENT:
            if not isinstance(self.value, str) or len(self.value) > 1000:
                raise ValueError("announcement requires a message of at most 1000 characters")
            if self.enabled and not self.value.strip():
                raise ValueError("enabled announcement requires a message")
        elif self.value not in (None, ""):
            raise ValueError(f"{self.key.value} does not accept a value")
        return self


class AdministrationControl(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: AdministrationControlKey
    flag_key: str = Field(alias="flagKey")
    enabled: bool
    value: int | str | None = None
    version: int | None = Field(default=None, ge=1)
    updated_by: str | None = Field(default=None, alias="updatedBy")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


class AdministrationImpactPreview(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    draft: AdministrationControlDraft
    impacts: tuple[str, ...]
    recovery: str
    confirmation: str
    approval: str
    expires_at: datetime = Field(alias="expiresAt")


class AdministrationApplyRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    draft: AdministrationControlDraft
    approval: str = Field(min_length=32, max_length=8192)
    confirmation: str = Field(min_length=1, max_length=128)


class AdministrationAuditEntry(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    event_id: str = Field(alias="eventId")
    actor_id: str = Field(alias="actorId")
    action: str
    resource_id: str = Field(alias="resourceId")
    outcome: str
    reason: str
    evidence: dict[str, Any]
    occurred_at: datetime = Field(alias="occurredAt")


class AdministrationApprovalError(ValueError):
    """Raised when a short-lived administration approval cannot authorize an apply."""


_DEFAULT_VALUES: dict[AdministrationControlKey, int | str | None] = {
    AdministrationControlKey.RETENTION: 30,
    AdministrationControlKey.ANNOUNCEMENT: "",
    AdministrationControlKey.MAINTENANCE: None,
    AdministrationControlKey.KILL_SWITCH: None,
}


def administration_controls(flags: tuple[FeatureFlag, ...]) -> tuple[AdministrationControl, ...]:
    by_key = {flag.key: flag for flag in flags}
    controls: list[AdministrationControl] = []
    for key in AdministrationControlKey:
        flag = by_key.get(CONTROL_FLAG_KEYS[key])
        payload = _decode_description(flag.description) if flag is not None else {}
        controls.append(
            AdministrationControl(
                key=key,
                flagKey=CONTROL_FLAG_KEYS[key],
                enabled=flag.enabled if flag is not None else False,
                value=payload.get("value", _DEFAULT_VALUES[key]),
                version=flag.version if flag is not None else None,
                updatedBy=flag.updated_by if flag is not None else None,
                updatedAt=flag.updated_at if flag is not None else None,
            )
        )
    return tuple(controls)


def administration_control_flag(
    draft: AdministrationControlDraft,
    *,
    tenant_id: str,
    actor_id: str,
) -> FeatureFlag:
    description = json.dumps(
        {
            "schemaVersion": "amesh.administration-control/v1",
            "value": draft.value,
            "reason": draft.reason,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return FeatureFlag(
        key=CONTROL_FLAG_KEYS[draft.key],
        scope=FeatureFlagScope.TENANT,
        tenant_id=tenant_id,
        enabled=draft.enabled,
        description=description,
        updated_by=actor_id,
    )


def issue_administration_preview(
    draft: AdministrationControlDraft,
    *,
    actor_id: str,
    tenant_id: str,
    signing_key: str,
    now: datetime | None = None,
) -> AdministrationImpactPreview:
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + timedelta(minutes=5)
    payload = {
        "actorId": actor_id,
        "tenantId": tenant_id,
        "draftHash": _draft_hash(draft),
        "expiresAt": expires_at.isoformat(),
    }
    encoded = _urlsafe(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    signature = _urlsafe(hmac.new(signing_key.encode(), encoded.encode(), hashlib.sha256).digest())
    impacts, recovery = _impact(draft)
    return AdministrationImpactPreview(
        draft=draft,
        impacts=impacts,
        recovery=recovery,
        confirmation=f"APPLY {draft.key.value}",
        approval=f"{encoded}.{signature}",
        expiresAt=expires_at,
    )


def verify_administration_approval(
    request: AdministrationApplyRequest,
    *,
    actor_id: str,
    tenant_id: str,
    signing_key: str,
    now: datetime | None = None,
) -> None:
    expected_confirmation = f"APPLY {request.draft.key.value}"
    if request.confirmation != expected_confirmation:
        raise AdministrationApprovalError("confirmation phrase does not match the preview")
    try:
        encoded, provided_signature = request.approval.split(".", 1)
        expected_signature = _urlsafe(
            hmac.new(signing_key.encode(), encoded.encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(provided_signature, expected_signature):
            raise AdministrationApprovalError("administration approval signature is invalid")
        payload = json.loads(_decode_urlsafe(encoded))
        expires_at = datetime.fromisoformat(str(payload["expiresAt"]))
    except AdministrationApprovalError:
        raise
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AdministrationApprovalError("administration approval is malformed") from exc
    if expires_at.tzinfo is None or expires_at <= (now or datetime.now(UTC)):
        raise AdministrationApprovalError("administration approval has expired")
    if payload.get("actorId") != actor_id or payload.get("tenantId") != tenant_id:
        raise AdministrationApprovalError("administration approval scope does not match")
    if payload.get("draftHash") != _draft_hash(request.draft):
        raise AdministrationApprovalError("administration control changed after preview")


def _impact(draft: AdministrationControlDraft) -> tuple[tuple[str, ...], str]:
    enabled = "enable" if draft.enabled else "disable"
    if draft.key is AdministrationControlKey.RETENTION:
        return (
            (
                f"Set retained execution policy to {draft.value} days for this tenant.",
                "A later lifecycle sweep may make expired data unavailable after its recovery window.",
            ),
            "Apply a longer retention policy before the next lifecycle sweep; already purged data requires backup restore.",
        )
    if draft.key is AdministrationControlKey.ANNOUNCEMENT:
        return (
            (f"{enabled.title()} the tenant-wide operator announcement banner.",),
            "Disable the banner or restore the previous message.",
        )
    if draft.key is AdministrationControlKey.MAINTENANCE:
        return (
            (
                f"{enabled.title()} tenant maintenance mode.",
                "New interactive changes may be restricted while running orchestration remains visible.",
            ),
            "Disable maintenance mode after platform checks complete.",
        )
    return (
        (
            f"{enabled.title()} the tenant execution kill switch.",
            "When enabled, new execution admission is stopped; already-running work follows its existing cancellation policy.",
        ),
        "Disable the kill switch, verify capacity, then resume paused admission.",
    )


def _draft_hash(draft: AdministrationControlDraft) -> str:
    value = draft.model_dump(mode="json", by_alias=True)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _decode_description(description: str) -> dict[str, Any]:
    try:
        value = json.loads(description)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _urlsafe(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _decode_urlsafe(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding).decode()
