"""LicenseTown formal-bank term explainer without external AI calls.

Definitions prefer a small reviewed glossary whose evidence points back to the
formal question bank. Other terms fall back to definition-like sentences found
in the saved formal question/explanation data. No definition is invented.
"""

from __future__ import annotations

import json
import re
import threading
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from question_bank import (
    QuestionBankError,
    get_category_name,
    get_question_tag,
    get_quiz_question,
    question_ids,
)

_QUERY_PREFIXES = ("教えて源さん", "源さん")
_QUERY_SUFFIXES = (
    "とは何ですか", "とはなんですか", "とは何", "とはなに",
    "って何ですか", "ってなんですか", "って何", "ってなに",
    "について教えて", "を教えて", "教えて", "とは",
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？!?])\s*|[\r\n]+")
_GLOSSARY_PATH = Path(__file__).resolve().parent / "data" / "term_glossary_v01.json"
_CACHE_LOCK = threading.Lock()
_INDEX_CACHE: tuple[dict, ...] | None = None
_GLOSSARY_CACHE: dict | None = None


@dataclass(frozen=True)
class TermSearchResult:
    question_id: str
    score: int
    category_name: str
    snippets: tuple[str, ...]


def _normalize(text: object) -> str:
    return unicodedata.normalize("NFKC", str(text or "")).strip().lower()


def clean_term_query(text: object) -> str:
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
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(str(text or "")) if s and s.strip()]


def _clip(text: str, limit: int = 180) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def _record_from_bank(question_id: str) -> dict:
    question = get_quiz_question(question_id)
    tag = get_question_tag(question_id)
    try:
        category_name = get_category_name(question.get("category_small"))
    except QuestionBankError:
        category_name = "関連分野"
    return {
        "question_id": str(question_id),
        "question_text": str(question.get("question", "")),
        "choices": tuple(str(v) for v in question.get("choices", {}).values()),
        "explanation": str(question.get("explanation", "")),
        "choice_explanations": tuple(str(v) for v in question.get("choice_explanations", {}).values()),
        "knowledge_node": str(tag.get("knowledge_node") or tag.get("knowledge_node_label") or tag.get("knowledge_node_id") or ""),
        "category_name": category_name,
    }


def _bank_records() -> tuple[dict, ...]:
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        with _CACHE_LOCK:
            if _INDEX_CACHE is None:
                _INDEX_CACHE = tuple(_record_from_bank(q_id) for q_id in question_ids())
    return _INDEX_CACHE


def _glossary() -> dict:
    global _GLOSSARY_CACHE
    if _GLOSSARY_CACHE is None:
        with _CACHE_LOCK:
            if _GLOSSARY_CACHE is None:
                payload = json.loads(_GLOSSARY_PATH.read_text(encoding="utf-8"))
                _GLOSSARY_CACHE = payload.get("terms", {})
    return _GLOSSARY_CACHE


def _glossary_entry(term: str) -> tuple[str, dict] | None:
    target = _normalize(term)
    for canonical, entry in _glossary().items():
        names = [canonical, *entry.get("aliases", [])]
        if any(_normalize(name) == target for name in names):
            return canonical, entry
    return None


def _matching_snippets(record: dict, normalized_term: str) -> tuple[str, ...]:
    candidates: list[str] = []
    for source in (record.get("explanation", ""), *record.get("choice_explanations", ())):
        for sentence in _sentences(source):
            if normalized_term in _normalize(sentence):
                clipped = _clip(sentence)
                if clipped and clipped not in candidates:
                    candidates.append(clipped)
            if len(candidates) >= 3:
                return tuple(candidates)
    return tuple(candidates)


def _score_record(record: dict, normalized_term: str) -> int:
    if not normalized_term:
        return 0
    node = _normalize(record.get("knowledge_node", ""))
    explanation = _normalize(record.get("explanation", ""))
    choice_explanations = " ".join(_normalize(v) for v in record.get("choice_explanations", ()))
    question = _normalize(record.get("question_text", ""))
    choices = " ".join(_normalize(v) for v in record.get("choices", ()))
    score = 0
    if node == normalized_term:
        score += 24
    elif normalized_term in node:
        score += 12
    if normalized_term in explanation: score += 10
    if normalized_term in choice_explanations: score += 8
    if normalized_term in question: score += 6
    if normalized_term in choices: score += 4
    return score


