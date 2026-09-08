"""Apply reviewed medical authoring for Lot01 Chunk02 (staging only)."""
from __future__ import annotations

import json
from pathlib import Path

from reports.question_bank_2000_lot01_chunk_validate import build_report

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "staging" / "question_bank_2000_lot01_chunks_v01" / "chunk_02.json"
DATE = "2026-09-08"
REVIEWER = "Aoi/GPT-5.6 Sol medical-structure review (AI; not human expert)"


def ev(url: str, support: str):
    return {"url": url, "support": support}


def review(refs: list[str], candidate: str, why: str):
    return {
        "reference_demand": f"{', '.join(refs)}: inspected formal demand(s) in same canonical Node",
        "candidate_demand": candidate,
        "why_not_same_demand": why,
        "related_formal_questions": [{"qid": qid, "relation": "same canonical Node; inspected direct formal reference"} for qid in refs],
        "decision": "accepted",
        "reviewer": REVIEWER,
        "reviewed_on": DATE,
        "expert_signoff": False,
    }


UPDATES = {
    "L01-C9-M01": {
        "title": "Parkinson病の所見統合",
        "question_text": "67歳男性。右手の安静時振戦で発症し、右優位の動作緩慢と筋強剛を認める。反復回内外運動では右側で振幅が次第に小さくなり、指鼻試験は正常である。最も考えられる病態はどれか。",
        "choices": {"1":"Parkinson病","2":"本態性振戦","3":"小脳性運動失調","4":"末梢神経障害","5":"痙性対麻痺"},
        "correct_choices": ["1"],
        "explanation": "左右差のある安静時振戦、動作緩慢、筋強剛、反復運動での振幅低下はParkinson病を支持する。小脳性運動失調を示す測定障害がない点も鑑別に有用である。",
        "choice_explanations": {
            "1":"○。動作緩慢に安静時振戦・筋強剛を伴う非対称性のパーキンソニズムである。",
            "2":"本態性振戦は主に姿勢時・動作時振戦で、明らかな動作緩慢や筋強剛を通常伴わない。",
            "3":"小脳障害では測定障害や企図振戦などが中心となる。",
            "4":"末梢神経障害では感覚障害、筋力低下、腱反射低下などが中心である。",
            "5":"痙性対麻痺は下肢優位の錐体路徴候で、本例の安静時振戦と筋強剛を説明しない。"
        },
        "clinical_intent": "複数の運動所見を統合し、単一徴候暗記ではなくParkinson病の臨床像を識別する。",
        "semantic_review": review(["Q521","Q1581"], "finding_interpretation/INTERPRET: asymmetric motor examination pattern -> Parkinson disease identification", "formal2問は突進現象・歯車様固縮・Myerson徴候などを直接選ぶfact recall。本問は左右差、反復運動のsequence effect、安静時振戦、筋強剛を統合して病態を判断させる。"),
        "evidence": [
            ev("https://www.ncbi.nlm.nih.gov/books/NBK535846/", "Parkinson disease is clinically suspected with bradykinesia/slowness plus rigidity, rest tremor and related gait/balance features; signs often begin unilaterally."),
            ev("https://www.ncbi.nlm.nih.gov/books/NBK536715/table/Ch6-t0001/", "MDS-based parkinsonism criteria require bradykinesia plus rest tremor or rigidity; cerebellar abnormalities are exclusionary for idiopathic PD."),
        ],
    },
    "L01-C9-M02": {
        "title": "活動記録からみたMS疲労",
        "question_text": "再発寛解型多発性硬化症の女性。1週間の活動・疲労記録では、午前に通勤と買い物を続けた日は午後の疲労が8/10、途中に20分休息を入れた日は4/10であった。気温との一定した関連はない。この記録から最も適切に解釈できるのはどれか。",
        "choices": {"1":"疲労は活動量と無関係である","2":"連続活動による疲労蓄積が示唆される","3":"Uhthoff現象だけで説明できる","4":"休息は疲労を必ず悪化させる","5":"歩行自立なら疲労評価は不要である"},
        "correct_choices": ["2"],
        "explanation": "同じ患者で連続活動時に疲労が強く、計画的な休息を挟むと軽いという記録は、生活活動の累積負荷と疲労の関連を示す。気温との一貫した関連がないため熱のみでは説明できない。",
        "choice_explanations": {
            "1":"活動条件によって疲労強度が変化しており、無関係とは解釈できない。",
            "2":"○。活動記録から連続した生活活動が疲労を増強し、休息配置で軽減するパターンが読み取れる。",
            "3":"Uhthoff現象は体温上昇に伴う一過性症状増悪であり、本記録では気温との一定した関連がない。",
            "4":"本例では休息を挟んだ日の方が疲労が軽い。",
            "5":"歩行自立でもMS関連疲労は仕事・家事・認知活動に影響し得る。"
        },
        "clinical_intent": "活動記録を処方するのではなく、記録された時間系列から疲労を増悪させる生活パターンを解釈する。",
        "semantic_review": review(["Q68","Q191"], "finding_interpretation/INTERPRET: activity-fatigue diary pattern -> identify cumulative-load association", "Q68/Q191はいずれも活動記録とpacingを介入として選ぶPRESCRIBE問題。本問は既に得られた活動・疲労記録のデータを読み取るINTERPRET需要である。"),
        "evidence": [ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC3196037/", "MS fatigue management includes pacing activities through the day, regular rest breaks, energy conservation and individualized assessment of fatigue and its functional impact.")],
    },
    "L01-C9-M03": {
        "title": "半側空間無視の機能予後",
        "question_text": "右半球脳卒中後3週。左単独刺激には反応できるが両側同時刺激では左を消去し、病棟では左側の物への衝突が頻回である。同程度の運動麻痺で無視のない患者と比べた機能予後として最も適切なのはどれか。",
        "choices": {"1":"ADL予後は必ず良好である","2":"転倒や機能自立低下のリスクが高い","3":"入院期間は必ず短くなる","4":"無視の程度は退院時機能と関連しない","5":"運動麻痺が同程度なら予後差は生じない"},
        "correct_choices": ["2"],
        "explanation": "半側空間無視は脳卒中リハビリテーションで機能自立度低下、転倒増加、入院長期化などと関連する。運動麻痺が同程度でも無視の存在・重症度は機能予後を悪化させ得る。",
        "choice_explanations": {
            "1":"無視はADL自立を妨げる重要な認知障害であり、必ず良好とはいえない。",
            "2":"○。無視は低いFIM、転倒増加、長い在院日数など不良なリハビリテーション転帰と関連する。",
            "3":"無視がある患者ではむしろ在院期間が長くなる関連が報告されている。",
            "4":"無視重症度は退院時FIMや回復効率と関連する。",
            "5":"同程度の運動障害でも無視そのものが機能転帰へ影響し得る。"
        },
        "clinical_intent": "消去現象を識別するだけでなく、その存在から病棟ADL・転倒を含む機能予後を推定する。",
        "semantic_review": review(["Q209","Q279"], "prognosis_prediction/PREDICT: demonstrated extinction/neglect -> predict rehabilitation functional risk", "formal2問は両側同時刺激から消去現象を同定するINTERPRET問題。本問では消去現象が確認済みで、その後のADL・転倒・在院期間など機能転帰を予測する。"),
        "evidence": [
            ev("https://pubmed.ncbi.nlm.nih.gov/21807144/", "Unilateral spatial neglect severity at rehabilitation admission independently predicts discharge FIM, FIM efficiency and effectiveness."),
            ev("https://pubmed.ncbi.nlm.nih.gov/25862254/", "Spatial neglect severity is associated with lower FIM, longer length of stay, lower improvement rate and substantially more falls."),
        ],
    },
    "L01-C16-S01": {
        "title": "外側上顆炎の誘発所見",
        "question_text": "46歳女性。右肘外側痛があり、ドライバー作業とコーヒーカップを持つ動作で増悪する。外側上顆周囲に圧痛があり、感覚障害はない。診断を支持する誘発所見はどれか。",
        "choices": {"1":"抵抗下手関節伸展で外側上顆痛が再現する","2":"抵抗下手関節屈曲で内側上顆痛が再現する","3":"頸部伸展で上肢放散痛が再現する","4":"Phalenテストで母指から環指橈側がしびれる","5":"肘屈曲で尺側手指のしびれだけが再現する"},
        "correct_choices": ["1"],
        "explanation": "上腕骨外側上顆炎では外側上顆付近の圧痛と、抵抗下手関節伸展などでの疼痛再現が典型的である。しびれなど神経症状が主体なら別病態を考える。",
        "choice_explanations": {
            "1":"○。抵抗下の手関節伸展は総伸筋腱起始部へ負荷をかけ、外側上顆痛を再現しやすい。",
            "2":"これは内側上顆炎を示唆する誘発パターンである。",
            "3":"頸部由来の放散痛なら頸椎神経根症などを考える。",
            "4":"Phalenテスト陽性は手根管症候群を示唆する。",
            "5":"尺側手指のしびれは尺骨神経障害を示唆する。"
        },
        "clinical_intent": "症状と誘発テストを対応させて外側上顆炎を臨床的に識別する。",
        "semantic_review": review(["Q564"], "finding_interpretation/INTERPRET: symptom pattern + provocation test -> support lateral epicondylitis", "Q564は伸筋腱付着部病変という病態知識を直接問う。本問は作業時痛・圧痛・抵抗下伸展での疼痛再現を臨床所見として解釈させる。"),
        "evidence": [
            ev("https://www.ncbi.nlm.nih.gov/books/NBK431092/", "Lateral epicondylitis produces lateral elbow tenderness and pain reproduced by resisted wrist extension; sensory symptoms suggest an alternative diagnosis."),
            ev("https://ncbi.nlm.nih.gov/books/NBK585755/", "The tennis elbow test reproduces lateral epicondylar pain when wrist/elbow extension is performed against resistance."),
        ],
    },
    "L01-C16-S02": {
        "title": "肘関節脱臼と神経血管障害",
        "question_text": "転倒して伸展位の手をついた直後から肘が変形し、前腕が短く見える。手指にしびれがあり橈骨動脈を触知しにくく、手部は健側より冷たい。最優先の対応はどれか。",
        "choices": {"1":"疼痛範囲内で自動運動を開始する","2":"神経血管障害を伴う脱臼として緊急整形外科対応を求める","3":"翌日までアイシングのみで経過を見る","4":"抵抗運動で肘周囲筋を評価する","5":"徒手で反復して可動域を確認する"},
        "correct_choices": ["2"],
        "explanation": "後方肘関節脱臼では上肢が短縮して見えることがあり、血管・神経損傷を伴い得る。脈拍低下と冷感は神経血管障害を示すため、運動評価より緊急の整形外科的整復・評価を優先する。",
        "choice_explanations": {
            "1":"脱臼と神経血管障害が疑われる急性期に運動開始を優先してはならない。",
            "2":"○。冷感や脈拍低下を伴う脱臼は肢の血流障害が疑われ、緊急対応が必要である。",
            "3":"血管障害を疑う所見があるため翌日まで待機するのは危険である。",
            "4":"抵抗運動より神経血管評価と緊急整復が優先される。",
            "5":"不必要な反復操作は行わず、専門的な整復・画像評価につなげる。"
        },
        "clinical_intent": "肘脱臼の典型機転・変形に神経血管障害が加わった場面で、運動器評価より肢救済を優先する。",
        "semantic_review": review(["Q580"], "safety_priority/DECIDE: suspected posterior elbow dislocation with ischemic signs -> urgent neurovascular/orthopedic management", "Q580は後方脱臼が最多というfact recall。本問は外傷機転と血流障害から緊急性を判断し、初期対応を選ばせる。"),
        "evidence": [
            ev("https://www.ncbi.nlm.nih.gov/books/NBK470574/", "Posterior elbow dislocation requires careful distal neurovascular assessment; signs of neurovascular compromise require immediate closed reduction and reassessment."),
            ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC5721315/", "Neurovascular status should be documented before and after elbow reduction because entrapment can require urgent surgical management."),
        ],
    },
    "L01-C16-S03": {
        "title": "腰椎分離症疑いの競技対応",
        "question_text": "15歳男子体操選手。2週間前から腰椎伸展・回旋で増悪する限局性腰痛があり、反復ジャンプ後に強くなる。下肢筋力・感覚・腱反射は正常で膀胱直腸障害はない。現時点で最も適切な対応はどれか。",
        "choices": {"1":"痛みを我慢して伸展練習を継続する","2":"競技負荷を一時中止し腰椎分離症を含む骨ストレス障害の評価につなげる","3":"最大負荷の体幹伸展筋力訓練を開始する","4":"神経症状がないため評価は不要である","5":"痛みが強い日にだけ反復伸展を増やす"},
        "correct_choices": ["2"],
        "explanation": "成長期競技者で反復する伸展・回旋により増悪する腰痛は腰椎分離症などparsの骨ストレス障害を疑う。神経学的赤旗がなくても、疼痛を誘発する競技負荷を継続せず評価と段階的リハビリテーションにつなげる。",
        "choice_explanations": {
            "1":"症状を誘発する反復伸展・回旋を継続すると骨ストレスを増やす可能性がある。",
            "2":"○。競技負荷を修正し、分離症を含む骨ストレス障害として評価するのが適切である。",
            "3":"急性期に疼痛を誘発する最大負荷伸展を開始するのは不適切である。",
            "4":"神経症状がなくても成長期アスリートの反復伸展痛は評価対象となる。",
            "5":"疼痛時に負荷を増やす根拠はない。"
        },
        "safety": "moderate",
        "clinical_intent": "成長期スポーツ選手の伸展関連腰痛で骨ストレス障害を疑い、無理な競技継続を止めるSafety判断を行う。",
        "semantic_review": review(["Q587"], "safety_priority/DECIDE: adolescent extension-related back pain -> stop provocative load and obtain evaluation", "Q587は椎弓関節突起間部の分離という解剖学的fact recall。本問は典型的な競技歴・疼痛誘発動作から安全な負荷管理を判断する。Safetyは生命・肢救済級ではないためcriticalからmoderateへ医学的に修正した。"),
        "evidence": [
            ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC7134351/", "Adolescent athlete spondylolysis is commonly managed non-operatively with cessation/modification of sport activity and progressive rehabilitation; repetitive forceful extension/rotation stresses the pars interarticularis."),
            ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC12911598/", "Recent multicenter trial supports structured physical therapy for active lumbar spondylolysis and symptom/function-guided return rather than continued provocative sport loading."),
        ],
    },
    "L01-C16-S04": {
        "title": "上腕骨顆上骨折の血流障害",
        "question_text": "7歳男児。転倒後に肘周囲の腫脹と変形を認める。手は蒼白で冷たく、橈骨動脈を触知できず毛細血管再充満も遅延している。上腕骨顆上骨折が疑われる。最優先の対応はどれか。",
        "choices": {"1":"翌日の外来受診まで安静にする","2":"肘の自動運動を反復させる","3":"循環障害を伴う骨折として直ちに緊急整形外科対応へつなぐ","4":"温熱療法で末梢循環を改善する","5":"前腕筋の抵抗運動で筋力を確認する"},
        "correct_choices": ["3"],
        "explanation": "小児上腕骨顆上骨折では上腕動脈損傷による前腕・手の循環障害が重要な合併症である。脈拍消失に加えて蒼白・冷感・毛細血管再充満遅延がある poorly perfused hand は肢救済を要する緊急状態である。",
        "choice_explanations": {
            "1":"血流障害所見があるため翌日まで待つのは危険である。",
            "2":"急性骨折と虚血が疑われる状況で反復運動は行わない。",
            "3":"○。poorly perfused pulseless handは緊急整復・血管評価を要する。",
            "4":"温熱で原因となる動脈障害は解決できず、緊急評価を遅らせてはならない。",
            "5":"抵抗運動より血流回復を目的とした緊急整形外科対応が優先される。"
        },
        "clinical_intent": "小児顆上骨折で血管障害を見逃さず、運動療法より肢救済の緊急対応を優先する。",
        "semantic_review": review(["Q624"], "safety_priority/DECIDE: supracondylar fracture + poorly perfused pulseless hand -> emergency management", "Q624は前腕循環不全を起こしやすいという知識を直接問う。本問は実際の虚血所見から緊急性と初期対応を決定させる。"),
        "evidence": [
            ev("https://pubmed.ncbi.nlm.nih.gov/26041856/", "A pulseless, poorly perfused hand with pediatric supracondylar humeral fracture requires emergency operative reduction; persistent poor perfusion may require vascular exploration."),
            ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC4242976/", "Pulseless pale/cold hand, delayed/absent perfusion signs after supracondylar fracture indicate vascular compromise requiring urgent restoration of circulation."),
        ],
    },
    "L01-C16-S05": {
        "title": "RA機能分類の解釈",
        "question_text": "関節リウマチの52歳女性。更衣・食事・入浴は自立し、事務職も通常どおり継続できるが、趣味のテニスは関節痛のため行えない。ACRの機能状態分類として最も適切なのはどれか。",
        "choices": {"1":"Class I","2":"Class II","3":"Class III","4":"Class IV","5":"機能分類は疾患活動性だけで決めるため判定不能"},
        "correct_choices": ["2"],
        "explanation": "ACR revised functional statusでは、self-careとvocational activityは通常どおり可能だがavocational activityが制限される場合はClass IIである。",
        "choice_explanations": {
            "1":"Class Iはself-care、仕事、余暇の通常活動をすべて行える。",
            "2":"○。身の回り動作と仕事は可能で、余暇活動のみ制限されるためClass IIである。",
            "3":"Class IIIはself-careは可能だが仕事と余暇活動が制限される。",
            "4":"Class IVはself-careを含む通常活動が制限される。",
            "5":"機能状態分類はself-care、vocational、avocational activitiesの可否から判断できる。"
        },
        "clinical_intent": "分類名の暗記ではなく、患者のself-care・仕事・余暇の実生活情報から機能classを判定する。",
        "semantic_review": review(["Q642"], "finding_interpretation/INTERPRET: functional narrative -> assign RA global functional class", "Q642は余暇・仕事・身の回り動作を用いる指標名を問うfact recall。本問は具体的な生活能力を分類基準へ当てはめてClass IIと解釈させる。"),
        "evidence": [
            ev("https://pubmed.ncbi.nlm.nih.gov/1575785/", "ACR revised RA functional status: Class II means usual self-care and vocational activities are possible while avocational activities are limited; Class III limits vocational and avocational activity while self-care remains possible."),
            ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC3941968/", "Published RA studies operationalize the four ACR functional classes using self-care, vocational and avocational activity capability."),
        ],
    },
}


def main() -> int:
    payload = json.loads(PATH.read_text(encoding="utf-8-sig"))
    seen = set()
    for draft in payload["drafts"]:
        did = draft["draft_id"]
        if did not in UPDATES:
            raise SystemExit(f"unexpected draft in Chunk02: {did}")
        draft.update(UPDATES[did])
        draft["status"] = "accepted"
        draft["reviewed_sha256"] = ""
        seen.add(did)
    if seen != set(UPDATES):
        raise SystemExit(f"missing drafts: {sorted(set(UPDATES) - seen)}")
    payload["status"] = "completed_chunk"
    report = build_report(payload)
    if report["hard_errors"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit("Chunk02 authoring validation failed")
    PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"completed_chunk": 2, "drafts": 8, "hard_errors": [], "expert_signoff_true": 0, "safety_adjustment": "L01-C16-S03 critical->moderate"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
