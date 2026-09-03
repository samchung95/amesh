from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.dsl import FlowDefinition
from amesh.ports.errors import NotFoundError
from amesh.ports.realtime_repository import RealtimeRepository
from amesh.ports.repository_support import AuditWrite
from amesh.realtime import (
    RealtimeEvent,
    RealtimeFilter,
    WebhookDelivery,
    WebhookDeliveryAttempt,
    WebhookDeliveryClaim,
    WebhookDeliveryHistory,
    WebhookDeliveryStatus,
    WebhookSubscription,
    WebhookSubscriptionCreate,
)
from amesh.workflow.data_contracts import sensitive_execution_values

from .repository_support import PostgresRepositoryBase, PostgresRepositoryServices

_LIST_EVENTS = text(
    """
    SELECT *
    FROM realtime_events
    WHERE tenant_id = :tenant_id
      AND cursor > :after_cursor
      AND (
          CAST(:namespace AS text) IS NULL
          OR namespace_name = CAST(:namespace AS text)
      )
      AND (CAST(:flow_id AS text) IS NULL OR flow_id = CAST(:flow_id AS text))
      AND (CAST(:execution_id AS uuid) IS NULL OR execution_id = CAST(:execution_id AS uuid))
      AND (
          cardinality(CAST(:event_types AS text[])) = 0
          OR event_type = ANY(CAST(:event_types AS text[]))
      )
      AND (
          cardinality(CAST(:severities AS text[])) = 0
          OR severity = ANY(CAST(:severities AS text[]))
      )
      AND (CAST(:include_audit AS boolean) OR event_type NOT LIKE 'audit.%')
    ORDER BY cursor
    LIMIT :limit
    """
)

_CURSOR_BOUNDS = text(
    """
    SELECT min(cursor) AS oldest_cursor, max(cursor) AS latest_cursor
    FROM realtime_events
    WHERE tenant_id = :tenant_id
    """
)

_INSERT_SUBSCRIPTION = text(
    """
    INSERT INTO webhook_subscriptions (
        id, tenant_id, name, url, filters, enabled, max_attempts, created_by, updated_by
    ) VALUES (
        :id, :tenant_id, :name, :url, CAST(:filters AS jsonb), :enabled,
        :max_attempts, :actor_id, :actor_id
    )
    RETURNING *
    """
)

_LIST_SUBSCRIPTIONS = text(
    """
    SELECT * FROM webhook_subscriptions
    WHERE tenant_id = :tenant_id
    ORDER BY name, id
    """
)

_GET_SUBSCRIPTION = text(
    """
    SELECT * FROM webhook_subscriptions
    WHERE tenant_id = :tenant_id AND id = :subscription_id
    """
)

_ROTATE_SUBSCRIPTION = text(
    """
    UPDATE webhook_subscriptions
    SET signing_version = signing_version + 1,
        resource_version = resource_version + 1,
        updated_by = :actor_id,
        updated_at = clock_timestamp()
    WHERE tenant_id = :tenant_id
      AND id = :subscription_id
      AND resource_version = :expected_version
    RETURNING *
    """
)

_LOCK_SUBSCRIPTIONS = text(
    """
    SELECT * FROM webhook_subscriptions
    WHERE tenant_id = :tenant_id AND enabled
    ORDER BY id
    FOR UPDATE
    """
)

_MAX_CURSOR = text(
    "SELECT COALESCE(max(cursor), 0) FROM realtime_events WHERE tenant_id = :tenant_id"
)

_INSERT_EVENT_DELIVERY = text(
    """
    INSERT INTO webhook_deliveries (
        id, tenant_id, subscription_id, event_cursor, event_id, event_type,
        event_occurred_at, payload, delivery_kind, signing_version
    ) VALUES (
        :id, :tenant_id, :subscription_id, :event_cursor, :event_id, :event_type,
        :event_occurred_at, CAST(:payload AS jsonb), 'EVENT', :signing_version
    )
    ON CONFLICT (tenant_id, subscription_id, event_cursor) DO NOTHING
    """
)

