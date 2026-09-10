# LicenseTown PT v1.0 定期点検 2026-09-10

## 今回のゴール

商品として成立している現在のPT v1.0本線を壊さず、Productionの実データ・ログから「今直すべき実在のv1.0 blocker」があるかだけを確認する。

判定基準は `docs/PT_V1_PRODUCT_GOAL.md` の車モデル（走る / 曲がる / 止まる / 壊れない / 原因追跡 / 修復可能）に限定する。見た目の磨き込み、将来機能、自然履歴を待たないと評価できない長期項目は blocker にしない。

## Productionログ点検

Render service `srv-d2m3iqvdiees73ch51l0` を確認。

- 2026-09-10 00:00Z 以降、error level の application log は 0 件。
- 2026-09-09 には既知の `/goukaku-no-michi` 例外が複数記録されている。これは既に原因特定・修正済みの既知事象。
- 同日には `/internal/learner-preview` の例外と、written understanding evaluation で OpenAI `billing_not_active` 429 が1系列記録されている。
- 今回の点検時点では、上記OpenAIエラーの継続発生は確認されなかった。したがって現時点で新しいv1.0 blockerとは判定しない。再発時のみ本線影響を確認する。

## Production DB 点検

Neon project `sparkling-frost-71060602` の read-only 集計。

### question_attempts

- total attempts: 1708
- distinct users: 3
- last 24h attempts: 135
- observed Q range: Q1〜Q1980
- Q2000超のattempt: 0
- 5分超未来時刻のattempt: 0
- max attempt_position: 5

`question_attempts` の基本的な保存境界に、今回の集計から明白な破損は見つからなかった。

### Recent exact-Q repeat

直近7日間の同一ユーザーにおける「直前attemptと完全に同じQ」の連続は3件あった。ただし、PR #296 のrepeat-quality fix反映後（2026-09-10 00:40Z以降）にはProduction attempt自体がまだ無く、自然履歴による修正後評価は未成立。

したがって現在の判定は以下。

- 過去履歴にexact same-Q consecutive evidence: YES
- PR #296でcode/test fix: YES
- fix後の自然Production evidence: PENDING
- 現時点で新たな追加修正を作る根拠: NO

次の自然学習セッション後に同じ集計を再確認する。

### free_monitor_slots

- total: 30
- used: 3
- free: 27
- slot range: 1〜30

30人上限の保存状態は今回の点検では正常。

### feedback_inbox

status集計は `responded = 1` のみ。未処理の `received/reviewing/planned` は今回の集計には存在しない。

## 判定

**今回、新しいv1.0 product blockerは検出されなかった。**

今すぐコード変更する根拠はない。商品化本線については、息子さんを含む自然利用を継続し、実利用で異常が出た時だけblocker修正へ進む。

## 次の点検ゲート

1. PR #296反映後の自然学習attemptがProductionに入る。
2. exact same-Q consecutive、Recent Cooldown、保存件数、Render error logを再確認する。
3. 異常がなければ追加実装せず継続運用。
4. 実在の学習不能、500、履歴破損、数字虚偽、異常repeat、today recommendationと出題の矛盾が観測された場合のみv1.0 blockerとして修正する。

## 今回はやらないこと

- Phase11の本番昇格
- 長期retention自然履歴を人工的に閉じること
- dashboardの追加polish
- session/fatigue分析
- speculative safeguard
- Question Bank再監査やQ2000超への増量
