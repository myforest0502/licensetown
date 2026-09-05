from pathlib import Path

import supporter_report


ROOT = Path(__file__).resolve().parents[1]


def test_parent_report_does_not_load_per_question_diagnostics():
    source = (ROOT / "supporter_report.py").read_text(encoding="utf-8")
    assert "get_question_attempts" not in source
    assert "build_pass_readiness" not in source
    assert "build_field_evidence" not in source
    assert "build_field_progress" not in source


def test_parent_template_keeps_parent_facing_information_only():
    text = (ROOT / "templates" / "goukaku" / "supporter.html").read_text(encoding="utf-8")
    for expected in (
        "今の学習状況",
        "累計：",
        "取り組んだ分野",
        "直近の学習",
        "学習時間",
        "学習ペース：",
        "今後の見通し：",
    ):
        assert expected in text

    for forbidden in (
        "Repair Supply",
        "selection_reason",
        "cooldown",
        "Phase11",
        "Shadow",
        "Baseline",
    ):
        assert forbidden not in text


def test_parent_trajectory_never_claims_pass_probability():
    trajectory = supporter_report._trajectory(
        {"total_answers": 100, "average_accuracy": 80},
        {"weekly_answers": 30},
        [{"name": "神経"}, {"name": "運動"}, {"name": "評価"}],
    )
    assert trajectory["pass_probability"] is None
    assert trajectory["pass_guarantee"] is False
