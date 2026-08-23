from __future__ import annotations

import json
import os

from amesh_client.execution import verify_webhook


def consume(headers: dict[str, str], raw_body: bytes) -> dict[str, object]:
    timestamp = int(headers["x-amesh-timestamp"])
    delivery_id = headers["x-amesh-delivery-id"]
    if not verify_webhook(
        os.environ["AMESH_WEBHOOK_SECRET"],
        timestamp,
        delivery_id,
        raw_body,
        headers["x-amesh-signature"],
    ):
        raise PermissionError("invalid AMESH webhook signature")
    return json.loads(raw_body)
