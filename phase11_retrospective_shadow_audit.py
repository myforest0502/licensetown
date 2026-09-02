"""Read-only current-policy historical replay for Phase11 promotion QA."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from field_evidence import build_field_evidence
from judgment_shadow import (
    build_field_judgment_evidence_profiles,
    build_shadow_comparison,
    build_shadow_judgment,
)
from question_bank import CATEGORY_NAMES


POLICY_LABEL = "phase11_v0.1_current_policy"
TOKYO = ZoneInfo("Asia/Tokyo")


def _parse_time(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed


def _result_payload(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return value
    return None


def _valid_anchor(event: dict[str, Any]) -> dict[str, Any] | None:
    if str(event.get("mode") or "") != "recommendation_plan":
        return None
    payload = _result_payload(event.get("question_results"))
    if not isinstance(payload, dict) or payload.get("activity_type") != "recommendation_plan":
        return None
    field = str(payload.get("field") or "").strip()
    goal = _as_int(payload.get("goal"))
    answered_at = _parse_time(event.get("answered_at"))
    if field not in set(CATEGORY_NAMES.values()) or goal is None or goal <= 0 or answered_at is None:
        return None
    return {
        "event_key": str(event.get("event_key") or ""),
        "answered_at": answered_at,
        "field": field,
        "goal": goal,
    }


def _attempt_key(attempt: dict[str, Any]) -> tuple[str, int] | None:
    event_key = str(attempt.get("event_key") or "")
    position = _as_int(attempt.get("attempt_position"))
    if not event_key or position is None or position < 1:
        return None
    return event_key, position


def _formal_results(event: dict[str, Any]) -> list[tuple[int, dict[str, Any]]] | None:
    payload = _result_payload(event.get("question_results"))
    if not isinstance(payload, list):
        return None
    formal = []
    for position, item in enumerate(payload, start=1):
        if not isinstance(item, dict) or not item.get("question_id"):
            continue
        formal.append((position, item))
    return formal


def audit_historical_attempt_coverage(
    learning_events: Iterable[dict[str, Any]],
    attempts: Iterable[dict[str, Any]],
    *,
    before: datetime,
) -> dict[str, Any]:
    """Verify cumulative persisted formal-answer coverage strictly before T."""
    cutoff = _parse_time(before)
    if cutoff is None:
        raise ValueError("before must be a parseable timestamp")
    events = []
    for raw in learning_events:
        event = dict(raw)
        timestamp = _parse_time(event.get("answered_at"))
        if timestamp is not None and timestamp < cutoff:
            events.append((timestamp, event))
    attempts_before = []
    for raw in attempts:
        item = dict(raw)
        timestamp = _parse_time(item.get("answered_at"))
        if timestamp is not None and timestamp < cutoff:
            attempts_before.append(item)
    attempts_by_key = {
        key: item for item in attempts_before if (key := _attempt_key(item)) is not None
    }

    expected = 0
    matched = 0
    issues: list[str] = []
    unreliable = False
    for _timestamp, event in sorted(events, key=lambda pair: (pair[0], str(pair[1].get("event_key") or ""))):
        answered_count = _as_int(event.get("answered_count"))
        if answered_count is None or answered_count < 0:
            unreliable = True
            issues.append(f"invalid_answered_count:{event.get('event_key')}")
            continue
        if answered_count == 0:
            continue
        formal = _formal_results(event)
        if formal is None:
            issues.append(f"missing_formal_results:{event.get('event_key')}")
            continue
        if len(formal) != answered_count:
            issues.append(f"formal_result_count_mismatch:{event.get('event_key')}")
            continue
        expected += answered_count
        event_unreliable = False
        event_matched = 0
        for position, result in formal:
            attempt = attempts_by_key.get((str(event.get("event_key") or ""), position))
            if attempt is None:
                issues.append(f"missing_attempt:{event.get('event_key')}:{position}")
                continue
            if str(attempt.get("question_id") or "") != str(result.get("question_id") or ""):
                unreliable = True
                event_unreliable = True
                issues.append(f"question_mismatch:{event.get('event_key')}:{position}")
                continue
            if "is_correct" in result and attempt.get("is_correct") is not result.get("is_correct"):
                unreliable = True
                event_unreliable = True
                issues.append(f"correctness_mismatch:{event.get('event_key')}:{position}")
                continue
            if "confidence" in result and attempt.get("confidence") != result.get("confidence"):
                unreliable = True
                event_unreliable = True
                issues.append(f"confidence_mismatch:{event.get('event_key')}:{position}")
                continue
            event_matched += 1
        if not event_unreliable:
            matched += event_matched

    if unreliable:
        status = "history_coverage_unreliable"
    elif issues:
        status = "history_coverage_incomplete"
    else:
        status = "history_coverage_complete"
    return {
        "status": status,
        "expected_formal_attempts": expected,
        "matched_formal_attempts": matched,
        "historical_formal_attempt_count": len(attempts_before),
        "issues": issues,
    }


def _historical_total_answers(learning_events: Iterable[dict[str, Any]], before: datetime) -> int | None:
    total = 0
    for event in learning_events:
        timestamp = _parse_time(event.get("answered_at"))
        if timestamp is None or timestamp >= before:
            continue
        answered_count = _as_int(event.get("answered_count"))
        if answered_count is None or answered_count < 0:
            return None
        total += answered_count
    return total


def _comparison_category(label: str) -> str:
    return {
        "same_target_same_reason": "agreement",
        "same_target_stronger_reason": "agreement",
        "different_target_shadow_has_stronger_evidence": "shadow_stronger_disagreement",
        "different_target_current_has_stronger_evidence": "current_stronger_disagreement",
    }.get(label, "inconclusive_disagreement")


def build_retrospective_shadow_audit(
    attempts: Iterable[dict[str, Any]],
    learning_events: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Replay current Phase11 policy at trustworthy persisted plan anchors."""
    attempts = [dict(item) for item in attempts]
    learning_events = [dict(item) for item in learning_events]
    anchors = [anchor for event in learning_events if (anchor := _valid_anchor(event))]
    anchors.sort(key=lambda item: (item["answered_at"], item["event_key"]))
    snapshots = []
    counts = Counter()

    for anchor in anchors:
        timestamp = anchor["answered_at"]
        coverage = audit_historical_attempt_coverage(
            learning_events,
            attempts,
            before=timestamp,
        )
        total_answers = _historical_total_answers(learning_events, timestamp)
        baseline_phase = None if total_answers is None else ("foundation" if total_answers < 100 else "analysis")
        base = {
            "snapshot_at": timestamp.isoformat(),
            "snapshot_jst": timestamp.astimezone(TOKYO).isoformat(),
            "policy_label": POLICY_LABEL,
            "anchor_event_key": anchor["event_key"],
            "coverage_status": coverage["status"],
            "coverage_issues": coverage["issues"],
            "historical_total_answers": total_answers,
            "historical_formal_attempt_count": coverage["historical_formal_attempt_count"],
            "baseline_target": anchor["field"],
            "baseline_goal": anchor["goal"],
            "baseline_phase": baseline_phase,
        }
        if coverage["status"] != "history_coverage_complete" or baseline_phase is None:
            counts["excluded"] += 1
            snapshots.append({**base, "eligible": False, "review_category": "excluded_snapshot"})
            continue

        historical_attempts = [
            item for item in attempts
            if (_parse_time(item.get("answered_at")) or timestamp) < timestamp
        ]
        field_evidence = build_field_evidence(historical_attempts, as_of=timestamp)
        current_guidance = {
            "phase": baseline_phase,
            "recommended_study": [(anchor["field"], anchor["goal"])],
        }
        shadow = build_shadow_judgment(
            historical_attempts,
            field_evidence,
            current_guidance,
            as_of=timestamp,
        )
        profiles = build_field_judgment_evidence_profiles(
            historical_attempts,
            field_evidence,
            as_of=timestamp,
        )
        comparison = build_shadow_comparison(current_guidance, shadow, profiles)
        category = _comparison_category(str(comparison.get("label") or ""))
        counts[category] += 1
        critical_safety_miss = bool(
            shadow.get("reason_code") == "safety_repair"
            and anchor["field"] != shadow.get("target_field")
        )
        ordinary_single_wrong_takeover = bool(
            shadow.get("reason_code") in {"confident_wrong_cluster", "repeated_wrong_cluster"}
            and comparison.get("shadow_target_formal_evidence", {}).get("active_repeated_weakness_node_count", 0) == 0
            and comparison.get("shadow_target_formal_evidence", {}).get("active_cross_question_wrong_node_count", 0) == 0
        )
        if critical_safety_miss:
            counts["critical_safety_miss_candidates"] += 1
        if ordinary_single_wrong_takeover:
            counts["ordinary_single_wrong_takeover_candidates"] += 1
        snapshots.append({
            **base,
            "eligible": True,
            "review_category": category,
            "shadow_intent": shadow.get("learning_intent"),
            "shadow_target": shadow.get("target_field"),
            "shadow_count": shadow.get("question_count"),
            "shadow_reason_code": shadow.get("reason_code"),
            "shadow_confidence": shadow.get("confidence"),
            "comparison_label": comparison.get("label"),
            "shadow_reason_profile_consistent": comparison.get("shadow_reason_profile_consistent"),
            "baseline_target_formal_evidence": comparison.get("current_target_formal_evidence"),
            "shadow_target_formal_evidence": comparison.get("shadow_target_formal_evidence"),
            "critical_safety_miss_candidate": critical_safety_miss,
            "ordinary_single_wrong_takeover_candidate": ordinary_single_wrong_takeover,
        })

    return {
        "policy_label": POLICY_LABEL,
        "plan_anchor_count": len(anchors),
        "eligible_snapshot_count": sum(item.get("eligible") is True for item in snapshots),
        "coverage_excluded_count": counts["excluded"],
        "agreement_count": counts["agreement"],
        "shadow_stronger_disagreement_count": counts["shadow_stronger_disagreement"],
        "current_stronger_disagreement_count": counts["current_stronger_disagreement"],
        "inconclusive_disagreement_count": counts["inconclusive_disagreement"],
        "critical_safety_miss_candidate_count": counts["critical_safety_miss_candidates"],
        "ordinary_single_wrong_takeover_candidate_count": counts["ordinary_single_wrong_takeover_candidates"],
        "snapshots": list(reversed(snapshots)),
    }
