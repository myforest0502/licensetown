"""Atomically integrate six source-verified past-exam items as Q1995-Q2000."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
START_Q, END_Q = 1995, 2000
BASE_END = 1994
TARGET_VERSION = "2026-09-b20"
QID_PATTERN = r"^Q(?:[1-9]|[1-9][0-9]{1,2}|1[0-9]{3}|2000)$"

ITEMS = [
    {
        "id": "Q1995", "question_no": 4, "category_large": "C", "category_small": 18,
        "node_id": "KN1559", "new_node": "Karvonen法では目標心拍数を（予測最大心拍数－安静時心拍数）×運動強度＋安静時心拍数で求める",
        "question_text": "70歳の女性。急性心筋梗塞で入院した。身長160cm、体重70kg。安静時心拍数70/分、安静時血圧130/70mmHg。心臓超音波検査にて低左心機能（LVEF＜40%）が指摘されている。\nKarvonen法（k＝0.5）を用いて計算した全身持久力運動の目標心拍数で正しいのはどれか。",
        "choices": {"1": "90/分", "2": "100/分", "3": "110/分", "4": "120/分", "5": "130/分"},
        "answers": ["3"], "task": "finding_interpretation", "ability": "INTERPRET", "level": 2, "safety": "moderate",
        "explanation": "予測最大心拍数は220－70＝150/分である。Karvonen法では（150－70）×0.5＋70＝110/分となる。",
        "choice_explanations": {"1": "90/分は心拍予備能の50%を加える計算より低い。", "2": "100/分はKarvonen法による算出値ではない。", "3": "正しい。心拍予備能80/分の50%を安静時心拍数70/分に加えると110/分となる。", "4": "120/分は心拍予備能と安静時心拍数を用いた計算値より高い。", "5": "130/分は本条件のk＝0.5で求める強度を上回る。"},
        "prerequisites": ["目標心拍数の計算では年齢から予測最大心拍数を求め、安静時心拍数との差を心拍予備能とする。"],
    },
    {
        "id": "Q1996", "question_no": 12, "category_large": "C", "category_small": 14,
        "node_id": "KN1560", "new_node": "Frenkel体操は視覚代償を用いて四肢運動を反復し、深部感覚障害による脊髄性運動失調の協調性改善を図る",
        "question_text": "58歳の男性。胸髄の脊髄腫瘍摘出術後、両下肢に明らかな運動麻痺、表在感覚障害はないが、深部感覚に重度鈍麻がみられた。開眼すると立位保持可能だが、閉眼するとふらついて倒れそうになる。また、歩行時にもふらつきがあり、踵打歩行が認められる。\n運動療法で適切なのはどれか。",
        "choices": {"1": "Buerger体操", "2": "Codman体操", "3": "Frenkel体操", "4": "Klapp体操", "5": "Williams体操"},
        "answers": ["3"], "task": "intervention_selection", "ability": "PRESCRIBE", "level": 3, "safety": "none",
        "explanation": "深部感覚障害により視覚遮断で動揺が増える脊髄性運動失調には、視覚で運動を確認しながら反復するFrenkel体操が適する。",
        "choice_explanations": {"1": "Buerger体操は末梢循環障害に対する肢位変換を利用した運動である。", "2": "Codman体操は肩関節の疼痛を抑えながら可動性を保つ振り子運動である。", "3": "正しい。視覚代償を利用して下肢の協調運動を反復する。", "4": "Klapp体操は四つ這い姿勢を用いる脊柱側弯症の運動療法である。", "5": "Williams体操は腰椎前弯を減らす方向の腰痛体操である。"},
        "prerequisites": ["深部感覚障害による運動失調では、視覚情報により姿勢や運動を代償できる。"],
    },
    {
        "id": "Q1997", "question_no": 16, "category_large": "C", "category_small": 18,
        "node_id": "KN1561", "new_node": "心肺運動負荷試験（CPX）は呼気ガスと循環応答を測定し、全身の運動耐容能を評価する",
        "question_text": "75歳の男性。糖尿病性腎症のため維持血液透析中である。\nこの患者の運動耐容能を評価する検査はどれか。",
        "choices": {"1": "CAVI", "2": "HOMA-R", "3": "HRV〈Heart Rate Variability〉", "4": "足関節上腕血圧比〈ABI〉", "5": "心肺運動負荷試験〈CPX〉"},
        "answers": ["5"], "task": "assessment_selection", "ability": "MEASURE", "level": 2, "safety": "none",
        "explanation": "CPXは運動中の酸素摂取量、二酸化炭素排出量、換気量、心拍応答などを測定し、全身の運動耐容能を評価できる。",
        "choice_explanations": {"1": "CAVIは動脈硬化の程度を示す血管機能指標であり、運動耐容能の直接評価ではない。", "2": "HOMA-Rは空腹時血糖とインスリン値からインスリン抵抗性を推定する。", "3": "HRVは心拍変動から自律神経活動を評価する指標である。", "4": "ABIは下肢動脈の血流障害をスクリーニングする指標である。", "5": "正しい。運動時の呼気ガス・循環応答から運動耐容能を評価する。"},
        "prerequisites": ["運動耐容能は全身運動中の呼吸・循環・代謝応答を統合して評価する。"],
    },
    {
        "id": "Q1998", "question_no": 18, "category_large": "C", "category_small": 18,
        "node_id": "KN1562", "new_node": "末梢神経障害による随意収縮困難な筋には、筋収縮の誘発と廃用予防を目的に神経筋電気刺激療法を用いる",
        "question_text": "77歳の女性。自宅で転倒し救急車で搬入された。右大腿骨頸部骨折に対し、人工骨頭置換術が施行された。術後の右股関節は背臥位で外旋位を呈していた。翌日に患者が右足の筋力低下を訴えたため、MMTを評価したところ右足関節背屈筋0であった。\n右足関節背屈筋力低下に対する物理療法で適切なのはどれか。",
        "choices": {"1": "温熱療法", "2": "赤外線療法", "3": "体外衝撃波療法", "4": "超音波療法", "5": "電気刺激療法"},
        "answers": ["5"], "task": "intervention_selection", "ability": "PRESCRIBE", "level": 3, "safety": "moderate",
        "explanation": "足関節背屈筋がMMT 0で随意収縮を認めない場合、神経筋電気刺激療法は筋収縮を誘発し、筋萎縮などの廃用を抑える目的で用いられる。",
        "choice_explanations": {"1": "温熱療法は疼痛軽減や組織伸張性改善に用いるが、随意収縮のない背屈筋を収縮させる方法ではない。", "2": "赤外線療法は表在性温熱療法であり、麻痺筋の収縮誘発を主目的としない。", "3": "体外衝撃波療法は腱障害などに用いられ、麻痺筋の収縮誘発には適さない。", "4": "超音波療法は深部加温などに用いるが、神経筋を刺激して収縮を起こす治療ではない。", "5": "正しい。神経筋電気刺激によって背屈筋の収縮を誘発できる。"},
        "prerequisites": ["末梢神経障害で随意収縮が困難な筋では、廃用性筋萎縮の予防と筋収縮誘発を検討する。"],
    },
    {
        "id": "Q1999", "question_no": 43, "category_large": "C", "category_small": 17,
        "node_id": "KN0307", "reference": "Q309",
        "question_text": "神経伝導検査でF波の潜時延長と出現率減少がみられる疾患はどれか。",
        "choices": {"1": "Guillain-Barré症候群", "2": "Parkinson病", "3": "重症筋無力症", "4": "進行性核上性麻痺", "5": "多系統萎縮症"},
        "answers": ["1"], "task": "finding_interpretation", "ability": "INTERPRET", "level": 2, "safety": "none",
        "explanation": "F波は運動神経近位部を含む伝導を反映する。Guillain-Barré症候群では末梢神経・神経根の脱髄によりF波潜時延長や出現率低下がみられる。",
        "choice_explanations": {"1": "正しい。末梢神経近位部や神経根の脱髄を反映してF波異常が生じる。", "2": "Parkinson病は中枢神経の変性疾患で、F波異常が診断の中心ではない。", "3": "重症筋無力症は神経筋接合部疾患で、反復刺激試験などを用いる。", "4": "進行性核上性麻痺は中枢神経変性疾患である。", "5": "多系統萎縮症は中枢神経変性疾患である。"},
    },
    {
        "id": "Q2000", "question_no": 68, "category_large": "A", "category_small": 2,
        "node_id": "KN0600", "reference": "Q608",
        "question_text": "排便中枢はどれか。",
        "choices": {"1": "第1～3胸髄", "2": "第5～7胸髄", "3": "第10～12胸髄", "4": "第3～5腰髄", "5": "第2～4仙髄"},
        "answers": ["5"], "task": "finding_interpretation", "ability": "INTERPRET", "level": 1, "safety": "none",
        "explanation": "排便反射の中枢は第2～4仙髄にあり、骨盤神経を介する副交感神経活動によって直腸収縮と内肛門括約筋弛緩が促される。",
        "choice_explanations": {"1": "上位胸髄は排便反射中枢ではない。", "2": "中位胸髄は排便反射中枢ではない。", "3": "下位胸髄は排便反射中枢ではない。", "4": "腰髄は排便反射中枢ではない。", "5": "正しい。排便中枢はS2～4にある。"},
    },
]


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write(path: Path, payload) -> None:
    bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + raw)


def integrate(bank_dir: Path = BANK) -> None:
    paths = {name: bank_dir / f"{name}.json" for name in ("questions", "answers", "explanations", "question_tags")}
    paths.update(nodes=bank_dir / "knowledge_nodes.json", manifest=bank_dir / "bank_manifest.json", schema=bank_dir / "schema/question_bank_schema_v1.json")
    data = {name: _read(path) for name, path in paths.items()}
    stores = [data[name] for name in ("questions", "answers", "explanations", "question_tags")]
    indexes = [{row["id"]: row for row in store} for store in stores]
    target_ids = [f"Q{i}" for i in range(START_Q, END_Q + 1)]
    present = [qid for qid in target_ids if qid in indexes[0]]
    integrated = len(present) == len(target_ids)
    if present and not integrated:
        raise ValueError(f"partial final-six allocation: {present}")
    # Replace the initially rejected AIS item if an interrupted local run wrote it
    # before source/medical review completed. This exact migration is idempotent.
    if integrated and indexes[0]["Q1998"].get("exam", {}).get("question_no") == 19:
        item = next(row for row in ITEMS if row["id"] == "Q1998")
        node = next(row for row in data["nodes"] if row["knowledge_node_id"] == item["node_id"])
        node["label"] = item["new_node"]
        indexes[0]["Q1998"].update(management_code="Q1998-C-18-P", category_large="C", category_small=18,
            question_text=item["question_text"], choices=item["choices"], exam={"exam_no": 60, "session": "午後", "question_no": 18})
        indexes[1]["Q1998"].update(display_answer="5", accepted_answer_sets=[["5"]])
        indexes[2]["Q1998"].update(explanation=item["explanation"], choice_explanations=item["choice_explanations"])
        indexes[3]["Q1998"].update(theme=item["question_text"].split("\n")[-1], knowledge_node=node["label"],
            task=item["task"], primary_ability=item["ability"], level=item["level"], safety=item["safety"],
            prerequisite_nodes=item["prerequisites"])
    if not integrated:
        if data["manifest"].get("question_count") != BASE_END or data["manifest"].get("last_question_number") != BASE_END:
            raise ValueError("unexpected Q1994 baseline")
        if any(len(store) != BASE_END for store in stores):
            raise ValueError("formal stores are not aligned at Q1994")
        node_index = {row["knowledge_node_id"]: row for row in data["nodes"]}
        for item in ITEMS:
            qid, node_id = item["id"], item["node_id"]
            if item.get("new_node"):
                if node_id in node_index:
                    raise ValueError(f"new Node collision: {node_id}")
                node = {"knowledge_node_id": node_id, "label": item["new_node"], "status": "singleton_initial", "question_ids": [qid], "aliases": [], "successor_ids": []}
                data["nodes"].append(node); node_index[node_id] = node
                prerequisites = item["prerequisites"]
            else:
                ref = item["reference"]
                if ref not in indexes[0] or indexes[3][ref]["knowledge_node_id"] != node_id:
                    raise ValueError(f"invalid reference contract for {qid}")
                node = node_index[node_id]
                node["question_ids"].append(qid); node["status"] = "confirmed_shared"
                prerequisites = indexes[3][ref].get("prerequisite_nodes", [])
            data["questions"].append({"id": qid, "management_code": f"{qid}-{item['category_large']}-{item['category_small']}-P", "category_large": item["category_large"], "category_small": item["category_small"], "source": "P", "title": None, "question_text": item["question_text"], "choices": item["choices"], "exam": {"exam_no": 60, "session": "午後", "question_no": item["question_no"]}})
            data["answers"].append({"id": qid, "display_answer": "・".join(item["answers"]), "accepted_answer_sets": [item["answers"]], "answer_basis": "MHLW_official"})
            data["explanations"].append({"id": qid, "explanation": item["explanation"], "choice_explanations": item["choice_explanations"]})
            data["question_tags"].append({"id": qid, "theme": item["question_text"].split("\n")[-1], "knowledge_node": node["label"], "knowledge_node_id": node_id, "task": item["task"], "primary_ability": item["ability"], "secondary_ability": None, "level": item["level"], "safety": item["safety"], "prerequisite_nodes": prerequisites, "tag_version": "1.0", "tag_status": "reviewed", "source": "past_exam"})
        data["manifest"].update(bank_version=TARGET_VERSION, last_question_number=END_Q, question_count=END_Q)
        data["schema"]["$defs"]["qid"]["pattern"] = QID_PATTERN
        for name in ("questions", "answers", "explanations", "question_tags"):
            data["schema"]["properties"][name]["minItems"] = END_Q
            data["schema"]["properties"][name]["maxItems"] = END_Q
    expected = [f"Q{i}" for i in range(1, END_Q + 1)]
    if any([row["id"] for row in store] != expected for store in stores):
        raise ValueError("formal stores are not a contiguous aligned Q1-Q2000 sequence")
    if not all(re.fullmatch(QID_PATTERN, qid) for qid in expected):
        raise ValueError("QID schema pattern does not accept the final range")
    if len(data["nodes"]) != len({row["knowledge_node_id"] for row in data["nodes"]}):
        raise ValueError("duplicate Knowledge Node ID")
    if (data["manifest"].get("question_count"), data["manifest"].get("last_question_number"), data["manifest"].get("bank_version")) != (END_Q, END_Q, TARGET_VERSION):
        raise ValueError("final manifest contract mismatch")
    for name, path in paths.items():
        _write(path, data[name])


if __name__ == "__main__":
    integrate()
