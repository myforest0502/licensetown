# Repair Supply Phase 2 — batch6 item design v0.2

Status: manual medical/content review candidate; not yet Question Bank data.

Targets: next five remaining Priority C repairing Nodes after batch5, based on the latest Production `PHASE11_PROMOTION_EVIDENCE_V1` supplied after Q1606-Q1625 were deployed to main. Proposed IDs assume main ends at Q1630; Codex must reconfirm before writing.

Design rule: same canonical Knowledge Node, materially different demand from the active-wrong source. Structural `different_question_strong` is necessary but not sufficient. Do not add reviewed STRONG-pair overrides merely to force classification.

## Q1631 — KN0811
- Active wrong: Q820
- Source demand: `fact_recall / KNOW`
- Existing concept: the hypothalamus integrates peripheral/central temperature information and coordinates sweating, vascular responses and shivering.
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q820 category semantics (`A-2`), source original.
- Stem: 暑熱環境で深部体温が上昇した人に、発汗と皮膚血管拡張が協調して起こっている。皮膚と中枢の温度情報を統合し、このような熱放散反応を調節する部位はどれか。
- Choices:
  A. 小脳虫部
  B. 扁桃体
  C. 視床下部
  D. 補足運動野
  E. 中脳水道周囲灰白質
- Correct: C
- Rationale: 視床下部は末梢・中枢の温度情報を統合し、体温上昇時の発汗や皮膚血管拡張、低温時のふるえなどを協調させる。Q820の「中枢名を直接答える」知識再生から、生理反応の組合せを手掛かりに調節中枢を解釈する需要へ変える。
- Tag target: KN0811; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.

## Q1632 — KN0894
- Active wrong: Q903
- Source demand: `fact_recall / KNOW`
- Existing concept: Eriksonの成人中期は生殖性（世代性）対停滞。
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q903 category semantics (`A-3`), source original.
- Stem: 45歳の会社員。若手職員の育成に力を入れ、地域では次世代のための活動にも継続して参加している。Eriksonの心理社会的発達理論で、この行動が最も表している成人中期の課題はどれか。
- Choices:
  A. 自我同一性
  B. 親密性
  C. 生殖性〈世代性〉
  D. 勤勉性
  E. 自我の統合
- Correct: C
- Rationale: 成人中期では次世代の育成や社会への貢献に関わる生殖性（世代性）対停滞が中心課題となる。Q903の段階名の直接再生ではなく、具体的な行動から発達課題を解釈する。
- Tag target: KN0894; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.

## Q1633 — KN1044
- Active wrong: Q1054
- Source demand: `intervention_selection / PRESCRIBE` (official multi-select)
- Existing concept: 歩行導入初期には反復、ハンドリング、適切なフィードバックを用いて運動学習を支援する。
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1054 category semantics (`C-13`), source original.
- Stem: 歩行練習を開始したばかりの患者に対し、理学療法士は踵接地を短い試行で繰り返し、必要に応じて下肢をハンドリングし、動作直後に具体的なフィードバックを与えている。この介入のねらいとして最も適切なのはどれか。
- Choices:
  A. 初期の運動学習を反復・誘導・フィードバックで支援する。
  B. 疲労を最大化して筋肥大だけを促進する。
  C. 歩行課題を避けて認知課題だけで代替する。
  D. 誤差情報を完全に遮断して偶然の成功だけを待つ。
  E. 学習初期から一切の外的手掛かりを禁止する。
- Correct: A
- Rationale: 新しい歩行パターンの獲得初期では、課題反復、必要なハンドリング、理解しやすいフィードバックが運動学習を支える。Q1054で個別手段を選ぶ需要から、実際の介入セットが何を狙っているかを解釈する需要へ変える。フィードバックは学習の進行に応じて量や頻度を調整し、恒久的依存を作ることが目的ではない。
- Tag target: KN1044; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=PRESCRIBE; level=3; safety=none; source=original.

## Q1634 — KN1047
- Active wrong: Q1057
- Source demand: `fact_recall / KNOW`
- Existing concept: 振戦は規則的・律動的な不随意運動。
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1057 category semantics (`C-18`), source original.
- Stem: 安静時に手指が一定の周期で反復して揺れ、観察すると規則的・律動的な往復運動を示している。この不随意運動として最も適切なのはどれか。
- Choices:
  A. チック
  B. バリスム
  C. アテトーゼ
  D. 振戦
  E. ミオクローヌス
- Correct: D
- Rationale: 振戦は比較的規則的・律動的な反復運動として観察される。チック、バリスム、アテトーゼ、ミオクローヌスは運動の時間的・形態的特徴が異なる。Q1057の定義再生から、観察所見をもとに不随意運動を分類する需要へ変える。
- Tag target: KN1047; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.

## Q1635 — KN1078
- Active wrong: Q1089
- Source demand: `fact_recall / KNOW` (official answer accepts 3 and 5)
- Existing concept: 手関節橈屈に作用・補助する筋。
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1089 category semantics (`C-13`), source original.
- Stem: 母指CM関節の外転運動を行わせると、同時に手関節を橈屈方向へ補助する作用も期待できる筋はどれか。
- Choices:
  A. 尺側手根屈筋
  B. 尺側手根伸筋
  C. 長母指外転筋
  D. 深指屈筋
  E. 円回内筋
- Correct: C
- Rationale: 長母指外転筋は母指CM関節の外転・伸展に作用し、その走行から手関節橈屈を補助する。Q1089の公式複数正答をそのまま再生するのではなく、母指運動と手関節作用を組み合わせて該当筋を解釈する。主な手関節橈屈筋が橈側手根屈筋・長短橈側手根伸筋であることとは区別する。
- Tag target: KN1078; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.

## Release constraints
- Q1-Q1630 canonical questions/answers/explanations/tags remain unchanged apart from array extension and required registry/head updates.
- No reviewed STRONG-pair override solely to force a test pass.
- Verify Q1631 STRONG vs Q820.
- Verify Q1632 STRONG vs Q903.
- Verify Q1633 STRONG vs Q1054.
- Verify Q1634 STRONG vs Q1057.
- Verify Q1635 STRONG vs Q1089, while preserving Q1089's existing official accepted answer semantics unchanged.
- Full validator/focused/full pytest before manual review.
