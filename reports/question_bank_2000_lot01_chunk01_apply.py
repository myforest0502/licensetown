"""Apply the reviewed medical authoring draft for Lot01 Chunk01.

One-shot authoring helper. It writes only the staging chunk and never allocates
formal Q IDs or Knowledge Node IDs.
"""
from __future__ import annotations

import json
from pathlib import Path

from reports.question_bank_2000_lot01_chunk_validate import build_report

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "staging" / "question_bank_2000_lot01_chunks_v01" / "chunk_01.json"
DATE = "2026-09-08"
REVIEWER = "Aoi/GPT-5.6 Sol medical-structure review (AI; not human expert)"


def ev(url: str, support: str):
    return {"url": url, "support": support}


def review(reference_qid: str, candidate: str, why: str):
    return {
        "reference_demand": f"{reference_qid}: direct fact_recall/KNOW in the same canonical Node",
        "candidate_demand": candidate,
        "why_not_same_demand": why,
        "related_formal_questions": [
            {"qid": reference_qid, "relation": "same canonical Node; inspected direct formal reference"}
        ],
        "decision": "accepted",
        "reviewer": REVIEWER,
        "reviewed_on": DATE,
        "expert_signoff": False,
    }


UPDATES = {
    "L01-C9-S01": {
        "title": "中心性脊髄損傷の臨床像",
        "question_text": "頸椎症のある78歳男性。転倒して額を打ち頸部が過伸展した。下肢は介助で立位できるが、両手の巧緻動作と上肢筋力の低下が著明である。肛門周囲感覚は保たれている。最も考えられる病態はどれか。",
        "choices": {"1":"前脊髄動脈症候群","2":"Brown-Séquard症候群","3":"中心性脊髄損傷","4":"脊髄円錐症候群","5":"馬尾症候群"},
        "correct_choices": ["3"],
        "explanation": "高齢者の頸椎過伸展外傷後に、下肢より上肢の運動障害が強く、仙髄機能が保たれる所見は中心性脊髄損傷に典型的である。",
        "choice_explanations": {
            "1":"前脊髄動脈症候群では運動麻痺と温痛覚障害が主体で、上肢優位麻痺という本例の分布とは合いにくい。",
            "2":"Brown-Séquard症候群では病変側の運動・深部感覚障害と反対側の温痛覚障害という半側性の所見が中心となる。",
            "3":"○。頸椎過伸展、上肢優位の筋力低下、仙髄機能の温存が中心性脊髄損傷を支持する。",
            "4":"脊髄円錐症候群では会陰部感覚や膀胱直腸機能の障害が目立ちやすい。",
            "5":"馬尾症候群では下位運動ニューロン性の下肢症状や膀胱直腸障害が中心で、本例の上肢優位障害を説明しない。"
        },
        "clinical_intent": "外傷機転と麻痺分布を統合して不完全脊髄損傷の臨床型を識別する。",
        "semantic_review": review("Q561", "finding_interpretation/INTERPRET: mechanism + neurologic distribution -> syndrome identification", "Q561は中心性脊髄損傷の特徴を直接選ぶ知識問題である。本問は年齢、過伸展機転、上肢優位麻痺、仙髄機能温存を統合して病態を同定させる。"),
        "evidence": [ev("https://www.ncbi.nlm.nih.gov/books/NBK441932/", "Central cord syndrome commonly follows cervical hyperextension in older adults with stenosis and causes disproportionate upper-extremity weakness with possible sacral sparing.")],
    },
    "L01-C9-S02": {
        "title": "多発性硬化症の長期予後",
        "question_text": "再発寛解型多発性硬化症の30歳女性。発症後18か月で3回再発し、各再発後に歩行障害が完全には回復せず障害度が徐々に増している。長期の身体障害進行リスクについて最も適切なのはどれか。",
        "choices": {"1":"再発頻度は長期障害と関連しない","2":"早期の反復再発と不完全回復はリスクを高める","3":"女性であることだけで予後不良と判断する","4":"30歳発症なら進行性障害は生じない","5":"初期の障害度は長期予後と関連しない"},
        "correct_choices": ["2"],
        "explanation": "多発性硬化症では早期の高い疾患活動性、再発、初期からの障害や回復不良などが長期障害進行と関連する。本例は短期間の反復再発と不完全回復があり、より注意を要する経過である。",
        "choice_explanations": {
            "1":"再発はその後の障害悪化と関連し、再発頻度が高い経過は予後評価上重要である。",
            "2":"○。早期の反復再発と障害の残存は長期障害リスクを高める所見として扱われる。",
            "3":"性別単独の予後効果は一貫せず、本例の疾患活動性より優先して判断する根拠にはならない。",
            "4":"若年発症でも長期的な障害進行は起こり得る。",
            "5":"初期の障害度や疾患活動性は長期予後と関連する。"
        },
        "clinical_intent": "再発寛解型MSの早期経過から長期障害リスクを推定する。",
        "semantic_review": review("Q566", "prognosis_prediction/PREDICT: early relapse/recovery pattern -> long-term disability risk", "Q566はMSが再発と寛解を繰り返すことを直接問う。本問は再発頻度と不完全回復という経過情報から長期障害リスクを予測させる。"),
        "evidence": [
            ev("https://pubmed.ncbi.nlm.nih.gov/40818446/", "Systematic review identifies baseline disability and disease activity, including recent relapses, among factors associated with poorer long-term disability outcomes in MS."),
            ev("https://pubmed.ncbi.nlm.nih.gov/17172607/", "Systematic review reports incomplete recovery from the first attack and a short interval to the second attack among consistent predictors of poorer long-term physical disability in relapsing-remitting MS."),
        ],
    },
    "L01-C9-S03": {
        "title": "ALSの所見統合",
        "question_text": "64歳男性。1年かけて右手の筋萎縮と線維束性収縮が進行し、両下肢では腱反射亢進とBabinski反射陽性を認める。感覚障害と膀胱直腸障害はない。最も考えられる疾患はどれか。",
        "choices": {"1":"慢性炎症性脱髄性多発根ニューロパチー","2":"重症筋無力症","3":"筋萎縮性側索硬化症","4":"Parkinson病","5":"Duchenne型筋ジストロフィー"},
        "correct_choices": ["3"],
        "explanation": "進行性の下位運動ニューロン徴候である筋萎縮・線維束性収縮と、上位運動ニューロン徴候である腱反射亢進・Babinski反射を併せ、感覚障害が乏しいことはALSを強く示唆する。",
        "choice_explanations": {
            "1":"CIDPでは感覚障害や腱反射低下を伴うことが多く、上下位運動ニューロン徴候の併存とは合いにくい。",
            "2":"重症筋無力症は易疲労性が中心で、筋萎縮・線維束性収縮やBabinski反射を説明しない。",
            "3":"○。上位・下位運動ニューロン徴候が併存し、感覚系が比較的保たれる進行性病像はALSに典型的である。",
            "4":"Parkinson病は動作緩慢、筋強剛、振戦などが主体で、本例の運動ニューロン徴候を説明しない。",
            "5":"Duchenne型筋ジストロフィーは小児期発症の筋疾患であり、本例の年齢と錐体路徴候に合わない。"
        },
        "clinical_intent": "上位・下位運動ニューロン徴候と感覚温存を統合してALSを識別する。",
        "semantic_review": review("Q582", "finding_interpretation/INTERPRET: mixed UMN/LMN examination pattern -> disease identification", "Q582はALSで生じにくい症状の直接知識を問う。本問は複数の神経学的所見を統合して疾患を同定させる。"),
        "evidence": [
            ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC6179867/", "ALS examination includes UMN signs such as spasticity/hyperreflexia and LMN signs such as weakness, atrophy and fasciculations; sensory function is typically spared."),
            ev("https://www.ncbi.nlm.nih.gov/books/NBK573427/", "ALS commonly shows fasciculations, weakness and atrophy, while numbness/paresthesia and sphincter dysfunction are generally absent."),
        ],
    },
    "L01-C9-S04": {
        "title": "自律神経過反射の初期対応",
        "question_text": "T4完全脊髄損傷の患者。車椅子座位中に突然の激しい頭痛と顔面紅潮が出現し、血圧210/110 mmHgで尿道留置カテーテルの排液が止まっている。最初に行う対応はどれか。",
        "choices": {"1":"仰臥位にして下肢を挙上する","2":"上体を起こし下肢を下げる","3":"膀胱を強く圧迫して排尿を促す","4":"そのまま運動を継続する","5":"30分安静にしてから再測定する"},
        "correct_choices": ["2"],
        "explanation": "T6以上の脊髄損傷で急激な高血圧、頭痛、顔面紅潮が出現すれば自律神経過反射を疑う。初期対応では直ちに座位・上体挙上として下肢を下げ、血圧低下を図りながら誘因を検索・除去する。",
        "choice_explanations": {
            "1":"仰臥位・下肢挙上は血圧をさらに高く保つ方向に働き得るため初期対応として不適切である。",
            "2":"○。直ちに座位または上体を起こして下肢を下げることが推奨される初期対応である。",
            "3":"膀胱圧迫などの刺激は自律神経過反射を悪化させ得る。閉塞カテーテルは安全に確認・解除する。",
            "4":"高血圧性緊急状態であり運動継続は不適切である。",
            "5":"重篤な高血圧を伴うため経過観察だけで待機してはならない。"
        },
        "clinical_intent": "自律神経過反射を認識し、生命を守る初期姿勢対応を最優先で選択する。",
        "semantic_review": review("Q621", "safety_priority/DECIDE: suspected autonomic dysreflexia -> immediate first action", "Q621は自律神経過反射の典型所見を選ばせる。本問は所見を認識した後の緊急初期対応を決定させるSafety問題である。"),
        "evidence": [
            ev("https://www.ncbi.nlm.nih.gov/books/NBK482434/", "Emergency management of autonomic dysreflexia begins by immediately sitting the patient upright with legs dangling, loosening constrictive items, monitoring blood pressure and identifying triggers such as bladder obstruction."),
            ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC10744198/", "Clinical recommendations include sitting the patient upright, lowering the legs, removing tight clothing, frequent blood pressure checks, and resolving the trigger."),
        ],
    },
    "L01-C9-S05": {
        "title": "NIHSS意識項目の解釈",
        "question_text": "急性期脳卒中患者。覚醒しており、年齢は正答したが現在の月を誤答した。開閉眼と手の握り・開放の2つの命令は両方実行できた。NIHSSの意識関連項目の解釈で正しいのはどれか。",
        "choices": {"1":"1a〈意識水準〉は2点である","2":"1b〈意識に関する質問〉は1点である","3":"1b〈意識に関する質問〉は2点である","4":"1c〈意識に関する命令〉は1点である","5":"意識関連3項目はすべて0点である"},
        "correct_choices": ["2"],
        "explanation": "NIHSS 1bでは月と年齢を尋ね、両方正答0点、1つ正答1点、両方誤答2点とする。本例は年齢のみ正答なので1点である。命令は両方実行できるため1cは0点となる。",
        "choice_explanations": {
            "1":"患者は覚醒しており、提示情報から1aを2点とする根拠はない。",
            "2":"○。月と年齢のうち1つだけ正答しているため1bは1点である。",
            "3":"1bが2点となるのは月と年齢の両方に正答できない場合である。",
            "4":"1cは2つの命令を両方実行できれば0点である。",
            "5":"月を誤答しているため1bは0点ではない。"
        },
        "clinical_intent": "NIHSSの意識質問・命令の実施結果から得点を正しく解釈する。",
        "semantic_review": review("Q646", "finding_interpretation/INTERPRET: observed NIHSS LOC responses -> item score interpretation", "Q646はNIHSSに意識評価が含まれることを直接問う。本問は実際の回答・命令遂行から1b/1cの得点を解釈させる。"),
        "evidence": [
            ev("https://www.ninds.nih.gov/sites/default/files/documents/NIH_Stroke_Scale_508C_0.pdf", "Official NIH Stroke Scale instructions state that LOC questions ask month and age; both correct scores 0, one correct scores 1, and neither correct scores 2."),
            ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC10564032/", "NIHSS summary lists LOC questions (month, age) scoring 0 for both correct, 1 for one correct and 2 for both incorrect, with separate LOC command scoring."),
        ],
    },
    "L01-C9-S06": {
        "title": "Parkinson病の運動・非運動症状",
        "question_text": "69歳男性。数年前から便秘と睡眠中の夢内容に伴う激しい体動があり、最近は右手の安静時振戦、動作緩慢、歯車様筋強剛が進行した。四肢の測定障害はない。最も考えられる疾患はどれか。",
        "choices": {"1":"Parkinson病","2":"本態性振戦","3":"脊髄小脳変性症","4":"重症筋無力症","5":"末梢性多発ニューロパチー"},
        "correct_choices": ["1"],
        "explanation": "安静時振戦、動作緩慢、筋強剛というParkinson症候に、便秘やREM睡眠行動障害を示唆する非運動症状が先行しており、Parkinson病が最も考えられる。",
        "choice_explanations": {
            "1":"○。運動症状に加えて便秘やREM睡眠行動障害などの非運動症状がみられる。",
            "2":"本態性振戦は主に姿勢時・動作時振戦で、動作緩慢や筋強剛を通常伴わない。",
            "3":"脊髄小脳変性症では運動失調が中心となり、本例では測定障害がない。",
            "4":"重症筋無力症は易疲労性筋力低下が主体で、安静時振戦や筋強剛を説明しない。",
            "5":"末梢性多発ニューロパチーでは感覚障害や腱反射低下などが中心となる。"
        },
        "clinical_intent": "運動症状と先行する非運動症状を統合してParkinson病を識別する。",
        "semantic_review": review("Q695", "finding_interpretation/INTERPRET: combined prodromal/nonmotor and motor pattern -> disease identification", "Q695はParkinson病でみられる症状を直接識別する知識問題である。本問は便秘・睡眠症状と運動症状の時間経過を統合して疾患を判断させる。"),
        "evidence": [ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC4779953/", "Parkinson disease core motor features include bradykinesia, rigidity and resting tremor; nonmotor manifestations include constipation and REM sleep behavior disorder.")],
    },
    "L01-C9-S07": {
        "title": "ALSの下位運動ニューロン徴候",
        "question_text": "ALS疑い患者。右母指球筋萎縮と線維束性収縮、右上腕二頭筋反射低下、両下肢痙縮と腱反射亢進、Babinski反射陽性を認める。下位運動ニューロン障害を示す所見の組合せはどれか。",
        "choices": {"1":"両下肢痙縮＋Babinski反射陽性","2":"腱反射亢進＋Babinski反射陽性","3":"母指球筋萎縮＋線維束性収縮＋反射低下","4":"痙縮＋腱反射亢進＋線維束性収縮","5":"Babinski反射陽性＋反射低下"},
        "correct_choices": ["3"],
        "explanation": "下位運動ニューロン障害では筋力低下、筋萎縮、線維束性収縮、腱反射低下などを認める。痙縮、腱反射亢進、Babinski反射陽性は上位運動ニューロン徴候である。",
        "choice_explanations": {
            "1":"痙縮とBabinski反射陽性はいずれも上位運動ニューロン徴候である。",
            "2":"腱反射亢進とBabinski反射陽性はいずれも上位運動ニューロン徴候である。",
            "3":"○。筋萎縮、線維束性収縮、腱反射低下は下位運動ニューロン障害を示す。",
            "4":"線維束性収縮は下位運動ニューロン徴候だが、痙縮と腱反射亢進は上位運動ニューロン徴候である。",
            "5":"反射低下は下位運動ニューロン徴候だが、Babinski反射陽性は上位運動ニューロン徴候である。"
        },
        "clinical_intent": "同一患者に混在する上位・下位運動ニューロン徴候を神経診察から分類する。",
        "semantic_review": review("Q789", "finding_interpretation/INTERPRET: mixed examination findings -> identify LMN-sign subset", "Q789は線維束性収縮が下位運動ニューロン徴候であることを単独で問う。本問は複数の診察所見からLMN徴候の組合せを選別させる。"),
        "evidence": [ev("https://pmc.ncbi.nlm.nih.gov/articles/PMC6179867/", "ALS UMN signs include spasticity and hyperreflexia, while LMN signs include weakness, muscle atrophy and fasciculations.")],
    },
    "L01-C9-S08": {
        "title": "意識が保たれる焦点発作",
        "question_text": "25歳男性。右手から始まる間代性けいれんが約40秒続いた。発作中も呼名に応じ、終了後には発作中の出来事を詳しく説明できた。この発作の解釈で最も適切なのはどれか。",
        "choices": {"1":"意識が保たれる焦点発作は起こり得る","2":"意識が保たれているためてんかん発作ではない","3":"てんかん発作では必ず意識障害を伴う","4":"この所見だけで全般欠神発作と判断する","5":"呼名に応じたため心因性非てんかん発作と確定する"},
        "correct_choices": ["1"],
        "explanation": "焦点発作では意識・認識が保たれる発作があり、局所の運動症状を呈しながら発作中の出来事を認識・想起できることがある。意識保持だけでてんかん発作を否定してはならない。",
        "choice_explanations": {
            "1":"○。焦点発作では意識が保たれる型が存在する。",
            "2":"意識保持は焦点発作を否定する所見ではない。",
            "3":"てんかん発作すべてに意識障害が必発するわけではない。",
            "4":"全般欠神発作では通常、短時間の意識・反応性の障害が中心で、本例の一側性間代性運動とは合わない。",
            "5":"発作中の反応性・意識保持だけで心因性非てんかん発作を確定することはできない。"
        },
        "clinical_intent": "局所運動症状と意識保持を同時に認める発作を、意識障害必発という誤解なく解釈する。",
        "semantic_review": review("Q839", "finding_interpretation/INTERPRET: observed unilateral motor event with retained awareness -> seizure interpretation", "Q839はてんかんの一般的事実と意識障害が必発ではないことを知識として問う。本問は実際の発作中の運動症状・反応性・記憶から焦点発作を解釈させる。"),
        "evidence": [
            ev("https://www.ilae.org/files/dmfile/Operational-Classification---Instruction-manual-Fisher_et_al-2017-Epilepsia-1.pdf", "ILAE operational classification recognizes focal aware seizures in which awareness is retained; responsiveness is a separate clinical attribute."),
            ev("https://www.ilae.org/updated-classification-epileptic-seizures-2025", "The updated ILAE classification retains focal seizures and uses consciousness as a classifier, reinforcing that focal seizures need not uniformly present with loss of consciousness."),
        ],
    },
}


def main() -> int:
    payload = json.loads(PATH.read_text(encoding="utf-8-sig"))
    seen = set()
    for draft in payload["drafts"]:
        did = draft["draft_id"]
        if did not in UPDATES:
            raise SystemExit(f"unexpected draft in Chunk01: {did}")
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
        raise SystemExit("Chunk01 authoring validation failed")
    PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"completed_chunk": 1, "drafts": 8, "hard_errors": [], "expert_signoff_true": 0}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
