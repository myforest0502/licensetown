# Question Bank 2000 Batch02 staging audit v01

## Scope / baseline

開始main: `9bd50710fed3bfee301d5a801c1b2feaf6f80a35`（PR #265 merge）。独立worktreeのgit statusはclean。正式範囲Q1–Q1749、original 655 / past_exam 1094。正式統合・Q ID予約・runtime/DB操作は行わない。

開始時: Question Bank validator PASS / schema-manifest checker PASS / CIと同じfull pytestは1140 passed, 1 deselected, 16 warnings, 125 subtests passed。ローカルはWindows/Python 3.13.14、GitHub ActionsはUbuntu/Python 3.13。依存はrequirements.txtとpytest、テスト用の環境変数と空のDATABASE_URLを使用。

## Selection / refreshed facts

参照済み: docs/question-bank-2000-audit-v01.md、reports/question_bank_2000_distribution_v01.csv、reports/question_bank_2000_gap_analysis_v01.json、reports/question_bank_2000_audit_v01.py。既存監査は1737問時点の凍結成果。旧スクリプトは1737固定assertと監査成果の上書きを含むため実行せず、現行4ストアとcanonical解決で再計算した。

現行canonical 1508、singleton 1294、multi 214、strongあり 160、weak-only 54。

| 分野 | 現行問題 | global singleton | strongありNode | 今回accepted |
|---|---|---|---|---|
| 神経医学 | 120 | 103 | 2 | 4 |
| 理学療法治療各論 | 306 | 270 | 7 | 3 |
| 理学療法評価各論 | 176 | 137 | 14 | 3 |
| 運動器 | 116 | 89 | 7 | 2 |

全体+257の分類配分（12,16,4,7,4,8,10,25,28,7,12,10,10,10,14,20,28,32）とtask/level/Node計画を維持したまま、小ロットの内容適合を優先。Batch01の12問を引いた残予算は245問。本12件を後日統合した場合の残予算は233問であり、今回はformal件数を増やさない。12件全て既存singletonの2問目候補、新規Node0。

優先順は神経→治療→評価→運動器。Node名だけで選ばず、reference全文・正答・解説・タグを読み、別の思考手順を作れるかを確認。raw registry statusは全件singleton_initial、canonical解決後も1問。現行strong供給のあるNodeは候補にしない。

Batch01 Q1738–Q1749のタグから算出した除外Node: KN0007, KN0010, KN0016, KN0024, KN0026, KN0027, KN0032, KN0043, KN0083, KN0102, KN0103, KN0400。これらとKN0779はvalidatorで除外。参照QとNode IDは全て現行データから取得。

## Accepted set

| draft | Node / ref | 分野 | reference task / primary / level / Safety | candidate task / primary / level / Safety |
|---|---|---|---|---|
| B02-01 | KN0117 / Q117 | 神経医学 | finding_interpretation/INTERPRET/2/none | assessment_selection/MEASURE/3/none |
| B02-02 | KN0575 / Q583 | 神経医学 | fact_recall/KNOW/1/none | finding_interpretation/INTERPRET/3/none |
| B02-03 | KN0639 / Q647 | 神経医学 | fact_recall/KNOW/1/none | assessment_selection/MEASURE/3/none |
| B02-04 | KN0241 / Q242 | 神経医学 | finding_interpretation/INTERPRET/2/none | safety_priority/DECIDE/4/critical |
| B02-05 | KN0287 / Q289 | 理学療法治療各論 | intervention_selection/PRESCRIBE/3/moderate | finding_interpretation/INTERPRET/3/moderate |
| B02-06 | KN0408 / Q415 | 理学療法治療各論 | fact_recall/KNOW/1/none | intervention_selection/PRESCRIBE/3/moderate |
| B02-07 | KN0364 / Q369 | 理学療法治療各論 | intervention_selection/PRESCRIBE/3/none | assessment_selection/MEASURE/2/moderate |
| B02-08 | KN0423 / Q431 | 理学療法評価各論 | assessment_selection/MEASURE/3/none | safety_priority/DECIDE/3/critical |
| B02-09 | KN0378 / Q383 | 理学療法評価各論 | fact_recall/KNOW/1/none | assessment_selection/MEASURE/3/none |
| B02-10 | KN0369 / Q374 | 理学療法評価各論 | fact_recall/KNOW/1/none | intervention_selection/PRESCRIBE/3/moderate |
| B02-11 | KN0327 / Q329 | 運動器 | finding_interpretation/INTERPRET/3/critical | safety_priority/DECIDE/4/critical |
| B02-12 | KN1533 / Q1559 | 運動器 | fact_recall/KNOW/1/none | safety_priority/DECIDE/3/moderate |

