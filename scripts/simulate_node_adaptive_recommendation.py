"""READ ONLY comparison of legacy and Node-adaptive 30-question selection."""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import database
from adaptive_question_selector import select_node_adaptive_questions
from learning_engine import build_daily_session


ATTEMPT_COLUMNS = ("event_key", "user_id", "question_id", "knowledge_node_id",
                   "is_correct", "confidence", "answered_at", "attempt_position")


def load_attempts_read_only(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT event_key, user_id, question_id, knowledge_node_id,
                      is_correct, confidence, answered_at, attempt_position
               FROM question_attempts
               ORDER BY answered_at, event_key, attempt_position"""
        )
        return [dict(zip(ATTEMPT_COLUMNS, row)) for row in cursor.fetchall()]


def _build_user_report(attempts):
    adaptive = select_node_adaptive_questions(attempts, 30, rng=random.Random(0))
    legacy_history = [
        {
            "question_id": item["question_id"],
            "knowledge_node_id": item["knowledge_node_id"],
            "is_correct": item["is_correct"],
            "confidence": item.get("confidence"),
            "answer_status": item.get("answer_status", "answered"),
        }
        for item in attempts
    ]
    legacy = build_daily_session(legacy_history, 30, rng=random.Random(0))
    return {
        "total_attempts": len(attempts),
        "legacy_question_ids": [item["id"] for item in legacy],
        "adaptive": [{key: value for key, value in item.items() if key != "tie"} for item in adaptive],
        "same_question_repeat_count": sum(item["same_question_repeat"] for item in adaptive),
        "cross_question_repair_candidate_count": sum(
            item["previous_wrong_count"] > 0 and not item["same_question_repeat"]
            for item in adaptive
        ),
        "unseen_count": sum(item["state"] == "unseen" for item in adaptive),
        "stable_count": sum(item["state"] == "stable" for item in adaptive),
    }


def build_report(attempts):
    grouped = defaultdict(list)
    for item in attempts:
        grouped[str(item.get("user_id") or "")].append(item)
    user_reports = [_build_user_report(items) for _user, items in sorted(grouped.items())]
    return {
        "user_count": len(user_reports),
        "total_attempts": len(attempts),
        "users": user_reports,
        "aggregate": {
            key: sum(report[key] for report in user_reports)
            for key in (
                "same_question_repeat_count",
                "cross_question_repair_candidate_count",
                "unseen_count",
                "stable_count",
            )
        },
    }


def main():
    if not database.database_is_available():
        print("simulation failed: DATABASE_URL is required", file=sys.stderr)
        return 2
    with database.get_db_connection() as connection:
        attempts = load_attempts_read_only(connection)
    print(json.dumps(build_report(attempts), ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
