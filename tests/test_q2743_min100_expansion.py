import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "licensetown" / "pt" / "data" / "question_bank"


def _read(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def test_q2743_minimum_100_field_supply_contract():
    questions = _read("questions.json")
    counts = Counter(int(row["category_small"]) for row in questions)
    assert len(questions) == 2743
    assert min(counts[field_id] for field_id in range(1, 19)) >= 100
    assert {
        field_id: counts[field_id]
        for field_id in (3, 4, 5, 6, 7, 10, 11, 12, 13, 14)
    } == {
        3: 100,
        4: 100,
        5: 100,
        6: 100,
        7: 100,
        10: 100,
        11: 100,
        12: 100,
        13: 100,
        14: 100,
    }


def test_q2234_q2743_have_complete_parallel_records():
    questions = {row["id"]: row for row in _read("questions.json")}
    answers = {row["id"]: row for row in _read("answers.json")}
    explanations = {row["id"]: row for row in _read("explanations.json")}
    tags = {row["id"]: row for row in _read("question_tags.json")}

    ids = [f"Q{i}" for i in range(2234, 2744)]
    assert len(ids) == 510
    for qid in ids:
        assert qid in questions
        assert qid in answers
        assert qid in explanations
        assert qid in tags
        assert questions[qid]["source"] == "O"
        assert answers[qid]["answer_basis"] == "LT_original"
        assert tags[qid]["source"] == "original"
        assert tags[qid]["tag_status"] == "provisional_bulk"
        assert len(questions[qid]["choices"]) == 5
        assert len(explanations[qid]["choice_explanations"]) == 5
        assert len(answers[qid]["accepted_answer_sets"]) == 1
        assert len(answers[qid]["accepted_answer_sets"][0]) == 1


def test_q2234_q2743_stems_are_unique_and_not_exact_existing_stems():
    questions = _read("questions.json")
    old = {
        row["question_text"]
        for row in questions
        if int(row["id"][1:]) <= 2233
    }
    new = [
        row["question_text"]
        for row in questions
        if 2234 <= int(row["id"][1:]) <= 2743
    ]
    assert len(new) == 510
    assert len(set(new)) == 510
    assert not (set(new) & old)
