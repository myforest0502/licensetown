"""LicenseTown formal-bank term explainer without external AI calls.

The learner-facing answer is built from a small vetted local glossary plus the
saved formal question bank. It intentionally does not invent a definition when
neither source has enough support.
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

# Frequently used exam terms get a short, learner-facing definition first.
# This stays local, deterministic and free of external AI calls. The related
# points/questions shown afterwards are still taken from the formal bank.
_LOCAL_GLOSSARY = {
    "fim": {
        "title": "FIM",
        "definition": "FIM（Functional Independence Measure：機能的自立度評価法）は、日常生活動作の自立度・介助量を評価する尺度で、運動13項目と認知5項目の計18項目で構成されます。",
        "points": (
            "認知5項目は、理解・表出・社会的交流・問題解決・記憶です。",
            "国試では『何を評価するか』『運動13＋認知5』をまず押さえると整理しやすいです。",
        ),
    },
    "mmt": {
        "title": "MMT",
        "definition": "MMT（Manual Muscle Testing：徒手筋力検査）は、筋力を徒手的に0〜5の6段階で評価する検査です。",
        "points": (
            "0＝筋収縮なし、1＝筋収縮はあるが関節運動なし、2＝重力の影響を除けば全可動域を動かせます。",
            "3＝重力に抗して全可動域、4＝抵抗に抗して運動可能、5＝正常筋力です。",
        ),
    },
    "brunnstrom": {
        "title": "Brunnstrom stage",
        "definition": "Brunnstrom stage（ブルンストローム・ステージ）は、脳卒中などの片麻痺における運動麻痺の回復段階をⅠ〜Ⅵの6段階で示す評価です。",
        "points": (
            "Ⅰは弛緩、Ⅱ〜Ⅲで共同運動や痙縮が目立ち、Ⅳ以降は共同運動から分離した運動が増えていきます。",
            "国試では、各Stageで『共同運動からどれだけ分離できているか』を整理すると覚えやすいです。",
        ),
    },
    "brunnstrom stage": {
        "title": "Brunnstrom stage",
        "definition": "Brunnstrom stage（ブルンストローム・ステージ）は、脳卒中などの片麻痺における運動麻痺の回復段階をⅠ〜Ⅵの6段階で示す評価です。",
        "points": (
            "Ⅰは弛緩、Ⅱ〜Ⅲで共同運動や痙縮が目立ち、Ⅳ以降は共同運動から分離した運動が増えていきます。",
            "国試では、各Stageで『共同運動からどれだけ分離できているか』を整理すると覚えやすいです。",
        ),
    },
    "ブルンストローム": {
        "title": "Brunnstrom stage",
        "definition": "Brunnstrom stage（ブルンストローム・ステージ）は、脳卒中などの片麻痺における運動麻痺の回復段階をⅠ〜Ⅵの6段階で示す評価です。",
        "points": (
            "Ⅰは弛緩、Ⅱ〜Ⅲで共同運動や痙縮が目立ち、Ⅳ以降は共同運動から分離した運動が増えていきます。",
            "国試では、各Stageで『共同運動からどれだけ分離できているか』を整理すると覚えやすいです。",
        ),
    },
}


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
    ranked.sort(
        key=lambda item: (
            -item.score,
            int(item.question_id[1:]) if item.question_id[1:].isdigit() else 10**9,
        )
    )
    return ranked[: max(1, int(limit))]


def _definition_sentence_score(sentence: str, normalized_term: str) -> int:
    normalized = _normalize(sentence)
    if normalized_term not in normalized:
        return -1
    score = 0
    if normalized.startswith(normalized_term + "は"):
        score += 30
    if normalized.startswith(normalized_term + "とは"):
        score += 32
    if f"{normalized_term}（" in normalized:
        score += 18
    for marker in ("評価する", "検査", "尺度", "指標", "方法", "分類", "段階", "構成", "測定"):
        if marker in sentence:
            score += 5
    # Case-description sentences are poor answers to "what is X?".
    for marker in ("歳", "患者", "症例", "歩行", "立脚", "rom", "mmt3", "mmt4", "mmt5"):
        if marker in normalized:
            score -= 8
    return score


def _find_definition_sentence(term: str) -> str | None:
    normalized_term = _normalize(term)
    best: tuple[int, str] | None = None
    for record in _bank_records():
        for source in (record.get("explanation", ""), *record.get("choice_explanations", ())):
            for sentence in _sentences(source):
                score = _definition_sentence_score(sentence, normalized_term)
                if score < 12:
                    continue
                clipped = _clip(sentence, limit=220)
                if best is None or score > best[0]:
                    best = (score, clipped)
    return best[1] if best else None


def _local_glossary_entry(term: str) -> dict | None:
    normalized = _normalize(term)
    if normalized in _LOCAL_GLOSSARY:
        return _LOCAL_GLOSSARY[normalized]
    if "brunnstrom" in normalized:
        return _LOCAL_GLOSSARY["brunnstrom"]
    if "ブルンストローム" in normalized:
        return _LOCAL_GLOSSARY["ブルンストローム"]
    return None


def _useful_bank_points(results: list[TermSearchResult], definition: str | None) -> list[str]:
    points: list[str] = []
    normalized_definition = _normalize(definition or "")
    for result in results:
        for snippet in result.snippets:
            normalized = _normalize(snippet)
            if normalized_definition and normalized == normalized_definition:
                continue
            # Avoid presenting individual case facts as a general definition/point.
            if any(marker in normalized for marker in ("歳", "患者", "症例", "立脚", "歩幅", "インプラント")):
                continue
            if snippet not in points:
                points.append(snippet)
            if len(points) >= 2:
                return points
    return points


def explain_term(term: object) -> str:
    """Return a LINE-friendly, definition-first explanation without OpenAI API."""
    cleaned = clean_term_query(term)
    if len(_normalize(cleaned)) < 2:
        return (
            "おう、調べたい言葉をもう少し具体的に入れてくれ＾＾\n"
            "たとえば『FIM』『MMT』『Brunnstrom stage』みたいな感じだ。"
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

    glossary = _local_glossary_entry(cleaned)
    definition = glossary["definition"] if glossary else _find_definition_sentence(cleaned)
    title = glossary["title"] if glossary else cleaned

    lines = [f"おう、『{title}』な。", "", "■一言でいうと"]
    if definition:
        lines.append(definition)
    else:
        lines.append(
            "この用語が出てくる問題は見つかったが、保存済み解説の中に『これは何か』を断定できる定義文までは見つからなかった。"
        )

    if glossary and glossary.get("points"):
        lines.extend(["", "■国試で押さえるポイント"])
        lines.extend(f"・{point}" for point in glossary["points"])
    else:
        bank_points = _useful_bank_points(results, definition)
        if bank_points:
            lines.extend(["", "■国試で押さえるポイント"])
            lines.extend(f"・{point}" for point in bank_points)

    lines.extend(["", "■関連問題"])
    lines.extend(
        f"{result.question_id}（{result.category_name}）"
        for result in results
    )
    lines.extend([
        "",
        "※定義はLicenseTown内の用語辞書または正式解説、関連ポイント・問題は正式Question Bankをもとに表示しています。",
    ])
    return "\n".join(lines)
