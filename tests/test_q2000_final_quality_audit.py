import json
from pathlib import Path

from reports.question_bank_q2000_final_quality_audit import main


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "question_bank_q2000_final_quality_audit.json"


def test_q2000_final_quality_audit_has_no_structural_blockers():
    assert main() == 0
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["scope"] == "Q1-Q2000"
    assert report["question_count"] == 2000
    assert report["blocker_count"] == 0
    assert len(report["registered_exact_provenance_repeats"]) == 4
    assert {
        frozenset(item["question_ids"])
        for item in report["registered_exact_provenance_repeats"]
    } == {
        frozenset(("Q972", "Q1354")),
        frozenset(("Q1067", "Q1391")),
        frozenset(("Q1230", "Q1526")),
        frozenset(("Q1411", "Q1585")),
    }

    canonicalized = report["review_candidates"].get(
        "duplicate_node_labels_already_canonicalized", []
    )
    assert any(
        set(item["raw_node_ids"]) == {"KN0597", "KN0807"}
        and item["canonical_node_ids"] == ["KN0597"]
        for item in canonicalized
    )

    unresolved = report["review_candidates"].get("duplicate_node_label_candidates", [])
    assert all(
        set(item["raw_node_ids"]) != {"KN0597", "KN0807"}
        for item in unresolved
    )
