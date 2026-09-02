# Repair Supply Phase2 batch11 item design v0.1

Date: 2026-09-02

## Purpose
Create five materially different STRONG alternate questions for the next five Production repair-supply targets after Batch10.

Production target order supplied by the latest post-Batch10 diagnostics:
1. KN1523 — source Q1549 — 失血性ショックの末梢血管抵抗
2. KN1525 — source Q1551 — 心気妄想
3. KN0001 — source Q1 — 立脚後期の下腿三頭筋と前方推進
4. KN0072 — source Q72 — アキレス腱修復後の底屈筋機能
5. KN0198 — source Q199 — 中足骨頭部の荷重分散

Expected Production effect under the same learning history after implementation:
- strong_available: 37 -> 42
- blocked: 83 -> 78

Do not change Q1-Q1655 canonical content. Do not change `classify_repair_confirmation()`. Do not add reviewed STRONG-pair overrides merely to force tests.

All new questions inherit the exact source question's category and O/P source convention unless the existing repository contract requires another mechanically derived value.

---

## Q1656 -> KN1523
- Source: Q1549
- Safety: none unless the existing source tag contract requires otherwise
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: KNOW
- Level: 3
- Key: D
- Title: 失血性ショック・代償性末梢血管収縮
- Knowledge node: 失血性ショックでは交感神経性末梢血管収縮により末梢血管抵抗が上昇する

### Stem
交通外傷後に多量出血が疑われる患者。血圧82/48 mmHg、脈拍124/分で、四肢末梢は冷たく皮膚は蒼白である。失血に対する代償反応として最も考えられる循環動態はどれか。

### Choices
A. 末梢血管抵抗の低下
B. 皮膚血流量の増加
C. 静脈還流量の増加を伴う中心静脈圧上昇
D. 交感神経性血管収縮による末梢血管抵抗の上昇
E. 末梢血管拡張による拡張期血圧の低下

### Correct answer
D

### Rationale
失血で循環血液量が低下すると、圧受容器反射を介して交感神経活動が亢進し、皮膚・内臓などの末梢血管が収縮する。これにより全末梢血管抵抗は上昇し、重要臓器への灌流維持が図られる。冷感・蒼白は末梢血管収縮と整合する。失血そのものは静脈還流や中心静脈圧を低下させる方向に働く。本問はQ1549の事実再生から、症例の循環所見を統合して代償反応を解釈する要求へ変える。

### Choice notes
- A: 失血性ショックの初期代償では一般に逆方向である。
- B: 皮膚血流は末梢血管収縮により低下しやすい。
- C: 循環血液量低下では静脈還流・中心静脈圧は低下方向である。
- D: 正しい。
- E: 代償反応の中心は末梢血管拡張ではなく収縮である。

### STRONG requirement
- Q1656 vs Q1549 = different_question_strong under the existing classifier

---

## Q1657 -> KN1525
- Source: Q1551
- Safety: none unless the existing source tag contract requires otherwise
- Task: assessment_selection
- Primary ability: MEASURE
- Secondary ability: INTERPRET
- Level: 3
- Key: B
- Title: 心気妄想・確信の訂正困難性評価
- Knowledge node: 重い身体疾患にかかっているという訂正困難な確信は心気妄想として評価される

### Stem
身体検査や画像検査で重篤な異常を認めない患者が、「自分は末期がんに違いない」と繰り返し訴えている。通常の健康不安ではなく心気妄想として評価するうえで、追加して確認する内容として最も重要なのはどれか。

### Choices
A. これまで受診した医療機関の数
B. 十分な説明や客観的な陰性所見を示されても確信が訂正されないか
C. 家族に悪性腫瘍の既往があるか
D. 現在の身体症状を0〜10で評価したときの強さ
E. 1日の睡眠時間が何時間か

### Correct answer
B

### Rationale
妄想を評価する際には、内容だけでなく、客観的根拠や十分な説明に対しても確信が修正されにくいという訂正困難性が重要である。心気妄想では、重篤な身体疾患に罹患しているという強固な確信がみられる。受診回数、家族歴、症状強度、睡眠時間だけでは妄想性の確信かどうかを判定できない。本問はQ1551の症状名判定から、心気妄想を評価するために何を追加確認するかという評価選択へ変える。

