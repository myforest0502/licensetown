# Repair Supply Phase 2 — batch3 item design v0.2

Status: **manual medical/content review candidate; not Question Bank data.**

Target: the next five Priority B repairing Nodes from the Production repair-supply bundle after batch2. Proposed IDs assume main ends at Q1615 when implementation starts; reconfirm before writing.

Design rule: each new question must assess the same canonical Knowledge Node through a materially different demand from the learner's active-wrong source question. Structural `different_question_strong` is necessary but not sufficient; stems and distractors must preserve educational independence.

---

## Q1616 — KN1186

- Priority evidence: tier B; active wrong Q1200; cycle_wrong=3; confident_wrong=2
- Source demand: Q1200 `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management: `Q1616-A-1-O`
- Title: 手の筋・機能解剖

**Stem**

手関節背側を超音波で観察したところ、筋腹は前腕にあり、その腱が手関節を越えて母指基節骨へ向かって走行していた。この筋を「手の外来筋」と判断する根拠として最も適切なのはどれか。

**Choices**

A. 手指に停止する筋はすべて手内在筋だから。
B. 筋腹が前腕にあり、腱が手へ入って作用する筋だから。
C. 母指に作用する筋はすべて母指球筋だから。
D. 手関節を越える腱をもつ筋はすべて虫様筋だから。
E. 手の外来筋は手掌内に筋腹をもつ筋だから。

**Correct:** B

**Rationale:** 手の外来筋は筋腹が前腕側にあり、腱が手へ入って手指に作用する筋群である。短母指伸筋などはその代表である。停止部が手にあることだけで内在筋になるわけではなく、筋腹が手内にある母指球筋・小指球筋・骨間筋などとは区別される。Q1200の筋名暗記ではなく、観察された筋腹と腱走行から外来筋の定義を解釈する。

**Choice explanations**

- A: 停止部が手にあっても、筋腹が前腕にある外来筋は存在する。
- B: 正しい。前腕の筋腹から腱が手へ入り作用することが外来筋の基本的特徴である。
- C: 母指に作用しても長母指屈筋・長母指伸筋・短母指伸筋などは外来筋である。
- D: 虫様筋の筋腹は手内にあり、前腕から手関節を越えてくる筋ではない。
- E: 手掌内に筋腹をもつ筋は内在筋として整理される。

**Tag:** theme=`前腕の筋腹と手へ入る腱走行から手外来筋を解釈する`; knowledge_node=`手の外来筋は前腕から起こり腱が手に入る筋`; knowledge_node_id=`KN1186`; task=`finding_interpretation`; primary_ability=`INTERPRET`; secondary_ability=`KNOW`; level=3; safety=`none`; prerequisites=`手外来筋`,`手内在筋`,`筋腹`,`腱走行`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1617 — KN0611

- Priority evidence: tier B; active wrong Q619; cycle_wrong=2; confident_wrong=2
- Source demand: Q619 `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management: `Q1617-A-3-O`
- Title: 記憶・学習

**Stem**

健忘症患者に毎日同じ鏡映描写課題を行った。患者は前日に練習したこと自体を思い出せないが、数日後には課題の所要時間と誤り数が明らかに減少した。この所見から最も考えられるのはどれか。

**Choices**

A. エピソード記憶が正常に形成されている。
B. 意味記憶だけが新たに形成されている。
C. 手続き記憶による技能学習が保たれている。
D. 即時記憶の保持時間だけが延長している。
E. 見当識が改善したため課題成績が上がっている。

**Correct:** C

**Rationale:** 手続き記憶は技能や習慣の学習に関わる非陳述記憶で、学習エピソードを意識的に想起できなくても成績改善として現れることがある。鏡映描写で「練習した記憶はないが技能成績が改善する」という乖離は、手続き記憶が保たれている典型的な所見である。Q619の用語再生ではなく、行動所見から記憶システムを解釈する。

**Choice explanations**

