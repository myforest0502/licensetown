from pathlib import Path

from supporter_report import _accuracy_trend, _parent_field_snapshot


def test_parent_accuracy_trend_compares_early_and_recent_days():
    activity = {
        "daily": [
            {"answered_count": 10, "correct_count": 5},
            {"answered_count": 10, "correct_count": 6},
            {"answered_count": 10, "correct_count": 6},
            {"answered_count": 0, "correct_count": 0},
            {"answered_count": 10, "correct_count": 8},
            {"answered_count": 10, "correct_count": 8},
            {"answered_count": 10, "correct_count": 9},
        ]
    }
    trend = _accuracy_trend(activity)
    assert trend["status"] == "上向き"
    assert trend["delta"] > 0
    assert "前半" in trend["reason"]
    assert "後半" in trend["reason"]


def test_parent_field_snapshot_ignores_tiny_samples():
    fields = [
        {"name": "解剖", "answered_count": 30, "accuracy": 90},
        {"name": "生理", "answered_count": 25, "accuracy": 55},
        {"name": "心理", "answered_count": 2, "accuracy": 100},
    ]
    snapshot = _parent_field_snapshot(fields)
    assert [item["name"] for item in snapshot["strengths"]] == ["解剖", "生理"]
    assert [item["name"] for item in snapshot["needs_attention"]] == ["生理", "解剖"]
    assert all(item["name"] != "心理" for item in snapshot["strengths"])


def test_parent_dashboard_focuses_on_parent_questions_and_loads_scoped_css():
    root = Path(__file__).resolve().parents[1]
    template = (root / "templates" / "goukaku" / "supporter.html").read_text(encoding="utf-8")
    base = (root / "templates" / "goukaku" / "base.html").read_text(encoding="utf-8")
    css = (root / "static" / "goukaku" / "supporter-parent-v01.css").read_text(encoding="utf-8")

    for phrase in [
        "試験まであと",
        "ちゃんと続いてる？",
        "成績は上がった？",
        "このままで大丈夫？",
        "そもそも、やってるの？",
        "何ができていて、何を見直している？",
        "親として今すること",
    ]:
        assert phrase in template

    assert "supporter-parent-v01.css" in base
    assert ".supporter-parent-v01" in css