### Choice notes
- A: 医療利用状況は参考になるが、妄想の訂正困難性を直接評価しない。
- B: 正しい。
- C: 家族歴は疾患リスクの情報であり、妄想性確信の評価ではない。
- D: 身体症状の強さだけでは確信の質を判定できない。
- E: 睡眠は精神状態把握に有用な場合があるが、本問の核心ではない。

### STRONG requirement
- Q1657 vs Q1551 = different_question_strong

---

## Q1658 -> KN0001
- Source: Q1
- Safety: none
- Task: assessment_selection
- Primary ability: MEASURE
- Secondary ability: INTERPRET
- Level: 3
- Key: C
- Title: 立脚終期・足関節底屈パワー評価
- Knowledge node: 立脚後期では下腿三頭筋による足関節底屈モーメントとパワー発揮が前方推進に重要である

### Stem
歩行観察で立脚終期の蹴り出しが弱く、前方推進力の低下が疑われる。三次元動作解析を用いて下腿三頭筋による前方推進機能を定量化するとき、最も直接的に確認すべき指標はどれか。

### Choices
A. 荷重応答期の膝関節伸展モーメント
B. 立脚中期の股関節外転モーメント
C. 立脚終期の足関節底屈パワー
D. 遊脚中期の足関節背屈角度
E. 1分間のケイデンス

### Correct answer
C

### Rationale
正常歩行の立脚終期では、下腿三頭筋群の作用により足関節底屈モーメントが生じ、足関節で大きな正のパワーが発揮される。これは身体の前方推進に重要である。したがって、蹴り出し低下を定量化するには立脚終期の足関節底屈パワーが最も直接的である。本問はQ1の機序解釈から、前方推進低下を定量化する評価指標の選択へ変える。

### Choice notes
- A: 荷重応答期の衝撃吸収・支持に関係するが、立脚終期の蹴り出しを直接表さない。
- B: 骨盤の前額面安定性に関係する。
- C: 正しい。
- D: 足尖クリアランスには関係するが、立脚終期の前方推進を直接表さない。
- E: 全体的な歩行リズムであり、底屈筋の推進機能を直接測定しない。

### STRONG requirement
- Q1658 vs Q1 = different_question_strong

---

## Q1659 -> KN0072
- Source: Q72
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: MEASURE
- Level: 3
- Key: A
- Title: アキレス腱修復後・片脚踵上げ所見解釈
- Knowledge node: アキレス腱修復後の片脚踵上げ回数と挙上高低下は足関節底屈筋の筋力・筋持久力低下を示唆する

### Stem
アキレス腱修復術後14週の患者。通常歩行は自立しているが、小走りでは蹴り出しが弱い。患側の片脚踵上げは5回で疲労し、反復するにつれて踵の挙上高も低下した。この所見から最も考えられる機能障害はどれか。

### Choices
A. 足関節底屈筋の筋力・筋持久力低下
B. 足関節背屈筋の選択的筋力低下
C. 大腿四頭筋の遠心性収縮不足
D. 中殿筋の筋力低下による骨盤不安定性
E. 深部感覚障害のみ

### Correct answer
A

### Rationale
片脚踵上げは下腿三頭筋を中心とした足関節底屈筋機能をみる代表的な課題である。反復回数が少なく、反復に伴い挙上高が低下する所見は、底屈筋の筋力・筋持久力不足を示唆し、立脚終期の蹴り出し低下とも整合する。本問はQ72の「何を評価するか」という評価手段の選択から、実際に得られた片脚踵上げ所見を機能障害として解釈する要求へ変える。

### Choice notes
- A: 正しい。
- B: 背屈筋低下は主に遊脚期の足尖クリアランス低下と関連する。
- C: 膝伸展機能の所見ではない。
- D: Trendelenburg徴候などの骨盤不安定性の所見は提示されていない。
- E: 感覚障害だけでは反復踵上げの回数・高さ低下を最もよく説明しない。

### STRONG requirement
- Q1659 vs Q72 = different_question_strong