- A: 前日の練習を思い出せないため、エピソード記憶の正常形成を示す所見ではない。
- B: 本問は知識の獲得ではなく、反復による技能成績の改善を示している。
- C: 正しい。意識的想起なしに技能が改善しており、手続き記憶の特徴に合う。
- D: 数日間にわたる技能改善を即時記憶だけでは説明できない。
- E: 見当識改善の情報はなく、技能学習の所見を直接説明しない。

**Tag:** theme=`想起できない反復課題の成績改善から手続き記憶を解釈する`; knowledge_node=`意識せずに技能や習慣として再生される記憶は手続き記憶で、非陳述記憶に分類される`; knowledge_node_id=`KN0611`; task=`finding_interpretation`; primary_ability=`INTERPRET`; secondary_ability=`KNOW`; level=3; safety=`none`; prerequisites=`手続き記憶`,`非陳述記憶`,`エピソード記憶`,`技能学習`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1618 — KN0714

- Priority evidence: tier B; active wrong Q722; cycle_wrong=2; confident_wrong=2
- Source demand: Q722 `assessment_selection / MEASURE`
- New demand: `finding_interpretation / INTERPRET`
- Management: `Q1618-C-17-O`
- Title: 理学療法評価・疼痛

**Stem**

腰痛患者の疼痛強度を100 mmのVASで評価した。初回は左端から76 mm、1週間後は34 mmの位置に印を付けた。他の評価所見は提示されていない。この結果から最も適切に言えるのはどれか。

**Choices**

A. 疼痛の原因となる組織が特定できた。
B. VAS上の自己申告による疼痛強度は42 mm低下した。
C. 日常生活動作能力が42％改善した。
D. 痛みは完全に消失した。
E. 筋緊張の程度が42 mm低下した。

**Correct:** B

**Rationale:** VASは本人が感じる疼痛強度を線上の位置で表す尺度であり、76 mmから34 mmへの変化はVAS上42 mmの低下である。VAS単独から疼痛の病因、ADL改善率、筋緊張などを直接推定することはできない。Q722で「VASを選ぶ」ことから一段進み、得られた尺度値が何を意味し、何を意味しないかを解釈する。

**Choice explanations**

- A: VASは疼痛強度を測るが、病因組織を同定する検査ではない。
- B: 正しい。76 mmから34 mmなので、自己申告疼痛強度はVAS上42 mm低下している。
- C: VASのmm変化をADL改善率へ直接換算できない。
- D: 34 mmの疼痛が残っており、完全消失ではない。
- E: VASは筋緊張尺度ではない。

**Tag:** theme=`VASの前後値から疼痛強度変化を解釈する`; knowledge_node=`疼痛強度の評価には表情図から選ぶface scaleと、線上の位置で強度を示すVASが用いられる`; knowledge_node_id=`KN0714`; task=`finding_interpretation`; primary_ability=`INTERPRET`; secondary_ability=`MEASURE`; level=3; safety=`none`; prerequisites=`VAS`,`疼痛強度`,`尺度値`,`前後比較`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1619 — KN0725

- Priority evidence: tier B; active wrong Q733; existing canonicalized weak candidate Q949; cycle_wrong=2; confident_wrong=2
- Existing demands: Q733/Q949 are near-duplicate `fact_recall / KNOW` pair and remain WEAK
- New demand: `finding_interpretation / INTERPRET`
- Management: `Q1619-A-1-O`
- Title: 神経解剖・外眼筋

**Stem**

眼球運動を評価したところ、内転位にした右眼を下方へ動かす運動が弱く、読書や階段を下りるときに垂直方向の複視が強くなる。この所見を最も直接説明する筋と支配神経の組合せはどれか。

**Choices**

A. 右上斜筋 ― 滑車神経
B. 右下斜筋 ― 動眼神経
C. 右外直筋 ― 外転神経
D. 右上直筋 ― 動眼神経
E. 右内直筋 ― 動眼神経

**Correct:** A

**Rationale:** 上斜筋は内転位の眼球を下制する作用が重要で、滑車神経に支配される。上斜筋または滑車神経の障害では下方視、とくに読書や階段下降などで垂直性複視が目立ちやすい。Q733/Q949の筋―神経ペア暗記ではなく、眼球運動所見から該当する筋・神経を解釈する。

