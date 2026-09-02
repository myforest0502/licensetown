"""Read-only Natural Pilot diagnostics built from formal attempt history."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from adaptive_question_selector import select_node_adaptive_questions
from database import (
    get_dashboard_learning_data,
    get_learning_events,
    get_learning_events_by_event_keys,
    get_latest_adaptive_daily_learning_session_events,
    get_question_attempts,
)
from field_evidence import build_field_evidence
from judgment_shadow import (
    build_field_judgment_evidence_profiles,
    build_shadow_comparison,
    build_shadow_judgment,
)
from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_state_transition import STATES, derive_all_user_node_states, derive_state_timeline
from knowledge_node_weakness_evidence import derive_repeated_weakness_evidence
from learning_analysis import build_learning_guidance
from question_bank import CATEGORY_NAMES, get_category_small, get_question_tag, question_ids
from phase11_active_weakness import build_active_repair_weakness
from phase11_retrospective_shadow_audit import build_retrospective_shadow_audit
from repairability_diagnostics import (
    build_repairing_node_repairability,
    build_strong_repair_supply_priorities,
)


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
_SAVED_ADAPTIVE_AUDIT_FIELDS = (
    "selection_reason",
    "selection_group",
    "selection_score",
    "repair_evidence_quality",
    "recent_question_repeat",
    "recent_cooldown_bypassed",
)
_REPEAT_CATEGORIES = (
    "justified_cooldown_bypass",
    "adaptive_spaced_repeat",
    "adaptive_unexplained_repeat",
    "adaptive_metadata_inconsistent",
    "nonadaptive_repeat",
    "audit_metadata_unavailable",
)


def _knowledge_node_labels():
    path = Path(__file__).resolve().parent / "data" / "question_bank" / "knowledge_nodes.json"
    records = json.loads(path.read_text(encoding="utf-8-sig"))
    return {str(item["knowledge_node_id"]): str(item["label"]) for item in records}


_NODE_LABELS = _knowledge_node_labels()


def _node_field_memberships():
    memberships = defaultdict(set)
    for question_id in question_ids():
        node_id = canonicalize_knowledge_node_id(
            get_question_tag(question_id)["knowledge_node_id"]
        )
        memberships[node_id].add(get_category_small(question_id))
    return dict(memberships)


_NODE_FIELDS = _node_field_memberships()


def _wrong_time(value):
    if isinstance(value, datetime):
        parsed = value
    elif value:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def build_confident_wrong_node_details(
    attempts, field_evidence, shadow_judgment, *, as_of=None
):
    """Expose only the active current-cycle evidence that contributes to J2."""
    if shadow_judgment.get("reason_code") != "confident_wrong_cluster":
        return []
    target_field = shadow_judgment.get("target_field")
    target_field_id = next(
        (field_id for field_id, name in CATEGORY_NAMES.items() if name == target_field),
        None,
    )
    if target_field_id is None:
        return []

    states = {
        str(item.get("canonical_node_id")): str(item.get("state") or "unseen")
        for item in field_evidence.get("canonical_node_evidence", [])
        if item.get("canonical_node_id")
    }
    active_by_node = build_active_repair_weakness(attempts, as_of=as_of)

    def field_for_question(question_id):
        try:
            return get_category_small(str(question_id))
        except (KeyError, TypeError, ValueError):
            return None

    def question_sort_key(value):
        return (
            (0, int(value[1:]))
            if value.startswith("Q") and value[1:].isdigit()
            else (1, value)
        )

    details = []
    for node_id, source in active_by_node.items():
        if states.get(node_id) != "repairing":
            continue
        wrong_qs = [
            str(q)
            for q in source.get("active_evaluable_wrong_question_ids", [])
            if q
        ]
        confident_qs = [
            str(q)
            for q in source.get("active_confident_wrong_question_ids", [])
            if q
        ]
        target_wrong_qs = [q for q in wrong_qs if field_for_question(q) == target_field_id]
        target_confident_qs = [
            q for q in confident_qs if field_for_question(q) == target_field_id
        ]
        cross_confident = (
            source.get("active_weakness_evidence_level")
            == "CROSS_QUESTION_CONFIDENT_WRONG"
        )
        contributes_to_target_j2 = bool(target_confident_qs) or bool(
            target_wrong_qs and cross_confident
        )
        if not contributes_to_target_j2:
            continue

        last_wrong = _wrong_time(source.get("active_last_evaluable_wrong_at"))
        question_ids_for_node = sorted(set(wrong_qs), key=question_sort_key)
        details.append({
            "canonical_node_id": node_id,
            "knowledge_text": _NODE_LABELS.get(node_id, "名称未登録"),
            "question_ids": question_ids_for_node,
            "confident_wrong_count": int(source.get("active_confident_wrong_count") or 0),
            "distinct_question_count": int(
                source.get("active_evaluable_wrong_question_count") or 0
            ),
            "cross_question": cross_confident,
            "node_state": states[node_id],
            "node_state_label": _STATE_LABELS.get(states[node_id], states[node_id]),
            "last_wrong_at": (
                last_wrong.astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M")
                if last_wrong else None
            ),
        })
    details.sort(key=lambda item: (
        -item["confident_wrong_count"],
        -item["distinct_question_count"],
        item["canonical_node_id"],
    ))
    return details


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


def _current_dashboard_guidance(user_id: str):
    """Read the same deterministic guidance inputs used by the current dashboard."""
    learning_data = get_dashboard_learning_data(user_id)
    return build_learning_guidance(
        int(learning_data["summary"].get("total_answers") or 0),
        learning_data["fields"],
    )


def _parse_adaptive_session_event_key(event_key):
    """Return (session_id, set_no) for the persisted ``{session_id}:{set_no}`` form."""
    head, separator, tail = str(event_key or "").rpartition(":")
    if not separator or not head or not tail.isdigit():
        return None
    set_no = int(tail)
    if set_no < 1:
        return None
    return head, set_no


def _adaptive_session_completion_status(events, question_count, unique_question_count):
    parsed = [_parse_adaptive_session_event_key(event.get("event_key")) for event in events]
    parsed_set_numbers = [item[1] for item in parsed if item is not None]
    parsed_session_ids = [item[0] for item in parsed if item is not None]
    if len(events) != 6:
        status = "event_count_incomplete"
    elif any(item is None for item in parsed):
        status = "event_key_unparseable"
    elif len(set(parsed_session_ids)) != 1:
        status = "mixed_session_ids"
    elif len(set(parsed_set_numbers)) != len(parsed_set_numbers) or set(parsed_set_numbers) != set(range(1, 7)):
        status = "set_sequence_invalid"
    elif question_count != 30:
        status = "question_count_incomplete"
    elif unique_question_count != 30:
        status = "duplicate_question_ids"
    else:
        status = "complete"
    return {
        "session_status": status,
        "parsed_session_ids": parsed_session_ids,
        "parsed_set_numbers": parsed_set_numbers,
        "event_key_parse_failure_count": sum(item is None for item in parsed),
    }


def build_saved_adaptive_daily_audit(events):
    """Summarize only the audit values already persisted in learning_events."""
    if not events:
        return {
            "exists": False,
            "results": [],
            "audit_fields_complete": False,
            "recent_repeat_count": 0,
            "cooldown_bypass_count": 0,
        }
    if isinstance(events, dict):
        events = [events]
    details = []
    for event in events:
        results = event.get("question_results")
        if isinstance(results, str):
            try:
                results = json.loads(results)
            except (TypeError, ValueError):
                results = []
        if not isinstance(results, list):
            results = []
        for result in results:
            if not isinstance(result, dict):
                continue
            missing = [name for name in _SAVED_ADAPTIVE_AUDIT_FIELDS if name not in result]
            item = {
                "question_id": str(result.get("question_id") or "不明"),
                "missing_audit_fields": missing,
            }
            item.update({name: result.get(name) for name in _SAVED_ADAPTIVE_AUDIT_FIELDS})
            details.append(item)
    event_times = [_wrong_time(event.get("answered_at")) for event in events]
    event_times = [value for value in event_times if value is not None]
    unique_question_count = len({item["question_id"] for item in details})
    expected_question_count = 30
    completion = _adaptive_session_completion_status(
        events, len(details), unique_question_count
    )
    session_complete = completion["session_status"] == "complete"
    return {
        "exists": True,
        "first_event_at": min(event_times).astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S") if event_times else None,
        "last_event_at": max(event_times).astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S") if event_times else None,
        "source": "adaptive_daily",
        "mode": str(events[-1].get("mode") or "不明"),
        "event_count": len(events),
        "expected_question_count": expected_question_count,
        "session_complete": session_complete,
        "session_status": completion["session_status"],
        "parsed_session_ids": completion["parsed_session_ids"],
        "parsed_set_numbers": completion["parsed_set_numbers"],
        "event_key_parse_failure_count": completion["event_key_parse_failure_count"],
        "question_count": len(details),
        "unique_question_count": unique_question_count,
        "audit_fields_complete": bool(details) and all(
            not item["missing_audit_fields"] for item in details
        ),
        "recent_repeat_count": sum(item["recent_question_repeat"] is True for item in details),
        "cooldown_bypass_count": sum(item["recent_cooldown_bypassed"] is True for item in details),
        "recent_repeat_question_ids": [
            item["question_id"] for item in details if item["recent_question_repeat"] is True
        ],
        "cooldown_bypass_question_ids": [
            item["question_id"] for item in details if item["recent_cooldown_bypassed"] is True
        ],
        "results": details,
    }


def _event_result_lookup(learning_events):
    lookup = {}
    for event in learning_events or ():
        event_key = str(event.get("event_key") or "")
        results = event.get("question_results")
        if isinstance(results, str):
            try:
                results = json.loads(results)
            except (TypeError, ValueError):
                results = []
        if not isinstance(results, list):
            continue
        for result in results:
            if not isinstance(result, dict) or not result.get("question_id"):
                continue
            lookup[(event_key, str(result["question_id"]))] = dict(result)
    return lookup


def _repeat_time_label(value):
    parsed = _wrong_time(value)
    return (
        parsed.astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M")
        if parsed else "日時不明"
    )


def build_repeat_structure_audit(attempts, learning_events):
    """Classify saved same-Q repeats without reconstructing selection intent."""
    ordered = sorted(
        (dict(item) for item in attempts or ()),
        key=lambda item: (
            _wrong_time(item.get("answered_at") or item.get("attempted_at"))
            or datetime.min.replace(tzinfo=timezone.utc),
            str(item.get("event_key") or ""),
            int(item.get("attempt_position") or 0),
        ),
    )
    result_lookup = _event_result_lookup(learning_events)
    prior_by_question = {}
    prior_questions_by_node = defaultdict(set)
    repeats = []
    same_node_different_question = 0
    unknown_count = 0

    for attempt in ordered:
        user_id = str(attempt.get("user_id") or "")
        question_id = str(attempt.get("question_id") or "")
        raw_node_id = str(attempt.get("knowledge_node_id") or "")
        node_id = canonicalize_knowledge_node_id(raw_node_id) if raw_node_id else ""
        current_at = _wrong_time(attempt.get("answered_at") or attempt.get("attempted_at"))
        question_key = (user_id, question_id)
        node_key = (user_id, node_id)
        if (
            attempt.get("answer_status") == "unknown"
            or (attempt.get("selected_answers") == [] and attempt.get("confidence") is None)
        ):
            unknown_count += 1

        previous = prior_by_question.get(question_key)
        if previous is None:
            if question_id and prior_questions_by_node[node_key] - {question_id}:
                same_node_different_question += 1
        else:
            previous_at = previous[0]
            delta = current_at - previous_at if current_at and previous_at else None
            metadata = result_lookup.get((str(attempt.get("event_key") or ""), question_id))
            audit_available = bool(metadata) and all(
                name in metadata for name in _SAVED_ADAPTIVE_AUDIT_FIELDS
            )
            source = str((metadata or {}).get("learning_source") or "")
            group = str((metadata or {}).get("selection_group") or "")
            recent_repeat = (metadata or {}).get("recent_question_repeat")
            bypassed = (metadata or {}).get("recent_cooldown_bypassed")

            if metadata and source and source != "adaptive_daily":
                category = "nonadaptive_repeat"
            elif not metadata or source != "adaptive_daily" or not audit_available:
                category = "audit_metadata_unavailable"
            elif not isinstance(recent_repeat, bool) or not isinstance(bypassed, bool):
                category = "audit_metadata_unavailable"
            elif recent_repeat is True and bypassed is True:
                category = "justified_cooldown_bypass"
            elif recent_repeat is True and bypassed is False:
                category = "adaptive_unexplained_repeat"
            elif recent_repeat is False and bypassed is True:
                category = "adaptive_metadata_inconsistent"
            else:
                category = "adaptive_spaced_repeat"

            seconds = delta.total_seconds() if delta is not None else None
            if seconds is None:
                distance_bucket = "unknown"
            elif seconds < 24 * 60 * 60:
                distance_bucket = "<24h"
            elif seconds < 7 * 24 * 60 * 60:
                distance_bucket = "1d–<7d"
            else:
                distance_bucket = ">=7d"
            same_day = bool(
                current_at and previous_at
                and current_at.astimezone(ZoneInfo("Asia/Tokyo")).date()
                == previous_at.astimezone(ZoneInfo("Asia/Tokyo")).date()
            )
            repeats.append({
                "question_id": question_id,
                "canonical_node_id": node_id,
                "answered_at": _repeat_time_label(current_at),
                "previous_answered_at": _repeat_time_label(previous_at),
                "elapsed_seconds": seconds,
                "elapsed_label": (
                    f"{seconds / 3600:.1f}時間" if seconds is not None and seconds < 86400
                    else f"{seconds / 86400:.1f}日" if seconds is not None else "不明"
                ),
                "same_day": same_day,
                "distance_bucket": distance_bucket,
                "category": category,
                "learning_source": source or "不明",
                "selection_reason": (metadata or {}).get("selection_reason"),
                "selection_group": (metadata or {}).get("selection_group"),
                "repair_evidence_quality": (metadata or {}).get("repair_evidence_quality"),
                "recent_question_repeat": recent_repeat,
                "recent_cooldown_bypassed": bypassed,
            })

        if question_id:
            prior_by_question[question_key] = (current_at, attempt)
            prior_questions_by_node[node_key].add(question_id)

    category_counts = Counter(item["category"] for item in repeats)
    distance_counts = Counter(item["distance_bucket"] for item in repeats)
    nonadaptive_modes = Counter(
        item["learning_source"] for item in repeats
        if item["category"] == "nonadaptive_repeat"
    )
    unique_questions = len({
        str(item.get("question_id")) for item in ordered if item.get("question_id")
    })
    unexplained = [
        item for item in repeats if item["category"] == "adaptive_unexplained_repeat"
    ]
    return {
        "total_attempts": len(ordered),
        "unique_questions": unique_questions,
        "repeat_occurrences": len(repeats),
        "same_question_repeats": len(repeats),
        "same_node_different_question_confirmations": same_node_different_question,
        "unknown_attempts": unknown_count,
        "category_counts": {name: category_counts[name] for name in _REPEAT_CATEGORIES},
        "distance_counts": {
            "under_24h": distance_counts["<24h"],
            "one_to_under_seven_days": distance_counts["1d–<7d"],
            "seven_days_or_more": distance_counts[">=7d"],
            "unknown": distance_counts["unknown"],
        },
        "same_day_count": sum(item["same_day"] for item in repeats),
        "nonadaptive_modes": dict(sorted(nonadaptive_modes.items())),
        "unexplained_repeat_count": len(unexplained),
        "unexplained_repeats": unexplained,
        "repeat_details": repeats,
    }


def _promotion_profile_text(profile):
    if not profile:
        return "none"
    return ",".join([
        f"field={profile.get('field_name') or 'none'}",
        f"reason={profile.get('strongest_reason_code') or 'none'}",
        f"rank={profile.get('reason_rank') if profile.get('reason_rank') is not None else 'none'}",
        f"critical_safety={int(profile.get('critical_safety_unresolved_count') or 0)}",
        f"cross_confident={int(profile.get('active_cross_question_confident_wrong_node_count') or profile.get('cross_question_confident_wrong_node_count') or 0)}",
        f"confident_nodes={int(profile.get('active_confident_wrong_repairing_node_count') or profile.get('distinct_confident_wrong_repairing_node_count') or 0)}",
        f"cross_wrong={int(profile.get('active_cross_question_wrong_node_count') or profile.get('cross_question_wrong_node_count') or 0)}",
        f"repeated={int(profile.get('active_repeated_weakness_node_count') or profile.get('repeated_weakness_node_count') or 0)}",
        f"recheck_due={int(profile.get('recheck_due_node_count') or 0)}",
        f"answers={int(profile.get('answered_count') or profile.get('raw_answer_count') or 0)}",
        f"accuracy_percent={profile.get('accuracy_percent') if profile.get('accuracy_percent') is not None else 'none'}",
        f"node_coverage_percent={profile.get('node_coverage_percent') if profile.get('node_coverage_percent') is not None else 'none'}",
    ])


def build_phase11_promotion_evidence_text(
    *,
    period,
    shadow_judgment,
    repeat_structure_audit,
    saved_adaptive_daily_audit,
    retrospective_shadow_audit,
    state_counts,
    transitions,
    repairing_node_repairability,
    adaptive_count,
    adaptive_unique_questions,
    adaptive_unique_nodes,
    adaptive_groups,
):
    """Build a deterministic Supporter-only Phase11 review bundle from existing facts."""
    period_label = {"7": "直近7日", "30": "直近30日", "all": "全期間"}.get(
        str(period), str(period)
    )
    shadow = shadow_judgment or {}
    comparison = shadow.get("comparison") or {}
    repeat = repeat_structure_audit or {}
    repeat_counts = repeat.get("category_counts") or {}
    saved = saved_adaptive_daily_audit or {}
    replay = retrospective_shadow_audit or {}
    repairability = repairing_node_repairability or {}
    groups = adaptive_groups or {}
    states = state_counts or {}
    transition_counts = transitions or {}

    recent_ids = ",".join(saved.get("recent_repeat_question_ids") or []) or "none"
    bypass_ids = ",".join(saved.get("cooldown_bypass_question_ids") or []) or "none"

    shadow_evidence = " | ".join(str(item) for item in (shadow.get("evidence") or [])) or "none"
    shadow_observations = " | ".join(str(item) for item in (shadow.get("observations") or [])) or "none"

    lines = [
        "PHASE11_PROMOTION_EVIDENCE_V1",
        f"selected_period={period_label}",
        "scope_note=period_metrics:selected_period;formal_current:all_history;replay:all_history",
        f"baseline_target={comparison.get('current_target') or 'none'}",
        f"shadow_target={shadow.get('target_field') or 'none'}",
        f"shadow_intent={shadow.get('learning_intent') or 'none'}",
        f"shadow_reason={shadow.get('reason_code') or 'none'}",
        f"shadow_confidence={shadow.get('confidence') or 'none'}",
        f"shadow_evidence={shadow_evidence}",
        f"shadow_observations={shadow_observations}",
        f"comparison_label={comparison.get('label') or 'none'}",
        f"shadow_profile_consistent={str(bool(comparison.get('shadow_reason_profile_consistent'))).lower()}",
        f"baseline_profile={_promotion_profile_text(comparison.get('current_target_formal_evidence'))}",
        f"shadow_profile={_promotion_profile_text(comparison.get('shadow_target_formal_evidence'))}",
        (
            "repeat="
            f"attempts:{int(repeat.get('total_attempts') or 0)},"
            f"unique_q:{int(repeat.get('unique_questions') or 0)},"
            f"same_q:{int(repeat.get('same_question_repeats') or 0)},"
            f"justified_bypass:{int(repeat_counts.get('justified_cooldown_bypass') or 0)},"
            f"spaced:{int(repeat_counts.get('adaptive_spaced_repeat') or 0)},"
            f"unexplained_recent:{int(repeat_counts.get('adaptive_unexplained_repeat') or 0)},"
            f"metadata_inconsistent:{int(repeat_counts.get('adaptive_metadata_inconsistent') or 0)},"
            f"nonadaptive:{int(repeat_counts.get('nonadaptive_repeat') or 0)},"
            f"metadata_unavailable:{int(repeat_counts.get('audit_metadata_unavailable') or 0)}"
        ),
        (
            "saved_adaptive="
            f"exists:{str(bool(saved.get('exists'))).lower()},"
            f"status:{saved.get('session_status') or 'none'},"
            f"events:{int(saved.get('event_count') or 0)},"
            f"questions:{int(saved.get('question_count') or 0)},"
            f"unique_q:{int(saved.get('unique_question_count') or 0)},"
            f"audit_complete:{str(bool(saved.get('audit_fields_complete'))).lower()},"
            f"recent_repeats:{int(saved.get('recent_repeat_count') or 0)},"
            f"bypasses:{int(saved.get('cooldown_bypass_count') or 0)},"
            f"recent_q:{recent_ids},bypass_q:{bypass_ids}"
        ),
        (
            "retrospective="
            f"anchors:{int(replay.get('plan_anchor_count') or 0)},"
            f"eligible:{int(replay.get('eligible_snapshot_count') or 0)},"
            f"excluded:{int(replay.get('coverage_excluded_count') or 0)},"
            f"agreement:{int(replay.get('agreement_count') or 0)},"
            f"shadow_stronger:{int(replay.get('shadow_stronger_disagreement_count') or 0)},"
            f"current_stronger:{int(replay.get('current_stronger_disagreement_count') or 0)},"
            f"inconclusive:{int(replay.get('inconclusive_disagreement_count') or 0)},"
            f"phase11_safety_miss:{int(replay.get('phase11_critical_safety_miss_candidate_count') or replay.get('critical_safety_miss_candidate_count') or 0)},"
            f"baseline_safety_miss:{int(replay.get('baseline_stronger_safety_miss_candidate_count') or 0)},"
            f"j2_j3_trigger_mismatch:{int(replay.get('ordinary_single_wrong_takeover_candidate_count') or 0)}"
        ),
        (
            "states="
            f"unseen:{int(states.get('unseen') or 0)},"
            f"checking:{int(states.get('checking') or 0)},"
            f"repairing:{int(states.get('repairing') or 0)},"
            f"repaired:{int(states.get('repaired') or 0)},"
            f"recheck_due:{int(states.get('recheck_due') or 0)},"
            f"stable:{int(states.get('stable') or 0)}"
        ),
        (
            "transitions="
            f"repairing_to_repaired:{int(transition_counts.get('repairing_to_repaired') or 0)},"
            f"repaired_to_repairing:{int(transition_counts.get('repaired_to_repairing') or 0)},"
            f"recheck_due_to_stable:{int(transition_counts.get('recheck_due_to_stable') or 0)},"
            f"recheck_due_to_repairing:{int(transition_counts.get('recheck_due_to_repairing') or 0)}"
        ),
        (
            "repairability="
            f"repairing_nodes:{int(repairability.get('repairing_node_total') or 0)},"
            f"strong_available:{int(repairability.get('strong_available_count') or 0)},"
            f"weak_only:{int(repairability.get('weak_only_count') or 0)},"
            f"blocked:{int(repairability.get('same_or_blocked_count') or 0)},"
            f"repairable_rate:{repairability.get('repairable_rate') if repairability.get('repairable_rate') is not None else 'none'}"
        ),
        (
            "adaptive_simulation="
            f"count:{int(adaptive_count or 0)},"
            f"unique_q:{int(adaptive_unique_questions or 0)},"
            f"unique_nodes:{int(adaptive_unique_nodes or 0)},"
            f"repair:{int(groups.get('repair') or 0)},"
            f"checking:{int(groups.get('checking') or 0)},"
            f"exploration:{int(groups.get('exploration') or 0)},"
            f"maintenance:{int(groups.get('maintenance') or 0)}"
        ),
    ]
    for index, snapshot in enumerate(replay.get("snapshots") or [], start=1):
        eligible = bool(snapshot.get("eligible"))
        issues = " | ".join(str(item) for item in (snapshot.get("coverage_issues") or [])) or "none"
        lines.append(
            "replay_snapshot_" + str(index) + "=" + ",".join([
                f"at:{snapshot.get('snapshot_jst') or snapshot.get('snapshot_at') or 'none'}",
                f"eligible:{str(eligible).lower()}",
                f"coverage:{snapshot.get('coverage_status') or 'none'}",
                f"baseline:{snapshot.get('baseline_target') or 'none'}",
                f"baseline_goal:{snapshot.get('baseline_goal') if snapshot.get('baseline_goal') is not None else 'none'}",
                f"baseline_phase:{snapshot.get('baseline_phase') or 'none'}",
                f"shadow:{snapshot.get('shadow_target') or 'none'}",
                f"shadow_reason:{snapshot.get('shadow_reason_code') or 'none'}",
                f"comparison:{snapshot.get('comparison_label') or 'none'}",
                f"review:{snapshot.get('review_category') or 'none'}",
                f"profile_consistent:{str(bool(snapshot.get('shadow_reason_profile_consistent'))).lower() if eligible else 'none'}",
                f"phase11_safety_miss:{str(bool(snapshot.get('phase11_critical_safety_miss_candidate') or snapshot.get('critical_safety_miss_candidate'))).lower()}",
                f"baseline_safety_miss:{str(bool(snapshot.get('baseline_stronger_safety_miss_candidate'))).lower()}",
                f"j2_j3_trigger_mismatch:{str(bool(snapshot.get('ordinary_single_wrong_takeover_candidate'))).lower()}",
                f"coverage_issues:{issues}",
            ])
        )
    return "\n".join(lines)


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

    field_evidence = build_field_evidence(all_attempts, as_of=now)
    current_guidance = _current_dashboard_guidance(user_id)
    shadow_judgment = build_shadow_judgment(
        all_attempts,
        field_evidence,
        current_guidance,
        as_of=now,
    )
    field_judgment_profiles = build_field_judgment_evidence_profiles(
        all_attempts,
        field_evidence,
        as_of=now,
    )
    shadow_judgment["comparison"] = build_shadow_comparison(
        current_guidance,
        shadow_judgment,
        field_judgment_profiles,
    )
    confident_wrong_node_details = build_confident_wrong_node_details(
        all_attempts,
        field_evidence,
        shadow_judgment,
        as_of=now,
    )
    saved_adaptive_daily_audit = build_saved_adaptive_daily_audit(
        get_latest_adaptive_daily_learning_session_events(user_id)
    )
    repairing_node_repairability = build_repairing_node_repairability(
        all_attempts,
        as_of=now,
    )
    strong_repair_supply_priorities = build_strong_repair_supply_priorities(
        repairing_node_repairability
    )
    repeat_structure_audit = build_repeat_structure_audit(
        attempts,
        get_learning_events_by_event_keys(
            user_id,
            {str(item.get("event_key") or "") for item in attempts},
        ),
    )
    retrospective_shadow_audit = build_retrospective_shadow_audit(
        all_attempts,
        get_learning_events(user_id),
    )
    promotion_evidence_text = build_phase11_promotion_evidence_text(
        period=period,
        shadow_judgment=shadow_judgment,
        repeat_structure_audit=repeat_structure_audit,
        saved_adaptive_daily_audit=saved_adaptive_daily_audit,
        retrospective_shadow_audit=retrospective_shadow_audit,
        state_counts={state: state_counts[state] for state in STATES},
        transitions={
            "repairing_to_repaired": transitions[("repairing", "repaired")],
            "repaired_to_repairing": transitions[("repaired", "repairing")],
            "recheck_due_to_stable": transitions[("recheck_due", "stable")],
            "recheck_due_to_repairing": transitions[("recheck_due", "repairing")],
        },
        repairing_node_repairability=repairing_node_repairability,
        adaptive_count=len(adaptive),
        adaptive_unique_questions=len({x["question_id"] for x in adaptive}),
        adaptive_unique_nodes=len({x["canonical_node_id"] for x in adaptive}),
        adaptive_groups=dict(adaptive_groups),
    )

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
        "current_guidance": current_guidance,
        "shadow_judgment": shadow_judgment,
        "confident_wrong_node_details": confident_wrong_node_details,
        "saved_adaptive_daily_audit": saved_adaptive_daily_audit,
        "repairing_node_repairability": repairing_node_repairability,
        "strong_repair_supply_priorities": strong_repair_supply_priorities,
        "repeat_structure_audit": repeat_structure_audit,
        "retrospective_shadow_audit": retrospective_shadow_audit,
        "promotion_evidence_text": promotion_evidence_text,
    }
