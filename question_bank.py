"""正式問題バンクを起動時に読み込み、出題・採点・解説を一元提供する。"""

from __future__ import annotations

import copy
import json
import logging
import random
import re
from pathlib import Path


logger = logging.getLogger(__name__)
QUESTION_BANK_DIR = Path(__file__).resolve().parent / "data" / "question_bank"
EXPECTED_QUESTION_IDS = {f"Q{number}" for number in range(1, 1565)}
QUESTION_BANK_ERROR_MESSAGE = (
    "おう、悪い。今は正式問題バンクを読み込めない状態だ。\n"
    "自由会話の問題には切り替えず、ここで止めておくぞ。少し待ってからもう一度試してくれ。"
)


class QuestionBankError(RuntimeError):
    pass


def _read_json(name: str) -> list[dict]:
    path = QUESTION_BANK_DIR / name
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError(f"{name} must contain a JSON array")
    return data


def _index(records: list[dict], name: str) -> dict[str, dict]:
    indexed = {}
    for record in records:
        q_id = str(record.get("id", "")).upper().strip()
        if not re.fullmatch(r"Q\d+", q_id) or q_id in indexed:
            raise ValueError(f"{name} has invalid or duplicate id: {q_id!r}")
        indexed[q_id] = record
    return indexed


def _load_question_bank():
    questions = _index(_read_json("questions.json"), "questions.json")
    answers = _index(_read_json("answers.json"), "answers.json")
    explanations = _index(_read_json("explanations.json"), "explanations.json")
    if set(questions) != EXPECTED_QUESTION_IDS:
        raise ValueError("Formal question bank must contain exactly Q1-Q1564")
    if set(questions) != set(answers) or set(questions) != set(explanations):
        raise ValueError("questions/answers/explanations ids do not match")
    return questions, answers, explanations


try:
    _QUESTIONS, _ANSWERS, _EXPLANATIONS = _load_question_bank()
    _LOAD_ERROR = None
except Exception as exc:  # 起動は継続し、学習開始時に固定エラーを返す。
    logger.exception("Failed to load formal question bank")
    _QUESTIONS, _ANSWERS, _EXPLANATIONS = {}, {}, {}
    _LOAD_ERROR = exc


def _canonical_id(q_id) -> str:
    text = str(q_id).upper().strip()
    if text.isdigit():
        text = f"Q{text}"
    if not re.fullmatch(r"Q\d+", text):
        raise QuestionBankError(f"Invalid question id: {q_id!r}")
    return text


def _require_loaded() -> None:
    if _LOAD_ERROR is not None:
        raise QuestionBankError("Formal question bank failed to load") from _LOAD_ERROR


def get_question(q_id) -> dict:
    _require_loaded()
    key = _canonical_id(q_id)
    try:
        return copy.deepcopy(_QUESTIONS[key])
    except KeyError as exc:
        raise QuestionBankError(f"Question not found: {key}") from exc


def get_answer(q_id) -> dict:
    _require_loaded()
    key = _canonical_id(q_id)
    try:
        return copy.deepcopy(_ANSWERS[key])
    except KeyError as exc:
        raise QuestionBankError(f"Answer not found: {key}") from exc


def get_explanation(q_id) -> dict:
    _require_loaded()
    key = _canonical_id(q_id)
    try:
        return copy.deepcopy(_EXPLANATIONS[key])
    except KeyError as exc:
        raise QuestionBankError(f"Explanation not found: {key}") from exc


def _choice_label(value: str) -> str:
    token = str(value).upper().strip()
    if token in "12345":
        return chr(ord("A") + int(token) - 1)
    return token


def _answer_tokens(answer) -> frozenset[str]:
    if isinstance(answer, (list, tuple, set, frozenset)):
        raw_tokens = answer
    else:
        compact = re.sub(r"[\s,、・/／]+", "", str(answer).upper())
        raw_tokens = list(compact)
    tokens = [_choice_label(token) for token in raw_tokens if str(token).strip()]
    return frozenset(tokens)


def is_answer_correct(question_or_answer: dict, selected_answer) -> bool:
    accepted = question_or_answer.get("accepted_answer_sets")
    if accepted:
        selected = _answer_tokens(selected_answer)
        return any(selected == _answer_tokens(answer_set) for answer_set in accepted)
    return _answer_tokens(selected_answer) == _answer_tokens(question_or_answer.get("answer", ""))


def display_answer(question_or_answer: dict) -> str:
    value = str(
        question_or_answer.get("display_answer", question_or_answer.get("answer", ""))
    )
    for number, label in zip("12345", "ABCDE"):
        value = value.replace(number, label)
    return value


def get_quiz_question(q_id) -> dict:
    question = get_question(q_id)
    answer = get_answer(q_id)
    explanation = get_explanation(q_id)
    choices = {
        _choice_label(key): str(value).strip()
        for key, value in question["choices"].items()
    }
    choice_explanations = {
        _choice_label(key): str(value).strip()
        for key, value in explanation.get("choice_explanations", {}).items()
    }
    accepted = [
        [_choice_label(value) for value in answer_set]
        for answer_set in answer.get("accepted_answer_sets", [])
    ]
    if not choices or not accepted or not explanation.get("explanation"):
        raise QuestionBankError(f"Incomplete formal question data: {_canonical_id(q_id)}")
    return {
        **question,
        "question": str(question["question_text"]).strip(),
        "choices": choices,
        "answer": display_answer(answer),
        "display_answer": display_answer(answer),
        "accepted_answer_sets": accepted,
        "answer_basis": answer.get("answer_basis"),
        "explanation": str(explanation["explanation"]).strip(),
        "choice_explanations": choice_explanations,
        "category": str(question.get("category_large", "未分類")),
    }


def select_random_questions(question_count: int) -> list[dict]:
    _require_loaded()
    if question_count > len(_QUESTIONS):
        raise QuestionBankError("Requested question count exceeds formal bank")
    ids = random.sample(list(_QUESTIONS), question_count)
    return [get_quiz_question(q_id) for q_id in ids]


def question_count() -> int:
    _require_loaded()
    return len(_QUESTIONS)
