# LicenseTown ⑪ 判断システムへの橋渡し設計

## 目的

⑪の役割は、単に「点数が低い分野を出す」ことではない。

受験生の現在地・弱点・修復状況・直近行動をまとめて、

- 今日は何をやるべきか
- どの分野を何問やるべきか
- 何を今は出さないべきか
- 弱点修復と未学習探索のどちらを優先するか

を判断する層とする。

⑩が「候補Qの選び方」、⑪が「今日は何を目的に学ぶか」を決める関係にする。

## ⑩と⑪の責任分離

### ⑩ 長期最適化

質問単位・Knowledge Node単位で、次の候補Qを安全に順位付けする。

主な入力:

- question attempts
- Node state
- repair evidence
- Safety
- recent cooldown

主な出力:

- question_id
- priority_reason
- priority_group
- priority_score
- repair evidence quality
- recent flags

### ⑪ 判断システム

ユーザー単位で「今日の学習方針」を決める。

主な入力:

- 分野別回答数・正答率
- Node state分布
- confident wrong件数
- repairing件数
- recheck_due件数
- unseen量
- 直近の学習量
- 直近のおすすめ達成状況
- 学習モードの利用状況
- ⑩のselection audit

主な出力:

- today_goal
- target_field
- target_question_count
- learning_intent
- recommended_route
- reason_code
- user-facing explanation

## 判断の最小単位

⑪で最初から複雑なAI判断をさせない。

まずは決定木・scoreベースで、再現可能な判断を行う。

learning_intentは最低限以下。

- repair: 明確な弱点修復
- recheck: 修復後の保持確認
- coverage: 未学習・回答不足分野の探索
- stabilization: 正解しているが自信が低い領域の安定化
- maintenance: 安定領域の維持

## 判断の優先順位案

### 1. Safety repair

重大Safety Nodeに誤答がある場合、最優先。

ただし⑩のRecent Cooldownとstrong/weak different-Q優先を尊重する。

### 2. Confident wrong / repeated wrong

自信を持った誤答、同Node複数誤答を優先。

単なる1回の不正解より重く扱う。

### 3. Recheck due

一度修復したNodeが保持確認時期に来た場合、再確認する。

### 4. Coverage不足

回答数が少なく、実力判定に必要なデータが不足している分野を埋める。

現在の「おすすめ10問」はこの役割を持つ。

### 5. Uncertain correct

正答していてもconfidence2/3が多い領域を安定化する。

### 6. Maintenance

上記が少ない時だけ安定Nodeを軽く維持する。

## 「分野」と「Node」を混同しない

⑪では二段階判断を基本にする。

1. どの分野・目的を優先するか
2. その目的の中で⑩にQ選択を任せる

例:

人間発達学の回答数不足
→ ⑪: coverageとして人間発達学10問
→ ⑩: その対象範囲内でrecentを避けつつNode多様性を確保

精神医学でconfident wrongが多い
→ ⑪: repairとして精神医学を優先
→ ⑩: strong different-Q、Safety、recent cooldownを考慮して具体Qを選ぶ

## おすすめ学習の正式データ

Phase2でrecommendation_planをlearning_eventsへ記録する設計を導入した。

⑪では今後、以下を利用できる。

- recommendation field
- recommendation goal
- recommendation progress
- completed / incomplete

これにより、

「おすすめを出したがやらなかった」
「別ルートで同じ分野を10問やって達成した」

を区別できる。

おすすめ達成判定は学習ルートではなく、対象分野の当日回答数で評価する。

## Selection Auditの使い道

⑩のselection auditは⑪の判断品質検証に使う。

例:

- repair目的の30問なのにselection_group=repairがほぼ0
- coverage目的なのにrecent_cooldown_bypassedが多数
- 同じreasonばかり選ばれている

こうした矛盾を後から検出できる。

監査情報を直接Node stateへ反映させない。

## 「おすすめ」の説明

ユーザー向けには内部scoreを見せない。

内部reason_codeから短い説明へ変換する。

例:

- insufficient_coverage
  - 「まだ実力を判断する問題数が少ないため」
- confident_wrong_cluster
  - 「自信を持って間違えた問題が続いているため」
- repair_followup
  - 「最近つまずいた内容を別の問題で確認するため」
- recheck_due
  - 「一度できた内容が定着しているか確認するため」
- uncertain_correct
  - 「正解できているけれど、まだ迷いが残っているため」

## 学習量の扱い

⑪は「多くやれば良い」にはしない。

最初の正式目安:

- おすすめ集中学習: 10問
- 通常adaptive: 30問
- 追加学習: 本人が続けたい時

同日に既に十分な学習量がある場合は、追加の30問を機械的に勧めない設計へ将来拡張する。

## 相談モードの扱い

相談利用の有無は活動状況として利用可能だが、相談内容は⑪へ入力しない。

プライバシー上、本文・会話内容を学習判断へ利用する設計にしない。

## ⑪ v0.1でやらないこと

- LLMに全判断を丸投げ
- 相談本文の分析
- 合否確率の断定
- 1回の誤答だけで強い弱点認定
- 直近Qを無視した大量repair
- dashboard表示のためだけの固定デモ値

## ⑪ v0.1の実装順

1. Judgment input snapshotを作る
2. reason_codeを定義する
3. deterministicな判断関数を作る
4. 既存recommended_studyとの比較をshadowで行う
5. 息子さんの実利用データで「現行おすすめ vs ⑪候補」を比較する
6. 明らかな改善が確認できたら表示へ接続する

いきなり本番おすすめを置き換えない。

## Judgment input snapshot案

```python
{
    "total_answers": 0,
    "today_answers": 0,
    "fields": [...],
    "node_states": {
        "repairing": 0,
        "repaired": 0,
        "recheck_due": 0,
        "stable": 0,
        "checking": 0,
        "unseen": 0,
    },
    "confident_wrong_count": 0,
    "cross_question_wrong_nodes": 0,
    "uncertain_correct_count": 0,
    "recommendation_plan": None,
    "recommendation_progress": None,
    "recent_learning": {...}
}
```

## Judgment output案

```python
{
    "learning_intent": "coverage",
    "target_field": "人間発達学",
    "question_count": 10,
    "recommended_route": "dashboard_recommendation",
    "reason_code": "insufficient_coverage",
    "reason_text": "まだ実力を判断する問題数が少ないため"
}
```

## ⑪へ進む前のゲート

⑩側で以下を満たした後に⑪の本実装へ進む。

- recent cooldown v0.2がmainで安定
- adaptive selection auditが保存できる
- 連続30問の不要重複が実利用でも解消
- selection reasonを後から確認できる
- Phase2のrecommendation_planが新規履歴で蓄積する

このゲートを満たすまでは⑪はshadow設計・QAに留める。
