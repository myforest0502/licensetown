# LicenseTown 診断充足度・Exam Weight 設計 — 実データ監査 2026-09-12

状態: 設計監査のみ。本番ロジック変更なし。

## 1. 目的

`docs/diagnostic-exam-weight-learning-strategy-v01.md` を実装へ進める前に、現在の Production selector と実学習データを確認し、次の2点を事実ベースで固定する。

1. PR #342 の low-coverage exploration floor が本番で意図どおり働いているか。
2. 既存の `repair / checking / exploration = 15 / 10 / 5` という説明が、実際の30問セッションでどの程度「固定構成」なのか。

## 2. 基準状態

- main: `bb19d9a875289c941bd8302a3ac147f7effb1eb5`
- PR #342: `feat: add PT low-coverage exploration floor`
- Render deploy: `dep-daiefntckfvc738vqutg`
- deploy status: LIVE
- deploy finished: 2026-09-12 05:51:09 UTC
- Production DB: Neon `sparkling-frost-71060602` / branch `br-raspy-pond-azxss69f` / DB `neondb`

## 3. PR #342 前の低coverage分野

18分野監査で特に低かった分野は以下。

| field | 分野 | Canonical Node coverage |
|---:|---|---:|
| 18 | 理学療法治療各論 | 17.9% |
| 16 | 運動器 | 22.1% |
| 9 | 神経医学 | 24.6% |
| 17 | 理学療法評価各論 | 32.3% |
| 8 | 内科学 | 37.1% |
| 6 | 医学概論 | 41.0% |
| 4 | 人間発達学 | 42.9% |
| 15 | 動作分析学 | 43.9% |
| 10 | 精神医学 | 44.1% |

## 4. PR #342 LIVE 後の Production evidence

PR #342 LIVE 後に、同一PT学習者で `adaptive_daily` の30問セッションが4回確認できた。

- 4 sessions
- 120 question results
- `selection_group` 保存 120 / 120
- repair: 6
- checking: 90
- exploration: 24
- exploration の distinct Q: 24 / 24

### session 1

30問中 exploration は5問。

| Q | field | 分野 |
|---|---:|---|
| Q110 | 18 | 理学療法治療各論 |
| Q1124 | 9 | 神経医学 |
| Q1927 | 8 | 内科学 |
| Q383 | 17 | 理学療法評価各論 |
| Q424 | 16 | 運動器 |

### session 2

30問中 exploration は5問。

| Q | field | 分野 |
|---|---:|---|
| Q152 | 16 | 運動器 |
| Q1794 | 18 | 理学療法治療各論 |
| Q1931 | 9 | 神経医学 |
| Q425 | 17 | 理学療法評価各論 |
| Q565 | 8 | 内科学 |

### session 3

30問中 exploration は5問。

| Q | field | 分野 |
|---|---:|---|
| Q1117 | 18 | 理学療法治療各論 |
| Q1046 | 8 | 内科学 |
| Q1779 | 16 | 運動器 |
| Q271 | 9 | 神経医学 |
| Q356 | 17 | 理学療法評価各論 |

### session 4

30問中 exploration は9問。

| Q | field | 分野 |
|---|---:|---|
| Q1009 | 18 | 理学療法治療各論 |
| Q176 | 9 | 神経医学 |
| Q1780 | 16 | 運動器 |
| Q1178 | 8 | 内科学 |
| Q405 | 17 | 理学療法評価各論 |
| Q1022 | 1 | 解剖学 |
| Q1372 | 17 | 理学療法評価各論 |
| Q263 | 15 | 動作分析学 |
| Q772 | 16 | 運動器 |

## 5. 判定 — PR #342 は本番で機能している

最初の3セッションでは、exploration 5問が毎回、当時coverage最下位群の

- field 18 理学療法治療各論
- field 16 運動器
- field 9 神経医学
- field 17 理学療法評価各論
- field 8 内科学

へ1問ずつ配分された。

これは PR #342 の `take_exploration()` が狙った「低coverage分野から、まず異なる分野へ1問ずつ配る」という挙動と一致する。

したがって、現時点の Production evidence では、PR #342 を「効いていない」とみなす根拠はない。むしろ、導入前に最も不足していた5分野へ exploration が明確に集中している。

## 6. 重要な発見 — 15 / 10 / 5 は実現値の固定比率ではない

selector 内の30問 target は、通常時

- repair: 15
- checking: 10
- exploration: 5

になる。

しかし実装は、各 target を満たせる eligible candidate が不足した場合、最後の fallback で `normal_candidates` から残り枠を埋める。

そのため、この比率は「必ず30問が15/10/5になる固定構成」ではない。

今回の実現値は4セッション合計で、

- repair 6 / 120 = 5.0%
- checking 90 / 120 = 75.0%
- exploration 24 / 120 = 20.0%

だった。

セッション別では、

- session 1: repair 0 / checking 25 / exploration 5
- session 2: repair 0 / checking 25 / exploration 5
- session 3: repair 4 / checking 21 / exploration 5
- session 4: repair 2 / checking 19 / exploration 9

となっている。

session 4 の exploration 9問も、coverage floor が勝手に5問を9問へ増やしたのではない。repair / checking の eligible supply を target 順に取った後、残り枠を fallback で埋めた結果、priority_group が exploration の候補も追加されたためである。

### 仕様上の整理

今後、15 / 10 / 5 は以下のように表現する。

> selector の優先取得 target。eligible candidate が不足した場合は fallback で構成が変動するため、実現値を保証する固定比率ではない。

「基本構成15/10/5を維持」という表現だけでは、本番挙動を誤解させるので注意する。

## 7. 診断60問設計への含意

今回の監査から、次の設計判断は維持できる。

1. 現行PR #342は、未網羅分野を埋める暫定Safety netとして残す。
2. ただし、coverage floorだけで「診断充足」を表現しない。
3. fieldごとの最低60問 + Node breadth を正式な診断充足層として別に設ける。
4. 60問未満のfieldを「今日やること」の通常配分で優先する。
5. Safety-critical / 明白な重大weakness repair は別レーンで割り込ませる。
6. selectorの実現構成は、target値ではなく Production の `selection_group` 実績でも監査する。

## 8. Exam Weight の一次資料

Library には第42回〜第61回の理学療法士国家試験問題PDFが午前・午後で揃っていることを確認済み。

- 20回分
- 午前 / 午後
- 合計40 PDF

また、現行 Question Bank の `questions.json` では past-exam 問題に `exam.exam_no`, `exam.session`, `exam.question_no` が保持されていることを確認した。

ただし、Question Bank は教材として選択・追加・除外を行っているため、Question Bank 内の past-exam 件数をそのまま20年の実試験出題分布とみなしてはならない。

Exam Weight の正式値は、40 PDF を一次資料として18分野へ分類した集計を根拠にする。

## 9. 次工程

実装前に次を行う。

1. 第42〜61回の40 PDFについて、午前/午後、問題番号、配点区分、18分野を持つ監査用 dataset を作る。
2. 各fieldの20年総出題数、総配点寄与、年平均、年ごとの安定性、直近5/10/20年を集計する。
3. その結果から Exam Weight と field別 target_arrival を設計する。
4. 同時に Production の field別 attempt数 / distinct Q / distinct Node / coverage を監査し、60問未満fieldの正式な診断不足判定を作る。
5. 仕様・テスト条件を固めてから selector / presentation を変更する。

現段階では main / Production selector は変更しない。
