# Repair Supply Phase 2 — batch2 item design v0.2

Status: **manual medical/content review candidate; not Question Bank data.**

This revision hardens biomechanics wording and distractors after source review. Proposed IDs assume the formal Question Bank head remains Q1610 when implementation starts; reconfirm immediately before writing data.

The design principle is the same as batch1: a new item must test the same canonical Knowledge Node through a materially different demand, not merely repeat the learner's failed fact in different wording.

---

## Q1611 — KN1399

- Priority evidence: tier B; active wrong Q1424; cycle_wrong=4; confident_wrong=4
- Existing demand: Q1424 `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management: `Q1611-C-13-O`
- Title: 基礎運動学・立位姿勢

**Stem**

成人の安静立位を矢状面から観察した。身体重心から鉛直に下ろした重力線が膝関節中心より後方を通り、立位保持中の大腿四頭筋活動が増えている。この所見の力学的解釈として最も適切なのはどれか。

**Choices**

A. 膝関節に外的伸展モーメントが増え、大腿四頭筋活動は不要になる。
B. 膝関節に外的屈曲モーメントが生じやすく、その制御に大腿四頭筋活動が必要になる。
C. 股関節の外的内転モーメントだけが増え、膝関節の筋活動とは無関係である。
D. 重力線が膝関節中心より後方にあるほど、靱帯性支持だけで安定しやすくなる。
E. 矢状面の重力線位置は膝関節まわりの外的モーメントに影響しない。

**Correct:** B

**Rationale:** 通常の安静立位では身体重心から鉛直に下ろした重力線は膝関節中心のわずか前方を通り、重力による小さな膝伸展方向のモーメントが生じる。重力線が膝関節中心より後方へ移れば外的屈曲モーメントが生じ、膝折れを防ぐため大腿四頭筋による伸展方向の制御が必要になる。Q1424の「通常位置」を再生するだけではなく、位置が逆転した所見から関節モーメントと筋活動を解釈する。

**Choice explanations**

- A: 後方を通る場合は外的屈曲方向であり、説明が逆である。
- B: 正しい。重力線の後方化と増えた大腿四頭筋活動を同じ力学で説明できる。
- C: 提示所見は矢状面で膝関節中心との前後関係を示している。
- D: 外的屈曲モーメントが生じるため、筋活動増加という所見とも矛盾する。
- E: 重力線と関節中心の位置関係は外的モーメントの方向を左右する。

**Tag:** theme=`膝関節中心に対する重力線位置と外的モーメント`; knowledge_node=`安静立位では重心線が膝関節中心のやや前方を通ることで少ない筋活動で安定する`; knowledge_node_id=`KN1399`; task=`finding_interpretation`; primary_ability=`INTERPRET`; secondary_ability=`KNOW`; level=3; safety=`none`; prerequisites=`重力線`,`膝関節中心`,`外的屈曲モーメント`,`大腿四頭筋`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1612 — KN1151

- Priority evidence: tier B; active wrong Q1164/Q1221; cycle_wrong=4; confident_wrong=2
- Existing demand: both sources `fact_recall / KNOW`
- New demand: `finding_interpretation / INTERPRET`
- Management: `Q1612-A-3-O`
- Title: 心理・障害受容

**Stem**

障害受容を「ショック、否認、混乱、解決への努力、受容」の5段階で整理するモデルを用いる。脊髄損傷後の患者は、受傷直後の茫然とした時期や「元どおりになるはずだ」と現実を認めにくい時期、気持ちの揺れが強い時期を経て、最近は「今の身体で仕事に戻る方法を考えたい」と福祉用具や職業復帰について具体的に相談している。現在の段階として最も当てはまるのはどれか。

**Choices**

A. ショック期
B. 否認期
C. 混乱期
D. 解決への努力期
E. 受容期

**Correct:** D

**Rationale:** この5段階モデルでは、ショック、否認、混乱を経た後、現状を前提に具体的な生活・職業上の方法を探し始める段階を「解決への努力」と整理する。実際の心理過程は個人差が大きく必ず直線的に進むものではないが、本問は提示された5段階モデル内での場面解釈を問う。

**Choice explanations**

- A: 受傷直後の茫然とした状態に対応する。
- B: 障害の現実を認めにくい時期であり、具体的適応策を探す現在像とは異なる。
- C: 感情的な揺れや葛藤が前景となる段階で、提示場面は具体策の探索へ進んでいる。
- D: 正しい。現状を前提に生活・職業上の解決策を具体的に探している。
- E: モデル上の最終段階であり、本問ではその前段階の積極的な解決策探索が前景となっている。

**Tag:** theme=`障害受容5段階モデルにおける解決への努力期の場面解釈`; knowledge_node=`障害受容の5段階はショック、否認、混乱、解決への努力、受容の順`; knowledge_node_id=`KN1151`; task=`finding_interpretation`; primary_ability=`INTERPRET`; secondary_ability=`KNOW`; level=2; safety=`none`; prerequisites=`ショック`,`否認`,`混乱`,`解決への努力`,`受容`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1613 — KN1256

- Priority evidence: tier B; active wrong Q1272; existing weak candidate Q1457; cycle_wrong=4; confident_wrong=2
- Existing demands: Q1272 and canonicalized Q1457 are near-duplicate `fact_recall / KNOW` items and remain WEAK as a repair pair
- New demand: `finding_interpretation / INTERPRET`
- Management: `Q1613-C-13-O`
- Title: 基礎運動学・立位姿勢

**Stem**

安静立位を矢状面から解析したところ、身体重心から鉛直に下ろした重力線が足関節中心（外果付近）より後方を通っていた。重力が足関節中心まわりに生じさせる外的モーメントと、それに拮抗する筋活動の組合せとして最も適切なのはどれか。

**Choices**

A. 背屈モーメント ― 足関節底屈筋
B. 底屈モーメント ― 足関節背屈筋
C. 内反モーメント ― 足関節外反筋
D. 外反モーメント ― 足関節内反筋
E. 膝伸展モーメント ― 大腿四頭筋

**Correct:** B

**Rationale:** 通常の安静立位では身体重心から鉛直に下ろした重力線は足関節中心より前方を通り、重力は身体を前方へ倒す方向、すなわち足関節には外的背屈方向の作用を生じ、底屈筋群がこれに抗する。重力線が足関節中心より後方へ移れば作用方向は逆転して外的底屈モーメントとなるため、それに拮抗するのは背屈筋群である。単なる「外果前方」という位置の再生ではなく、前後関係の変化からモーメントを解釈する。

**Choice explanations**

- A: 重力線が足関節中心より前方にある通常の関係に対応する。
- B: 正しい。重力線が後方なら外的底屈方向となり、背屈筋が拮抗する。
- C: 矢状面の前後位置から内反モーメントは導かれない。
- D: 同様に外反モーメントを問う所見ではない。
- E: 問われている回転中心は足関節である。

**Tag:** theme=`外果に対する重力線位置から足関節外的モーメントを解釈する`; knowledge_node=`矢状面の重心線は耳垂付近、肩峰付近、大転子や膝関節のやや前方、外果のやや前方を通る`; knowledge_node_id=`KN1256`; task=`finding_interpretation`; primary_ability=`INTERPRET`; secondary_ability=`KNOW`; level=3; safety=`none`; prerequisites=`重力線`,`外果`,`足関節中心`,`外的モーメント`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1614 — KN1263

- Priority evidence: tier B; active wrong Q1279; cycle_wrong=4; confident_wrong=2
- Existing demand: Q1279 `fact_recall / KNOW`
- New demand: `intervention_selection / PRESCRIBE`
- Management: `Q1614-B-8-O`
- Title: 脊髄損傷・上肢機能

**Stem**

第6頸髄節まで機能が残存する完全頸髄損傷患者。手関節背屈は可能だが、手指の随意的な屈曲は困難である。残存機能を利用して物品把持を獲得するための訓練として最も適切なのはどれか。

**Choices**

A. 手関節背屈に伴う受動的な手指屈曲を利用し、テノデーシス把持を反復練習する。
B. 小指外転筋の抵抗運動を優先し、手関節背屈は使わない。
C. 中指DIP関節の随意屈曲を最大抵抗で反復する。
D. 手関節を掌屈位に保ちながら手指屈筋を強く伸張し、受動的な手指屈曲が生じないようにする。
E. 上腕三頭筋の筋力増強だけで物品把持の獲得を図る。

**Correct:** A

**Rationale:** C6レベルでは手関節伸筋が残存しやすい一方、十分な随意的手指屈曲は期待しにくい。手関節を能動的に伸展すると手指屈筋腱の受動張力によって指が屈曲するテノデーシス作用を利用できる。C6機能残存の四肢麻痺では、この残存手関節伸展を利用した把持・開放を学習することが重要であり、指屈筋を過度に伸張してテノデーシス作用を失わせる管理は避ける。

**Choice explanations**

- A: 正しい。残存する手関節背屈を受動的手指屈曲へ結び付ける機能訓練である。
- B: 小指外転は主にT1で、C6残存機能を利用した方法ではない。
- C: DIP屈曲はより下位髄節の機能であり、提示された残存機能と合わない。
- D: テノデーシス把持に必要な手指屈筋の受動張力を損なう方向である。
- E: 上腕三頭筋は主にC7であり、単独で手指把持を生じさせない。

**Tag:** theme=`C6残存機能を利用したテノデーシス把持訓練`; knowledge_node=`C6まで機能残存ならC5の肘屈筋とC6の手関節伸筋が使用できる`; knowledge_node_id=`KN1263`; task=`intervention_selection`; primary_ability=`PRESCRIBE`; secondary_ability=`KNOW`; level=3; safety=`none`; prerequisites=`C6機能`,`手関節背屈`,`テノデーシス把持`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1615 — KN0607

- Priority evidence: tier B; active wrong Q615; cycle_wrong=3; confident_wrong=2
- Existing demand: Q615 `fact_recall / KNOW`
- New demand: `assessment_selection / MEASURE`
- Management: `Q1615-C-13-O`
- Title: 基礎運動学・立位姿勢

**Stem**

成人の安静開脚立位でみられる微小な姿勢動揺を客観的に定量化したい。前後・左右方向の動揺量や軌跡を最も直接的に評価できるのはどれか。

**Choices**

A. 床反力計で足圧中心（COP）の軌跡を記録し、前後・左右方向の動揺指標を算出する。
B. Functional Reach Testで最大前方リーチ距離を測定する。
C. Berg Balance Scaleの総得点だけを算出する。
D. 下腿三頭筋の徒手筋力検査と足関節背屈可動域だけを測定する。
E. 10m歩行時間と歩数だけを測定する。

**Correct:** A

**Rationale:** 安静立位でも身体は完全には静止せず微小な姿勢動揺を示す。床反力計から得られる足圧中心（COP）の時系列は、前後・左右方向の変位、軌跡長、速度などを定量化でき、静的立位中の動揺を直接評価する代表的な方法である。臨床的バランステストや筋力・歩行指標は関連機能を評価できるが、安静立位中のCOP軌跡そのものを直接測定しない。

**Choice explanations**

- A: 正しい。静的立位の動揺を前後・左右方向の時系列として直接定量化できる。
- B: 動的な安定性限界の臨床評価であり、安静立位の微小動揺軌跡を直接測定しない。
- C: 総合的なバランス能力評価であり、COP軌跡の定量値ではない。
- D: 関連因子の評価であって、立位中の実際の動揺量ではない。
- E: 歩行能力の指標であり、安静開脚立位の動揺を直接評価しない。

**Tag:** theme=`安静開脚立位の姿勢動揺をCOPで定量化する`; knowledge_node=`成人の安静開脚立位の基本事項`; knowledge_node_id=`KN0607`; task=`assessment_selection`; primary_ability=`MEASURE`; secondary_ability=`INTERPRET`; level=2; safety=`none`; prerequisites=`安静立位`,`姿勢動揺`,`足圧中心`,`床反力計`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Manual design review basis

The v0.2 wording was checked against external biomechanics/rehabilitation literature before implementation:

- typical standing places the center of gravity above the knee slightly anterior to the joint, producing a small gravitational extension torque (PubMed PMID 4018044);
- during normal quiet standing the COM is in front of the ankle and gravity produces the forward/dorsiflexion tendency opposed by plantarflexors; reversing the gravity-line position reverses that moment relationship (Gait & Posture motor-control literature);
- C6-C7 tetraplegia can use active wrist extension to produce passive finger flexion through tenodesis grasp; effective tenodesis also depends on preserving appropriate passive flexor properties (PubMed PMID 8856569; PMC rehabilitation literature);
- force-platform COP measures are established quantitative measures of quiet-standing postural sway (PubMed PMID 19278852 and related force-platform studies).

Q1612 intentionally identifies the named five-stage model rather than implying that real psychological adaptation is universally linear.

## Batch2 implementation gate

Before Question Bank implementation:

1. Reconfirm Q1611-Q1615 are still free IDs and main head is Q1610.
2. Reconfirm each source Q resolves to the intended canonical Node.
3. Preserve this v0.2 content unless manual implementation review identifies a concrete medical defect.
4. Require every new `(task, primary_ability)` to differ from the active-wrong source demand(s).
5. Require `classify_repair_confirmation(source,new) == different_question_strong` for every active source Q in the target Node.
6. Do not add a reviewed strong-pair override to rescue weak design.
7. Preserve Q1-Q1610 canonical content unchanged.
8. Run focused tests, full pytest and Q1-Q1615 validator before manual merge review.
9. Do not merge before manual medical/content review of the implemented records.
