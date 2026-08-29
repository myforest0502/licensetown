"""READ ONLY production simulation of repeated canonical-Node weakness."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import database
from knowledge_node_weakness_evidence import derive_repeated_weakness_evidence


ATTEMPT_COLUMNS = (
    "id", "event_key", "user_id", "question_id", "knowledge_node_id",
    "is_correct", "confidence", "attempted_at", "attempt_position",
)
REPORTED_LEVELS = (
    "SINGLE_WRONG",
    "REPEATED_SAME_QUESTION_WRONG",
    "CROSS_QUESTION_WRONG",
    "CROSS_QUESTION_CONFIDENT_WRONG",
    "MIXED_EVIDENCE",
)


def load_attempts_read_only(connection) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, event_key, user_id, question_id, knowledge_node_id,
                   is_correct, confidence, answered_at AS attempted_at,
                   attempt_position
            FROM question_attempts
            ORDER BY answered_at, event_key, attempt_position, id
            """
        )
        return [dict(zip(ATTEMPT_COLUMNS, row)) for row in cursor.fetchall()]


def build_report(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    evidence = derive_repeated_weakness_evidence(attempts)
    counts = Counter(item["evidence_level"] for item in evidence)
    kn1080 = [
        {key: value for key, value in item.items() if key != "evidence_reason"}
        for item in evidence
        if item["canonical_node_id"] == "KN1080"
    ]
    return {
        "total_question_attempts_scanned": len(attempts),
        "user_canonical_node_count": len(evidence),
        "evidence_level_counts": {level: counts[level] for level in REPORTED_LEVELS},
        "no_wrong_evidence_count": counts["NO_WRONG_EVIDENCE"],
        "kn1080": kn1080,
    }


def run_simulation(connection=None) -> dict[str, Any]:
    if connection is None:
        if not database.database_is_available():
            raise RuntimeError("DATABASE_URL is required for production simulation")
        with database.get_db_connection() as created_connection:
            attempts = load_attempts_read_only(created_connection)
    else:
        attempts = load_attempts_read_only(connection)
    return build_report(attempts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = run_simulation()
    except Exception as exc:
        print(f"simulation failed: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2, default=str)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
