# Repair Supply Phase2 batch10 item design v0.2

## Scope
Batch10 extends the Question Bank from Q1650 to Q1655 with five original repair-supply questions. Existing Q1-Q1650 canonical content, official accepted answers, classifier behavior, canonical map, Phase10/11 logic, DB behavior, and learner-facing behavior must remain unchanged.

Branch: `feature/repair-supply-phase2-batch10-q1651-q1655-v01`
Base main: `930b904c6cfb0721bd47d3ad4f3a10663c6da84d`

## Formal STRONG contract
The current `classify_repair_confirmation()` contract must remain unchanged. A candidate is STRONG only when it resolves to the same canonical Node and has a different `(task, primary_ability)` demand, unless an already reviewed formal pair exists. Do not add a reviewed STRONG override merely to force tests.

Expected mapping:
- Q1651 -> KN0966, source Q976
- Q1652 -> KN0988, source Q998
- Q1653 -> KN1029, source Q1039
- Q1654 -> KN1470, source Q1495
- Q1655 -> KN1475, source Q1500

## Source audit

### Q976 -> KN0966
- management code: Q976-B-8-P
- source question: acute myocardial infarction blood-test finding that does **not** rise after onset
- official answer: 1 = creatinine
- relevant choices include creatinine, troponin T, myoglobin, LD
- explanation contract: troponin T/myoglobin/CK/LD may rise with myocardial injury; creatinine is a renal-function marker rather than a myocardial-necrosis marker
- existing tags: `finding_interpretation / INTERPRET`

### Q998 -> KN0988
- management code: Q998-C-15-P
- source question: correct gait-disorder/cause combinations, two choices
- official answer: 3 and 4
- relevant source pair: `steppage gait — common peroneal nerve palsy`
- explanation contract: steppage gait results from ankle dorsiflexor weakness/paralysis; common peroneal neuropathy is a representative cause
- existing tags: `fact_recall / KNOW`

### Q1039 -> KN1029
- management code: Q1039-A-3-P
- source question: second stage in the five-stage disability-acceptance model
- official answer: 3 = denial
- explanation contract: shock is followed by denial in the model used by the source
- existing tags: `fact_recall / KNOW`
- canonicalization note: KN1029 is not currently aliased to KN1151 in `knowledge_node_canonical_map.json`, although both cover the same five-stage sequence. **Do not merge or edit the canonical map in Batch10.** Treat canonicalization quality as a separate follow-up concern.

### Q1495 -> KN1470
- management code: Q1495-A-3-P
- source question: which measure is a questionnaire method
- official answer: 1 = BDI-II
- source explanation: BDI-II is a self-administered questionnaire answered by the patient; BPRS/HAM-D are interviewer/rater based
- existing tags: `assessment_selection / MEASURE`

### Q1500 -> KN1475
- management code: Q1500-B-8-P
- source question: diseases that may accompany sensory impairment, two choices
- official answer: 2 and 5
- explanation contract: multiple sclerosis can produce sensory impairment through CNS sensory-pathway lesions; CIDP is a peripheral demyelinating neuropathy that can include sensory impairment
- existing tags: `fact_recall / KNOW`

---

## Q1651 -> KN0966
- Category: B-8-O
- Safety: moderate
- Task: `assessment_selection`
- Primary ability: `MEASURE`
- Secondary ability: `INTERPRET`
- Level: 3
- Key: B
- Title: 急性心筋梗塞・心筋障害マーカー
- Theme: 急性心筋梗塞が疑われる症例で心筋障害を確認する血液検査を選ぶ
- Knowledge node: 急性心筋梗塞では心筋障害マーカーが上昇し、クレアチニンは心筋壊死マーカーではない
- Prerequisites: 心筋トロポニン, 急性心筋梗塞, 心筋障害マーカー, 腎機能

### Stem
68歳の男性。1時間前から持続する前胸部痛と冷汗を認め救急搬送された。12誘導心電図で急性心筋梗塞が疑われている。心筋障害の有無を血液検査で確認するため、最も優先して測定すべき項目はどれか。

