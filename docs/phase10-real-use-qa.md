# LicenseTown ⑩ 実利用QAマトリクス

## 目的

⑩の品質はpytestの通過だけでなく、実際の受験生利用で「不自然な出題」が起きないことを確認して判断する。

本QAは、RenderやProduction DBを使わなくても設計・テスト可能な項目と、実利用でしか確認できない項目を分離する。

## A. 自動テストで固定する項目

### A1. Recent Cooldown

- 直前30回答が全て正答でもrecent対象
- 直前30回答が全て誤答でもrecent対象
- 15 repairing singleton + 十分なnon-recent bank → overlap 0
- 30 repairing singleton + 十分なnon-recent bank → overlap 0
- non-recentだけで30問完成可能 → recent bypass 0
- non-recent 25問しかない → recent fallback 5問
- Safety singleton → 必要時のみrecent bypass可
- exclude_ids → fallbackでも復活しない

### A2. Repair evidence

- strong different-Q > weak different-Q > same-Q
- same-Q correctだけではrepairedへ進まない
- weak different-Q correctだけではrepairedへ進まない
- strong different-Q + correct + confidence1 → repaired
- repaired後の新規wrong/unknown → repairingへ戻る

### A3. Retention

- repaired + 7日 → recheck_due
- stable + 30日 → recheck_due
- recheck_due + strong different-Q + correct + confidence1 → stable
- recheck_dueでwrong/unknown → repairing

### A4. Composition

30問の15/10/5はsoft target。

- recent Qを使ってまで比率を維持しない
- Safetyを比率維持のために落とさない
- 候補不足時はquestion_count完成を優先
- 1 Node集中を避ける

### A5. Audit

adaptive_dailyの選定理由がquestion_resultsへ保存されること。

最低限:

- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed

通常random / dashboard recommendation / nekketsuにはadaptive auditを付けない。

## B. 実利用で確認する項目

### B1. 30問→30問

観察:

- Q重複数
- Node重複数
- recent cooldown bypass数
- bypass理由

期待:

通常はQ重複0。

重複がある場合は、Safetyまたは候補不足として説明可能であること。

### B2. 「同じ問題ばかり」の体感

Q重複が0でも、同じテーマ・似た設問が続けば受験生には反復感がある。

観察:

- canonical Node集中
- category_small集中
- relationの近いNode集中

これはQ番号重複とは別問題として扱う。

### B3. 「弱点を放置している」の体感

cooldownを強くしすぎると、間違えた直後に弱点が全く出なくなる可能性がある。

観察:

- confident wrong後の次sessionで同Nodeのdifferent-Qが出たか
- strong different-Q候補があるのにunseenばかりになっていないか
- singletonのためにrepairが一時保留されているだけか

### B4. 自信度との整合

特に確認するパターン:

- wrong conf1 → 最優先repair候補
- wrong conf2/3 → repair候補
- correct conf2/3 → stabilization/checking候補
- correct conf1 → 過剰反復しない

### B5. 1日の長時間利用

10問おすすめ + 30問 + 30問など複数セッション時に、後半ほど不自然なfallbackが増えないか確認する。

観察:

- recent_cooldown_bypassed率
- maintenance比率
- unseen比率
- 同一Node再出現率

## C. 異常判定の暫定しきい値

これは運用開始時の監視目安であり、正式な教育的閾値ではない。

### 赤信号

- 十分なbankがあるのに連続30問overlap > 0
- recent_cooldown_bypassedがSafety/候補不足で説明できない
- 同じQが同一30問内に2回出る
- exclude_idsのQが出る
- strong different-Qが存在するのにrecent same-Qが優先される

### 黄信号

- 30問で同一canonical Nodeが3問以上
- repair目的なのにrepair候補がほぼ出ない
- exploration目的なのに既出Q中心
- 60問以上連続利用でmaintenanceが急増

### 観察継続

- 同一分野への集中
- uncertain correctの再確認頻度
- repaired Nodeの維持問題頻度

これらは目的次第で正常な場合もある。

## D. 実利用ログで最低限見る列

- question_id
- knowledge_node_id
- canonical_node_id（再構成可）
- is_correct
- confidence
- answer_status
- learning_source
- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed
- answered_at

## E. ⑩完了後も残す回帰テスト

以下は⑪以降でも削除しない。

1. 2連続adaptive30 overlap=0（十分なbank）
2. singleton-heavy overlap=0
3. Safety singleton fallback
4. strong > weak > recent same-Q
5. exclude_ids完全除外
6. Node多様性
7. repaired/recheck_due/stable遷移
8. adaptive audit保存

⑪が学習目的を決めるようになっても、⑩の安全装置として維持する。
