import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "licensetown" / "pt" / "data" / "question_bank"


def _read(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def test_provisional_bulk_stem_direction_matches_accepted_rationale():
    questions = {row["id"]: row for row in _read("questions.json")}
    answers = {row["id"]: row for row in _read("answers.json")}

    conflicts = []
    for number in range(2234, 2744):
        qid = f"Q{number}"
        question = questions[qid]
        answer_key = str(answers[qid]["accepted_answer_sets"][0][0])
        rationale = question["choices"][answer_key].strip()
        stem = question["question_text"]

        correct_stem = (
            "判断が正しい理由" in stem
            or "という判断が正しい理由" in stem
            or "判断を支持する根拠" in stem
        )
        wrong_stem = "適切でない理由" in stem or "不適切である根拠" in stem

        negative_rationale = bool(
            re.search(r"ではない|不適切|誤り|低くない|必要はない|妥当でない", rationale)
        )
        positive_rationale = bool(
            re.search(r"(?<!不)適切[。．]?$|正しい[。．]?$", rationale)
        )

        if (correct_stem and negative_rationale) or (wrong_stem and positive_rationale):
            conflicts.append((qid, stem, rationale))

    assert conflicts == []
