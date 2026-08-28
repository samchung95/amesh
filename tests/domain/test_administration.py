from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from amesh.domain import (
    AdministrationApplyRequest,
    AdministrationApprovalError,
    AdministrationControlDraft,
    AdministrationControlKey,
    administration_controls,
    issue_administration_preview,
    verify_administration_approval,
)


def test_administration_controls_have_safe_defaults_and_typed_values() -> None:
    controls = administration_controls(())
    assert [item.key for item in controls] == list(AdministrationControlKey)
    assert controls[0].value == 30
    assert all(not item.enabled and item.version is None for item in controls)

    with pytest.raises(ValueError, match="integer day count"):
        AdministrationControlDraft(
            key=AdministrationControlKey.RETENTION,
            enabled=True,
            value="30",
            reason="test invalid retention",
        )
    with pytest.raises(ValueError, match="requires a message"):
        AdministrationControlDraft(
            key=AdministrationControlKey.ANNOUNCEMENT,
            enabled=True,
            value="",
            reason="test invalid announcement",
        )


def test_administration_approval_is_short_lived_actor_tenant_and_draft_bound() -> None:
    now = datetime(2026, 8, 23, tzinfo=UTC)
    draft = AdministrationControlDraft(
        key=AdministrationControlKey.KILL_SWITCH,
        enabled=True,
        reason="stop new execution admission",
    )
    preview = issue_administration_preview(
        draft,
        actor_id="actor-1",
        tenant_id="default",
        signing_key="test-signing-key",
        now=now,
    )
    request = AdministrationApplyRequest(
        draft=draft,
        approval=preview.approval,
        confirmation=preview.confirmation,
    )
    verify_administration_approval(
        request,
        actor_id="actor-1",
        tenant_id="default",
        signing_key="test-signing-key",
        now=now + timedelta(minutes=1),
    )

    with pytest.raises(AdministrationApprovalError, match="scope does not match"):
        verify_administration_approval(
            request,
            actor_id="actor-2",
            tenant_id="default",
            signing_key="test-signing-key",
            now=now,
        )
    with pytest.raises(AdministrationApprovalError, match="expired"):
        verify_administration_approval(
            request,
            actor_id="actor-1",
            tenant_id="default",
            signing_key="test-signing-key",
            now=now + timedelta(minutes=6),
        )
    changed = request.model_copy(
        update={"draft": draft.model_copy(update={"enabled": False})}
    )
    with pytest.raises(AdministrationApprovalError, match="changed after preview"):
        verify_administration_approval(
            changed,
            actor_id="actor-1",
            tenant_id="default",
            signing_key="test-signing-key",
            now=now,
        )
