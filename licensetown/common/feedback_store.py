"""Persistence helpers for LicenseTown public feedback.

Neon is the authoritative copy of every inquiry and operator reply. When a
requester supplied an email address, email delivery is also required and its
state is recorded alongside the stored reply.
"""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from database import database_is_available, get_db_connection


VALID_CATEGORIES = {
    "bug": "不具合",
    "request": "ご要望",
    "usage": "使い方について",
    "other": "その他",
}
VALID_STATUSES = {"received", "reviewing", "planned", "responded", "closed"}
VALID_EMAIL_DELIVERY_STATUSES = {"not_requested", "pending", "sent", "failed"}

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class FeedbackError(RuntimeError):
    """Base error for feedback operations."""


class FeedbackValidationError(FeedbackError):
    """Raised when submitted feedback is invalid."""


class FeedbackStoreUnavailable(FeedbackError):
    """Raised when the database is not configured."""


@dataclass(frozen=True)
class FeedbackReceipt:
    public_id: str
    tracking_token: str
    created_at: datetime


def _clean_optional(value: str | None, *, max_length: int) -> str | None:
    cleaned = str(value or "").strip()
    if not cleaned:
        return None
    if len(cleaned) > max_length:
        raise FeedbackValidationError("入力が長すぎます。")
    return cleaned


def _clean_required(value: str | None, *, max_length: int, message: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise FeedbackValidationError(message)
    if len(cleaned) > max_length:
        raise FeedbackValidationError("入力が長すぎます。")
    return cleaned


def validate_feedback(*, name: str | None, email: str | None, category: str | None, message: str | None) -> dict[str, str | None]:
    cleaned_name = _clean_optional(name, max_length=80)
    cleaned_email = _clean_optional(email, max_length=254)
    cleaned_category = _clean_required(category, max_length=32, message="お問い合わせ種類を選んでください。")
    cleaned_message = _clean_required(message, max_length=4000, message="お問い合わせ内容を入力してください。")

    if cleaned_category not in VALID_CATEGORIES:
        raise FeedbackValidationError("お問い合わせ種類を選び直してください。")
    if cleaned_email and not _EMAIL_RE.match(cleaned_email):
        raise FeedbackValidationError("メールアドレスの形式を確認してください。")

    return {
        "name": cleaned_name,
        "email": cleaned_email,
        "category": cleaned_category,
        "message": cleaned_message,
    }


def _new_public_id(now: datetime) -> str:
    return f"LT-{now:%Y%m%d}-{secrets.token_hex(4).upper()}"


def create_feedback(
    *,
    name: str | None,
    email: str | None,
    category: str | None,
    message: str | None,
    source: str = "web",
    page_path: str | None = None,
    line_user_id: str | None = None,
) -> FeedbackReceipt:
    values = validate_feedback(name=name, email=email, category=category, message=message)
    if not database_is_available():
        raise FeedbackStoreUnavailable("お問い合わせの保存先に接続できません。")

    now = datetime.now(timezone.utc)
    tracking_token = secrets.token_urlsafe(32)
    source_value = _clean_required(source, max_length=32, message="送信元が不明です。")
    page_value = _clean_optional(page_path, max_length=240)
    line_value = _clean_optional(line_user_id, max_length=160)

    for _ in range(4):
        public_id = _new_public_id(now)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO feedback_inbox (
                            public_id, tracking_token, source, name, email,
                            category, message, page_path, line_user_id
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING created_at
                        """,
                        (
                            public_id,
                            tracking_token,
                            source_value,
                            values["name"],
                            values["email"],
                            values["category"],
                            values["message"],
                            page_value,
                            line_value,
                        ),
                    )
                    created_at = cur.fetchone()[0]
                conn.commit()
            return FeedbackReceipt(
                public_id=public_id,
                tracking_token=tracking_token,
                created_at=created_at,
            )
        except Exception as exc:
            if getattr(exc, "sqlstate", None) == "23505" and "public_id" in str(exc):
                continue
            raise

    raise FeedbackError("受付番号を発行できませんでした。")


def get_feedback_for_public_status(tracking_token: str | None) -> dict[str, Any] | None:
    token = str(tracking_token or "").strip()
    if not token or len(token) > 128:
        return None
    if not database_is_available():
        raise FeedbackStoreUnavailable("お問い合わせの保存先に接続できません。")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT public_id, category, status, operator_reply,
                       created_at, updated_at, replied_at
                FROM feedback_inbox
                WHERE tracking_token = %s
                """,
                (token,),
            )
            row = cur.fetchone()
    if not row:
        return None
    return {
        "public_id": row[0],
        "category": row[1],
        "status": row[2],
        "operator_reply": row[3],
        "created_at": row[4],
        "updated_at": row[5],
        "replied_at": row[6],
    }


def list_feedback_for_operator(*, limit: int = 100) -> list[dict[str, Any]]:
    if not database_is_available():
        raise FeedbackStoreUnavailable("お問い合わせの保存先に接続できません。")
    safe_limit = min(max(int(limit), 1), 200)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT public_id, name, email, category, message, status,
                       operator_reply, email_delivery_status, email_sent_at,
                       created_at, updated_at, replied_at, tracking_token
                FROM feedback_inbox
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (safe_limit,),
            )
            rows = cur.fetchall()
    return [
        {
            "public_id": row[0],
            "name": row[1],
            "email": row[2],
            "category": row[3],
            "message": row[4],
            "status": row[5],
            "operator_reply": row[6],
            "email_delivery_status": row[7],
            "email_sent_at": row[8],
            "created_at": row[9],
            "updated_at": row[10],
            "replied_at": row[11],
            "tracking_token": row[12],
        }
        for row in rows
    ]


