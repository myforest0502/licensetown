# Repair Supply Phase 2 — batch2 item design v0.1

Status: **content design candidate; not Question Bank data.**

Basis: Production `repair_supply_top_6` through `top_10` after the five Priority A Nodes were assigned to batch1. Existing weak pairs were manually reviewed first; KN1256 Q1272/Q1457 remains WEAK because the questions are near-duplicate `fact_recall/KNOW` items.

Proposed IDs assume current Question Bank head remains Q1610 when implementation starts. Reconfirm immediately before writing data.

---

## Q1611 candidate — KN1399

**Priority evidence:** tier B; active wrong Q1424; cycle_wrong=4; confident_wrong=4.

**Existing demand:** Q1424 `fact_recall / KNOW`

**New demand:** `finding_interpretation / INTERPRET`

**Management:** `Q1611-C-13-O`

**Title:** 基礎運動学・立位姿勢

**Stem**

成人の安静立位を矢状面から観察した。膝関節中心に対して重心線が通常より後方を通り、立位保持中の大腿四頭筋活動が増えている。この所見の力学的解釈として最も適切なのはどれか。

**Choices**

A. 膝関節に外的伸展モーメントが増え、大腿四頭筋活動は不要になる。
B. 膝関節に外的屈曲モーメントが生じやすく、その制御に大腿四頭筋活動が必要になる。
C. 股関節の外的内転モーメントだけが増え、膝関節の筋活動とは無関係である。
D. 重心線が膝関節中心の後方にあるほど、靱帯性支持だけで安定しやすくなる。
E. 矢状面の重心線位置は膝関節モーメントに影響しない。

**Correct:** B

**Rationale:** 安静立位では重心線が膝関節中心のやや前方を通ることで膝には小さな外的伸展方向の作用が生じ、過大な大腿四頭筋活動を要さず安定しやすい。重心線が膝関節中心より後方へ移ると外的屈曲モーメントが生じやすく、膝折れを防ぐために大腿四頭筋による制御が必要になる。

**Choice notes**

- A: 後方を通る場合は外的屈曲方向であり、説明が逆。
- B: 正しい。重心線の後方化と増えた大腿四頭筋活動を同じ力学で説明できる。
- C: 矢状面の膝モーメントを直接扱う所見である。
- D: 通常のやや前方という位置関係から外れるため、筋活動が増える所見と矛盾する。
- E: 重心線と関節中心の位置関係は外的モーメントを左右する。

**Tag draft:** theme=`膝関節中心に対する重心線位置と外的モーメント`; knowledge_node=`安静立位では重心線が膝関節中心のやや前方を通ることで少ない筋活動で安定する`; knowledge_node_id=`KN1399`; task=`finding_interpretation`; primary_ability=`INTERPRET`; secondary_ability=`KNOW`; level=3; safety=`none`; prerequisites=`重心線`,`膝関節中心`,`外的屈曲モーメント`,`大腿四頭筋`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1612 candidate — KN1151

**Priority evidence:** tier B; active wrong Q1164/Q1221; cycle_wrong=4; confident_wrong=2.

**Existing demand:** Q1164 and Q1221 both `fact_recall / KNOW`

**New demand:** `finding_interpretation / INTERPRET`

**Management:** `Q1612-A-3-O`

**Title:** 心理・障害受容

**Stem**

脊髄損傷後の患者。受傷直後の茫然とした時期や「元どおりになるはずだ」と現実を認めにくい時期を経て、しばらく気持ちの揺れが続いていた。最近は「今の身体で仕事に戻る方法を考えたい」と自ら福祉用具や職業復帰について具体的に相談するようになった。障害受容の5段階で最も当てはまるのはどれか。

**Choices**

A. ショック期
B. 否認期
C. 混乱期
D. 解決への努力期
E. 受容期

**Correct:** D

**Rationale:** 障害受容の代表的な5段階は、ショック、否認、混乱、解決への努力、受容の順で整理される。現状を前提に具体的な生活・職業上の方法を探し始める場面は、単なる否認や混乱ではなく「解決への努力」の段階として捉える。

