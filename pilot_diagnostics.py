"""Read-only Natural Pilot diagnostics built from formal attempt history."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from adaptive_question_selector import select_node_adaptive_questions
from database import get_question_attempts
from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_state_transition import STATES, derive_all_user_node_states, derive_state_timeline
from knowledge_node_weakness_evidence import derive_repeated_weakness_evidence
from question_bank import get_question_tag, question_ids


def _canonical_total():
    return len({canonicalize_knowledge_node_id(get_question_tag(q)["knowledge_node_id"]) for q in question_ids()})


def build_pilot_diagnostics(user_id: str, period: str = "7", now=None):
    now = now or datetime.now(timezone.utc)
    days = {"7": 7, "30": 30, "all": None}.get(period, 7)
    if days:
        jst = ZoneInfo("Asia/Tokyo")
        start_date = now.astimezone(jst).date() - timedelta(days=days - 1)
        start_at = datetime.combine(start_date, datetime.min.time(), jst).astimezone(timezone.utc)
    else:
        start_at = None
    all_attempts = get_question_attempts(user_id)
    attempts = get_question_attempts(user_id, start_at=start_at) if start_at else all_attempts
    total_nodes = _canonical_total()
    touched = {canonicalize_knowledge_node_id(str(a.get("knowledge_node_id") or "")) for a in all_attempts if a.get("knowledge_node_id")}
    states = derive_all_user_node_states(all_attempts, as_of=now)
    state_counts = Counter(item["state"] for item in states)
    state_counts["unseen"] = max(0, total_nodes - len(touched))
    correct = sum(a.get("is_correct") is True for a in attempts)
    unknown = sum(a.get("answer_status") == "unknown" or (not a.get("selected_answers") and a.get("confidence") is None) for a in attempts)
    confidence = Counter(a.get("confidence") for a in attempts if a.get("confidence") in {1, 2, 3})
    transitions = Counter()
    grouped = defaultdict(list)
    for attempt in all_attempts:
        grouped[(str(attempt.get("user_id")), canonicalize_knowledge_node_id(str(attempt.get("knowledge_node_id") or "")))].append(attempt)
    for history in grouped.values():
        timeline = derive_state_timeline(history)
        for before, after in zip(timeline, timeline[1:]):
            transitions[(before["state"], after["state"])] += 1
    adaptive = select_node_adaptive_questions(all_attempts, 30)
    adaptive_groups = Counter(item["priority_group"] for item in adaptive)
    weakness = [item for item in derive_repeated_weakness_evidence(all_attempts)
                if item["evidence_level"] in {"CROSS_QUESTION_WRONG", "CROSS_QUESTION_CONFIDENT_WRONG"}]
    weakness.sort(key=lambda item: (item["wrong_question_count"], item["confident_wrong_count"]), reverse=True)
    return {
        "period": period, "start_at": start_at, "total_attempts": len(attempts),
        "unique_questions": len({a.get("question_id") for a in attempts}), "correct": correct,
        "incorrect": len(attempts) - correct, "accuracy": round(correct * 100 / len(attempts), 1) if attempts else 0,
        "confidence": {str(i): confidence[i] for i in (1, 2, 3)}, "unknown": unknown,
        "confident_wrong": sum(a.get("is_correct") is False and a.get("confidence") == 1 and a.get("answer_status") != "unknown" for a in attempts),
        "canonical_node_total": total_nodes, "touched_nodes": len(touched),
        "coverage": round(len(touched) * 100 / total_nodes, 1) if total_nodes else 0,
        "state_counts": {state: state_counts[state] for state in STATES},
        "repair_to_repaired": transitions[("repairing", "repaired")],
        "repaired_to_repairing": transitions[("repaired", "repairing")],
        "due_to_stable": transitions[("recheck_due", "stable")],
        "due_to_repairing": transitions[("recheck_due", "repairing")],
        "adaptive_count": len(adaptive), "adaptive_unique_questions": len({x["question_id"] for x in adaptive}),
        "adaptive_unique_nodes": len({x["canonical_node_id"] for x in adaptive}),
        "adaptive_groups": dict(adaptive_groups), "weakness": weakness[:10],
    }
