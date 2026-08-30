"""Offline/READ ONLY repairability audit; emits no personal identifiers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repairability import build_repairability_audit, summarize_repairability
from knowledge_node_state_transition import derive_all_user_node_states


def production_repairing_breakdown(user_id: str, records: list[dict]) -> dict[str, int]:
    """Read question_attempts via the existing SELECT-only accessor."""
    from database import get_question_attempts

    by_node = {item["canonical_node_id"]: item for item in records}
    attempts = get_question_attempts(user_id)
    states = derive_all_user_node_states(attempts)
    repairing = [item for item in states if item["state"] == "repairing"]
    result = {
        "repairing_node_count": len(repairing),
        "singleton_repairing_node_count": 0,
        "strong_alt_repairing_node_count": 0,
        "weak_only_repairing_node_count": 0,
        "same_question_only_repairing_node_count": 0,
        "currently_unrepairable_repairing_node_count": 0,
    }
    for state in repairing:
        canonical = str(canonicalize_knowledge_node_id(state["canonical_node_id"]))
        item = by_node.get(canonical)
        if not item:
            continue
        result["singleton_repairing_node_count"] += item["question_count"] == 1
        result["strong_alt_repairing_node_count"] += item["repairable"]
        result["weak_only_repairing_node_count"] += item["classification"] == "weak_alt_question_only"
        result["same_question_only_repairing_node_count"] += item["classification"] == "same_question_only"
        result["currently_unrepairable_repairing_node_count"] += item["currently_unrepairable"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", help="Optional internal lookup key; never emitted")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    records = build_repairability_audit()
    report = {
        "summary": summarize_repairability(records),
        "nodes": records,
        "production_repairing_breakdown": (
            production_repairing_breakdown(args.user_id, records) if args.user_id else None
        ),
        "safety": {
            "database_mode": "READ_ONLY",
            "formal_state_changes": 0,
            "adaptive_changes": 0,
            "user_identifiers_emitted": 0,
        },
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, default=str)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
