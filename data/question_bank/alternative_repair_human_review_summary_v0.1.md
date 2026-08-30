# ⑩-D Alternative Repair Human Review v0.1

## 1. KN0238
- Target label: Fickの原理による酸素摂取量の算出
- Problem A (Q239): 運動中の心拍出量が10L/分、動静脈酸素較差が100mL/Lであった。Fickの原理から求める酸素摂取量はどれか。
- Answer / explanation A: E / Fickの原理では、酸素摂取量は心拍出量と動静脈酸素較差の積で求める。単位をそろえると、10L/分×100mL/L＝1,000mL/分となる。運動時の酸素摂取量は、循環による酸素運搬量と末梢組織での酸素抜き取りの双方で決まる。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q475, PREREQUISITE): 心肺運動負荷試験で用いる酸素脈〈VO2/HR〉が主に反映するのはどれか。
- Answer / explanation B: E / 酸素脈〈VO₂/HR〉は1心拍あたりの酸素摂取量を表す。Fickの原理から、心拍出量＝心拍数×一回拍出量であるため、VO₂/HRは一回拍出量と動静脈酸素較差の積を反映する。運動中の循環応答を見る指標として用いられる。
- B metadata: task=finding_interpretation, primary=INTERPRET, secondary=None, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN

## 2. KN0259
- Target label: MIPが反映する吸気筋力
- Problem A (Q260): 最大吸気口腔内圧〈MIP〉が主に反映するのはどれか。
- Answer / explanation A: B / MIPは閉鎖されたマウスピースに対して最大吸気努力を行った際の陰圧で、横隔膜など吸気筋の総合的な筋力指標である。MEPは呼気筋力を反映する。類題では圧の最大値は筋力、スパイロメトリーの流量は気流制限、DLCOは拡散能と区別する。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q386, PREREQUISITE): 安定期COPD患者にthreshold deviceを用いた吸気筋トレーニングを開始する。最大吸気口腔内圧〈MIP〉が60 cmH₂Oであった。初期負荷をMIPの30％に設定する場合はどれか。
- Answer / explanation B: A / MIP 60 cmH₂Oの30％は、60×0.30＝18 cmH₂Oである。吸気筋トレーニングでは測定の再現性を確認し、患者の息切れ、疲労、呼吸パターンを監視しながら開始する。一定期間ごとにMIPと症状を再評価し、耐容性に応じて負荷や時間を漸増する。数値だけでなく正しい機器操作も確認する。
- B metadata: task=intervention_selection, primary=PRESCRIBE, secondary=None, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN

## 3. KN0305
- Target label: 口すぼめ呼吸による呼気時気道内圧維持と気道虚脱抑制
- Problem A (Q307): COPD患者に口すぼめ呼吸を指導する主な目的はどれか。
- Answer / explanation A: B / 口すぼめ呼吸は呼気抵抗をつくり、呼気時の気道内圧を保って末梢気道の動的虚脱を抑え、呼気を延長する。閉塞性障害では「吐きやすくする」機序を理解する。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q1397, PREREQUISITE): 口すぼめ呼吸の指導で正しいのはどれか。
- Answer / explanation B: 3 / 口すぼめ呼吸はCOPDで呼気時の気道虚脱を防ぎ、呼気を延長する。
- B metadata: task=intervention_selection, primary=PRESCRIBE, secondary=INTERPRET, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Problem B (Q1013, PREREQUISITE): 呼吸障害に対する理学療法として、口すぼめ呼吸が有効なのはどれか。
- Answer / explanation B: 1 / COPDでは口すぼめ呼吸により呼気時の気道内圧を保ち、末梢気道の虚脱を抑えて呼気を延長できる。
- B metadata: task=intervention_selection, primary=PRESCRIBE, secondary=None, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN

