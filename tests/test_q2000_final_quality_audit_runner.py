import json
from pathlib import Path

from reports.question_bank_q2000_final_quality_audit import main


def test_q2000_final_quality_audit_runner():
    """Temporary CI-only runner for the read-only Q1-Q2000 final quality audit."""
    rc = main()
    report_path = Path(__file__).resolve().parents[1] / "reports" / "question_bank_q2000_final_quality_audit.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    print("Q2000_FINAL_QUALITY_AUDIT_SUMMARY=" + json.dumps({
        "scope": report.get("scope"),
        "bank_version": report.get("bank_version"),
        "question_count": report.get("question_count"),
        "blocker_count": report.get("blocker_count"),
        "review_candidate_counts": report.get("review_candidate_counts"),
        "top_near_duplicate_candidates": (report.get("review_candidates") or {}).get("near_duplicate_candidates", [])[:20],
        "duplicate_node_label_candidates": (report.get("review_candidates") or {}).get("duplicate_node_label_candidates", [])[:20],
    }, ensure_ascii=False, sort_keys=True))
    assert rc == 0
    assert report.get("blocker_count") == 0
