"""READ ONLY simulation of canonical Knowledge Node state transitions."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import database
from knowledge_node_state_transition import STATES, derive_all_user_node_states


ATTEMPT_COLUMNS = (
    "id", "event_key", "user_id", "question_id", "knowledge_node_id",
    "is_correct", "confidence", "attempted_at", "attempt_position",
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


def _registry_node_count() -> int:
    records = json.loads(
        (ROOT / "data" / "question_bank" / "knowledge_nodes.json").read_text(encoding="utf-8")
    )
    return len(records)


def build_report(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    states = derive_all_user_node_states(attempts, as_of=datetime.now(timezone.utc))
    counts = Counter(item["state"] for item in states)
    user_count = len({str(item.get("user_id") or "") for item in attempts})
    registry_count = _registry_node_count()
    attempted_raw_node_slots = len({
        (str(item.get("user_id") or ""), str(item.get("knowledge_node_id") or ""))
        for item in attempts
        if item.get("knowledge_node_id")
    })
    return {
        "total_question_attempts_scanned": len(attempts),
        "user_count": user_count,
        "attempted_user_canonical_node_count": len(states),
        "state_counts": {state: counts[state] for state in STATES},
        "registry_node_count": registry_count,
        "attempted_raw_node_slots": attempted_raw_node_slots,
        "unseen_raw_node_slots": max(0, user_count * registry_count - attempted_raw_node_slots),
        "kn1080": [item for item in states if item["canonical_node_id"] == "KN1080"],
        "recheck_due_policy": {
            "implemented_in_production": False,
            "design": "stable and 30 days since last attempt",
        },
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
