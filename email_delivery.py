"""Transactional email delivery for LicenseTown feedback replies.

Neon remains the source of truth. When a requester supplied an email address,
LicenseTown also delivers the stored operator reply to that address.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Any

import requests


_PRIMITIVE_SEND_URL = "https://api.primitive.dev/v1/send-mail"
_DEFAULT_FROM = "LicenseTown <agent@thin-snail.primitive.email>"
_SUCCESS_STATUSES = {"delivered"}
_PENDING_STATUSES = {"queued", "submitted_to_agent", "deferred", "wait_timeout", "unknown"}


class EmailDeliveryError(RuntimeError):
    """Raised when the provider cannot accept or deliver a feedback reply."""


@dataclass(frozen=True)
class EmailDeliveryResult:
    delivery_state: str
    provider_status: str
    provider_message_id: str | None = None


def email_delivery_configured() -> bool:
    return bool(str(os.getenv("PRIMITIVE_API_KEY") or "").strip())


def _idempotency_key(public_id: str, reply: str) -> str:
    digest = hashlib.sha256(reply.encode("utf-8")).hexdigest()[:20]
    return f"lt-feedback-{public_id}-{digest}"


def send_feedback_reply(
    *,
    public_id: str,
    to_email: str,
    reply: str,
    timeout_seconds: float = 20.0,
) -> EmailDeliveryResult:
    """Send the exact stored operator reply through Primitive.

    The request uses Primitive's idempotency support so a retry with the same
    receipt number and reply body does not create a duplicate message.
    """

    api_key = str(os.getenv("PRIMITIVE_API_KEY") or "").strip()
    if not api_key:
        raise EmailDeliveryError("PRIMITIVE_API_KEY が設定されていません。")

    from_address = str(os.getenv("LT_FEEDBACK_EMAIL_FROM") or _DEFAULT_FROM).strip()
    subject = f"【LicenseTown】お問い合わせへの返信 {public_id}"
    body_text = (
        "お問い合わせありがとうございます。\n\n"
        f"{reply.strip()}\n\n"
        f"受付番号: {public_id}\n\n"
        "※このメールが迷惑メールフォルダに入っていた場合は、"
        "「迷惑メールではない」に設定してください。\n"
        "LicenseTown"
    )
    payload: dict[str, Any] = {
        "from": from_address,
        "to": to_email,
        "subject": subject,
        "body_text": body_text,
        "wait": True,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Idempotency-Key": _idempotency_key(public_id, reply),
    }

    try:
        response = requests.post(
            _PRIMITIVE_SEND_URL,
            json=payload,
            headers=headers,
            timeout=timeout_seconds,
        )
    except requests.RequestException as exc:
        raise EmailDeliveryError("メール送信サービスに接続できませんでした。") from exc

    try:
        data = response.json()
    except ValueError:
        data = {}

    if response.status_code >= 400:
        message = str(data.get("message") or data.get("error_message") or "").strip()
        suffix = f" ({message})" if message else ""
        raise EmailDeliveryError(f"メール送信サービスが送信を受け付けませんでした{suffix}")

    inner = data.get("data") if isinstance(data.get("data"), dict) else data
    provider_status = str(
        inner.get("delivery_status") or inner.get("status") or "unknown"
    ).strip()
    message_id = str(inner.get("id") or "").strip() or None

    if provider_status in _SUCCESS_STATUSES:
        return EmailDeliveryResult("sent", provider_status, message_id)
    if provider_status in _PENDING_STATUSES:
        return EmailDeliveryResult("pending", provider_status, message_id)
    raise EmailDeliveryError(f"メール配送に失敗しました ({provider_status or 'unknown'})")
