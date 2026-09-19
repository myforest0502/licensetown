# PT Question Bank 新規追加問題 Node割当表 v0.2

Date: 2026-09-19  
Baseline: main `20c411588432744620c8d492769459eeca8b64fa`  
Formal bank: 2000 questions / 1562 registry Nodes

## Final recommendation

**追加問題: 233問**  
**追加後: 2233問**

この233問は全分野への均等配分ではなく、1つのtarget derived Knowledge Nodeにつき原則1問を追加し、
既存問題とは異なる task / primary ability を設計して STRONG different-question repair evidence を作るためのもの。

採用条件は以下のいずれか。

- critical Safety NodeなのにSTRONG alternateがない
- 過去問が複数収録されているNodeなのにSTRONG alternateがない
- Exam Weight >= 1.0 の高重要度分野で、official singletonかつ非fact-recallで、level>=3またはSafety付き

低頻度の一回出題fact-recallを一律に増やさない。

## 分野別確定配分

| 分野 | 追加 |
|---|---:|
| 解剖学 | **4** |
| 生理学 | **8** |
| 心理学 | **0** |
| 人間発達学 | **0** |
| 教育学 | **0** |
| 医学概論 | **2** |
| 病理学 | **0** |
| 内科学 | **18** |
| 神経医学 | **20** |
| 精神医学 | **0** |
| 小児学 | **3** |
| 臨床心理学 | **0** |
| 基礎運動学 | **1** |
| 臨床運動学 | **0** |
| 動作分析学 | **6** |
| 運動器 | **3** |
| 理学療法評価各論 | **54** |
| 理学療法治療各論 | **114** |

## Target Nodes

