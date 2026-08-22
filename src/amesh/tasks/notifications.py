from __future__ import annotations

import asyncio
import smtplib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Any

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext, TaskHandler

from .http import HttpTaskPolicy, core_http_handler

_MAX_MESSAGE_BYTES = 1_048_576


@dataclass(frozen=True)
class SmtpDelivery:
    host: str
    port: int
    start_tls: bool
    username: str | None
    password: str | None


EmailSender = Callable[[EmailMessage, SmtpDelivery], Awaitable[None]]


def core_notification_handlers(
    *,
    http_policy: HttpTaskPolicy | None = None,
    http_client: Any | None = None,
    email_sender: EmailSender | None = None,
) -> dict[str, TaskHandler]:
    return {
        "core.notify.webhook": core_http_handler(http_client, policy=http_policy),
        "core.notify.email": _email_handler(email_sender or _smtp_send),
    }


def _email_handler(sender: EmailSender) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
        del context
        extra = task.model_extra or {}
        host = _required_string(extra, "smtpHost")
        port = extra.get("smtpPort", 587)
        if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65_535:
            raise ValueError("smtpPort must be between 1 and 65535")
        recipients = extra.get("recipients")
        if (
            not isinstance(recipients, list)
            or not recipients
            or not all(isinstance(item, str) and "@" in item for item in recipients)
        ):
            raise ValueError("email recipients must be a non-empty array of addresses")
        message = EmailMessage()
        message["From"] = _required_string(extra, "sender")
        message["To"] = ", ".join(recipients)
        message["Subject"] = _required_string(extra, "subject")
        text = _required_string(extra, "text")
        if len(text.encode("utf-8")) > _MAX_MESSAGE_BYTES:
            raise ValueError("email body exceeds the configured payload limit")
        message.set_content(text)
        auth = extra.get("auth", {})
        if not isinstance(auth, dict):
            raise ValueError("email auth must be an object")
        username = auth.get("username")
        password = auth.get("password")
        if (username is None) != (password is None) or (
            username is not None
            and (not isinstance(username, str) or not isinstance(password, str))
        ):
            raise ValueError("email auth requires string username and password together")
        await sender(
            message,
            SmtpDelivery(
                host=host,
                port=port,
                start_tls=bool(extra.get("startTls", True)),
                username=username,
                password=password,
            ),
        )
        return {"accepted": True, "recipients": recipients, "messageBytes": len(message.as_bytes())}

    return run


async def _smtp_send(message: EmailMessage, delivery: SmtpDelivery) -> None:
    def send() -> None:
        with smtplib.SMTP(delivery.host, delivery.port, timeout=30) as client:
            if delivery.start_tls:
                client.starttls()
            if delivery.username is not None and delivery.password is not None:
                client.login(delivery.username, delivery.password)
            client.send_message(message)

    await asyncio.to_thread(send)


def _required_string(extra: dict[str, Any], field: str) -> str:
    value = extra.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"email task requires {field}")
    return value