### Choices
A. クレアチニン
B. 心筋トロポニン
C. Dダイマー
D. BNP
E. CRP

### Rationale
心筋トロポニンは心筋障害を評価する中心的な血液マーカーであり、急性心筋梗塞が疑われる症例で優先して確認する。クレアチニンは腎機能指標で、心筋壊死そのものを示すマーカーではない。発症早期では単回の陰性値だけで急性心筋梗塞を除外せず、臨床状況に応じて経時的評価が必要であることを解説に明記する。

### STRONG requirement
- Q1651 vs Q976 = `different_question_strong`
- No classifier change
- No reviewed STRONG-pair override

---

## Q1652 -> KN0988
- Category: C-15-O
- Safety: none
- Task: `finding_interpretation`
- Primary ability: `INTERPRET`
- Secondary ability: `KNOW`
- Level: 3
- Key: C
- Title: 鶏歩・総腓骨神経麻痺
- Theme: 下垂足と感覚・筋力所見から鶏歩の原因を局在する
- Knowledge node: 鶏歩は足関節背屈筋麻痺で生じ、総腓骨神経麻痺が代表的原因である
- Prerequisites: 総腓骨神経, 足関節背屈筋, 下垂足, 鶏歩, 感覚分布

### Stem
54歳の男性。長時間のしゃがみ作業後から右足が引っかかりやすくなった。歩行では右遊脚期に股関節と膝関節を過度に屈曲して足尖を持ち上げる。右足関節背屈MMT1、外反MMT2、内反MMT5、底屈MMT5で、下腿外側から足背に感覚低下を認める。最も考えられる障害はどれか。

### Choices
A. 右大腿神経障害
B. 右脛骨神経障害
C. 右総腓骨神経障害
D. 右上殿神経障害
E. 右閉鎖神経障害

### Rationale
足関節背屈と外反が低下し、内反と底屈が保たれ、下腿外側〜足背の感覚低下を伴う所見は総腓骨神経障害に整合する。下垂足を補うため遊脚期に股・膝屈曲を増やす鶏歩が生じる。L5神経根障害なども下垂足の鑑別に入るが、本問では末梢神経局在を支持する筋力・感覚分布を提示して曖昧さを避ける。

### STRONG requirement
- Q1652 vs Q998 = `different_question_strong`
- No classifier change
- No reviewed STRONG-pair override

---

## Q1653 -> KN1029
- Category: A-3-O
- Safety: none
- Task: `finding_interpretation`
- Primary ability: `INTERPRET`
- Secondary ability: `KNOW`
- Level: 2
- Key: B
- Title: 障害受容・否認期の場面解釈
- Theme: 障害受容5段階モデルの言動から否認期を解釈する
- Knowledge node: 障害受容過程ではショック期の後に否認期が続くと整理される
- Prerequisites: ショック, 否認, 混乱, 解決への努力, 受容

### Stem
障害受容を「ショック、否認、混乱、解決への努力、受容」の5段階で整理するモデルを用いる。脊髄損傷後の患者が「すぐ完全に元どおりになるはずだから、退院後の手すりや生活上の工夫を考える必要はない」と話している。この言動が最も当てはまる段階はどれか。

### Choices
A. ショック
B. 否認
C. 混乱
D. 解決への努力
E. 受容

### Rationale
障害やその持続性を現実として認めず、必要な対応を不要と捉える言動は、この5段階モデルでは否認期に対応する。心理的適応は個人差が大きく、実際には必ずしも直線的・一方向に進行するものではないことを解説に明記する。

### STRONG requirement
- Q1653 vs Q1039 = `different_question_strong`
- Do not change the KN1029/KN1151 canonical map in this batch
- No classifier change
- No reviewed STRONG-pair override

---

## Q1654 -> KN1470
- Category: A-3-O
- Safety: none
- Task: `finding_interpretation`
- Primary ability: `INTERPRET`
- Secondary ability: `MEASURE`
- Level: 3
- Key: B
- Title: BDI-II・結果の位置づけ
- Theme: BDI-II結果を自己記入式の抑うつ症状評価として解釈する
- Knowledge node: BDI-IIは本人が回答する自己記入式質問紙で、抑うつ症状の程度を評価する
- Prerequisites: BDI-II, 質問紙法, 自己記入式, 抑うつ症状, 診断と評価

