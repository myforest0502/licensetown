from datetime import datetime, timedelta, timezone

from knowledge_node_weakness_evidence import (
    CROSS_QUESTION_CONFIDENT_WRONG,
    CROSS_QUESTION_WRONG,
    REPEATED_SAME_QUESTION_WRONG,
    SINGLE_WRONG,
)
from phase11_active_safety import build_active_safety_candidates


BASE = datetime(2026, 9, 1, tzinfo=timezone.utc)


def fact(
    *,
    wrong_qs,
    level=SINGLE_WRONG,
    confident=False,
    count=1,
    when=BASE,
):
    return {
        "active_evaluable_wrong_question_ids": list(wrong_qs),
        "active_evaluable_wrong_attempt_count": count,
        "active_has_confident_wrong": confident,
        "active_weakness_evidence_level": level,
        "active_last_evaluable_wrong_at": when,
    }


def test_unknown_only_or_no_evaluable_wrong_creates_no_safety_candidate():
    candidates = build_active_safety_candidates(
        {"KN1": fact(wrong_qs=[], count=0)},
        field_by_question={"Q1": 8},
        critical_nodes={"KN1"},
    )
    assert candidates == []


def test_noncritical_active_wrong_is_not_j1_candidate():
    candidates = build_active_safety_candidates(
        {"KN1": fact(wrong_qs=["Q1"])},
        field_by_question={"Q1": 8},
        critical_nodes=set(),
    )
    assert candidates == []


def test_j1_tier_order_matches_existing_phase11_policy():
    candidates = build_active_safety_candidates(
        {
            "KNCROSSCONF": fact(
                wrong_qs=["Q1", "Q2"],
                level=CROSS_QUESTION_CONFIDENT_WRONG,
                confident=True,
            ),
            "KNCROSS": fact(
                wrong_qs=["Q3", "Q4"],
                level=CROSS_QUESTION_WRONG,
            ),
            "KNCONF": fact(wrong_qs=["Q5"], confident=True),
            "KNREPEAT": fact(
                wrong_qs=["Q6"],
                level=REPEATED_SAME_QUESTION_WRONG,
                count=2,
            ),
            "KNSINGLE": fact(wrong_qs=["Q7"]),
        },
        field_by_question={
            "Q1": 8, "Q2": 8, "Q3": 8, "Q4": 8,
            "Q5": 8, "Q6": 8, "Q7": 8,
        },
        critical_nodes={"KNCROSSCONF", "KNCROSS", "KNCONF", "KNREPEAT", "KNSINGLE"},
    )
    assert [item["canonical_node_id"] for item in candidates] == [
        "KNCROSSCONF", "KNCROSS", "KNCONF", "KNREPEAT", "KNSINGLE"
    ]
    assert [item["priority_tier"] for item in candidates] == [0, 1, 2, 3, 4]


def test_more_recent_wrong_wins_within_same_tier():
    candidates = build_active_safety_candidates(
        {
            "KNOLD": fact(wrong_qs=["Q1"], when=BASE),
            "KNNEW": fact(wrong_qs=["Q2"], when=BASE + timedelta(hours=1)),
        },
        field_by_question={"Q1": 8, "Q2": 8},
        critical_nodes={"KNOLD", "KNNEW"},
    )
    assert [item["canonical_node_id"] for item in candidates] == ["KNNEW", "KNOLD"]


def test_multi_field_node_uses_only_observed_wrong_source_fields():
    candidates = build_active_safety_candidates(
        {"KN1": fact(wrong_qs=["Q1", "Q2"], level=CROSS_QUESTION_WRONG)},
        field_by_question={"Q1": 3, "Q2": 9},
        critical_nodes={"KN1"},
    )
    assert [item["field_id"] for item in candidates] == [3, 9]


def test_unobserved_static_member_field_is_not_invented():
    candidates = build_active_safety_candidates(
        {"KN1": fact(wrong_qs=["Q1"])},
        field_by_question={"Q1": 3, "QSTATIC": 9},
        critical_nodes={"KN1"},
    )
    assert [item["field_id"] for item in candidates] == [3]
