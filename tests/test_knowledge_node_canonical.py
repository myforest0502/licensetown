import json
from pathlib import Path

from knowledge_node_canonical import (
    canonicalize_knowledge_node_id,
    get_knowledge_node_canonical_map,
    group_attempts_by_canonical_node,
    is_cross_question_evidence,
    load_and_validate_canonical_map,
)


BANK_DIR = Path(__file__).resolve().parents[1] / "data" / "question_bank"
EXPECTED = {
    "KN0807": "KN0597",
    "KN1509": "KN1337",
    "KN1292": "KN1082",
    "KN1210": "KN0609",
    "KN0272": "KN0205",
}


def attempt(question_id, node_id, user_id="user-a"):
    return {
        "user_id": user_id,
        "question_id": question_id,
        "knowledge_node_id": node_id,
        "is_correct": True,
    }


def test_all_five_reviewed_aliases_map_to_lower_canonical_ids():
    records, aliases = load_and_validate_canonical_map()
    assert len(records) == 5
    assert aliases == EXPECTED
    assert len(get_knowledge_node_canonical_map()) == 5


def test_alias_canonical_and_unknown_resolution():
    assert canonicalize_knowledge_node_id("KN0807") == "KN0597"
    assert canonicalize_knowledge_node_id("KN0597") == "KN0597"
    assert canonicalize_knowledge_node_id("KN9999") == "KN9999"
    assert canonicalize_knowledge_node_id(None) is None


def test_raw_alias_and_canonical_attempts_group_together_without_rewrite():
    original = [attempt("Q605", "KN0597"), attempt("Q815", "KN0807")]
    grouped = group_attempts_by_canonical_node(original)
    combined = grouped[("user-a", "KN0597")]
    assert len(combined) == 2
    assert {item["question_id"] for item in combined} == {"Q605", "Q815"}
    assert {item["knowledge_node_id"] for item in combined} == {"KN0597", "KN0807"}
    assert "canonical_knowledge_node_id" not in original[0]


def test_cross_question_requires_different_question_ids_on_same_canonical_node():
    canonical = attempt("Q605", "KN0597")
    same_question_alias = attempt("Q605", "KN0807")
    other_question_alias = attempt("Q815", "KN0807")
    unrelated = attempt("Q815", "KN0808")
    assert not is_cross_question_evidence(canonical, same_question_alias)
    assert is_cross_question_evidence(canonical, other_question_alias)
    assert not is_cross_question_evidence(canonical, unrelated)


def test_reviewed_candidates_preserve_original_ids_questions_and_reasons():
    candidates = json.loads(
        (BANK_DIR / "knowledge_node_merge_candidates.json").read_text(encoding="utf-8-sig")
    )
    assert len(candidates) == 5
    assert all(item["review_status"] == "reviewed" for item in candidates)
    assert [item["node_ids"] for item in candidates] == [
        ["KN0597", "KN0807"],
        ["KN1337", "KN1509"],
        ["KN1082", "KN1292"],
        ["KN0609", "KN1210"],
        ["KN0205", "KN0272"],
    ]
    assert all(item["question_ids"] and item["reason"] for item in candidates)
