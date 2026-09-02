from pathlib import Path

path = Path("pilot_diagnostics.py")
text = path.read_text(encoding="utf-8")

old = '''    adaptive_unique_nodes,\n    adaptive_groups,\n):'''
new = '''    adaptive_unique_nodes,\n    adaptive_groups,\n    strong_repair_supply_priorities=None,\n):'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"signature marker count={text.count(old)}")
    text = text.replace(old, new)

old = '''    repairability = repairing_node_repairability or {}\n    groups = adaptive_groups or {}'''
new = '''    repairability = repairing_node_repairability or {}\n    repair_supply = strong_repair_supply_priorities or {}\n    groups = adaptive_groups or {}'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"repair supply init marker count={text.count(old)}")
    text = text.replace(old, new)

old = '''        (\n            "adaptive_simulation="\n            f"count:{int(adaptive_count or 0)},"'''
new = '''        (\n            "repair_supply="\n            f"targets:{int(repair_supply.get('target_node_total') or 0)},"\n            f"priority_A:{int((repair_supply.get('priority_counts') or {}).get('A') or 0)},"\n            f"priority_B:{int((repair_supply.get('priority_counts') or {}).get('B') or 0)},"\n            f"priority_C:{int((repair_supply.get('priority_counts') or {}).get('C') or 0)},"\n            f"priority_D:{int((repair_supply.get('priority_counts') or {}).get('D') or 0)},"\n            f"weak_pair_review:{int(repair_supply.get('weak_pair_review_count') or 0)},"\n            f"create_strong_alternate:{int(repair_supply.get('create_strong_alternate_count') or 0)}"\n        ),\n        (\n            "adaptive_simulation="\n            f"count:{int(adaptive_count or 0)},"'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"repair supply summary marker count={text.count(old)}")
    text = text.replace(old, new)

old = '''    ]\n    for index, snapshot in enumerate(replay.get("snapshots") or [], start=1):'''
new = '''    ]\n    for item in repair_supply.get("top") or []:\n        def _csv(values):\n            return "|".join(str(value) for value in (values or [])) or "none"\n\n        lines.append(\n            "repair_supply_top_" + str(int(item.get("rank") or 0)) + "=" + ",".join([\n                f"node:{item.get('canonical_node_id') or 'none'}",\n                f"label:{item.get('formal_label') or 'none'}",\n                f"tier:{item.get('supply_priority_tier') or 'none'}",\n                f"action:{item.get('supply_action') or 'none'}",\n                f"safety:{_csv(item.get('safety_levels'))}",\n                f"cycle_wrong:{int(item.get('current_cycle_wrong_count') or 0)}",\n                f"confident_wrong:{int(item.get('confident_wrong_count') or 0)}",\n                f"distinct_wrong_q:{int(item.get('distinct_wrong_question_count') or 0)}",\n                f"wrong_q:{_csv(item.get('wrong_question_ids'))}",\n                f"all_q:{_csv(item.get('all_question_ids'))}",\n                f"weak_candidates:{_csv(item.get('weak_repair_candidate_question_ids'))}",\n                f"unseen_different_q:{_csv(item.get('unseen_different_question_ids'))}",\n            ])\n        )\n    for index, snapshot in enumerate(replay.get("snapshots") or [], start=1):'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"repair supply top marker count={text.count(old)}")
    text = text.replace(old, new)

old = '''        repairing_node_repairability=repairing_node_repairability,\n        adaptive_count=len(adaptive),'''
new = '''        repairing_node_repairability=repairing_node_repairability,\n        strong_repair_supply_priorities=strong_repair_supply_priorities,\n        adaptive_count=len(adaptive),'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"bundle call marker count={text.count(old)}")
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
