from __future__ import annotations

from typing import TYPE_CHECKING, Protocol
from uuid import UUID

if TYPE_CHECKING:
    from amesh.realtime import (
        RealtimeEvent,
        RealtimeFilter,
        WebhookDelivery,
        WebhookDeliveryClaim,
        WebhookDeliveryHistory,
        WebhookSubscription,
        WebhookSubscriptionCreate,
    )


class RealtimeRepository(Protocol):
    async def list_events(
        self,
        *,
        tenant_id: str,
        after_cursor: int,
        filters: RealtimeFilter,
        limit: int,
    ) -> tuple[RealtimeEvent, ...]: ...

    async def cursor_bounds(self, *, tenant_id: str) -> tuple[int | None, int | None]: ...

    async def create_subscription(
        self,
        request: WebhookSubscriptionCreate,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> WebhookSubscription: ...

    async def list_subscriptions(self, *, tenant_id: str) -> tuple[WebhookSubscription, ...]: ...

    async def get_subscription(
        self, subscription_id: UUID, *, tenant_id: str
    ) -> WebhookSubscription: ...

    async def rotate_subscription(
        self,
        subscription_id: UUID,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int,
    ) -> WebhookSubscription: ...

    async def prepare_deliveries(self, *, tenant_id: str, limit: int) -> int: ...

    async def enqueue_test(
        self, subscription_id: UUID, *, tenant_id: str, actor_id: str
    ) -> WebhookDelivery: ...

    async def replay_delivery(
        self, delivery_id: UUID, *, tenant_id: str, actor_id: str
    ) -> WebhookDelivery: ...

    async def claim_deliveries(
        self, *, tenant_id: str, worker_id: str, limit: int
    ) -> tuple[WebhookDeliveryClaim, ...]: ...

    async def record_delivery_result(
        self,
        claim: WebhookDeliveryClaim,
        *,
        request_timestamp: int,
        response_status: int | None,
        error_code: str | None,
        duration_ms: int,
    ) -> WebhookDelivery: ...

    async def list_delivery_history(
        self, subscription_id: UUID, *, tenant_id: str, limit: int = 100
    ) -> tuple[WebhookDeliveryHistory, ...]: ...

    async def get_delivery(self, delivery_id: UUID, *, tenant_id: str) -> WebhookDelivery: ...


__all__ = ["RealtimeRepository"]
