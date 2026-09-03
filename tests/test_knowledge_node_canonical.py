import json
import shutil
from pathlib import Path

import pytest

from knowledge_node_canonical import (
    KnowledgeNodeCanonicalValidationError,
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


def test_v02_keeps_original_aliases_and_adds_reviewed_clusters():
    records, aliases = load_and_validate_canonical_map()
    assert len(records) == 25
    assert len(aliases) == 30
    assert all(aliases[alias] == canonical for alias, canonical in EXPECTED.items())
    assert len(get_knowledge_node_canonical_map()) == 25


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


@pytest.mark.parametrize(("canonical", "aliases"), [
    ("KN0071", ["KN0126", "KN0195", "KN0211"]),
    ("KN0202", ["KN0227", "KN0318"]),
    ("KN1337", ["KN0945", "KN1509"]),
    ("KN0205", ["KN0272", "KN1421"]),
])
def test_expanded_clusters_resolve_directly_and_support_cross_question_evidence(
    canonical, aliases,
):
    assert canonicalize_knowledge_node_id(canonical) == canonical
    for index, alias in enumerate(aliases, 1):
        assert canonicalize_knowledge_node_id(alias) == canonical
        assert is_cross_question_evidence(
            attempt("Q1", canonical), attempt(f"Q{index + 1}", alias)
        )


def test_aoi_review_preserves_boundaries_without_canonicalizing_snc0024():
    reviews = json.loads(
        (BANK_DIR / "same_node_review_v0.2.json").read_text(encoding="utf-8-sig")
    )
    assert len(reviews) == 39
    assert all(item["review_status"] == "reviewed" for item in reviews)
    rejected_same = next(item for item in reviews if item["candidate_id"] == "SNC0024")
    assert rejected_same["aoi_decision"] == "PREREQUISITE_CANDIDATE"
    assert rejected_same["source_node_id"] == "KN1175"
    assert rejected_same["target_node_id"] == "KN0842"
    assert rejected_same["canonical_node_id"] is None
    assert canonicalize_knowledge_node_id("KN0842") == "KN0842"
    assert canonicalize_knowledge_node_id("KN1175") == "KN1175"

    by_id = {item["candidate_id"]: item for item in reviews}
    assert by_id["SNC0026"]["aoi_decision"] == "RELATED_ONLY"
    assert (by_id["SNC0027"]["source_node_id"], by_id["SNC0027"]["target_node_id"]) == (
        "KN0647", "KN1533",
    )
    assert (by_id["SNC0028"]["source_node_id"], by_id["SNC0028"]["target_node_id"]) == (
        "KN1499", "KN0184",
    )
    assert (by_id["SNC0029"]["source_node_id"], by_id["SNC0029"]["target_node_id"]) == (
        "KN1112", "KN1439",
    )
    assert by_id["SNC0030"]["aoi_decision"] == "TRANSFER_CANDIDATE"
    assert by_id["SNC0031"]["aoi_decision"] == "TRANSFER_CANDIDATE"
    assert all(by_id[f"SNC{number:04d}"]["aoi_decision"] == "RELATED_ONLY" for number in range(32, 37))
    assert all(by_id[f"SNC{number:04d}"]["aoi_decision"] == "UNRELATED" for number in range(37, 39))


def _copy_bank_for_validation(tmp_path):
    for name in (
        "knowledge_node_canonical_map.json",
        "knowledge_node_merge_candidates.json",
        "knowledge_nodes.json",
        "same_node_review_v0.2.json",
    ):
        shutil.copyfile(BANK_DIR / name, tmp_path / name)


def _read_temp(tmp_path, name):
    return json.loads((tmp_path / name).read_text(encoding="utf-8-sig"))


def _write_temp(tmp_path, name, value):
    (tmp_path / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def test_validation_rejects_duplicate_alias_and_alias_chain(tmp_path):
    _copy_bank_for_validation(tmp_path)
    records = _read_temp(tmp_path, "knowledge_node_canonical_map.json")
    records[-1]["alias_node_ids"] = ["KN0807"]
    reviews = _read_temp(tmp_path, "same_node_review_v0.2.json")
    review = next(item for item in reviews if item["candidate_id"] == "SNC0025")
    review["alias_node_ids"] = ["KN0807"]
    _write_temp(tmp_path, "knowledge_node_canonical_map.json", records)
    _write_temp(tmp_path, "same_node_review_v0.2.json", reviews)
    with pytest.raises(KnowledgeNodeCanonicalValidationError):
        load_and_validate_canonical_map(tmp_path)


def test_validation_rejects_changed_existing_root(tmp_path):
    _copy_bank_for_validation(tmp_path)
    records = _read_temp(tmp_path, "knowledge_node_canonical_map.json")
    record = next(item for item in records if item["candidate_id"] == "KNC0002")
    record["canonical_node_id"] = "KN0945"
    record["alias_node_ids"] = ["KN1337", "KN1509"]
    _write_temp(tmp_path, "knowledge_node_canonical_map.json", records)
    with pytest.raises(KnowledgeNodeCanonicalValidationError):
        load_and_validate_canonical_map(tmp_path)


def test_validation_rejects_unknown_node(tmp_path):
    _copy_bank_for_validation(tmp_path)
    records = _read_temp(tmp_path, "knowledge_node_canonical_map.json")
    records[-1]["alias_node_ids"] = ["KN9999"]
    reviews = _read_temp(tmp_path, "same_node_review_v0.2.json")
    review = next(item for item in reviews if item["candidate_id"] == "SNC0025")
    review["alias_node_ids"] = ["KN9999"]
    _write_temp(tmp_path, "knowledge_node_canonical_map.json", records)
    _write_temp(tmp_path, "same_node_review_v0.2.json", reviews)
    with pytest.raises(KnowledgeNodeCanonicalValidationError):
        load_and_validate_canonical_map(tmp_path)


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