**Choice notes**

- A: 受傷直後の茫然・感情反応の乏しい状態に対応する。
- B: 障害の現実を認めにくい時期であり、具体的適応策を探す現在像とは異なる。
- C: 感情的な揺れや葛藤が前景となる段階で、現在はそこから具体策へ進んでいる。
- D: 正しい。現状を踏まえて具体的な解決策を探している。
- E: 適応が進んだ最終段階として整理されるが、提示場面は積極的に解決策を模索している段階を問うている。

**Tag draft:** theme=`障害受容の解決への努力期の行動解釈`; knowledge_node=`障害受容の5段階はショック、否認、混乱、解決への努力、受容の順`; knowledge_node_id=`KN1151`; task=`finding_interpretation`; primary_ability=`INTERPRET`; secondary_ability=`KNOW`; level=2; safety=`none`; prerequisites=`ショック`,`否認`,`混乱`,`解決への努力`,`受容`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1613 candidate — KN1256

**Priority evidence:** tier B; active wrong Q1272; existing weak candidate Q1457; cycle_wrong=4; confident_wrong=2.

**Existing demands:** Q1272 and canonicalized Q1457 are both `fact_recall / KNOW` and remain formally WEAK as a repair pair.

**New demand:** `finding_interpretation / INTERPRET`

**Management:** `Q1613-C-13-O`

**Title:** 基礎運動学・立位姿勢

**Stem**

安静立位を矢状面から解析したところ、重心線が外果より後方を通っていた。足関節中心まわりに重力が生じさせる外的モーメントと、それに拮抗する筋活動の組合せとして最も適切なのはどれか。

**Choices**

A. 背屈モーメント ― 足関節底屈筋
B. 底屈モーメント ― 足関節背屈筋
C. 内反モーメント ― 足関節外反筋
D. 外反モーメント ― 足関節内反筋
E. 回旋モーメント ― 膝関節伸筋

**Correct:** B

**Rationale:** 通常の安静立位では矢状面の重心線は外果のやや前方を通る。重力線が足関節中心より後方へ移れば、重力による外的作用は足関節を底屈方向へ回そうとするため、それに拮抗するには背屈筋側の活動が必要になる。単なる「外果前方」という位置の再生ではなく、位置変化から外的モーメントを解釈する問題である。

**Choice notes**

- A: 重心線が足関節中心より前方にある場合の方向関係に近い。
- B: 正しい。後方化した重力線は底屈方向の外的モーメントを生じる。
- C: 矢状面の前後位置から内反モーメントを導かない。
- D: 同様に外反モーメントを問う所見ではない。
- E: 足関節中心に対する矢状面位置の解釈として不適切。

**Tag draft:** theme=`外果に対する重心線位置から足関節外的モーメントを解釈する`; knowledge_node=`矢状面の重心線は耳垂付近、肩峰付近、大転子や膝関節のやや前方、外果のやや前方を通る`; knowledge_node_id=`KN1256`; task=`finding_interpretation`; primary_ability=`INTERPRET`; secondary_ability=`KNOW`; level=3; safety=`none`; prerequisites=`重心線`,`外果`,`足関節中心`,`外的モーメント`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1614 candidate — KN1263

**Priority evidence:** tier B; active wrong Q1279; cycle_wrong=4; confident_wrong=2.

**Existing demand:** Q1279 `fact_recall / KNOW`

**New demand:** `intervention_selection / PRESCRIBE`

**Management:** `Q1614-B-8-O`

**Title:** 脊髄損傷・上肢機能

**Stem**

第6頸髄節まで機能が残存する完全頸髄損傷患者。手関節背屈は可能だが、手指の随意的な屈曲は困難である。残存機能を利用して物品把持を獲得するための訓練として最も適切なのはどれか。

**Choices**

A. 手関節背屈に伴う受動的な手指屈曲を利用し、テノデーシス把持を練習する。
B. 小指外転筋の最大筋力訓練を反復し、側方つまみを獲得する。
C. 中指DIP関節の随意屈曲を抵抗運動で強化する。
D. 手関節を常に掌屈位に固定し、手指屈筋を完全に伸張しておく。
E. 手関節背屈を使わず、上腕三頭筋の随意収縮だけで把持を練習する。