task: assessment_selection 4 / finding_interpretation 2 / intervention_selection 2 / safety_priority 4。level2=1、level3=9、level4=2。Safety critical=3、moderate=5、none=4。全て5択・単一ベスト・全選択肢の説明あり。問題文は64〜105字、不要な年齢や検査値の追加を避けた。正式形式を参考にcorrect_choices、explanation、choice_explanationsを保持（数値キーの5択）。

## HOLD / REJECT / replacement

内容方向を15案検討し、以下3案を原稿化前にREJECT_IDEA。完成したdraftは12件で全件accepted。HOLD原稿0、完成原稿のsemantic replacement0、category correction0。空overlayは作成しない。却下はNode自体の価値を否定せず、今回考えた問い方への判断。

| ref / Node | 却下理由 | 別案で選んだref |
|---|---|---|
| Q490 / KN0482 | 角度の数値からティルト機構を言い当てる案は、機構の特徴を問うreferenceと同じ需要。 | Q289 |
| Q344 / KN0341 | 電流を増やさず運動点へ電極を置く案は、正答概念の言い換えに留まる。 | Q415 |
| Q423 / KN0415 | 仰臥位肺活量低下から横隔膜低下を答える逆向き設問は、同じ対応関係の再生に留まる。 | Q431 |

## Duplicate / semantic review

正規化はNFKC・小文字化・空白と句読点除去。12×1749=20988のformal stem比較、候補同士66ペアをSequenceMatcher(autojunk=False)で比較。完全一致はformal/candidateとも0。formal最大類似度0.423841、候補間最大0.320442。0.65以上は自動採用せずvalidatorを失敗させる。0.65未満であることは意味の新規性を証明しない。

formal全体のstem比較に加え、全文・解説・Nodeラベルを疾患/検査/介入語で検索し、関連問題を個別に比較した。新規性は以下の内容監査による判断であり、全1749問を専門家が再審査したという意味ではない。原稿・正答・誤答理由・タグ・参考根拠・監査記述をreviewed_sha256で結び、変更時は再監査を要求する。hashは意味理解や医学的正しさの証明ではない。formal入力はGitのWindows CRLF / Ubuntu LF差だけを正規化してSHA256を比較し、内容変更は拒否する。

| draft | 近似上位3（qid:ratio） |
|---|---|
| B02-01 | Q238:0.416667, Q175:0.377953, Q494:0.363636 |
| B02-02 | Q268:0.294118, Q235:0.280488, Q441:0.27972 |
| B02-03 | Q396:0.423841, Q273:0.423358, Q1124:0.407407 |
| B02-04 | Q141:0.350515, Q1608:0.34, Q186:0.335079 |
| B02-05 | Q1740:0.366197, Q1706:0.363636, Q1611:0.359281 |
| B02-06 | Q1648:0.335664, Q1634:0.333333, Q1742:0.331126 |
| B02-07 | Q1742:0.29932, Q370:0.287425, Q437:0.28169 |
| B02-08 | Q431:0.386667, Q164:0.268456, Q1602:0.258503 |
| B02-09 | Q1674:0.335766, Q196:0.316327, Q1626:0.313725 |
| B02-10 | Q354:0.403846, Q471:0.403226, Q1706:0.4 |
| B02-11 | Q219:0.4, Q497:0.388889, Q391:0.386667 |
| B02-12 | Q385:0.311377, Q467:0.28777, Q404:0.283784 |

