# PT Question Bank 新規追加問題 設計表 v0.1

Date: 2026-09-19  
Baseline main: `20c411588432744620c8d492769459eeca8b64fa`  
Formal bank: `2026-09-b20` / Q1-Q2000 / 2000問

## 目的

この設計表は、2000問を一律に増やすためのものではない。

次の4点を同時に満たす分野・Knowledge Nodeだけを優先して追加対象にする。

1. 国家試験における相対的重要度が高い
2. 現在のBankで同一Knowledge Nodeを別角度から確認する問題が不足している
3. formal repairで使える STRONG different-question evidence が不足している
4. critical Safety Nodeに代替確認問題がない

低頻度・一回限りの論点を、単に「1問しかない」という理由だけで複製しない。

## 使用した正式データ

- `questions.json`
- `question_tags.json`
- `knowledge_node_canonical_map.json`
- `question_equivalence_groups.json`
- `strong_different_question_pairs.json`
- Stage C repository-frequency Exam Weight
- Stage E / Stage F の正式 field supply 集計

Question Bankの過去問1100問は、分野別のrepository frequency proxyとして使う。
全1100問について正式な試験年度 provenance が揃っているわけではないため、
5年・10年・20年の出題頻度や「何年間で何回出た」という推測は行わない。

## 判定ルール v0.1

### 1. STRONG repair coverage

formal repair confirmationは、原則として同一derived Knowledge Node内の
materially different questionが必要である。

既存BankでSTRONG扱いできるのは、

- reviewed formal STRONG pair
- 同一derived Node内で task / primary ability が異なる別問題

のいずれか。

### 2. 分野別 target

これは国試統計ではなく、Level 2「深さ」学習へ移行するための
暫定Bank設計目標である。

- Exam Weight >= 1.5: official Nodeの40%にSTRONG alternateを持たせる
- Exam Weight >= 1.0 and <1.5: 35%
- Exam Weight >= 0.5 and <1.0: 30%
- Exam Weight <0.5: 一律増量しない

ただしExam Weightに関係なく、
critical Safety NodeでSTRONG alternateがないものは優先追加対象とする。

### 3. Node選択順

各分野の追加枠では次の順でNodeを選ぶ。

1. critical SafetyかつSTRONG alternateなし
2. 過去問が複数存在するがSTRONG alternateなし
3. 重要度の高い分野内のofficial singleton Node
4. original-only singletonは原則対象外。ただしSafetyまたは別途明確な教育上の理由がある場合のみ例外

このため、過去問が1回しか確認できない論点を均等に増やす設計にはしない。

## 現状診断と第一弾追加案

| ID | 分野 | 現在問数 | official過去問 | Canonical Node | 問/Node | STRONG可能Node | STRONG率 | official singleton | critical未補強 | 第一弾追加 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 解剖学 | 178 | 137 | 140 | 1.27 | 32 | 22.9% | 99 | 0 | **22** |
| 2 | 生理学 | 187 | 152 | 154 | 1.21 | 24 | 15.6% | 115 | 0 | **34** |
| 3 | 心理学 | 29 | 15 | 15 | 1.93 | 11 | 73.3% | 4 | 0 | **0** |
| 4 | 人間発達学 | 41 | 22 | 28 | 1.46 | 10 | 35.7% | 13 | 0 | **0** |
| 5 | 教育学 | 10 | 6 | 5 | 2.00 | 3 | 60.0% | 2 | 0 | **0** |
| 6 | 医学概論 | 77 | 34 | 61 | 1.26 | 12 | 19.7% | 21 | 2 | **2** |
| 7 | 病理学 | 92 | 63 | 65 | 1.42 | 22 | 33.8% | 39 | 0 | **0** |
| 8 | 内科学 | 195 | 118 | 151 | 1.29 | 36 | 23.8% | 83 | 10 | **15** |
| 9 | 神経医学 | 146 | 65 | 114 | 1.28 | 25 | 21.9% | 47 | 0 | **6** |
| 10 | 精神医学 | 47 | 35 | 34 | 1.38 | 10 | 29.4% | 24 | 0 | **1** |
| 11 | 小児学 | 58 | 16 | 44 | 1.32 | 10 | 22.7% | 6 | 3 | **3** |
| 12 | 臨床心理学 | 23 | 13 | 14 | 1.64 | 7 | 50.0% | 6 | 0 | **0** |
| 13 | 基礎運動学 | 92 | 50 | 65 | 1.42 | 21 | 32.3% | 30 | 1 | **1** |
| 14 | 臨床運動学 | 15 | 5 | 7 | 2.14 | 6 | 85.7% | 1 | 0 | **0** |
| 15 | 動作分析学 | 134 | 25 | 98 | 1.37 | 27 | 27.6% | 10 | 7 | **7** |
| 16 | 運動器 | 133 | 53 | 104 | 1.28 | 22 | 21.2% | 35 | 2 | **2** |
| 17 | 理学療法評価各論 | 203 | 87 | 158 | 1.28 | 35 | 22.2% | 57 | 11 | **11** |
| 18 | 理学療法治療各論 | 340 | 204 | 291 | 1.17 | 32 | 11.0% | 168 | 21 | **51** |

**旧暫定案: 155問（v0.2詳細監査で撤回）**

v0.2詳細監査では、単純なfield別STRONG率目標だけではfact-recallまで過剰に増やすため撤回。正式な最終推奨は Node割当表 v0.2 の **233問 / 合計2233問**。

## なぜ教育学・心理学などを一律に増やさないのか

総問題数が少ないことと、Bankが不足していることは同義ではない。

例:

- 教育学: 10問 / 5 Node = 2.00問/Node
- 心理学: 29問 / 15 Node = 1.93問/Node
- 臨床運動学: 15問 / 7 Node = 2.14問/Node

これらは絶対数は小さいが、Nodeあたりの深さは高く、
repository Exam Weightも低い。
よって「60問未満だから60問まで増やす」といった増量は行わない。

一方で理学療法治療各論は340問あるが291 Nodeに分散し、
STRONG alternateを持つNodeは32（11.0%）しかない。
総数が多くても、Level 2で深く確認するための別問題供給が薄い。

## 第一弾の意味

155問は初期スクリーニング値であり、最終推奨ではない。

これは、

- 高重要度fieldのrepair depth不足
- critical Safety singleton
- official Nodeのalternate不足

をまず埋めるための**第一弾設計量**。

追加後に再度、

- STRONG coverage
- singleton数
- Level 2での30問供給
- 実利用時fallback
- 72時間repeat guard
- field偏在

を再監査して、第二弾が必要か判断する。

## 次工程

詳細なNode監査を行い、追加対象を233 Nodeへ確定した。

各追加問題について最低限、

- field
- target Knowledge Node
- 現在の既存Q
- source側の根拠
- 追加理由
- intended task
- intended primary ability
- STRONG repair pair成立見込み
- Safety
- duplication risk
- 作問優先度

を持つ「新規追加問題 Node割当表」を作る。

その表を確認してから、実際に追加する問題数を確定する。

## 現時点の判断

- 2000問を一律に増やす: **NO**
- 問題数の少ないfieldを均等補充: **NO**
- 息子個人の弱点だけに合わせて作問: **NO**
- 正式Bank構造と国試weightに基づく追加: **YES**
- 最終推奨追加数: **233問**
- 233問を即作成: **まだNO**
- Node単位割当表: **作成済み（PT_QB_EXPANSION_NODE_ALLOCATION_V02_20260919.md）**
