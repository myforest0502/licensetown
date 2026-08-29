"""Pure helpers for the optional written understanding check."""

from __future__ import annotations

import json

from knowledge_node_canonical import canonicalize_knowledge_node_id


EVALUATIONS = {"PASS", "PARTIAL", "FAIL"}


def should_offer_written_check(attempts: list[dict]) -> bool:
    """Return true only when a Node has both saved correct and wrong evidence."""
    return any(item.get("is_correct") is True for item in attempts) and any(
        item.get("is_correct") is False for item in attempts
    )


def select_written_check_candidate(
    session_results: list[dict],
    history: list[dict],
    *,
    used_canonical_node_ids=(),
) -> dict | None:
    """Select one current-session Node with past/current correct and wrong evidence."""
    used = {str(value) for value in used_canonical_node_ids}
    grouped: dict[str, list[dict]] = {}
    for item in history:
        node_id = item.get("knowledge_node_id")
        if not node_id:
            continue
        canonical = canonicalize_knowledge_node_id(str(node_id))
        grouped.setdefault(canonical, []).append(item)

    # Prefer the most recently encountered correct question in this session.
    for item in reversed(session_results):
        node_id = item.get("knowledge_node_id")
        if not node_id or item.get("is_correct") is not True:
            continue
        canonical = canonicalize_knowledge_node_id(str(node_id))
        if canonical in used or not should_offer_written_check(grouped.get(canonical, [])):
            continue
        return {
            "canonical_node_id": canonical,
            "source_question_id": str(item["question_id"]),
        }
    return None


def build_written_prompt(knowledge_node: str) -> str:
    """Build a short deterministic prompt without calling an LLM."""
    label = str(knowledge_node).strip()
    return f"「{label}」について、中心となる考え方を1〜2文で自分の言葉で説明してみてくれ。"


def parse_structured_evaluation(content: str) -> dict:
    """Validate the small JSON contract returned by the evaluator."""
    payload = json.loads(content)
    result = str(payload.get("result", "")).upper()
    if result not in EVALUATIONS:
        raise ValueError("invalid written-check evaluation")
    return {
        "result": result,
        "reason": str(payload.get("reason", "")).strip()[:500],
        "feedback": str(payload.get("feedback", "")).strip()[:1000],
    }


def unknown_evaluation() -> dict:
    return {
        "result": "UNKNOWN",
        "reason": "ユーザーが0（分からない）を選択",
        "feedback": "よし、分からないって分かったのも大事な情報だ。\nここはもう一回直していこう。",
    }


def evaluation_fallback() -> dict:
    """Allowed structured fallback; persistence still happens after AI failure."""
    return {
        "result": "PARTIAL",
        "reason": "AI判定を完了できなかったため保留",
        "feedback": "今ちょっとうまく判定できなかった。\nでも回答はちゃんと預かったぞ。ここは判定を保留にしておくな。",
    }
