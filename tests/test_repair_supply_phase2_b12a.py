import hashlib
import json
from pathlib import Path

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, classify_repair_confirmation
from question_bank import get_answer, get_explanation, get_question, get_question_tag, question_count

BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
PREVIOUS = 1660
END = 1680
ITEMS = {'Q1661': ['KN0240', ['Q241'], 'B', 8, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1662': ['KN0242', ['Q243'], 'C', 15, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1663': ['KN0259', ['Q260'], 'B', 8, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1664': ['KN0283', ['Q285'], 'C', 13, 'intervention_selection', 'PRESCRIBE', 'KNOW'], 'Q1665': ['KN0315', ['Q317'], 'B', 8, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1666': ['KN0316', ['Q318'], 'A', 2, 'fact_recall', 'KNOW', 'INTERPRET'], 'Q1667': ['KN0359', ['Q363'], 'C', 17, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1668': ['KN0376', ['Q381'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1669': ['KN0381', ['Q386'], 'B', 8, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1670': ['KN0407', ['Q414'], 'C', 17, 'assessment_selection', 'MEASURE', 'KNOW'], 'Q1671': ['KN0436', ['Q444'], 'C', 16, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1672': ['KN0446', ['Q454'], 'A', 1, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1673': ['KN0495', ['Q503'], 'C', 17, 'assessment_selection', 'MEASURE', 'DECIDE'], 'Q1674': ['KN0507', ['Q515'], 'C', 13, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1675': ['KN0512', ['Q520'], 'C', 17, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1676': ['KN0532', ['Q540'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1677': ['KN0540', ['Q548'], 'A', 2, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1678': ['KN0546', ['Q554'], 'C', 13, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1679': ['KN0548', ['Q556'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1680': ['KN0549', ['Q557', 'Q1426'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW']}
EXPECTED_KEYS = {'Q1661': 'C', 'Q1662': 'D', 'Q1663': 'B', 'Q1664': 'E', 'Q1665': 'C', 'Q1666': 'D', 'Q1667': 'B', 'Q1668': 'D', 'Q1669': 'B', 'Q1670': 'E', 'Q1671': 'C', 'Q1672': 'A', 'Q1673': 'D', 'Q1674': 'B', 'Q1675': 'C', 'Q1676': 'E', 'Q1677': 'A', 'Q1678': 'C', 'Q1679': 'B', 'Q1680': 'E'}
DIGESTS = {'questions.json': '20a5e2d94885dfaca431a2d96e1b8c8ae4cfd9844161921ada224ed10f16f3dc', 'answers.json': '00771b2a3391e4d1cb5540a85eb67df68f2a9cd08620b5517d6f078425bf1790', 'explanations.json': 'e0e9db6ad98fa10f934f6b89f28d3d50599431f665cc89c9e87dc0ddea01adf1', 'question_tags.json': '76328829e79397cb8ff96e1c44afa4c28ed5107a2db172763ff6e11c5a761ee3'}

def test_historical_content_is_unchanged():
    for filename, expected in DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        payload = json.dumps(records[:PREVIOUS], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        assert hashlib.sha256(payload).hexdigest() == expected

def test_batch_records_match_frozen_matrix():
    assert question_count() == END
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

def test_canonical_shared_q1680_and_node_cleanup():
    assert canonicalize_knowledge_node_id("KN1401") == "KN0549"
    assert classify_repair_confirmation("Q557", "Q1680") == DIFFERENT_QUESTION_STRONG
    assert classify_repair_confirmation("Q1426", "Q1680") == DIFFERENT_QUESTION_STRONG
    nodes = json.loads((BANK / "knowledge_nodes.json").read_text(encoding="utf-8-sig"))
    labels = {x["knowledge_node_id"]: x["label"] for x in nodes}
    assert labels["KN0495"] == "Barthel Indexにおける移乗・移動能力の採点"


def test_frozen_content_has_varied_keys_and_specific_prerequisites():
    assert len(set(EXPECTED_KEYS.values())) > 1
    for qid in EXPECTED_KEYS:
        tag = get_question_tag(qid)
        assert tag['prerequisite_nodes']
        assert all(len(value) <= 30 for value in tag['prerequisite_nodes'])
