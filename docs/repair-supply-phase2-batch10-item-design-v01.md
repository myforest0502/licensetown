# Repair Supply Phase2 batch10 item design v0.1

## Purpose
Create five materially different STRONG alternate questions for the current top five blocked repairing Nodes from the latest Production `PHASE11_PROMOTION_EVIDENCE_V1` after Q1650.

Latest Production basis:
- repairing_nodes: 121
- strong_available: 32
- weak_only: 1
- blocked: 88
- repairable_rate: 26.4%
- Priority A/B/C: 0 / 0 / 0
- Priority D: 89

Targets:
1. KN0966 — source Q976 — cycle_wrong=2
2. KN0988 — source Q998 — cycle_wrong=2
3. KN1029 — source Q1039 — cycle_wrong=2
4. KN1470 — source Q1495 — cycle_wrong=2
5. KN1475 — source Q1500 — cycle_wrong=2

Do not change Q1-Q1650 canonical content. Do not change `classify_repair_confirmation()`. Do not add reviewed STRONG-pair overrides merely to force tests.

---

## Q1651 -> KN0966
- Source: Q976 (finding_interpretation / INTERPRET)
- Category: inherit B-8, source O
- Safety: none
- Task: assessment_selection
- Primary ability: MEASURE
- Secondary ability: INTERPRET
- Level: 3
- Key: B
- Title: 急性心筋梗塞・心筋障害マーカー選択
- Knowledge node: 急性心筋梗塞ではトロポニンT、ミオグロビン、CK、LDなど心筋障害マーカーが上昇し、クレアチニンは腎機能指標である

### Stem
胸痛発症から6時間後に急性心筋梗塞が疑われる患者で、心筋障害の有無を血液検査で評価したい。心筋壊死を反映する検査として最も優先して確認すべきものはどれか。

### Choices
A. 血清クレアチニン
B. 心筋トロポニンT
C. 血清ナトリウム
D. 総ビリルビン
E. 血清尿酸

### Rationale
心筋トロポニンTは心筋障害を反映する代表的バイオマーカーであり、急性心筋梗塞が疑われる場面で心筋壊死の評価に用いられる。クレアチニンは主に腎機能の指標であり、心筋壊死を直接評価する検査ではない。本問はQ976の「AMI後に上昇しない検査値を選ぶ」需要から、臨床場面で心筋障害評価に用いる検査を選択する需要へ変える。

### STRONG requirement
- Q1651 vs Q976 = different_question_strong under the existing classifier

---

## Q1652 -> KN0988
- Source: Q998 (fact_recall / KNOW)
- Category: inherit C-15, source O
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: KNOW
- Level: 3
- Key: C
- Title: 鶏歩・総腓骨神経麻痺
- Knowledge node: 鶏歩（steppage gait）は足関節背屈筋麻痺で生じ、総腓骨神経麻痺が代表的原因

### Stem
歩行観察で、右遊脚期に足尖が床へ引っかからないよう右股関節と膝関節を過剰に屈曲している。右足関節背屈筋力は著明に低下し、足背の感覚低下もみられる。この歩行と原因の組合せとして最も適切なのはどれか。

### Choices
A. はさみ脚歩行 ― 両側錐体路障害
B. 動揺性歩行 ― 股関節外転筋麻痺
C. 鶏歩 ― 総腓骨神経麻痺
D. 小刻み歩行 ― 小脳障害
E. 失調性歩行 ― 前庭神経だけの障害

### Rationale
足関節背屈筋力低下による下垂足では、遊脚期の足尖クリアランスを確保するため股・膝関節を過剰に屈曲する鶏歩を呈し得る。総腓骨神経麻痺は代表的原因で、足背の感覚障害を伴うこともある。Q998の歩行障害と原因の組合せを直接再生する問題から、歩行所見・筋力・感覚所見を統合して原因を解釈する問題へ変える。

### STRONG requirement
- Q1652 vs Q998 = different_question_strong
- Q998 official accepted-answer contract [["3","4"]] unchanged

---

## Q1653 -> KN1029
- Source: Q1039 (fact_recall / KNOW)
- Category: inherit A-3, source O
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: KNOW
- Level: 3
- Key: B
- Title: 障害受容・否認期
- Knowledge node: 障害受容過程はショック期の後に否認期が続くと整理される

### Stem
障害受容を「ショック、否認、混乱、解決への努力、受容」の5段階で整理するモデルを用いる。受傷直後の茫然とした時期を過ぎた患者が、「この障害はすぐ消えるはずだから、今は何も変える必要はない」と繰り返し話している。現在の段階として最も当てはまるのはどれか。

### Choices
A. ショック期
B. 否認期
C. 混乱期
D. 解決への努力期
E. 受容期

### Rationale
提示されたモデルでは、ショック期の後に現実を受け入れにくい否認期が続くと整理される。本例は受傷直後の茫然状態を過ぎた後も障害の持続を認めず対応を不要と考えており、否認期に当てはまる。実際の心理過程は個人差が大きく直線的とは限らない。本問はQ1039の順序直接再生ではなく、患者の語りから段階を解釈する。

### STRONG requirement
- Q1653 vs Q1039 = different_question_strong

---

## Q1654 -> KN1470
- Source: Q1495 (assessment_selection / MEASURE)
- Category: inherit A-3, source O
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: MEASURE
- Level: 3
- Key: D
- Title: BDI-II・自己記入式質問紙
- Knowledge node: BDI-IIはうつ症状について本人が回答する自己記入式質問紙

### Stem
外来患者の抑うつ症状を把握するため、本人に用紙を渡し、自分の症状について各項目を選んで回答してもらった。用いた尺度がBDI-IIであった場合、この評価法の特徴として最も適切なのはどれか。

### Choices
A. 評価者が面接して重症度を判定する他者評価尺度である
B. 認知機能を検査者が採点する認知症スクリーニングである
C. 精神症状を医療者が観察して採点する尺度である
D. 本人が抑うつ症状について回答する自己記入式質問紙である
E. 運動機能を理学療法士が実測する機能検査である

### Rationale
BDI-IIは抑うつ症状について本人が回答する自己記入式質問紙である。HAM-D、BPRS、PANSSなどの評価者による尺度とは実施形式が異なる。Q1495は「質問紙法はどれか」と尺度名を選ぶ需要だが、本問は実施場面からBDI-IIの評価形式を解釈する需要へ変える。

### STRONG requirement
- Q1654 vs Q1495 = different_question_strong

---

## Q1655 -> KN1475
- Source: Q1500 (fact_recall / KNOW)
- Category: inherit B-8, source O
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: KNOW
- Level: 3
- Key: A
- Title: MSとCIDP・感覚障害
- Knowledge node: 多発性硬化症は中枢神経の感覚路障害、CIDPは末梢神経障害で感覚障害を伴う

### Stem
感覚障害を伴う神経疾患について整理している。症例Aは中枢神経系の脱髄性病変を反復し、視覚症状と四肢の感覚障害がみられる。症例Bは慢性進行性の末梢神経脱髄により四肢筋力低下と感覚障害を呈している。症例Aと症例Bの組合せとして最も適切なのはどれか。

### Choices
A. 多発性硬化症 ― 慢性炎症性脱髄性多発ニューロパチー
B. 重症筋無力症 ― 筋萎縮性側索硬化症
C. 筋萎縮性側索硬化症 ― Duchenne型筋ジストロフィー
D. パーキンソン病 ― 重症筋無力症
E. 肢帯型筋ジストロフィー ― 筋萎縮性側索硬化症

### Rationale
多発性硬化症は中枢神経系の脱髄疾患で感覚路障害を伴い得る。CIDPは末梢神経の慢性炎症性脱髄性疾患で、運動障害に加えて感覚障害を伴う。Q1500は感覚障害を伴う疾患名を直接2つ選ぶ問題だが、本問は中枢・末梢の病態と臨床像を手掛かりに2疾患を解釈する。

### STRONG requirement
- Q1655 vs Q1500 = different_question_strong
- Q1500 official accepted-answer contract [["2","5"]] unchanged

---

## Implementation / QA contract
- Extend canonical Question Bank stores consistently through Q1655.
- Keep Q1-Q1650 questions/answers/explanations/tags unchanged apart from extension and legitimate registry/schema/head/test-count updates.
- Preserve all existing official accepted-answer sets, especially Q998 and Q1500.
- Do not change `classify_repair_confirmation()`.
- Do not add reviewed STRONG-pair overrides for test passage.
- Focused tests must verify exact Node/task/primary/secondary ability/key and all required STRONG pairs.
- Full pytest PASS; only known unmanaged UTF fixture may be explicitly deselected if still absent.
- Question Bank validator PASS through Q1655 with gaps/duplicates/schema/reference/cross-file errors 0.
- No Phase11 ranking change, Phase10 selector change, Node-state transition change, DB schema/write, learner-facing recommendation change, Production or Render operation.
- Draft PR only; manual medical/content review required before merge.
