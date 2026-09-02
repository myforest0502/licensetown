from pathlib import Path

path = Path("adaptive_question_selector.py")
text = path.read_text(encoding="utf-8")
replacements = [
    (
        'REPAIR_REASONS = {\n    "safety_wrong", "confident_wrong", "cross_question_wrong", "repairing",\n    "previous_wrong_unconfirmed",\n}',
        'REPAIR_REASONS = {\n    "safety_wrong", "safety_unresolved", "confident_wrong",\n    "cross_question_wrong", "repairing", "previous_wrong_unconfirmed",\n}',
    ),
    (
        '        "wrong_questions": set(), "correct_questions": set(),\n        "confident_wrong": False, "uncertain_correct": False, "unknown": False,',
        '        "wrong_questions": set(), "evaluable_wrong_questions": set(),\n        "correct_questions": set(), "confident_wrong": False,\n        "uncertain_correct": False, "unknown": False,',
    ),
    (
        '        else:\n            summary["wrong_questions"].add(question_id)\n            summary["unknown"] = summary["unknown"] or is_unknown\n            summary["confident_wrong"] = (\n                summary["confident_wrong"] or item.get("confidence") == 1\n            )',
        '        else:\n            summary["wrong_questions"].add(question_id)\n            if not is_unknown:\n                summary["evaluable_wrong_questions"].add(question_id)\n            summary["unknown"] = summary["unknown"] or is_unknown\n            summary["confident_wrong"] = (\n                summary["confident_wrong"] or (not is_unknown and item.get("confidence") == 1)\n            )',
    ),
    (
        'def _priority(state: str, summary: dict[str, Any], safety: str) -> tuple[int, str, str]:\n    has_wrong = bool(summary["wrong_questions"])',
        'def _priority(state: str, summary: dict[str, Any], safety: str) -> tuple[int, str, str]:\n    has_wrong = bool(summary["wrong_questions"])\n    has_evaluable_wrong = bool(summary.get("evaluable_wrong_questions", summary["wrong_questions"]))',
    ),
    (
        '    if has_wrong and safety in {"critical", "high", "moderate"}:\n        return 1000, "safety_wrong", "repair"\n    if summary["confident_wrong"]:',
        '    if has_evaluable_wrong and safety in {"critical", "high", "moderate"}:\n        return 1000, "safety_wrong", "repair"\n    if summary["unknown"] and safety in {"critical", "high", "moderate"}:\n        return 1000, "safety_unresolved", "repair"\n    if summary["confident_wrong"]:',
    ),
    (
        '            "wrong_questions": set(), "correct_questions": set(),\n            "confident_wrong": False, "uncertain_correct": False, "unknown": False,',
        '            "wrong_questions": set(), "evaluable_wrong_questions": set(),\n            "correct_questions": set(), "confident_wrong": False,\n            "uncertain_correct": False, "unknown": False,',
    ),
    (
        '            item["priority_reason"] == "safety_wrong"\n            and item["canonical_node_id"] not in non_recent_nodes',
        '            item["priority_reason"] in {"safety_wrong", "safety_unresolved"}\n            and item["canonical_node_id"] not in non_recent_nodes',
    ),
]
for old, new in replacements:
    if new in text:
        continue
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"patch target count={count}: {old[:60]}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
