from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_parent_trend_labels_are_plain_japanese():
    text = (ROOT / "supporter_report.py").read_text(encoding="utf-8")
    assert 'status = "好調"' in text
    assert 'status = "注意"' in text
    assert 'status = "順調"' in text
    assert 'status = "上向き"' not in text
    assert 'status = "要確認"' not in text
    assert 'status = "ほぼ横ばい"' not in text


def test_parent_intro_has_visible_accent_treatment():
    css = (ROOT / "static" / "goukaku" / "supporter-parent-v01.css").read_text(encoding="utf-8")
    assert ".supporter-parent-intro:before" in css
    assert "linear-gradient(135deg,#edf8f1,#f7fbff 58%,#fff8eb)" in css
