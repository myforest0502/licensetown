import importlib.util
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_question_content_quality.py"
SPEC = importlib.util.spec_from_file_location("content_quality", PATH)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(audit)


def records(keys, *, duplicate_stem=False, meta=False):
    questions, answers, explanations, tags = [], [], [], []
    for index, key in enumerate(keys, 1):
        qid = f"Q{index}"
        stem = "同じ設問" if duplicate_stem else f"領域{index}の固有所見から判断する設問"
        choices = {letter: f"領域{index}-{letter}の具体的選択肢" for letter in "ABCDE"}
        if meta:
            choices["E"] = "条件を無視した一般化を行う"
        questions.append({"id": qid, "question_text": stem, "choices": choices})
        answers.append({"id": qid, "display_answer": key})
        explanations.append({"id": qid, "explanation": f"領域{index}固有の根拠"})
        tags.append({"id": qid, "knowledge_node_id": f"KN{index:04d}", "prerequisite_nodes": [f"概念{index}"]})
    return questions, answers, explanations, tags


def test_b12_style_universal_key_fails():
    report = audit.audit_content_records(*records("A" * 20))
    assert any(item["rule_id"] == "KEY_CONCENTRATION" and item["severity"] == "FAIL" for item in report["findings"])


def test_legitimate_skew_warns_but_does_not_fail():
    report = audit.audit_content_records(*records("AAAAAAAABC"))
    assert report["fail_count"] == 0
    assert any(item["rule_id"] == "KEY_CONCENTRATION" and item["severity"] == "WARN" for item in report["findings"])


def test_duplicate_stem_and_repeated_meta_distractor_fail():
    duplicate = audit.audit_content_records(*records("ABCDEABCDE", duplicate_stem=True))
    meta = audit.audit_content_records(*records("ABCDEABCDE", meta=True))
    assert any(item["rule_id"] == "EXACT_DUPLICATE_STEM" for item in duplicate["findings"])
    assert any(item["rule_id"] == "META_WRONG_DISTRACTOR" for item in meta["findings"])


def test_clean_mixed_domain_batch_passes():
    report = audit.audit_content_records(*records("ABCDEABCDE"))
    assert report["fail_count"] == report["warn_count"] == 0


def test_prerequisite_sentence_leak_is_visible_without_mutation():
    data = records("ABCDEABCDE")
    data[3][0]["prerequisite_nodes"] = ["これは説明文として長すぎる前提知識であり、そのまま保存すべきではありません。"]
    report = audit.audit_content_records(*data)
    assert any(item["rule_id"] == "PREREQUISITE_SENTENCE_LEAK" for item in report["findings"])


def test_learner_internal_metadata_and_generic_choice_rationale_fail():
    data = records("ABCDEABCDE")
    data[0][0]["question_text"] += " These amendments preserve frozen Node metadata."
    data[2][0]["choice_explanations"] = {
        letter: ("正しい。" if letter == "A" else f"誤り。「{letter}」ではなく、この設問の条件では「A」を選ぶ。")
        for letter in "ABCDE"
    }
    report = audit.audit_content_records(*data)
    assert any(item["rule_id"] == "LEARNER_TEXT_INTERNAL_METADATA" and item["severity"] == "FAIL" for item in report["findings"])
    assert any(item["rule_id"] == "GENERIC_CHOICE_RATIONALE" and item["severity"] == "FAIL" for item in report["findings"])


def test_repeated_stem_template_warns_and_source_alt_is_formally_deferred():
    data = records("ABCDEABCDE")
    for question in data[0][:3]:
        question["question_text"] = f"{question['id']}について、次の判断を行う。最も適切なのはどれか。"
    report = audit.audit_content_records(*data)
    assert any(item["rule_id"] == "REPEATED_STEM_TEMPLATE" and item["severity"] == "WARN" for item in report["findings"])
    assert audit.SOURCE_ALT_DEMAND_DEFERRED_TO_FORMAL_PAIR_TESTS is True
