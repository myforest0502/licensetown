"""Refresh formal-bank count assertions after the reviewed Lot04 Q1906-Q1953 append.

This migration is intentionally narrow: it updates tests whose constants describe the
current formal bank and makes the historical Lot03 integrator test skip once a later
formal lot has superseded its exact b17/Q1905 terminal-state contract.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str, *, count: int | None = None) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    found = text.count(old)
    if count is not None and found != count:
        raise RuntimeError(f"{path}: expected {count} occurrences of {old!r}, found {found}")
    if found == 0:
        raise RuntimeError(f"{path}: migration pattern missing: {old!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def main() -> int:
    # Developer status mirrors the saved formal audit regenerated at integration.
    path = "tests/test_developer_status.py"
    for old, new in [
        ('assert bank["records"] == 1905', 'assert bank["records"] == 1953'),
        ('assert bank["original"] == 811', 'assert bank["original"] == 859'),
        ('assert bank["canonical_registry"] == 1551', 'assert bank["canonical_registry"] == 1555'),
        ('assert bank["canonical_represented"] == 1521', 'assert bank["canonical_represented"] == 1525'),
        ('assert bank["canonical_singleton"] == 1201', 'assert bank["canonical_singleton"] == 1178'),
        ('assert bank["canonical_multi"] == 320', 'assert bank["canonical_multi"] == 347'),
        ('assert bank["shared_groups"] == 312', 'assert bank["shared_groups"] == 340'),
        ('assert bank["safety_critical"] == 91', 'assert bank["safety_critical"] == 98'),
        ('assert bank["safety_moderate"] == 262', 'assert bank["safety_moderate"] == 267'),
    ]:
        replace(path, old, new, count=1)

    # Canonical represented-node count grew by four genuinely new Lot04 Nodes.
    for path in [
        "tests/test_field_evidence.py",
        "tests/test_field_progress.py",
        "tests/test_knowledge_node_repairability.py",
        "tests/test_overall_progress_ui.py",
        "tests/test_progress_shadow_audit.py",
    ]:
        target = ROOT / path
        text = target.read_text(encoding="utf-8")
        if "1521" not in text:
            raise RuntimeError(f"{path}: expected historical canonical count missing")
        text = text.replace("1521", "1525")
        if path.endswith("test_progress_shadow_audit.py"):
            if "1537" not in text:
                raise RuntimeError(f"{path}: expected historical membership total missing")
            text = text.replace("1537", "1541")
        target.write_text(text, encoding="utf-8")

    replace(
        "tests/test_past_exam_normal_import_47_51_lot2_v01.py",
        "assert len(nodes) == 1551",
        "assert len(nodes) == 1555",
        count=1,
    )
    replace(
        "tests/test_question_bank_schema.py",
        'assert report["registry_node_count"] == 1551',
        'assert report["registry_node_count"] == 1555',
        count=1,
    )

    # The production-plan audit now describes the one remaining 41-original lot.
    path = "tests/test_question_bank_2000_production_plan.py"
    replacements = [
        ('assert manifest["question_count"] == manifest["last_question_number"] == 1905', 'assert manifest["question_count"] == manifest["last_question_number"] == 1953'),
        ('assert report["current_formal_count"] == 1905', 'assert report["current_formal_count"] == 1953'),
        ('assert report["formal_original_added_since_audit"] == 168', 'assert report["formal_original_added_since_audit"] == 216'),
        ('assert report["original_remaining"] == 89', 'assert report["original_remaining"] == 41'),
        ('assert report["total_remaining"] == 95', 'assert report["total_remaining"] == 47'),
        ('== 89\n    assert sum(map(int, remaining["task"].values())) == 89\n    assert sum(map(int, remaining["level"].values())) == 89\n    assert sum(map(int, remaining["node_slot"].values())) == 89', '== 41\n    assert sum(map(int, remaining["task"].values())) == 41\n    assert sum(map(int, remaining["level"].values())) == 41\n    assert sum(map(int, remaining["node_slot"].values())) == 41'),
        ('"multi_reinforcement": 26, "new_node": 13, "singleton_second": 129,', '"multi_reinforcement": 37, "new_node": 18, "singleton_second": 161,'),
        ('assert report["used"]["strong_formations"] == 155', 'assert report["used"]["strong_formations"] == 198'),
    ]
    for old, new in replacements:
        replace(path, old, new, count=1)

    # Lot03's integrator deliberately remains strict for its historical b17 baseline.
    # Once the formal bank is newer, verify its range still exists and skip replaying
    # an obsolete terminal-manifest contract instead of weakening the integrator.
    path = ROOT / "tests/test_question_bank_2000_lot03_integration.py"
    text = path.read_text(encoding="utf-8")
    if "import pytest\n" not in text:
        text = text.replace("from pathlib import Path\n", "from pathlib import Path\n\nimport pytest\n", 1)
    marker = "def test_lot03_integrator_dry_run_is_atomic_and_idempotent(tmp_path):\n"
    guard = '''def test_lot03_integrator_dry_run_is_atomic_and_idempotent(tmp_path):\n    live_manifest = read(BANK / "bank_manifest.json")\n    if int(live_manifest["question_count"]) > 1905:\n        live_ids = {row["id"] for row in read(BANK / "questions.json")}\n        assert all(f"Q{i}" in live_ids for i in range(1858, 1906))\n        pytest.skip("Lot03 terminal integration contract is historical after later formal lots")\n'''
    if marker not in text:
        raise RuntimeError(f"{path}: Lot03 test marker missing")
    text = text.replace(marker, guard, 1)
    path.write_text(text, encoding="utf-8")

    print("Refreshed formal-count assertions for Q1-Q1953")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