**Choice explanations**

- A: 正しい。内転位での下制低下と下方視時の複視は上斜筋―滑車神経の障害に合う。
- B: 下斜筋は動眼神経支配だが、主に内転位で眼球を挙上する。
- C: 外直筋は外転神経支配で、主作用は外転である。
- D: 上直筋は動眼神経支配で、主に挙上へ関与する。
- E: 内直筋は動眼神経支配で、主作用は内転である。

**Tag:** theme=`内転位での下制障害から上斜筋と滑車神経を解釈する`; knowledge_node=`上斜筋は滑車神経支配である`; knowledge_node_id=`KN0725`; task=`finding_interpretation`; primary_ability=`INTERPRET`; secondary_ability=`KNOW`; level=3; safety=`none`; prerequisites=`上斜筋`,`滑車神経`,`内転位`,`下制`,`垂直性複視`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1620 — KN1281

- Priority evidence: tier B; active wrong Q1297; cycle_wrong=2; confident_wrong=2
- Source demand: Q1297 `fact_recall / KNOW`
- New demand: `assessment_selection / MEASURE`
- Management: `Q1620-A-3-O`
- Title: 認知・記憶評価

**Stem**

患者は簡単な計算知識や数の意味は理解しているが、「聞いた数字を頭の中に保ちながら並べ替える課題」や暗算でつまずく。ワーキングメモリーの弱さをより直接確認する追加課題として最も適切なのはどれか。

**Choices**

A. 昔の旅行について自由に想起してもらう。
B. 一般常識に関する語句の意味を答えてもらう。
C. 数字列を聞かせ、逆順に再生してもらう。
D. 自転車の乗り方を実演してもらう。
E. 直前に見た図形をそのまま模写してもらう。

**Correct:** C

**Rationale:** ワーキングメモリーは情報を一時的に保持しながら操作する機能であり、数字の逆唱は保持した情報を並べ替えて出力する必要があるため、その負荷を直接かける代表的課題である。自由再生はエピソード記憶、語の意味は意味記憶、技能実演は手続き記憶を主に反映し、単純模写は同じ保持・操作要求ではない。Q1297の「暗算＝ワーキングメモリー」という対応暗記から、評価課題の選択へ需要を変える。

**Choice explanations**

- A: 過去体験の自由想起はエピソード記憶を主に評価する。
- B: 語句の意味は意味記憶の側面をみる。
- C: 正しい。数字逆唱は一時保持した情報を操作して再生するワーキングメモリー課題である。
- D: 習得技能の実演は手続き記憶を反映する。
- E: 単純模写は視空間・構成能力をみるが、本問で疑う保持しながら操作する能力を直接問わない。

**Tag:** theme=`数字逆唱を用いたワーキングメモリー評価`; knowledge_node=`紙や鉛筆を使わず暗算するには、数値を一時保持しながら操作するワーキングメモリーが必要である`; knowledge_node_id=`KN1281`; task=`assessment_selection`; primary_ability=`MEASURE`; secondary_ability=`KNOW`; level=3; safety=`none`; prerequisites=`ワーキングメモリー`,`数字逆唱`,`一時保持`,`情報操作`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Batch3 expected formal mapping

| New Q | Node | Active-wrong / weak comparison | New demand | Key |
|---|---|---|---|---|
| Q1616 | KN1186 | Q1200 | finding_interpretation / INTERPRET | B |
| Q1617 | KN0611 | Q619 | finding_interpretation / INTERPRET | C |
| Q1618 | KN0714 | Q722 | finding_interpretation / INTERPRET | B |
| Q1619 | KN0725 | Q733 + canonicalized Q949 | finding_interpretation / INTERPRET | A |
| Q1620 | KN1281 | Q1297 | assessment_selection / MEASURE | C |

Release gate: implementation must not be merged until the actual canonical records receive manual medical/content review and executable STRONG checks pass against every listed active-wrong source. Existing Q733/Q949 remains WEAK; do not add an override to relabel that pair.
