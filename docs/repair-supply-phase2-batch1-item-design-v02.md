# Repair Supply Phase 2 — batch1 item design v0.2

Status: **manual medical/content review candidate; not Question Bank data.**

This revision strengthens distractors so confidence=1 is more meaningful. All proposed `(task, primary_ability)` pairs differ from both active-wrong questions in the same canonical Node.

## Q1606 — KN0194

- Sources: Q195 `device_selection/PRESCRIBE`, Q1599 `finding_interpretation/INTERPRET`
- New demand: `assessment_selection/MEASURE`
- Management: `Q1606-C-15-O`
- Title: 地域・住宅改修

**Stem**

79歳の女性。脳梗塞後の軽度左片麻痺があり、屋内歩行はT字杖で自立している。玄関の18cmの上がり框で昇降時のみ右手を壁につき、左下肢へ荷重する場面でふらつく。手すりの設置位置と高さを決めるため、住宅訪問で最も優先して確認すべき内容はどれか。

**Choices**

A. Timed Up & GoとBerg Balance Scaleのみ
B. 上がり框の高さ、実際の昇降方法、現在手をつく位置と右上肢の到達範囲
C. 握力、肩関節可動域、利き手のみ
D. 身長と一般的な手すり推奨高のみ
E. 家族が希望する設置側と玄関幅のみ

**Correct:** B

**Rationale:** 手すりの具体的位置・高さは、一般的なバランス能力や身体計測だけではなく、問題となる段差の寸法、実際の昇降戦略、現在の支持位置、支持側上肢の安全な到達範囲を同じ場面で観察して決める。

**Choice explanations**

- A: 全身的バランスの把握には有用だが、玄関で必要な支持位置・高さを直接決める情報として不足する。
- B: 正しい。段差条件と実動作、現支持位置、上肢到達を直接評価できる。
- C: 上肢機能は参考になるが、段差昇降時の実際の支持位置を評価していない。
- D: 標準値だけで個別の動作戦略や到達範囲を反映できない。
- E: 家族希望や玄関幅は環境調整に関係するが、患者本人の安全な支持位置を決める主評価ではない。

**Tag:** theme=`上がり框手すり設置前の動作・環境評価`; knowledge_node=`玄関上がり框への手すり`; knowledge_node_id=`KN0194`; task=`assessment_selection`; primary_ability=`MEASURE`; secondary_ability=`PRESCRIBE`; level=3; safety=`moderate`; prerequisites=`上がり框寸法`,`段差昇降観察`,`上肢到達範囲`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1607 — KN0676

- Sources: Q684 `finding_interpretation/INTERPRET`, Q1602 `safety_priority/DECIDE`
- New demand: `assessment_selection/MEASURE`
- Management: `Q1607-B-7-O`
- Title: 救急・ショック

**Stem**

頸髄損傷後の患者で血圧低下を認め、神経原性ショックと循環血液量減少性ショックの鑑別が必要になった。血圧と併せて、神経原性ショックを支持する循環所見を把握するために優先して確認すべき組合せはどれか。

**Choices**

A. 心拍数の推移と皮膚温・末梢血管拡張の所見
B. 呼吸数とSpO₂
C. 毛細血管再充満時間と外出血量
D. 尿量と体重変化
E. 深部腱反射と下肢筋力

**Correct:** A

**Rationale:** 神経原性ショックでは交感神経活動低下により低血圧に徐脈を伴いやすく、末梢血管拡張により皮膚が温かくなることがある。循環血液量減少性ショックでは一般に頻脈や末梢冷感を伴いやすいため、心拍応答と皮膚・末梢循環所見は鑑別に有用である。外出血など他のショック原因の確認自体は別途必要である。

**Choice explanations**

- A: 正しい。低血圧に対する心拍応答と末梢血管拡張の組合せが神経原性ショックの特徴把握に直結する。
- B: 呼吸状態の安全確認として重要だが、神経原性と循環血液量減少性の特徴的鑑別所見ではない。
- C: 出血性要因の評価に重要だが、神経原性ショックを積極的に支持する所見の組合せではない。
- D: 循環状態の追跡には関係するが、急性のショック型を特徴づける組合せではない。
- E: 脊髄損傷の神経学的評価として有用でも、循環性ショックの型を直接判別しない。

**Tag:** theme=`神経原性ショックの鑑別に必要な循環所見`; knowledge_node=`神経原性ショックにおける低血圧・徐脈などの特徴`; knowledge_node_id=`KN0676`; task=`assessment_selection`; primary_ability=`MEASURE`; secondary_ability=`INTERPRET`; level=3; safety=`moderate`; prerequisites=`低血圧`,`徐脈`,`末梢血管拡張`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1608 — KN0025