近似上位は定型句の一致も多い。Q1124はParkinson病に適した検査・徴候を選ぶもので服薬条件統一ではなく、Q431は測定法選択であって測定済み情報から蘇生を避ける判断ではない。Q467は新鮮骨折疑いで初回画像陰性の対応であり、固定除去後の荷重再開判断ではない。他の上位候補も疾患・観察対象・判断目的を照合し、同一需要を示すものは認めなかった。

候補同士では全66組を比較。B02-01/03は共に測定計画だが、前者は髄液排除後の遅延反応、後者は服薬による交絡の統制。B02-04/11は共に緊急連携が正答だが、前者は眼球所見と急性持続性めまい、後者は区画圧上昇徴候と脈拍温存の不一致を処理するため、疾患名だけの差替えではない。B02-08は保たれた灌流下で誤った蘇生を回避し、B02-12は骨癒合確認と負荷許可を待つ非緊急の判断。呼吸・皮膚・筋力・車椅子各案も求める入力と結論を区別した。

## Per-draft demand / medical rationale

### B02-01 髄液排除前後の歩行評価計画

Node KN0117 / reference Q117。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: 79歳の男性。歩行障害を主訴に受診した。歩幅は小さく、歩行開始時に足が出にくい。方向転換では数歩を要する。軽度の認知機能低下と尿失禁を認める。四肢筋力は保たれ、安静時振戦は認めない。最も考えられる疾患はどれか。

**Candidate全文**: 特発性正常圧水頭症が疑われ、医師が髄液タップテストを行う。理学療法士は歩行の変化を評価する。測定計画として最も適切なのはどれか。

**Reference需要**: 三徴から正常圧水頭症を同定する

**Candidate需要**: 髄液排除への遅延反応と交絡を考慮して前後比較の測定計画を選ぶ

**別需要の根拠**: 疾患名は与え、測定時点・基準値・条件統一を選ばせる。Q74/Q144の歩行観察項目選択とは異なり、介入反応を比較可能にする設計が正答条件。

**正答**: 3 — 排除前に測定し、同じ補助具・介助条件で排除後の複数時点に歩行時間や方向転換を再評価する

**正答理由**: 排除前の基準値と条件をそろえた反復評価が必要である。歩行時間・歩数・方向転換などを記録し、排除後早期、翌日など複数時点で比較する。陰性だけで疾患や治療効果を否定しない。

