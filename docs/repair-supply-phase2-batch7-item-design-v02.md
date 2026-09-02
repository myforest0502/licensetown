# Repair Supply Phase 2 — batch7 item design v0.2

Status: manual medical/content review candidate; not yet Question Bank data.

Targets: next five remaining Priority C repairing Nodes after Q1631-Q1635. Proposed IDs assume main ends at Q1635; Codex must reconfirm before writing.

Design rule: preserve the same canonical Knowledge Node while changing the cognitive demand materially from the active-wrong source. Structural `different_question_strong` is necessary but not sufficient. Do not add reviewed STRONG-pair overrides simply to force a passing classification.

## Q1636 — KN1100
- Active wrong: Q1111
- Source demand: `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1111 category semantics; source original.
- Stem: 78歳。就寝前にベンゾジアゼピン系睡眠薬を開始した翌朝から、眠気が残り、立ち上がり時にふらついて歩行が不安定になった。新たな片麻痺や感覚障害はない。この所見を最も適切に説明するのはどれか。
- Choices:
  A. 筋弛緩作用や持ち越し効果による運動失調・ふらつき
  B. 錐体外路症状による固縮だけが出現した
  C. 末梢神経の急性脱髄により左右対称の麻痺が生じた
  D. 小脳梗塞を示すため睡眠薬とは無関係である
  E. 薬剤によって筋力が恒久的に増加した
- Correct: A
- Rationale: ベンゾジアゼピン系睡眠薬では筋弛緩作用、鎮静の持ち越し、ふらつき・運動失調などに注意する。Q1111の副作用名称の直接再生ではなく、服薬開始後の時間関係と歩行所見から薬剤関連の機序を解釈する。高齢者では転倒リスクにも注意し、実臨床で薬剤調整を自己判断させる設問にはしない。
- Tag target: KN1100; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3. Codex must inspect the current source safety/category contract and preserve it unless repository policy explicitly requires a different value.

## Q1637 — KN1143
- Active wrong: Q1156
- Source demand: `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1156 category semantics; source original.
- Stem: 上肢挙上時に肩甲骨の上方回旋が不十分で、前鋸筋の活動低下が確認された。正常な上方回旋を作るために前鋸筋と協働する筋として最も適切なのはどれか。
- Choices:
  A. 僧帽筋
  B. 菱形筋
  C. 肩甲挙筋
  D. 広背筋
  E. 大胸筋
- Correct: A
- Rationale: 前鋸筋は僧帽筋上部・下部などと協働して肩甲骨の上方回旋を形成し、上肢挙上を支える。Q1156の「上方回旋筋はどれか」という単独名称再生から、観察された機能低下を力のカップルとして解釈する需要へ変える。
- Tag target: KN1143; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; source=original. Preserve source safety/category semantics.

## Q1638 — KN1149
- Active wrong: Q1162
- Source demand: `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1162 category semantics; source original.
- Stem: 下肢深部静脈血栓症の患者が突然の呼吸困難と胸痛を訴え、低酸素血症を認めた。血栓が遊離した場合の経路と病態の組合せとして最も適切なのはどれか。
- Choices:
  A. 下大静脈→右心系→肺動脈に到達し、肺塞栓症を起こす
  B. 下大静脈→左心系→冠動脈に直接到達し、心筋梗塞を起こす
  C. 門脈→肝静脈にのみ到達し、肺循環には入らない
  D. 下大静脈→頸動脈へ直接移動し、脳梗塞だけを起こす
  E. 下大静脈→腎動脈へ直接移動し、腎梗塞だけを起こす
- Correct: A
- Rationale: 下肢DVTから遊離した血栓は下大静脈、右房、右室を経て肺動脈へ到達し、肺塞栓症を起こし得る。Q1162の「塞栓先の臓器」を直接答える問題から、急性症状と循環経路を統合して病態を解釈する需要へ変える。設問は診断・治療指示ではなく病態理解を問う。
- Tag target: KN1149; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; source=original. Codex must inspect current safety policy; do not silently broaden selector behavior merely by changing safety tagging.

## Q1639 — KN1265
- Active wrong: Q1281
- Source demand: `fact_recall / KNOW` (official two-answer item)
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1281 category semantics; source original.
- Stem: 生後10か月。初対面の人を見ると養育者にしがみつき、食事では両手でコップを持って飲もうとする。この2つの行動の解釈として最も適切なのはどれか。
- Choices:
  A. いずれも生後12か月以前にみられ得る発達行動である
  B. どちらも2歳以降に初めて出現する行動である
  C. 人見知りは異常所見であり正常発達ではみられない
  D. コップを持つ行動は学童期まで出現しない
  E. この2所見だけで発達遅滞と確定できる
- Correct: A
- Rationale: 人見知りや、自分でコップを持って飲もうとする行動は12か月以前にも観察され得る。Q1281で個々の項目を2つ選ぶ直接再生から、実際に観察された複数行動を月齢との関係で解釈する需要へ変える。2所見のみで発達遅滞を確定しない。
- Tag target: KN1265; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; source=original. Preserve Q1281 official answer contract unchanged.

## Q1640 — KN1321
- Active wrong: Q1341
- Source demand: `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1341 category semantics; source original.
- Stem: 視覚的に手の軌道をずらす外乱を加えて到達運動を反復すると、次第に誤差が小さくなった。外乱を突然外すと反対方向へのafter-effectが生じた。この学習を最もよく説明する機序はどれか。
- Choices:
  A. 小脳が予測誤差を利用して内部モデルを更新した
  B. 視床下部が体温調節反応を学習した
  C. 扁桃体が情動記憶だけを形成した
  D. 脊髄反射だけで外乱の予測モデルを形成した
  E. 末梢筋の肥大だけで軌道誤差が消失した
- Correct: A
- Rationale: 運動適応とafter-effectは、予測誤差を基に内部モデルが更新されたことを示す代表的な所見であり、小脳が重要な役割を担う。Q1341の「内部モデル形成に重要な中枢」を直接再生する問題から、適応現象を手掛かりに内部モデル更新機序を解釈する需要へ変える。
- Tag target: KN1321; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; source=original. Preserve source safety/category semantics.

## Release constraints
- Q1-Q1635 canonical content unchanged apart from array extension / required registry-head updates.
- Preserve Q1111 and Q1281 existing official accepted-answer contracts unchanged.
- No reviewed STRONG-pair override solely to force a test pass.
- Verify Q1636-Q1640 classify `different_question_strong` against Q1111/Q1156/Q1162/Q1281/Q1341 respectively.
- Full validator/focused/full pytest before manual review.
