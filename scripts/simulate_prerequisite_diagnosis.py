"""READ ONLY simulation of prerequisite diagnosis against question_attempts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import database
from knowledge_node_relations import get_reviewed_node_relations
from prerequisite_diagnosis import simulate_prerequisite_diagnoses


ATTEMPT_COLUMNS = (
    "id", "event_key", "user_id", "question_id", "knowledge_node_id",
    "is_correct", "confidence", "answered_at", "attempt_position",
)


def load_attempts_read_only(connection) -> list[dict[str, Any]]:
    """Issue exactly one SELECT and return no private answer content."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, event_key, user_id, question_id, knowledge_node_id,
                   is_correct, confidence, answered_at, attempt_position
            FROM question_attempts
            ORDER BY answered_at, event_key, attempt_position, id
            """
        )
        return [dict(zip(ATTEMPT_COLUMNS, row)) for row in cursor.fetchall()]


def run_simulation(connection=None) -> dict[str, Any]:
    if connection is None:
        if not database.database_is_available():
            raise RuntimeError("DATABASE_URL is required for production simulation")
        with database.get_db_connection() as created_connection:
            attempts = load_attempts_read_only(created_connection)
    else:
        attempts = load_attempts_read_only(connection)
    relations = [
        relation for relation in get_reviewed_node_relations()
        if relation["relation_type"] == "PREREQUISITE"
    ]
    return simulate_prerequisite_diagnoses(attempts, relations)


def main() -> int:
    try:
        report = run_simulation()
    except Exception as exc:
        print(f"simulation failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
