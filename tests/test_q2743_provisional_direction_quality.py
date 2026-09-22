import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "licensetown" / "pt" / "data" / "question_bank"


def _read(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def _norm(text):
    text = re.sub(r"^[〇○]\s*[。．.]\s*", "", str(text or ""))
    text = re.sub(r"\s+", "", text)
    return re.sub(r"[。．.]$", "", text)


def test_provisional_bulk_preserves_source_context_and_direction():
    questions = {row["id"]: row for row in _read("questions.json")}
    answers = {row["id"]: row for row in _read("answers.json")}
    explanations = {row["id"]: row for row in _read("explanations.json")}

    source_by_signature = {}
    for number in range(1, 2001):
        qid = f"Q{number}"
        rationale_set = explanations[qid]["choice_explanations"]
        signature = tuple(sorted(_norm(v) for v in rationale_set.values()))
        source_by_signature[signature] = qid

    negative_question = re.compile(
        r"誤っているのは|誤りは|適切でないのは|正しくないのは|不適切なのは"
    )

    failures = []
    for number in range(2234, 2744):
        qid = f"Q{number}"
        question = questions[qid]
        answer_key = str(answers[qid]["accepted_answer_sets"][0][0])
        accepted_rationale = _norm(question["choices"][answer_key])
        signature = tuple(sorted(_norm(v) for v in question["choices"].values()))
        source_id = source_by_signature.get(signature)

        if source_id is None:
            failures.append((qid, "missing_unique_source"))
            continue

        source_question = questions[source_id]
        source_explanations = explanations[source_id]["choice_explanations"]
        source_choice_matches = [
            str(key)
            for key, value in source_explanations.items()
            if _norm(value) == accepted_rationale
        ]
        if len(source_choice_matches) != 1:
            failures.append((qid, "source_choice_match", source_choice_matches))
            continue

        source_choice_key = source_choice_matches[0]
        source_choice_text = source_question["choices"][source_choice_key]
        source_is_negative = bool(negative_question.search(source_question["question_text"]))
        source_accepted = source_choice_key in {
            str(value)
            for answer_set in answers[source_id]["accepted_answer_sets"]
            for value in answer_set
        }
        statement_is_true = source_accepted != source_is_negative

        stem = question["question_text"]
        if source_question["question_text"] not in stem:
            failures.append((qid, "missing_source_context", source_id))
        if source_choice_text not in stem:
            failures.append((qid, "missing_source_choice", source_choice_key))

        positive_direction = "正しい理由" in stem or "妥当である根拠" in stem
        negative_direction = "適切でない理由" in stem or "不適切である根拠" in stem
        if statement_is_true and not positive_direction:
            failures.append((qid, "should_be_positive", source_id, source_choice_key))
        if not statement_is_true and not negative_direction:
            failures.append((qid, "should_be_negative", source_id, source_choice_key))

    assert failures == []
