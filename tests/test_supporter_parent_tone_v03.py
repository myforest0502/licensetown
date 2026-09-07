from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_parent_trend_labels_are_plain_japanese():
    text = (ROOT / "templates" / "goukaku" / "supporter.html").read_text(encoding="utf-8")
    assert "'好調' if ps.accuracy_trend.status == '上向き'" in text
    assert "'注意' if ps.accuracy_trend.status == '要確認'" in text
    assert "'順調' if ps.accuracy_trend.status == 'ほぼ横ばい'" in text
    assert "<strong>{{ trend_label }}</strong>" in text


def test_parent_intro_has_visible_accent_treatment():
    css = (ROOT / "static" / "goukaku" / "supporter-parent-v01.css").read_text(encoding="utf-8")
    assert ".supporter-parent-intro:before" in css
    assert "linear-gradient(135deg,#edf8f1,#f7fbff 58%,#fff8eb)" in css
