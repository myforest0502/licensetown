"""READ ONLY simulation of PREREQUISITE backtrack candidate selection."""

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
from prerequisite_backtrack import simulate_prerequisite_backtrack_selection
from scripts.simulate_prerequisite_diagnosis import load_attempts_read_only


def run_simulation(connection=None) -> dict[str, Any]:
    if connection is None:
        if not database.database_is_available():
            raise RuntimeError("DATABASE_URL is required for production simulation")
        with database.get_db_connection() as created_connection:
            attempts = load_attempts_read_only(created_connection)
    else:
        attempts = load_attempts_read_only(connection)
    return simulate_prerequisite_backtrack_selection(
        attempts,
        get_reviewed_node_relations(),
    )


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
