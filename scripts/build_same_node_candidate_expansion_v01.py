"""Build the reviewed SAME_NODE expansion candidate artifacts (no master writes)."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
OUTPUT_JSON = ROOT / "same_node_candidates_v0.1.json"
OUTPUT_AUDIT = ROOT / "same_node_candidates_audit_v0.1.txt"
ALLOWED_ACTIONS = {
    "SAME_NODE", "PREREQUISITE", "TRANSFER", "RELATED_ONLY", "UNRELATED",
    "NEEDS_CLINICAL_REVIEW",
}


def _load(name: str) -> list[dict[str, Any]]:
    value = json.loads((BANK / name).read_text(encoding="utf-8-sig"))
    if not isinstance(value, list):
        raise ValueError(f"{name} must contain an array")
    return value


def _summary(text: str, limit: int = 220) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return normalized if len(normalized) <= limit else normalized[: limit - 1] + "…"


# The list is deliberately small and precision-oriented. Existing canonical pairs
# and formal relations are excluded during validation below.
SELECTIONS = [
    # High-confidence SAME_NODE candidates.
    ("KN0593", "KN1245", "SAME_NODE", "high", "ネフロンの構成", "どちらもネフロン=腎小体（糸球体＋Bowman嚢）＋尿細管という同一の解剖知識を問う。"),
    ("KN0503", "KN0883", "SAME_NODE", "high", "嫌気的解糖とピルビン酸・乳酸", "どちらもグルコースからピルビン酸、低酸素下で乳酸へという同一経路が正答根拠。"),
    ("KN0623", "KN1212", "SAME_NODE", "high", "リンパ浮腫と蜂窩織炎", "蛋白に富む間質液と皮膚バリア低下による感染反復という中心機序が同一。"),
    ("KN0232", "KN0312", "SAME_NODE", "high", "Brown-Séquard症候群", "同側運動・深部感覚障害と対側温痛覚障害の交叉解釈が同一。"),
    ("KN1324", "KN1367", "SAME_NODE", "high", "ICFの環境因子", "制度・サービス・支援・態度等を環境因子と識別する同一知識。"),
    ("KN0202", "KN0318", "SAME_NODE", "high", "胸部症状と血圧低下時の運動中止", "運動中の胸部圧迫感と収縮期血圧低下を危険徴候として即時中止する判断が同一。"),
    ("KN0509", "KN0927", "SAME_NODE", "high", "下腿義足の足部内側浮き", "同一所見からソケット初期内転角不足を推定する同一のアライメント知識。"),
    ("KN0107", "KN0148", "SAME_NODE", "high", "Borg 13で安定時の運動継続", "Borg 13で症状・循環動態・酸素化が安定しているとき現負荷を継続する判断が同一。"),
    ("KN0627", "KN1220", "SAME_NODE", "high", "欠神発作と過換気誘発", "欠神発作は小児に多く過換気で誘発されやすいという同一の識別知識。"),
    ("KN0795", "KN1366", "SAME_NODE", "high", "ノーマライゼーション", "障害の有無にかかわらず地域で普通の生活と自己決定を保障する同一理念。"),
    ("KN1013", "KN1527", "SAME_NODE", "high", "角膜反射の求心路・遠心路", "求心路が三叉神経第1枝、遠心路が顔面神経という同一反射弓。"),
    ("KN1080", "KN1518", "SAME_NODE", "high", "遠心性収縮", "筋が張力を発揮しながら伸張される収縮という同一定義の事例識別。"),
    ("KN0945", "KN1337", "SAME_NODE", "high", "半規管と角加速度", "内リンパ流と膨大部稜により角加速度を感知する同一知識。"),
    ("KN0272", "KN1421", "SAME_NODE", "high", "Parkinson病のすくみ足と視覚的外的キュー", "床上の目印など視覚的外的キューですくみ足を改善する同一介入知識。"),
    ("KN0071", "KN0126", "SAME_NODE", "high", "Pusher現象の視覚的垂直学習", "視覚的垂直指標を用いて正中位を自己修正する同一介入原理。"),
    ("KN0071", "KN0211", "SAME_NODE", "high", "Pusher現象の視覚的垂直学習", "座位でも視覚的垂直を基準に正中位を学習する中心介入は同一。"),
    ("KN0126", "KN0195", "SAME_NODE", "high", "Pusher現象の視覚的正中学習", "鏡や垂直物を視覚的手掛かりとする正中学習が同一。"),
    ("KN0112", "KN0142", "SAME_NODE", "high", "股関節外転筋と骨盤制御", "Trendelenburg徴候とMMT3から外転筋機能・片脚荷重時骨盤制御を優先する同一修復単位。"),
    ("KN0128", "KN0196", "SAME_NODE", "high", "足底腱膜炎の柔軟性介入", "下腿三頭筋と足底腱膜の柔軟性改善を選ぶ同一病態・介入判断。"),
    ("KN0007", "KN0033", "SAME_NODE", "high", "下垂足・鶏歩へのAFO", "背屈筋力低下による足尖クリアランス不足をAFOで補う同一適応判断。"),
    ("KN1256", "KN1432", "SAME_NODE", "high", "矢状面重心線と外果", "安静立位の矢状面重心線が外果のやや前方を通る同一解剖学的基準。"),
    ("KN0068", "KN0190", "SAME_NODE", "high", "多発性硬化症の活動・疲労記録", "活動量と疲労の関係を記録し、休息と運動を配分する同一自己管理戦略。"),
    ("KN0202", "KN0227", "SAME_NODE", "high", "心リハ中の胸部危険徴候", "胸部圧迫感・顔面蒼白など循環器イベントを疑う所見で運動を即時中止する同一安全判断。"),
    # SAME_NODE candidates that still deserve focused clinical review.
    ("KN0842", "KN1175", "SAME_NODE", "medium", "錐体路障害の上位運動ニューロン徴候", "多発性硬化症の疾患文脈と一般的錐体路徴候は、腱反射亢進・病的反射という中心知識を共有するが粒度確認が必要。"),
    ("KN0725", "KN0940", "SAME_NODE", "medium", "上斜筋と滑車神経", "どちらも上斜筋=滑車神経を正答根拠に含むが、一方は複数筋の組合せ問題のため最小単位の確認が必要。"),
    # Directional or transfer relationships deliberately not merged.
    ("KN0913", "KN0914", "PREREQUISITE", "high", "腰椎椎間板ヘルニアの診断と理学療法", "疼痛分布から責任椎間を推定する診断理解は、亜急性期介入の選択に先行するが同一知識ではない。"),
    ("KN0647", "KN1533", "PREREQUISITE", "high", "血流不良と手舟状骨偽関節", "血流の乏しい骨折で偽関節が生じやすい一般原理が、手舟状骨の個別判断の前提。"),
    ("KN0184", "KN1499", "PREREQUISITE", "medium", "Berg Balance Scaleの選択と項目理解", "BBSを適切なバランス評価として選ぶことと、項目・採点を知ることは方向性のある別知識。"),
    ("KN1112", "KN1439", "PREREQUISITE", "medium", "SIASの非麻痺側機能と握力", "SIASが非麻痺側機能を含む一般理解が、握力がその具体項目であるという判断の前提。"),
    ("KN0760", "KN1424", "TRANSFER", "high", "Barthel Index採点", "同じBI採点基準を異なる疾患・ADL組合せに適用する転移証拠であり、問題ごとの計算条件は異なる。"),
    ("KN0205", "KN0765", "TRANSFER", "medium", "Parkinson病の外的キューと歩行練習", "外的キューの基礎知識を、小刻み・突進を含む包括的歩行練習へ応用する関係。"),
    # Similar surface wording but not the same repair target.
    ("KN0717", "KN1213", "RELATED_ONLY", "high", "Perthes病の病態と治療", "疾患は同じだが、阻血性壊死・片側性の病態知識と、免荷・containment治療は別の修復単位。"),
    ("KN1414", "KN1490", "RELATED_ONLY", "medium", "GBSの感染後発症と上行性麻痺", "同一疾患だが、先行感染と対称性上行性筋力低下は別の診断特徴。"),
    ("KN0538", "KN0808", "RELATED_ONLY", "medium", "トロンビンと凝固系", "トロンビンのフィブリン生成作用と、凝固因子を複数選ぶ分類知識は重なるが同一とは限らない。"),
    ("KN1130", "KN1384", "RELATED_ONLY", "medium", "純運動性脳神経", "純運動性という分類は同じだが、滑車・外転・舌下神経と副神経は個別に覚える必要がある。"),
    ("KN0856", "KN1182", "RELATED_ONLY", "low", "筋力増強運動の正しい原則", "設問形式と大テーマは同じだが、正答の中心原則が一致するか追加確認が必要。"),
    ("KN1142", "KN1252", "UNRELATED", "high", "筋と作用の組合せ", "ラベルと問題形式は同一だが、前頭筋・側頭筋と短腓骨筋・薄筋は異なる解剖知識。"),
    ("KN0935", "KN1062", "UNRELATED", "high", "複数正答の公式採点", "どちらも公式採点上の複数正答だが、医学的な修復内容は別問題である。"),
]


def build_candidates() -> list[dict[str, Any]]:
    questions = {item["id"]: item for item in _load("questions.json")}
    explanations = {item["id"]: item for item in _load("explanations.json")}
    tags = _load("question_tags.json")
    nodes = {item["knowledge_node_id"]: item for item in _load("knowledge_nodes.json")}
    qids_by_node: dict[str, list[str]] = {}
    for tag in tags:
        qids_by_node.setdefault(str(tag["knowledge_node_id"]), []).append(str(tag["id"]))

    canonical_pairs = {
        frozenset([record["canonical_node_id"], alias])
        for record in _load("knowledge_node_canonical_map.json")
        for alias in record["alias_node_ids"]
    }
    relation_pairs = {
        frozenset([record["source_node_id"], record["target_node_id"]])
        for record in _load("knowledge_node_relations.json")
    }
    candidates = []
    seen_pairs = set()
    for number, (left, right, action, confidence, topic, rationale) in enumerate(SELECTIONS, 1):
        pair = frozenset([left, right])
        if pair in seen_pairs or pair in canonical_pairs or pair in relation_pairs:
            raise ValueError(f"duplicate or already formal pair: {left}/{right}")
        if left not in nodes or right not in nodes:
            raise ValueError(f"unknown Node: {left}/{right}")
        if action not in ALLOWED_ACTIONS or confidence not in {"high", "medium", "low"}:
            raise ValueError(f"invalid classification: {left}/{right}")
        seen_pairs.add(pair)
        node_ids = [left, right]
        question_ids = [qids_by_node[node_id][0] for node_id in node_ids]
        if action == "SAME_NODE":
            why_same = rationale
            why_not_prerequisite = "一方が他方の前提なのではなく、両問の中心的な修復内容自体が同じ。"
            why_not_transfer = "別場面への応用力より、同一の中心知識を別Qで再確認している。"
        elif action == "PREREQUISITE":
            why_same = "SAME_NODEではない。" + rationale
            why_not_prerequisite = "該当せず。PREREQUISITE分類が妥当。"
            why_not_transfer = "対等な応用関係ではなく、基礎から個別判断への方向性がある。"
        elif action == "TRANSFER":
            why_same = "SAME_NODEではない。" + rationale
            why_not_prerequisite = "単純な先行知識ではなく、同じ原理を異なる状況へ適用する。"
            why_not_transfer = "該当せず。TRANSFER分類が妥当。"
        else:
            why_same = "SAME_NODEではない。" + rationale
            why_not_prerequisite = "明確な前提から応用への方向性は確認できない。"
            why_not_transfer = "同じ中心知識の場面間適用とは言えない。"
        candidates.append({
            "candidate_id": f"SNC{number:04d}",
            "node_ids": node_ids,
            "question_ids": question_ids,
            "knowledge_node_labels": [nodes[node_id]["label"] for node_id in node_ids],
            "problem_summaries": [_summary(questions[qid]["question_text"]) for qid in question_ids],
            "correct_answer_concept_summaries": [
                _summary(explanations[qid]["explanation"]) for qid in question_ids
            ],
            "topic": topic,
            "why_same_node": why_same,
            "why_not_prerequisite": why_not_prerequisite,
            "why_not_transfer": why_not_transfer,
            "confidence": confidence,
            "recommended_action": action,
            "repair_confirmation_suitability": (
                "一方の誤答後に他方を別Qの修復確認として出題することが医学教育的に妥当。"
                if action == "SAME_NODE" and confidence == "high"
                else "自動利用せず、Aoiの臨床・教育レビューを先行する。"
            ),
            "clinical_review_recommended": True,
        })
    if len(candidates) > 50:
        raise ValueError("candidate limit exceeded")
    return candidates


def build_audit(candidates: list[dict[str, Any]]) -> str:
    action_counts = Counter(item["recommended_action"] for item in candidates)
    same_counts = Counter(
        item["confidence"] for item in candidates if item["recommended_action"] == "SAME_NODE"
    )
    review = [item for item in candidates if item["clinical_review_recommended"]]
    lines = [
        "LicenseTown SAME_NODE candidate expansion v0.1 audit",
        f"source_questions: {len(_load('questions.json'))}",
        f"source_question_tags: {len(_load('question_tags.json'))}",
        f"source_knowledge_nodes: {len(_load('knowledge_nodes.json'))}",
        f"candidate_total: {len(candidates)}",
        f"SAME_NODE_high: {same_counts['high']}",
        f"SAME_NODE_medium: {same_counts['medium']}",
        f"SAME_NODE_low: {same_counts['low']}",
    ]
    lines.extend(f"{action}: {action_counts[action]}" for action in sorted(ALLOWED_ACTIONS))
    lines.extend([
        "existing_canonical_pair_overlap: 0",
        "existing_relation_pair_overlap: 0",
        "canonical_map_modified: no",
        "merge_candidates_modified: no",
        "question_tags_modified: no",
        "knowledge_nodes_modified: no",
        "production_db_accessed: no",
        "",
        "Aoi canonical review queue (SAME_NODE only):",
    ])
    lines.extend(
        f"- {item['candidate_id']} {item['node_ids'][0]} / {item['node_ids'][1]} "
        f"[{item['recommended_action']} {item['confidence']}] {item['topic']}"
        for item in review if item["recommended_action"] == "SAME_NODE"
    )
    lines.append("")
    lines.append("Aoi boundary review queue (not SAME_NODE):")
    lines.extend(
        f"- {item['candidate_id']} {item['node_ids'][0]} / {item['node_ids'][1]} "
        f"[{item['recommended_action']} {item['confidence']}] {item['topic']}"
        for item in review if item["recommended_action"] != "SAME_NODE"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        candidates = build_candidates()
        OUTPUT_JSON.write_text(
            json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        OUTPUT_AUDIT.write_text(build_audit(candidates), encoding="utf-8")
    except Exception as exc:
        print(f"candidate build failed: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {len(candidates)} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