### Stem
抑うつ症状が疑われる患者がBDI-IIに自分で回答し、高い得点を示した。この結果の解釈として最も適切なのはどれか。

### Choices
A. 評価者面接だけで判定されたため、本人の主観は反映されていない
B. 本人が回答した抑うつ症状の程度を把握する資料となるが、この結果だけで疾患の診断を確定するものではない
C. 認知機能障害の重症度を直接診断する検査である
D. 躁症状の重症度だけを評価する尺度である
E. 運動機能障害の程度を客観的に測定する尺度である

### Rationale
BDI-IIは自己記入式質問紙で、本人が経験する抑うつ症状の程度を把握するために用いる。尺度の結果は臨床評価の一部であり、単独で精神疾患の診断を確定するものとして扱わない。数値cutoffを新たな必須知識にせず、source Nodeの中心概念を保つ。

### STRONG requirement
- Q1654 vs Q1495 = `different_question_strong`
- No classifier change
- No reviewed STRONG-pair override

---

## Q1655 -> KN1475
- Category: B-8-O
- Safety: none
- Task: `finding_interpretation`
- Primary ability: `INTERPRET`
- Secondary ability: `KNOW`
- Level: 3
- Key: D
- Title: CIDP・末梢性脱髄の所見
- Theme: 感覚障害と神経学的所見からCIDPの末梢性脱髄を解釈する
- Knowledge node: 多発性硬化症は中枢神経の脱髄、CIDPは末梢神経の脱髄性ニューロパチーで、いずれも感覚症状を生じ得る
- Prerequisites: CIDP, 多発性硬化症, 末梢神経伝導, 腱反射, 感覚障害

### Stem
48歳の男性。2か月以上かけて両下肢優位の筋力低下と四肢末端のしびれが進行している。腱反射は四肢で低下し、神経伝導検査では複数神経で伝導速度低下と遠位潜時延長を認める。最も考えられる病態はどれか。

### Choices
A. 神経筋接合部障害
B. 筋原性疾患
C. 中枢神経の脱髄性疾患
D. 末梢神経の脱髄性ニューロパチー
E. 錐体外路障害

### Rationale
進行性の筋力低下と感覚症状、腱反射低下、複数末梢神経での脱髄性神経伝導所見はCIDPなどの末梢性脱髄性ニューロパチーを支持する。多発性硬化症は中枢神経の脱髄疾患であり、感覚症状はあり得るが、末梢神経伝導の脱髄所見と全般的腱反射低下を本問の主所見として説明しにくい。

### STRONG requirement
- Q1655 vs Q1500 = `different_question_strong`
- No classifier change
- No reviewed STRONG-pair override

---

## Required implementation contract
Add Q1651-Q1655 consistently to:
- `data/question_bank/questions.json`
- `data/question_bank/answers.json`
- `data/question_bank/explanations.json`
- `data/question_bank/question_tags.json`
- `data/question_bank/knowledge_nodes.json` or other existing registries only where the current extension pattern requires it
- head/count/audit artifacts and focused tests required by the existing repository contract

Do not edit source questions Q976/Q998/Q1039/Q1495/Q1500 or Q1-Q1650 canonical content.

## Focused QA contract
Focused tests must assert:
1. exact mapping, task, primary/secondary ability, key and safety for Q1651-Q1655;
2. `different_question_strong` for:
   - Q976 -> Q1651
   - Q998 -> Q1652
   - Q1039 -> Q1653
   - Q1495 -> Q1654
   - Q1500 -> Q1655
3. classifier source remains unchanged;
4. no reviewed STRONG override added for these five pairs;
5. canonical map remains unchanged, including no KN1029/KN1151 change;
6. validator passes through Q1655 with gaps/duplicates/reference/cross-file errors 0;
7. full pytest passes apart from any already-known explicitly documented unmanaged fixture exception.
