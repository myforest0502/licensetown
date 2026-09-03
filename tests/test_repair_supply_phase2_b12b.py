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
DIGESTS = {'questions.json': '94a912a566f6bbb2e154dbab9f81aea8c699baa20d986f3cc6463eff1fce7d47', 'answers.json': '4166ae03055e04ba523372e98fd70dfa3c6d11f931c05d54a2f9e66c9dd9a708', 'explanations.json': '50d9874c672a87083cecff5bfd50fd0c7daee087321f129096bc577032f4f056', 'question_tags.json': '8b8c445973ef7e615c920ec776aba5e93c57295cff0f2417527e2576c43856d5'}

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
