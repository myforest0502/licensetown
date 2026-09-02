# Repair Supply Phase 2 — batch1 item design v0.1

Status: **content design draft for manual medical review; not Question Bank data yet.**

The five items below are deliberately designed with `(task, primary_ability)` pairs different from both active-wrong questions in their Node.

## Q1606 candidate — KN0194

**Existing active wrong:** Q195 `device_selection/PRESCRIBE`; Q1599 `finding_interpretation/INTERPRET`

**New demand:** `assessment_selection/MEASURE`

**Management code:** `Q1606-C-15-O`

**Title:** 地域・住宅改修

**Stem**

79歳の女性。脳梗塞後の軽度左片麻痺があり、屋内歩行はT字杖で自立している。玄関の18cmの上がり框で昇降時のみ右手を壁につき、左下肢へ荷重する場面でふらつく。手すりの設置位置と高さを決めるため、住宅訪問で最も優先して確認すべき内容はどれか。

**Choices**

A. 10m歩行速度とTimed Up & Goのみ
B. 上がり框の高さ、実際の昇降方法、現在手をつく位置と右上肢の到達範囲
C. 握力と肩関節可動域のみ
D. 廊下幅と屋内歩数のみ
E. ベッド高と寝返り方法のみ

**Correct:** B

**Explanation:** 手すりの位置・高さは、問題となる上がり框の寸法だけでなく、実際の昇降方法、支持を求める位置、支持側上肢が安全に届く範囲を直接観察して決める。一般的な歩行能力や上肢機能だけでは、玄関で必要な支持位置を十分に決定できない。

**Choice notes:**
- A: 全身的な移動能力の把握には有用だが、手すりの具体的な位置・高さを直接決める情報としては不足する。
- B: 正しい。段差条件、動作、現支持位置、支持側上肢の到達を同じ場面で確認できる。
- C: 上肢機能は参考になるが、実際の上がり框昇降と支持位置を評価しないため不十分。
- D: 廊下環境は今回の問題場面ではない。
- E: ベッド動作は玄関の支持位置決定には直接つながらない。

**Tag draft:** theme=`上がり框手すり設置前の動作・環境評価`; knowledge_node=`玄関上がり框への手すり`; knowledge_node_id=`KN0194`; task=`assessment_selection`; primary_ability=`MEASURE`; secondary_ability=`PRESCRIBE`; level=3; safety=`moderate`; prerequisites=`上がり框寸法`,`段差昇降観察`,`上肢到達範囲`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

## Q1607 candidate — KN0676

**Existing active wrong:** Q684 `finding_interpretation/INTERPRET`; Q1602 `safety_priority/DECIDE`

**New demand:** `assessment_selection/MEASURE`

**Management code:** `Q1607-B-7-O`

**Title:** 救急・ショック

**Stem**

頸髄損傷後の患者で血圧低下を認め、神経原性ショックと循環血液量減少性ショックの鑑別が必要になった。血圧と併せて、神経原性ショックを支持する所見を把握するために優先して確認すべき組合せはどれか。

**Choices**

A. 心拍数の推移と皮膚温・末梢の血管拡張所見
B. 握力と上下肢の関節可動域
C. 呼吸数と喀痰量
D. 瞳孔径と視力
E. 腹囲と排便回数

**Correct:** A

**Explanation:** 神経原性ショックでは交感神経活動低下により低血圧に徐脈を伴いやすく、末梢血管拡張のため皮膚が温かいことがある。循環血液量減少性ショックでは一般に頻脈や冷感を伴いやすいため、心拍数の推移と皮膚・末梢循環所見は鑑別に有用である。

**Choice notes:**
- A: 正しい。低血圧に対する心拍応答と末梢血管拡張の組合せが神経原性ショックの特徴把握に直結する。
- B: 神経学的・運動機能評価としては有用でも、ショック型の鑑別に直接用いない。
- C: 呼吸状態の把握は重要だが、神経原性ショックと循環血液量減少性ショックの特徴的鑑別所見ではない。
- D: 意識・神経評価の一部になり得るが、提示された循環動態の鑑別には直接的でない。
- E: 急性のショック型鑑別の優先項目ではない。

