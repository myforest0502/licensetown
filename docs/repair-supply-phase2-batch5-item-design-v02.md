# Repair Supply Phase 2 — batch5 item design v0.2

Status: manual medical/content review candidate; not yet Question Bank data.

Targets: current top five Priority C repairing Nodes after Q1606-Q1625 were added. Proposed IDs assume main ends at Q1625; Codex must reconfirm before writing.

Design rule: same canonical Knowledge Node, materially different demand from the active-wrong source. Existing weak pairs stay WEAK unless independent review proves otherwise. Structural `different_question_strong` is necessary but not sufficient.

## Q1626 — KN0404
- Active wrong: Q410
- Source demand: `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q410 category semantics (`A-4`), source original.
- Stem: 四つ這い位の乳児で、頭頸部を屈曲させると両上肢が屈曲し、両下肢が伸展する反応が繰り返しみられた。この反応として最も適切なのはどれか。
- Choices:
  A. 非対称性緊張性頸反射〈ATNR〉
  B. 対称性緊張性頸反射〈STNR〉
  C. Moro反射
  D. 陽性支持反応
  E. パラシュート反応
- Correct: B
- Rationale: STNRでは頸部屈曲により両上肢屈曲・両下肢伸展、頸部伸展では両上肢伸展・両下肢屈曲が誘発される。Q410の反応パターン暗記ではなく、観察された四つ這い位での反応から反射名を解釈する。
- Tag target: KN0404; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.

## Q1627 — KN0412
- Active wrong: Q1580
- Existing weak candidate: Q419
- Existing pair review: Q419/Q1580 are near-duplicate fact-recall items about sustained deep inspiration; keep WEAK.
- New demand: `intervention_selection / PRESCRIBE`
- Management target: inherit active-wrong Q1580 category semantics (`C-18`).
- Stem: 腹部手術翌日。疼痛のため浅い呼吸が続き、胸部画像で軽度の無気肺を認めた。インセンティブスパイロメトリの指導として最も適切なのはどれか。
- Choices:
  A. 強く速く呼気して指標を最大まで上げる。
  B. ゆっくり深く吸気し、十分な吸気位を短時間保つ練習を反復する。
  C. 声門を閉じて息こらえだけを反復する。
  D. 浅く速い呼吸を数分間続ける。
  E. 咳嗽だけを反復し、吸気練習は避ける。
- Correct: B
- Rationale: インセンティブスパイロメトリはゆっくり深い吸気と持続吸気を視覚的フィードバックで促し、肺胞再膨張や術後無気肺予防を図る。Q419/Q1580の「何の器具か」という知識再生ではなく、術後場面で適切な実施方法を選ぶ。
- Tag target: KN0412; task=intervention_selection; primary_ability=PRESCRIBE; secondary_ability=MEASURE; level=3; safety=none; source=original.

## Q1628 — KN0483
- Active wrong: Q491
- Source demand: `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q491 category semantics (`A-4`).
- Stem: 在胎32週で出生した乳児が、生後6か月時点で「修正月齢4か月相当」の発達課題を達成している。早産を考慮した発達評価として最も適切なのはどれか。
- Choices:
  A. 暦月齢6か月に比べて必ず2か月の発達遅滞があると判定する。
  B. 修正月齢約4か月を基準に発達を評価する。
  C. 在胎32週で出生しても修正月齢は用いない。
  D. 修正月齢は暦月齢に早産期間を加えて求める。
  E. 生後1か月を過ぎれば早産期間は発達評価に影響しない。
- Correct: B
- Rationale: 在胎32週は満期40週より約8週早く出生しているため、生後6か月では修正月齢は約4か月となる。早産児の乳幼児期の発達評価では修正月齢を考慮し、暦月齢との差だけで直ちに発達遅滞と断定しない。Q491の単純計算から、修正月齢を臨床評価にどう使うかへ需要を変える。
- Tag target: KN0483; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.

## Q1629 — KN0609
- Active wrong: Q617
- Existing weak candidates: Q1363 and canonicalized Q1225 family.
- Existing pair review: Q617/Q1363 and Q1225 are near-duplicate vitamin-K fact-recall items; do not promote them to STRONG merely by override.
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q617 clinical-category semantics unless current registry contract requires canonical grouping adjustments.
- Stem: ワルファリン内服中でこれまで安定していた患者のPT-INRが低下した。聞き取りで、最近になって納豆を毎日多量に食べ始めたことが分かった。この変化を最も適切に説明するのはどれか。
- Choices:
  A. ビタミンK摂取増加によりワルファリンの抗凝固作用が弱まった。
  B. ビタミンK摂取増加によりワルファリン作用が増強した。
  C. 納豆摂取により血小板数だけが低下した。
  D. ワルファリンはビタミンKとは無関係に作用する。
  E. PT-INR低下はワルファリン作用増強を示す。
- Correct: A
- Rationale: ワルファリンはビタミンK依存性凝固因子の合成を阻害するため、ビタミンK摂取が増えると作用が減弱しPT-INRが低下し得る。Q617/Q1363/Q1225の「拮抗するビタミンは何か」という暗記ではなく、服薬中の検査値変化と食事歴を結び付けて解釈する。実臨床では食事内容を一律禁止するのではなく、摂取量の急変を避け、処方医等と連携して管理する。
- Tag target: KN0609; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=moderate; source=original.

## Q1630 — KN0799
- Active wrong: Q807
- Source demand: `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q807 category semantics (`A-1`).
- Stem: 手掌側手関節の解剖を確認している。腱が豆状骨へ向かい、屈筋支帯の表層を走行して手根管内には入らない筋はどれか。
- Choices:
  A. 浅指屈筋
  B. 深指屈筋
  C. 長母指屈筋
  D. 尺側手根屈筋
  E. 正中神経
- Correct: D
- Rationale: 尺側手根屈筋腱は屈筋支帯の表層を走行し、豆状骨へ停止するため手根管を通過しない。浅指屈筋・深指屈筋・長母指屈筋腱と正中神経は手根管内容である。Q807の名称再生ではなく、走行と停止部の所見から該当構造を解釈する。
- Tag target: KN0799; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.

## Release constraints
- Q1-Q1625 canonical content unchanged apart from array extension / required registry-head updates.
- No reviewed STRONG-pair override solely to force a test pass.
- Verify Q1627 is STRONG vs both Q1580 and Q419 while Q419/Q1580 remain WEAK.
- Verify Q1629 is STRONG vs Q617 and every canonicalized current weak candidate used for the same concept; existing near-duplicate pairs remain WEAK.
- Full validator/focused/full pytest before manual review.