- 関連Q74: 通常の歩行指標選択。髄液排除前後の時点設計は問わない。
- 関連Q144: 歩行観察項目の列挙。前後条件統一と遅延反応は問わない。
- [根拠資料](https://www.jstage.jst.go.jp/article/nmc/advpub/0/advpub_st.2020-0292/_pdf/-char/en): iNPH第3版CQ7：タップ後の複数時点の機能評価。（参照2026-09-08）

### B02-02 末梢神経損傷後の電気生理所見

Node KN0575 / reference Q583。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: 末梢神経損傷で予後が最も良いのはどれか。

**Candidate全文**: 上腕部の圧迫後に手関節伸展が低下した。3週後、病変より遠位での神経刺激による複合筋活動電位は保たれるが、病変をまたぐ刺激では著しく低下する。針筋電図で脱神経電位はない。最も整合する病態はどれか。

**Reference需要**: 神経損傷分類のうち予後良好な名称を再生する

**Candidate需要**: 受傷後の時間と近位・遠位刺激および筋電図の組合せから伝導障害を局在する

**別需要の根拠**: 予後ランキングを問わず、3週という時期を含めた電気生理所見の整合性を判断させる。診断名の単純な置換ではない。

**正答**: 1 — 軸索の連続性が保たれた局所伝導ブロック

**正答理由**: 受傷3週後も遠位刺激の反応が保たれ、病変を越える伝導のみ障害され、脱神経所見を欠く組合せはneurapraxiaに整合する。受傷直後の遠位反応だけでは軸索損傷を除外できない点に注意する。

- [根拠資料](https://now.aapmr.org/peripheral-neurological-recovery-and-regeneration/): AAPM&R：neurapraxiaの遠位伝導保持、局所ブロック、脱神経所見と検査時期。（参照2026-09-08）

### B02-03 Parkinson病評価の条件統一

Node KN0639 / reference Q647。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: Parkinson病に対する包括的な評価指標であるUPDRSの評価項目でないのはどれか。

**Candidate全文**: Parkinson病患者の4週間の運動療法前後を、同じ版のUPDRS運動評価で比較する。薬物療法は変更されていないが、日内のON・OFF変動がある。評価計画として最も適切なのはどれか。

**Reference需要**: UPDRSに含まれない項目を再生する

**Candidate需要**: 薬効の日内変動を統制した経時的運動評価計画を選ぶ

**別需要の根拠**: 尺度名・用途は与える。項目暗記ではなく、介入効果の判定に必要な比較条件を選ばせる。Q396の練習時間帯選択とも目的が異なる。

**正答**: 4 — 服薬後経過時間とON・OFF状態を記録し、同じ状態・手順で比較する

**正答理由**: 服薬状態と評価手順をそろえることで、日内変動による交絡を減らせる。評価時の薬効状態を記録し、条件をそろえた経時比較を行う。

- 関連Q396: 新しい歩行課題を練習する時間帯の選択。評価の交絡制御ではない。
- 関連Q1124: Parkinson病に適した検査・徴候の選択。本案は選択済み尺度での薬効条件統一。
- [根拠資料](https://web.stanford.edu/group/adrc/cgi-bin/web-proj/updrs.php): MDS-UPDRS Part IIIの服薬状況・最終服薬後時間・ON/OFF記録。版を混同せず記録原則を参照。（参照2026-09-08）

### B02-04 持続性めまいの受診優先判断

Node KN0241 / reference Q242。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: めまい患者の眼振所見で、中枢性前庭障害を最も疑うのはどれか。

**Candidate全文**: 外来で突然のめまいが2時間続いている。頭位変換に限らず持続し、右方視では右向き、左方視では左向きの眼振がある。四肢筋力は保たれているが、自力で安定した座位を保てない。理学療法士の対応として最も適切なのはどれか。

**Reference需要**: 中枢性を示唆する眼振パターンを選ぶ

**Candidate需要**: 筋力温存に惑わされず、急性持続性めまいの練習中断と緊急連携を決める

**別需要の根拠**: 眼振の名称選択で終わらず、発症様式・体幹不安定性・筋力温存を統合して緊急対応を優先する。HINTSの未訓練実施やPTによる確定診断を要求しない。

**正答**: 2 — 評価・練習を中断し、安全を確保して直ちに医師へ緊急評価を求める

**正答理由**: 持続性めまい、注視方向で変わる眼振、著しい体幹不安定性は中枢性病変を疑う根拠となる。理学療法を進めず、転倒を防いで速やかな医学的評価につなぐ。

- 関連Q479: skew所見の意味を選ぶ問題で、急性期の受診優先判断ではない。
- 関連Q408: 典型的Dix-Hallpike陽性に対するEpley法。持続性症状とは異なる。
- 関連Q312: 頭位眼振から水平半規管型BPPVの患側を判断する。
- [根拠資料](https://www.saem.org/publications/grace/grace-3): GRACE-3：急性めまいで中枢性所見と歩行不安定を重視。HINTSは訓練された臨床家に限る。（参照2026-09-08）

### B02-05 踵部痂皮の経時変化

Node KN0287 / reference Q289。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: 踵部に乾燥して硬く、周囲の発赤・浮腫・排膿を伴わない黒色痂皮がある。最も適切な対応はどれか。

**Candidate全文**: 踵の乾燥した黒色痂皮を除圧して経過観察していた。今回は痂皮辺縁が軟化して膿性排液が出現し、周囲に発赤と熱感が広がっている。現在の所見の解釈として最も適切なのはどれか。

**Reference需要**: 感染徴候のない安定痂皮に対する保護を選ぶ

**Candidate需要**: 経時的に出現した排膿・炎症所見から安定性判断を更新する

**別需要の根拠**: 以前の保護方針の暗記を転用できないよう、安定という前提が崩れた証拠を解釈させる。病期判定や一律デブリードマンの選択にはしない。

**正答**: 5 — 安定した乾燥痂皮とは扱えず、感染を含む不安定化を疑う

**正答理由**: 以前の安定した乾燥痂皮という条件が失われている。感染等の不安定化を疑い、除圧を維持しつつ創傷管理担当者へ速やかに評価を依頼する。PT単独の切除を意味しない。

- 関連Q247: 真皮露出から褥瘡Stage2を分類する。感染による経時的不安定化ではない。
- 関連Q332: 皮下脂肪露出からStage3を分類する。
- [根拠資料](https://internationalguideline.com/s/CPG2019edition-digital-Nov2023version.pdf): 2019国際指針Heel pressure injuries：安定痂皮と感染が疑われる痂皮を区別して評価。（参照2026-09-08）

### B02-06 車軸調整後の段階的導入

Node KN0408 / reference Q415。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: 手動車椅子の後輪車軸を前方へ移動した場合の変化として正しいのはどれか。

**Candidate全文**: 手動車椅子の後輪車軸を調整すると、平地の駆動負担は減ったが、発進時に前輪が意図せず浮くようになった。本人は後輪バランスをまだ習得していない。新しい設定の導入方法として最も適切なのはどれか。

**Reference需要**: 車軸前方移動による操作性と安定性の変化を再生する

**Candidate需要**: 実際に得た操作性向上と不安定性を両立させる試用・練習計画を選ぶ

**別需要の根拠**: 車軸移動方向は正答にせず、本人の技能と観察された浮き上がりから導入手順を組み立てる。単純な前方移動の効果の再生を超える。

**正答**: 3 — 転倒防止装置と介助者を確保し、設定の再調整も含めて平地から安定性と操作を確認する

**正答理由**: 操作性の改善を生かすには、後方転倒を防ぐ介助・装置と段階的な試用が必要である。本人の技能に合わなければ設定を再調整する。

- 関連Q490: ティルト機構の特徴。車軸調整後の技能評価や導入方法ではない。
- [根拠資料](https://wheelchairskillsprogram.ca/wp-content/uploads/WSP-Manual-version-5.0-approved-version.2.pdf): WSP：調整による安定性変化、後方spotter・転倒防止装置を用いた安全な技能評価と練習。（参照2026-09-08）

### B02-07 咳介助効果を捉える測定

Node KN0364 / reference Q369。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: 進行性神経筋疾患患者で、痰が増えると自力排痰が困難になる。意識は清明で気道分泌物はあるが、呼気筋力低下のため咳の流速が著しく低い。排痰を補助する方法として最も適切なのはどれか。

**Candidate全文**: 神経筋疾患患者に咳介助を試す。安静時SpO₂は保たれ、指示理解とマウスピース保持は可能である。介助によって分泌物を動かす咳の能力が改善したか、最も直接的に前後比較する指標はどれか。

**Reference需要**: 咳流速不足に対して機械的咳介助を選ぶ

**Candidate需要**: 咳介助を試した際の直接効果を測定する指標を選ぶ

**別需要の根拠**: 治療法は既に決まっている。酸素化と咳の力学的能力を区別して効果判定の指標を選ぶ。Q406/Q1738の換気不全進行判定とは別。

**正答**: 1 — 咳嗽時最大呼気流量

**正答理由**: 咳嗽時最大呼気流量は咳によって生じる流速を測る。姿勢・器具等の条件をそろえた介助前後比較により、咳介助による流速の変化を直接捉えられる。

- 関連Q406: GBSの呼吸不全進行の監視。咳介助前後の流速ではない。
- 関連Q1738: 肺活量の連続低下から呼吸筋機能の悪化を解釈する。
- 関連Q354: 分泌物貯留所見から吸引適応を選ぶ。
- [根拠資料](https://pmc.ncbi.nlm.nih.gov/articles/PMC8640837/): CHEST expert panel：peak cough flowを咳・気道クリアランス機能の評価に用いる。（参照2026-09-08）

### B02-08 連続流型LVADの脈拍触知不能

Node KN0423 / reference Q431。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: 連続流型左室補助人工心臓〈LVAD〉装着患者では末梢動脈の拍動を触知しにくい。歩行練習前の循環評価として最も適切なのはどれか。

**Candidate全文**: 連続流型LVAD装着者の離床前評価で橈骨動脈を触知できない。本人は清明で会話でき、呼吸は正常、皮膚は温かい。ドプラ法の血圧値とポンプ流量は本人の通常範囲で、アラームもない。最も適切な対応はどれか。

**Reference需要**: 連続流型で適切な循環測定法を選ぶ

**Candidate需要**: 測定済みの灌流情報から脈拍触知不能を誤って心停止と扱うことを防ぐ

**別需要の根拠**: 測定手段は全て提示する。新たに測るものを選ぶのではなく、相反して見える脈拍と灌流情報を統合して危険な介入を回避する。

**正答**: 4 — 脈拍触知不能だけで心停止と判断せず、意識・呼吸・灌流と装置の監視を続ける

**正答理由**: 連続流型では拍動を触知しにくい。意識、正常呼吸、灌流、ドプラ血圧、装置情報を総合し、触知不能だけで蘇生を開始しない。意識や呼吸が悪化した場合は別途緊急対応する。

- 関連Q93: 退院後のLVAD機器自己管理の確認。脈拍触知不能と心停止を区別する問題ではない。
- [根拠資料](https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines/adult-and-pediatric-special-circumstances-of-resuscitation): AHA LVAD：連続流で脈拍を触知しないことがあり、血圧・呼吸・灌流を併用して心停止を判断。（参照2026-09-08）

### B02-09 肩外転MMTの次の検査条件

Node KN0378 / reference Q383。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: 徒手筋力検査で、重力を除いた肢位では全可動域を動かせるが、抗重力肢位では動かせない。筋力段階はどれか。

**Candidate全文**: 肩関節に疼痛や他動可動域制限はない。座位で肩を外転しようとすると体幹を傾けるが、上腕を持ち上げられない。筋収縮は触知できる。筋力段階1と2を区別するため、次に行う検査として最も適切なのはどれか。

**Reference需要**: 重力除去位の全可動域運動を段階2と対応させる

**Candidate需要**: 抗重力検査失敗と代償所見を受け、重力・摩擦・体幹代償を除く次の検査を設計する

**別需要の根拠**: 段階の数字を選ばせず、観察が不十分な状態から必要な検査操作を選ぶ。部位暗記だけでなく支持と代償制御が正答条件。

**正答**: 2 — 背臥位で上肢を支持して摩擦を減らし、体幹を固定して水平面内の肩外転を確認する

**正答理由**: 肩外転を重力の影響を減らした条件で観察し、体幹の代償を抑える。収縮の触知のみか、重力除去下で運動できるかを分けて評価する。

- 関連Q501: MMTの一般原則の正誤。個別の代償後に行う検査操作ではない。
- 関連Q852: 筋・段階・開始肢位の組合せの再生。
- 関連Q1240: 膝屈伸で肢位が共通する段階の再生。
- [根拠資料](https://www.niehs.nih.gov/research/resources/assets/docs/mmt8_grading_and_testing_procedures_for_the_abbreviated_8_muscle_groups_508.pdf): NIEHS：肩外転の抗重力位は座位、重力除去位は背臥位。（参照2026-09-08）

### B02-10 腹臥位療法中の除圧調整

Node KN0369 / reference Q374。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: 重症呼吸不全患者に長時間の腹臥位療法を行う。褥瘡予防のため、仰臥位とは異なる部位を重点的に観察する必要がある。腹臥位で圧迫を受けやすい部位の組合せはどれか。

**Candidate全文**: 人工呼吸管理中の患者に腹臥位療法を継続している。酸素化と循環は安定しているが、頬部の支持部に圧が集中している。予防的な体位調整として最も適切なのはどれか。

**Reference需要**: 腹臥位で圧迫されやすい部位を再生する

**Candidate需要**: 気道の安全と局所除圧を両立するチームでの調整手順を選ぶ

**別需要の根拠**: 観察部位は与える。どこが圧迫されるかの再生を不要にし、挿管患者の安全な実施手順を問う。

**正答**: 5 — 気道・回路を担当するスタッフと協働し、支持具と頭部位置を調整して再度皮膚・呼吸状態を確認する

**正答理由**: 気道・回路を保護しながら圧を再分配し、調整後の皮膚と呼吸・循環を確認する。支持具だけを追加して確認を終えない。

- 関連Q770: 長時間座位の褥瘡好発部位の再生。気道管理下の除圧ではない。
- 関連Q1473: 腹臥位の呼吸への効果の正誤。皮膚障害を防ぐ実施手順ではない。
- [根拠資料](https://internationalguideline.com/s/CPG2019edition-digital-Nov2023version.pdf): 国際指針：腹臥位での支持面・枕、体位調整、医療機器関連圧迫への配慮。（参照2026-09-08）
- [根拠資料](https://www.internationalguideline.com/repositioning): 2025第4版：体位変換ごとの皮膚評価、患者の状態に応じた体位調整。（参照2026-09-08）

### B02-11 脈拍がある外傷後の強い疼痛

Node KN0327 / reference Q329。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: 前腕骨折後、疼痛が増強し、他動的な手指伸展で強い疼痛を認める。最も疑うべき病態はどれか。

**Candidate全文**: 前腕骨折後の患者が、鎮痛薬を使用しても増強する疼痛を訴えた。手指を他動伸展すると激痛があり、前腕は緊満している。橈骨動脈は触知できる。理学療法士の対応として最も適切なのはどれか。

**Reference需要**: 他動伸張痛からコンパートメント症候群を同定する

**Candidate需要**: 脈拍温存という誤った安心材料を退け、進行所見を待たずに緊急連携する

**別需要の根拠**: 病名を選ぶだけでなく、動脈が触れる状況でも観察待機しない時機判断を問う。Q466の『何をまず測るか』とも段階が異なる。

**正答**: 1 — 脈拍消失を待たずに練習を中止し、直ちに担当医へ緊急評価を求める

**正答理由**: 脈拍が保たれていても急性コンパートメント症候群を除外できない。増悪痛、他動伸張痛、緊満は早期の緊急評価が必要な所見で、麻痺や脈拍消失を待たない。

- 関連Q466: 循環・神経所見の優先確認項目を選ぶ。本案は確認済みの脈拍に惑わされず紹介時機を決める。
- [根拠資料](https://www.aaos.org/AAOSNow/2019/Jun/Clinical/clinical06/): AAOS：古典的5Pのみに依存せず、不釣合いな痛み・他動伸張痛を重視。（参照2026-09-08）

### B02-12 舟状骨骨折後の負荷再開判断

Node KN1533 / reference Q1559。categoryはreferenceの正式分類を継承（内容から再割当なし）。

**Reference全文**: 骨折後に偽関節を生じやすいのはどれか。

**Candidate全文**: 舟状骨腰部骨折後、固定が外れて日常動作の痛みは軽くなった。本人は手を床について行う腕立て伏せを再開したいが、直近の画像では骨癒合が未確認で、医師から荷重再開の指示はない。最も適切な対応はどれか。

**Reference需要**: 偽関節を生じやすい骨の名称を選ぶ

**Candidate需要**: 疼痛軽減と骨癒合を区別し、許可のない手関節荷重再開を保留する

**別需要の根拠**: 骨名は提示し、癒合未確認と本人の活動希望の対立を処理させる。Q467の初回X線陰性・新鮮骨折疑いの対応ではない。

**正答**: 4 — 手をつく負荷は保留し、骨癒合と許容荷重を担当医に確認して段階的な再開を計画する

**正答理由**: 舟状骨は癒合不全のリスクがあり、症状だけで荷重を再開しない。画像等による骨癒合と医師の許可を確認し、許容範囲で負荷を段階化する。

- 関連Q655: 偽関節好発部位の複数選択。復帰判断ではない。
- 関連Q467: 未診断の新鮮損傷で初回X線が陰性の場合。本案は診断後・固定除去後の負荷許可。
- [根拠資料](https://www.orthoinfo.org/diseases--conditions/scaphoid-fracture-of-the-wrist): AAOS：舟状骨の癒合不全リスク、癒合までの荷重・押す動作の制限。（参照2026-09-08）

## Guards / validation

staging validatorは全入力を読み取るのみ。Node存在・canonical解決・registry/ref/4ストア整合・singleton維持・Batch01/KN0779除外・category一致・task/ability・正答形式・完全一致/近似・監査sealとformal入力ハッシュを検証。DB/appはimportしない。

異常系テストで、未知/除外Node、参照不存在、category不一致、重複ID/Node、同じstemのコピー、年齢だけの改変、同一task/ability、同一需要記述、監査後の問題/正答変更、欠落answer、registry状態変更、canonical2問化を検出する。正式統合または別Bank改訂が行われた場合は、このstaging snapshotの再監査が必要。

実行コマンド（repo root）:

```text
python reports/question_bank_2000_batch02_validate.py
python -m pytest -q tests/test_question_bank_2000_batch02_staging.py tests/test_question_bank_2000_batch01_staging.py tests/test_question_bank_2000_batch01_integration.py
python scripts/validate_question_bank.py
python scripts/check_question_bank_schema_manifest.py
python -m pytest -q --deselect=tests/test_quiz_answer_numbering.py::ConfigurableQuizTest::test_runtime_loader_supports_current_utf16_and_candidate_utf8
git diff --check
git diff 9bd50710fed3bfee301d5a801c1b2feaf6f80a35 -- data/question_bank app.py learning_engine.py
```

最終full suite内でBatch02専用29件、Batch01 permanent 5件がPASS。Batch02 validator accepted=12、unique_targets=12、hard_errors=[]。最終full regression: 1169 passed, 1 deselected, 16 warnings, 125 subtests passed。正式validator・schema checker・git diff --checkもPASS。GitHub Actionsの確定結果はPR・完了報告に記載。

## Formal impact / handoff

変更はBatch02 staging JSON・本監査・read-only validator・専用testsの4ファイルのみ。formal4ストア、manifest、schema、registry、canonical map、strong pair master、app.py、selector、Phase11、DB、Render、LINE変更0。入力9ファイルのLF正規化SHA256も原稿に保存。git diffの範囲で確認できる。

acceptedは今回のCodex内容監査でのstaging採用を意味する。医療専門家の承認・実測の教育効果・正式strong認定ではない。formal integrationに向けたレビュー用12件セットとして引き渡す。正式Q IDの割当とNode transitionは別PRで現行Bankを再検証して行う。自動mergeなし。