**Tag draft:** theme=`神経原性ショックの鑑別に必要な循環所見`; knowledge_node=`神経原性ショックにおける低血圧・徐脈などの特徴`; knowledge_node_id=`KN0676`; task=`assessment_selection`; primary_ability=`MEASURE`; secondary_ability=`INTERPRET`; level=3; safety=`moderate`; prerequisites=`低血圧`,`徐脈`,`末梢血管拡張`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

## Q1608 candidate — KN0025

**Existing active wrong:** Q25 `assessment_selection/MEASURE`; Q1596 `finding_interpretation/INTERPRET`

**New demand:** `safety_priority/DECIDE`

**Management code:** `Q1608-C-15-O`

**Title:** 頸椎疾患

**Stem**

頸椎症性脊髄症で保存的に理学療法を行っている患者。ここ2週間でボタン操作がさらに不器用となり、歩行時のつまずきが増えた。診察時には上下肢腱反射亢進があり、新たに排尿障害も訴えている。理学療法士の対応として最も適切なのはどれか。

**Choices**

A. 予定どおり運動負荷を増やし、1か月後に再評価する。
B. 歩行練習だけ減らし、頸部伸展運動は積極的に継続する。
C. 症状を記録し、次の定期診察まで同じプログラムを継続する。
D. 神経症状の進行を疑い、負荷の進行を止めて速やかな医学的再評価につなぐ。
E. 上肢MMTが保たれていれば握力訓練のみ追加する。

**Correct:** D

**Explanation:** 頸髄症では手指巧緻性低下、歩行障害、錐体路徴候が重要であり、神経学的悪化や膀胱機能変化は進行を疑う所見である。保存的管理中に神経症状が悪化した場合は、通常どおり負荷を進めるのではなく、速やかな医学的再評価へつなぐ。

**Choice notes:**
- A: 神経症状が進行している状況で負荷を増やして経過を見るのは適切でない。
- B: 頸部伸展で症状を誘発・増悪することがあり、進行所見を無視して継続しない。
- C: 新たな神経学的悪化があるため定期診察まで待つ対応は不十分。
- D: 正しい。進行性の頸髄症を疑い医学的再評価を優先する。
- E: 筋力が保たれていても巧緻性・歩行・自律神経症状の進行は否定できない。

**Tag draft:** theme=`頸髄症の神経学的悪化に対する安全判断`; knowledge_node=`頸髄症による上肢巧緻運動・歩行障害と上位運動ニューロン徴候`; knowledge_node_id=`KN0025`; task=`safety_priority`; primary_ability=`DECIDE`; secondary_ability=`INTERPRET`; level=4; safety=`moderate`; prerequisites=`手指巧緻性低下`,`歩行障害`,`錐体路徴候`,`膀胱機能変化`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

## Q1609 candidate — KN0329

**Existing active wrong:** Q331 `intervention_selection/PRESCRIBE`; Q1600 `finding_interpretation/INTERPRET`

**New demand:** `assessment_selection/MEASURE`

**Management code:** `Q1609-C-16-O`

**Title:** 熱傷

**Stem**

前頸部熱傷後の患者に頸部伸展位を用いた抗拘縮ポジショニングを行っている。前頸部瘢痕による屈曲拘縮の進行とポジショニング効果を経時的に把握するため、最も直接的な評価はどれか。

**Choices**

A. 頸部伸展可動域と前頸部瘢痕の短縮・伸張性の変化
B. 頸部回旋可動域のみ
C. 肩関節外転可動域と握力
D. 胸郭拡張差とSpO₂
E. 膝関節伸展可動域と立ち上がり回数

**Correct:** A

**Explanation:** 前頸部熱傷では瘢痕短縮により頸部屈曲拘縮が生じやすい。抗拘縮ポジショニングの効果を追うには、直接影響を受ける頸部伸展可動域と前頸部瘢痕の短縮・伸張性を経時的に確認するのが最も適切である。

