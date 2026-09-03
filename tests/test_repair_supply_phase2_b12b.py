import hashlib
import json
from pathlib import Path

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, classify_repair_confirmation
from question_bank import get_answer, get_explanation, get_question, get_question_tag, question_count

BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
PREVIOUS = 1680
END = 1700
ITEMS = {'Q1681': ['KN0586', ['Q594'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1682': ['KN0663', ['Q671'], 'A', 2, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1683': ['KN0695', ['Q703'], 'C', 17, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1684': ['KN0706', ['Q714'], 'C', 15, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1685': ['KN0742', ['Q750'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1686': ['KN0746', ['Q754'], 'B', 10, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1687': ['KN0804', ['Q812'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1688': ['KN0818', ['Q827'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1689': ['KN0819', ['Q828'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1690': ['KN0839', ['Q848'], 'A', 6, 'assessment_selection', 'MEASURE', 'KNOW'], 'Q1691': ['KN0893', ['Q902'], 'A', 3, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1692': ['KN0928', ['Q937'], 'C', 17, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1693': ['KN0960', ['Q970'], 'B', 8, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1694': ['KN0961', ['Q971'], 'B', 7, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1695': ['KN0982', ['Q992'], 'C', 15, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1696': ['KN0994', ['Q1004'], 'B', 8, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1697': ['KN1015', ['Q1025'], 'A', 2, 'finding_interpretation', 'INTERPRET', 'MEASURE'], 'Q1698': ['KN1051', ['Q1061'], 'C', 13, 'assessment_selection', 'MEASURE', 'INTERPRET'], 'Q1699': ['KN1055', ['Q1065'], 'C', 18, 'finding_interpretation', 'INTERPRET', 'KNOW'], 'Q1700': ['KN1063', ['Q1073'], 'A', 1, 'finding_interpretation', 'INTERPRET', 'KNOW']}
EXPECTED_KEYS = {'Q1681': 'B', 'Q1682': 'D', 'Q1683': 'C', 'Q1684': 'D', 'Q1685': 'E', 'Q1686': 'B', 'Q1687': 'D', 'Q1688': 'C', 'Q1689': 'A', 'Q1690': 'D', 'Q1691': 'E', 'Q1692': 'B', 'Q1693': 'C', 'Q1694': 'A', 'Q1695': 'D', 'Q1696': 'C', 'Q1697': 'E', 'Q1698': 'C', 'Q1699': 'A', 'Q1700': 'D'}
DIGESTS = {'questions.json': 'ef801a9100277a3bf94ff1ca3d4cb6c1d9e2bec407d8717d2b3f1f95432653f2', 'answers.json': 'bda75bc63d4771777c70f0f3b0f85983d278b5559aa23a916e83bd9eea304398', 'explanations.json': '3bec020a06929a15b10f606e5c3d9e762e58254c85017944f9006e2edad520ec', 'question_tags.json': '47cf69e76e33d09b93379c61a62a1dd2b08ff36cd2e829f2ff89eb420c82aef4'}

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


def test_frozen_content_has_varied_keys_and_specific_prerequisites():
    assert len(set(EXPECTED_KEYS.values())) > 1
    for qid in EXPECTED_KEYS:
        tag = get_question_tag(qid)
        assert tag['prerequisite_nodes']
        assert all(len(value) <= 30 for value in tag['prerequisite_nodes'])
