from pathlib import Path

path = Path("pilot_diagnostics.py")
text = path.read_text(encoding="utf-8")

import_marker = '''from phase11_retrospective_shadow_audit import build_retrospective_shadow_audit\n'''
import_line = '''from phase11_active_weakness import build_active_repair_weakness\n'''
if import_line not in text:
    if text.count(import_marker) != 1:
        raise SystemExit(f"import marker count={text.count(import_marker)}")
    text = text.replace(import_marker, import_line + import_marker)

start_marker = '''def build_confident_wrong_node_details(attempts, field_evidence, shadow_judgment):\n'''
end_marker = '''\n\ndef build_adaptive_selection_audit(adaptive):\n'''
start = text.find(start_marker)
end = text.find(end_marker)
if start < 0 or end < 0 or end <= start:
    raise SystemExit("confident wrong detail function boundaries not found")

replacement = '''def build_confident_wrong_node_details(\n    attempts, field_evidence, shadow_judgment, *, as_of=None\n):\n    """Expose only the active current-cycle evidence that contributes to J2."""\n    if shadow_judgment.get("reason_code") != "confident_wrong_cluster":\n        return []\n    target_field = shadow_judgment.get("target_field")\n    target_field_id = next(\n        (field_id for field_id, name in CATEGORY_NAMES.items() if name == target_field),\n        None,\n    )\n    if target_field_id is None:\n        return []\n\n    states = {\n        str(item.get("canonical_node_id")): str(item.get("state") or "unseen")\n        for item in field_evidence.get("canonical_node_evidence", [])\n        if item.get("canonical_node_id")\n    }\n    active_by_node = build_active_repair_weakness(attempts, as_of=as_of)\n\n    def field_for_question(question_id):\n        try:\n            return get_category_small(str(question_id))\n        except (KeyError, TypeError, ValueError):\n            return None\n\n    def question_sort_key(value):\n        return (\n            (0, int(value[1:]))\n            if value.startswith("Q") and value[1:].isdigit()\n            else (1, value)\n        )\n\n    details = []\n    for node_id, source in active_by_node.items():\n        if states.get(node_id) != "repairing":\n            continue\n        wrong_qs = [\n            str(q)\n            for q in source.get("active_evaluable_wrong_question_ids", [])\n            if q\n        ]\n        confident_qs = [\n            str(q)\n            for q in source.get("active_confident_wrong_question_ids", [])\n            if q\n        ]\n        target_wrong_qs = [q for q in wrong_qs if field_for_question(q) == target_field_id]\n        target_confident_qs = [\n            q for q in confident_qs if field_for_question(q) == target_field_id\n        ]\n        cross_confident = (\n            source.get("active_weakness_evidence_level")\n            == "CROSS_QUESTION_CONFIDENT_WRONG"\n        )\n        contributes_to_target_j2 = bool(target_confident_qs) or bool(\n            target_wrong_qs and cross_confident\n        )\n        if not contributes_to_target_j2:\n            continue\n\n        last_wrong = _wrong_time(source.get("active_last_evaluable_wrong_at"))\n        question_ids_for_node = sorted(set(wrong_qs), key=question_sort_key)\n        details.append({\n            "canonical_node_id": node_id,\n            "knowledge_text": _NODE_LABELS.get(node_id, "名称未登録"),\n            "question_ids": question_ids_for_node,\n            "confident_wrong_count": int(source.get("active_confident_wrong_count") or 0),\n            "distinct_question_count": int(\n                source.get("active_evaluable_wrong_question_count") or 0\n            ),\n            "cross_question": cross_confident,\n            "node_state": states[node_id],\n            "node_state_label": _STATE_LABELS.get(states[node_id], states[node_id]),\n            "last_wrong_at": (\n                last_wrong.astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M")\n                if last_wrong else None\n            ),\n        })\n    details.sort(key=lambda item: (\n        -item["confident_wrong_count"],\n        -item["distinct_question_count"],\n        item["canonical_node_id"],\n    ))\n    return details\n'''
text = text[:start] + replacement + text[end:]

old_call = '''    confident_wrong_node_details = build_confident_wrong_node_details(\n        all_attempts,\n        field_evidence,\n        shadow_judgment,\n    )'''
new_call = '''    confident_wrong_node_details = build_confident_wrong_node_details(\n        all_attempts,\n        field_evidence,\n        shadow_judgment,\n        as_of=now,\n    )'''
if text.count(old_call) != 1:
    raise SystemExit(f"call target count={text.count(old_call)}")
text = text.replace(old_call, new_call)

path.write_text(text, encoding="utf-8")
