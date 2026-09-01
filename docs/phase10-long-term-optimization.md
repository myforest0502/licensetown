# LicenseTown ⑩ 長期最適化 仕様書

## 目的

⑩の役割は、受験生の学習履歴から「次に何を出すか」を安定して決め、同じ問題のやり過ぎを避けながら、弱点修復・確認・未学習探索を両立すること。

本仕様では、Knowledge Node状態遷移そのものと、出題選択ロジックを分離して扱う。

- 状態遷移: unseen / checking / repairing / repaired / recheck_due / stable
- 出題選択: repair / checking / exploration / maintenance
- 修復証拠: same question / different question weak / different question strong
- Safety: safety wrongを最優先候補として扱う

## 正式な優先順位

基本scoreの順序は以下。

1. safety wrong: 1000
2. confident wrong: 950
3. cross-question wrong: 900
4. repairing / unknown: 850
5. previous wrong unconfirmed: 800
6. recheck due: 700 + overdue
7. uncertain correct: 600
8. checking: 500
9. unseen: 300
10. repaired maintenance: 150
11. stable maintenance: 100

追加補正:

- same-question repeat: -180
- different-question strong: +80
- wrong Nodeのdifferent-question weak: +20
- 未出題Q: +10

## Repair evidenceの正式ルール

repairing Nodeを「直った」とみなすには、原則として同一Qの正解では足りない。

- same-Q success → repairing維持
- weak different-Q → repairing維持
- strong different-Q + correct + confidence=1 → repaired

recheck_dueも同様に、strong different-Q + correct + confidence=1でstableへ進める。

AIによる自由記述確認やatomic rubricは研究したが、再現性不足のため正式な修復証拠には採用しない。

## Singleton Nodeの扱い

Canonical Knowledge Nodeの大多数はsingletonであり、同一Node内に別Qが存在しない。

そのため「全Nodeをdifferent-Qで修復可能にする」は現状不可能。

正式方針:

- strong different-Qが存在するNodeではそれを優先
- weak relationしかない場合は形式的repair完了には使わない
- singletonはsame-Q再確認だけでrepairedへ昇格させない
- Safety上必要な場合のみsame-Qを再利用し得る

## 30問の基本構成

30問adaptiveではsoft targetとして以下を使う。

- repair: 15
- checking: 10
- exploration: 5

ただしこれは「絶対配分」ではない。

最近解いたQを再投入してまで15/10/5を満たしてはいけない。

## Recent Question Cooldown

### 目的

連続した30問セッションで同じQが大量再出題されることを防ぐ。

実利用では、修正前に2回目30問のうち15問が直前セッションと重複した。

### 対象

answered_atの新しい順で最大30 attemptsのquestion_idをrecent_question_idsとする。

正解・不正解に関係なくrecent対象。

### 正式な選択順

1. Safety緊急例外
2. non-recent repair/checking/exploration
3. non-recent maintenance/その他でquestion_countを完成
4. それでもquestion_count不足ならrecent fallback

soft compositionよりcooldownを優先する。

### Safety例外

safety_wrongかつ同一canonical Nodeにnon-recent代替Qが存在しない場合はrecent same-Qを許可する。

代替Qがある場合は:

strong different-Q > weak different-Q > recent same-Q

### repairing singleton

repair枠不足という理由だけでrecent repairing singletonを再投入しない。

bank全体でquestion_count不足の場合だけ最終fallbackとして使用する。

### 完全除外

exclude_idsはrecent fallbackより強い。fallbackでも復活させない。

### 監査フラグ

selector recordには以下を保持する。

- recent_question_repeat
- recent_cooldown_bypassed

十分なbankがある2連続30問ではoverlap=0を正式な回帰条件とする。

## Node多様性

同一canonical Nodeに偏りすぎないよう、原則1 Node 1問を先に選ぶ。

不足時のみ2問目、3問目を許可する。

目的は、repair優先度が高い1 Nodeだけで30問を埋めないこと。

## ⑩-B〜Eの研究結果

### ⑩-B Singleton repairability

- canonical Nodes: 1509
- singleton: 1462
- multi-question: 47
- strong confirmation可能: 3
- weak-only: 44
- formally unrepairable: 1506

結論: 問題追加・relation拡張なしに、全Nodeを形式的repair可能にはできない。

### ⑩-C Shadow pilot

alternative repair confirmationをshadow評価したが、正式採用せず。

### ⑩-D AI reliability

real AI評価120件でfalse PASSを確認。自由AI判定はrepair確定根拠にしない。

### ⑩-E Atomic rubric

clear-correct再現性が不足しfalse PASSも残ったため、正式repair evidenceには採用しない。

## 実利用から得た正式フィードバック

### 1. 連続30問の同一Q再出題

原因:

- same-Q誤答には-180があった
- recent正解Qには抑制がなかった
- soft repair targetがrecent singletonを再投入し得た

対策:

Recent Question Cooldown v0.2で、non-recentだけで30問を構成できる限りrecentを使わない。

### 2. 同じQの再回答は「悪」ではない

同一Q再回答は、理解の不安定性検出には価値がある。

例:

- correct confidence1 → wrong confidence1
- wrong confidence2 → wrong confidence1

したがって永久除外ではなくcooldownとcontrolled fallbackを採用する。

## 今後の監査情報

adaptive_dailyでは、後から「なぜそのQを出したか」を検証できるよう、selection metadataをlearning_events.question_results JSONBに保存する方向とする。

最小監査項目:

- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed

このmetadataは監査専用であり、Node状態遷移の入力条件に使わない。

## ⑩の完了条件

⑩は「理論上最適」になった時ではなく、以下が安定した時点で完了とする。

- 連続30問で不要な同一Q大量再出題が起きない
- Safetyの重要問題をcooldownで失わない
- strong different-Qが利用可能なら優先される
- repair/checking/explorationが特定Nodeへ極端に偏らない
- 選定理由を後から追跡できる
- 実利用で「同じ問題ばかり」「弱点を無視している」が再現しない

この状態を⑪「判断システム」への入力基盤とする。