def _definition_score(sentence: str, normalized_term: str) -> int:
    normalized = _normalize(sentence)
    if normalized_term not in normalized:
        return -100
    score = 4 if normalized.find(normalized_term) <= 6 else 0
    if any(m in normalized for m in ("とは", "である", "をいう", "を指す", "のことで", "評価する", "測定する", "尺度", "検査", "指標", "方法", "分類", "構成され", "段階", "手法")):
        score += 8
    if re.search(r"(?:は|とは).{0,60}(?:である|をいう|を指す|のこと|尺度|検査|指標|方法|分類|評価)", normalized):
        score += 10
    if any(m in normalized for m in ("患者", "症例", "rom", "筋力は", "徴候", "歩幅", "立ち上がり", "困難である", "インプラント", "立脚", "遊脚", "上肢支持")):
        score -= 8
    return score


def _pick_definition_and_points(term: str, results: list[TermSearchResult]) -> tuple[str | None, list[str]]:
    normalized_term = _normalize(term)
    candidates: list[str] = []
    for result in results:
        for snippet in result.snippets:
            if snippet not in candidates:
                candidates.append(snippet)
    definition = None
    if candidates:
        ranked = sorted(candidates, key=lambda v: (-_definition_score(v, normalized_term), candidates.index(v)))
        if _definition_score(ranked[0], normalized_term) >= 8:
            definition = ranked[0]
    points = [v for v in candidates if v != definition]
    points.sort(key=lambda v: (-_definition_score(v, normalized_term), candidates.index(v)))
    return definition, points[:3]


def search_term_records(term: str, records: Iterable[dict] | None = None, *, limit: int = 3) -> list[TermSearchResult]:
    cleaned = clean_term_query(term)
    normalized = _normalize(cleaned)
    if len(normalized) < 2:
        return []
    ranked: list[TermSearchResult] = []
    for record in records if records is not None else _bank_records():
        score = _score_record(record, normalized)
        if score <= 0:
            continue
        ranked.append(TermSearchResult(
            question_id=str(record.get("question_id", "")), score=score,
            category_name=str(record.get("category_name", "関連分野")),
            snippets=_matching_snippets(record, normalized),
        ))
    ranked.sort(key=lambda item: (-item.score, int(item.question_id[1:]) if item.question_id[1:].isdigit() else 10**9))
    return ranked[: max(1, int(limit))]


def explain_term(term: object) -> str:
    cleaned = clean_term_query(term)
    if len(_normalize(cleaned)) < 2:
        return "おう、調べたい言葉をもう少し具体的に入れてくれ＾＾\nたとえば『FIM』『MMT』『Brunnstrom stage』みたいな感じだ。"
    try:
        evidence_results = search_term_records(cleaned, limit=20)
    except QuestionBankError:
        return "おう、悪い。今は正式問題バンクを確認できない状態だ。\n推測では答えず、問題バンクが戻ってからもう一度確認しよう。"
    if not evidence_results:
        return f"おう、『{cleaned}』だな。\n今あるLicenseTownの正式問題・解説だけでは、意味を断定できるだけの記述を見つけられなかった。\n略語なら正式名称、長い質問なら調べたい用語だけにして、もう一度入れてみてくれ＾＾"

    glossary_match = _glossary_entry(cleaned)
    extracted_definition, points = _pick_definition_and_points(cleaned, evidence_results)
    display_term = glossary_match[0] if glossary_match else cleaned
    definition = glossary_match[1].get("definition") if glossary_match else extracted_definition
    related_results = evidence_results[:3]

    lines = [f"おう、『{display_term}』な。", "", f"■{display_term}とは？"]
    if definition:
        lines.append(definition)
    else:
        lines.extend([
            "この言葉が出てくる問題は見つかったが、保存済み解説の中に『何か』を直接説明する定義文は見つからなかった。",
            "ここは推測で意味を作らず、問題・解説から確認できる内容だけを示すぞ。",
        ])
    if points:
        lines.extend(["", "■国試で押さえるポイント"])
        lines.extend(f"・{point}" for point in points)
    lines.extend(["", "■関連問題"])
    lines.extend(f"{r.question_id}（{r.category_name}）" for r in related_results)
    lines.extend(["", "※この回答はLicenseTownに保存してある正式問題・解説と、そこに根拠をひも付けた確認済み用語定義をもとにしている。"])
    return "\n".join(lines)
