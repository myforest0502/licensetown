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
DIGESTS = {'questions.json': '932f52f63706af14aaf985a42d24a5174fd630fda7a64b0b294217cb130fa12d', 'answers.json': '59ddbd1fe662f846f32a37ef99898e0ebdb067bb6c4604d4b83e60c8acaf611b', 'explanations.json': '980f1496938795ce9c93f0c96467b1eb957fdaeb7088d3d98b3d184f8d04382a', 'question_tags.json': '95f38c06418d2ba4272cc0ff40d7137af693989ebc22bb70a218bb16d2020e43'}

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
        assert a["accepted_answer_sets"] == [["A"]] and a["answer_basis"] == "LT_original"
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
