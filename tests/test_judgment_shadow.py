from datetime import datetime, timezone

import judgment_shadow as shadow


NOW = datetime(2026, 9, 1, tzinfo=timezone.utc)


def field_evidence(answer_counts=None, *, due=None, checking=None):
    answer_counts = answer_counts or {}
    due = due or {}
    checking = checking or {}
    fields = []
    for field_id, name in shadow.CATEGORY_NAMES.items():
        answers = answer_counts.get(field_id, 0)
        due_nodes = [
            {
                "canonical_node_id": f"KN-DUE-{field_id}-{index}",
                "state": "recheck_due",
                "due_overdue_days": days,
            }
            for index, days in enumerate(due.get(field_id, []), start=1)
        ]
        fields.append({
            "field_id": field_id,
            "field_name": name,
            "question_answer_count": answers,
            "question_correct_count": answers,
            "question_accuracy": 1.0 if answers else None,
            "node_coverage": {"percent": min(100.0, answers * 2.0)},
            "repairing_node_count": 0,
            "checking_node_count": checking.get(field_id, 0),
            "retention_nodes": due_nodes,
        })
    return {"fields": fields}


def guidance(field_id=1):
    return {
        "phase": "foundation",
        "recommended_study": [(shadow.CATEGORY_NAMES[field_id], 10)],
    }


def attempt(q, node, field_id, *, correct=True, confidence=1, safety="none"):
    return {
        "user_id": "u",
        "question_id": q,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": "answered",
        "_field_id": field_id,
        "_safety": safety,
        "answered_at": NOW,
    }


def install_catalog(monkeypatch, attempts, *, states=None, weakness=None):
    node_fields = {}
    question_fields = {}
    tags = {}
    for item in attempts:
        node_fields.setdefault(item["knowledge_node_id"], set()).add(item["_field_id"])
        question_fields[item["question_id"]] = item["_field_id"]
        tags[item["question_id"]] = {
            "knowledge_node_id": item["knowledge_node_id"],
            "safety": item["_safety"],
        }
    monkeypatch.setattr(shadow, "_catalog", lambda: (node_fields, question_fields))
    monkeypatch.setattr(shadow, "get_question_tag", lambda q: tags[q])
    monkeypatch.setattr(
        shadow,
        "derive_all_user_node_states",
        lambda *_args, **_kwargs: [
            {"canonical_node_id": node, "state": state}
            for node, state in (states or {}).items()
        ],
    )
    monkeypatch.setattr(
        shadow,
        "derive_repeated_weakness_evidence",
        lambda *_args, **_kwargs: list(weakness or []),
    )


def test_sparse_new_user_preserves_current_foundation_target(monkeypatch):
    install_catalog(monkeypatch, [])
    result = shadow.build_shadow_judgment([], field_evidence(), guidance(4), as_of=NOW)
    assert result["learning_intent"] == "coverage"
    assert result["target_field_id"] == 4
    assert result["reason_code"] == "insufficient_coverage"
    assert result["confidence"] == "low"


def test_one_ordinary_wrong_does_not_override_foundation(monkeypatch):
    attempts = [attempt("Qx", "KNx", 10, correct=False, confidence=2)]
    install_catalog(monkeypatch, attempts, states={"KNx": "repairing"})
    result = shadow.build_shadow_judgment(attempts, field_evidence({10: 1}), guidance(4), as_of=NOW)
    assert result["learning_intent"] == "coverage"
    assert result["target_field_id"] == 4


def test_critical_safety_wrong_overrides_foundation(monkeypatch):
    attempts = [attempt("Qs", "KNs", 9, correct=False, confidence=2, safety="critical")]
    install_catalog(monkeypatch, attempts, states={"KNs": "repairing"})
    result = shadow.build_shadow_judgment(attempts, field_evidence({9: 1}), guidance(4), as_of=NOW)
    assert result["learning_intent"] == "repair"
    assert result["target_field_id"] == 9
    assert result["reason_code"] == "safety_repair"
    assert result["confidence"] == "high"