_ADVANCE_SUBSCRIPTION = text(
    """
    UPDATE webhook_subscriptions
    SET last_enqueued_cursor = GREATEST(last_enqueued_cursor, :cursor),
        updated_at = clock_timestamp()
    WHERE tenant_id = :tenant_id AND id = :subscription_id
    """
)

_INSERT_TEST_DELIVERY = text(
    """
    INSERT INTO webhook_deliveries (
        id, tenant_id, subscription_id, event_type, event_occurred_at,
        payload, delivery_kind, signing_version
    )
    SELECT :id, tenant_id, id, 'webhook.test', :occurred_at,
           CAST(:payload AS jsonb), 'TEST', signing_version
    FROM webhook_subscriptions
    WHERE tenant_id = :tenant_id AND id = :subscription_id
    RETURNING *
    """
)

_INSERT_REPLAY_DELIVERY = text(
    """
    INSERT INTO webhook_deliveries (
        id, tenant_id, subscription_id, event_cursor, event_id, event_type,
        event_occurred_at, payload, delivery_kind, original_delivery_id, signing_version
    )
    SELECT :new_id, original.tenant_id, original.subscription_id, NULL,
           original.event_id, original.event_type, original.event_occurred_at,
           original.payload, 'REPLAY', original.id, subscription.signing_version
    FROM webhook_deliveries AS original
    JOIN webhook_subscriptions AS subscription
      ON subscription.tenant_id = original.tenant_id
     AND subscription.id = original.subscription_id
    WHERE original.tenant_id = :tenant_id AND original.id = :delivery_id
    RETURNING webhook_deliveries.*
    """
)

_CLAIM_DELIVERIES = text(
    """
    WITH candidate AS (
        SELECT delivery.id
        FROM webhook_deliveries AS delivery
        WHERE delivery.tenant_id = :tenant_id
          AND (
              delivery.status IN ('PENDING', 'RETRY')
              OR (delivery.status = 'DELIVERING' AND delivery.locked_until <= clock_timestamp())
          )
          AND delivery.next_attempt_at <= clock_timestamp()
        ORDER BY delivery.next_attempt_at, delivery.created_at, delivery.id
        FOR UPDATE SKIP LOCKED
        LIMIT :limit
    )
    UPDATE webhook_deliveries AS delivery
    SET status = 'DELIVERING',
        attempts = delivery.attempts + 1,
        locked_by = :worker_id,
        locked_until = clock_timestamp() + interval '60 seconds'
    FROM candidate, webhook_subscriptions AS subscription
    WHERE delivery.id = candidate.id
      AND subscription.tenant_id = delivery.tenant_id
      AND subscription.id = delivery.subscription_id
    RETURNING delivery.*, subscription.url, subscription.max_attempts
    """
)

_SENSITIVE_EVENT_CONTEXTS = text(
    """
    SELECT event.event_id, execution.inputs, execution.outputs,
           revision.canonical_definition
    FROM realtime_events AS event
    JOIN executions AS execution
      ON execution.tenant_id = event.tenant_id
     AND execution.id = event.execution_id
    JOIN flow_revisions AS revision
      ON revision.tenant_id = execution.tenant_id
     AND revision.id = execution.flow_revision_id
    WHERE event.tenant_id = :tenant_id
      AND event.event_id = ANY(CAST(:event_ids AS uuid[]))
    """
)

_UPDATE_DELIVERY_RESULT = text(
    """
    UPDATE webhook_deliveries
    SET status = :status,
        next_attempt_at = CASE
            WHEN :status = 'RETRY'
            THEN clock_timestamp() + make_interval(secs => LEAST(300, (2 ^ LEAST(attempts, 8))::int))
            ELSE next_attempt_at
        END,
        locked_by = NULL,
        locked_until = NULL,
        response_status = :response_status,
        error_code = :error_code,
        delivered_at = CASE WHEN :status = 'DELIVERED' THEN clock_timestamp() ELSE NULL END
    WHERE tenant_id = :tenant_id AND id = :delivery_id AND attempts = :attempt
    RETURNING *
    """
)