---

## Q1660 -> KN0198
- Source: Q199
- Safety: none
- Task: finding_interpretation
- Primary ability: INTERPRET
- Secondary ability: MEASURE
- Level: 3
- Key: E
- Title: 中足骨頭部・足底圧除圧効果の解釈
- Knowledge node: 中足骨頭部痛では足底圧を用いて中足骨頭部への局所荷重が減少しているかを評価できる

### Stem
第2・3中足骨頭部に胼胝と歩行時痛がある患者に、中足骨頭部の除圧を目的としたパッドを使用した。歩行時足底圧を比較すると、パッド使用後は第2・3中足骨頭部のピーク圧が低下し、荷重が周囲へ分散していた。この結果の解釈として最も適切なのはどれか。

### Choices
A. 中足骨頭部への局所荷重が増加した
B. 足趾把持力が必ず正常化した
C. 足関節背屈可動域が改善したことを直接示す
D. 疼痛の原因が神経障害であることを確定できる
E. 中足骨頭部への局所荷重を分散する除圧効果が得られた

### Correct answer
E

### Rationale
足底圧で第2・3中足骨頭部のピーク圧が低下し、周囲へ荷重が分散していれば、対象部位への局所荷重を減らす除圧効果が得られたと解釈できる。足底圧データだけで足趾把持力や足関節可動域の改善、疼痛原因の確定まではできない。パッドの除圧効果は設置位置や個人差によって変わるため、作製・適合後には対象部位の足底圧分布を再評価し、固定した効果を前提にしない。本問はQ199の装具・パッドの目的選択から、介入前後の足底圧データを解釈する要求へ変える。

### Choice notes
- A: 測定結果と逆である。
- B: 足底圧低下から足趾把持力正常化を断定できない。
- C: 足底圧は足関節背屈ROM改善を直接示さない。
- D: 圧分布だけで疼痛原因を確定できない。
- E: 正しい。

### STRONG requirement
- Q1660 vs Q199 = different_question_strong

---

## Medical/content review conditions
Before implementation/merge, review all five items against the actual source questions/tags and the current repository conventions.

Required safeguards:
- Q1656: do not imply all hemorrhagic shock phases always have identical SVR behavior; the item is explicitly about the early compensatory sympathetic response.
- Q1657: do not diagnose a delusion from health concern alone. The item must retain the criterion-like emphasis on fixed/poorly correctable conviction despite adequate contrary evidence.
- Q1658: do not equate ankle power with a direct isolated muscle force measurement. It is the most direct gait-analysis proxy among the choices for late-stance push-off function.
- Q1659: do not infer tendon structural failure from heel-rise endurance findings alone; interpret as plantarflexor functional deficit.
- Q1660: do not infer pain etiology or unrelated ROM/strength changes from plantar-pressure redistribution alone. Metatarsal-pad effects vary with pad position and between individuals, so reassess the target plantar-pressure distribution after fabrication/fitting rather than assuming a fixed effect.

## Implementation / QA contract
- Extend canonical Question Bank stores consistently through Q1660.
- Keep Q1-Q1655 questions/answers/explanations/tags unchanged apart from extension and legitimate registry/schema/head/test-count updates.
- Preserve all existing official accepted-answer sets.
- Do not change `classify_repair_confirmation()`.
- Do not add reviewed STRONG-pair overrides for test passage.
- Focused Batch11 tests must verify exact Node/task/primary/secondary ability/key and all five required STRONG pairs bidirectionally.
- Add an invariant/digest check that Q1-Q1655 canonical content is unchanged.
- Full pytest PASS; only the known unmanaged UTF fixture may be explicitly deselected if still absent.
- Question Bank validator PASS through Q1660 with gaps/duplicates/schema/reference/cross-file errors 0.
- Run repairability-related tests and confirm the expected 37 -> 42 STRONG-supply increase under the same diagnostic history when measurable.
- No Phase11 ranking change, Phase10 selector change, Node-state transition change, DB schema/write, learner-facing recommendation change, Production or Render operation during implementation review.
- Keep the implementation PR Draft until formal content review and QA are complete.
