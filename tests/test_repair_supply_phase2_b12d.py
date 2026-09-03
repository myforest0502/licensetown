import hashlib
import json
from pathlib import Path

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, classify_repair_confirmation
from question_bank import get_answer, get_explanation, get_question, get_question_tag, question_count

BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
PREVIOUS = 1720
END = 1737
ITEMS = {'Q1721': ['KN1357', ['Q1380'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1722': ['KN1361', ['Q1384'], 'B', 10, 'intervention_selection', 'PRESCRIBE', 'DECIDE'], 'Q1723': ['KN1377', ['Q1401'], 'C', 15, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1724': ['KN1389', ['Q1413'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1725': ['KN1405', ['Q1430'], 'A', 4, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1726': ['KN1431', ['Q1456'], 'B', 8, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1727': ['KN1444', ['Q1469'], 'C', 18, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1728': ['KN1454', ['Q1479'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1729': ['KN1464', ['Q1489'], 'A', 2, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1730': ['KN1492', ['Q1517'], 'C', 16, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1731': ['KN1504', ['Q1530'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1732': ['KN1512', ['Q1538'], 'A', 2, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1733': ['KN1521', ['Q1547'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1734': ['KN1528', ['Q1554'], 'B', 8, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1735': ['KN1535', ['Q1561'], 'B', 7, 'assessment_selection', 'MEASURE', 'DECIDE'], 'Q1736': ['KN0453', ['Q461'], 'A', 6, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1737': ['KN0861', ['Q870'], 'B', 11, 'finding_interpretation', 'INTERPRET', 'MEASURE']}
EXPECTED_KEYS = {'Q1721': 'D', 'Q1722': 'A', 'Q1723': 'A', 'Q1724': 'D', 'Q1725': 'B', 'Q1726': 'C', 'Q1727': 'D', 'Q1728': 'B', 'Q1729': 'C', 'Q1730': 'B', 'Q1731': 'D', 'Q1732': 'A', 'Q1733': 'B', 'Q1734': 'B', 'Q1735': 'D', 'Q1736': 'D', 'Q1737': 'B'}
DIGESTS = {'questions.json': '44c72d59b228d543873732cae8f2cd1c3b27c611ae831d82b7801093baa0556d', 'answers.json': 'd288569a52e3d68cf983401ded9141e0fffd8edcebd0b3b2c6a74c0ccf301918', 'explanations.json': '3a6da66b27f2b82b07731423360d49a24a3dc9ae83c6c792c100378f661c3c60', 'question_tags.json': 'ecef7f54b4af84c7760e07841bdd69361842e9d5597a2fb4a2fffae96786c911'}

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

def test_kn1431_label_cleanup():
    nodes = json.loads((BANK / "knowledge_nodes.json").read_text(encoding="utf-8-sig"))
    labels = {x["knowledge_node_id"]: x["label"] for x in nodes}
    assert labels["KN1431"] == "Hospitalization-Associated Disability（入院関連機能障害）の評価"


def test_frozen_content_has_varied_keys_and_specific_prerequisites():
    assert len(set(EXPECTED_KEYS.values())) > 1
    for qid in EXPECTED_KEYS:
        tag = get_question_tag(qid)
        assert tag['prerequisite_nodes']
        assert all(len(value) <= 30 for value in tag['prerequisite_nodes'])