**Choice notes:**
- A: 正しい。拘縮方向と瘢痕組織の変化を直接追える。
- B: 回旋は参考になる場合があるが、前頸部瘢痕による屈曲拘縮の主要評価ではない。
- C: 肩機能・握力だけでは頸部抗拘縮ポジショニングの効果を評価できない。
- D: 呼吸状態の評価であり、前頸部瘢痕短縮の直接評価ではない。
- E: 下肢機能は今回の頸部拘縮評価と一致しない。

**Tag draft:** theme=`前頸部熱傷の抗拘縮ポジショニング効果の評価`; knowledge_node=`前頸部熱傷瘢痕拘縮を予防する頸部伸展位`; knowledge_node_id=`KN0329`; task=`assessment_selection`; primary_ability=`MEASURE`; secondary_ability=`INTERPRET`; level=3; safety=`moderate`; prerequisites=`頸部伸展可動域`,`前頸部瘢痕`,`抗拘縮ポジショニング`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

## Q1610 candidate — KN0697

**Existing active wrong:** Q705 `intervention_selection/PRESCRIBE`; Q1603 `assessment_selection/MEASURE`

**New demand:** `safety_priority/DECIDE`

**Management code:** `Q1610-C-17-O`

**Title:** 内部障害・呼吸器疾患

**Stem**

在宅酸素療法中の重症COPD患者に自転車エルゴメータ運動を開始した。処方された酸素療法を継続した状態で、低強度負荷にもかかわらずSpO₂が93％から86％へ低下し、修正Borg息切れが7となった。次の対応として最も適切なのはどれか。

**Choices**

A. 胸痛がなければ同じ負荷を予定時間まで継続する。
B. 適応を促すため負荷を上げて短時間で終了する。
C. いったん運動を中断または減量し、SpO₂・症状の回復と酸素供給状態を確認して運動処方を再調整する。
D. 心拍数だけを目安にし、SpO₂低下は無視して継続する。
E. 酸素療法を外して自然な運動反応を確認する。

**Correct:** C

**Explanation:** 重症COPDの運動療法は個別化し、呼吸困難と酸素化を監視しながら調整する。低強度でも著明な酸素化低下と強い息切れを認めた場合は、そのまま負荷を継続・増加せず、運動を中断または減量して回復と酸素供給状態を確認し、より低い強度や方法へ再調整する。

**Choice notes:**
- A: 強い息切れと酸素化低下を認めており、予定時間の完遂を優先しない。
- B: 反応が不良な状態で負荷を増やすのは適切でない。
- C: 正しい。症状と酸素化を基準に安全を確保し、処方を個別調整する。
- D: COPDでは心拍数だけでなく自覚症状とSpO₂を重視する。
- E: 在宅酸素療法の処方を自己判断で外して評価しない。

**Tag draft:** theme=`重症COPD運動中の酸素化低下に対する安全判断`; knowledge_node=`重症COPDに対する有酸素運動強度の設定`; knowledge_node_id=`KN0697`; task=`safety_priority`; primary_ability=`DECIDE`; secondary_ability=`PRESCRIBE`; level=4; safety=`moderate`; prerequisites=`運動時SpO2`,`修正Borg息切れ`,`運動負荷調整`; tag_version=`1.0`; tag_status=`reviewed`; source=`original`.

## Medical-review notes

The design is consistent with established principles used for manual review:

- Neurogenic shock: hypotension with bradycardia and warm/pink skin from loss of sympathetic tone; assessment must also consider alternative causes of shock.
- Degenerative cervical myelopathy: hand dexterity loss, gait dysfunction, UMN signs and sphincter dysfunction are recognized features; neurological deterioration during nonoperative care requires medical/surgical reassessment.
- Anterior neck burn rehabilitation: anti-contracture positioning is neck extension, commonly avoiding a pillow behind the head; ROM and scar shortening are direct follow-up targets.
- COPD pulmonary rehabilitation: exercise prescription is individualized and monitored using physiologic and symptom response; marked exercise desaturation or intolerable dyspnea requires reduction/interruption and reassessment rather than automatic progression.

## Structural STRONG expectation

Because every proposed new demand pair differs from both corresponding active-wrong demand pairs, each candidate is expected to classify as `different_question_strong` against both source questions once the tags are present. This must be verified by executable tests; expectation alone is not acceptance.
