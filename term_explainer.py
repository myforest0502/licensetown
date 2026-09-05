"""LicenseTown formal-bank term explainer without external AI calls.

The learner-facing answer is built only from the saved formal question bank.
It intentionally does not invent a definition when the bank has no supporting text.
"""

from __future__ import annotations

import re
import threading
import unicodedata
from dataclasses import dataclass
from typing import Iterable

from question_bank import (
    QuestionBankError,
    get_category_name,
    get_question_tag,
    get_quiz_question,
    question_ids,
)


_QUERY_PREFIXES = (
    "教えて源さん",
    "源さん",
)
_QUERY_SUFFIXES = (
    "とは何ですか",
    "とはなんですか",
    "とは何",
    "とはなに",
    "って何ですか",
    "ってなんですか",
    "って何",
    "ってなに",
    "について教えて",
    "を教えて",
    "教えて",
    "とは",
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？!?])\s*|[\r\n]+")
_CACHE_LOCK = threading.Lock()
_INDEX_CACHE: tuple[dict, ...] | None = None


@dataclass(frozen=True)
class TermSearchResult:
    question_id: str
    score: int
    category_name: str
    snippets: tuple[str, ...]


def _normalize(text: object) -> str:
    return unicodedata.normalize("NFKC", str(text or "")).strip().lower()


def clean_term_query(text: object) -> str:
    """Remove conversational wrappers while preserving the learner's term text."""
    value = unicodedata.normalize("NFKC", str(text or "")).strip()
    value = re.sub(r"^[\s、。,.!?！？]+|[\s、。,.!?！？]+$", "", value)
    for prefix in _QUERY_PREFIXES:
        if value.startswith(prefix):
            value = value[len(prefix):].lstrip(" 、。,:：")
            break
    for suffix in _QUERY_SUFFIXES:
        if value.endswith(suffix):
            value = value[: -len(suffix)].rstrip(" 、。,:：")
            break
    return value.strip()


def _sentences(text: object) -> list[str]:
    return [
        sentence.strip()
        for sentence in _SENTENCE_SPLIT_RE.split(str(text or ""))
        if sentence and sentence.strip()
    ]


def _clip(text: str, limit: int = 180) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _record_from_bank(question_id: str) -> dict:
    question = get_quiz_question(question_id)
    tag = get_question_tag(question_id)
    category_small = question.get("category_small")
    try:
        category_name = get_category_name(category_small)
    except QuestionBankError:
        category_name = "関連分野"
    return {
        "question_id": str(question_id),
        "question_text": str(question.get("question", "")),
        "choices": tuple(str(value) for value in question.get("choices", {}).values()),
        "explanation": str(question.get("explanation", "")),
        "choice_explanations": tuple(
            str(value) for value in question.get("choice_explanations", {}).values()
        ),
        "knowledge_node": str(
            tag.get("knowledge_node")
            or tag.get("knowledge_node_label")
            or tag.get("knowledge_node_id")
            or ""
        ),
        "category_name": category_name,
    }


def _bank_records() -> tuple[dict, ...]:
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        with _CACHE_LOCK:
            if _INDEX_CACHE is None:
                _INDEX_CACHE = tuple(_record_from_bank(q_id) for q_id in question_ids())
    return _INDEX_CACHE


def _matching_snippets(record: dict, normalized_term: str) -> tuple[str, ...]:
    candidates: list[str] = []
    for source in (record.get("explanation", ""), *record.get("choice_explanations", ())):
        for sentence in _sentences(source):
            if normalized_term in _normalize(sentence):
                clipped = _clip(sentence)
                if clipped and clipped not in candidates:
                    candidates.append(clipped)
            if len(candidates) >= 2:
                return tuple(candidates)
    return tuple(candidates)


def _score_record(record: dict, normalized_term: str) -> int:
    if not normalized_term:
        return 0
    node = _normalize(record.get("knowledge_node", ""))
    explanation = _normalize(record.get("explanation", ""))
    choice_explanations = " ".join(
        _normalize(value) for value in record.get("choice_explanations", ())
    )
    question = _normalize(record.get("question_text", ""))
    choices = " ".join(_normalize(value) for value in record.get("choices", ()))

    score = 0
    if node == normalized_term:
        score += 24
    elif normalized_term in node:
        score += 12
    if normalized_term in explanation:
        score += 10
    if normalized_term in choice_explanations:
        score += 8
    if normalized_term in question:
        score += 6
    if normalized_term in choices:
        score += 4
    return score


def search_term_records(
    term: str,
    records: Iterable[dict] | None = None,
    *,
    limit: int = 3,
) -> list[TermSearchResult]:
    """Rank exact textual evidence from formal saved data only."""
    cleaned = clean_term_query(term)
    normalized = _normalize(cleaned)
    if len(normalized) < 2:
        return []

    ranked: list[TermSearchResult] = []
    for record in records if records is not None else _bank_records():
        score = _score_record(record, normalized)
        if score <= 0:
            continue
        ranked.append(
            TermSearchResult(
                question_id=str(record.get("question_id", "")),
                score=score,
                category_name=str(record.get("category_name", "関連分野")),
                snippets=_matching_snippets(record, normalized),
            )
        )
    ranked.sort(key=lambda item: (-item.score, int(item.question_id[1:]) if item.question_id[1:].isdigit() else 10**9))
    return ranked[: max(1, int(limit))]


def explain_term(term: object) -> str:
    """Return a LINE-friendly evidence-grounded explanation without OpenAI API."""
    cleaned = clean_term_query(term)
    if len(_normalize(cleaned)) < 2:
        return (
            "おう、調べたい言葉をもう少し具体的に入れてくれ＾＾\n"
            "たとえば『FIM』『相反性抑制』『Brunnstrom stage』みたいな感じだ。"
        )

    try:
        results = search_term_records(cleaned)
    except QuestionBankError:
        return (
            "おう、悪い。今は正式問題バンクを確認できない状態だ。\n"
            "推測では答えず、問題バンクが戻ってからもう一度確認しよう。"
        )

    if not results:
        return (
            f"おう、『{cleaned}』だな。\n"
            "今あるLicenseTownの正式問題・解説だけでは、意味を断定できるだけの記述を見つけられなかった。\n"
            "略語なら正式名称、長い質問なら調べたい用語だけにして、もう一度入れてみてくれ＾＾"
        )

    snippets: list[str] = []
    for result in results:
        for snippet in result.snippets:
            if snippet not in snippets:
                snippets.append(snippet)
            if len(snippets) >= 3:
                break
        if len(snippets) >= 3:
            break

    lines = [
        f"おう、『{cleaned}』な。",
        "LicenseTownの正式な問題・解説から確認すると、ここを押さえるといいぞ。",
    ]
    if snippets:
        lines.extend(["", "■問題・解説にあるポイント"])
        lines.extend(f"・{snippet}" for snippet in snippets)
    else:
        lines.extend([
            "",
            "この言葉が出てくる問題は見つかったが、保存済み解説の中に直接説明している文は見つからなかった。",
            "意味を推測で作らず、まず関連問題を示しておくぞ。",
        ])

    lines.extend(["", "■関連問題"])
    lines.extend(
        f"{result.question_id}（{result.category_name}）"
        for result in results
    )
    lines.extend([
        "",
        "※この回答はLicenseTownに保存してある正式問題・解説をもとにしている。",
    ])
    return "\n".join(lines)