def get_feedback_for_operator(public_id: str | None) -> dict[str, Any] | None:
    public_id_value = str(public_id or "").strip()
    if not public_id_value or len(public_id_value) > 40:
        return None
    items = list_feedback_for_operator(limit=200)
    return next((item for item in items if item["public_id"] == public_id_value), None)


def set_operator_reply(
    *,
    public_id: str,
    reply: str,
    status: str = "responded",
) -> dict[str, Any] | None:
    """Store the reply first; email delivery follows from this stored text."""

    public_id_value = _clean_required(public_id, max_length=40, message="受付番号が必要です。")
    reply_value = _clean_required(reply, max_length=8000, message="返信内容が必要です。")
    if status not in VALID_STATUSES:
        raise FeedbackValidationError("対応状況が不正です。")
    if not database_is_available():
        raise FeedbackStoreUnavailable("お問い合わせの保存先に接続できません。")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE feedback_inbox
                SET operator_reply = %s,
                    status = %s,
                    replied_at = NOW(),
                    updated_at = NOW(),
                    email_delivery_status = CASE
                        WHEN email IS NULL THEN 'not_requested'
                        ELSE 'pending'
                    END,
                    email_sent_at = NULL
                WHERE public_id = %s
                RETURNING public_id, email, operator_reply, status,
                          tracking_token, email_delivery_status
                """,
                (reply_value, status, public_id_value),
            )
            row = cur.fetchone()
        conn.commit()
    if not row:
        return None
    return {
        "public_id": row[0],
        "email": row[1],
        "operator_reply": row[2],
        "status": row[3],
        "tracking_token": row[4],
        "email_delivery_status": row[5],
    }


def mark_email_delivery(*, public_id: str, delivery_status: str) -> bool:
    public_id_value = _clean_required(public_id, max_length=40, message="受付番号が必要です。")
    if delivery_status not in VALID_EMAIL_DELIVERY_STATUSES:
        raise FeedbackValidationError("メール配送状況が不正です。")
    if not database_is_available():
        raise FeedbackStoreUnavailable("お問い合わせの保存先に接続できません。")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE feedback_inbox
                SET email_delivery_status = %s,
                    email_sent_at = CASE
                        WHEN %s = 'sent' THEN NOW()
                        WHEN %s IN ('failed', 'not_requested') THEN NULL
                        ELSE email_sent_at
                    END,
                    updated_at = NOW()
                WHERE public_id = %s
                """,
                (delivery_status, delivery_status, delivery_status, public_id_value),
            )
            updated = cur.rowcount > 0
        conn.commit()
    return updated
