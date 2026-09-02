# Repair Supply Phase 2 — batch8 item design v0.2

Status: manual medical/content review candidate; not yet Question Bank data.

Targets: the three remaining Priority C repair-supply targets visible in the latest Production evidence after batch7, followed by the two highest Priority D targets. Proposed IDs assume main ends at Q1640; Codex must reconfirm before writing.

Design rule: same canonical Knowledge Node, materially different demand from the active-wrong source. Existing weak/canonicalized families stay WEAK unless independently reviewed. Structural `different_question_strong` is necessary but not sufficient.

## Q1641 — KN1337
- Active wrong: Q1358
- Canonicalized weak-family candidates: Q954, Q1535
- Source demand: fact recall / KNOW
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit the active-wrong Q1358 clinical-category semantics unless the current registry contract requires canonical grouping adjustments.
- Stem: 回転椅子を静止状態から急に回し始めると眼振が誘発されたが、一定速度で回転を続けると反応は次第に弱くなった。この現象に最も直接関与する受容器と刺激の組合せはどれか。
- Choices:
  A. 蝸牛のコルチ器 ― 直線加速度
  B. 卵形囊斑 ― 角加速度
  C. 半規管の膨大部稜 ― 角加速度
  D. 球形囊斑 ― 音圧
  E. 鼓膜 ― 頭部回転速度
- Correct: C
- Rationale: 半規管では回転開始・停止などの角加速度で内リンパの相対的な流れが生じ、クプラが偏位して膨大部稜の有毛細胞が刺激される。一定角速度が続くと内リンパが追従し、刺激は弱くなる。Q954/Q1358/Q1535の「半規管は角加速度」「受容器は膨大部稜」という直接再生から、回転刺激時の生理現象を解釈する需要へ変える。
- Tag target: KN1337; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.

## Q1642 — KN1494
- Active wrong: Q1519
- Source demand: `assessment_selection / MEASURE`
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1519 category semantics (`C-17`).
- Stem: 高齢者が基本チェックリストの「週に1回以上は外出していますか」に「いいえ」と回答した。この回答の解釈として最も適切なのはどれか。
- Choices:
  A. 閉じこもりに関するリスクを示す回答として扱う。
  B. 栄養改善項目だけの異常を示す。
  C. 口腔機能項目だけの異常を示す。
  D. 認知症を確定診断できる回答である。
  E. 基本チェックリストでは外出頻度を扱わない。
- Correct: A
- Rationale: 基本チェックリストには外出頻度など閉じこもりに関連する質問が含まれる。「週に1回以上は外出していますか」への「いいえ」は閉じこもりリスクをみる回答として解釈する。これだけで認知症などを確定診断するものではない。Q1519の制度・実施形式に関する選択から、実際の回答を領域別に解釈する需要へ変える。
- Tag target: KN1494; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=MEASURE; level=3; safety=none; source=original.
- Preserve Q1519 official accepted-answer contract unchanged.

## Q1643 — KN1514
- Active wrong: Q1540
- Source demand: fact recall / KNOW
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1540 category semantics (`A-1`).
- Stem: 射精時に精液が膀胱内へ逆流する病態を考える。正常では、この逆流を防ぐために射精時に起こる反応として最も適切なのはどれか。
- Choices:
  A. 副交感神経活動による膀胱排尿筋の強い収縮
  B. 交感神経活動による膀胱頸部〈内尿道括約筋〉の収縮
  C. 陰部神経遮断による外尿道括約筋の完全弛緩だけ
  D. 迷走神経活動による精管の弛緩
  E. 体性神経活動による膀胱頸部の開大
- Correct: B
- Rationale: 射精では主に交感神経活動により精管・精囊・前立腺などが収縮し、同時に膀胱頸部（内尿道括約筋）が閉鎖して精液の膀胱内逆流を防ぐ。Q1540の正しい生殖器知識を直接選ぶ需要から、逆行性射精の機序を正常生理と結び付けて解釈する需要へ変える。
- Tag target: KN1514; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.
- Preserve Q1540 official accepted-answer contract unchanged.

## Q1644 — KN1080
- Active wrong: Q1091 and canonicalized Q1544 family
- Source demand: fact recall / KNOW
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1091 category semantics (`C-13`) unless the current registry contract requires canonical grouping adjustments.
- Stem: 階段をゆっくり下りる際、支持脚の膝は徐々に屈曲しているが、大腿四頭筋は身体が急に落下しないよう張力を発揮して制動している。このときの大腿四頭筋の状態として最も適切なのはどれか。
- Choices:
  A. 筋が短縮しながら張力を発揮する求心性収縮
  B. 筋長を一定に保ったまま張力を発揮する等尺性収縮
  C. 筋が伸張されながら張力を発揮する遠心性収縮
  D. 筋活動を伴わない受動的伸張
  E. 筋が短縮も伸張もせず弛緩している状態
- Correct: C
- Rationale: 階段下降で膝屈曲を制動する大腿四頭筋は、張力を発揮しながら筋長が伸びるため遠心性収縮である。Q1091/Q1544の具体例から遠心性収縮を選ぶ問題とは逆に、動作中の筋長変化と張力の関係を読み取って収縮様式を解釈する。
- Tag target: KN1080; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.
- Existing Q1091/Q1544-family semantics must not be modified merely to force STRONG classification.

## Q1645 — KN1224
- Active wrong: Q1239
- Source demand: fact recall / KNOW
- New demand: `finding_interpretation / INTERPRET`
- Management target: inherit Q1239 category semantics (`C-15`).
- Stem: 右下肢の歩行周期を観察している。左足が床から離れた直後から、左足が再び床に接地する直前まで、右足だけが床に接していた。この単脚支持期間に含まれる右下肢の歩行相の組合せはどれか。
- Choices:
  A. 初期接地と荷重応答期
  B. 荷重応答期と立脚中期
  C. 立脚中期と立脚終期
  D. 立脚終期と前遊脚期
  E. 前遊脚期と遊脚初期
- Correct: C
- Rationale: 正常歩行の単脚支持は、反対側下肢のtoe-off後から反対側のinitial contactまでで、観察側では立脚中期から立脚終期に相当する。荷重応答期と前遊脚期は両脚支持を含む。Q1239の歩行相名称の直接選択から、両脚の接地状況をもとに歩行相を解釈する需要へ変える。
- Tag target: KN1224; task=finding_interpretation; primary_ability=INTERPRET; secondary_ability=KNOW; level=3; safety=none; source=original.
- Preserve Q1239 official accepted-answer contract unchanged.

## Release constraints
- Reconfirm current main ends at Q1640 before assigning Q1641-Q1645.
- Q1-Q1640 canonical content unchanged apart from array extension / required registry-head updates.
- No reviewed STRONG-pair override solely to force a test pass.
- Q1641 must be STRONG vs Q1358 and every current canonicalized weak-family candidate for the same concept (including Q954/Q1535 if the current registry still maps them into the canonical family); the old near-duplicate family remains WEAK.
- Q1642 must be STRONG vs Q1519; Q1519 official accepted-answer contract unchanged.
- Q1643 must be STRONG vs Q1540; Q1540 official accepted-answer contract unchanged.
- Q1644 must be STRONG vs Q1091 and canonicalized Q1544 if still in the same family; old family semantics remain unchanged.
- Q1645 must be STRONG vs Q1239; Q1239 official accepted-answer contract unchanged.
- Full validator/focused/full pytest before manual review.
