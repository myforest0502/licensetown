"""Build the read-only ⑩-G remaining-Node repairability priority audit."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repairability import build_repairability_audit
from question_bank import CATEGORY_NAMES, get_question, get_question_tag


BANK = ROOT / "data" / "question_bank"
OUTPUT_DIR = ROOT / "audits" / "10g_remaining_repairability"
S_RANK_TARGET = 75
S_CATEGORY_QUOTAS = {
    1: 4, 2: 4, 3: 2, 4: 2, 5: 1, 6: 3,
    7: 3, 8: 6, 9: 6, 10: 2, 11: 4, 12: 2,
    13: 4, 14: 1, 15: 6, 16: 7, 17: 8, 18: 10,
}

FIELD_LARGE = {**{n: "A" for n in range(1, 7)}, **{n: "B" for n in range(7, 13)}, **{n: "C" for n in range(13, 19)}}
TASK_REASONING = {
    "fact_recall": 2, "finding_interpretation": 4, "assessment_selection": 4,
    "intervention_selection": 5, "device_selection": 5,
    "functional_goal_decision": 5, "prognosis_prediction": 5,
    "safety_priority": 5,
}
TASK_FEASIBILITY = {
    "fact_recall": 4, "finding_interpretation": 5, "assessment_selection": 5,
    "intervention_selection": 5, "device_selection": 5,
    "functional_goal_decision": 4, "prognosis_prediction": 4,
    "safety_priority": 5,
}
TASK_PATTERN = {
    "fact_recall": "TYPE_A Definition → Case",
    "finding_interpretation": "TYPE_F Result → Cause",
    "assessment_selection": "TYPE_K Static knowledge → Applied judgment",
    "intervention_selection": "TYPE_J Clinical case → Intervention choice",
    "device_selection": "TYPE_J Clinical case → Intervention choice",
    "functional_goal_decision": "TYPE_K Static knowledge → Applied judgment",
    "prognosis_prediction": "TYPE_E Cause → Result",
    "safety_priority": "TYPE_J Clinical case → Intervention choice",
}
SAFETY_TERMS_5 = ("禁忌", "中止", "急変", "誤嚥", "脱臼", "DVT", "深部静脈血栓", "感染", "自律神経過反射")
SAFETY_TERMS_4 = ("転倒", "血圧", "心疾患", "呼吸", "骨折", "脊髄", "リスク", "装具", "安全")
AUDIT_FIELDS = [
    "canonical_node_id", "label", "category_large", "category_small",
    "category_name", "all_category_smalls", "current_question_ids",
    "strong_available", "exam_importance", "safety_importance",
    "clinical_reasoning", "single_question_risk", "strong_creation_feasibility",
    "memorization_risk", "balance_adjustment", "source_quality_risk",
    "priority_score", "final_rank", "recommended_pattern", "reason", "notes",
]


def _read(name: str) -> Any:
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def _node_registry() -> dict[str, dict[str, Any]]:
    return {item["knowledge_node_id"]: item for item in _read("knowledge_nodes.json")}


def _canonical_members() -> dict[str, list[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for node in _read("knowledge_nodes.json"):
        raw = str(node["knowledge_node_id"])
        result[canonicalize_knowledge_node_id(raw)].add(raw)
    return {key: sorted(values) for key, values in result.items()}


def _primary_category(question_ids: list[str]) -> tuple[int, list[int]]:
    categories = [int(get_question(q_id)["category_small"]) for q_id in question_ids]
    counts = Counter(categories)
    primary = sorted(counts, key=lambda value: (-counts[value], value))[0]
    return primary, sorted(counts)


def _safety_score(safety_values: list[str], text: str) -> int:
    if "critical" in safety_values or any(term in text for term in SAFETY_TERMS_5):
        return 5
    if "moderate" in safety_values or any(term in text for term in SAFETY_TERMS_4):
        return 4
    return 1


def _exam_importance(category_large: str, tasks: list[str], levels: list[int], sources: list[str]) -> int:
    value = 4 if category_large in {"B", "C"} else 3
    if any(task in {"safety_priority", "finding_interpretation", "intervention_selection"} for task in tasks):
        value += 1
    if max(levels or [1]) >= 4 or "past_exam" in sources:
        value += 1
    return min(5, value)


def _source_quality_risk(labels: list[str], questions: list[dict[str, Any]]) -> tuple[int, list[str]]:
    issues = []
    if not labels or not any(label.strip() for label in labels):
        issues.append("missing_node_label")
    if any(len(label) > 180 for label in labels):
        issues.append("overlong_node_label")
    if len(set(labels)) > 2:
        issues.append("multiple_node_descriptions")
    if any(len(str(question.get("question_text") or "").strip()) < 12 for question in questions):
        issues.append("short_question_context")
    if any(any(term in str(question.get("question_text") or "") for term in ("平成", "法律", "制度")) for question in questions):
        issues.append("currentness_review_needed")
    return min(5, 1 + len(issues)), issues


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "|".join(map(str, row[key])) if isinstance(row.get(key), list) else row.get(key, "") for key in fields})


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_audit() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    repairability = build_repairability_audit()
    registry = _node_registry()
    members = _canonical_members()
    all_records = {item["canonical_node_id"]: item for item in repairability}
    strong_nodes = {key for key, item in all_records.items() if item["repairable"]}

    category_totals: Counter[int] = Counter()
    category_strong: Counter[int] = Counter()
    primary_by_node: dict[str, int] = {}
    for item in repairability:
        primary, _ = _primary_category(item["question_ids"])
        primary_by_node[item["canonical_node_id"]] = primary
        category_totals[primary] += 1
        if item["repairable"]:
            category_strong[primary] += 1

    rows: list[dict[str, Any]] = []
    separate_issues: list[dict[str, Any]] = []
    for item in repairability:
        if item["repairable"]:
            continue
        canonical = item["canonical_node_id"]
        q_ids = list(item["question_ids"])
        questions = [get_question(q_id) for q_id in q_ids]
        tags = [get_question_tag(q_id) for q_id in q_ids]
        primary = primary_by_node[canonical]
        all_categories = sorted({int(question["category_small"]) for question in questions})
        category_large = FIELD_LARGE[primary]
        labels = [str(value) for value in item["knowledge_node_labels"] if str(value).strip()]
        label = str(registry.get(canonical, {}).get("label") or (labels[0] if labels else canonical))
        tasks = sorted({str(tag["task"]) for tag in tags})
        levels = [int(tag["level"]) for tag in tags]
        sources = [str(tag["source"]) for tag in tags]
        combined = " ".join([label] + [str(q["question_text"]) for q in questions])
        exam = _exam_importance(category_large, tasks, levels, sources)
        safety = _safety_score(item["safety"], combined)
        clinical = max(TASK_REASONING.get(task, 2) for task in tasks)
        single_risk = 5 if len(q_ids) == 1 else 4
        feasibility = max(TASK_FEASIBILITY.get(task, 3) for task in tasks)
        memorization = 5 if "fact_recall" in tasks or len(q_ids) == 1 else 3
        coverage = category_strong[primary] / category_totals[primary]
        balance = 5 if category_strong[primary] == 0 else 4 if coverage < 0.01 else 3 if coverage < 0.02 else 2
        quality, quality_issues = _source_quality_risk(labels, questions)
        score = exam * 2 + safety * 2 + clinical * 2 + single_risk * 2 + feasibility + memorization + balance + quality
        hold_reasons = []
        if "missing_node_label" in quality_issues:
            hold_reasons.append("Node label missing")
        if len(all_categories) > 2:
            hold_reasons.append("canonical Node spans more than two fields")
        if "overlong_node_label" in quality_issues and "multiple_node_descriptions" in quality_issues:
            hold_reasons.append("Node definition needs human review")
        if hold_reasons:
            separate_issues.append({"canonical_node_id": canonical, "issues": hold_reasons + quality_issues})
        task = max(tasks, key=lambda value: (TASK_REASONING.get(value, 0), value))
        rows.append({
            "canonical_node_id": canonical, "raw_node_ids": members.get(canonical, [canonical]),
            "label": label, "category_large": category_large, "category_small": primary,
            "category_name": CATEGORY_NAMES[primary], "all_category_smalls": all_categories,
            "current_question_ids": q_ids, "strong_available": False,
            "exam_importance": exam, "safety_importance": safety,
            "clinical_reasoning": clinical, "single_question_risk": single_risk,
            "strong_creation_feasibility": feasibility, "memorization_risk": memorization,
            "balance_adjustment": balance, "source_quality_risk": quality,
            "priority_score": score, "final_rank": "HOLD" if hold_reasons else "",
            "recommended_pattern": TASK_PATTERN.get(task, "TYPE_K Static knowledge → Applied judgment"),
            "reason": f"{CATEGORY_NAMES[primary]}の{task}。重要度{exam}、Safety{safety}、臨床推論{clinical}。別経路での確認価値を評価。",
            "notes": "; ".join(hold_reasons + quality_issues),
            "tasks": tasks, "safety_values": item["safety"], "question_count": len(q_ids),
        })

    eligible = sorted((row for row in rows if row["final_rank"] != "HOLD"), key=lambda row: (-row["priority_score"], -row["safety_importance"], -row["clinical_reasoning"], row["canonical_node_id"]))
    if sum(S_CATEGORY_QUOTAS.values()) != S_RANK_TARGET:
        raise RuntimeError("S category quotas must equal the strict S-rank target")
    s_ids = set()
    for category, quota in S_CATEGORY_QUOTAS.items():
        category_rows = [row for row in eligible if int(row["category_small"]) == category]
        s_ids.update(row["canonical_node_id"] for row in category_rows[:quota])
    if len(s_ids) != S_RANK_TARGET:
        raise RuntimeError("Not enough eligible Nodes to satisfy S category quotas")
    for row in eligible:
        if row["canonical_node_id"] in s_ids:
            row["final_rank"] = "S"
        elif row["priority_score"] >= 48:
            row["final_rank"] = "A"
        elif row["priority_score"] >= 41:
            row["final_rank"] = "B"
        else:
            row["final_rank"] = "C"
    rows.sort(key=lambda row: ({"S": 0, "A": 1, "B": 2, "C": 3, "HOLD": 4}[row["final_rank"]], -row["priority_score"], row["canonical_node_id"]))
    meta = {
        "canonical_node_count": len(repairability), "strong_available_node_count": len(strong_nodes),
        "target_node_count": len(rows), "s_rank_target": S_RANK_TARGET,
        "rank_counts": dict(Counter(row["final_rank"] for row in rows)),
        "separate_issue_count": len(separate_issues),
    }
    return rows, separate_issues, meta


def _category_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    repairability = build_repairability_audit()
    total = Counter()
    strong = Counter()
    for item in repairability:
        primary, _ = _primary_category(item["question_ids"])
        total[primary] += 1
        strong[primary] += int(item["repairable"])
    ranks = defaultdict(Counter)
    for row in rows:
        ranks[int(row["category_small"])][row["final_rank"]] += 1
    return [{
        "category_large": FIELD_LARGE[number], "category_small": number,
        "category_name": CATEGORY_NAMES[number], "total_canonical_nodes": total[number],
        "strong_available_nodes": strong[number], "strong_unsupported_nodes": total[number] - strong[number],
        "s_rank_nodes": ranks[number]["S"], "a_rank_nodes": ranks[number]["A"],
    } for number in range(1, 19)]


def _reserve_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # The frozen screening summary names a 19-record ledger, but the ledger itself
    # is not present in the repository or supplied source pack. Preserve the gap
    # explicitly; do not fabricate candidate IDs or call them rejected.
    ranked_nodes = {row["canonical_node_id"]: row["final_rank"] for row in rows}
    return [{
        "reserve_slot": f"B{number:02d}", "candidate_source": "42_51_reserve_candidates_v04.json",
        "candidate_node_id": "", "priority_rank": "", "reusable": "not_assessed",
        "reason": "Reserve ledger record unavailable; screening summary confirms count only.",
        "known_ranked_node_count": len(ranked_nodes),
    } for number in range(1, 20)]


def _report(rows, categories, issues, meta, reserve_rows) -> str:
    s_rows = [row for row in rows if row["final_rank"] == "S"]
    top20 = s_rows[:20]
    lines = [
        "# LicenseTown ⑩-G Remaining Repairability Priority Audit v0.1", "",
        "## 結論", "",
        f"- canonical Node: {meta['canonical_node_count']}",
        f"- formal strong対応済み: {meta['strong_available_node_count']}",
        f"- 評価対象: {meta['target_node_count']}",
        "- Question Bank・Node・DB・Production変更: 0", "",
        "## Rank内訳", "",
        *[f"- {rank}: {meta['rank_counts'].get(rank, 0)}" for rank in ("S", "A", "B", "C", "HOLD")],
        "", "## カテゴリ別", "",
        "|分野|total|strong|unsupported|S|A|", "|---|---:|---:|---:|---:|---:|",
        *[f"|{item['category_small']} {item['category_name']}|{item['total_canonical_nodes']}|{item['strong_available_nodes']}|{item['strong_unsupported_nodes']}|{item['s_rank_nodes']}|{item['a_rank_nodes']}|" for item in categories],
        "", "## 上位20 Node", "",
    ]
    for index, row in enumerate(top20, 1):
        lines.extend([
            f"### {index}. {row['canonical_node_id']} — {row['label']}", "",
            f"- 現Q: {', '.join(row['current_question_ids'])}",
            f"- 分野: {row['category_small']} {row['category_name']}",
            f"- 優先理由: {row['reason']}",
            f"- 1問では弱い理由: {'単一問題のみで答え暗記と理解を分離できない。' if row['question_count'] == 1 else '複数問はあるがformal strong経路がない。'}",
            f"- 推奨形式: {row['recommended_pattern']}", "",
        ])
    lines.extend([
        "## Safety / Clinical reasoning", "",
        f"- Safety S: {sum(row['safety_importance'] >= 4 for row in s_rows)}",
        f"- Clinical reasoning S: {sum(row['clinical_reasoning'] >= 4 for row in s_rows)}", "",
        "## Reserve 19", "",
        "`42_51_screening_summary_v04.json`で19件の存在は確認できたが、個票台帳はrepo・提供source packにない。",
        "19枠を`not_assessed`として記録し、未評価を不採用と誤表示していない。再利用可能数は現時点で判定不能。", "",
        "## 別issue", "",
        f"- 機械的に人間確認が必要と判定したNode: {len(issues)}", "- 内容はJSON監査のseparate issuesへ保存。", "",
        "## 判定上の注意", "",
        "スコアは優先候補抽出用であり、医学的採用判定ではない。S Nodeも問題作成前に臨床・教育レビューと原典確認を要する。", "",
    ])
    return "\n".join(lines)


def build_outputs(output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows, issues, meta = build_audit()
    s_rows = [row for row in rows if row["final_rank"] == "S"]
    categories = _category_summary(rows)
    safety_rows = [row for row in rows if row["safety_importance"] >= 4]
    reserve_rows = _reserve_rows(rows)
    _write_csv(output_dir / "remaining_node_priority_audit_v01.csv", rows, AUDIT_FIELDS)
    _write_json(output_dir / "remaining_node_priority_audit_v01.json", {"meta": meta, "separate_issues": issues, "nodes": rows})
    _write_csv(output_dir / "S_rank_nodes_v01.csv", s_rows, AUDIT_FIELDS)
    _write_json(output_dir / "S_rank_nodes_v01.json", s_rows)
    category_fields = ["category_large", "category_small", "category_name", "total_canonical_nodes", "strong_available_nodes", "strong_unsupported_nodes", "s_rank_nodes", "a_rank_nodes"]
    _write_csv(output_dir / "category_repairability_summary_v01.csv", categories, category_fields)
    _write_csv(output_dir / "safety_priority_nodes_v01.csv", safety_rows, AUDIT_FIELDS)
    _write_csv(output_dir / "reserve19_recheck_v01.csv", reserve_rows, list(reserve_rows[0]))
    (output_dir / "10G_priority_audit_report_v01.md").write_text(_report(rows, categories, issues, meta, reserve_rows), encoding="utf-8")
    return {"meta": meta, "rows": rows, "s_rows": s_rows, "categories": categories, "issues": issues, "reserve_rows": reserve_rows}


if __name__ == "__main__":
    result = build_outputs()
    print(json.dumps(result["meta"], ensure_ascii=False, indent=2))
