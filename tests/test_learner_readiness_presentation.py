import learner_readiness_presentation as presentation


def _shadow(*, reason="coverage_expand", proven=False, stable=0, repaired=0, due=0):
    fields = [
        {
            "field_id": 1,
            "field_name": "神経医学",
            "node_coverage": 0.25,
            "state_counts": {
                "unseen": 70,
                "checking": 20,
                "repairing": 0,
                "repaired": repaired,
                "recheck_due": due,
                "stable": stable,
            },
        },
        {
            "field_id": 2,
            "field_name": "心理学",
            "node_coverage": 0.10,
            "state_counts": {
                "unseen": 90,
                "checking": 10,
                "repairing": 0,
                "repaired": 0,
                "recheck_due": 0,
                "stable": 0,
            },
        },
    ]
    return {
        "status": "dashboard_real_data_shadow_v0.1",
        "fields": fields,
        "weakness_top3": [
            {
                "field_name": "神経医学",
                "reason_code": reason,
                "is_proven_weakness": proven,
            }
        ],
        "recommendation_intent": {
            "target_field": "神経医学",
            "learning_intent": "repair" if proven else "exploration",
            "priority_reason": reason,
            "requested_question_count": 10,
            "exact_question_ids": None,
            "selector_owns_exact_q": True,
        },
    }


def _readiness(status, *, repaired=0, due=0, stable=0, safety_ready=True, trial=False):
    return {
        "version": "lt_pass_readiness_v0.1",
        "status": status,
        "components": {
            "retention": {
                "repaired_nodes": repaired,
                "recheck_due_nodes": due,
                "stable_nodes": stable,
            },
            "trial100": {
                "has_supportive_full_format_evidence": trial,
            },
            "safety": {"ready": safety_ready},
        },
    }


def _public_text(result):
    parts = [result["headline"], result["summary"], result["today_action"]["reason"]]
    parts.extend(item["message"] for item in result["attention_items"])
    parts.extend(item["message"] for item in result["stable_areas"])
    parts.extend(item["message"] for item in result["repair_areas"])
    parts.extend(item["message"] for item in result["coverage_gaps"])
    parts.extend([result["retention_message"], result["trial100_message"]])
    return " ".join(parts)


def test_all_statuses_have_plain_non_guaranteeing_copy():
    for status in presentation.STATUS_COPY:
        result = presentation.build_learner_readiness_presentation(
            _readiness(status), _shadow()
        )
        text = _public_text(result)
        assert result["headline"]
        assert "合格率" not in text
        assert "合格確実" not in text
        assert "必ず受かる" not in text


def test_sparse_coverage_is_not_described_as_proven_weakness():
    result = presentation.build_learner_readiness_presentation(
        _readiness("insufficient_evidence"), _shadow(reason="coverage_expand", proven=False)
    )
    assert result["headline"] == "まだ現在地を測っている途中"
    assert result["attention_items"][0]["proven_weakness"] is False
    assert "弱いと決まったわけではありません" in result["coverage_gaps"][0]["message"]


def test_safety_attention_and_action_are_first_class_but_not_alarmist():
    result = presentation.build_learner_readiness_presentation(
        _readiness("safety_attention_required", safety_ready=False),
        _shadow(reason="safety_repair", proven=True),
    )
    assert result["safety_attention"] is True
    assert result["headline"] == "まず大事なところを確認しよう"
    assert result["today_action"]["reason"] == "安全に関わる重要な内容を先に確認しよう。"
    assert result["attention_items"][0]["label"] == "大事な確認"


def test_repaired_and_stable_have_distinct_learner_language():
    repaired = presentation.build_learner_readiness_presentation(
        _readiness("retention_confirmation_needed", repaired=3),
        _shadow(repaired=3),
    )
    stable = presentation.build_learner_readiness_presentation(
        _readiness("approaching_readiness", stable=3),
        _shadow(stable=3),
    )
    assert "いったん修復できた" in repaired["retention_message"]
    assert "時間を空けても確認できた" in stable["retention_message"]
    assert stable["stable_areas"][0]["stable_count"] == 3


def test_internal_jargon_is_not_present_in_public_copy():
    result = presentation.build_learner_readiness_presentation(
        _readiness("repair_required", repaired=2),
        _shadow(reason="confident_wrong_repair", proven=True, repaired=2),
    )
    text = _public_text(result)
    for forbidden in ("KN0", "STRONG", "WEAK", "Phase11", "Phase12", "J1", "canonical", "cooldown"):
        assert forbidden not in text
    # Traceability stays internal and is never required to render as copy.
    assert result["trace"]["recommendation_reason_code"] == "confident_wrong_repair"


def test_cta_is_intent_only_and_contains_no_exact_question_ids():
    result = presentation.build_learner_readiness_presentation(
        _readiness("building_coverage"), _shadow()
    )
    action = result["today_action"]
    assert action["field"] == "神経医学"
    assert action["count"] == 10
    assert action["learning_intent"] == "exploration"
    assert action["reason_code"] == "coverage_expand"
    assert "question_id" not in action
    assert "exact_question_ids" not in action