## 4. KN0358
- Target label: ACBTの呼吸コントロール・胸郭拡張・強制呼出法
- Problem A (Q362): 気管支拡張症患者に自律的な排痰法としてactive cycle of breathing techniques〈ACBT〉を指導する。ACBTを構成する基本的な組合せはどれか。
- Answer / explanation A: B / ACBTは、安静で力みの少ない呼吸コントロール、深吸気と必要に応じた吸気保持を用いる胸郭拡張運動、低～中肺気量からのハフィングを中心とする強制呼出手技で構成する。これらを循環させ、末梢から中枢へ分泌物を移動させる。強い咳だけを反復すると疲労や気道虚脱を招くことがある。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q223, PREREQUISITE): 74歳の男性。気管支拡張症である。朝方に多量の喀痰を認め、自力での排痰が困難となっている。SpO₂は95％で全身状態は安定している。理学療法として最も適切なのはどれか。
- Answer / explanation B: A / 気管支拡張症で喀痰が多く、自力排痰が困難である。全身状態は安定しているため、Active Cycle of Breathing Techniques（ACBT）による気道クリアランスが適切である。
- B metadata: task=intervention_selection, primary=PRESCRIBE, secondary=None, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN

## 5. KN0666
- Target label: Bohr効果により酸素解離曲線が右方移動し、ヘモグロビンから酸素が解離しやすくなる / 組織でpHが低下すると酸素解離曲線が右方移動し、ヘモグロビンから酸素が放出されやすくなるBohr効果が起こる
- Problem A (Q674): 末梢組織への酸素供給を増やすのはどれか。
- Answer / explanation A: 1 / 組織でpHが低下すると酸素解離曲線が右方移動し、ヘモグロビンから酸素が放出されやすくなるBohr効果が起こる。したがって1が正しい。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q318, PREREQUISITE): 発熱と代謝性アシドーシスがある患者で、ヘモグロビン酸素解離曲線に生じる変化はどれか。
- Answer / explanation B: A / 体温上昇とアシドーシスによる水素イオン濃度上昇はいずれも、ヘモグロビン酸素解離曲線を右方へ移動させる。右方移動ではヘモグロビンの酸素親和性が低下し、同じ酸素分圧でも末梢組織へ酸素を放出しやすくなる。発熱と代謝性アシドーシスが同方向に作用する点が判断の決め手である。
- B metadata: task=finding_interpretation, primary=INTERPRET, secondary=None, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN

## 6. KN0737
- Target label: アドレナリンは肝・筋のグリコーゲン分解や糖新生を促進し、血糖を上昇させる
- Problem A (Q745): 血糖を上昇させる作用のあるホルモンはどれか。
- Answer / explanation A: 1 / アドレナリンは肝・筋のグリコーゲン分解や糖新生を促進し、血糖を上昇させる。したがって1が正しい。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q1209, PREREQUISITE): 血糖を上昇させる作用のあるホルモンはどれか。2つ選べ。
- Answer / explanation B: 1・4 / アドレナリンとグルカゴンはいずれも肝グリコーゲン分解や糖新生を促し血糖を上昇させる。
- B metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN

## 7. KN0922
- Target label: Trendelenburg徴候は股関節外転筋機能不全で生じ、変形性股関節症で中殿筋機能低下を伴うと出現しやすい / 変形性股関節症では股関節外転筋機能低下によりTrendelenburg徴候がみられる
- Problem A (Q931): Trendelenburg徴候が生じやすいのはどれか。
- Answer / explanation A: 1 / Trendelenburg徴候は股関節外転筋機能不全で生じ、変形性股関節症で中殿筋機能低下を伴うと出現しやすい。1が正しい。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q112, PREREQUISITE): 67歳の女性。右変形性股関節症で保存療法中である。歩行開始時に右股関節痛を認めるが、歩行を続けると軽減する。Trendelenburg徴候は陽性で、股関節外転筋MMT3である。股関節屈曲可動域は110°、脚長差は認めない。歩行能力改善を目的として最も優先すべき介入はどれか。
- Answer / explanation B: A / Trendelenburg徴候陽性で股関節外転筋MMT3であり、右立脚期の骨盤支持能力が低下している。脚長差はなく、屈曲ROMも110°保たれているため、歩行能力改善には外転筋機能を高め、片脚支持時に骨盤を水平に制御する練習を優先することが適切である。
- B metadata: task=intervention_selection, primary=PRESCRIBE, secondary=INTERPRET, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN

