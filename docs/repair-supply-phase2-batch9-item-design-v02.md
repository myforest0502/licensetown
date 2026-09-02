# Repair Supply Phase2 batch9 item design v0.2

## Purpose
Create five materially different STRONG alternate questions for the highest-priority currently blocked repairing Nodes from the latest Production `PHASE11_PROMOTION_EVIDENCE_V1` after Q1645.

Priority order used:
1. KN1151 — tier B, cycle_wrong=5, confident_wrong=2, distinct_wrong_q=3
2. KN0067 — tier D, cycle_wrong=2, distinct_wrong_q=2
3. KN0534 — tier D, cycle_wrong=2, distinct_wrong_q=2
4. KN0652 — tier D, cycle_wrong=2, distinct_wrong_q=2
5. KN0545 — tier D, cycle_wrong=2

Do not change existing canonical content Q1-Q1645. Do not add reviewed STRONG-pair overrides merely to force the classifier.

---

## Q1646 -> KN1151
- Source family: Q1164 / Q1221 / Q1612
- Category: A-3-O
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: KNOW
- Level: 3
- Key: E
- Title: 障害受容・受容期
- Theme: 長期経過の語りから障害受容モデルの受容期を解釈する
- Knowledge node: 障害受容の5段階はショック、否認、混乱、解決への努力、受容の順

### Stem
障害受容を「ショック、否認、混乱、解決への努力、受容」の5段階で整理するモデルを用いる。脊髄損傷から1年が経過した患者は、職場復帰後も残る身体機能の制約を理解し、「できないことは残るけれど、今の身体での生活が自分の日常になった。必要な工夫を続けながら、この生活でやっていく」と話している。現在の段階として最も当てはまるのはどれか。

### Choices
A. ショック期
B. 否認期
C. 混乱期
D. 解決への努力期
E. 受容期

### Rationale
提示されたモデルでは、現実を前提に具体的な工夫を探す「解決への努力」を経て、障害を含む現在の自分と生活を受け入れていく段階を「受容」と整理する。本問はQ1164/Q1221の順序直接再生ではなく、またQ1612の「解決への努力期」の場面とも異なり、長期経過の語りから受容期を解釈させる。実際の心理過程は個人差が大きく、必ず直線的に進むものではないことを解説に明記する。

### STRONG requirement
- Q1646 vs Q1164 = different_question_strong
- Q1646 vs Q1221 = different_question_strong
- Q1646 vs Q1612 = different_question_strong
- Existing Q1164/Q1221/Q1612 relationships must not be artificially upgraded by override.

---

## Q1647 -> KN0067
- Source family: Q67 / Q1567
- Category: C-15-O
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: MEASURE
- Level: 3
- Key: B
- Title: 股関節伸展制限・対側歩幅
- Theme: 歩行所見とROMから立脚終期の股関節伸展制限による対側歩幅減少を解釈する
- Knowledge node: 股関節伸展制限は立脚終期の運動連鎖を妨げ、反対側歩幅を短縮させ得る

### Stem
右THA後の患者。Trendelenburg徴候は陰性、右股関節外転筋MMTは5である。右股関節伸展ROMは−10°で、歩行では右立脚終期が短く、左歩幅が小さい。これらの所見を最もよく説明するのはどれか。

### Choices
A. 右股関節外転筋力低下が骨盤を下制させ、左歩幅を短縮している
B. 右股関節伸展不足で立脚終期の前方進行が制限され、左下肢の前方振り出し量が減っている
C. 左足関節背屈筋麻痺により右立脚終期だけが短縮している
D. 右肩関節可動域制限により左歩幅だけが短縮している
E. 右股関節屈曲可動域の過大により左遊脚が停止している

### Rationale
右股関節伸展制限により右立脚終期で十分な股関節伸展と骨盤・体幹の前方進行が得られにくく、反対側である左下肢を十分に前方へ送り出せないため左歩幅が短くなり得る。外転筋MMT5かつTrendelenburg陰性なので外転筋力低下を主因とする根拠は乏しい。本問はQ67の「優先評価項目を選ぶ」需要、Q1567の「ROMから歩行特徴を予測する」需要から、複数所見を統合して機序を解釈する需要へ変える。

### STRONG requirement
- Q1647 vs Q67 = different_question_strong
- Q1647 vs Q1567 = different_question_strong

---

## Q1648 -> KN0534
- Source family: Q542 / Q1591
- Category: A-1-O
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: KNOW
- Level: 2
- Key: C
- Title: 対光反射・瞳孔括約筋
- Theme: 明所での縮瞳から虹彩の瞳孔括約筋収縮を解釈する
- Knowledge node: 虹彩には瞳孔散大筋と瞳孔括約筋があり、括約筋は瞳孔を縮小させる

### Stem
暗所から明るい場所へ移動すると瞳孔径が小さくなった。この変化を直接生じさせる虹彩の筋として最も適切なのはどれか。

### Choices
A. 瞳孔散大筋
B. 毛様体筋
C. 瞳孔括約筋
D. 上直筋
E. 眼輪筋

### Rationale
明所では瞳孔括約筋が収縮して縮瞳する。瞳孔散大筋は散瞳に作用する。Q542/Q1591は「虹彩にどの筋があるか」を直接再生する問題だが、本問は観察された瞳孔径変化から作用筋を解釈させる。

### STRONG requirement
- Q1648 vs Q542 = different_question_strong
- Q1648 vs Q1591 = different_question_strong
- Existing Q542/Q1591 relationship is not to be changed by override.

---

## Q1649 -> KN0652
- Source family: Q660 / Q1308
- Category: C-18-O
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: MEASURE
- Level: 3
- Key: D
- Title: Friedフレイル基準・症例解釈
- Theme: 症例の5所見からFried身体的フレイル表現型を解釈する
- Knowledge node: Friedの身体的フレイル基準は体重減少、疲労感、筋力低下、歩行速度低下、身体活動低下を評価する

### Stem
高齢者の評価で、意図しない体重減少、強い疲労感、握力低下、歩行速度低下を認めた。一方、身体活動量は保たれている。Friedの身体的フレイル表現型に基づく解釈として最も適切なのはどれか。

### Choices
A. 該当項目は0項目なのでrobustである
B. 該当項目は1項目なのでfrailである
C. 該当項目は2項目なのでfrailである
D. 4項目に該当するためfrailに相当する
E. 身体活動量が保たれていれば他の4項目は評価しない

### Rationale
Fried基準では、体重減少、疲労感、筋力低下、歩行速度低下、身体活動低下の5項目をみる。本例は前4項目に該当し、3項目以上なのでfrailに相当する。Q660/Q1308は個々の特徴・基準項目を直接選ぶ問題だが、本問は症例所見を基準に当てはめて表現型を解釈させる。

### STRONG requirement
- Q1649 vs Q660 = different_question_strong
- Q1649 vs Q1308 = different_question_strong
- Q660 official multiple-answer contract must remain unchanged.

---

## Q1650 -> KN0545
- Source: Q553
- Category: C-13-O
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: KNOW
- Level: 3
- Key: A
- Title: 薄筋・股関節内転
- Theme: 股関節内転と膝関節屈曲をまたぐ筋の臨床所見から薄筋を同定する
- Knowledge node: 薄筋は股関節内転に作用し、膝関節もまたぐ

### Stem
大腿内側の筋損傷後、股関節内転が弱くなり、膝関節屈曲にも軽度の筋力低下がみられた。損傷筋は股関節と膝関節の両方をまたぎ、脛骨近位内側の鵞足に停止する。この筋はどれか。

### Choices
A. 薄筋
B. 長内転筋
C. 短内転筋
D. 大内転筋
E. 腸腰筋

### Rationale
薄筋は股関節を内転し、膝関節をまたいで脛骨近位内側の鵞足に停止するため膝屈曲にも関与する。長内転筋・短内転筋・大内転筋は膝関節をまたがず、腸腰筋は主に股関節屈曲に作用する。Q553の単純な運動―筋の組合せ再生から、二関節筋としての解剖学的特徴と機能を統合して筋を同定する需要へ変える。

### STRONG requirement
- Q1650 vs Q553 = different_question_strong

---

## Implementation / QA contract
- Extend all canonical Question Bank stores consistently through Q1650.
- Keep Q1-Q1645 questions/answers/explanations/tags byte-equivalent in semantic content except unavoidable array extension / registry head changes.
- Preserve all existing official accepted-answer sets, especially Q660.
- Add only legitimate registry/schema/head/test-count changes.
- No reviewed STRONG-pair override for test passage.
- Focused tests must verify exact Node/task/primary ability/key and required STRONG pairs.
- Full pytest PASS; only the known unmanaged UTF fixture may be explicitly deselected if still absent.
- Question Bank validator PASS: Q1-Q1650, no gap/duplicate/schema/reference/cross-file error.
- No Phase11 ranking change, Phase10 selector change, Node state transition change, DB schema/write, learner-facing recommendation change, Production or Render operation.
- Draft PR only; manual medical/content review required before merge.
