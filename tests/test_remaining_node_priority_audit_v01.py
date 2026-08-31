import hashlib
import json
from collections import Counter
from pathlib import Path

from scripts.build_remaining_node_priority_audit_v01 import build_audit, build_outputs


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
FORMAL_FILES = (
    "questions.json", "answers.json", "explanations.json", "question_tags.json",
    "knowledge_nodes.json", "knowledge_node_canonical_map.json",
    "strong_different_question_pairs.json",
)


def hashes():
    return {
        name: hashlib.sha256((BANK / name).read_bytes()).hexdigest()
        for name in FORMAL_FILES
    }


def test_all_1496_unsupported_canonical_nodes_are_ranked_once():
    rows, issues, meta = build_audit()
    assert meta["canonical_node_count"] == 1509
    assert meta["strong_available_node_count"] == 13
    assert meta["target_node_count"] == 1496
    assert len(rows) == len({row["canonical_node_id"] for row in rows}) == 1496
    assert set(row["final_rank"] for row in rows) <= {"S", "A", "B", "C", "HOLD"}
    assert sum(meta["rank_counts"].values()) == 1496
    assert len(issues) == meta["separate_issue_count"]


def test_s_rank_is_strict_and_has_patterns_safety_and_reasoning_evidence():
    rows, _issues, meta = build_audit()
    s_rows = [row for row in rows if row["final_rank"] == "S"]
    assert len(s_rows) == meta["s_rank_target"] == 75
    assert 50 <= len(s_rows) <= 100
    assert all(row["recommended_pattern"].startswith("TYPE_") for row in s_rows)
    assert all(row["reason"] and row["current_question_ids"] for row in s_rows)
    assert any(row["safety_importance"] >= 4 for row in s_rows)
    assert any(row["clinical_reasoning"] >= 4 for row in s_rows)


def test_category_summary_covers_all_18_fields_without_double_counting_primary_assignment(tmp_path):
    result = build_outputs(tmp_path)
    categories = result["categories"]
    assert [row["category_small"] for row in categories] == list(range(1, 19))
    assert sum(row["total_canonical_nodes"] for row in categories) == 1509
    assert sum(row["strong_available_nodes"] for row in categories) == 13
    assert sum(row["strong_unsupported_nodes"] for row in categories) == 1496
    assert sum(row["s_rank_nodes"] for row in categories) == 75


def test_outputs_include_every_required_artifact_and_do_not_mutate_formal_data(tmp_path):
    before = hashes()
    result = build_outputs(tmp_path)
    assert hashes() == before
    expected = {
        "remaining_node_priority_audit_v01.csv",
        "remaining_node_priority_audit_v01.json",
        "S_rank_nodes_v01.csv",
        "S_rank_nodes_v01.json",
        "category_repairability_summary_v01.csv",
        "safety_priority_nodes_v01.csv",
        "reserve19_recheck_v01.csv",
        "10G_priority_audit_report_v01.md",
    }
    assert {path.name for path in tmp_path.iterdir()} == expected
    parsed = json.loads((tmp_path / "remaining_node_priority_audit_v01.json").read_text(encoding="utf-8"))
    assert len(parsed["nodes"]) == 1496
    assert len(result["reserve_rows"]) == 19
    assert Counter(row["reusable"] for row in result["reserve_rows"]) == {"not_assessed": 19}
