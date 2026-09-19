"""Pure, exact-timestamp learning milestone reconstruction."""

from collections import defaultdict
from datetime import datetime, timezone

from dashboard_settings import TOKYO
from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_state_transition import derive_state_timeline


ANSWER_MILESTONES = (100, 500, 1000)


def _timestamp(value):
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def build_learning_milestones(attempts, limit=5):
    """Build only milestones whose occurrence time is exactly reconstructable."""
    ordered = []
    user_ids = set()
    for attempt in attempts or ():
        timestamp = _timestamp(attempt.get("answered_at"))
        if timestamp is None:
            continue
        if attempt.get("user_id") is not None:
            user_ids.add(str(attempt["user_id"]))
        ordered.append((timestamp, attempt))
    if len(user_ids) > 1:
        raise ValueError("attempts must belong to one user")
    ordered.sort(key=lambda item: (
        item[0], str(item[1].get("event_key", "")), int(item[1].get("attempt_position", 0) or 0)
    ))
    if not ordered:
        return []

    events = [{
        "event_type": "learning_started",
        "occurred_at": ordered[0][0],
        "title": "学習を始めました",
        "description": "最初の回答が保存された日です。",
        "metadata": {},
    }]
    for count in ANSWER_MILESTONES:
        if len(ordered) >= count:
            events.append({
                "event_type": f"answers_{count}",
                "occurred_at": ordered[count - 1][0],
                "title": f"回答数が{count}問に到達しました",
                "description": "保存済みの回答履歴から確認できた節目です。",
                "metadata": {"answer_count": count},
            })
    grouped = defaultdict(list)
    for _timestamp_value, attempt in ordered:
        node_id = str(attempt.get("knowledge_node_id") or "")
        if node_id:
            grouped[canonicalize_knowledge_node_id(node_id)].append(attempt)
    first_transitions = {}
    for canonical_node_id, history in grouped.items():
        for attempt, state_result in zip(history, derive_state_timeline(history)):
            state = state_result["state"]
            if state in {"repaired", "stable"}:
                candidate = (_timestamp(attempt.get("answered_at")), canonical_node_id)
                current = first_transitions.get(state)
                if candidate[0] and (current is None or candidate[0] < current[0]):
                    first_transitions[state] = candidate
    transition_labels = {
        "repaired": ("first_repaired", "初めて弱点の修復を確認しました"),
        "stable": ("first_stable", "初めて学習内容の定着を確認しました"),
    }
    for state, (event_type, title) in transition_labels.items():
        transition = first_transitions.get(state)
        if transition and transition[0]:
            events.append({
                "event_type": event_type,
                "occurred_at": transition[0],
                "title": title,
                "description": "正式なKnowledge Node状態履歴から確認できた節目です。",
                "metadata": {"canonical_node_id": transition[1]},
            })
    events.sort(key=lambda event: (event["occurred_at"], event["event_type"]))
    for event in events:
        event["display_date"] = event["occurred_at"].astimezone(TOKYO).strftime("%Y年%m月%d日")
    return events[-max(int(limit), 0):] if limit else []
