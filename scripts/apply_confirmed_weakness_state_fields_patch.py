from pathlib import Path

path = Path("knowledge_node_state_transition.py")
text = path.read_text(encoding="utf-8")

old_empty = '''            "wrong_question_count": 0,\n            "confident_correct_after_wrong_count": 0,\n            "evidence_level": "NO_WRONG_EVIDENCE",\n            "retention_reference_question_id": None,'''
new_empty = '''            "wrong_question_count": 0,\n            "confident_correct_after_wrong_count": 0,\n            "evidence_level": "NO_WRONG_EVIDENCE",\n            "confirmed_weakness_evidence_level": "NO_WRONG_EVIDENCE",\n            "evaluable_wrong_question_count": 0,\n            "unknown_attempt_count": 0,\n            "retention_reference_question_id": None,'''

old_evidence = '''    evidence = _evidence(history)\n    return {\n        "canonical_node_id": canonical_node_id,'''
new_evidence = '''    evidence = _evidence(history)\n    evaluable_history = [\n        item for item in history\n        if item.get("answer_status") != "unknown"\n    ]\n    confirmed = (\n        _evidence(evaluable_history)\n        if evaluable_history\n        else {"evidence_level": "NO_WRONG_EVIDENCE", "wrong_question_count": 0}\n    )\n    unknown_attempt_count = sum(\n        item.get("answer_status") == "unknown"\n        for item in history\n    )\n    return {\n        "canonical_node_id": canonical_node_id,'''

old_fields = '''        "wrong_question_count": evidence["wrong_question_count"],\n        "confident_correct_after_wrong_count": confident_correct_after_wrong_count,\n        "evidence_level": evidence["evidence_level"],\n        "retention_reference_question_id": retention_reference_question_id,'''
new_fields = '''        "wrong_question_count": evidence["wrong_question_count"],\n        "confident_correct_after_wrong_count": confident_correct_after_wrong_count,\n        "evidence_level": evidence["evidence_level"],\n        "confirmed_weakness_evidence_level": confirmed["evidence_level"],\n        "evaluable_wrong_question_count": confirmed["wrong_question_count"],\n        "unknown_attempt_count": unknown_attempt_count,\n        "retention_reference_question_id": retention_reference_question_id,'''

for old, new in ((old_empty, new_empty), (old_evidence, new_evidence), (old_fields, new_fields)):
    if new in text:
        continue
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"patch target count={count}: {old[:80]}")
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