| # | 分野 | Node | 既存Q | 過去問数 | 理由 | Node label |
|---:|---|---|---|---:|---|---|
| 1 | 解剖学 | KN1006 | Q1016 | 1 | high_weight_depth_singleton | 脳底動脈からは上小脳動脈と前下小脳動脈などが分岐するを評価する |
| 2 | 解剖学 | KN1008 | Q1018 | 1 | high_weight_depth_singleton | 腱板を構成する筋はどれかに対して適切な理学療法・介入を選択する |
| 3 | 解剖学 | KN1009 | Q1019 | 1 | high_weight_depth_singleton | 第3腓骨筋腱は足関節前外側を通り外果の前方を走行するに対する機器選択 |
| 4 | 解剖学 | KN1010 | Q1020,Q1142 | 2 | repeated_past_no_strong | 体性感覚一次ニューロン細胞体が後根神経節にあること |
| 5 | 生理学 | KN0601 | Q609,Q1153,Q1263 | 3 | repeated_past_no_strong | プロラクチンによる乳汁産生促進 |
| 6 | 生理学 | KN0666 | Q674,Q816 | 2 | repeated_past_no_strong | Bohr効果による酸素解離曲線右方移動 |
| 7 | 生理学 | KN0731 | Q739,Q1589 | 2 | repeated_past_no_strong | 皮膚の痛覚・温度覚など侵害刺激は自由神経終末で受容される |
| 8 | 生理学 | KN0805 | Q813,Q1079 | 2 | repeated_past_no_strong | 副腎髄質からのアドレナリン・ノルアドレナリン分泌 |
| 9 | 生理学 | KN0812 | Q821,Q1365 | 2 | repeated_past_no_strong | 広背筋の肩関節伸展・内転・内旋作用 |
| 10 | 生理学 | KN1013 | Q1023,Q1553 | 2 | repeated_past_no_strong | 角膜反射の求心路は三叉神経第1枝、遠心路は顔面神経である |
| 11 | 生理学 | KN1134 | Q1146,Q1414 | 2 | repeated_past_no_strong | ミトコンドリアでの酸化的リン酸化によるATP産生 |
| 12 | 生理学 | KN1387 | Q1411,Q1585 | 2 | repeated_past_no_strong | 下垂体後葉からはオキシトシンとバソプレシンが放出される |
| 13 | 医学概論 | KN0100 | Q100 | 0 | critical_safety_no_strong | 模擬作業で緊急停止反応と安全確認能力を評価する |
| 14 | 医学概論 | KN0237 | Q238 | 0 | critical_safety_no_strong | 感染性肺結核に対する空気感染予防策とN95使用 |
| 15 | 内科学 | KN0017 | Q17 | 0 | critical_safety_no_strong | バイタルサインと人工呼吸器条件を監視しながら、端座位から立位へ段階的に離床を進めるへの介入選択 |
| 16 | 内科学 | KN0058 | Q58 | 0 | critical_safety_no_strong | 携帯酸素の安全な生活使用 |
| 17 | 内科学 | KN0093 | Q93 | 0 | critical_safety_no_strong | 退院後はバッテリー残量の確認・交換、ケーブルの引っ掛かり防止、機器携行などを自ら安全に行う必要があるため、実際の外出場面を想定して自己管理能力を確認する |
| 18 | 内科学 | KN0105 | Q105 | 0 | critical_safety_no_strong | 疼痛を皮膚損傷の警告として利用できないため、毎日の足部観察、靴内の異物や縫い目の確認、足幅や圧迫部位に配慮した靴選びを習慣化し、潰瘍への進行を防ぐことが重要である時の優先対応 |
| 19 | 内科学 | KN0163 | Q164 | 0 | critical_safety_no_strong | シャント肢を避けた血圧測定 |
| 20 | 内科学 | KN0356 | Q359 | 0 | critical_safety_no_strong | 呼吸音消失・気管偏位・循環不安定から緊張性気胸を識別する |
| 21 | 内科学 | KN0463 | Q471 | 0 | critical_safety_no_strong | VA-ECMO離床前のカニューレ固定・血行動態・回路安全確認 |
| 22 | 内科学 | KN0464 | Q472 | 0 | critical_safety_no_strong | 大腿静脈CRRTカテーテルを保護した端座位離床 |
| 23 | 内科学 | KN0615 | Q623 | 1 | high_weight_depth_singleton | 摂食嚥下障害への対応の基本事項 |
| 24 | 内科学 | KN0627 | Q635,Q1235 | 2 | repeated_past_no_strong | 欠神発作は過換気で誘発されやすい |
| 25 | 内科学 | KN0721 | Q729 | 1 | high_weight_depth_singleton | 人工呼吸器管理中に起こりやすい呼吸器合併症の識別 |
| 26 | 内科学 | KN1099 | Q1110 | 1 | high_weight_depth_singleton | 睡眠日誌は就床・入眠・覚醒時刻を連日記録して概日リズムのずれを把握するため、睡眠相後退症候群で特に有用を評価する |
| 27 | 内科学 | KN1118 | Q1129 | 1 | high_weight_depth_singleton | 1秒量は5.00L×0.80＝4.00Lを評価する |
| 28 | 内科学 | KN1208 | Q1223 | 1 | high_weight_depth_singleton | 積極的な全身持久力トレーニングを開始してよい状態はどれかに対する適切な介入・練習・指導を選択する |
| 29 | 内科学 | KN1411 | Q1436 | 1 | high_weight_depth_singleton | Thomas testで股関節屈曲拘縮を評価する |
| 30 | 内科学 | KN1430 | Q1455 | 1 | high_weight_depth_singleton | 肥満・高血圧を伴うメタボリックシンドロームに適した有酸素運動形式を選択する |
| 31 | 内科学 | KN1543 | Q1854 | 0 | critical_safety_no_strong | 高カリウム血症で心電図変化がある場合は致死的不整脈リスクがあり運動より緊急医療評価を優先する |
| 32 | 内科学 | KN1554 | Q1952 | 0 | critical_safety_no_strong | SIADHでは低張性低Na血症に対して尿が不適切に濃縮され、重症低Na血症では意識障害やけいれんを生じ得る |
| 33 | 神経医学 | KN0518 | Q526 | 1 | high_weight_depth_singleton | 脳卒中片麻痺者の応用歩行練習について麻痺側から行う場合が多いのはどれに対する適切な介入・支援選択 |
| 34 | 神経医学 | KN0682 | Q690 | 1 | high_weight_depth_singleton | 失行は運動麻痺などでは説明できない学習された目的動作の障害であるを評価する |
| 35 | 神経医学 | KN0763 | Q771 | 1 | high_weight_depth_singleton | Broca失語患者とのコミュニケーション方法を選択する |
| 36 | 神経医学 | KN0791 | Q799 | 1 | high_weight_depth_singleton | 脳卒中左片麻痺患者のADL練習における安全な自立支援 |
| 37 | 神経医学 | KN0826 | Q835 | 1 | high_weight_depth_singleton | 脳血管障害と治療の組合せで正しいのはどれかに対して適切な理学療法・介入を選択する |
| 38 | 神経医学 | KN0835 | Q844 | 1 | high_weight_depth_singleton | 脳卒中屈曲共同運動を抑え肘伸展を促す筋促通の選択 |
| 39 | 神経医学 | KN0973 | Q983 | 1 | high_weight_depth_singleton | 内反尖足・膝ロッキングに対するダブルクレンザックAFO設定 |
| 40 | 神経医学 | KN1039 | Q1049 | 1 | high_weight_depth_singleton | 複雑部分発作で歩き回る患者を刺激せず安全確保しながら付き添う対応 |
| 41 | 神経医学 | KN1102 | Q1113 | 1 | high_weight_depth_singleton | 非流暢性失語に対するYes/No質問などのコミュニケーション支援 |
| 42 | 神経医学 | KN1113 | Q1124 | 1 | high_weight_depth_singleton | Westphal現象はParkinson病でみられる姿勢反射障害・筋強剛に関連する現象として評価される |
| 43 | 神経医学 | KN1121 | Q1132 | 1 | high_weight_depth_singleton | 脳卒中片麻痺に対する早期立位・歩行・トレッドミル練習 |
| 44 | 神経医学 | KN1207 | Q1222 | 1 | high_weight_depth_singleton | SIASには体幹機能評価が含まれる |
| 45 | 神経医学 | KN1221 | Q1236 | 1 | high_weight_depth_singleton | 脳卒中片麻痺患者の位置覚を適切な手順で検査する |
| 46 | 神経医学 | KN1308 | Q1328 | 1 | high_weight_depth_singleton | 脳卒中回復期の嚥下障害に対する安全な栄養経路選択 |
| 47 | 神経医学 | KN1320 | Q1340 | 1 | high_weight_depth_singleton | 左半側空間無視を疑う患者で優先すべき高次脳機能検査を選択する |
| 48 | 神経医学 | KN1355 | Q1378 | 1 | high_weight_depth_singleton | ALSの針筋電図では脱神経・再支配所見に加え線維束性収縮電位を認めるを評価する |
| 49 | 神経医学 | KN1363 | Q1386 | 1 | high_weight_depth_singleton | 非麻痺側を向く一方、麻痺側刺激への反応はあり、食事・歯磨きで麻痺側の見落としが多いを評価する |
| 50 | 神経医学 | KN1410 | Q1435 | 1 | high_weight_depth_singleton | 末梢神経伝導検査が有用な末梢神経障害を選択する |
| 51 | 神経医学 | KN1418 | Q1443 | 1 | high_weight_depth_singleton | 焦点意識減損発作で徘徊する患者の周囲から危険物を除去して安全確保する |
| 52 | 神経医学 | KN1424 | Q1449 | 1 | high_weight_depth_singleton | 片麻痺患者のADL情報からBarthel Index総得点を算出する |
| 53 | 小児学 | KN0028 | Q28 | 0 | critical_safety_no_strong | 無痛性皮膚障害の自己管理 |
| 54 | 小児学 | KN0135 | Q135 | 0 | critical_safety_no_strong | Pavlik harness装着中の皮膚圧迫・ずれを確認し自己調整を避ける |
| 55 | 小児学 | KN0333 | Q336 | 0 | critical_safety_no_strong | Down症候群児の頸部痛・歩容変化から環軸椎不安定性を疑う運動中止 |
| 56 | 基礎運動学 | KN0388 | Q393 | 0 | critical_safety_no_strong | 骨転移患者の新規荷重時痛から病的骨折リスクを疑い運動を中止する |
| 57 | 動作分析学 | KN0048 | Q48 | 0 | critical_safety_no_strong | 運動時低酸素への条件再検討 |
| 58 | 動作分析学 | KN0114 | Q114 | 0 | critical_safety_no_strong | 疼痛消失と機能確認後の段階復帰 |
| 59 | 動作分析学 | KN0182 | Q183 | 0 | critical_safety_no_strong | SpO2＋呼吸困難モニタリング |
| 60 | 動作分析学 | KN0187 | Q188 | 0 | critical_safety_no_strong | 安静時痛・蒼白・冷感で運動中止 |
| 61 | 動作分析学 | KN0192 | Q193 | 0 | critical_safety_no_strong | 運動中胸部圧迫感への中止・報告 |
| 62 | 動作分析学 | KN0365 | Q370 | 0 | critical_safety_no_strong | 運動中の著明なSpO₂低下と症状出現時に運動を中止する |
| 63 | 運動器 | KN0458 | Q466 | 0 | critical_safety_no_strong | 上腕骨顆上骨折後の循環障害・コンパートメント症候群徴候の優先確認 |
| 64 | 運動器 | KN0922 | Q931,Q1299 | 2 | repeated_past_no_strong | 股関節外転筋機能低下によるTrendelenburg徴候 |
| 65 | 運動器 | KN1278 | Q1294 | 1 | critical_safety_no_strong | 大腿骨近位部骨折術後の下腿腫脹・圧痛からDVTを疑いD-dimerを優先確認する |
| 66 | 理学療法評価各論 | KN0115 | Q115 | 0 | critical_safety_no_strong | 歩行とADLは自立しているが、複数課題を同時に行うと反応が遅れるを評価する |
| 67 | 理学療法評価各論 | KN0177 | Q178 | 0 | critical_safety_no_strong | 運動中低血糖への糖質摂取 |
| 68 | 理学療法評価各論 | KN0197 | Q198 | 0 | critical_safety_no_strong | 運動中血圧低下・めまいで中止 |
| 69 | 理学療法評価各論 | KN0202 | Q203,Q228,Q320 | 0 | critical_safety_no_strong | 心リハ中の胸部症状と血圧低下に対する運動中止判断 |
| 70 | 理学療法評価各論 | KN0281 | Q283 | 0 | critical_safety_no_strong | 胸痛・ST低下・運動時血圧低下に対する運動負荷中止 |
| 71 | 理学療法評価各論 | KN0286 | Q288 | 0 | critical_safety_no_strong | 重度高カリウム血症時の運動中止と医師報告 |
| 72 | 理学療法評価各論 | KN0319 | Q321 | 0 | critical_safety_no_strong | 内シャントのスリル消失時の運動中止と速やかな報告 |
| 73 | 理学療法評価各論 | KN0331 | Q334 | 0 | critical_safety_no_strong | 尿閉・会陰部感覚低下を伴う馬尾症候群red flagへの緊急対応 |
| 74 | 理学療法評価各論 | KN0348 | Q351 | 0 | critical_safety_no_strong | THA術後の急性呼吸困難・胸痛・低酸素から肺塞栓を疑う緊急対応 |
| 75 | 理学療法評価各論 | KN0431 | Q439 | 0 | critical_safety_no_strong | GBS急性期の自律神経障害を踏まえた離床時循環監視 |
| 76 | 理学療法評価各論 | KN0552 | Q560 | 1 | high_weight_depth_singleton | HDS-Rには「知っている野菜の名前をできるだけ多く言う」語想起課題が含まれ、語の流暢性をみるを評価する |
| 77 | 理学療法評価各論 | KN0555 | Q563 | 1 | high_weight_depth_singleton | 観念運動失行は運動麻痺がないのに、命令された習慣的動作やパントマイムを正しく行えない状態であるを評価する |
| 78 | 理学療法評価各論 | KN0584 | Q592 | 1 | high_weight_depth_singleton | 栄養評価ではBMI、体重減少率、血清アルブミン、下腿周囲径などが用いられる |
| 79 | 理学療法評価各論 | KN0637 | Q645 | 1 | high_weight_depth_singleton | 上腕二頭筋腱炎を誘発するYergason testの選択 |
| 80 | 理学療法評価各論 | KN0704 | Q712 | 1 | high_weight_depth_singleton | Daniels法で重力に抗して全可動域を動かせる筋力を段階3と判定する |
| 81 | 理学療法評価各論 | KN0716 | Q724 | 1 | high_weight_depth_singleton | 高次脳機能障害に応じた検査法の選択 |
| 82 | 理学療法評価各論 | KN0748 | Q756 | 1 | high_weight_depth_singleton | ASIA感覚検査における髄節とkey sensory pointの対応 |
| 83 | 理学療法評価各論 | KN0767 | Q775 | 1 | critical_safety_no_strong + high_weight_depth_singleton | Guillain-Barré症候群急性進行期の呼吸・自律神経リスクを優先する判断 |
| 84 | 理学療法評価各論 | KN0779 | Q787,Q1579 | 2 | repeated_past_no_strong | Froment徴候は尺骨神経麻痺で母指内転筋が弱く、紙をつまむ際に長母指屈筋で代償して母指IP関節が屈曲する徴候である |
| 85 | 理学療法評価各論 | KN0782 | Q790 | 1 | high_weight_depth_singleton | 6分間歩行テストの標準的実施・解釈 |
| 86 | 理学療法評価各論 | KN0845 | Q854 | 1 | high_weight_depth_singleton | WCSTで方略転換を含む遂行機能を評価する |
| 87 | 理学療法評価各論 | KN0919 | Q928 | 1 | high_weight_depth_singleton | 第VII脳神経は顔面神経で、表情筋を支配するを評価する |
| 88 | 理学療法評価各論 | KN0951 | Q960 | 1 | high_weight_depth_singleton | 胸腰部回旋ROM測定では基本軸を両上後腸骨棘を結ぶ線、移動軸を両肩峰を結ぶ線として評価する |
| 89 | 理学療法評価各論 | KN0977 | Q987 | 1 | high_weight_depth_singleton | 筋強直性ジストロフィーの重度筋力低下に対する過用を避けた理学療法 |
| 90 | 理学療法評価各論 | KN0985 | Q995 | 1 | high_weight_depth_singleton | 周径測定は再現性のため測定部位・肢位を統一し、メジャーを皮膚に密着させて過度に締め付けず測定する |
| 91 | 理学療法評価各論 | KN1032 | Q1042 | 1 | high_weight_depth_singleton | ASIAの感覚キーポイントではT4は乳頭部に相当するを評価する |
| 92 | 理学療法評価各論 | KN1043 | Q1053 | 1 | high_weight_depth_singleton | Parkinson病のすくみ足・移動不安定に対応した住環境整備と外的キュー |
| 93 | 理学療法評価各論 | KN1048 | Q1058 | 1 | high_weight_depth_singleton | TMTは注意、視覚探索、処理速度、注意転換などを評価する |
| 94 | 理学療法評価各論 | KN1049 | Q1059 | 1 | high_weight_depth_singleton | 補助具使用を含むFIM修正自立の判定 |
| 95 | 理学療法評価各論 | KN1054 | Q1064 | 1 | high_weight_depth_singleton | MMSEは見当識、記銘・再生、注意計算、言語などを短時間で評価する認知症スクリーニング検査 |
| 96 | 理学療法評価各論 | KN1087 | Q1098 | 1 | high_weight_depth_singleton | ASIA key muscleと髄節の対応 |
| 97 | 理学療法評価各論 | KN1088 | Q1099 | 1 | high_weight_depth_singleton | フレイルとサルコペニアの双方で筋力低下と身体機能低下を評価し、握力と歩行速度が共通項目となる |
| 98 | 理学療法評価各論 | KN1108 | Q1119 | 1 | high_weight_depth_singleton | 徒手筋力テストを安全かつ標準的条件で実施する |
| 99 | 理学療法評価各論 | KN1112 | Q1123 | 1 | high_weight_depth_singleton | SIASに含まれる非麻痺側機能などの評価項目 |
| 100 | 理学療法評価各論 | KN1115 | Q1126 | 1 | high_weight_depth_singleton | face scaleとNRSはいずれも疼痛強度の評価に用いる |
| 101 | 理学療法評価各論 | KN1117 | Q1128 | 1 | high_weight_depth_singleton | 嚥下反射時の食塊通過を観察できる嚥下造影検査の選択 |
| 102 | 理学療法評価各論 | KN1181 | Q1195 | 1 | high_weight_depth_singleton | Roos testは上肢を挙上外転外旋位で開閉手運動を反復し、胸郭出口での神経血管圧迫症状を誘発するを評価する |
| 103 | 理学療法評価各論 | KN1209 | Q1224 | 1 | high_weight_depth_singleton | ASIAでS4-5感覚と随意肛門収縮から仙髄機能温存を判定する |
| 104 | 理学療法評価各論 | KN1279 | Q1295 | 1 | high_weight_depth_singleton | 受傷後に人格変化、脱抑制、自己中心性など前頭葉機能障害が疑われるため、前頭葉機能を簡便に評価するFABが優先される |
| 105 | 理学療法評価各論 | KN1283 | Q1300 | 1 | high_weight_depth_singleton | Thomasテストは一側股関節を最大屈曲し、反対側大腿が浮き上がるかをみて股関節屈曲拘縮を評価する |
| 106 | 理学療法評価各論 | KN1284 | Q1301 | 1 | high_weight_depth_singleton | SIASには視空間認知、言語、体幹機能、感覚、麻痺側・非麻痺側運動などが含まれるを評価する |
| 107 | 理学療法評価各論 | KN1289 | Q1307 | 1 | high_weight_depth_singleton | QMGには眼球運動・眼瞼下垂、嚥下、発語、四肢筋力、肺活量など重症筋無力症の主要症候が含まれるを評価する |
| 108 | 理学療法評価各論 | KN1311 | Q1331 | 1 | high_weight_depth_singleton | NIHSSは脳卒中急性期の神経学的重症度、SIASは脳卒中の機能障害を評価する |
| 109 | 理学療法評価各論 | KN1349 | Q1372 | 1 | high_weight_depth_singleton | 日常生活上の記憶障害を検出するRBMTなどの検査選択 |
| 110 | 理学療法評価各論 | KN1369 | Q1393 | 1 | high_weight_depth_singleton | FMAは総得点226点で、Brunnstromの共同運動・分離運動に関連する運動項目を含むを評価する |
| 111 | 理学療法評価各論 | KN1370 | Q1394 | 1 | high_weight_depth_singleton | WeeFIMの社会的認知には社会的交流があり、小児では遊びへの参加などを含めて評価する |
| 112 | 理学療法評価各論 | KN1374 | Q1398 | 1 | high_weight_depth_singleton | MRC sum scoreをICU獲得性筋力低下の評価に用いる |
| 113 | 理学療法評価各論 | KN1439 | Q1464 | 1 | high_weight_depth_singleton | SIASには非麻痺側機能として握力評価が含まれる |
| 114 | 理学療法評価各論 | KN1442 | Q1467 | 1 | high_weight_depth_singleton | CATで持続・選択・分配・転換性注意を評価する |
| 115 | 理学療法評価各論 | KN1445 | Q1470 | 1 | high_weight_depth_singleton | Hoehn & Yahr stage IIを両側性症状と姿勢反射障害の有無から判定する |
| 116 | 理学療法評価各論 | KN1478 | Q1503 | 1 | high_weight_depth_singleton | CMIは心身両面の自覚症状や神経症傾向を質問紙で把握する検査で、STAIは状態不安・特性不安という人格傾向を評価する質問紙 |
| 117 | 理学療法評価各論 | KN1480 | Q1505 | 1 | high_weight_depth_singleton | Daniels MMT肩屈曲grade 4の検査肢位・抵抗方法を適切に実施する |
| 118 | 理学療法評価各論 | KN1489 | Q1514 | 1 | high_weight_depth_singleton | 位置覚・振動覚など深部感覚検査に用いる器具を選択する |
| 119 | 理学療法評価各論 | KN1500 | Q1525 | 1 | high_weight_depth_singleton | 顔面神経機能を適切な運動・反射で評価する |
| 120 | 理学療法治療各論 | KN0011 | Q11 | 0 | critical_safety_no_strong | 自律神経過反射への初期対応 |
| 121 | 理学療法治療各論 | KN0132 | Q132 | 0 | critical_safety_no_strong | 足部痛の原因と皮膚・循環・運動機能を評価し、安全な運動療法を検討する |
| 122 | 理学療法治療各論 | KN0172 | Q173 | 0 | critical_safety_no_strong | 援助要請と夜間環境の共同調整 |
| 123 | 理学療法治療各論 | KN0176 | Q177 | 0 | critical_safety_no_strong | 脊柱過屈曲を避けた生活動作 |
| 124 | 理学療法治療各論 | KN0301 | Q303 | 0 | critical_safety_no_strong | 症候性重度低ナトリウム血症の緊急対応 |
| 125 | 理学療法治療各論 | KN0322 | Q324 | 0 | critical_safety_no_strong | リンパ浮腫患者の発熱・発赤・熱感から蜂窩織炎を疑う緊急対応 |
| 126 | 理学療法治療各論 | KN0367 | Q372 | 0 | critical_safety_no_strong | 関節リウマチの頸椎不安定性red flagと徒手療法回避 |
| 127 | 理学療法治療各論 | KN0371 | Q376 | 0 | critical_safety_no_strong | 自律神経過反射の誘因除去と緊急対応 |
| 128 | 理学療法治療各論 | KN0379 | Q384 | 0 | critical_safety_no_strong | TKA術後の発熱・発赤・排液から感染を疑う緊急対応 |
| 129 | 理学療法治療各論 | KN0386 | Q391 | 0 | critical_safety_no_strong | 急性下肢動脈閉塞の6P徴候と緊急対応 |
| 130 | 理学療法治療各論 | KN0390 | Q395 | 0 | critical_safety_no_strong | 重度血小板減少と出血徴候がある化学療法患者の運動中止 |
| 131 | 理学療法治療各論 | KN0396 | Q401 | 0 | critical_safety_no_strong | 増悪する鮮血喀出時の排痰練習中止と医療対応 |
| 132 | 理学療法治療各論 | KN0424 | Q432 | 0 | critical_safety_no_strong | 胸腔ドレーンの連続気泡からエアリークを疑い離床前に安全確認する判断 |
| 133 | 理学療法治療各論 | KN0425 | Q433 | 0 | critical_safety_no_strong | 一方向性発声弁装着前の上気道開存・カフ脱気確認 |
| 134 | 理学療法治療各論 | KN0428 | Q436 | 0 | critical_safety_no_strong | 湿性嗄声を不顕性誤嚥徴候として扱う嚥下安全判断 |
| 135 | 理学療法治療各論 | KN0488 | Q496 | 0 | critical_safety_no_strong | 高血糖かつケトン陽性時の運動中止判断 |
| 136 | 理学療法治療各論 | KN0489 | Q497 | 0 | critical_safety_no_strong | 副腎クリーゼを疑う低血圧・消化器症状への緊急対応 |
| 137 | 理学療法治療各論 | KN0490 | Q498 | 0 | critical_safety_no_strong | 巨細胞性動脈炎を疑う頭痛・視覚症状への緊急医療連携 |
| 138 | 理学療法治療各論 | KN0499 | Q507 | 1 | high_weight_depth_singleton | 52 歳の女性に対する適切な介入・支援選択 |
| 139 | 理学療法治療各論 | KN0516 | Q524 | 1 | high_weight_depth_singleton | 工場生産労働者の腰痛対策として、産業理学療法の観点から優先度が低いのに対する適切な介入・支援選択 |
| 140 | 理学療法治療各論 | KN0517 | Q525 | 1 | high_weight_depth_singleton | 超音波治療が可能なのはどれかに対する適切な介入・支援選択 |
| 141 | 理学療法治療各論 | KN0519 | Q527 | 1 | high_weight_depth_singleton | 部分損傷をきたした靱帯と強化すべき筋の組合せで適切なのはどれかに対する適切な介入・支援選択 |
| 142 | 理学療法治療各論 | KN0520 | Q528 | 1 | high_weight_depth_singleton | エネルギー蓄積機能によって大きな推進力を得る目的で使われる義足の足部に対する適切な介入・支援選択 |
| 143 | 理学療法治療各論 | KN0523 | Q531 | 1 | high_weight_depth_singleton | 疾患と自助具の組合せの基本事項 |
| 144 | 理学療法治療各論 | KN0578 | Q586 | 1 | high_weight_depth_singleton | 転位のない大腿骨転子部骨折に対する観血的整復固定術後の理学療法としてに対する適切な介入・支援選択 |
| 145 | 理学療法治療各論 | KN0580 | Q588 | 1 | high_weight_depth_singleton | 白杖を使用している視覚障害者の介助の特徴 |
| 146 | 理学療法治療各論 | KN0633 | Q641 | 1 | high_weight_depth_singleton | 内反足に対する靴補正の選択 |
| 147 | 理学療法治療各論 | KN0648 | Q656 | 1 | high_weight_depth_singleton | 脊髄損傷による対麻痺患者に対して立位・歩行練習を行う目的として誤っているのはどれかに対する適切な介入・装具・支援を選択する |
| 148 | 理学療法治療各論 | KN0703 | Q711 | 1 | high_weight_depth_singleton | 胸囲は安静呼吸の呼気終末に測定するのが基本である |
| 149 | 理学療法治療各論 | KN0707 | Q715 | 1 | high_weight_depth_singleton | 下腿義足のつま先浮き上がり・膝折れ傾向に対するソケットアライメント調整 |
| 150 | 理学療法治療各論 | KN0711 | Q719 | 1 | high_weight_depth_singleton | 断端成熟を追跡する再現性のある周径計測 |
| 151 | 理学療法治療各論 | KN0715 | Q723 | 1 | high_weight_depth_singleton | 運動療法の適応・目的・負荷設定の基本原則 |
| 152 | 理学療法治療各論 | KN0765 | Q773 | 1 | high_weight_depth_singleton | Parkinson病の小刻み・突進・すくみ足に対する歩行練習 |
| 153 | 理学療法治療各論 | KN0766 | Q774 | 1 | high_weight_depth_singleton | 多発性硬化症のUhthoff現象を踏まえた運動・環境調整 |
| 154 | 理学療法治療各論 | KN0768 | Q776 | 1 | high_weight_depth_singleton | Sharrard分類に応じた二分脊椎児の歩行練習・装具選択 |
| 155 | 理学療法治療各論 | KN0769 | Q777 | 1 | high_weight_depth_singleton | 広範囲熱傷・植皮術後早期の拘縮予防と創部保護を両立する理学療法 |
| 156 | 理学療法治療各論 | KN0776 | Q784 | 1 | high_weight_depth_singleton | 大腿義足遊脚期の振り出し速度を制御する膝継手機構 |
| 157 | 理学療法治療各論 | KN0783 | Q791 | 1 | high_weight_depth_singleton | 関節可動域運動の適応と実施原則 |
| 158 | 理学療法治療各論 | KN0784 | Q792 | 1 | high_weight_depth_singleton | 対象筋の作用方向に沿った求心性抵抗運動の選択 |
| 159 | 理学療法治療各論 | KN0787 | Q795 | 1 | high_weight_depth_singleton | 外側ストラップ付き金属支柱AFOの適応選択 |
| 160 | 理学療法治療各論 | KN0789 | Q797 | 1 | high_weight_depth_singleton | 慢性腰痛に対する認知行動療法の適切な介入原則 |
| 161 | 理学療法治療各論 | KN0792 | Q800 | 1 | high_weight_depth_singleton | 多発性筋炎回復初期の過用を避けた段階的運動療法 |
| 162 | 理学療法治療各論 | KN0793 | Q801 | 1 | high_weight_depth_singleton | Down症候群乳児期の低緊張・関節弛緩を踏まえた運動発達支援 |
| 163 | 理学療法治療各論 | KN0838 | Q847 | 1 | high_weight_depth_singleton | 変形性股関節症の疼痛・肥満・筋力低下を踏まえた低負荷運動選択 |
| 164 | 理学療法治療各論 | KN0841 | Q850 | 1 | critical_safety_no_strong | 除細動適応となりうる心室頻拍の識別 |
| 165 | 理学療法治療各論 | KN0853 | Q862 | 1 | high_weight_depth_singleton | 他筋への影響を抑えた選択的筋伸張肢位の決定 |
| 166 | 理学療法治療各論 | KN0855 | Q864 | 1 | high_weight_depth_singleton | PTB式装具は膝蓋腱部など耐圧性の高い部位で荷重し、脛骨粗面や腓骨頭など骨突出部は除圧する |
| 167 | 理学療法治療各論 | KN0856 | Q865 | 1 | high_weight_depth_singleton | 筋力増強運動について正しいのはどれかに対して適切な理学療法・介入を選択する |
| 168 | 理学療法治療各論 | KN0859 | Q868 | 1 | high_weight_depth_singleton | 急性期脳血管障害の離床可否を安全基準から判断する |
| 169 | 理学療法治療各論 | KN0862 | Q871 | 1 | high_weight_depth_singleton | 『ベッドアップ60°まで』と上限を固定する1が不適切時の優先対応 |
| 170 | 理学療法治療各論 | KN0912 | Q921 | 1 | high_weight_depth_singleton | 立位重心移動獲得後に行う段階的バランス練習の選択 |
| 171 | 理学療法治療各論 | KN0914 | Q923 | 1 | high_weight_depth_singleton | 亜急性腰椎椎間板ヘルニアに対する理学療法選択 |
| 172 | 理学療法治療各論 | KN0932 | Q941 | 1 | high_weight_depth_singleton | 訪問理学療法で正しいのはどれかに対して適切な理学療法・介入を選択する |
| 173 | 理学療法治療各論 | KN0997 | Q1007 | 1 | high_weight_depth_singleton | 栄養管理について正しいのはどれかに対して適切な理学療法・介入を選択する |
| 174 | 理学療法治療各論 | KN0998 | Q1008 | 1 | high_weight_depth_singleton | 持久力トレーニングでは同一運動強度での心拍・換気応答が小さくなり、最大酸素摂取量、毛細血管密度、嫌気性代謝閾値などは改善するを評価する |
| 175 | 理学療法治療各論 | KN0999 | Q1009 | 1 | high_weight_depth_singleton | 脊髄完全損傷者の機能残存レベルと実用可能な能力の組合せで正しいのはどれかに対して適切な理学療法・介入を選択する |
| 176 | 理学療法治療各論 | KN1000 | Q1010 | 1 | high_weight_depth_singleton | ACL再建術後3日では疼痛・腫脹管理、ROM、自動介助運動、筋賦活が中心で、荷重を伴うハーフスクワットは通常この時期の最優先ではないに対する機器選択 |
| 177 | 理学療法治療各論 | KN1003 | Q1013 | 1 | high_weight_depth_singleton | 呼吸障害に対する理学療法として、口すぼめ呼吸が有効なのはどれかに対して適切な理学療法・介入を選択する |
| 178 | 理学療法治療各論 | KN1004 | Q1014 | 1 | high_weight_depth_singleton | 廃用症候群について正しいのはどれかに対して適切な理学療法・介入を選択する |
| 179 | 理学療法治療各論 | KN1037 | Q1047 | 1 | high_weight_depth_singleton | 理学療法士法及び作業療法士法で正しいのはどれかに対する適切な介入・練習・指導を選択する |
| 180 | 理学療法治療各論 | KN1042 | Q1052 | 1 | high_weight_depth_singleton | 下腿義足歩行時の膝折れを生むソケット位置・膝伸展筋力などの原因推定 |
| 181 | 理学療法治療各論 | KN1050 | Q1060 | 1 | high_weight_depth_singleton | 下垂足に対するAFO背屈補助機能の適応 |
| 182 | 理学療法治療各論 | KN1060 | Q1070 | 1 | high_weight_depth_singleton | 認知症患者の運動療法で拒否を尊重し慣れた動作を用いる対応 |
| 183 | 理学療法治療各論 | KN1061 | Q1071 | 1 | high_weight_depth_singleton | 疾患・機能障害に応じた支援機器の適応選択 |
| 184 | 理学療法治療各論 | KN1101 | Q1112 | 1 | high_weight_depth_singleton | L4機能残存二分脊椎児の歩行に適した装具・杖選択 |
| 185 | 理学療法治療各論 | KN1106 | Q1117 | 1 | high_weight_depth_singleton | 支持基底面・視覚・二重課題を操作してバランス練習難度を上げる |
| 186 | 理学療法治療各論 | KN1110 | Q1121 | 1 | high_weight_depth_singleton | PEDIの対象・評価項目・評定方法 |
| 187 | 理学療法治療各論 | KN1116 | Q1127 | 1 | high_weight_depth_singleton | 全身持久力トレーニングの効果で正しいのはどれかに対する適切な介入・練習・指導を選択する |
| 188 | 理学療法治療各論 | KN1120 | Q1131 | 1 | high_weight_depth_singleton | 腰椎椎間板ヘルニア保存療法後の症状に応じた運動・姿勢指導 |
| 189 | 理学療法治療各論 | KN1122 | Q1133 | 1 | high_weight_depth_singleton | 温熱で症状悪化を招く疾患を識別し禁忌を判断する |
| 190 | 理学療法治療各論 | KN1123 | Q1134 | 1 | high_weight_depth_singleton | 重症筋無力症で過用を避けた漸増負荷運動を選択する |
| 191 | 理学療法治療各論 | KN1125 | Q1136 | 1 | high_weight_depth_singleton | 心臓リハビリテーションにおいて有酸素運動が勧められる理由として正しいのはどれかに対する適切な介入・練習・指導を選択する |
| 192 | 理学療法治療各論 | KN1126 | Q1137 | 1 | high_weight_depth_singleton | 地域リハビリテーションについて正しいのはどれかに対する適切な介入・練習・指導を選択する |
| 193 | 理学療法治療各論 | KN1167 | Q1180 | 1 | high_weight_depth_singleton | 78歳の男性に対する適切な介入・練習・指導を選択する |
| 194 | 理学療法治療各論 | KN1170 | Q1183 | 1 | high_weight_depth_singleton | 理学療法実施時のインフォームドコンセントで適切なのはどれかに対する適切な介入・練習・指導を選択する |
| 195 | 理学療法治療各論 | KN1178 | Q1192 | 1 | high_weight_depth_singleton | 下腿義足で足部外側が浮くのは、ソケットの初期内転角が大きすぎて義足全体が内反方向に傾く場合に起こる |
| 196 | 理学療法治療各論 | KN1182 | Q1196 | 1 | high_weight_depth_singleton | 筋力増強運動で正しいのはどれかに対する適切な介入・練習・指導を選択する |
| 197 | 理学療法治療各論 | KN1233 | Q1248 | 1 | high_weight_depth_singleton | 装具と疾患の組合せで正しいのはどれかに対する適切な装具・義足・機器を選択する |
| 198 | 理学療法治療各論 | KN1237 | Q1252 | 1 | high_weight_depth_singleton | 小脳性運動失調に対する四つ這いバランス練習の難易度調整 |
| 199 | 理学療法治療各論 | KN1282 | Q1298 | 1 | high_weight_depth_singleton | 関節リウマチの槌趾・中足骨頭痛に対する足底装具選択 |
| 200 | 理学療法治療各論 | KN1291 | Q1311 | 1 | high_weight_depth_singleton | 間質性肺疾患の呼吸困難・低酸素に配慮した理学療法選択 |
| 201 | 理学療法治療各論 | KN1317 | Q1337 | 1 | high_weight_depth_singleton | 内側型変形性膝関節症の内側荷重を軽減する装具療法 |
| 202 | 理学療法治療各論 | KN1319 | Q1339 | 1 | high_weight_depth_singleton | 痙直型両麻痺児のPCW歩行に対する適切な動作指導 |
| 203 | 理学療法治療各論 | KN1322 | Q1342 | 1 | high_weight_depth_singleton | 片麻痺患者の車椅子から床への移乗手順を安全性から判断する |
| 204 | 理学療法治療各論 | KN1323 | Q1343 | 1 | high_weight_depth_singleton | Lawton IADLには電話使用、買物、食事準備、家事、洗濯、交通、服薬、金銭管理が含まれるを評価する |
| 205 | 理学療法治療各論 | KN1331 | Q1351 | 1 | high_weight_depth_singleton | MRC sum scoreでICU-AWの全身筋力低下を判定する |
| 206 | 理学療法治療各論 | KN1333 | Q1353 | 1 | critical_safety_no_strong + high_weight_depth_singleton | 歩行練習中の転倒後に患者の状態確認を最優先する |
| 207 | 理学療法治療各論 | KN1353 | Q1376 | 1 | high_weight_depth_singleton | 装具療法の主たる目的でないのはどれかに対する適切な装具・義足・機器を選択する |
| 208 | 理学療法治療各論 | KN1362 | Q1385 | 1 | high_weight_depth_singleton | 足関節離断後に適した義足を選択する |
| 209 | 理学療法治療各論 | KN1364 | Q1387 | 1 | high_weight_depth_singleton | 通所リハビリでの転倒リスクを適切な尺度で評価する |
| 210 | 理学療法治療各論 | KN1365 | Q1388 | 1 | high_weight_depth_singleton | 大腿四頭筋広範囲切除後の膝伸展機能低下に対する補装具選択 |
| 211 | 理学療法治療各論 | KN1371 | Q1395 | 1 | high_weight_depth_singleton | 身体的フレイルの代表要件には歩行速度低下と身体活動量低下が含まれるを評価する |
| 212 | 理学療法治療各論 | KN1372 | Q1396 | 1 | high_weight_depth_singleton | 酸素療法機器で正しいのはどれかに対する適切な装具・義足・機器を選択する |
| 213 | 理学療法治療各論 | KN1375 | Q1399 | 1 | high_weight_depth_singleton | 体重は身体的・医学的情報であり社会的情報ではないを評価する |
| 214 | 理学療法治療各論 | KN1420 | Q1445 | 1 | high_weight_depth_singleton | ICU術後患者の意識・疼痛・循環動態から積極的離床の可否を判断する |
| 215 | 理学療法治療各論 | KN1422 | Q1447 | 1 | high_weight_depth_singleton | 間質性肺疾患の呼吸仕事量増大に対し胸郭可動性を改善する理学療法を選択する |
| 216 | 理学療法治療各論 | KN1423 | Q1448 | 1 | high_weight_depth_singleton | Pusher現象を想定し非麻痺側への能動的重心移動を促す |
| 217 | 理学療法治療各論 | KN1425 | Q1450 | 1 | high_weight_depth_singleton | 高用量昇圧剤投与中の術翌日患者で離床負荷を避け安全なベッド上介入を選択する |
| 218 | 理学療法治療各論 | KN1426 | Q1451 | 1 | critical_safety_no_strong + high_weight_depth_singleton | C6完全脊髄損傷の頭痛・顔面紅潮・著明高血圧から自律神経過反射を疑い誘因を確認する |
| 219 | 理学療法治療各論 | KN1427 | Q1452 | 1 | high_weight_depth_singleton | BPPVに対して耳石置換法〈Epley法〉を選択する |
| 220 | 理学療法治療各論 | KN1429 | Q1454 | 1 | high_weight_depth_singleton | ALSの下垂足・鶏歩に対して軽量AFOを用いた歩行を選択する |
| 221 | 理学療法治療各論 | KN1434 | Q1459 | 1 | high_weight_depth_singleton | 両側支柱付き長下肢装具の継手・半月・支柱位置の適合判定 |
| 222 | 理学療法治療各論 | KN1438 | Q1463 | 1 | high_weight_depth_singleton | 加齢性筋萎縮に対する抗重力筋中心のレジスタンストレーニング |
| 223 | 理学療法治療各論 | KN1440 | Q1465 | 1 | high_weight_depth_singleton | 脳卒中片麻痺で下肢Brunnstrom stage Vでも、立脚初期の急激な底屈や遊脚期の下垂足が残れば、足関節底屈制動式短下肢装具が適応となる |
| 224 | 理学療法治療各論 | KN1449 | Q1474 | 1 | high_weight_depth_singleton | 関節リウマチの病期・炎症活動性を踏まえ安全な理学療法を選択する |
| 225 | 理学療法治療各論 | KN1481 | Q1506 | 1 | high_weight_depth_singleton | 開腹術後の呼吸器合併症を予防する早期呼吸理学療法を選択する |
| 226 | 理学療法治療各論 | KN1482 | Q1507 | 1 | high_weight_depth_singleton | 糖尿病性末梢神経障害と足部色調変化を踏まえ前足部を免荷する |
| 227 | 理学療法治療各論 | KN1486 | Q1511 | 1 | high_weight_depth_singleton | L5レベル二分脊椎児の歩行安定性向上に必要な筋力強化対象を選択する |
| 228 | 理学療法治療各論 | KN1488 | Q1513 | 1 | high_weight_depth_singleton | 松葉杖の腋窩・握り位置などの適切な設定 |
| 229 | 理学療法治療各論 | KN1491 | Q1516 | 1 | high_weight_depth_singleton | 転倒リスクを踏まえ静的から動的へ段階づけたバランス練習を選択する |
| 230 | 理学療法治療各論 | KN1498 | Q1523 | 1 | high_weight_depth_singleton | GMFMの対象・領域・採点・Item Mapを理解する |
| 231 | 理学療法治療各論 | KN1499 | Q1524 | 1 | high_weight_depth_singleton | Berg Balance Scaleの項目・採点・解釈を理解する |
| 232 | 理学療法治療各論 | KN1559 | Q1995 | 1 | high_weight_depth_singleton | Karvonen法では目標心拍数を（予測最大心拍数－安静時心拍数）×運動強度＋安静時心拍数で求める |
| 233 | 理学療法治療各論 | KN1562 | Q1998 | 1 | high_weight_depth_singleton | 末梢神経障害による随意収縮困難な筋には、筋収縮の誘発と廃用予防を目的に神経筋電気刺激療法を用いる |

## 作問時の固定条件

- 既存Qの言い換えだけにしない。
- 同一derived Nodeの最小知識単位は維持する。
- 可能な限り既存Qと異なる task / primary ability を選び、formal STRONG confirmationを成立させる。
- official exact repeatと同一evidenceになる問題は作らない。
- Safety targetは臨床的に安全な判断を問う。
- provenanceのない「過去N年で頻出」等の主張は作らない。
- 問題・正答・解説・タグを同時に作成し、validatorを通すまでBankへ追加しない。
