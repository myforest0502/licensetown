#!/usr/bin/env python3
"""Deterministic, read-only generation-quality audit for a Question Bank range."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
META_WRONG_PHRASES = (
    "条件を無視", "単一所見から診断", "関連しない機能", "逆方向の判断",
)
PLACEHOLDER_TOKENS = ("TODO", "TBD", "PLACEHOLDER", "ここに", "ダミー")
INTERNAL_METADATA_PATTERNS = (
    r"\bQ\d+\b",
    r"\bNode\b",
    r"\bfrozen\b",
    r"\bamendment(?:s)?\b",
    r"\bkey distribution\b",
    r"these amendments",
    r"these replacements",
    r"all other b12d frozen items",
    r"implementation(?: note| review)?",
    r"現行Node",
    r"正式ラベル",
)
GENERIC_RATIONALE_PATTERNS = (
    r"誤り。?「?.+?」?ではなく、?この設問の条件では「?.+?」?を選ぶ",
    r"この設問の条件では「?.+?」?が該当する",
)
STEM_TEMPLATE_PATTERNS = (
    r"について、次の判断を行う。最も適切なのはどれか",
    r"次のうち最も適切なのはどれか",
)
# SOURCE_ALT_DEMAND is intentionally not inferred by this text linter: source-Q
# pairing is not stored in learner-facing records, and guessing it from wording
# would duplicate the formal classifier.  Batch tests call
# classify_repair_confirmation() for every reviewed pair instead.
SOURCE_ALT_DEMAND_DEFERRED_TO_FORMAL_PAIR_TESTS = True


def _norm(value: str) -> str:
    return re.sub(r"\s+", "", str(value)).lower()


def _finding(severity: str, rule_id: str, qids: Iterable[str], reason: str) -> dict[str, Any]:
    return {
        "severity": severity,
        "rule_id": rule_id,
        "question_ids": sorted(set(qids), key=lambda value: int(value[1:])),
        "reason": reason,
    }


def audit_content_records(
    questions: list[dict[str, Any]],
    answers: list[dict[str, Any]],
    explanations: list[dict[str, Any]],
    tags: list[dict[str, Any]],
) -> dict[str, Any]:
    """Audit supplied records without mutation or medical/classifier inference."""
    findings: list[dict[str, Any]] = []
    answer_by_id = {item["id"]: item for item in answers}
    explanation_by_id = {item["id"]: item for item in explanations}
    tag_by_id = {item["id"]: item for item in tags}
    qids = [item["id"] for item in questions]
    node_by_q = {qid: str(tag_by_id.get(qid, {}).get("knowledge_node_id", "")) for qid in qids}

    if len(questions) >= 10:
        keys = Counter(str(answer_by_id.get(qid, {}).get("display_answer", "")) for qid in qids)
        key, count = keys.most_common(1)[0]
        ratio = count / len(questions)
        if ratio == 1:
            findings.append(_finding("FAIL", "KEY_CONCENTRATION", qids, f"全{len(qids)}問の正答位置が{key}に集中"))
        elif ratio >= 0.8:
            findings.append(_finding("WARN", "KEY_CONCENTRATION", [qid for qid in qids if answer_by_id[qid]["display_answer"] == key], f"正答位置{key}が{ratio:.0%}"))

    stems: dict[str, list[str]] = defaultdict(list)
    choice_sets: dict[tuple[str, ...], list[str]] = defaultdict(list)
    distractors: dict[str, list[str]] = defaultdict(list)
    explanations_by_text: dict[str, list[str]] = defaultdict(list)
    for question in questions:
        qid = question["id"]
        stem = str(question.get("question_text", "")).strip()
        choices = question.get("choices") or {}
        stems[_norm(stem)].append(qid)
        choice_sets[tuple(sorted(_norm(value) for value in choices.values()))].append(qid)
        key = str(answer_by_id.get(qid, {}).get("display_answer", ""))
        for letter, value in choices.items():
            if letter != key and len(_norm(value)) >= 8:
                distractors[_norm(value)].append(qid)
        explanation = str(explanation_by_id.get(qid, {}).get("explanation", ""))
        explanations_by_text[_norm(explanation)].append(qid)

        learner_fields = [stem, explanation]
        choice_explanations = explanation_by_id.get(qid, {}).get("choice_explanations") or {}
        learner_fields.extend(str(value) for value in choice_explanations.values())
        learner_text = "\n".join(learner_fields)
        matched_internal = [pattern for pattern in INTERNAL_METADATA_PATTERNS if re.search(pattern, learner_text, re.I)]
        if matched_internal:
            findings.append(_finding("FAIL", "LEARNER_TEXT_INTERNAL_METADATA", [qid], "学習者向け本文に内部管理情報を検出"))

        generic = [
            letter for letter, value in choice_explanations.items()
            if letter != key and any(re.search(pattern, str(value), re.I) for pattern in GENERIC_RATIONALE_PATTERNS)
        ]
        if len(generic) >= 3:
            findings.append(_finding("FAIL", "GENERIC_CHOICE_RATIONALE", [qid], "3選択肢以上で差替え型の汎用誤答理由を検出"))
        elif generic:
            findings.append(_finding("WARN", "GENERIC_CHOICE_RATIONALE", [qid], "差替え型の汎用誤答理由を検出"))


        malformed = not stem or set(choices) != set("ABCDE") or any(not str(value).strip() for value in choices.values())
        malformed = malformed or any(token.lower() in (stem + json.dumps(choices, ensure_ascii=False)).lower() for token in PLACEHOLDER_TOKENS)
        if malformed:
            findings.append(_finding("FAIL", "MALFORMED_TEXT", [qid], "空欄、選択肢不備、またはplaceholderを検出"))

        prerequisites = tag_by_id.get(qid, {}).get("prerequisite_nodes") or []
        leaked = [value for value in prerequisites if len(str(value)) > 30 or re.search(r"[。！？]", str(value))]
        if leaked:
            findings.append(_finding("WARN", "PREREQUISITE_SENTENCE_LEAK", [qid], "前提知識に長文または説明文形式を検出"))

    for values, rule, reason in (
        (stems, "EXACT_DUPLICATE_STEM", "同一問題文を複数Qで検出"),
        (choice_sets, "CHOICE_SET_DUPLICATE", "同一選択肢セットを複数Qで検出"),
    ):
        for related in values.values():
            if len(related) > 1:
                findings.append(_finding("FAIL", rule, related, reason))
    for pattern in STEM_TEMPLATE_PATTERNS:
        related = [q["id"] for q in questions if re.search(pattern, str(q.get("question_text", "")), re.I)]
        if len(related) >= 3:
            findings.append(_finding("WARN", "REPEATED_STEM_TEMPLATE", related, "汎用問題文テンプレートを3問以上で検出"))

    for normalized, related in distractors.items():
        nodes = {node_by_q[qid] for qid in related}
        if len(nodes) >= 3:
            severity = "FAIL" if any(_norm(phrase) in normalized for phrase in META_WRONG_PHRASES) else "WARN"
            findings.append(_finding(severity, "REPEATED_DISTRACTOR", related, f"同一distractorを{len(nodes)} Nodeで再利用"))
    for phrase in META_WRONG_PHRASES:
        related = [q["id"] for q in questions if _norm(phrase) in _norm(json.dumps(q.get("choices", {}), ensure_ascii=False))]
        if len(related) >= 3:
            findings.append(_finding("FAIL", "META_WRONG_DISTRACTOR", related, f"meta-wrong phrase反復: {phrase}"))
    for related in explanations_by_text.values():
        nodes = {node_by_q[qid] for qid in related}
        if len(nodes) >= 3:
            findings.append(_finding("WARN" if len(nodes) < 5 else "FAIL", "REPEATED_EXPLANATION", related, "同一解説を複数Nodeで再利用"))

    severity_order = {"FAIL": 0, "WARN": 1}
    findings.sort(key=lambda item: (severity_order[item["severity"]], item["rule_id"], item["question_ids"]))
    return {
        "question_count": len(qids),
        "fail_count": sum(item["severity"] == "FAIL" for item in findings),
        "warn_count": sum(item["severity"] == "WARN" for item in findings),
        "findings": findings,
    }


def audit_question_range(start: int, end: int, bank: Path = BANK) -> dict[str, Any]:
    if start < 1 or end < start:
        raise ValueError("invalid Q range")
    def load(name: str) -> list[dict[str, Any]]:
        return json.loads((bank / name).read_text(encoding="utf-8-sig"))
    qids = {f"Q{number}" for number in range(start, end + 1)}
    selected = []
    datasets = []
    for name in ("questions.json", "answers.json", "explanations.json", "question_tags.json"):
        records = [item for item in load(name) if item.get("id") in qids]
        if {item.get("id") for item in records} != qids:
            raise ValueError(f"{name}: requested range is not contiguous/present")
        datasets.append(records)
    selected, answers, explanations, tags = datasets
    report = audit_content_records(selected, answers, explanations, tags)
    report.update({"start": start, "end": end})
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    report = audit_question_range(args.start, args.end)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_output:
        args.json_output.write_text(rendered + "\n", encoding="utf-8")
    return 1 if report["fail_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
