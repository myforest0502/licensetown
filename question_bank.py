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
CATEGORY_NAMES = {
    1: "解剖学", 2: "生理学", 3: "心理学", 4: "人間発達学", 5: "教育学", 6: "医学概論",
    7: "病理学", 8: "内科学", 9: "神経医学", 10: "精神医学", 11: "小児学", 12: "臨床心理学",
    13: "基礎運動学", 14: "臨床運動学", 15: "動作分析学", 16: "運動器",
    17: "理学療法評価各論", 18: "理学療法治療各論",
}
CATEGORY_LARGE_BY_SMALL = {
    **{number: "A" for number in range(1, 7)},
    **{number: "B" for number in range(7, 13)},
    **{number: "C" for number in range(13, 19)},
}
CATEGORY_GROUP_CODES = {
    "基礎": "A",
    "専門基礎": "B",
    "専門": "C",
}
CATEGORY_GROUPS = {
    group_name: tuple(
        number for number, category_code in CATEGORY_LARGE_BY_SMALL.items()
        if category_code == group_code
    )
    for group_name, group_code in CATEGORY_GROUP_CODES.items()
}
BASIC_CATEGORY_SMALLS = frozenset(
    number for number, category_large in CATEGORY_LARGE_BY_SMALL.items()
    if category_large == "A"
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


def get_category_small(q_id) -> int:
    """正式問題バンクのQ番号から小カテゴリ番号を取得する。"""
    value = get_question(q_id).get("category_small")
    try:
        category_small = int(value)
    except (TypeError, ValueError) as exc:
        raise QuestionBankError(f"Invalid category_small for {q_id}: {value!r}") from exc
    if category_small not in CATEGORY_NAMES:
        raise QuestionBankError(f"Unknown category_small for {q_id}: {category_small}")
    return category_small


def get_category_name(category_small) -> str:
    """小カテゴリ番号を正式な18分野名に変換する。"""
    try:
        return CATEGORY_NAMES[int(category_small)]
    except (KeyError, TypeError, ValueError) as exc:
        raise QuestionBankError(f"Unknown category_small: {category_small!r}") from exc


def get_category_group_names() -> tuple[str, ...]:
    """学習画面で表示する正式な大分類名を順番どおり返す。"""
    return tuple(CATEGORY_GROUPS)


def get_category_names_for_group(group_name: str) -> tuple[str, ...]:
    """大分類に属する正式な6分野名を返す。"""
    try:
        category_numbers = CATEGORY_GROUPS[str(group_name).strip()]
    except KeyError as exc:
        raise QuestionBankError(f"Unknown category group: {group_name!r}") from exc
    return tuple(CATEGORY_NAMES[number] for number in category_numbers)


def resolve_category_small(category_name: str, group_name: str | None = None) -> int:
    """正式分野名を小カテゴリ番号へ変換し、必要なら大分類との整合も確認する。"""
    normalized_name = str(category_name).strip()
    category_small = next(
        (number for number, name in CATEGORY_NAMES.items() if name == normalized_name),
        None,
    )
    if category_small is None:
        raise QuestionBankError(f"Unknown category name: {category_name!r}")
    if group_name is not None and category_small not in CATEGORY_GROUPS.get(str(group_name).strip(), ()):
        raise QuestionBankError(
            f"Category {category_name!r} does not belong to group {group_name!r}"
        )
    return category_small


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


def selected_answers_for_history(question: dict, selected_answer) -> list[str]:
    """画面用A～E回答を正式JSON本来の選択肢キーへ戻す。"""
    choice_key_map = question.get("choice_key_map", {})
    selected = sorted(_answer_tokens(selected_answer))
    return [str(choice_key_map.get(label, label)) for label in selected]


def get_quiz_question(q_id) -> dict:
    question = get_question(q_id)
    answer = get_answer(q_id)
    explanation = get_explanation(q_id)
    choices = {
        _choice_label(key): str(value).strip()
        for key, value in question["choices"].items()
    }
    choice_key_map = {
        _choice_label(key): str(key)
        for key in question["choices"]
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
        "choice_key_map": choice_key_map,
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


def select_questions_by_category(category_small: int, question_count: int) -> list[dict]:
    """正式JSONから指定分野だけを抽出する。少数分野は一巡後に再抽出する。"""
    _require_loaded()
    try:
        category_number = int(category_small)
    except (TypeError, ValueError) as exc:
        raise QuestionBankError(f"Unknown category_small: {category_small!r}") from exc
    if category_number not in CATEGORY_NAMES:
        raise QuestionBankError(f"Unknown category_small: {category_small!r}")
    if question_count < 1:
        raise QuestionBankError("Requested question count must be positive")

    matching_ids = [
        q_id for q_id, question in _QUESTIONS.items()
        if int(question.get("category_small", 0)) == category_number
    ]
    if not matching_ids:
        raise QuestionBankError(f"No questions found for category_small={category_number}")

    selected_ids = []
    while len(selected_ids) < question_count:
        shuffled_ids = random.sample(matching_ids, len(matching_ids))
        selected_ids.extend(shuffled_ids[: question_count - len(selected_ids)])
    return [get_quiz_question(q_id) for q_id in selected_ids]


def question_count() -> int:
    _require_loaded()
    return len(_QUESTIONS)
