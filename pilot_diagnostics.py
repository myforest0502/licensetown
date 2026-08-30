"""Read-only Natural Pilot diagnostics built from formal attempt history."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from adaptive_question_selector import select_node_adaptive_questions
from database import get_question_attempts
from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_state_transition import STATES, derive_all_user_node_states, derive_state_timeline
from knowledge_node_weakness_evidence import derive_repeated_weakness_evidence
from question_bank import get_question_tag, question_ids


_STATE_LABELS = {
    "unseen": "未着手", "checking": "確認中", "repairing": "修復中",
    "repaired": "修復済み", "recheck_due": "再確認待ち", "stable": "定着",
}
_GROUP_LABELS = {
    "repair": "修復", "checking": "確認", "exploration": "新規学習",
    "maintenance": "維持確認", "recheck": "再確認",
}
_REASON_LABELS = {
    "safety_wrong": "Safety誤答",
    "confident_wrong": "自信あり誤答",
    "cross_question_wrong": "異なる問題での反復誤答",
    "repairing": "修復中",
    "previous_wrong_unconfirmed": "過去誤答・未修復",
    "recheck_due": "再確認時期",
    "uncertain_correct": "自信の低い正解",
    "checking": "確認中",
    "unseen": "未着手Node探索",
    "repaired": "修復済みNodeの維持",
    "stable_maintenance": "定着Nodeの維持",
}


def _knowledge_node_labels():
    path = Path(__file__).resolve().parent / "data" / "question_bank" / "knowledge_nodes.json"
    records = json.loads(path.read_text(encoding="utf-8-sig"))
    return {str(item["knowledge_node_id"]): str(item["label"]) for item in records}


_NODE_LABELS = _knowledge_node_labels()


def build_adaptive_selection_audit(adaptive):
    """Decorate selector output without changing its order or selection."""
    details = []
    for rank, source in enumerate(adaptive, 1):
        item = dict(source)
        node_id = str(item["canonical_node_id"])
        reason_parts = [_REASON_LABELS.get(item.get("priority_reason"), str(item.get("priority_reason") or "-"))]
        if item.get("strong_repair_confirmation"):
            reason_parts.append("strong別問題の修復確認候補")
        if item.get("same_question_repeat"):
            reason_parts.append("同一問題の再出題（減点済み）")
        details.append({
            **item,
            "rank": rank,
            "node_label": _NODE_LABELS.get(node_id, "名称未登録"),
            "state_label": _STATE_LABELS.get(item.get("state"), str(item.get("state") or "-")),
            "group_label": _GROUP_LABELS.get(item.get("priority_group"), str(item.get("priority_group") or "-")),
            "reason_label": "、".join(reason_parts),
        })
    audit_text = "\n\n".join(
        f'{item["rank"]}. {item["question_id"]} / {item["canonical_node_id"]} / {item["node_label"]} / {item["state_label"]}\n'
        f'   分類：{item["group_label"]}\n   理由：{item["reason_label"]}\n   priority：{item["priority_score"]}'
        for item in details
    )
    return details, audit_text


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
    adaptive_details, adaptive_audit_text = build_adaptive_selection_audit(adaptive)
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
        "adaptive_groups": dict(adaptive_groups), "adaptive_details": adaptive_details,
        "adaptive_audit_text": adaptive_audit_text, "weakness": weakness[:10],
    }