_INSERT_DELIVERY_ATTEMPT = text(
    """
    INSERT INTO webhook_delivery_attempts (
        delivery_id, attempt, tenant_id, request_timestamp, response_status,
        outcome, error_code, duration_ms
    ) VALUES (
        :delivery_id, :attempt, :tenant_id, :request_timestamp, :response_status,
        :outcome, :error_code, :duration_ms
    )
    ON CONFLICT (delivery_id, attempt) DO NOTHING
    """
)

_LIST_DELIVERIES = text(
    """
    SELECT * FROM webhook_deliveries
    WHERE tenant_id = :tenant_id AND subscription_id = :subscription_id
    ORDER BY created_at DESC, id DESC
    LIMIT :limit
    """
)

_GET_DELIVERY = text(
    """
    SELECT * FROM webhook_deliveries
    WHERE tenant_id = :tenant_id AND id = :delivery_id
    """
)

_LIST_ATTEMPTS = text(
    """
    SELECT * FROM webhook_delivery_attempts
    WHERE tenant_id = :tenant_id AND delivery_id = ANY(CAST(:delivery_ids AS uuid[]))
    ORDER BY delivery_id, attempt
    """
)


class PostgresRealtimeRepository(PostgresRepositoryBase, RealtimeRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def list_events(
        self,
        *,
        tenant_id: str,
        after_cursor: int,
        filters: RealtimeFilter,
        limit: int,
    ) -> tuple[RealtimeEvent, ...]:
        if after_cursor < 0:
            raise ValueError("realtime cursor cannot be negative")
        if not 1 <= limit <= 1000:
            raise ValueError("realtime event limit must be between 1 and 1000")
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _LIST_EVENTS,
                        _event_parameters(
                            tenant_uuid,
                            after_cursor=after_cursor,
                            filters=filters,
                            limit=limit,
                        ),
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_to_event(row) for row in rows)

    async def cursor_bounds(self, *, tenant_id: str) -> tuple[int | None, int | None]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (await connection.execute(_CURSOR_BOUNDS, {"tenant_id": tenant_uuid}))
                .mappings()
                .one()
            )
        return row["oldest_cursor"], row["latest_cursor"]

    async def create_subscription(
        self,
        request: WebhookSubscriptionCreate,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> WebhookSubscription:
        subscription_id = new_runtime_id()
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _INSERT_SUBSCRIPTION,
                        {
                            "id": subscription_id,
                            "tenant_id": tenant_uuid,
                            "name": request.name,
                            "url": request.url,
                            "filters": request.filters.model_dump_json(by_alias=True),
                            "enabled": request.enabled,
                            "max_attempts": request.max_attempts,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await _audit(
                connection,
                self._services,
                tenant_uuid=tenant_uuid,
                actor_id=actor_id,
                action="webhook_subscription.create",
                resource_id=str(subscription_id),
                reason="outbound webhook subscription created",
                source={"namespace": request.filters.namespace},
                evidence={"name": request.name, "urlHost": request.url.split("/", 3)[2]},
            )
        return _to_subscription(row)

    async def list_subscriptions(self, *, tenant_id: str) -> tuple[WebhookSubscription, ...]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                (await connection.execute(_LIST_SUBSCRIPTIONS, {"tenant_id": tenant_uuid}))
                .mappings()
                .all()
            )
        return tuple(_to_subscription(row) for row in rows)

    async def get_subscription(
        self, subscription_id: UUID, *, tenant_id: str
    ) -> WebhookSubscription:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _GET_SUBSCRIPTION,
                        {"tenant_id": tenant_uuid, "subscription_id": subscription_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise NotFoundError(
                "webhook subscription",
                subscription_id,
                message="webhook subscription does not exist",
            )
        return _to_subscription(row)

    async def rotate_subscription(
        self,
        subscription_id: UUID,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int,
    ) -> WebhookSubscription:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _ROTATE_SUBSCRIPTION,
                        {
                            "tenant_id": tenant_uuid,
                            "subscription_id": subscription_id,
                            "actor_id": actor_id,
                            "expected_version": expected_version,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise NotFoundError(
                    "webhook subscription",
                    subscription_id,
                    message="webhook subscription does not exist or version changed",
                )
            await _audit(
                connection,
                self._services,
                tenant_uuid=tenant_uuid,
                actor_id=actor_id,
                action="webhook_subscription.rotate",
                resource_id=str(subscription_id),
                reason="outbound webhook signing secret rotated",
                source={},
                evidence={"signingVersion": row["signing_version"]},
            )
        return _to_subscription(row)

    async def prepare_deliveries(self, *, tenant_id: str, limit: int) -> int:
        prepared = 0
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            subscriptions = (
                (await connection.execute(_LOCK_SUBSCRIPTIONS, {"tenant_id": tenant_uuid}))
                .mappings()
                .all()
            )
            maximum_cursor = int(
                await connection.scalar(_MAX_CURSOR, {"tenant_id": tenant_uuid}) or 0
            )
            for subscription in subscriptions:
                filters = RealtimeFilter.model_validate(subscription["filters"])
                events = (
                    (
                        await connection.execute(
                            _LIST_EVENTS,
                            _event_parameters(
                                tenant_uuid,
                                after_cursor=int(subscription["last_enqueued_cursor"]),
                                filters=filters,
                                limit=limit,
                            ),
                        )
                    )
                    .mappings()
                    .all()
                )
                for event in events:
                    result = await connection.execute(
                        _INSERT_EVENT_DELIVERY,
                        {
                            "id": new_runtime_id(),
                            "tenant_id": tenant_uuid,
                            "subscription_id": subscription["id"],
                            "event_cursor": event["cursor"],
                            "event_id": event["event_id"],
                            "event_type": event["event_type"],
                            "event_occurred_at": event["occurred_at"],
                            "payload": self._services.codec.dumps(event["payload"]),
                            "signing_version": subscription["signing_version"],
                        },
                    )
                    prepared += result.rowcount
                advanced_cursor = int(events[-1]["cursor"]) if events else maximum_cursor
                await connection.execute(
                    _ADVANCE_SUBSCRIPTION,
                    {
                        "tenant_id": tenant_uuid,
                        "subscription_id": subscription["id"],
                        "cursor": advanced_cursor,
                    },
                )
        return prepared

    async def enqueue_test(
        self,
        subscription_id: UUID,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> WebhookDelivery:
        delivery_id = new_runtime_id()
        occurred_at = self._services.clock.now()
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _INSERT_TEST_DELIVERY,
                        {
                            "id": delivery_id,
                            "tenant_id": tenant_uuid,
                            "subscription_id": subscription_id,
                            "occurred_at": occurred_at,
                            "payload": self._services.codec.dumps(
                                {"test": True, "requestedBy": actor_id}
                            ),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise NotFoundError(
                "webhook subscription",
                subscription_id,
                message="webhook subscription does not exist",
            )
        return _to_delivery(row)

    async def replay_delivery(
        self,
        delivery_id: UUID,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> WebhookDelivery:
        replay_id = new_runtime_id()
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _INSERT_REPLAY_DELIVERY,
                        {
                            "new_id": replay_id,
                            "tenant_id": tenant_uuid,
                            "delivery_id": delivery_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise NotFoundError(
                    "webhook delivery",
                    delivery_id,
                    message="webhook delivery does not exist",
                )
            await _audit(
                connection,
                self._services,
                tenant_uuid=tenant_uuid,
                actor_id=actor_id,
                action="webhook_delivery.replay",
                resource_id=str(row["subscription_id"]),
                reason="selected webhook delivery replayed",
                source={},
                evidence={"deliveryId": str(delivery_id), "replayId": str(replay_id)},
            )
        return _to_delivery(row)

    async def claim_deliveries(
        self,
        *,
        tenant_id: str,
        worker_id: str,
        limit: int,
    ) -> tuple[WebhookDeliveryClaim, ...]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _CLAIM_DELIVERIES,
                        {
                            "tenant_id": tenant_uuid,
                            "worker_id": worker_id,
                            "limit": limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
            event_ids = [row["event_id"] for row in rows if row["event_id"] is not None]
            contexts = (
                (
                    await connection.execute(
                        _SENSITIVE_EVENT_CONTEXTS,
                        {"tenant_id": tenant_uuid, "event_ids": event_ids},
                    )
                )
                .mappings()
                .all()
                if event_ids
                else []
            )
        sensitive_by_event = {
            row["event_id"]: tuple(
                item
                for item in sensitive_execution_values(
                    FlowDefinition.model_validate(row["canonical_definition"]),
                    row["inputs"],
                    row["outputs"],
                )
                if isinstance(item, str)
            )
            for row in contexts
        }
        return tuple(
            WebhookDeliveryClaim(
                tenantId=tenant_id,
                id=row["id"],
                subscriptionId=row["subscription_id"],
                url=row["url"],
                maxAttempts=row["max_attempts"],
                signingVersion=row["signing_version"],
                attempt=row["attempts"],
                eventCursor=row["event_cursor"],
                eventId=row["event_id"],
                eventType=row["event_type"],
                eventOccurredAt=row["event_occurred_at"],
                payload=row["payload"],
                sensitiveValues=sensitive_by_event.get(row["event_id"], ()),
                deliveryKind=row["delivery_kind"],
            )
            for row in rows
        )

    async def record_delivery_result(
        self,
        claim: WebhookDeliveryClaim,
        *,
        request_timestamp: int,
        response_status: int | None,
        error_code: str | None,
        duration_ms: int,
    ) -> WebhookDelivery:
        outcome = (
            WebhookDeliveryStatus.DELIVERED
            if error_code is None and response_status is not None and 200 <= response_status < 300
            else (
                WebhookDeliveryStatus.RETRY
                if claim.attempt < claim.max_attempts
                else WebhookDeliveryStatus.FAILED
            )
        )
        async with self._services.transactions.tenant(claim.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            row = (
                (
                    await connection.execute(
                        _UPDATE_DELIVERY_RESULT,
                        {
                            "tenant_id": tenant_uuid,
                            "delivery_id": claim.delivery_id,
                            "attempt": claim.attempt,
                            "status": outcome.value,
                            "response_status": response_status,
                            "error_code": error_code,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise NotFoundError(
                    "webhook delivery claim",
                    claim.delivery_id,
                    message="webhook delivery claim is stale",
                )
            await connection.execute(
                _INSERT_DELIVERY_ATTEMPT,
                {
                    "delivery_id": claim.delivery_id,
                    "attempt": claim.attempt,
                    "tenant_id": tenant_uuid,
                    "request_timestamp": request_timestamp,
                    "response_status": response_status,
                    "outcome": outcome.value,
                    "error_code": error_code,
                    "duration_ms": duration_ms,
                },
            )
        return _to_delivery(row)

    async def list_delivery_history(
        self,
        subscription_id: UUID,
        *,
        tenant_id: str,
        limit: int = 100,
    ) -> tuple[WebhookDeliveryHistory, ...]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            deliveries = (
                (
                    await connection.execute(
                        _LIST_DELIVERIES,
                        {
                            "tenant_id": tenant_uuid,
                            "subscription_id": subscription_id,
                            "limit": limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
            delivery_ids = [row["id"] for row in deliveries]
            attempts = (
                (
                    await connection.execute(
                        _LIST_ATTEMPTS,
                        {"tenant_id": tenant_uuid, "delivery_ids": delivery_ids},
                    )
                )
                .mappings()
                .all()
                if delivery_ids
                else []
            )
        attempts_by_delivery: dict[UUID, list[WebhookDeliveryAttempt]] = {}
        for row in attempts:
            attempts_by_delivery.setdefault(row["delivery_id"], []).append(_to_attempt(row))
        return tuple(
            WebhookDeliveryHistory(
                delivery=_to_delivery(row),
                attempts=tuple(attempts_by_delivery.get(row["id"], [])),
            )
            for row in deliveries
        )

    async def get_delivery(self, delivery_id: UUID, *, tenant_id: str) -> WebhookDelivery:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _GET_DELIVERY,
                        {"tenant_id": tenant_uuid, "delivery_id": delivery_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise NotFoundError(
                "webhook delivery",
                delivery_id,
                message="webhook delivery does not exist",
            )
        return _to_delivery(row)


def _event_parameters(
    tenant_uuid: UUID,
    *,
    after_cursor: int,
    filters: RealtimeFilter,
    limit: int,
) -> dict[str, object]:
    return {
        "tenant_id": tenant_uuid,
        "after_cursor": after_cursor,
        "namespace": filters.namespace,
        "flow_id": filters.flow_id,
        "execution_id": str(filters.execution_id) if filters.execution_id is not None else None,
        "event_types": list(filters.event_types),
        "severities": [item.value for item in filters.severities],
        "include_audit": filters.include_audit,
        "limit": limit,
    }


async def _audit(
    connection: AsyncConnection,
    services: PostgresRepositoryServices,
    *,
    tenant_uuid: UUID,
    actor_id: str,
    action: str,
    resource_id: str,
    reason: str,
    source: dict[str, object],
    evidence: dict[str, object],
) -> None:
    await services.audit.write(
        connection,
        AuditWrite(
            tenant_id=tenant_uuid,
            actor_id=actor_id,
            action=action,
            resource_type="webhook_subscription",
            resource_id=resource_id,
            outcome="SUCCESS",
            reason=reason,
            source=source,
            evidence=evidence,
            event_id=new_runtime_id(),
            generate_correlation_id=False,
            use_database_clock=True,
        ),
    )


def _to_event(row: RowMapping) -> RealtimeEvent:
    return RealtimeEvent(
        cursor=row["cursor"],
        eventId=row["event_id"],
        namespace=row["namespace_name"],
        flowId=row["flow_id"],
        executionId=row["execution_id"],
        taskRunId=row["task_run_id"],
        eventType=row["event_type"],
        severity=row["severity"],
        payload=row["payload"],
        occurredAt=row["occurred_at"],
        ingestedAt=row["ingested_at"],
    )


def _to_subscription(row: RowMapping) -> WebhookSubscription:
    return WebhookSubscription(
        id=row["id"],
        name=row["name"],
        url=row["url"],
        filters=row["filters"],
        enabled=row["enabled"],
        maxAttempts=row["max_attempts"],
        signingVersion=row["signing_version"],
        lastEnqueuedCursor=row["last_enqueued_cursor"],
        resourceVersion=row["resource_version"],
        createdBy=row["created_by"],
        updatedBy=row["updated_by"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
    )


def _to_delivery(row: RowMapping) -> WebhookDelivery:
    return WebhookDelivery(
        id=row["id"],
        subscriptionId=row["subscription_id"],
        eventCursor=row["event_cursor"],
        eventId=row["event_id"],
        eventType=row["event_type"],
        eventOccurredAt=row["event_occurred_at"],
        deliveryKind=row["delivery_kind"],
        originalDeliveryId=row["original_delivery_id"],
        signingVersion=row["signing_version"],
        status=row["status"],
        attempts=row["attempts"],
        nextAttemptAt=row["next_attempt_at"],
        responseStatus=row["response_status"],
        errorCode=row["error_code"],
        createdAt=row["created_at"],
        deliveredAt=row["delivered_at"],
    )


def _to_attempt(row: RowMapping) -> WebhookDeliveryAttempt:
    return WebhookDeliveryAttempt(
        deliveryId=row["delivery_id"],
        attempt=row["attempt"],
        requestTimestamp=row["request_timestamp"],
        responseStatus=row["response_status"],
        outcome=row["outcome"],
        errorCode=row["error_code"],
        attemptedAt=row["attempted_at"],
        durationMs=row["duration_ms"],
    )
