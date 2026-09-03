"""Read-only source-mix diagnostics for learner question routes.

This module is deliberately diagnostic-only.  It never changes selector priority:
Safety, repair evidence, cooldown and formal route policy remain authoritative.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Iterable, Mapping

from question_bank import get_question_tag


KNOWN_SOURCES = ("past_exam", "original")


def _source_for_question(question_id: str, tag_getter: Callable[[str], Mapping[str, Any]]) -> str:
    source = str(tag_getter(question_id).get("source") or "").strip()
    return source if source in KNOWN_SOURCES else "unknown"


def _bucket() -> dict[str, Any]:
    return {
        "question_count": 0,
        "correct_count": 0,
        "answered_count": 0,
        "confidence_sum": 0,
        "confidence_count": 0,
        "question_ids": [],
    }


def _finish(bucket: Mapping[str, Any]) -> dict[str, Any]:
    answered = int(bucket["answered_count"])
    confidence_count = int(bucket["confidence_count"])
    return {
        "question_count": int(bucket["question_count"]),
        "correct_count": int(bucket["correct_count"]),
        "answered_count": answered,
        "accuracy": (int(bucket["correct_count"]) / answered) if answered else None,
        "mean_confidence": (
            float(bucket["confidence_sum"]) / confidence_count if confidence_count else None
        ),
        "question_ids": list(bucket["question_ids"]),
    }


def build_source_mix_audit(
    question_results: Iterable[Mapping[str, Any]],
    *,
    tag_getter: Callable[[str], Mapping[str, Any]] = get_question_tag,
) -> dict[str, Any]:
    """Summarize source mix by route and selection group without mutating input.

    ``question_results`` should be persisted learner-result rows (for example the
    flattened ``learning_events.question_results`` objects). Unknown/zero answers
    stay in exposure counts but do not affect accuracy.
    """
    source_buckets = defaultdict(_bucket)
    route_buckets: dict[str, dict[str, dict[str, Any]]] = defaultdict(lambda: defaultdict(_bucket))
    group_buckets: dict[str, dict[str, dict[str, Any]]] = defaultdict(lambda: defaultdict(_bucket))
    total = 0

    for raw in question_results:
        item = dict(raw)
        question_id = str(item.get("question_id") or "").strip().upper()
        if not question_id:
            continue
        source = _source_for_question(question_id, tag_getter)
        route = str(item.get("learning_source") or "unknown").strip() or "unknown"
        group = str(item.get("selection_group") or "unclassified").strip() or "unclassified"
        status = str(item.get("answer_status") or "answered").strip().lower()
        answered = status != "unknown"
        confidence = item.get("confidence")

        for bucket in (source_buckets[source], route_buckets[route][source], group_buckets[group][source]):
            bucket["question_count"] += 1
            bucket["question_ids"].append(question_id)
            if answered:
                bucket["answered_count"] += 1
                if item.get("is_correct") is True:
                    bucket["correct_count"] += 1
                if confidence in (1, 2, 3):
                    bucket["confidence_sum"] += int(confidence)
                    bucket["confidence_count"] += 1
        total += 1

    def finalize_nested(raw_nested):
        return {
            outer: {source: _finish(bucket) for source, bucket in sorted(inner.items())}
            for outer, inner in sorted(raw_nested.items())
        }

    by_source = {source: _finish(bucket) for source, bucket in sorted(source_buckets.items())}
    past = by_source.get("past_exam", {}).get("question_count", 0)
    return {
        "question_count": total,
        "past_exam_count": int(past),
        "past_exam_share": (int(past) / total) if total else None,
        "by_source": by_source,
        "by_learning_source": finalize_nested(route_buckets),
        "by_selection_group": finalize_nested(group_buckets),
        "policy_note": (
            "Source is diagnostic evidence only; it must not override Safety, repair, "
            "retention/cooldown, or formal selector priority."
        ),
    }