## 8. KN0992
- Target label: 脊髄性運動失調では深部感覚障害を視覚で代償するため、閉眼で動揺が増えるRomberg徴候陽性が典型的である
- Problem A (Q1002): 脊髄性運動失調症でみられるのはどれか。
- Answer / explanation A: 5 / 脊髄性運動失調では深部感覚障害を視覚で代償するため、閉眼で動揺が増えるRomberg徴候陽性が典型的である。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q306, PREREQUISITE): 開眼では立位を保てるが、閉眼すると動揺が著明に増大する。主に障害が疑われるのはどれか。
- Answer / explanation B: E / 閉眼で動揺が増えるRomberg徴候陽性は、視覚で代償されていた深部感覚障害を示し、脊髄後索系障害を疑う。小脳性運動失調では開眼時から不安定になりやすい。
- B metadata: task=finding_interpretation, primary=INTERPRET, secondary=None, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN

## 9. KN1138
- Target label: 過換気ではCO2が過剰に排出されPaCO2が低下し、呼吸性アルカローシスとなる
- Problem A (Q1150): 酸塩基平衡で正しいのはどれか。
- Answer / explanation A: 3 / 過換気ではCO2が過剰に排出されPaCO2が低下し、呼吸性アルカローシスとなる。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q246, TRANSFER): 安定期COPD患者の動脈血液ガス分析は、pH 7.37、PaCO2 60mmHg、HCO3－ 32mEq/Lであった。酸塩基平衡の判定で最も適切なのはどれか。
- Answer / explanation B: A / PaCO2上昇は呼吸性アシドーシス方向の変化で、HCO3－上昇は腎による代償を示す。pHは正常範囲内でも7.40より酸性側であり、安定期COPDという経過から慢性の代償性呼吸性アシドーシスと判断する。類題ではpH、PaCO2、HCO3－の順に主病態と代償方向を確認する。
- B metadata: task=finding_interpretation, primary=INTERPRET, secondary=None, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN

## 10. KN1155
- Target label: 神経性間欠性跛行が特徴で、腰椎屈曲で症状が軽減し、伸展で増悪しやすい
- Problem A (Q1168): 腰部脊柱管狭窄症で正しいのはどれか。
- Answer / explanation A: 3 / 腰部脊柱管狭窄症では神経性間欠性跛行が特徴で、腰椎屈曲で症状が軽減し、伸展で増悪しやすい。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q867, PREREQUISITE): 腰椎変性すべり症で歩行中に殿部から下肢にかけて疼痛が出現したときの対応で正しいのはどれか。
- Answer / explanation B: 1 / 腰椎変性すべり症では腰部脊柱管狭窄による神経性間欠性跛行を伴うことが多く、腰椎屈曲で症状が軽減する。歩行中に痛みが出たらしゃがみ込むのが有効で1が正しい。
- B metadata: task=intervention_selection, primary=PRESCRIBE, secondary=INTERPRET, safety=moderate
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Problem B (Q284, PREREQUISITE): 歩行で両下肢痛が出現するが、自転車走行では症状が軽い。最も考えられるのはどれか。
- Answer / explanation B: C / 腰部脊柱管狭窄症の神経性間欠跛行は腰椎伸展で悪化し、前屈位となる自転車や手押し車で軽減しやすい。類題では運動量より姿勢依存性を鑑別点にする。
- B metadata: task=finding_interpretation, primary=INTERPRET, secondary=None, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN

## 11. KN1391
- Target label: 自律神経の節前線維末端では交感・副交感ともアセチルコリンが放出される
- Problem A (Q1416): 自律神経で正しいのはどれか。
- Answer / explanation A: 5 / 自律神経の節前線維末端では交感・副交感ともアセチルコリンが放出される。
- A metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Problem B (Q1485, PREREQUISITE): 交感神経で正しいのはどれか。
- Answer / explanation B: 5 / 交感神経節前線維末端からはアセチルコリンが放出される。
- B metadata: task=fact_recall, primary=KNOW, secondary=None, safety=none
- Relation reason: The relation metadata says the candidate question requires or transfers the repair target concept, but that claim still needs human review.
- Risk: A learner may answer from the target question's surrounding knowledge without demonstrating the source Node itself.
- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)
- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN
