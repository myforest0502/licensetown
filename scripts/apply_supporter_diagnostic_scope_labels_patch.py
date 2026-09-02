from pathlib import Path

path = Path("templates/goukaku/supporter_pilot_diagnostics.html")
text = path.read_text(encoding="utf-8")

replacements = {
    '<section class="card pilot-diagnostic-card"><h2>学習量</h2>': '<section class="card pilot-diagnostic-card"><h2>学習量</h2>\n    <p><strong>表示範囲：選択期間</strong></p>',
    '<h2>Repeat構造監査</h2>': '<h2>Repeat構造監査</h2>\n    <p><strong>表示範囲：選択期間</strong></p>',
    '<section class="card pilot-diagnostic-card"><h2>学習範囲</h2>': '<section class="card pilot-diagnostic-card"><h2>学習範囲</h2><p><strong>表示範囲：現在状態（全履歴の正式証拠から算出）</strong></p>',
    '<section class="card pilot-diagnostic-card"><h2>理解状態</h2>': '<section class="card pilot-diagnostic-card"><h2>理解状態</h2><p><strong>表示範囲：現在状態（全履歴の正式証拠から算出）</strong></p>',
    '<section class="card pilot-diagnostic-card"><h2>修復・定着</h2>': '<section class="card pilot-diagnostic-card"><h2>修復・定着</h2><p><strong>表示範囲：全履歴の正式状態遷移</strong></p>',
    '<h2>修復中Nodeの修復可能性</h2>': '<h2>修復中Nodeの修復可能性</h2>\n    <p><strong>表示範囲：現在状態（全履歴の正式証拠から算出）</strong></p>',
    '<h2>strong repair問題 整備優先順位</h2>': '<h2>strong repair問題 整備優先順位</h2>\n    <p><strong>表示範囲：現在状態（全履歴の正式証拠から算出）</strong></p>',
    '<h2>⑪ Shadow判断（開発中）</h2>': '<h2>⑪ Shadow判断（開発中）</h2>\n    <p><strong>表示範囲：現在状態（全履歴の正式証拠から算出）</strong></p>',
    '<h2>Phase11 過去推薦リプレイ</h2>': '<h2>Phase11 過去推薦リプレイ</h2>\n    <p><strong>表示範囲：全履歴</strong></p>',
    '<section class="card pilot-diagnostic-card saved-adaptive-audit-card"><h2>最新 adaptive_daily 30問セッション監査</h2>': '<section class="card pilot-diagnostic-card saved-adaptive-audit-card"><h2>最新 adaptive_daily 30問セッション監査</h2>\n    <p><strong>表示範囲：最新の保存済みadaptive_dailyセッション</strong></p>',
    '<section class="card pilot-diagnostic-card"><h2>最新のおすすめ30問シミュレーション</h2>': '<section class="card pilot-diagnostic-card"><h2>最新のおすすめ30問シミュレーション</h2>\n    <p><strong>表示範囲：現在状態（全履歴の正式証拠から算出）</strong></p>',
    '<section class="card pilot-diagnostic-card"><h2>分野横断の弱点候補</h2>': '<section class="card pilot-diagnostic-card"><h2>分野横断の弱点候補</h2><p><strong>表示範囲：全履歴の参考表示（Phase11 formal判断には未使用）</strong></p>',
}

for old, new in replacements.items():
    if new in text:
        continue
    if text.count(old) != 1:
        raise SystemExit(f"scope label target count={text.count(old)} for {old!r}")
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