- Sources: Q25 `assessment_selection/MEASURE`, Q1596 `finding_interpretation/INTERPRET`
- New demand: `safety_priority/DECIDE`
- Management: `Q1608-C-15-O`
- Title: 頸椎疾患

**Stem**

頸椎症性脊髄症で保存的に理学療法を行っている患者。ここ2週間でボタン操作がさらに不器用となり、歩行時のつまずきが増えた。上下肢腱反射亢進があり、新たに排尿障害も訴えている。理学療法士の対応として最も適切なのはどれか。

**Choices**

A. 予定どおり運動負荷を増やし、1か月後に再評価する。
B. 歩行練習だけ減らし、頸部伸展運動は積極的に継続する。
C. 症状を記録し、次の定期診察まで同じプログラムを継続する。
D. 神経症状の進行を疑い、負荷の進行を止めて速やかな医学的再評価につなぐ。
E. 上肢MMTが保たれていれば握力訓練のみ追加する。

**Correct:** D

**Rationale:** 頸髄症では手指巧緻性低下、歩行障害、錐体路徴候が重要であり、神経学的悪化や膀胱機能変化は進行を疑う所見である。保存的管理中に神経症状が悪化した場合は、通常どおり負荷を進めるのではなく速やかな医学的再評価へつなぐ。

**Choice explanations**

- A: 神経症状が進行している状況で負荷増加と長期経過観察を優先しない。
- B: 進行所見があるため、一部訓練だけ調整して頸部負荷を積極継続する段階ではない。
- C: 新たな神経学的悪化があるため定期診察まで待つ対応は不十分。
- D: 正しい。進行性の頸髄症を疑い医学的再評価を優先する。
- E: 筋力が保たれていても巧緻性、歩行、自律神経症状の進行は否定できない。

**Tag:** theme=`頸髄症の神経学的悪化に対する安全判断`; knowledge_node=`頸髄症による上肢巧緻運動・歩行障害と上位運動ニューロン徴候`; knowledge_node_id=`KN0025`; task=`safety_priority`; primary_ability=`DECIDE`; secondary_ability=`INTERPRET`; level=4; safety=`moderate`; prerequisites=`手指巧緻性低下`,`歩行障害`,`錐体路徴候`,`膀胱機能変化`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1609 — KN0329

- Sources: Q331 `intervention_selection/PRESCRIBE`, Q1600 `finding_interpretation/INTERPRET`
- New demand: `assessment_selection/MEASURE`
- Management: `Q1609-C-16-O`
- Title: 熱傷

**Stem**

前頸部熱傷後の患者に頸部伸展位を用いた抗拘縮ポジショニングを行っている。前頸部瘢痕による屈曲拘縮の進行とポジショニング効果を経時的に把握するため、最も直接的な評価はどれか。

**Choices**

A. 頸部伸展可動域と前頸部瘢痕の短縮・伸張性の変化
B. 頸部屈曲可動域と疼痛NRSのみ
C. 頸部回旋可動域と側頸部皮膚の伸張性のみ
D. 肩関節外転可動域と腋窩部瘢痕の伸張性
E. 胸郭拡張差と安静時SpO₂

**Correct:** A

**Rationale:** 前頸部熱傷では瘢痕短縮により頸部屈曲拘縮が生じやすい。抗拘縮ポジショニングの効果を追うには、直接制限される頸部伸展可動域と前頸部瘢痕の短縮・伸張性を経時的に確認するのが最も適切である。

**Choice explanations**

- A: 正しい。予想される拘縮方向と原因組織の変化を直接追える。
- B: 痛みや屈曲可動域も参考になるが、前頸部短縮による伸展制限を直接追う組合せではない。
- C: 回旋・側頸部評価だけでは前頸部全体の屈曲拘縮を十分に評価できない。
- D: 腋窩熱傷の評価には適するが、前頸部の抗拘縮効果とは異なる。
- E: 呼吸状態の評価であり、前頸部瘢痕短縮の直接評価ではない。

**Tag:** theme=`前頸部熱傷の抗拘縮ポジショニング効果の評価`; knowledge_node=`前頸部熱傷瘢痕拘縮を予防する頸部伸展位`; knowledge_node_id=`KN0329`; task=`assessment_selection`; primary_ability=`MEASURE`; secondary_ability=`INTERPRET`; level=3; safety=`moderate`; prerequisites=`頸部伸展可動域`,`前頸部瘢痕`,`抗拘縮ポジショニング`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Q1610 — KN0697

- Sources: Q705 `intervention_selection/PRESCRIBE`, Q1603 `assessment_selection/MEASURE`
- New demand: `safety_priority/DECIDE`
- Management: `Q1610-C-17-O`
- Title: 内部障害・呼吸器疾患

