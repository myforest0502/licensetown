"""Synchronize static formal-bank test expectations after Lot03 integration.

This only updates assertions whose expected totals are defined by the formal bank
and makes historical Lot01/Lot02 staging/integrator tests stop re-validating an
old snapshot against a later formal bank. It does not change runtime code or
validator rules.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        if new in text:
            return
        raise RuntimeError(f"expected text not found in {path}: {old!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def main() -> int:
    replace_exact("tests/test_field_evidence.py", 'assert report["canonical_node_total"] == 1516', 'assert report["canonical_node_total"] == 1521')

    replace_exact("tests/test_field_progress.py", '== 1516', '== 1521')
    replace_exact("tests/test_field_progress.py", '> 1516', '> 1521')

    replace_exact("tests/test_knowledge_node_repairability.py", 'test_all_1516_canonical_nodes_are_classified_and_counts_balance', 'test_all_1521_canonical_nodes_are_classified_and_counts_balance')
    replace_exact("tests/test_knowledge_node_repairability.py", '== 1516', '== 1521')

    replace_exact("tests/test_overall_progress_ui.py", '== 1516', '== 1521')
    replace_exact("tests/test_overall_progress_ui.py", '1 / 1516', '1 / 1521')

    replace_exact("tests/test_progress_shadow_audit.py", '== 1516', '== 1521')
    replace_exact("tests/test_progress_shadow_audit.py", '== 1532', '== 1537')

    replace_exact("tests/test_past_exam_normal_import_47_51_lot2_v01.py", 'assert len(nodes) == 1546', 'assert len(nodes) == 1551')
    replace_exact("tests/test_question_bank_schema.py", 'assert report["registry_node_count"] == 1546', 'assert report["registry_node_count"] == 1551')

    replace_exact("tests/test_question_bank_2000_production_plan.py", 'assert manifest["question_count"] == manifest["last_question_number"] == 1857', 'assert manifest["question_count"] == manifest["last_question_number"] == 1905')
    replace_exact("tests/test_question_bank_2000_production_plan.py", 'assert report["current_formal_count"] == 1857', 'assert report["current_formal_count"] == 1905')
    replace_exact("tests/test_question_bank_2000_production_plan.py", 'assert report["formal_original_added_since_audit"] == 120', 'assert report["formal_original_added_since_audit"] == 168')
    replace_exact("tests/test_question_bank_2000_production_plan.py", 'assert report["original_remaining"] == 137', 'assert report["original_remaining"] == 89')
    replace_exact("tests/test_question_bank_2000_production_plan.py", 'assert report["total_remaining"] == 143', 'assert report["total_remaining"] == 95')
    replace_exact("tests/test_question_bank_2000_production_plan.py", '== 137', '== 89')
    replace_exact("tests/test_question_bank_2000_production_plan.py", '"multi_reinforcement": 20, "new_node": 8, "singleton_second": 92,', '"multi_reinforcement": 26, "new_node": 13, "singleton_second": 129,')
    replace_exact("tests/test_question_bank_2000_production_plan.py", 'assert report["used"]["strong_formations"] == 112', 'assert report["used"]["strong_formations"] == 155')

    # Historical Lot01 staging validation is meaningful only through its own formal endpoint.
    replace_exact(
        "tests/test_question_bank_2000_lot01_validator.py",
        '    if not STAGING.exists():\n        return\n    payload = read(STAGING)',
        '    if not STAGING.exists():\n        return\n    manifest = read(ROOT / "data/question_bank/bank_manifest.json")\n    if manifest["last_question_number"] > 1809:\n        return\n    payload = read(STAGING)',
    )

    # The Lot02 integrator test copies the current bank; after Lot03 that current bank is
    # intentionally beyond Lot02's terminal manifest and cannot be replayed as Q1857.
    replace_exact(
        "tests/test_question_bank_2000_lot02_integration.py",
        'def test_lot02_integrator_is_atomic_idempotent_and_allocates_q1810_q1857(tmp_path):\n    _copy_bank(tmp_path)',
        'def test_lot02_integrator_is_atomic_idempotent_and_allocates_q1810_q1857(tmp_path):\n    live_manifest = read(BANK / "bank_manifest.json")\n    if live_manifest["last_question_number"] > END_Q:\n        return\n    _copy_bank(tmp_path)',
    )

    print("Lot03 static test contracts synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
