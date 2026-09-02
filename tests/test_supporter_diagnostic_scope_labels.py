from pathlib import Path


TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "templates"
    / "goukaku"
    / "supporter_pilot_diagnostics.html"
)


def _template_text():
    return TEMPLATE.read_text(encoding="utf-8")


def test_selected_period_scope_is_explicit_for_period_filtered_cards():
    text = _template_text()
    assert text.count("表示範囲：選択期間") == 2
    assert "<h2>学習量</h2>\n    <p><strong>表示範囲：選択期間</strong></p>" in text
    assert "<h2>Repeat構造監査</h2>\n    <p><strong>表示範囲：選択期間</strong></p>" in text


def test_current_formal_state_scope_is_explicit_for_current_state_cards():
    text = _template_text()
    assert text.count("表示範囲：現在状態（全履歴の正式証拠から算出）") == 6
    for heading in (
        "学習範囲",
        "理解状態",
        "修復中Nodeの修復可能性",
        "strong repair問題 整備優先順位",
        "⑪ Shadow判断（開発中）",
        "最新のおすすめ30問シミュレーション",
    ):
        assert heading in text


def test_special_scope_labels_distinguish_history_latest_session_and_reference_data():
    text = _template_text()
    assert "表示範囲：全履歴の正式状態遷移" in text
    assert "表示範囲：全履歴" in text
    assert "表示範囲：最新の保存済みadaptive_dailyセッション" in text
    assert "表示範囲：全履歴の参考表示（Phase11 formal判断には未使用）" in text


def test_scope_change_is_supporter_presentation_only():
    text = _template_text()
    assert "この判断は学習者画面には反映されていません。" in text
    assert "pilot-period-tabs" in text