**Stem**

在宅酸素療法中の重症COPD患者に自転車エルゴメータ運動を開始した。処方された酸素療法を継続した状態で、低強度負荷にもかかわらずSpO₂が93％から86％へ低下し、修正Borg息切れが7となった。次の対応として最も適切なのはどれか。

**Choices**

A. 胸痛がなければ同じ負荷を維持し、5分後に再評価する。
B. ペダル回転数だけ下げ、酸素供給状態を確認せず同じ目標負荷を続ける。
C. いったん運動を中断または減量し、SpO₂・症状の回復と酸素供給状態を確認して、より低い強度や方法へ再調整する。
D. 酸素流量を自己判断で処方以上に増やし、同じ負荷を継続する。
E. 心拍数を主指標に切り替え、SpO₂と息切れは運動強度判断から外す。

**Correct:** C

**Rationale:** 重症COPDの運動療法は個別化し、呼吸困難と酸素化を監視しながら調整する。低強度でも著明な酸素化低下と強い息切れを認めた場合は、そのまま負荷を継続・増加せず、運動を中断または減量して回復と酸素供給状態を確認し、より低い強度やインターバル等へ再調整する。

**Choice explanations**

- A: 強い息切れと酸素化低下を認めており、同じ負荷の時間延長を優先しない。
- B: 表面的に回転数だけ変えず、酸素化・症状と実負荷を再評価する必要がある。
- C: 正しい。安全を確保して生理学的・自覚的反応を確認し、個別に再処方する。
- D: 酸素流量を理学療法士が自己判断で処方以上へ変更して負荷継続する対応ではない。
- E: COPDの運動強度判断では自覚症状と酸素化を無視しない。

**Tag:** theme=`重症COPD運動中の酸素化低下に対する安全判断`; knowledge_node=`重症COPDに対する有酸素運動強度の設定`; knowledge_node_id=`KN0697`; task=`safety_priority`; primary_ability=`DECIDE`; secondary_ability=`PRESCRIBE`; level=4; safety=`moderate`; prerequisites=`運動時SpO2`,`修正Borg息切れ`,`運動負荷調整`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

---

## Manual review result for design v0.2

### Medical correctness

- Q1606: PASS — direct task/environment assessment is appropriate before individualized handrail placement.
- Q1607: PASS — neurogenic shock classically combines hypotension with bradycardia and warm/pink skin due to loss of sympathetic tone; competing shock causes still require evaluation.
- Q1608: PASS — worsening hand dexterity/gait with new bladder dysfunction represents neurological deterioration in degenerative cervical myelopathy and warrants prompt medical reassessment rather than routine progression.
- Q1609: PASS — anterior neck burns are positioned in extension to oppose flexion contracture; cervical extension ROM and anterior scar shortening/pliability directly track the target impairment.
- Q1610: PASS — COPD exercise training should be individualized using physiologic and symptom response; marked desaturation with intolerable dyspnea warrants interruption/reduction and reassessment rather than automatic progression.

### Distractor quality

- Q1606: PASS — alternatives are plausible but incomplete ways of setting installation parameters.
- Q1607: PASS — alternatives are clinically relevant assessments but do not characterize the neurogenic shock circulation pattern as directly.
- Q1608: PASS — alternatives represent delayed or incomplete PT responses to neurological worsening.
- Q1609: PASS — alternatives are legitimate rehabilitation measures for other dimensions/regions but not the direct target of anterior-neck flexion contracture.
- Q1610: PASS — alternatives represent plausible but unsafe/incomplete exercise-management choices rather than absurd unrelated actions.

### Independence

All five are designed as a third demand/context, not a paraphrase of either active-wrong source item.

### Structural STRONG expectation

- Q1606 (`assessment_selection/MEASURE`) differs from Q195 (`device_selection/PRESCRIBE`) and Q1599 (`finding_interpretation/INTERPRET`).
- Q1607 (`assessment_selection/MEASURE`) differs from Q684 (`finding_interpretation/INTERPRET`) and Q1602 (`safety_priority/DECIDE`).
- Q1608 (`safety_priority/DECIDE`) differs from Q25 (`assessment_selection/MEASURE`) and Q1596 (`finding_interpretation/INTERPRET`).
- Q1609 (`assessment_selection/MEASURE`) differs from Q331 (`intervention_selection/PRESCRIBE`) and Q1600 (`finding_interpretation/INTERPRET`).
- Q1610 (`safety_priority/DECIDE`) differs from Q705 (`intervention_selection/PRESCRIBE`) and Q1603 (`assessment_selection/MEASURE`).

Executable classifier tests remain mandatory after insertion into the actual Question Bank.
