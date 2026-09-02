from pathlib import Path

pilot_path = Path("pilot_diagnostics.py")
text = pilot_path.read_text(encoding="utf-8")

marker = '''\n\ndef build_pilot_diagnostics(user_id: str, period: str = "7", now=None):\n'''
helper = r'''

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

    lines = [
        "PHASE11_PROMOTION_EVIDENCE_V1",
        f"selected_period={period_label}",
        "scope_note=period_metrics:selected_period;formal_current:all_history;replay:all_history",
        f"baseline_target={comparison.get('current_target') or 'none'}",
        f"shadow_target={shadow.get('target_field') or 'none'}",
        f"shadow_intent={shadow.get('learning_intent') or 'none'}",
        f"shadow_reason={shadow.get('reason_code') or 'none'}",
        f"shadow_confidence={shadow.get('confidence') or 'none'}",
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
    return "\n".join(lines)
'''

if helper not in text:
    if text.count(marker) != 1:
        raise SystemExit(f"formatter insertion marker count={text.count(marker)}")
    text = text.replace(marker, helper + marker)

old = '''    retrospective_shadow_audit = build_retrospective_shadow_audit(\n        all_attempts,\n        get_learning_events(user_id),\n    )\n\n    return {'''
new = '''    retrospective_shadow_audit = build_retrospective_shadow_audit(\n        all_attempts,\n        get_learning_events(user_id),\n    )\n    promotion_evidence_text = build_phase11_promotion_evidence_text(\n        period=period,\n        shadow_judgment=shadow_judgment,\n        repeat_structure_audit=repeat_structure_audit,\n        saved_adaptive_daily_audit=saved_adaptive_daily_audit,\n        retrospective_shadow_audit=retrospective_shadow_audit,\n        state_counts={state: state_counts[state] for state in STATES},\n        transitions={\n            "repairing_to_repaired": transitions[("repairing", "repaired")],\n            "repaired_to_repairing": transitions[("repaired", "repairing")],\n            "recheck_due_to_stable": transitions[("recheck_due", "stable")],\n            "recheck_due_to_repairing": transitions[("recheck_due", "repairing")],\n        },\n        repairing_node_repairability=repairing_node_repairability,\n        adaptive_count=len(adaptive),\n        adaptive_unique_questions=len({x["question_id"] for x in adaptive}),\n        adaptive_unique_nodes=len({x["canonical_node_id"] for x in adaptive}),\n        adaptive_groups=dict(adaptive_groups),\n    )\n\n    return {'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"bundle call target count={text.count(old)}")
    text = text.replace(old, new)

old_key = '''        "retrospective_shadow_audit": retrospective_shadow_audit,\n    }'''
new_key = '''        "retrospective_shadow_audit": retrospective_shadow_audit,\n        "promotion_evidence_text": promotion_evidence_text,\n    }'''
if new_key not in text:
    if text.count(old_key) != 1:
        raise SystemExit(f"bundle result target count={text.count(old_key)}")
    text = text.replace(old_key, new_key)

pilot_path.write_text(text, encoding="utf-8")

template_path = Path("templates/goukaku/supporter_pilot_diagnostics.html")
template = template_path.read_text(encoding="utf-8")
old_template = '''  </nav>\n  <section class="card pilot-diagnostic-card"><h2>学習量</h2>'''
new_template = '''  </nav>\n  <div class="adaptive-audit-actions phase11-promotion-evidence-copy">\n    <button type="button" data-copy-q-ids="{{ diagnostics.promotion_evidence_text }}">Phase11 Promotion evidenceをコピー</button>\n    <span aria-live="polite"></span>\n  </div>\n  <section class="card pilot-diagnostic-card"><h2>学習量</h2>'''
if new_template not in template:
    if template.count(old_template) != 1:
        raise SystemExit(f"template bundle button target count={template.count(old_template)}")
    template = template.replace(old_template, new_template)
template_path.write_text(template, encoding="utf-8")
