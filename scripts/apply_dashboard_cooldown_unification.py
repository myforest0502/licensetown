from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected source block not found in {path}: {old[:120]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    replace_once(
        "adaptive_question_selector.py",
        "from question_bank import get_question_tag, get_quiz_question, question_ids\n",
        "from question_bank import get_category_small, get_question_tag, get_quiz_question, question_ids\n",
    )
    replace_once(
        "adaptive_question_selector.py",
        "    exclude_ids=(),\n    rng=None,\n    as_of: datetime | None = None,\n) -> list[dict[str, Any]]:\n",
        "    exclude_ids=(),\n    rng=None,\n    as_of: datetime | None = None,\n    category_small: int | None = None,\n) -> list[dict[str, Any]]:\n",
    )
    replace_once(
        "adaptive_question_selector.py",
        "    for question_id in question_ids():\n        if question_id in excluded:\n            continue\n        tag = get_question_tag(question_id)\n",
        "    for question_id in question_ids():\n        if question_id in excluded:\n            continue\n        if category_small is not None and get_category_small(question_id) != category_small:\n            continue\n        tag = get_question_tag(question_id)\n",
    )
    replace_once(
        "adaptive_question_selector.py",
        "def build_node_adaptive_session(\n    attempts, question_count=30, exclude_ids=(), rng=None, *, audit_out=None\n):\n    records = select_node_adaptive_questions(\n        attempts, question_count, exclude_ids=exclude_ids, rng=rng\n    )\n",
        "def build_node_adaptive_session(\n    attempts, question_count=30, exclude_ids=(), rng=None, *, audit_out=None,\n    category_small: int | None = None,\n):\n    records = select_node_adaptive_questions(\n        attempts, question_count, exclude_ids=exclude_ids, rng=rng,\n        category_small=category_small,\n    )\n",
    )

    replace_once(
        "app.py",
        "        questions = select_category_questions(category_small, question_count)\n        session_id = secrets.token_urlsafe(24)\n",
        "        attempts = get_question_attempts(user_id)\n        selection_audit = {}\n        questions = build_node_adaptive_session(\n            attempts,\n            question_count=question_count,\n            category_small=category_small,\n            audit_out=selection_audit,\n        )\n        session_id = secrets.token_urlsafe(24)\n",
    )
    replace_once(
        "app.py",
        "            \"questions\": questions,\n            \"current_index\": 0,\n",
        "            \"questions\": questions,\n            \"selection_audit\": selection_audit,\n            \"current_index\": 0,\n",
    )
    replace_once(
        "app.py",
        "        \"learning_source\": \"dashboard_recommendation\",\n    }\n    answer_number = session[\"current_index\"] + 1\n",
        "        \"learning_source\": \"dashboard_recommendation\",\n    }\n    result.update(session.get(\"selection_audit\", {}).get(question_id, {}))\n    answer_number = session[\"current_index\"] + 1\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
