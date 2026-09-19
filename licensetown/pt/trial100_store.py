"""Persistence adapter for Trial100 evidence.

The schema is applied explicitly from migrations/20260904_trial100_attempts.sql.
Importing this module never creates or alters Production tables.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Any, Mapping

import database
from trial100_evidence import normalize_trial100_record


_local_trial100_attempts: dict[tuple[str, str, str], dict[str, Any]] = {}


@contextmanager
def _connection_or_existing(connection=None):
    if connection is not None:
        yield connection
        return
    with database.get_db_connection() as created:
        yield created


def _local_key(record: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(record["user_id"]),
        str(record["test_date"]),
        str(record["source_version"]),
    )


def save_trial100_record(
    record: Mapping[str, Any],
    *,
    recorded_by: str | None = None,
    connection=None,
) -> dict[str, Any]:
    """Validate and store one real Trial100 result without inventing readiness."""
    normalized = normalize_trial100_record(record)
    actor = str(recorded_by or "").strip() or None

    if not database.database_is_available():
        key = _local_key(normalized)
        if key in _local_trial100_attempts:
            raise ValueError("duplicate Trial100 record")
        stored = {**normalized, "recorded_by": actor}
        _local_trial100_attempts[key] = stored
        return dict(stored)

    with _connection_or_existing(connection) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO trial100_attempts (
                    user_id,
                    test_date,
                    source_version,
                    total_questions,
                    correct_count,
                    completion_status,
                    duration_minutes,
                    supportive,
                    field_breakdown,
                    review_summary,
                    recorded_by
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s::jsonb, %s::jsonb, %s
                )
                RETURNING id
                """,
                (
                    normalized["user_id"],
                    normalized["test_date"],
                    normalized["source_version"],
                    normalized["total_questions"],
                    normalized["correct_count"],
                    normalized["completion_status"],
                    normalized["duration_minutes"],
                    normalized["supportive"],
                    json.dumps(normalized["field_breakdown"], ensure_ascii=False)
                    if normalized["field_breakdown"] is not None else None,
                    json.dumps(normalized["review_summary"], ensure_ascii=False)
                    if normalized["review_summary"] is not None else None,
                    actor,
                ),
            )
            row = cur.fetchone()
    return {**normalized, "id": int(row[0]), "recorded_by": actor}


def get_trial100_records(user_id: str, *, connection=None) -> list[dict[str, Any]]:
    """Return readiness-compatible Trial100 records, newest first."""
    user_id = str(user_id or "").strip()
    if not user_id:
        return []

    if not database.database_is_available():
        rows = [
            dict(record)
            for key, record in _local_trial100_attempts.items()
            if key[0] == user_id
        ]
        rows.sort(key=lambda item: (item["test_date"], item["source_version"]), reverse=True)
        return rows

    with _connection_or_existing(connection) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    user_id,
                    test_date,
                    source_version,
                    total_questions,
                    correct_count,
                    completion_status,
                    duration_minutes,
                    supportive,
                    field_breakdown,
                    review_summary,
                    recorded_by
                FROM trial100_attempts
                WHERE user_id = %s
                ORDER BY test_date DESC, id DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()

    result = []
    for row in rows:
        normalized = normalize_trial100_record({
            "user_id": row[1],
            "test_date": row[2],
            "source_version": row[3],
            "total_questions": row[4],
            "correct_count": row[5],
            "completion_status": row[6],
            "duration_minutes": row[7],
            "supportive": row[8],
            "field_breakdown": row[9],
            "review_summary": row[10],
        })
        result.append({**normalized, "id": int(row[0]), "recorded_by": row[11]})
    return result
