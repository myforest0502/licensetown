import hashlib
import json
from pathlib import Path

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, classify_repair_confirmation
from question_bank import get_answer, get_explanation, get_question, get_question_tag, question_count

BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
PREVIOUS = 1700
END = 1720
ITEMS = {'Q1701': ['KN1064', ['Q1074'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1702': ['KN1076', ['Q1087'], 'A', 2, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1703': ['KN1081', ['Q1092'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1704': ['KN1096', ['Q1107'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1705': ['KN1130', ['Q1141'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1706': ['KN1133', ['Q1145'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1707': ['KN1160', ['Q1173'], 'B', 8, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1708': ['KN1174', ['Q1187'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1709': ['KN1218', ['Q1233'], 'B', 8, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1710': ['KN1226', ['Q1241'], 'C', 17, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1711': ['KN1241', ['Q1256'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1712': ['KN1243', ['Q1258'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1713': ['KN1260', ['Q1276'], 'A', 3, 'assessment_selection', 'MEASURE', 'KNOW'], 'Q1714': ['KN1275', ['Q1291'], 'B', 10, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1715': ['KN1276', ['Q1292'], 'B', 8, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1716': ['KN1305', ['Q1325'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1717': ['KN1307', ['Q1327'], 'A', 4, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1718': ['KN1313', ['Q1333'], 'B', 10, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1719': ['KN1329', ['Q1349'], 'C', 15, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1720': ['KN1344', ['Q1367'], 'C', 13, 'finding_interpretation', 'INTERPRET', 'MEASURE']}
EXPECTED_KEYS = {'Q1701': 'B', 'Q1702': 'D', 'Q1703': 'B', 'Q1704': 'C', 'Q1705': 'D', 'Q1706': 'C', 'Q1707': 'A', 'Q1708': 'E', 'Q1709': 'B', 'Q1710': 'B', 'Q1711': 'C', 'Q1712': 'D', 'Q1713': 'A', 'Q1714': 'C', 'Q1715': 'E', 'Q1716': 'C', 'Q1717': 'D', 'Q1718': 'B', 'Q1719': 'D', 'Q1720': 'C'}
DIGESTS = {'questions.json': '6c431faa96060fd01800c18e725013fc0ca0a006533075063fa2f5eb2e6347dd', 'answers.json': '05aa23c1d63c219c21e36746981d1531c0eeb3a1e1ba0824d00ef244d68773c9', 'explanations.json': 'b9519930156973b5eac803c371eafe83a15f1e5d425bc724daa3cc3d7fae5891', 'question_tags.json': 'b38a56cafc58d1ff299c9f8848266bee13370e8c1bdb368285399610e39d7282'}

def test_historical_content_is_unchanged():
    for filename, expected in DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        payload = json.dumps(records[:PREVIOUS], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        assert hashlib.sha256(payload).hexdigest() == expected

def test_batch_records_match_frozen_matrix():
    assert question_count() >= END
    for qid, (node, sources, category, small, task, primary, secondary) in ITEMS.items():
        q, a, e, t = get_question(qid), get_answer(qid), get_explanation(qid), get_question_tag(qid)
        assert q["management_code"] == f"{qid}-{category}-{small}-O"
        assert q["source"] == "O" and q["exam"] is None
        assert a["accepted_answer_sets"] == [[EXPECTED_KEYS[qid]]] and a["answer_basis"] == "LT_original"
        assert set(q["choices"]) == set(e["choice_explanations"]) == set("ABCDE")
        assert (t["knowledge_node_id"], t["task"], t["primary_ability"], t["secondary_ability"]) == (node, task, primary, secondary)
        assert all(canonicalize_knowledge_node_id(get_question_tag(source)["knowledge_node_id"]) == canonicalize_knowledge_node_id(node) for source in sources)

def test_all_required_pairs_are_strong_bidirectionally():
    for qid, (_node, sources, *_rest) in ITEMS.items():
        for source in sources:
            assert classify_repair_confirmation(source, qid) == DIFFERENT_QUESTION_STRONG
            assert classify_repair_confirmation(qid, source) == DIFFERENT_QUESTION_STRONG

def test_kn1275_label_cleanup():
    nodes = json.loads((BANK / "knowledge_nodes.json").read_text(encoding="utf-8-sig"))
    labels = {x["knowledge_node_id"]: x["label"] for x in nodes}
    assert labels["KN1275"] == "統合失調型パーソナリティ障害の長期的な対人関係困難・奇異な認知行動"


def test_frozen_content_has_varied_keys_and_specific_prerequisites():
    assert len(set(EXPECTED_KEYS.values())) > 1
    for qid in EXPECTED_KEYS:
        tag = get_question_tag(qid)
        assert tag['prerequisite_nodes']
        assert all(len(value) <= 30 for value in tag['prerequisite_nodes'])
