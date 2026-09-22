import json
from pathlib import Path

from question_equivalence import (
    are_equivalent_questions,
    canonicalize_question_evidence_id,
    get_question_equivalence_groups,
)

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "licensetown" / "pt" / "data" / "question_bank"


def _read(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def test_q2743_provisional_same_source_choice_repeats_are_one_evidence_identity():
    groups = [
        row
        for row in get_question_equivalence_groups()
        if row["equivalence_type"] == "provisional_same_source_choice_repeat"
    ]
    assert len(groups) == 55

    tags = {row["id"]: row for row in _read("question_tags.json")}
    members = set()
    for group in groups:
        assert group["review_status"] == "reviewed"
        assert len(group["question_ids"]) == 2
        first, second = group["question_ids"]
        assert 2234 <= int(first[1:]) <= 2743
        assert 2234 <= int(second[1:]) <= 2743
        assert tags[first]["knowledge_node_id"] == tags[second]["knowledge_node_id"]
        assert group["canonical_knowledge_node_id"] == tags[first]["knowledge_node_id"]
        assert canonicalize_question_evidence_id(first) == first
        assert canonicalize_question_evidence_id(second) == first
        assert are_equivalent_questions(first, second)
        members.update(group["question_ids"])

    assert len(members) == 110