def test_cross_question_confident_wrong_is_high_priority_repair(monkeypatch):
    attempts = [
        attempt("Q1", "KN1", 10, correct=False, confidence=1),
        attempt("Q2", "KN1", 10, correct=False, confidence=2),
    ]
    weakness = [{
        "canonical_node_id": "KN1",
        "evidence_level": shadow.CROSS_QUESTION_CONFIDENT_WRONG,
    }]
    install_catalog(monkeypatch, attempts, states={"KN1": "repairing"}, weakness=weakness)
    result = shadow.build_shadow_judgment(attempts, field_evidence({10: 2}), guidance(4), as_of=NOW)
    assert result["reason_code"] == "confident_wrong_cluster"
    assert result["target_field_id"] == 10


def test_cross_question_wrong_triggers_repair_without_confident_wrong(monkeypatch):
    attempts = [
        attempt("Q1", "KN1", 10, correct=False, confidence=2),
        attempt("Q2", "KN1", 10, correct=False, confidence=2),
    ]
    weakness = [{
        "canonical_node_id": "KN1",
        "evidence_level": shadow.CROSS_QUESTION_WRONG,
    }]
    install_catalog(monkeypatch, attempts, states={"KN1": "repairing"}, weakness=weakness)
    result = shadow.build_shadow_judgment(attempts, field_evidence({10: 2}), guidance(4), as_of=NOW)
    assert result["reason_code"] == "repeated_wrong_cluster"
    assert result["target_field_id"] == 10


def test_lone_repeated_same_question_wrong_does_not_commandeer_field(monkeypatch):
    attempts = [
        attempt("Q1", "KN1", 10, correct=False, confidence=2),
        attempt("Q1", "KN1", 10, correct=False, confidence=2),
    ]
    weakness = [{
        "canonical_node_id": "KN1",
        "evidence_level": shadow.REPEATED_SAME_QUESTION_WRONG,
    }]
    install_catalog(monkeypatch, attempts, states={"KN1": "repairing"}, weakness=weakness)
    result = shadow.build_shadow_judgment(attempts, field_evidence({10: 2}), guidance(4), as_of=NOW)
    assert result["learning_intent"] == "coverage"
    assert result["target_field_id"] == 4


def test_recheck_due_outranks_foundation_coverage(monkeypatch):
    install_catalog(monkeypatch, [])
    evidence = field_evidence(due={7: [2, 4], 8: [10]})
    result = shadow.build_shadow_judgment([], evidence, guidance(4), as_of=NOW)
    assert result["learning_intent"] == "recheck"
    assert result["target_field_id"] == 7
    assert result["reason_code"] == "recheck_due"


def test_uncertain_correct_cluster_after_foundation(monkeypatch):
    attempts = []
    for i in range(1, 101):
        field_id = 3 if i <= 10 else 4
        attempts.append(attempt(
            f"Q{i}", f"KN{i}", field_id,
            correct=True,
            confidence=2 if field_id == 3 and i <= 3 else 1,
        ))
    install_catalog(monkeypatch, attempts, states={})
    counts = {field_id: 10 for field_id in shadow.CATEGORY_NAMES}
    result = shadow.build_shadow_judgment(
        attempts, field_evidence(counts, checking={3: 3}), {"phase": "analysis", "recommended_study": []}, as_of=NOW
    )
    assert result["learning_intent"] == "stabilization"
    assert result["target_field_id"] == 3
    assert result["reason_code"] == "uncertain_correct_cluster"


def test_maintenance_when_no_higher_signal_after_foundation(monkeypatch):
    attempts = [attempt(f"Q{i}", f"KN{i}", ((i - 1) % 18) + 1) for i in range(1, 181)]
    install_catalog(monkeypatch, attempts, states={})
    counts = {field_id: 10 for field_id in shadow.CATEGORY_NAMES}
    result = shadow.build_shadow_judgment(
        attempts, field_evidence(counts), {"phase": "analysis", "recommended_study": []}, as_of=NOW
    )
    assert result["learning_intent"] == "maintenance"
    assert result["target_field"] is None
    assert result["question_count"] == 30
    assert result["recommended_route"] == "adaptive_daily"


def test_compare_current_and_shadow_is_descriptive_only(monkeypatch):
    install_catalog(monkeypatch, [])
    current = guidance(4)
    result = shadow.build_shadow_judgment([], field_evidence(), current, as_of=NOW)
    comparison = shadow.compare_current_and_shadow(current, result)
    assert comparison["comparison_label"] == "same_target_same_reason"
    assert comparison["current"]["target_field"] == shadow.CATEGORY_NAMES[4]
    assert comparison["shadow"]["shadow_only"] is True