**Correct:** A

**Rationale:** C6まで機能が残存する場合、手関節背屈を利用できる一方で、手指内在筋や十分な随意指屈曲は期待しにくい。手関節背屈に伴う手指の受動的屈曲を利用するテノデーシス把持は、C6レベルの残存機能を日常的把持へ結びつける代表的な方法である。

**Choice notes**

- A: 正しい。残存する手関節背屈を機能的把持へ変換する。
- B: 小指外転は主にT1で、C6残存機能を利用した方法ではない。
- C: DIP屈曲はより下位髄節の機能であり、提示された残存機能と合わない。
- D: テノデーシスを利用するうえで不適切な固定・過度な伸張となる。
- E: 上腕三頭筋は主にC7であり、把持そのものの代替にもならない。

**Tag draft:** theme=`C6残存機能を利用したテノデーシス把持訓練`; knowledge_node=`C6まで機能残存ならC5の肘屈筋とC6の手関節伸筋が使用できる`; knowledge_node_id=`KN1263`; task=`intervention_selection`; primary_ability=`PRESCRIBE`; secondary_ability=`KNOW`; level=3; safety=`none`; prerequisites=`C6機能`,`手関節背屈`,`テノデーシス把持`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1615 candidate — KN0607

**Priority evidence:** tier B; active wrong Q615; cycle_wrong=3; confident_wrong=2.

**Existing demand:** Q615 `fact_recall / KNOW`

**New demand:** `assessment_selection / MEASURE`

**Management:** `Q1615-C-13-O`

**Title:** 基礎運動学・立位姿勢

**Stem**

成人の安静開脚立位でみられる微小な姿勢動揺を客観的に定量化したい。前後・左右方向の動揺量や軌跡を最も直接的に評価できるのはどれか。

**Choices**

A. 床反力計で足圧中心（COP）の軌跡と動揺量を記録する。
B. 10m歩行時間を測定する。
C. 下腿三頭筋の徒手筋力検査だけを行う。
D. 足関節背屈可動域だけを角度計で測定する。
E. 立位後の自覚的疲労度だけを聞き取る。

**Correct:** A

**Rationale:** 安静立位でも身体は完全静止せず微小な姿勢動揺を示す。床反力計から得られる足圧中心（COP）軌跡は、その前後・左右方向の移動や総軌跡長などを定量化でき、静的立位の動揺を直接評価する代表的な方法である。

**Choice notes**

- A: 正しい。静的立位の動揺を時間系列の軌跡として直接測定できる。
- B: 歩行能力の指標であり、安静立位の微小動揺を直接測定しない。
- C: 筋力は関連因子だが、立位中の実際の動揺量そのものではない。
- D: 可動域も関連し得るが、姿勢動揺の直接指標ではない。
- E: 主観情報のみでは前後・左右の動揺軌跡を定量化できない。

**Tag draft:** theme=`安静開脚立位の重心動揺をCOPで定量化する`; knowledge_node=`成人の安静開脚立位の基本事項`; knowledge_node_id=`KN0607`; task=`assessment_selection`; primary_ability=`MEASURE`; secondary_ability=`INTERPRET`; level=2; safety=`none`; prerequisites=`安静立位`,`重心動揺`,`足圧中心`,`床反力計`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Batch2 design gate

Before Question Bank implementation:

1. Reconfirm Q1611-Q1615 are still free IDs.
2. Reconfirm each source Q remains in the intended canonical Node.
3. Check medical/biomechanical correctness, especially Q1611 and Q1613 moment directions and Q1614 tenodesis wording.
4. Confirm every new `(task, primary_ability)` differs from its active-wrong source demand(s).
5. Require `classify_repair_confirmation(source,new) == different_question_strong` for every active source Q in the Node.
6. Do not add a reviewed strong-pair override to rescue weak design.
7. Preserve Q1-Q1610 canonical content unchanged.
8. Run focused tests, full pytest and Q1-Q1615 validator before manual merge review.
