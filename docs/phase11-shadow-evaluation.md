# LicenseTown ⑪ Shadow評価仕様

## 目的

⑪の新しい判断システムをいきなり本番おすすめへ接続せず、現行ロジックと並走させて品質を比較する。

本番表示・Render反映・Production DB writeなしでも、入力スナップショットと期待判断を設計できる。

## 比較する2つの判断

- current_recommendation: 現行のおすすめ学習
- shadow_judgment: ⑪候補

ユーザー画面にはcurrentだけを表示し、shadowは内部QA用。

## Shadow output

最低限:

```python
{
    "learning_intent": "repair|recheck|coverage|stabilization|maintenance",
    "target_field": "..." | None,
    "question_count": 10 | 30,
    "reason_code": "...",
    "reason_text": "..."
}
```

## 主要reason_code案

- safety_repair
- confident_wrong_cluster
- repeated_wrong_cluster
- recheck_due
- insufficient_coverage
- uncertain_correct_cluster
- maintenance_only

## 優先順位

1. safety_repair
2. confident_wrong_cluster
3. repeated_wrong_cluster
4. recheck_due
5. insufficient_coverage
6. uncertain_correct_cluster
7. maintenance_only

ただし「1回のwrongだけ」で分野全体をrepair最優先にしない。

## Shadow QAケース

### Case 1: 新規ユーザー

条件:

- total_answers = 0
- field data不足

期待:

- intent = coverage
- 回答不足分野を10問

### Case 2: 回答数不足の分野あり

条件:

- 一部fieldのみ3問など
- 明確なconfident wrong clusterなし

期待:

- intent = coverage
- insufficient_coverage

### Case 3: confident wrongが複数

条件:

- 同分野または同Node周辺でconfidence1 wrong複数

期待:

- coverageよりrepair優先
- reason = confident_wrong_cluster

### Case 4: repeated wrong

条件:

- 同canonical Nodeで異なるQを複数誤答

期待:

- repair
- repeated_wrong_cluster

### Case 5: recheck_due

条件:

- urgent repairなし
- recheck_dueあり

期待:

- recheck

### Case 6: uncertain correct中心

条件:

- wrong clusterなし
- correct confidence2/3多数

期待:

- stabilization

### Case 7: 全体安定

条件:

- urgent repairなし
- coverage十分
- recheckなし
- uncertain少数

期待:

- maintenance

## 実利用比較で見るポイント

### 1. 現行とshadowが一致

理由も一致するなら改善不要。

### 2. fieldは一致、理由が違う

どちらの理由が学習履歴に忠実か確認する。

### 3. fieldが異なる

以下を確認:

- confident wrongをshadowだけが拾っているか
- 現行が単純な回答数不足だけを優先していないか
- shadowが1回の誤答に過剰反応していないか

### 4. question_countが異なる

10問集中と30問adaptiveのどちらが自然かを確認する。

## 採用判定

⑪を本番へ昇格する条件:

- 主要QAケースで決定論的に再現可能
- 現行より明確に悪い判断がない
- confident wrong / repeated wrongを現行より適切に拾える
- coverage不足を無視しない
- recent cooldownや⑩の安全装置と矛盾しない
- 理由をユーザー向け日本語で説明可能

## 不採用条件

以下が1つでも再現する場合、本番接続しない。

- 1誤答で分野全体を固定
- 同じ分野を延々おすすめ
- recent Q大量再出題を誘発
- Safetyよりcoverageを優先
- 理由コードと実際の選定Qが一致しない
- 相談内容を判断材料に使う

## ⑩との接続契約

⑪は「何を目的に何問やるか」を決める。

⑩は「具体的にどのQを出すか」を決める。

⑪はQ番号を直接固定しない。

例:

```text
⑪: repair / 精神医学 / 10問
↓
⑩: priority + repair evidence + recent cooldown + Node diversity
↓
Q選定
```

この責任分離を崩さない。
