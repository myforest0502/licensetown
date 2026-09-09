from datetime import datetime, timezone
import random

from adaptive_question_selector import select_node_adaptive_questions
from knowledge_node_repair_evidence import SAME_QUESTION, classify_repair_confirmation
from knowledge_node_state_transition import derive_all_user_node_states, derive_knowledge_node_state
from knowledge_node_weakness_evidence import (
    REPEATED_SAME_QUESTION_WRONG,
    derive_repeated_weakness_evidence,
)
from question_equivalence import (
    are_equivalent_questions,
    canonicalize_question_evidence_id,
    canonicalize_question_evidence_node,
    equivalent_question_ids,
    get_question_equivalence_groups,
)


def _attempt(q, node, *, correct, confidence=1, at="2026-09-01T00:00:00+00:00"):
    return {
        "user_id": "u1",
        "question_id": q,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": at,
    }


def test_reviewed_exact_official_repeat_groups_are_registered():
    groups = get_question_equivalence_groups()
    assert len(groups) == 4
    assert {frozenset(item["question_ids"]) for item in groups} == {
        frozenset(("Q972", "Q1354")),
        frozenset(("Q1067", "Q1391")),
        frozenset(("Q1230", "Q1526")),
        frozenset(("Q1411", "Q1585")),
    }


def test_equivalent_questions_share_one_evidence_identity():
    assert canonicalize_question_evidence_id("Q1354") == "Q972"
    assert canonicalize_question_evidence_id("Q1585") == "Q1411"
    assert equivalent_question_ids("Q1411") == frozenset(("Q1411", "Q1585"))
    assert are_equivalent_questions("Q1411", "Q1585") is True
    assert are_equivalent_questions("Q1411", "Q667") is False


def test_cross_node_exact_repeat_uses_reviewed_evidence_node_without_mutating_raw_id():
    assert canonicalize_question_evidence_node("Q1411", "KN1387") == "KN1387"
    assert canonicalize_question_evidence_node("Q1585", "KN0659") == "KN1387"


def test_exact_repeat_can_never_be_strong_repair_confirmation():
    for first, second in (
        ("Q972", "Q1354"),
        ("Q1067", "Q1391"),
        ("Q1230", "Q1526"),
        ("Q1411", "Q1585"),
    ):
        assert classify_repair_confirmation(first, second) == SAME_QUESTION
        assert classify_repair_confirmation(second, first) == SAME_QUESTION


def test_equivalent_wrong_ids_do_not_create_cross_question_weakness():
    attempts = [
        _attempt("Q972", "KN0962", correct=False, at="2026-09-01T00:00:00+00:00"),
        _attempt("Q1354", "KN0962", correct=False, at="2026-09-02T00:00:00+00:00"),
    ]
    evidence = derive_repeated_weakness_evidence(attempts)[0]
    assert evidence["distinct_question_count"] == 1
    assert evidence["wrong_question_count"] == 1
    assert evidence["evidence_level"] == REPEATED_SAME_QUESTION_WRONG


def test_cross_node_exact_repeat_is_one_derived_node_and_one_question():
    attempts = [
        _attempt("Q1585", "KN0659", correct=True, at="2026-09-01T00:00:00+00:00"),
        _attempt("Q1411", "KN1387", correct=True, at="2026-09-02T00:00:00+00:00"),
    ]
    states = derive_all_user_node_states(
        attempts,
        as_of=datetime(2026, 9, 3, tzinfo=timezone.utc),
    )
    assert len(states) == 1
    assert states[0]["canonical_node_id"] == "KN1387"
    assert states[0]["distinct_question_count"] == 1
    assert states[0]["state"] == "checking"


def test_cross_node_exact_repeat_correct_does_not_confirm_prior_wrong():
    attempts = [
        _attempt("Q1411", "KN1387", correct=False, at="2026-09-01T00:00:00+00:00"),
        _attempt("Q1585", "KN0659", correct=True, confidence=1, at="2026-09-02T00:00:00+00:00"),
    ]
    state = derive_knowledge_node_state(attempts, as_of=datetime(2026, 9, 2, tzinfo=timezone.utc))
    assert state["canonical_node_id"] == "KN1387"
    assert state["state"] == "repairing"
    assert state["confident_correct_after_wrong_count"] == 0


def test_selector_exclude_applies_to_entire_equivalence_group():
    records = select_node_adaptive_questions(
        [],
        question_count=30,
        exclude_ids=("Q1585",),
        rng=random.Random(7),
        as_of=datetime(2026, 9, 9, tzinfo=timezone.utc),
    )
    selected = {item["question_id"] for item in records}
    assert "Q1585" not in selected
    assert "Q1411" not in selected


def test_recent_equivalent_member_applies_cooldown_to_whole_group():
    attempts = [
        _attempt("Q1585", "KN0659", correct=True, at="2026-09-09T00:00:00+00:00"),
    ]
    records = select_node_adaptive_questions(
        attempts,
        question_count=30,
        rng=random.Random(11),
        as_of=datetime(2026, 9, 9, 1, tzinfo=timezone.utc),
    )
    selected = {item["question_id"] for item in records}
    assert "Q1585" not in selected
    assert "Q1411" not in selected
